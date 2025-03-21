import sys
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTreeView, QPushButton, QMessageBox, QApplication
from PyQt6.QtCore import QDir, Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from miy.album.album import ImageDialog


class FileSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择测试集文件")

        self.layout = QVBoxLayout(self)

        # 创建树视图
        self.tree_view = QTreeView(self)
        self.layout.addWidget(self.tree_view)
        self.tree_view.setHeaderHidden(True)
        # 创建模型
        self.model = QStandardItemModel()
        self.tree_view.setModel(self.model)

        # 添加根目录
        self.populate_tree_view(QDir("dataset"))

        # 连接双击信号
        self.tree_view.doubleClicked.connect(self.on_item_double_clicked)

        # 连接复选框状态变化信号
        self.model.itemChanged.connect(self.on_item_changed)
        self.model.itemChanged.connect(self.update_check_state)

        # 按钮
        self.ok_button = QPushButton("确认选择", self)
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)

        self.selected_files = []

    def populate_tree_view(self, path):
        root_item = self.model.invisibleRootItem()
        root_item.setCheckable(True)
        self.add_items(root_item, path)

    def add_items(self, parent_item, path):
        # 创建文件夹项并设置复选框
        dir_item = QStandardItem(QDir(path).dirName())
        dir_item.setData(path)  # 设置文件夹的路径数据
        dir_item.setCheckable(True)  # 使文件夹项可复选
        dir_item.setCheckState(Qt.CheckState.Unchecked)  # 默认不选中
        parent_item.appendRow(dir_item)

        # 遍历目录
        filters = QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot
        for file_info in QDir(path).entryInfoList(filters):
            if file_info.isDir():
                self.add_items(dir_item, file_info.filePath())
            elif file_info.suffix() in ['png', 'jpg', 'jpeg', 'avi', 'mp4']:
                file_item = QStandardItem(file_info.fileName())
                file_item.setData(file_info.filePath())  # 存储文件路径
                file_item.setCheckable(True)  # 使文件项可复选
                file_item.setCheckState(Qt.CheckState.Unchecked)  # 默认不选中
                dir_item.appendRow(file_item)

        dir_item.setEditable(False)  # 不允许手动编辑，防止直接修改

    def on_item_changed(self, item):
        if item.checkState() == Qt.CheckState.Checked:
            # print(f"Checked: {item.text()}")
            pass
        else:
            # print(f"Unchecked: {item.text()}")
            pass

    def update_check_state(self, item):
        # 如果文件夹被勾选，递归勾选所有子项
        if item.checkState() == Qt.CheckState.Checked:
            for row in range(item.rowCount()):
                child_item = item.child(row)
                child_item.setCheckState(Qt.CheckState.Checked)
                if child_item.hasChildren():
                    self.update_check_state(child_item)
        else:
            # 如果文件夹未被勾选，递归取消勾选所有子项
            for row in range(item.rowCount()):
                child_item = item.child(row)
                child_item.setCheckState(Qt.CheckState.Unchecked)
                if child_item.hasChildren():
                    self.update_check_state(child_item)

    def on_item_double_clicked(self, index):
        if index.isValid():
            item = self.model.itemFromIndex(index)
            if not item.hasChildren():  # 只有在选中的是文件时才弹出预览
                image_path = item.data()
                if image_path:
                    # QMessageBox.information(self, "Image Path", image_path)  # 显示文件路径
                    dialog = ImageDialog(image_path)
                    dialog.exec()  # 显示图像对话框

    def get_selected_files(self):
        self.selected_files.clear()
        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            self.collect_checked_files(item)

        return self.selected_files

    def collect_checked_files(self, item):
        # TODO: 现在只能选择文件项或者最底层的目录，把这个hasChildren改成rowCount()会出现很奇怪的对象报错
        """
无法复制 <PyQt6.QtCore.QDir object at 0x000001DAA4F86F50> 到 run/noiseReduction/tmp: expected str, bytes or os.PathLike object, not QDir

        :param item:
        :return:
        """

        if item.hasChildren():
            if item.checkState() == Qt.CheckState.Checked:
                filters = QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot
                for file_info in QDir(item.data()).entryInfoList(filters):
                    if file_info.isFile() and file_info.suffix() in ['png', 'jpg', 'jpeg', 'avi', 'mp4']:
                        self.selected_files.append(file_info.filePath())
                return
            for row in range(item.rowCount()):
                child_item = item.child(row)
                self.collect_checked_files(child_item)
        else:
            if item.checkState() == Qt.CheckState.Checked:
                file_path = item.data()
                if file_path:  # 检查文件路径是否存在
                    self.selected_files.append(file_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = FileSelectorDialog()
    dialog.exec()
