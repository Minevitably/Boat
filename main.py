import sys
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QWidget
from Form import Ui_Form


class MWindow(QWidget, Ui_Form):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setupEvent()

    def setupEvent(self):
        # self.self.displayMenuStackWidget(0)用于在程序启动后显示，默认显示空的二级菜单

        # 一级菜单
        # 海上船舶小目标识别背景与意义
        self.backgroundAnalysisBtn.clicked.connect(lambda: self.displayMenuStackWidget(1))
        # 船舶小目标存取
        self.targetAccessBtn.clicked.connect(lambda: self.displayMenuStackWidget(2))
        # 船舶小目标检测
        self.targetDectionBtn.clicked.connect(lambda: self.displayMenuStackWidget(3))
        self.targetDectionBtn.clicked.connect(lambda: self.displayViewStackWidget(6))
        # 小目标去噪
        self.noiseReductionBtn.clicked.connect(lambda: self.displayMenuStackWidget(4))
        # 主要信息查看
        self.mainInfoBtn.clicked.connect(lambda: self.displayMenuStackWidget(0))
        self.mainInfoBtn.clicked.connect(lambda: self.displayViewStackWidget(7))

        # self.displayViewStackWidget(0)用于在程序启动后显示，默认显示船舶小目标识别简介，

        # 二级菜单第一页的按钮
        # 背景与意义
        self.backgroundBtn.clicked.connect(lambda: self.displayViewStackWidget(1))
        # 小目标检测介绍
        self.targetDetectionIntroBtn.clicked.connect(lambda: self.displayViewStackWidget(2))
        # 小目标生成介绍
        self.targetGenIntroBtn.clicked.connect(lambda: self.displayViewStackWidget(3))
        # 小目标去噪介绍
        self.noiseReductionIntroBtn.clicked.connect(lambda: self.displayViewStackWidget(4))

        # 二级菜单第二页的按钮
        # 选择分类
        self.chooseClassBtn.clicked.connect(lambda: self.displayViewStackWidget(5))
        # 新建分类
        self.addClassBtn.clicked.connect(self.addClass)

        # 二级菜单第三页的按钮
        # Yolo
        self.YoloModelBtn.clicked.connect(self.YoloModel)
        # DETR
        self.DETRModelBtn.clicked.connect(self.DETRModel)
        # RCNN
        self.RCNNModelBtn.clicked.connect(self.RCNNModel)

        # 二级菜单第四页的按钮
        # M1
        self.M1ModelBtn.clicked.connect(self.M1Model)
        # M2
        self.M2ModelBtn.clicked.connect(self.M2Model)
        # M3
        self.M3ModelBtn.clicked.connect(self.M3Model)

    def displayMenuStackWidget(self, i):
        """
        二级菜单
        :param i: 索引
        :return: None
        """
        self.menuStackedWidget.setCurrentIndex(i)

    def displayViewStackWidget(self, page):
        """
        视图区域
        :param i: 索引
        :return: None
        """
        self.viewStackWidget.setCurrentIndex(page)

    def addClass(self):
        """
        新建分类
        :return: None
        """
        print("addClass")

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
