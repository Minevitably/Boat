import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QScrollArea, QFileDialog, QPushButton
)
from PyQt6.QtGui import QPixmap

class PhotoAlbumApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("相册程序 - PyQt6")
        self.setGeometry(100, 100, 800, 600)

        # 主布局
        main_layout = QVBoxLayout()

        # 顶部按钮布局
        button_layout = QHBoxLayout()
        self.open_button = QPushButton("打开文件夹")
        self.open_button.clicked.connect(self.open_folder)
        button_layout.addWidget(self.open_button)
        main_layout.addLayout(button_layout)

        # 图片显示区域
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

    def open_folder(self):
        """打开文件夹并加载图片"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_path:
            self.load_images(folder_path)

    def load_images(self, folder_path):
        """加载文件夹中的所有 JPG 图片"""
        # 清空当前图片
        for i in reversed(range(self.image_grid.count())):
            self.image_grid.itemAt(i).widget().setParent(None)

        # 获取文件夹中的所有 JPG 文件
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]
        if not image_files:
            print("文件夹中没有 JPG 文件")
            return

        # 加载图片并显示
        for i, image_file in enumerate(image_files):
            row = i // 3  # 计算行
            col = i % 3   # 计算列

            # 创建 QLabel 并加载图片
            label = QLabel()
            pixmap = QPixmap(os.path.join(folder_path, image_file))
            if pixmap.isNull():
                print(f"图片加载失败: {image_file}")
                label.setText("图片未找到")
            else:
                label.setPixmap(pixmap.scaled(200, 200))  # 缩放图片为缩略图

            # 将 QLabel 添加到网格布局中
            self.image_grid.addWidget(label, row, col)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建主窗口
    window = PhotoAlbumApp()
    window.show()

    sys.exit(app.exec())