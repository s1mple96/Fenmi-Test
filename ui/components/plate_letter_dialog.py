# -*- coding: utf-8 -*-
"""
车牌字母选择对话框（A~Z，点击即选中，无确定/取消按钮）
"""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

LETTERS = [chr(i) for i in range(ord('A'), ord('Z')+1)]

class PlateLetterDialog(QDialog):
    def __init__(self, parent=None, selected_letter=None):
        super().__init__(parent)
        self.setWindowTitle("选择车牌字母")
        self.setFixedSize(420, 260)
        self.selected_letter = selected_letter if selected_letter in LETTERS else None
        self.letter_buttons = {}
        self.init_ui()
        if self.selected_letter:
            self.highlight_selected(self.selected_letter)

    def init_ui(self):
        layout = QVBoxLayout()
        title_label = QLabel("请选择车牌字母")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        layout.addWidget(title_label)

        grid_widget = QGridLayout()
        max_cols = 7
        row, col = 0, 0
        for letter in LETTERS:
            btn = QPushButton(letter)
            btn.setFixedSize(40, 40)
            btn.clicked.connect(lambda checked, l=letter: self.select_and_accept(l))
            self.letter_buttons[letter] = btn
            grid_widget.addWidget(btn, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        layout.addLayout(grid_widget)
        self.setLayout(layout)

    def select_and_accept(self, letter):
        self.selected_letter = letter
        self.highlight_selected(letter)
        self.accept()

    def highlight_selected(self, letter):
        for k, btn in self.letter_buttons.items():
            if k == letter:
                btn.setStyleSheet("background-color: #409EFF; color: white; font-weight: bold; border:2px solid #0057b7;")
            else:
                btn.setStyleSheet("")

    def get_selected_letter(self):
        return self.selected_letter

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = PlateLetterDialog(selected_letter="A")
    if dialog.exec_() == QDialog.Accepted:
        print("选中的字母:", dialog.get_selected_letter())
    sys.exit() 