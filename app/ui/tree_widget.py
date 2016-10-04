from io import StringIO

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QTreeWidget, QAbstractItemView, QFileDialog, QTreeWidgetItem, QMessageBox

from app.domain import main_context
from app.domain.well import Well
from app.domain.wells_dir import WellsDir
from app.logic import imports
from app.util.config import Config
from app.util.logger import log


class TreeWidget(QTreeWidget):
    """ Implements functionality of treewiget placed in left part """

    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.setupUi()

    def setupUi(self):
        self.setObjectName("treeWidget")
        self.headerItem().setText(0, "Navigation")
        self.headerItem().setText(1, "Status")
        # self.setMinimumWidth(300)
        # self.setMaximumWidth(400)
        self.setFixedWidth(320)
        self.setSortingEnabled(False)

        def on_dropEvent(self):
            """ executes when some item in treewidget has been dropped"""
            dropEvent = self.dropEvent  # original drop event

            def wrapper(event):  # my drop event
                items = event.source().selectedItems()  # items which were dropped
                dropEvent(event)  # executing original drop event
                for item in items[::-1]:
                    if isinstance(item.source, Well):
                        item.source.parent_dir.remove_well(item.source)
                        item.source.parent_dir = item.parent().source
                        destination_item = event.source().itemAt(event.pos())
                        # print(destination_item.text(0))
                        if hasattr(destination_item, 'source') and isinstance(destination_item.source, Well):
                            index = event.source().indexFromItem(destination_item)
                            item.source.parent_dir.insert_well(item.source, index.row() - 2)
                            print(index.row() - 2)
                        else:
                            item.source.parent_dir.add_well(item.source)

                    elif isinstance(item.source, WellsDir):
                        item.source.parent_dir.remove_sub_dir(item.source)
                        item.source.parent_dir = item.parent().source
                        item.source.parent_dir.add_sub_dir(item.source)
                self.refresh()

            return wrapper  # returns my drop event

        self.dropEvent = on_dropEvent(self)  # redefine original drop event by mine

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.tree_widget_context_menu)

        self.itemChanged.connect(self.check_changed)

    # @QtCore.pyqtSlot()
    def tree_widget_context_menu(self, pos):
        """ response for context menu in tree widget
        :param pos: position on the window of item
        """
        qt_item = self.itemAt(pos)
        if qt_item is None:
            return

        qt_menu = QtWidgets.QMenu()

        if qt_item.UserType == 'wells_dir':
            actionImport = QtWidgets.QAction('Import', qt_menu)
            actionRename = QtWidgets.QAction('Rename', qt_menu)
            actionDelete = QtWidgets.QAction('Delete', qt_menu)
            actionCreateSubDir = QtWidgets.QAction('Create folder', qt_menu)

            qt_menu.addAction(actionImport)
            if qt_item.source is not main_context.root_dir:
                qt_menu.addAction(actionRename)
            if qt_item.source is not main_context.root_dir:
                qt_menu.addAction(actionDelete)
            qt_menu.addAction(actionCreateSubDir)

            actionImport.triggered.connect(lambda: self.on_actionImport_triggered(qt_item))
            actionRename.triggered.connect(lambda: self.on_actionRename_triggered(qt_item))
            actionDelete.triggered.connect(lambda: self.on_actionDelete_triggered(qt_item))
            actionCreateSubDir.triggered.connect(lambda: self.on_createSubDir_triggered(qt_item))

        if qt_item.UserType == 'well':
            actionSpreadsheet = QtWidgets.QAction('Spreadsheet', qt_menu)
            actionDelete = QtWidgets.QAction('Delete', qt_menu)

            qt_menu.addAction(actionSpreadsheet)
            qt_menu.addAction(actionDelete)

            actionSpreadsheet.triggered.connect(lambda: self.on_actionSpreadsheet_triggered(qt_item))
            actionDelete.triggered.connect(lambda: self.on_actionDelete_triggered(qt_item))

        if qt_item.UserType == 'tops_dir':
            actionSpreadsheet = QtWidgets.QAction('Spreadsheet', qt_menu)
            qt_menu.addAction(actionSpreadsheet)
            actionSpreadsheet.triggered.connect(lambda: self.on_actionSpreadsheet_triggered(qt_item))
            # lambda: QMessageBox(QMessageBox.NoIcon, 'Spreadsheet',
            #                                                     'well = "{0}"  surface_id = "{1}"  md = {2}'.format(
            #                                                         qt_item.source.well_name,
            #                                                         qt_item.source.surface_id,
            #                                                         qt_item.source.md), QMessageBox.Ok,
            #                                                     self).show())

        if qt_item.UserType == 'curves_dir':
            actionSpreadsheet = QtWidgets.QAction('Spreadsheet', qt_menu)
            qt_menu.addAction(actionSpreadsheet)
            actionSpreadsheet.triggered.connect(lambda: self.on_actionSpreadsheet_triggered(qt_item))

        qt_menu.exec_(self.mapToGlobal(pos))

    # @QtCore.pyqtSlot()
    def check_changed(self, item, column):
        """ executes when some item in tree widget changed their state
        :param column: column where item state was changed
        :param item: item which state was changed
        """
        self.blockSignals(True)

        # not mark signal
        if item.checkState(0) == item.previous_state:
            return

        item.previous_state = item.checkState(0)
        log.debug('type="{0}"  name="{1}  signal={2}"'.format(item.UserType, item.text(0), item.previous_state))

        if item.UserType == 'wells_dir':
            def mark_sub_items(item):
                children = [item.child(i) for i in range(item.childCount())]
                for child in children:
                    if child.UserType == 'well':
                        child.setCheckState(0, item.checkState(0))
                        child.previous_state = item.checkState(0)
                        continue

                    if child.UserType == 'wells_dir':
                        child.setCheckState(0, item.checkState(0))
                        child.previous_state = item.checkState(0)
                        mark_sub_items(child)

            mark_sub_items(item)

        elif item.UserType == 'curve_aliases_dir':
            state = item.checkState(0)
            item = item.parent()

            def mark_sub_items(item):
                children = [item.child(i) for i in range(item.childCount())]
                for child in children:
                    if child.UserType in ['curve_alias', 'curve']:
                        child.setCheckState(0, state)
                        child.previous_state = state
                        continue
                    if child.UserType in ['curve_aliases_dir', 'curves_dir']:
                        child.setCheckState(0, state)
                        child.previous_state = state
                        mark_sub_items(child)
                        continue
                    if child.UserType in ['wells_dir', 'well']:
                        mark_sub_items(child)

            mark_sub_items(item)

        elif item.UserType == 'top_aliases_dir':
            state = item.checkState(0)
            item = item.parent()

            def mark_sub_items(item):
                children = [item.child(i) for i in range(item.childCount())]
                for child in children:
                    if child.UserType in ['top_alias', 'top']:
                        child.setCheckState(0, state)
                        child.previous_state = state
                        continue
                    if child.UserType in ['top_aliases_dir', 'tops_dir']:
                        child.setCheckState(0, state)
                        child.previous_state = state
                        mark_sub_items(child)
                        continue
                    if child.UserType in ['wells_dir', 'well']:
                        mark_sub_items(child)

            mark_sub_items(item)

        elif item.UserType == 'curve_alias':
            state = item.checkState(0)
            name = item.text(0)
            item = item.parent().parent()

            def mark_sub_items(item):
                children = [item.child(i) for i in range(item.childCount())]
                for child in children:
                    if child.UserType in ['curve', 'curve_alias'] and child.text(0) == name:
                        child.setCheckState(0, state)
                        child.previous_state = state
                        continue
                    if child.UserType in ['wells_dir', 'well', 'curve_aliases_dir', 'curves_dir']:
                        mark_sub_items(child)

            mark_sub_items(item)

        elif item.UserType == 'top_alias':
            state = item.checkState(0)
            name = item.text(0)
            item = item.parent().parent()

            def mark_sub_items(item):
                children = [item.child(i) for i in range(item.childCount())]
                for child in children:
                    if child.UserType in ['top', 'top_alias'] and child.text(0) == name:
                        child.setCheckState(0, state)
                        child.previous_state = state
                        continue
                    if child.UserType in ['wells_dir', 'well', 'top_aliases_dir', 'tops_dir']:
                        mark_sub_items(child)

            mark_sub_items(item)

        elif item.UserType in ['curves_dir', 'tops_dir']:
            children = [item.child(i) for i in range(item.childCount())]
            for child in children:
                child.setCheckState(0, item.checkState(0))
                child.previous_state = item.checkState(0)

        self.window().tab_2d_map.refresh()
        self.window().tab_sections.reset()
        self.blockSignals(False)

    @QtCore.pyqtSlot()
    def on_actionImport_triggered(self, qt_invoker):
        """ executes from context menu
        :param qt_invoker: item where was context menu invoked
        """
        files_list, files_type = QFileDialog.getOpenFileNames(
            self,
            "Select one or more files to open",
            Config.default_dir_path,
            "dev files *.dev(*.dev);; las files *.las(*.las);; WellTops file *.txt(*.txt)")

        log.debug("files_type = {0} \tfiles_list = {1}".format(files_type, files_list))

        func = {
            "dev files *.dev(*.dev)": imports.import_dev,
            " las files *.las(*.las)": imports.import_las,
            " WellTops file *.txt(*.txt)": imports.import_well_tops
        }.get(files_type)

        if not func:
            return

        broken_files = str()
        if not isinstance(qt_invoker, QTreeWidgetItem):
            broken_files = func(files_list, main_context.root_dir)
        else:
            broken_files = func(files_list, qt_invoker.source)

        if broken_files and len(broken_files) > 0:
            QMessageBox.warning(self, "Warning", "Following files are broken:\n" + broken_files)

        self.reset_content()

    # @QtCore.pyqtSlot()
    def on_actionRename_triggered(self, qt_invoker):
        """ executes from context menu
        :param qt_invoker: item where was context menu invoked
        """
        new_name, ok = QtWidgets.QInputDialog.getText(self, 'Rename', 'Input new name:')
        if ok and len(new_name) > 0:
            qt_invoker.source.name = new_name
            self.reset_content()

    # @QtCore.pyqtSlot()
    def on_createSubDir_triggered(self, qt_invoker):
        """ executes from context menu
        :param qt_invoker: item where was context menu invoked
        """
        print('------------------------------------------')
        print(id(qt_invoker.source.sub_dirs_list))

        wd = WellsDir(qt_invoker.source, 'sub_folder_%i' % len(qt_invoker.source.sub_dirs_list))

        print(id(wd.sub_dirs_list))

        print(wd)
        qt_invoker.source.add_sub_dir(wd)
        self.reset_content()

    # @QtCore.pyqtSlot()
    def on_actionDelete_triggered(self, qt_invoker):
        """ executes from context menu
        :param qt_invoker: item where was context menu invoked
        """
        reply = QtWidgets.QMessageBox.question(self, 'Message',
                                               'Are you sure you want to delete "%s"?' % qt_invoker.source.name,
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QMessageBox.No:
            return

        if isinstance(qt_invoker.source, WellsDir):
            qt_invoker.parent().removeChild(qt_invoker)
            qt_invoker.source.parent_dir.remove_sub_dir(qt_invoker.source)
            for well in qt_invoker.source.wells_list:
                main_context.wells_list.remove(well)
                for top in well.tops_list:
                    main_context.tops_list.remove(top)
            qt_invoker.source.wells_list.clear()
            # print('wells in folder = {0}'.format([well.name for well in qt_invoker.source.wells_list]))
            del qt_invoker.source
            self.refresh()

        elif isinstance(qt_invoker.source, Well):
            well = qt_invoker.source
            well.parent_dir.remove_well(well)
            main_context.wells_list.remove(well)
            for top in well.tops_list:
                main_context.tops_list.remove(top)
            del well
            qt_invoker.parent().removeChild(qt_invoker)
            self.refresh()

    # @QtCore.pyqtSlot()
    def on_actionSpreadsheet_triggered(self, qt_invoker):
        """ executes from context menu
        :param qt_invoker: item where was context menu invoked
        """
        log.debug('action spreadsheet')

        if qt_invoker.UserType == 'well' and qt_invoker.text(1) != 'needs dev':
            text = \
                'well_name = {0}\n' \
                'head_x = {1}\n' \
                'head_y = {2}\n' \
                'offset = {3}\n' \
                '#======================================================================================================================================\n' \
                '      MD              X              Y             Z           TVD           DX           DY          AZIM          INCL          DLS\n' \
                '#======================================================================================================================================\n' \
                ''.format(qt_invoker.source.name, qt_invoker.source.head_x, qt_invoker.source.head_y,
                          qt_invoker.source.offset)
            for i in range(len(qt_invoker.source.md)):
                text += ' {0:0<12}   {1:0<12} {2:0<12} {3:0<12} {4:0<12} {5:0<12} {6:0<12} {7:0<12} {8:0<12} {9:0<12}\n'.format(
                    qt_invoker.source.md[i], qt_invoker.source.x[i], qt_invoker.source.y[i],
                    qt_invoker.source.z[i], qt_invoker.source.tvd[i], qt_invoker.source.dx[i],
                    qt_invoker.source.dy[i], qt_invoker.source.azim[i], qt_invoker.source.incl[i],
                    qt_invoker.source.dls[i])

            layout = QtWidgets.QVBoxLayout(self)
            qt_text_edit = QtWidgets.QTextEdit(self)
            qt_text_edit.setReadOnly(True)
            qt_text_edit.setCurrentFont(QtGui.QFont("Liberation Mono", 10))
            layout.addWidget(qt_text_edit)
            qt_text_edit.setText(text)

            qt_dialog = QtWidgets.QDialog(self)
            qt_dialog.setWindowTitle('Spreadsheet')
            qt_dialog.setLayout(layout)
            qt_dialog.setMinimumWidth(1100)
            qt_dialog.setMinimumHeight(600)
            qt_dialog.show()

        if qt_invoker.UserType == 'tops_dir':
            well = qt_invoker.parent().source

            if len(well.tops_list) < 1:
                return

            text = 'Well       Surface_id      MD\n'
            for top in well.tops_list:
                text += '{0:<10} {1:<15} {2:<f}\n'.format(top.well_name, top.surface_id, top.md)

            layout = QtWidgets.QVBoxLayout(self)
            qt_text_edit = QtWidgets.QTextEdit(self)
            qt_text_edit.setReadOnly(True)
            qt_text_edit.setCurrentFont(QtGui.QFont("Liberation Mono", 10))
            layout.addWidget(qt_text_edit)
            qt_text_edit.setText(text)

            qt_dialog = QtWidgets.QDialog(self)
            qt_dialog.setWindowTitle('Spreadsheet')
            qt_dialog.setLayout(layout)
            qt_dialog.setMinimumWidth(330)
            qt_dialog.setMinimumHeight(180)
            qt_dialog.show()

        if qt_invoker.UserType == 'curves_dir':
            well = qt_invoker.parent().source

            if not well.las:
                return
            text = StringIO()

            well.las.write(text, version=2.0, fmt="%10.5f")
            layout = QtWidgets.QVBoxLayout(self)
            qt_text_edit = QtWidgets.QTextEdit(self)
            qt_text_edit.setReadOnly(True)
            qt_text_edit.setCurrentFont(QtGui.QFont("Liberation Mono", 10))
            layout.addWidget(qt_text_edit)
            qt_text_edit.setText(text.getvalue())

            qt_dialog = QtWidgets.QDialog(self)
            qt_dialog.setWindowTitle('Spreadsheet')
            qt_dialog.setLayout(layout)
            qt_dialog.setMinimumWidth(1000)
            qt_dialog.setMinimumHeight(500)
            qt_dialog.show()

    def reset_content(self):
        """ general resetting of tree widget
            including refreshing of the whole tree in domain (begins from maincontext 'root' dir)
            including redraw of 2d_map and sections
        """
        self.blockSignals(True)

        self.clear()

        # self.treeWidget.setDragEnabled(True)
        # self.treeWidget.setAcceptDrops(True)
        # self.treeWidget.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove)

        main_context.root_dir.set_qt_items(self)
        main_context.root_dir.qt_item.setExpanded(True)
        if self.invisibleRootItem().flags() & QtCore.Qt.ItemIsDropEnabled:
            self.invisibleRootItem().setFlags(
                self.invisibleRootItem().flags() ^ QtCore.Qt.ItemIsDropEnabled)

        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)

        # print('wells = {0}'.format(list(well.name for well in main_context.wells_list)))
        # print(main_context.root_dir)

        self.window().tab_2d_map.refresh()
        self.window().tab_sections.reset()
        self.blockSignals(False)

    def refresh(self):
        """ more light then reset_content() resetting of the treewidget
        including BFS redefining of the domain items begins from the 'root' dir, which placed in the main context
        including redraw of 2d_map and sections
        """
        self.blockSignals(True)

        main_context.root_dir.refresh_qt_items()

        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)

        # print('wells = {0}'.format(list(well.name for well in main_context.wells_list)))
        # print(main_context.root_dir)

        self.window().tab_2d_map.refresh()
        self.window().tab_sections.reset()
        self.blockSignals(False)
