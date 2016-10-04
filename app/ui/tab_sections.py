""" This module is responsible for displaying logging curves in tab 'sections' """
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QWidget, QScrollArea

from app.domain import main_context
from app.ui.section import Section


class Sections(QWidget):
    """ contains Section objects for all checked curves"""
    def __init__(self):
        super().__init__()

        # Container Widget
        self.cont_widget = QWidget()
        self.cont_layout = QtWidgets.QHBoxLayout(self)

        self.cont_widget.setLayout(self.cont_layout)

        # Scroll Area Properties
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.cont_widget)

        # self layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(scroll)

        self.setLayout(layout)

        self.reset()

    def clear_cont_layout(self):
        for i in range(self.cont_layout.count()):
            section = self.cont_layout.itemAt(i).widget()
            section.close()

    def reset(self):
        self.clear_cont_layout()
        print(main_context.root_dir)

        for well in main_context.root_dir.get_checked_wells():
            if well.qt_item.checkState(0):
                section = Section(well)
                self.cont_layout.addWidget(section)
