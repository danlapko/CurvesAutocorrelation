import os
import re

import lasio

from app.util.config import Config
from app.util.logger import log


class Well:
    """ Well entity and their attributes """
    def __init__(self, name=None):
        parent_dir = None  # the reference to the dir which contains this well

        # head fields (from *.dev)
        self.name = name
        self.head_x = float()
        self.head_y = float()
        self.offset = float()

        # coordinate columns (from *.dev)
        self.md, self.x, self.y, self.z, self.tvd, self.dx, self.dy, self.azim, self.incl, self.dls = list(), list(), list(), list(), list(), list(), list(), list(), list(), list()

        # las file
        self.las = None

        # list of well_tops
        self.tops_list = list()

        # qt_items
        self.qt_item = None
        self.curves_qt_item = None
        self.tops_qt_item = None

    def read_dev(self, dev_file):
        """ reads las file using the following parser
        :param dev_file: path to target file
        """
        try:
            f = open(dev_file, 'r')
            lines = f.readlines()

            # check for file length validity
            if len(lines) < 17:
                log.warning('Too short file: "%s"' % dev_file)
                return False

            def read_head(self, lines):
                """ submethod for reading las file head information """
                try:
                    self.name = re.search(r'# WELL NAME:\s*(?P<well_name>\S+)', lines[1]).group('well_name')
                    self.head_x = float(
                        re.search(r'# WELL HEAD X-COORDINATE:\s*(?P<head_x>[-+]?\d+\.\d+)', lines[2]).group('head_x'))
                    self.head_y = float(
                        re.search(r'# WELL HEAD Y-COORDINATE:\s*(?P<head_y>[-+]?\d+\.\d+)', lines[3]).group('head_y'))
                    self.offset = float(
                        re.search(r'# WELL OFFSET \(from MSL\):\s*(?P<offset>[-+]?\d+\.\d+)', lines[4]).group('offset'))
                    log.debug(
                        'name={0}\t head_x={1}\t head_y={2}\t offset={3}'.format(self.name, self.head_x,
                                                                                 self.head_y,
                                                                                 self.offset))
                except AttributeError as ex:
                    log.warning(str(ex))
                    return False
                return True

            # reads the head information
            if not read_head(self, lines):
                return False, '*.dev file header format not valid'

            # reads the list of available columns
            columns = re.findall(r'\s*(\b\w+)\s*', lines[13])
            columns = [column.lower() for column in columns]
            for column in columns:
                getattr(self, column).clear()

            log.debug('columns=' + str(columns))

            # reads coordinates information by each column
            for line in lines[15:]:
                values = re.findall(r'\s*([-+]?\d+\.\d+)\s*', line)
                for i in range(len(columns)):
                    getattr(self, columns[i]).append(float(values[i]))

            self.check_coordinate_columns_validity()  # verify validity of the columns coordinates
        except Exception as ex:
            log.error(str(ex))
            return False
        return True

    def read_las(self, las_file):
        """ reads las file using lasio
        :param las_file: path to target file
        """
        self.las = lasio.read(las_file)  # contains all well lasfile information

    def check_coordinate_columns_validity(self):
        # TODO check the validity of the columns data
        pass

    def add_top(self, top):
        """
        :param top: already inited Top object
        """
        from app.domain.top import Top
        assert isinstance(top, Top), '"top" expected to be item of Top, but {0} found'.format(top)
        tops_names = [top_in_list.surface_id for top_in_list in self.tops_list]
        if top.surface_id in tops_names:
            del top
            return False
        self.tops_list.append(top)
        return True

    def get_curve_names_list(self):
        """ accessory method """
        if self.las is None:
            return []

        res = list()
        for curve in self.las.curves:
            if curve.mnemonic != "DEPT":
                res.append(curve.mnemonic)
        return res

    def set_qt_items(self, tree_widget_item_parent):
        """ this method sets qt.treewidget items for:
            * self.well
            * list of the wells curves (from the self.las file)
            * list of the wells tops (from the list of the self.tops_list)
            * each curve item
            * each top item
            :param tree_widget_item_parent: parent dir qt.treewiget item
        """
        from PyQt5 import QtWidgets
        from PyQt5 import QtGui
        from PyQt5 import QtCore

        # self tree_widget item
        self.qt_item = QtWidgets.QTreeWidgetItem(tree_widget_item_parent)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(Config.icons_path, "well.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.qt_item.setIcon(0, icon)
        self.qt_item.setText(0, self.name)
        self.qt_item.setCheckState(0, QtCore.Qt.Unchecked)
        setattr(self.qt_item, 'previous_state', QtCore.Qt.Unchecked)
        self.qt_item.UserType = 'well'
        setattr(self.qt_item, 'source', self)
        self.qt_item.setFlags(self.qt_item.flags() ^ QtCore.Qt.ItemIsDropEnabled)
        if not self.las:
            self.qt_item.setText(1, 'needs las')
            self.qt_item.setForeground(1, QtGui.QBrush(QtCore.Qt.red))
        elif len(self.md) == 0:
            self.qt_item.setText(1, 'needs dev')
            self.qt_item.setForeground(1, QtGui.QBrush(QtCore.Qt.red))
        else:
            self.qt_item.setText(1, 'ok')

        # curves tree_widget item
        self.curves_qt_item = QtWidgets.QTreeWidgetItem(self.qt_item)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(Config.icons_path, "global_well_logs.png")), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.curves_qt_item.setIcon(0, icon)
        self.curves_qt_item.setText(0, 'Well logs')
        self.curves_qt_item.setCheckState(0, QtCore.Qt.Unchecked)
        setattr(self.curves_qt_item, 'previous_state', QtCore.Qt.Unchecked)
        self.curves_qt_item.UserType = 'curves_dir'
        self.curves_qt_item.setFlags(
            self.curves_qt_item.flags() ^ QtCore.Qt.ItemIsDropEnabled ^ QtCore.Qt.ItemIsDragEnabled ^ QtCore.Qt.ItemIsSelectable)

        # tops tree_widget item
        self.tops_qt_item = QtWidgets.QTreeWidgetItem(self.qt_item)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(Config.icons_path, "global_well_tops.png")), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.tops_qt_item.setIcon(0, icon)
        self.tops_qt_item.setText(0, 'Well tops')
        self.tops_qt_item.setCheckState(0, QtCore.Qt.Unchecked)
        setattr(self.tops_qt_item, 'previous_state', QtCore.Qt.Unchecked)
        self.tops_qt_item.UserType = 'tops_dir'
        self.tops_qt_item.setFlags(
            self.tops_qt_item.flags() ^ QtCore.Qt.ItemIsDropEnabled ^ QtCore.Qt.ItemIsDragEnabled ^ QtCore.Qt.ItemIsSelectable)

        # set each curve tree_widget item
        for curve_name in self.get_curve_names_list():
            curve_qt_item = QtWidgets.QTreeWidgetItem(self.curves_qt_item)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(os.path.join(Config.icons_path, "curve.png")), QtGui.QIcon.Normal,
                           QtGui.QIcon.Off)
            curve_qt_item.setIcon(0, icon)
            curve_qt_item.setText(0, curve_name)
            curve_qt_item.setCheckState(0, QtCore.Qt.Unchecked)
            setattr(curve_qt_item, 'previous_state', QtCore.Qt.Unchecked)
            curve_qt_item.UserType = 'curve'
            curve_qt_item.setFlags(
                curve_qt_item.flags() ^ QtCore.Qt.ItemIsDropEnabled ^ QtCore.Qt.ItemIsDragEnabled ^ QtCore.Qt.ItemIsSelectable)
            setattr(curve_qt_item, 'source', self.las.get_curve(curve_name))
            setattr(self.las.get_curve(curve_name), 'qt_item', curve_qt_item)

        # set each top tree_widget item
        for top in self.tops_list:
            top.qt_item = QtWidgets.QTreeWidgetItem(self.tops_qt_item)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(os.path.join(Config.icons_path, "top.png")), QtGui.QIcon.Normal,
                           QtGui.QIcon.Off)
            top.qt_item.setIcon(0, icon)
            top.qt_item.setText(0, top.surface_id)
            top.qt_item.setCheckState(0, QtCore.Qt.Unchecked)
            setattr(top.qt_item, 'previous_state', QtCore.Qt.Unchecked)
            top.qt_item.UserType = 'top'
            top.qt_item.setFlags(
                top.qt_item.flags() ^ QtCore.Qt.ItemIsDropEnabled ^ QtCore.Qt.ItemIsDragEnabled ^ QtCore.Qt.ItemIsSelectable)
            setattr(top.qt_item, 'source', top)
