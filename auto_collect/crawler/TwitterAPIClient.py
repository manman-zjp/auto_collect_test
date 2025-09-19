import tweepy
import json
import re
import sys
from pathlib import Path

TG_LINK_RE = re.compile(r"((?:https?://)?t\.me/[A-Za-z0-9_+/?=-]+)", re.I)

def extract_tg_links_from_text(text):
    matches = set(m.group(0) for m in TG_LINK_RE.finditer(text))
    # 标准化链接，确保都有 https:// 前缀
    normalized_links = set()
    for match in matches:
        if not match.startswith('http'):
            normalized_links.add('https://' + match)
        else:
            normalized_links.add(match)
    return normalized_links

class TwitterAPIClient:
    def __init__(self, api_key, api_secret, access_token, access_token_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

        # 设置认证
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)

        # 创建API对象
        self.api = tweepy.API(auth, wait_on_rate_limit=True)

    def search_telegram_links(self, keyword, count=100):
        """
        搜索包含Telegram链接的推文
        """
        results = set()
        url = f"https://twitter.com/search?q={keyword}"

        try:
            # 使用Twitter API搜索推文
            tweets = tweepy.Cursor(self.api.search_tweets,
                                 q=keyword,
                                 result_type="recent",
                                 lang="en").items(count)

            for tweet in tweets:
                # 从推文文本中提取Telegram链接
                links = extract_tg_links_from_text(tweet.text)
                for link in links:
                    results.add(link)

            print(f"[API Worker] 搜索完成，总共找到 {len(results)} 个 t.me 链接", flush=True)

            # 打印找到的链接用于调试
            for i, link in enumerate(list(results)[:5], 1):
                print(f"[API Worker] 链接 {i}: {link}", flush=True)
            if len(results) > 5:
                print(f"[API Worker] ...还有 {len(results) - 5} 个链接", flush=True)

        except tweepy.TooManyRequests:
            print("[API Worker] ⚠️  Twitter API 速率限制，请稍后再试", flush=True)
            return []
        except tweepy.Unauthorized:
            print("[API Worker] ⚠️  Twitter API 认证失败，请检查API密钥", flush=True)
            return []
        except tweepy.NotFound:
            print("[API Worker] ⚠️  搜索请求未找到结果", flush=True)
            return []
        except Exception as e:
            print(f"[API Worker] 搜索失败: {e}", flush=True)
            import traceback
            print(f"[API Worker] 错误详情: {traceback.format_exc()}", flush=True)
            return []

        return [{"link": link, "source": url} for link in results]

def load_api_keys():
    """
    从文件加载API密钥
    """
    keys_file = Path("twitter_api_keys.json")
    if keys_file.exists():
        try:
            with open(keys_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[API] 加载API密钥失败: {e}", flush=True)
            return []
    return []

def save_api_keys(keys):
    """
    保存API密钥到文件
    """
    try:
        with open("twitter_api_keys.json", "w") as f:
            json.dump(keys, f, indent=2)
    except Exception as e:
        print(f"[API] 保存API密钥失败: {e}", flush=True)

# ---------------- CLI 调用 ----------------
if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("用法: python layer4_twitter_api.py <api_key> <api_secret> <access_token> <access_token_secret> <keyword>", flush=True)
        sys.exit(1)

    api_key = sys.argv[1]
    api_secret = sys.argv[2]
    access_token = sys.argv[3]
    access_token_secret = sys.argv[4]
    keyword = sys.argv[5]

    client = TwitterAPIClient(api_key, api_secret, access_token, access_token_secret)
    results = client.search_telegram_links(keyword)
    print(json.dumps(results, ensure_ascii=False), flush=True)
