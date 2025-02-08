import math
import os
import sys

import cv2
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea, QDialog, \
    QProgressDialog
from PyQt6.QtCore import Qt, QEvent


import cv2
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QSizePolicy, QApplication
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QTimer, Qt

class ImageDialog(QDialog):
    def __init__(self, media_path):
        super().__init__()
        self.setWindowTitle(media_path)
        self.resize(800, 600)
        self.setMinimumSize(300, 200)  # 设置最小窗口大小
        self.setStyleSheet("background-color: black;")

        # 创建媒体标签
        self.media_label = QLabel()
        self.media_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.media_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.media_label)
        self.setLayout(layout)

        # 媒体相关属性
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # 判断是图片还是视频
        if media_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            self.display_image(media_path)
        elif media_path.lower().endswith(('.avi', '.mp4')):
            self.open_video_file(media_path)
        self.center_on_screen()

    def display_image(self, image_path):
        pixmap = QPixmap(image_path)
        self.media_label.setPixmap(
            pixmap.scaled(self.media_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def open_video_file(self, video_path):
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            print("无法打开视频文件")
            return
        self.timer.start(30)  # 每30毫秒更新一次

    def update_frame(self):
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                self.timer.stop()
                return

            # 将 BGR 转换为 RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 缩放视频帧以适应 QLabel
            scaled_frame = self.scale_frame(frame, self.media_label.size())

            # 转换为 QImage
            h, w, ch = scaled_frame.shape
            bytes_per_line = ch * w
            q_image = QImage(scaled_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

            # 更新 QLabel
            self.media_label.setPixmap(QPixmap.fromImage(q_image))

    def scale_frame(self, frame, size):
        return cv2.resize(frame, (size.width(), size.height()), interpolation=cv2.INTER_AREA)

    def closeEvent(self, event):
        if self.cap is not None:
            self.cap.release()
        event.accept()

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()  # 获取屏幕大小
        window_rect = self.frameGeometry()  # 获取窗口大小
        center_point = screen.center()  # 获取屏幕中心点
        window_rect.moveCenter(center_point)  # 将窗口中心移动到屏幕中心
        self.move(window_rect.topLeft())  # 设置窗口位置

    def resizeEvent(self, event):
        # 调整图像显示
        if self.cap is None:  # 仅在显示图片时调整
            self.display_image(self.windowTitle())  # 重新加载当前显示的图片
        else:
            # 对于视频，更新当前帧的显示
            self.update_frame()
        super().resizeEvent(event)  # 调用基类的 resizeEvent


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
        self.file_path = "video"
        self.boxes = []
        self.init_grid()
        self.update_grid()
        self.image_dialog = []
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
        progress_dialog = QProgressDialog()
        # 获取文件夹中所有文件
        try:
            files = os.listdir(self.file_path)
            image_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png', 'avi', 'mp4'))]  # 过滤出图片文件和视频文件

            if len(image_files) > 100:
                # 创建进度对话框
                progress_dialog = QProgressDialog("加载中，请稍候...", "取消", 0, len(image_files), self)
                progress_dialog.setWindowTitle("加载进度")
                progress_dialog.setModal(True)  # 设置为模态
                progress_dialog.setValue(0)
                progress_dialog.show()

            for i, image_file in enumerate(image_files):
                box = QWidget()
                box.setMinimumSize(99, 99)  # 设置成小于100的值以防无法缩小组件
                box.setMaximumSize(100, 100)

                # 创建标签
                label = QLabel(f"{i}")
                label.setStyleSheet("color: red;")

                # 判断文件类型并加载相应的内容
                if image_file.endswith(('.avi', '.mp4')):  # 视频文件
                    cap = cv2.VideoCapture(os.path.join(self.file_path, image_file))
                    ret, frame = cap.read()  # 读取第一帧
                    if ret:
                        # 转换为 QPixmap
                        height, width, channel = frame.shape
                        bytes_per_line = 3 * width
                        qimg = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
                        pixmap = QPixmap.fromImage(qimg)
                        label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))  # 设置图片大小
                    cap.release()
                else:  # 图片文件
                    pixmap = QPixmap(os.path.join(self.file_path, image_file))  # 加载图片
                    label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))  # 设置图片大小

                label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中对齐

                # 布局
                box_layout = QVBoxLayout(box)
                box_layout.addWidget(label)

                # 创建名称标签
                name_label = QLabel(image_file)  # 显示文件名
                if image_file.endswith(('.avi', '.mp4')):  # 如果是视频文件
                    name_label.setStyleSheet("color: green; background-color: transparent;")  # 绿色字体
                else:
                    name_label.setStyleSheet("color: black; background-color: transparent;")  # 黑色字体

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

                if len(image_files) > 100:
                    progress_dialog.setValue(i + 1)  # 更新进度条
                if progress_dialog.wasCanceled():
                    break  # 如果用户点击了取消，则退出循环

            if len(image_files) > 100:
                progress_dialog.close()  # 加载完成后关闭进度对话框

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
            self.image_dialog.append(dialog)
            dialog.setWindowModality(Qt.WindowModality.NonModal)  # 设置为非模态
            dialog.show()  # 以非模态方式显示对话框

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
