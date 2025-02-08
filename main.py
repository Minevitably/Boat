import os
import shutil
import sys

import cv2
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QWidget, QInputDialog, QMessageBox, QPushButton, QSpacerItem, QSizePolicy, QApplication, \
    QFileDialog, QProgressDialog, QDialog

from Form import Ui_Form
import xml.etree.ElementTree as ET

from miy.album.album import MGridWidget

from miy.clazz.manage import ClassManager
from model_apis import Yolov11Predict, DETRPredict, RCNNPredict, M1Predict, M2Predict, M3Predict, Yolov10Predict
from utils import FileSelectorDialog


class MWindow(QWidget, Ui_Form):

    def __init__(self):
        super().__init__()
        self.class_data = None
        self.noiseReductionMGridWidget = None
        self.detectMGridWidget = None
        self.currentUploadPath = None
        self.currentBtnName = None
        self.currentClassName = None
        self.classMGridWidget = None
        self.setupUi(self)
        self.setupEvent()
        # 默认显示空的二级菜单页面
        self.displayMenu(self.defaultMenuPage)
        # 默认显示系统简介视图页面
        self.displayView(self.defaultViewPage)
        self.xml_file_path = "class.xml"
        self.load_xml()

        # 一些初始化工作，例如将第二个页面的默认选中的分类设置为小船
        self.replaceWidget()
        self.detectModelFun = None
        self.noiseReductionModelFun = None

        # 这里有个神奇的bug，如果注释下面这一行classMGridWidget就会保持正常大小，现在classMGridWidget有点高
        # 但不影响系统正常运行，暂时不管
        self.on_class_button_click('small_ship', '小船', r'dataset\test\small_ship')
        self.center_on_screen()

    def replaceWidget(self):
        # 小目标存取页面的相册组件
        layout = self.classMGridWidget.layout()
        layout.itemAt(0).widget().deleteLater()
        self.classMGridWidget = MGridWidget()
        layout.addWidget(self.classMGridWidget)

        # 小目标检测页面的相册组件
        layout = self.detectMGridWidget.layout()
        layout.itemAt(0).widget().deleteLater()
        self.detectMGridWidget = MGridWidget()
        layout.addWidget(self.detectMGridWidget)

        # 小目标去噪页面的相册组件
        layout = self.noiseReductionMGridWidget.layout()
        layout.itemAt(0).widget().deleteLater()
        self.noiseReductionMGridWidget = MGridWidget()
        layout.addWidget(self.noiseReductionMGridWidget)

    def load_xml(self):
        # 读取 XML 文件内容
        self.class_data = self.load_class_data(self.xml_file_path)
        self.populate_buttons()

        print(self.class_data)  # 打印读取的数据

    def load_class_data(self, file_path):
        """
        读取 class.xml 文件并返回分类数据
        :param file_path: XML 文件路径
        :return: 包含分类信息的字典列表
        """
        tree = ET.parse(file_path)
        root = tree.getroot()

        classes = []
        for class_elem in root.findall('class'):
            class_info = {
                'name': class_elem.find('name').text,
                'btnName': class_elem.find('btnName').text,
                'relativePath': class_elem.find('relativePath').text
            }
            classes.append(class_info)

        return classes

    def populate_buttons(self):
        """
        清空 classBtnWidget，并根据 XML 数据添加新的按钮
        """
        # 清空现有的按钮和间隔器
        for i in reversed(range(self.class_layout.count())):
            item = self.class_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()  # 删除按钮
                else:
                    # 如果是间隔器，直接移除
                    self.class_layout.removeItem(item)
        # 添加新按钮
        for class_info in self.class_data:
            btn = QPushButton(class_info['btnName'])
            btn.clicked.connect(
                lambda checked, name=class_info['name'], btnName=class_info['btnName'], path=class_info['relativePath']:
                self.on_class_button_click(name, btnName, path))
            self.class_layout.addWidget(btn)
        # 添加一个垂直间隔器到布局底部
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.class_layout.addItem(spacer)

    def on_class_button_click(self, name, btnName, path):
        """
        处理按钮点击事件
        :param name: 分类名称
        :param btnName: 按钮名称
        :param path: 相对路径
        """
        print(f"分类名称: {name}, 相对路径: {path}")
        self.classLabel.setText(f"正在加载文件路径: {path}")  # 更新标签文本以指示正在加载

        # 更新文件路径
        self.classMGridWidget.update_file_path(path)
        self.currentClassName = name
        self.currentBtnName = btnName
        self.currentUploadPath = path

        # 统计图片和视频数量
        if os.path.exists(path):
            files = os.listdir(path)
            image_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png'))]
            video_files = [f for f in files if f.endswith(('.avi', '.mp4'))]

            image_count = len(image_files)
            video_count = len(video_files)

            if image_count == 0 and video_count == 0:
                self.classLabel.setText("该路径下没有找到图片或视频。")
            else:
                self.classLabel.setText(f"{btnName} 共 {image_count} 张图片，共 {video_count} 个视频")
        else:
            self.classLabel.setText("路径不存在或无效！")

    def setupEvent(self):
        # 一级菜单
        # 海上船舶小目标识别背景与意义
        self.backgroundAnalysisBtn.clicked.connect(lambda: self.displayMenu(self.backgroundMenuPage))
        self.backgroundAnalysisBtn.clicked.connect(lambda: self.displayView(self.defaultViewPage))
        # 船舶小目标存取
        self.targetAccessBtn.clicked.connect(lambda: self.displayMenu(self.targetAccessMenuPage))
        self.targetAccessBtn.clicked.connect(lambda: self.displayView(self.targetAccessViewPage))
        # 船舶小目标检测
        self.targetDectionBtn.clicked.connect(lambda: self.displayMenu(self.targetDetectionMenuPage))
        self.targetDectionBtn.clicked.connect(lambda: self.displayView(self.targetDetectionViewPage))
        # 小目标去噪
        self.noiseReductionBtn.clicked.connect(lambda: self.displayMenu(self.noiseReductionMenuPage))
        self.noiseReductionBtn.clicked.connect(lambda: self.displayView(self.noiseReductionViewPage))
        # 主要信息查看
        self.mainInfoBtn.clicked.connect(lambda: self.displayMenu(self.defaultMenuPage))
        self.mainInfoBtn.clicked.connect(lambda: self.displayView(self.mainInfoViewPage))
        self.mainInfoBtn.clicked.connect(self.updateMainInfoLabel)

        # 海上船舶小目标识别背景与意义对应的二级菜单
        # 背景与意义
        self.backgroundBtn.clicked.connect(lambda: self.displayView(self.backgroundViewPage))
        # 小目标检测介绍
        self.targetDetectionIntroBtn.clicked.connect(lambda: self.displayView(self.targetDetectionIntroViewPage))
        # 小目标生成介绍
        self.targetGenIntroBtn.clicked.connect(lambda: self.displayView(self.targetGenIntroViewPage))
        # 小目标去噪介绍
        self.noiseReductionIntroBtn.clicked.connect(lambda: self.displayView(self.noiseReductionIntroViewPage))

        # 船舶小目标存取对应的二级菜单
        # 选择分类
        self.chooseClassBtn.clicked.connect(self.chooseClass)
        # 新建分类
        self.addClassBtn.clicked.connect(self.addClass)

        # 船舶小目标检测对应的二级菜单
        # Yolov10
        self.Yolov10ModelBtn.clicked.connect(self.Yolov10Model)
        # Yolov11
        self.Yolov11ModelBtn.clicked.connect(self.Yolov11Model)
        # DETR
        self.DETRModelBtn.clicked.connect(self.DETRModel)
        # RCNN
        self.RCNNModelBtn.clicked.connect(self.RCNNModel)

        # 小目标去噪对应的二级菜单
        # M1
        self.M1ModelBtn.clicked.connect(self.M1Model)
        # M2
        self.M2ModelBtn.clicked.connect(self.M2Model)
        # M3
        self.M3ModelBtn.clicked.connect(self.M3Model)

        # 上传
        self.uploadBtn.clicked.connect(self.uploadPicture)

        # 小目标检测选择测试集
        self.detectChooseTestSetBtn.clicked.connect(self.detectChooseTestSet)
        # 小目标检测开始检测
        self.detectStartBtn.clicked.connect(self.detectStart)
        # 小目标去噪选择测试集
        self.noiseReductionChooseTestSetBtn.clicked.connect(self.noiseReductionChooseTestSet)
        # 小目标去噪开始检测
        self.noiseReductionStartBtn.clicked.connect(self.noiseReductionStart)

    def updateMainInfoLabel(self):
        # 读取 XML 文件
        class_data = self.class_data  # 假设 class_data 已经通过 load_xml 填充
        class_file_count = []

        # 获取分类数量
        class_count = len(class_data)
        display_text = f"本系统存储图像共 {class_count} 个分类，其中：\n"

        # 遍历每个类，计算文件数量
        for class_info in class_data:
            relative_path = class_info['relativePath']

            # 初始化计数器
            image_count = 0
            video_count = 0

            # 计算文件数量
            if os.path.exists(relative_path):
                files = os.listdir(relative_path)

                # 统计图片和视频文件
                image_count = len([f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                video_count = len([f for f in files if f.lower().endswith(('.avi', '.mp4'))])
            else:
                display_text += f"{class_info['btnName']} 路径不存在\n"
                continue  # 跳过到下一个类

            # 添加到显示文本
            display_text += f"{class_info['btnName']} 下 {image_count} 张图像； {video_count} 个视频\n"

        display_text += "目标检测模型4个；图像去噪模型3个；\n"
        # 更新主信息标签
        self.mainInfoLabel.setText(display_text.strip())

    def detectChooseTestSet(self):
        print('小目标检测选择测试集')
        dialog = FileSelectorDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_files = dialog.get_selected_files()
            if selected_files:
                self.detectTestSet = selected_files
                print(self.detectTestSet)

                # 清空 tmp_path 下的所有文件
                tmp_path = 'run/detect/tmp'
                self.clear_tmp_path(tmp_path)

                # 将选中的文件复制到 tmp_path
                self.copy_selected_files(selected_files, tmp_path)

                # 更新文件路径
                self.detectMGridWidget.update_file_path(tmp_path)
                QMessageBox.information(self, "选择成功", "已选择测试集文件！")
            else:
                QMessageBox.warning(self, "选择警告", "没有选择任何文件。")

    def clear_tmp_path(self, tmp_path):
        # 检查目录是否存在
        if os.path.exists(tmp_path):
            # 删除目录下所有文件
            for filename in os.listdir(tmp_path):
                file_path = os.path.join(tmp_path, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"无法删除 {file_path}: {e}")
        else:
            os.makedirs(tmp_path)  # 如果目录不存在，则创建

    def copy_selected_files(self, selected_files, tmp_path):
        for file in selected_files:
            try:
                shutil.copy(file, tmp_path)
            except Exception as e:
                print(f"无法复制 {file} 到 {tmp_path}: {e}")

    def detectStart(self):
        # 检查模型是否选择
        if self.detectModelFun is None:
            # 创建消息框
            QMessageBox.warning(self, "选择模型", "请先选择一个检测模型。")
            return

        print('小目标检测开始检测')
        tmp_path = 'run/detect/tmp'

        # 确定输出目录
        exp_dir = 'run/detect/exp1'
        counter = 1
        while os.path.exists(exp_dir):
            counter += 1
            exp_dir = f'run/detect/exp{counter}'  # 找到下一个可用的目录

        os.makedirs(exp_dir)  # 创建输出目录

        # 获取文件列表
        files = [f for f in os.listdir(tmp_path) if os.path.isfile(os.path.join(tmp_path, f))]
        total_files = len(files)

        # 创建进度对话框
        progress_dialog = QProgressDialog("正在处理文件...", "取消", 0, total_files)
        progress_dialog.setWindowTitle("处理进度")
        progress_dialog.setModal(True)
        progress_dialog.show()

        for i, filename in enumerate(files):
            file_path = os.path.join(tmp_path, filename)

            # 打印正在处理的文件
            print(f'正在处理文件: {filename}')

            # 判断文件类型
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                # 读取图片
                src_img = cv2.imread(file_path)

                # 使用小目标检测模型进行检测
                res_img = self.detectModelFun(src_img)

                # 保存处理后的图片
                output_path = os.path.join(exp_dir, filename)
                cv2.imwrite(output_path, res_img)  # 保存结果图像

            elif filename.lower().endswith(('.avi', '.mp4')):
                # 读取视频
                cap = cv2.VideoCapture(file_path)

                if not cap.isOpened():
                    print(f"无法打开视频文件: {filename}")
                    continue

                # 获取视频信息
                fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                # 创建 VideoWriter 对象以保存处理后的视频
                output_video_path = os.path.join(exp_dir, filename)
                fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 可根据需要修改编码格式
                out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    # 使用小目标检测模型进行检测
                    res_frame = self.detectModelFun(frame)

                    # 写入处理后的帧
                    out.write(res_frame)

                cap.release()
                out.release()

            # 更新进度条
            progress_dialog.setValue(i + 1)
            progress_dialog.setLabelText(f'正在处理文件: {filename}')

            # 检查用户是否取消
            if progress_dialog.wasCanceled():
                print("检测已被取消")
                break

        progress_dialog.close()
        self.detectMGridWidget.update_file_path(exp_dir)
        print(f'检测完成，结果保存在: {exp_dir}')

    def noiseReductionChooseTestSet(self):
        print('小目标去噪选择测试集')
        dialog = FileSelectorDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_files = dialog.get_selected_files()
            if selected_files:
                self.noiseReductionTestSet = selected_files
                print(self.noiseReductionTestSet)

                # 清空 tmp_path 下的所有文件
                tmp_path = 'run/noiseReduction/tmp'
                self.clear_tmp_path(tmp_path)

                # 将选中的文件复制到 tmp_path
                self.copy_selected_files(selected_files, tmp_path)

                # 更新文件路径
                self.noiseReductionMGridWidget.update_file_path(tmp_path)
                QMessageBox.information(self, "选择成功", "已选择测试集文件！")
            else:
                QMessageBox.warning(self, "选择警告", "没有选择任何文件。")
        pass

    def noiseReductionStart(self):
        # 检查模型是否选择
        if self.noiseReductionModelFun is None:
            # 创建消息框
            QMessageBox.warning(self, "选择模型", "请先选择一个去噪模型。")
            return

        print('小目标去噪开始检测')

        tmp_path = 'run/noiseReduction/tmp'

        # 确定输出目录
        exp_dir = 'run/noiseReduction/exp1'
        counter = 1
        while os.path.exists(exp_dir):
            counter += 1
            exp_dir = f'run/noiseReduction/exp{counter}'  # 找到下一个可用的目录

        os.makedirs(exp_dir)  # 创建输出目录

        # 获取文件列表
        files = [f for f in os.listdir(tmp_path) if os.path.isfile(os.path.join(tmp_path, f))]
        total_files = len(files)

        # 创建进度对话框
        progress_dialog = QProgressDialog("正在处理文件...", "取消", 0, total_files)
        progress_dialog.setWindowTitle("处理进度")
        progress_dialog.setModal(True)
        progress_dialog.show()

        for i, filename in enumerate(files):
            file_path = os.path.join(tmp_path, filename)
            print(f'正在处理文件: {filename}')

            # 判断文件类型
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                # 读取图片
                src_img = cv2.imread(file_path)

                # 使用小目标去噪模型进行检测
                res_img = self.noiseReductionModelFun(src_img)

                # 保存处理后的图片
                output_path = os.path.join(exp_dir, filename)
                cv2.imwrite(output_path, res_img)  # 保存结果图像

            elif filename.lower().endswith(('.avi', '.mp4')):
                # 读取视频
                cap = cv2.VideoCapture(file_path)

                if not cap.isOpened():
                    print(f"无法打开视频文件: {filename}")
                    continue

                # 获取视频信息
                fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                # 创建 VideoWriter 对象以保存处理后的视频
                output_video_path = os.path.join(exp_dir, filename)
                fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 可根据需要修改编码格式
                out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    # 使用小目标去噪模型进行检测
                    res_frame = self.noiseReductionModelFun(frame)

                    # 写入处理后的帧
                    out.write(res_frame)

                cap.release()
                out.release()

            # 更新进度条
            progress_dialog.setValue(i + 1)
            progress_dialog.setLabelText(f'正在处理文件: {filename}')

            # 检查用户是否取消
            if progress_dialog.wasCanceled():
                print("检测已被取消")
                break

        progress_dialog.close()
        self.noiseReductionMGridWidget.update_file_path(exp_dir)
        print(f'检测完成，结果保存在: {exp_dir}')

    @pyqtSlot()
    def chooseClass(self):
        """打开窗口以管理分类"""
        self.class_manager_window = ClassManager(self.xml_file_path)
        self.class_manager_window.data_changed.connect(self.load_xml)  # 连接信号
        self.class_manager_window.show()

    @pyqtSlot(QWidget)
    def displayView(self, page):
        self.viewStackedWidget.setCurrentWidget(page)

    @pyqtSlot(QWidget)
    def displayMenu(self, page):
        self.menuStackedWidget.setCurrentWidget(page)

    def addClass(self):
        """
        新建分类
        :return: None
        """
        # 获取用户输入的分类中文名
        chinese_name, ok1 = QInputDialog.getText(self, "输入分类中文名", "请输入分类中文名:")

        # 如果用户点击了确认
        if ok1 and chinese_name:
            # 获取用户输入的分类文件夹名称（英文）
            folder_name, ok2 = QInputDialog.getText(self, "输入分类文件夹名称", "请输入分类文件夹名称（英文）:")

            # 如果用户点击了确认
            if ok2 and folder_name:
                # 创建文件夹路径
                folder_path = os.path.join("dataset", "test", folder_name)

                # 创建新文件夹
                os.makedirs(folder_path, exist_ok=True)

                # 更新 XML 配置文件
                self.update_xml_config(folder_name, chinese_name, folder_path)

                self.currentClassName = folder_name
                self.currentBtnName = chinese_name
                self.currentUploadPath = folder_path
                self.on_class_button_click(self.currentClassName, self.currentBtnName, self.currentUploadPath)

                print(f"分类中文名: {chinese_name}, 分类文件夹名称: {folder_name}")
                QMessageBox.information(self, "成功", "分类创建成功！")
                self.load_xml()
            else:
                QMessageBox.warning(self, "警告", "未输入分类文件夹名称！")
        else:
            QMessageBox.warning(self, "警告", "未输入分类中文名！")

    def update_xml_config(self, folder_name, chinese_name, folder_path):
        """
        更新 XML 配置文件
        :param folder_name: 分类文件夹名称（英文）
        :param chinese_name: 分类中文名
        :param folder_path: 分类文件夹路径
        """
        tree = ET.parse(self.xml_file_path)
        root = tree.getroot()

        # 创建新的 class 元素
        new_class = ET.Element("class")
        name_elem = ET.SubElement(new_class, "name")
        name_elem.text = folder_name
        btn_name_elem = ET.SubElement(new_class, "btnName")
        btn_name_elem.text = chinese_name
        relative_path_elem = ET.SubElement(new_class, "relativePath")
        relative_path_elem.text = folder_path

        # 将新的 class 元素添加到根节点
        root.append(new_class)

        # 保存更新后的 XML 文件
        tree.write(self.xml_file_path, encoding='utf-8', xml_declaration=True)

    def uploadPicture(self):
        try:
            # 使用 QFileDialog 获取多个文件路径
            file_names, _ = QFileDialog.getOpenFileNames(
                self,
                "选择图片和视频",
                "",
                "Images (*.png *.jpg *.jpeg);;Videos (*.avi *.mp4);;All Files (*)"
            )

            if file_names:
                progress_dialog = QProgressDialog("上传文件中，请稍候...", "取消", 0, len(file_names), self)
                progress_dialog.setWindowTitle("上传进度")
                progress_dialog.setModal(True)  # 设置为模态
                progress_dialog.setValue(0)
                progress_dialog.show()

                for i, file_path in enumerate(file_names):
                    self.copy_file(file_path)
                    progress_dialog.setValue(i + 1)  # 更新进度条

                    if progress_dialog.wasCanceled():
                        break  # 如果用户点击了取消，则退出循环

                progress_dialog.close()  # 上传完成后关闭进度对话框

                QMessageBox.information(self, "成功", "文件已成功上传！")
                self.on_class_button_click(self.currentClassName, self.currentBtnName, self.currentUploadPath)
            else:
                QMessageBox.warning(self, "警告", "没有选择任何文件。")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发生错误: {e}")

    def copy_file(self, file_path):
        try:
            if os.path.isfile(file_path):
                shutil.copy2(file_path, self.currentUploadPath)  # 复制文件到目标文件夹
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法复制文件: {e}")

    def Yolov10Model(self):
        print("Yolov10Model")
        # 创建消息框
        QMessageBox.information(self, "选择模型", "选择了Yolov10模型。")
        self.detectModelFun = Yolov10Predict
        pass

    def Yolov11Model(self):
        print("Yolov11Model")
        # 创建消息框
        QMessageBox.information(self, "选择模型", "选择了Yolov11模型。")
        self.detectModelFun = Yolov11Predict
        pass

    def DETRModel(self):
        print("DETRModel")
        # 创建消息框
        QMessageBox.information(self, "选择模型", "选择了DETR模型。")
        self.detectModelFun = DETRPredict
        pass

    def RCNNModel(self):
        print("RCNNModel")
        QMessageBox.information(self, "选择模型", "选择了RCNN模型。")
        self.detectModelFun = RCNNPredict
        pass

    def M1Model(self):
        print("M1Model")
        QMessageBox.information(self, "选择模型", "选择了M1模型。")
        self.noiseReductionModelFun = M1Predict
        pass

    def M2Model(self):
        print("M2Model")
        QMessageBox.information(self, "选择模型", "选择了M2模型。")

        self.noiseReductionModelFun = M2Predict
        pass

    def M3Model(self):
        print("M3Model")
        QMessageBox.information(self, "选择模型", "选择了M3模型。")

        self.noiseReductionModelFun = M3Predict
        pass

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()  # 获取屏幕大小
        window_rect = self.frameGeometry()  # 获取窗口大小
        center_point = screen.center()  # 获取屏幕中心点
        window_rect.moveCenter(center_point)  # 将窗口中心移动到屏幕中心
        self.move(window_rect.topLeft())  # 设置窗口位置


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MWindow()
    window.show()
    sys.exit(app.exec())
