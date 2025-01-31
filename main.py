import sys
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QWidget, QInputDialog, QMessageBox, QPushButton, QSpacerItem, QSizePolicy
from Form import Ui_Form
import xml.etree.ElementTree as ET

class MWindow(QWidget, Ui_Form):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setupEvent()
        # 默认显示空的二级菜单页面
        self.displayMenu(self.defaultMenuPage)
        # 默认显示系统简介视图页面
        self.displayView(self.defaultViewPage)

        # 读取 XML 文件内容
        self.class_data = self.load_class_data("class.xml")
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
                lambda checked, name=class_info['name'], path=class_info['relativePath']: self.on_button_click(name,
                                                                                                               path))
            self.class_layout.addWidget(btn)
        # 添加一个垂直间隔器到布局底部
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.class_layout.addItem(spacer)

    def on_button_click(self, name, path):
        """
        处理按钮点击事件
        :param name: 分类名称
        :param path: 相对路径
        """
        print(f"分类名称: {name}, 相对路径: {path}")

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
        self.chooseClassBtn.clicked.connect(lambda: self.displayView(self.targetAccessViewPage))
        # 新建分类
        self.addClassBtn.clicked.connect(self.addClass)

        # 船舶小目标检测对应的二级菜单
        # Yolo
        self.YoloModelBtn.clicked.connect(self.YoloModel)
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
        if ok1:
            # 获取用户输入的分类文件夹名称（英文）
            folder_name, ok2 = QInputDialog.getText(self, "输入分类文件夹名称", "请输入分类文件夹名称（英文）:")

            # 如果用户点击了确认
            if ok2:
                # 打印用户输入的内容
                print(f"分类中文名: {chinese_name}, 分类文件夹名称: {folder_name}")
            else:
                QMessageBox.warning(self, "警告", "未输入分类文件夹名称！")
        else:
            QMessageBox.warning(self, "警告", "未输入分类中文名！")

        pass

    def YoloModel(self):
        print("YoloModel")
        pass

    def DETRModel(self):
        print("DETRModel")

        pass

    def RCNNModel(self):
        print("RCNNModel")

        pass

    def M1Model(self):
        print("M1Model")

        pass

    def M2Model(self):
        print("M2Model")

        pass

    def M3Model(self):
        print("M3Model")

        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MWindow()
    window.show()
    sys.exit(app.exec())
