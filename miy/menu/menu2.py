import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QScrollArea
)
from PyQt6.QtGui import QPixmap

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("相册软件")
        self.setGeometry(100, 100, 800, 600)

        # 主布局
        main_layout = QHBoxLayout()

        # 左侧导航栏
        self.nav_layout = QVBoxLayout()
        self.nav_layout.setSpacing(10)
        self.nav_layout.setContentsMargins(10, 10, 10, 10)

        # 添加分类按钮
        self.add_category_button("分类1")
        self.add_category_button("分类2")
        self.add_category_button("分类3")

        # 将导航栏放入容器
        nav_container = QWidget()
        nav_container.setLayout(self.nav_layout)
        nav_container.setFixedWidth(150)
        main_layout.addWidget(nav_container)

        # 右侧图片区域
        self.image_grid = QGridLayout()
        self.image_grid.setSpacing(10)
        self.image_grid.setContentsMargins(10, 10, 10, 10)

        # 将图片区域放入滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        image_container = QWidget()
        image_container.setLayout(self.image_grid)
        scroll_area.setWidget(image_container)
        main_layout.addWidget(scroll_area)

        # 设置主窗口的中心部件
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def add_category_button(self, name):
        """添加分类按钮"""
        button = QPushButton(name)
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
        button.clicked.connect(lambda _, n=name: self.show_category_images(n))
        self.nav_layout.addWidget(button)

    def show_category_images(self, category):
        """显示分类图片"""
        print(f"显示分类: {category}")

        # 清空当前图片
        for i in reversed(range(self.image_grid.count())):
            self.image_grid.itemAt(i).widget().setParent(None)

        # 加载图片（假设图片路径为固定格式）
        for i in range(6):  # 6 张图片
            row = i // 3  # 计算行
            col = i % 3   # 计算列

            # 创建 QLabel 并加载图片
            label = QLabel()
            pixmap = QPixmap(f"images/{category}/image{i+1}.jpg")  # 假设图片路径为 images/分类X/imageY.jpg
            if pixmap.isNull():
                print(f"图片加载失败: images/{category}/image{i+1}.jpg")
                label.setText("图片未找到")
            else:
                label.setPixmap(pixmap.scaled(200, 200))  # 缩放图片

            # 将 QLabel 添加到网格布局中
            self.image_grid.addWidget(label, row, col)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建主窗口
    window = MainWindow()
    window.show()

    sys.exit(app.exec())