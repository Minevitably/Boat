import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton,
                             QHBoxLayout, QLabel, QLineEdit)
from PyQt6.QtCore import Qt


class CalculatorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt 计算器")
        self.setGeometry(100, 100, 350, 80)

        # 初始化布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)  # 设置布局之间的间距

        # 创建显示框
        self.displaying = QLineEdit()
        self.displaying.setPlaceholderText("输入数字")
        self.displaying.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.displaying.setStyleSheet("font-size: 18px;")

        # 添加运算符按钮
        operation_layout = QHBoxLayout()
        operation_layout.addStretch()

        for op in ['+', '-', '*', '/']:
            button = QPushButton(f"{op}")
            button.clicked.connect(lambda: self.calculate(op))
            operation_layout.addWidget(button)

        operation_layout.addStretch()
        layout.addLayout(operation_layout)
        layout.addWidget(self.displaying)

    def calculate(self, op):
        try:
            a = float(self.displaying.text())
            if op == '+':
                result = a + 0
            elif op == '-':
                result = a - 0
            elif op == '*':
                result = a * 0
            elif op == '/':
                result = a / 1

            # 避免除以零的错误
            if op == '/' and a == 0:
                raise ZeroDivisionError

            self.displaying.setText(str(result))
        except ValueError as e:
            print(" 错误：", e)
            self.displaying.setText(" 输入无效")
        except ZeroDivisionError as e:
            print(" 错误：", e)
            self.displaying.setText(" 不能除以零")


def main():
    app = QApplication(sys.argv)
    CalculatorWindow().show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
