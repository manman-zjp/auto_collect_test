from auto_collect.crawler.layer3_selenium import search_keyword as search_with_saved_login


def search_keyword(keyword, log_callback=None, result_callback=None, port=9222, storage_state="storage_state.json"):
    def log(msg):
        if log_callback:
            log_callback(msg)
        print(msg)

    def add_result(item):
        if result_callback:
            result_callback(keyword, item['link'], item['source'])

    log(f"[Manager] 开始搜索关键字: {keyword}")
    results = search_with_saved_login(keyword, storage_state)
    for item in results:
        add_result(item)
    return results