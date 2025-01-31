import math
import os
import sys

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea, QDialog
from PyQt6.QtCore import Qt, QEvent




class ImageDialog(QDialog):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle(image_path)
        self.resize(800, 600)  # 使用 resize 代替 setGeometry 以便后续调整居中
        self.setStyleSheet("background-color: black;")  # 设置背景颜色

        # 创建图片标签
        pixmap = QPixmap(image_path)
        label = QLabel()
        label.setPixmap(
            pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

        # 居中窗口
        self.center_on_screen()

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()  # 获取屏幕大小
        window_rect = self.frameGeometry()  # 获取窗口大小
        center_point = screen.center()  # 获取屏幕中心点
        window_rect.moveCenter(center_point)  # 将窗口中心移动到屏幕中心
        self.move(window_rect.topLeft())  # 设置窗口位置


class MGridWidget(QWidget):
    def __init__(self):
        super().__init__()

        # 创建一个 QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # 使内容自适应滚动区大小

        # 创建一个内部 widget 用于添加 grid layout
        self.scroll_content = QWidget()
        self.layout = QGridLayout(self.scroll_content)  # 将 grid layout 设置为 scroll_content 的布局

        self.scroll_area.setWidget(self.scroll_content)  # 将内部 widget 设置为滚动区域的内容
        self.file_path = "picture"
        self.boxes = []
        self.init_grid()
        self.update_grid()

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 设置主布局的边距为0
        main_layout.addWidget(self.scroll_area)  # 将滚动区域添加到主布局

    def update_file_path(self, file_path):
        self.file_path = file_path
        self.init_grid()
        self.update_grid()

    def init_grid(self):
        self.boxes = []

        # 获取文件夹中所有文件
        try:
            files = os.listdir(self.file_path)
            image_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png'))]  # 过滤出图片文件

            for i, image_file in enumerate(image_files):
                box = QWidget()
                box.setMinimumSize(99, 99)  # 设置成小于100的值以防无法缩小组件
                box.setMaximumSize(100, 100)

                # 创建图片标签
                label = QLabel(f"{i}")
                label.setStyleSheet("color: red;")
                pixmap = QPixmap(os.path.join(self.file_path, image_file))  # 加载图片
                label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))  # 设置图片大小

                label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中对齐

                # 布局
                box_layout = QVBoxLayout(box)
                box_layout.addWidget(label)

                name_label = QLabel(image_file)  # 显示图片文件名
                name_label.setStyleSheet("background-color: transparent;")  # 设置背景色为透明
                box_layout.addWidget(name_label)

                box_layout.setAlignment(label, Qt.AlignmentFlag.AlignCenter)

                # 添加 hover 效果
                box.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
                box.setStyleSheet("background-color: transparent;")  # 初始背景透明

                # 事件过滤器，用于 hover 效果
                box.installEventFilter(self)

                # 连接点击事件
                box.mousePressEvent = lambda event, img_path=os.path.join(self.file_path, image_file): self.show_image(
                    event, img_path)

                self.boxes.append(box)
        except FileNotFoundError:
            print(f"Directory {self.file_path} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.Enter and source in self.boxes:
            source.setStyleSheet("background-color: rgba(204, 232, 255, 0.8);")  # 鼠标进入时设置半透明蓝色
        elif event.type() == QEvent.Type.Leave and source in self.boxes:
            source.setStyleSheet("background-color: transparent;")  # 鼠标离开时恢复透明
        return super().eventFilter(source, event)

    def show_image(self, event, image_path):
        if event.button() == Qt.MouseButton.LeftButton:  # 确保是左键点击
            dialog = ImageDialog(image_path)
            dialog.exec()  # 显示对话框

    def update_grid(self):
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            widget.hide()  # 隐藏组件而不是删除

        # 计算当前窗口的列数和行数
        # 这里-50也许可以避免，先这么着吧
        total_width = self.scroll_area.width() - 50
        total_height = self.scroll_area.height()
        # print(total_width)
        # print(total_height)
        cols = total_width // 100  # 每个格子100像素宽
        rows = total_height // 100  # 每个格子100像素高

        new_rows = math.ceil(len(self.boxes) / cols)

        rows = max(rows, new_rows)
        i = 0
        # 创建新的格子
        for row in range(rows):
            for col in range(cols):
                if i < len(self.boxes):
                    self.layout.addWidget(self.boxes[i], row, col)
                    self.boxes[i].show()  # 显示组件
                    i += 1
                else:
                    # 添加一些空格子，把有图片的格子挤到上方
                    self.layout.addWidget(QWidget(), row, col)
        # print(i)

    def resizeEvent(self, event):
        # 窗口大小改变时更新格子
        self.update_grid()
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    grid_widget = MGridWidget()
    grid_widget.setWindowTitle("Dynamic Grid of Widgets")
    grid_widget.resize(400, 300)  # 设置窗口初始大小为 400x300
    grid_widget.show()
    sys.exit(app.exec())
