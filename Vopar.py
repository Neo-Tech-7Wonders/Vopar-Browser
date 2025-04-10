import sys
from PyQt5.QtCore import QUrl, Qt, QPropertyAnimation, QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QVBoxLayout, QWidget, QToolBar, QAction, QTabWidget, QPushButton, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor

# Add this new class for ad blocking
class AdBlocker(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()
        self.ad_domains = {
            'ads.', 'doubleclick.net', 'google-analytics.com',
            'adnxs.com', 'advertising.com', 'admob.',
            'ad.', 'analytics.', 'tracker.', 'banner.',
            'popup.', 'stats.', 'pixel.'
        }

    def interceptRequest(self, info):
        url = info.requestUrl().toString().lower()
        # Block if URL contains any ad domain
        if any(ad_domain in url for ad_domain in self.ad_domains):
            info.block(True)

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vopar")
        self.setGeometry(100, 100, 1200, 800)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)

        # Add tab button
        self.new_tab_button = QPushButton("+")
        self.new_tab_button.clicked.connect(lambda: self.add_tab("https://www.bing.com"))
        self.tabs.setCornerWidget(self.new_tab_button)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search the web...")
        self.search_bar.returnPressed.connect(self.search_web)

        # Toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        back_action = QAction("<", self)
        back_action.triggered.connect(self.navigate_back)
        self.toolbar.addAction(back_action)

        forward_action = QAction(">", self)
        forward_action.triggered.connect(self.navigate_forward)
        self.toolbar.addAction(forward_action)

        # Add ad blocking
        self.ad_blocker = AdBlocker()
        QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(self.ad_blocker)

        # Add ad blocker toggle button to toolbar
        self.ad_block_action = QAction("🛡️ Ads Blocked", self)
        self.ad_block_action.setCheckable(True)
        self.ad_block_action.setChecked(True)
        self.ad_block_action.triggered.connect(self.toggle_ad_blocker)
        self.toolbar.addAction(self.ad_block_action)

        # Loading Animation
        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setText("🔄")  # Unicode spinner icon or any symbol
        self.loading_label.setFixedSize(50, 50)
        self.loading_label.hide()

        self.loading_animation = QPropertyAnimation(self.loading_label, b"geometry")
        self.loading_animation.setDuration(1000)
        self.loading_animation.setLoopCount(-1)  # Infinite loop
        self.loading_animation.setStartValue(QRect(50, 50, 50, 50))  # Start position
        self.loading_animation.setEndValue(QRect(60, 50, 50, 50))  # End position (move slightly)

        # Main layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.url_bar)
        self.layout.addWidget(self.search_bar)
        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.loading_label)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Initialize with the first tab
        self.add_tab("file:///C:/Users/fidge/OneDrive/Desktop/Documentos/codes/python/welcome.html")

    def add_tab(self, url="www.bing.com"):
        new_browser = QWebEngineView()
        new_browser.setUrl(QUrl(url))
        new_browser.urlChanged.connect(self.update_url_bar_from_browser)
        new_browser.loadStarted.connect(self.show_loading)
        new_browser.loadFinished.connect(self.hide_loading)
        self.tabs.addTab(new_browser, f"Tab {self.tabs.count() + 1}")
        self.tabs.setCurrentWidget(new_browser)

    def show_loading(self):
        self.loading_label.show()
        self.loading_animation.start()

    def hide_loading(self):
        self.loading_animation.stop()
        self.loading_label.hide()

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        current_browser = self.tabs.currentWidget()
        if isinstance(current_browser, QWebEngineView):
            current_browser.setUrl(QUrl(url))

    def search_web(self):
        query = self.search_bar.text()
        search_url = f"https://www.bing.com/search?q={query}"
        current_browser = self.tabs.currentWidget()
        if isinstance(current_browser, QWebEngineView):
            current_browser.setUrl(QUrl(search_url))

    def update_url_bar(self, index):
        current_browser = self.tabs.widget(index)
        if isinstance(current_browser, QWebEngineView):
            self.url_bar.setText(current_browser.url().toString())

    def update_url_bar_from_browser(self, url):
        self.url_bar.setText(url.toString())

    def navigate_back(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.back()

    def navigate_forward(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.forward()

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def toggle_ad_blocker(self):
        if self.ad_block_action.isChecked():
            QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(self.ad_blocker)
            self.ad_block_action.setText("🛡️ Ads Blocked")
        else:
            QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(None)
            self.ad_block_action.setText("🛡️ Ads Allowed")

        # Reload current tab to apply changes
        current_browser = self.tabs.currentWidget()
        if isinstance(current_browser, QWebEngineView):
            current_browser.reload()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())
