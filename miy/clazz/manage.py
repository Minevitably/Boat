import os
import shutil

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QMessageBox, QPushButton, \
    QVBoxLayout, QListWidget, QHBoxLayout
import xml.etree.ElementTree as ET


# from main import MWindow


class ClassManager(QWidget):
    data_changed = pyqtSignal()

    def __init__(self, xml_file_path: str):
        super().__init__()
        self.setWindowTitle("管理分类")
        self.setGeometry(100, 100, 400, 300)

        self.xml_file_path = xml_file_path
        # 布局
        self.layout = QVBoxLayout(self)

        # 分类列表
        self.class_list = QListWidget()
        self.layout.addWidget(self.class_list)

        # 加载分类
        self.load_classes()

        # 按钮布局
        button_layout = QHBoxLayout()
        self.delete_button = QPushButton("删除分类")
        self.delete_button.clicked.connect(self.delete_class)
        button_layout.addWidget(self.delete_button)

        self.layout.addLayout(button_layout)

    def load_classes(self):
        """从 XML 文件加载分类并显示在列表中"""
        tree = ET.parse(self.xml_file_path)
        root = tree.getroot()

        for class_elem in root.findall('class'):
            name = class_elem.find('name').text
            btn_name = class_elem.find('btnName').text
            self.class_list.addItem(f"{btn_name} ({name})")

    def delete_class(self):
        """删除选中的分类"""
        selected_item = self.class_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "警告", "请选择一个分类进行删除！")
            return

        # 解析选中的项
        name = selected_item.text().split(' ')[-1][1:-1]  # 获取分类英文名
        btn_name = selected_item.text().split(' ')[0]  # 获取分类中文名

        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除分类 '{btn_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        # 删除对应的 XML 行和文件夹
        self.remove_class_from_xml(name)
        self.delete_folder(name)

        # 从列表中移除项
        self.class_list.takeItem(self.class_list.row(selected_item))

        self.data_changed.emit()

    def remove_class_from_xml(self, class_name):
        """从 XML 文件中删除指定分类"""
        tree = ET.parse(self.xml_file_path)
        root = tree.getroot()

        # 查找并删除指定分类
        for class_elem in root.findall('class'):
            if class_elem.find('name').text == class_name:
                root.remove(class_elem)
                break

        # 保存更新后的 XML 文件
        tree.write(self.xml_file_path, encoding='utf-8', xml_declaration=True)

    def delete_folder(self, class_name):
        """删除对应的文件夹"""
        folder_path = os.path.join("dataset", "test", class_name)

        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)  # 删除文件夹及其所有内容
                print(f"文件夹 '{folder_path}' 已成功删除。")
            except Exception as e:
                print(f"删除文件夹时发生错误: {e}")
        else:
            print(f"文件夹 '{folder_path}' 不存在。")
