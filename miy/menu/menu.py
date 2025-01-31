import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QScrollArea

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("导航栏示例")
        self.setGeometry(100, 100, 800, 600)

        # 创建主布局
        main_layout = QHBoxLayout()

        # 创建导航栏容器
        nav_container = QWidget()
        nav_container.setFixedWidth(200)
        self.nav_layout = QVBoxLayout(nav_container)  # 导航栏使用垂直布局
        self.nav_layout.setSpacing(5)  # 设置按钮之间的间距
        self.nav_layout.setContentsMargins(5, 5, 5, 5)  # 设置边距

        # 将导航栏容器放入滚动区域（如果按钮很多，可以滚动）
        scroll_area = QScrollArea()
        scroll_area.setWidget(nav_container)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        # 创建右侧内容区域
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: #f0f0f0;")
        main_layout.addWidget(self.content_area)

        # 创建添加按钮
        self.add_button = QPushButton("添加导航按钮")
        self.add_button.clicked.connect(self.add_nav_button)

        # 创建主窗口的布局
        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        # 创建整体布局
        layout = QVBoxLayout()
        layout.addWidget(main_widget)
        layout.addWidget(self.add_button)

        # 设置中心窗口
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def add_nav_button(self):
        """动态添加导航按钮"""
        button = QPushButton(f"按钮 {self.nav_layout.count() + 1}")
        button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                padding: 10px;
                border: none;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        button.clicked.connect(lambda _, b=button: self.on_nav_button_clicked(b))
        self.nav_layout.addWidget(button)

    def on_nav_button_clicked(self, button):
        """导航按钮点击事件"""
        print(f"点击了: {button.text()}")
        # 在这里可以更新右侧内容区域的内容
        self.content_area.setStyleSheet(f"background-color: #f0f0f0; font-size: 16px;")
        self.content_area.setWindowTitle(button.text())  # 示例：更新窗口标题

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())