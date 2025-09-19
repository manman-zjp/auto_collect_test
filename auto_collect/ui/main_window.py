from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLineEdit, 
                             QTableWidget, QTableWidgetItem, QPlainTextEdit, 
                             QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
                             QComboBox, QHBoxLayout, QLabel, QTabWidget, QTextEdit,
                             QSplitter, QFrame, QSizePolicy, QAbstractItemView)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, pyqtSlot, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QIcon, QPalette, QCloseEvent
from typing import Optional
import subprocess
import json
from pathlib import Path
import sys
import sqlite3
import os

# 添加项目根目录到sys.path以确保可以导入
sys.path.append(str(Path(__file__).parent.parent))

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，处理打包后的情况"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后的路径
        return os.path.join(getattr(sys, '_MEIPASS'), relative_path)
    # 开发环境中的路径
    return os.path.join(os.path.abspath("."), relative_path)

class DatabaseManager:
    def __init__(self, db_path: str = "telegram_links.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库和表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS telegram_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link TEXT UNIQUE NOT NULL,
                    source TEXT,
                    keyword TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引提高查询性能
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_link ON telegram_links(link)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_keyword ON telegram_links(keyword)
            ''')
            
            conn.commit()
    
    def get_all_links(self) -> list:
        """获取所有链接"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, link, source, keyword, created_at FROM telegram_links
                ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'link': row[1],
                    'source': row[2],
                    'keyword': row[3],
                    'created_at': row[4]
                }
                for row in rows
            ]
    
    def search_links(self, keyword=None, link_contains=None) -> list:
        """根据条件搜索链接"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT id, link, source, keyword, created_at FROM telegram_links WHERE 1=1"
            params = []
            
            if keyword:
                query += " AND keyword LIKE ?"
                params.append(f"%{keyword}%")
                
            if link_contains:
                query += " AND link LIKE ?"
                params.append(f"%{link_contains}%")
                
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'link': row[1],
                    'source': row[2],
                    'keyword': row[3],
                    'created_at': row[4]
                }
                for row in rows
            ]
    
    def delete_link(self, link_id: int) -> bool:
        """根据ID删除链接"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM telegram_links WHERE id = ?", (link_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"[DB] 删除链接时出错: {e}")
            return False
    
    def delete_links_by_keyword(self, keyword: str) -> int:
        """根据关键词删除链接"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM telegram_links WHERE keyword = ?", (keyword,))
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            print(f"[DB] 根据关键词删除链接时出错: {e}")
            return 0
    
    def clear_database(self) -> int:
        """清空数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM telegram_links")
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            print(f"[DB] 清空数据库时出错: {e}")
            return 0

class APIKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API密钥管理")
        self.setModal(True)
        self.resize(500, 300)
        
        layout = QFormLayout(self)
        
        self.name_edit = QLineEdit()
        self.api_key_edit = QLineEdit()
        self.api_secret_edit = QLineEdit()
        self.access_token_edit = QLineEdit()
        self.access_token_secret_edit = QLineEdit()
        
        # 设置密码模式
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_secret_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.access_token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.access_token_secret_edit.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addRow("名称:", self.name_edit)
        layout.addRow("API Key:", self.api_key_edit)
        layout.addRow("API Secret:", self.api_secret_edit)
        layout.addRow("Access Token:", self.access_token_edit)
        layout.addRow("Access Token Secret:", self.access_token_secret_edit)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
    def get_data(self):
        return {
            "name": self.name_edit.text(),
            "api_key": self.api_key_edit.text(),
            "api_secret": self.api_secret_edit.text(),
            "access_token": self.access_token_edit.text(),
            "access_token_secret": self.access_token_secret_edit.text()
        }
    
    def set_data(self, data):
        self.name_edit.setText(data.get("name", ""))
        self.api_key_edit.setText(data.get("api_key", ""))
        self.api_secret_edit.setText(data.get("api_secret", ""))
        self.access_token_edit.setText(data.get("access_token", ""))
        self.access_token_secret_edit.setText(data.get("access_token_secret", ""))

class SearchPanel(QWidget):
    """搜索面板组件"""
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("数据查询")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # 搜索表单
        form_layout = QFormLayout()
        
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("输入关键词")
        form_layout.addRow("关键词:", self.keyword_input)
        
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("链接包含的内容")
        form_layout.addRow("链接:", self.link_input)
        
        layout.addLayout(form_layout)
        
        # 搜索按钮
        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self.perform_search)
        layout.addWidget(self.search_btn)
        
        # 清空按钮
        self.clear_btn = QPushButton("清空条件")
        self.clear_btn.clicked.connect(self.clear_search)
        layout.addWidget(self.clear_btn)
        
        # 结果显示区域
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(["ID", "链接", "来源", "关键字", "创建时间"])
        self.result_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # 禁止编辑
        self.result_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)  # 选择整行
        layout.addWidget(self.result_table)
        
        # 删除按钮
        delete_layout = QHBoxLayout()
        self.delete_selected_btn = QPushButton("删除选中项")
        self.delete_selected_btn.clicked.connect(self.delete_selected)
        self.delete_selected_btn.setStyleSheet("background-color: #ff4444; color: white;")
        delete_layout.addWidget(self.delete_selected_btn)
        
        self.delete_by_keyword_btn = QPushButton("按关键词删除")
        self.delete_by_keyword_btn.clicked.connect(self.delete_by_keyword)
        self.delete_by_keyword_btn.setStyleSheet("background-color: #ff8800; color: white;")
        delete_layout.addWidget(self.delete_by_keyword_btn)
        
        delete_layout.addStretch()
        layout.addLayout(delete_layout)
        
        # 初始加载所有数据 - 延迟加载以避免初始化问题
        # self.load_all_data()  # 暂时注释，等窗口显示后再加载
        
    def load_all_data(self):
        """加载所有数据"""
        try:
            links = self.db_manager.get_all_links()
            self.display_results(links)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载数据时出错: {e}")
    
    def perform_search(self):
        """执行搜索"""
        keyword = self.keyword_input.text().strip()
        link_contains = self.link_input.text().strip()
        
        try:
            links = self.db_manager.search_links(keyword, link_contains)
            self.display_results(links)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"搜索时出错: {e}")
    
    def clear_search(self):
        """清空搜索条件"""
        self.keyword_input.clear()
        self.link_input.clear()
        self.load_all_data()
    
    def display_results(self, links):
        """显示搜索结果"""
        self.result_table.setRowCount(len(links))
        
        for row, link_info in enumerate(links):
            self.result_table.setItem(row, 0, QTableWidgetItem(str(link_info['id'])))
            self.result_table.setItem(row, 1, QTableWidgetItem(link_info['link']))
            self.result_table.setItem(row, 2, QTableWidgetItem(link_info['source']))
            self.result_table.setItem(row, 3, QTableWidgetItem(link_info['keyword']))
            self.result_table.setItem(row, 4, QTableWidgetItem(link_info['created_at']))
        
        # 调整列宽
        self.result_table.resizeColumnsToContents()
        self.result_table.resizeRowsToContents()
    
    def delete_selected(self):
        """删除选中的行"""
        selection_model = self.result_table.selectionModel()
        if selection_model is None:
            QMessageBox.information(self, "提示", "无法获取选择模型")
            return
            
        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "提示", "请先选择要删除的行")
            return
        
        reply = QMessageBox.question(self, "确认删除", f"确定要删除选中的 {len(selected_rows)} 条记录吗？",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                deleted_count = 0
                # 从后往前删除，避免索引变化
                for index in reversed(selected_rows):
                    row = index.row()
                    id_item = self.result_table.item(row, 0)
                    if id_item:
                        link_id = int(id_item.text())
                        if self.db_manager.delete_link(link_id):
                            deleted_count += 1
                
                # 重新加载数据
                self.load_all_data()
                QMessageBox.information(self, "成功", f"成功删除 {deleted_count} 条记录")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除记录时出错: {e}")
    
    def delete_by_keyword(self):
        """按关键词删除"""
        keyword = self.keyword_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "警告", "请先在关键词输入框中输入要删除的关键词")
            return
        
        # 确认删除
        reply = QMessageBox.question(self, "确认删除", f"确定要删除所有关键词为 '{keyword}' 的记录吗？",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                deleted_count = self.db_manager.delete_links_by_keyword(keyword)
                self.load_all_data()
                QMessageBox.information(self, "成功", f"成功删除 {deleted_count} 条记录")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除记录时出错: {e}")

class Worker(QObject):
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(list)
    finished_signal = pyqtSignal()

    def __init__(self, args, use_api=False, api_keys=None):
        super().__init__()
        self.args = args
        self.use_api = use_api
        self.api_keys = api_keys or {}

    @pyqtSlot()
    def run(self):
        try:
            if self.use_api and self.args[0] == "search":
                # 使用Twitter API
                worker_path = Path(__file__).parent.parent / "crawler" / "layer4_twitter_api.py"
                cmd = [sys.executable, str(worker_path)]
                
                # 添加API密钥参数
                cmd.extend([
                    self.api_keys.get("api_key", ""),
                    self.api_keys.get("api_secret", ""),
                    self.api_keys.get("access_token", ""),
                    self.api_keys.get("access_token_secret", ""),
                    self.args[1]  # keyword
                ])
            else:
                # 使用默认的Selenium爬虫
                worker_path = Path(__file__).parent.parent / "crawler" / "layer3_selenium.py"
                cmd = [sys.executable, str(worker_path)] + self.args
                
            proc = subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    text=True)
            
            json_output = ""
            if proc.stdout:
                for line in proc.stdout:
                    line = line.strip()
                    if line:
                        self.log_signal.emit(line)
                        # 尝试解析 JSON 结果
                        if line.startswith('[') and line.endswith(']'):
                            json_output = line
            
            proc.wait()
            
            # 处理搜索结果
            if (self.args[0] == "search" or (self.use_api and self.args[0] == "search")) and json_output:
                try:
                    results = json.loads(json_output)
                    self.log_signal.emit(f"解析到 {len(results)} 个结果")
                    self.result_signal.emit(results)
                except json.JSONDecodeError as e:
                    self.log_signal.emit(f"JSON 解析错误: {e}")
                except Exception as e:
                    self.log_signal.emit(f"处理结果时出错: {e}")
        except Exception as e:
            self.log_signal.emit(f"执行任务时出错: {e}")
        finally:
            self.finished_signal.emit()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        print("开始初始化 MainWindow")  # 调试信息
        
        self.setWindowTitle("X/T.me 抓取工具")
        self.resize(1200, 700)
        
        # 当前运行的工作线程和对象 - 初始化为None
        self.worker_thread = None
        self.worker = None
        
        # API密钥
        self.api_keys = self.load_api_keys()
        self.current_api_key = None
        
        # 数据库管理器 - 延迟初始化
        self.db_manager = None
        
        # 设置窗口属性，确保显示
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)

        # 创建主布局
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建水平分割器
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        # 创建主要内容区域
        self.main_content = QWidget()
        self.setup_main_content()
        self.splitter.addWidget(self.main_content)
        
        # 搜索面板 - 延迟创建
        self.search_panel = None
        
        # 创建切换按钮
        self.toggle_button = QPushButton("▶")
        self.toggle_button.setFixedSize(30, 60)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_search_panel)
        
        # 将切换按钮添加到主窗口布局中
        self.main_layout.addWidget(self.toggle_button)
        
        print("MainWindow 基本初始化完成")
        
        # 延迟初始化数据库相关组件
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.delayed_init)
        
        print("MainWindow 初始化完成")
        
    def setup_main_content(self):
        layout = QVBoxLayout(self.main_content)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 创建搜索标签页
        self.search_tab = QWidget()
        self.setup_search_tab()
        self.tab_widget.addTab(self.search_tab, "搜索")
        
        # 创建数据库查看标签页
        self.database_tab = QWidget()
        self.setup_database_tab()
        self.tab_widget.addTab(self.database_tab, "数据库")

    def setup_search_tab(self):
        layout = QVBoxLayout(self.search_tab)
        
        # API密钥选择区域
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("API密钥:"))
        self.api_key_combo = QComboBox()
        self.api_key_combo.setMinimumWidth(200)
        self.update_api_key_combo()
        api_layout.addWidget(self.api_key_combo)
        
        self.btn_manage_api_keys = QPushButton("管理API密钥")
        self.btn_manage_api_keys.clicked.connect(self.manage_api_keys)
        api_layout.addWidget(self.btn_manage_api_keys)
        
        self.btn_use_api = QPushButton("使用API搜索")
        self.btn_use_api.setCheckable(True)
        self.btn_use_api.toggled.connect(self.toggle_api_usage)
        api_layout.addWidget(self.btn_use_api)
        
        api_layout.addStretch()
        layout.addLayout(api_layout)
        
        # 搜索区域
        self.input = QLineEdit()
        self.input.setPlaceholderText("输入关键字")
        layout.addWidget(self.input)

        self.btn_start_browser = QPushButton("一键登录 X (Twitter)")
        self.btn_start_browser.clicked.connect(self.start_browser_login)
        self.btn_start_browser.setStyleSheet("background-color: #1da1f2; color: white; font-weight: bold; padding: 8px;")
        layout.addWidget(self.btn_start_browser)

        self.btn_confirm_login = QPushButton("确认登录完成")
        self.btn_confirm_login.clicked.connect(self.confirm_login)
        self.btn_confirm_login.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 8px;")
        layout.addWidget(self.btn_confirm_login)

        self.btn_search = QPushButton("开始抓取")
        self.btn_search.clicked.connect(self.start_search)
        layout.addWidget(self.btn_search)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["关键字","t.me 链接","来源"])
        layout.addWidget(self.table)

        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        self.next_row = 0

    def setup_database_tab(self):
        layout = QVBoxLayout(self.database_tab)
        
        # 数据库操作按钮
        db_buttons_layout = QHBoxLayout()
        self.btn_refresh_db = QPushButton("刷新数据库")
        self.btn_refresh_db.clicked.connect(self.refresh_database_view)
        db_buttons_layout.addWidget(self.btn_refresh_db)
        
        self.btn_clear_db = QPushButton("清空数据库")
        self.btn_clear_db.clicked.connect(self.clear_database)
        self.btn_clear_db.setStyleSheet("background-color: #ff4444; color: white;")
        db_buttons_layout.addWidget(self.btn_clear_db)
        
        db_buttons_layout.addStretch()
        layout.addLayout(db_buttons_layout)
        
        # 数据库内容显示
        self.db_table = QTableWidget()
        self.db_table.setColumnCount(5)
        self.db_table.setHorizontalHeaderLabels(["ID", "链接", "来源", "关键字", "创建时间"])
        self.db_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # 禁止编辑
        self.db_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)  # 选择整行
        layout.addWidget(self.db_table)
        
        # 数据库删除操作按钮
        delete_layout = QHBoxLayout()
        self.btn_delete_selected = QPushButton("删除选中项")
        self.btn_delete_selected.clicked.connect(self.delete_selected_from_db)
        self.btn_delete_selected.setStyleSheet("background-color: #ff4444; color: white;")
        delete_layout.addWidget(self.btn_delete_selected)
        
        self.btn_delete_by_keyword = QPushButton("按当前关键词删除")
        self.btn_delete_by_keyword.clicked.connect(self.delete_by_current_keyword)
        self.btn_delete_by_keyword.setStyleSheet("background-color: #ff8800; color: white;")
        delete_layout.addWidget(self.btn_delete_by_keyword)
        
        delete_layout.addStretch()
        layout.addLayout(delete_layout)

    def delayed_init(self):
        """延迟初始化数据库相关组件"""
        try:
            print("开始延迟初始化")
            
            # 初始化数据库管理器
            self.db_manager = DatabaseManager()
            print("数据库管理器初始化完成")
            
            # 创建搜索面板
            self.search_panel = SearchPanel(self.db_manager)
            self.search_panel.setMinimumWidth(400)
            self.search_panel.setMaximumWidth(600)
            self.splitter.insertWidget(1, self.search_panel)  # 插入到正确位置
            
            # 设置分割器初始大小
            self.splitter.setSizes([800, 400])
            
            # 隐藏搜索面板（初始状态）
            self.search_panel.setVisible(False)
            
            print("搜索面板创建完成")
            
            # 加载初始数据
            self.refresh_database_view()
            if self.search_panel:
                self.search_panel.load_all_data()
            
            print("延迟初始化完成")
            
        except Exception as e:
            print(f"延迟初始化时出错: {e}")
    
    def toggle_search_panel(self):
        """切换搜索面板的显示/隐藏"""
        if self.search_panel is None:
            print("搜索面板尚未初始化")
            return
            
        if self.search_panel.isVisible():
            # 隐藏面板
            self.search_panel.setVisible(False)
            self.toggle_button.setText("▶")
        else:
            # 显示面板
            self.search_panel.setVisible(True)
            self.toggle_button.setText("◀")
            
        # 调整分割器大小
        self.splitter.setSizes([self.splitter.width() - 50, 50] if not self.search_panel.isVisible() 
                              else [self.splitter.width() - 450, 450])

    def log(self, msg):
        self.log_area.appendPlainText(msg)

    def add_result_row(self, keyword, link, source):
        # 检查是否已存在相同的链接
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            if item and item.text() == link:
                return
        
        self.table.insertRow(self.next_row)
        self.table.setItem(self.next_row, 0, QTableWidgetItem(keyword))
        self.table.setItem(self.next_row, 1, QTableWidgetItem(link))
        self.table.setItem(self.next_row, 2, QTableWidgetItem(source))
        self.next_row += 1

    def process_results(self, results):
        try:
            keyword = self.input.text().strip()
            for result in results:
                link = result.get('link', '')
                source = result.get('source', '')
                if link:
                    self.add_result_row(keyword, link, source)
            
            if not results:
                self.log("未找到任何 t.me 链接")
            else:
                self.log(f"成功处理 {len(results)} 个结果")
        except Exception as e:
            self.log(f"处理结果时出错: {e}")

    def cleanup_thread(self):
        """安全地清理工作线程"""
        if self.worker_thread is not None:
            try:
                if self.worker_thread.isRunning():
                    # 先停止工作对象
                    if self.worker is not None:
                        # 如果worker有停止方法，调用它（这里只是示例，实际Worker类没有stop方法）
                        pass  # worker没有stop方法，跳过
                    
                    # 等待线程结束
                    self.worker_thread.quit()
                    if not self.worker_thread.wait(3000):  # 等待3秒
                        # 如果线程没有在3秒内结束，强制终止
                        self.worker_thread.terminate()
                        self.worker_thread.wait(1000)  # 再等1秒
                
                # 清理引用
                self.worker_thread.deleteLater()
                if self.worker is not None:
                    self.worker.deleteLater()
                    
            except Exception as e:
                print(f"清理线程时出错: {e}")
            
            finally:
                self.worker_thread = None
                self.worker = None

    def update_api_key_combo(self):
        self.api_key_combo.clear()
        for key in self.api_keys:
            self.api_key_combo.addItem(key["name"], key)
        
    def load_api_keys(self):
        keys_file = Path("twitter_api_keys.json")
        if keys_file.exists():
            try:
                with open(keys_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.log(f"加载API密钥失败: {e}")
                return []
        return []
    
    def save_api_keys(self):
        try:
            with open("twitter_api_keys.json", "w") as f:
                json.dump(self.api_keys, f, indent=2)
        except Exception as e:
            self.log(f"保存API密钥失败: {e}")

    # ---------------- 数据库操作 ----------------
    def refresh_database_view(self):
        """刷新数据库视图"""
        try:
            if self.db_manager is None:
                print("数据库管理器尚未初始化")
                return
                
            links = self.db_manager.get_all_links()
            self.db_table.setRowCount(len(links))
            
            for row, link_info in enumerate(links):
                self.db_table.setItem(row, 0, QTableWidgetItem(str(link_info['id'])))
                self.db_table.setItem(row, 1, QTableWidgetItem(link_info['link']))
                self.db_table.setItem(row, 2, QTableWidgetItem(link_info['source']))
                self.db_table.setItem(row, 3, QTableWidgetItem(link_info['keyword']))
                self.db_table.setItem(row, 4, QTableWidgetItem(link_info['created_at']))
                
            self.log(f"数据库刷新完成，共 {len(links)} 条记录")
        except Exception as e:
            self.log(f"刷新数据库视图时出错: {e}")

    def clear_database(self):
        """清空数据库"""
        if self.db_manager is None:
            QMessageBox.warning(self, "警告", "数据库管理器尚未初始化")
            return
            
        reply = QMessageBox.question(self, "确认", "确定要清空数据库吗？此操作不可恢复！",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                deleted_count = self.db_manager.clear_database()
                self.refresh_database_view()
                self.log(f"数据库已清空，共删除 {deleted_count} 条记录")
                # 同时刷新搜索面板
                if self.search_panel is not None:
                    self.search_panel.load_all_data()
            except Exception as e:
                self.log(f"清空数据库时出错: {e}")
    
    def delete_selected_from_db(self):
        """从数据库标签页删除选中的记录"""
        if self.db_manager is None:
            QMessageBox.warning(self, "警告", "数据库管理器尚未初始化")
            return
            
        selection_model = self.db_table.selectionModel()
        if selection_model is None:
            QMessageBox.warning(self, "警告", "无法获取选择模型")
            return
            
        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "提示", "请先选择要删除的行")
            return
        
        reply = QMessageBox.question(self, "确认删除", f"确定要删除选中的 {len(selected_rows)} 条记录吗？",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                deleted_count = 0
                # 从后往前删除，避免索引变化
                for index in reversed(selected_rows):
                    row = index.row()
                    id_item = self.db_table.item(row, 0)
                    if id_item:
                        link_id = int(id_item.text())
                        if self.db_manager.delete_link(link_id):
                            deleted_count += 1
                
                # 重新加载数据
                self.refresh_database_view()
                # 同时刷新搜索面板
                if self.search_panel is not None:
                    self.search_panel.load_all_data()
                self.log(f"成功删除 {deleted_count} 条记录")
            except Exception as e:
                self.log(f"删除记录时出错: {e}")
    
    def delete_by_current_keyword(self):
        """按当前搜索关键词删除"""
        if self.db_manager is None:
            QMessageBox.warning(self, "警告", "数据库管理器尚未初始化")
            return
            
        keyword = self.input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "警告", "请先输入关键词")
            return
        
        # 确认删除
        reply = QMessageBox.question(self, "确认删除", f"确定要删除所有关键词为 '{keyword}' 的记录吗？",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                deleted_count = self.db_manager.delete_links_by_keyword(keyword)
                self.refresh_database_view()
                # 同时刷新搜索面板
                if self.search_panel is not None:
                    self.search_panel.load_all_data()
                self.log(f"成功删除 {deleted_count} 条关键词为 '{keyword}' 的记录")
            except Exception as e:
                self.log(f"删除记录时出错: {e}")

    # ---------------- UI事件处理 ----------------
    def manage_api_keys(self):
        dialog = APIKeyDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data["name"] and data["api_key"]:
                # 检查是否已存在同名密钥
                existing_index = None
                for i, key in enumerate(self.api_keys):
                    if key["name"] == data["name"]:
                        existing_index = i
                        break
                
                if existing_index is not None:
                    self.api_keys[existing_index] = data
                else:
                    self.api_keys.append(data)
                
                self.save_api_keys()
                self.update_api_key_combo()
                
    def toggle_api_usage(self, checked):
        if checked:
            if self.api_key_combo.currentIndex() >= 0:
                self.current_api_key = self.api_key_combo.currentData()
                self.log("已启用Twitter API搜索")
            else:
                self.log("请先添加并选择API密钥")
                self.btn_use_api.setChecked(False)
                self.current_api_key = None
        else:
            self.current_api_key = None
            self.log("已禁用Twitter API搜索，使用默认爬虫")

    # ---------------- 子进程调用 ----------------
    def run_worker(self, args):
        # 清理之前的线程
        self.cleanup_thread()
        
        # 创建新的线程和工作对象
        self.worker_thread = QThread()
        self.worker = Worker(args, self.btn_use_api.isChecked(), self.current_api_key)
        
        # 将工作对象移动到线程
        self.worker.moveToThread(self.worker_thread)
        
        # 连接信号和槽
        self.worker_thread.started.connect(self.worker.run)
        self.worker.log_signal.connect(self.log)
        self.worker.result_signal.connect(self.process_results)
        self.worker.finished_signal.connect(self.worker_thread.quit)
        self.worker.finished_signal.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.finished.connect(self.on_worker_finished)
        
        # 启动线程
        self.worker_thread.start()

    def on_worker_finished(self):
        self.worker_thread = None
        self.worker = None
        # 刷新数据库视图
        self.refresh_database_view()
        # 刷新搜索面板
        if self.search_panel is not None:
            self.search_panel.load_all_data()

    def start_browser_login(self):
        """一键登录功能，直接启动浏览器并完成登录流程"""
        self.run_worker(["login"])

    def start_browser(self):
        """保留原有的方法名称以保持兼容性"""
        self.start_browser_login()

    def confirm_login(self):
        """确认登录完成（现在主要用于向后兼容）"""
        self.run_worker(["save_login"])

    def start_search(self):
        keyword = self.input.text().strip()
        if not keyword:
            QMessageBox.warning(self,"提示","请输入关键字")
            return
        self.table.setRowCount(0)
        self.next_row=0
        self.log_area.clear()
        self.run_worker(["search", keyword])

    def closeEvent(self, a0: Optional[QCloseEvent]):
        """窗口关闭事件处理"""
        print("正在关闭应用...")  # 添加调试信息
        try:
            # 确保工作线程已完成
            self.cleanup_thread()
            print("线程清理完成")
            
            # 接受关闭事件
            if a0 is not None:
                a0.accept()
            print("应用关闭完成")
        except Exception as e:
            print(f"关闭应用时出错: {e}")
            if a0 is not None:
                a0.accept()  # 仍然关闭应用
