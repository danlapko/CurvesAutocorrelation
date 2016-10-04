from app.domain.top import *
from app.domain.well import *
from app.util.config import Config


class WellsDir:
    """ Dir entity and their attributes """
    def __init__(self, parent_dir, name, wells_list=None, sub_dirs_list=None):
        """
        :type sub_dirs_list: list of WellsDirs objects
        :type wells_list: list of Wells objects
        :type name: string
        :type parent_dir: WellsDir object
        """
        self.parent_dir = parent_dir
        self.name = name
        if wells_list:
            self.wells_list = wells_list
        else:
            self.wells_list = list()

        if sub_dirs_list:
            self.sub_dirs_list = sub_dirs_list
        else:
            self.sub_dirs_list = list()
        self.curves = list()  # all types of curves occurrence in the wells_list
        self.tops = list()  # all types of tops occurrence in the  wells_list

        # ---- qt_items ----
        self.qt_item = None

        self.curves_qt_item = None
        self.curves_qt_items_list = list()

        self.tops_qt_item = None
        self.tops_qt_items_list = list()

        # TODO check for unic well in wells_list

        self.generate_global_well_logs_list()
        self.generate_global_well_tops_list()

    def generate_global_well_logs_list(self):
        """ generate logs list for this Dir """
        self.curves.clear()
        for sub_dir in self.sub_dirs_list:
            sub_dir.generate_global_well_logs_list()
            for curve in sub_dir.curves:
                if curve not in self.curves:
                    self.curves.append(curve)

        for well in self.wells_list:
            for curve in well.get_curve_names_list():
                if curve not in self.curves:
                    self.curves.append(curve)

    def generate_global_well_tops_list(self):
        """ generate tops list for this Dir """
        self.tops.clear()
        for sub_dir in self.sub_dirs_list:
            sub_dir.generate_global_well_tops_list()
            for surface_id in sub_dir.tops:
                if surface_id not in self.tops:
                    self.tops.append(surface_id)

        for well in self.wells_list:
            for top in well.tops_list:
                if top.surface_id not in self.tops:
                    self.tops.append(top.surface_id)

    def add_top(self, top):
        """ adds top to appropriate well from this Dir by top.well_name
            if there is no appropriate well returns False
            :param top: Top object"""
        assert isinstance(top, Top), '"top" expected to be item of Top, but {0} found'.format(top)
        # TODO check for unic top in tops_list
        for well in self.wells_list:
            if well.name == top.well_name:
                well.add_top(top)
                top.add_well(well)
                self.generate_global_well_tops_list()
                return True

        for sub_dir in self.sub_dirs_list:
            if sub_dir.add_top:
                self.generate_global_well_tops_list()
                return True

        return False

    def add_well(self, well):
        """ adds new well to this Dir """
        # TODO check for unic well in wells_list
        assert isinstance(well, Well), '"well" expected to be item of Well, but {0} found'.format(well)
        well.parent_dir = self
        self.wells_list.append(well)
        self.generate_global_well_logs_list()
        self.generate_global_well_logs_list()

    def insert_well(self, well, index):
        """
        inserts well to this Dir in index place
        :param index: int
        :type well: Well object
        """
        if index in range(len(self.wells_list)):
            self.wells_list.insert(index, well)
        else:
            self.wells_list.append(well)

    def remove_well(self, well):
        self.wells_list.remove(well)
        self.generate_global_well_logs_list()
        self.generate_global_well_tops_list()

    def add_sub_dir(self, sub_dir):
        assert isinstance(sub_dir, WellsDir), '"sub_dir" expected to be item of WellsDir, but {0} found'.format(sub_dir)
        self.sub_dirs_list.append(sub_dir)
        sub_dir.parent_dir = self

        self.generate_global_well_logs_list()
        self.generate_global_well_tops_list()

    def remove_sub_dir(self, sub_dir):
        self.sub_dirs_list.remove(sub_dir)
        self.generate_global_well_logs_list()
        self.generate_global_well_tops_list()

    def set_qt_items(self, qt_item_parent):
        """
        sets:
        * self (dir) qt item
        * global well logs qt item
        * global well tops qt item
        * each well qt item
        * each unic name log item
        * each top item
        then goes to subdirs and wells
        :type qt_item_parent: qt.treewidget item
        """
        self.generate_global_well_logs_list()
        self.generate_global_well_tops_list()

        from PyQt5 import QtWidgets
        from PyQt5 import QtGui
        from PyQt5 import QtCore

        # dir tree_widget item
        self.qt_item = QtWidgets.QTreeWidgetItem(qt_item_parent)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(Config.icons_path, "wells_dir.png")), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.qt_item.setIcon(0, icon)
        self.qt_item.setText(0, self.name)
        self.qt_item.setCheckState(0, QtCore.Qt.Unchecked)
        setattr(self.qt_item, 'previous_state', QtCore.Qt.Unchecked)
        setattr(self.qt_item, 'source', self)
        self.qt_item.UserType = 'wells_dir'

        # global well logs tree_widget item
        self.curves_qt_item = QtWidgets.QTreeWidgetItem(self.qt_item)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(Config.icons_path, "global_well_logs.png")), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.curves_qt_item.setIcon(0, icon)
        if self.name == 'root':
            self.curves_qt_item.setText(0, 'Global well logs')
        else:
            self.curves_qt_item.setText(0, 'Local well logs')
        self.curves_qt_item.setCheckState(0, QtCore.Qt.Unchecked)
        setattr(self.curves_qt_item, 'previous_state', QtCore.Qt.Unchecked)
        self.curves_qt_item.UserType = 'curve_aliases_dir'
        self.curves_qt_item.setFlags(
            self.curves_qt_item.flags() ^ QtCore.Qt.ItemIsDropEnabled ^ QtCore.Qt.ItemIsDragEnabled ^ QtCore.Qt.ItemIsSelectable)

        # global well tops tree_widget item
        self.tops_qt_item = QtWidgets.QTreeWidgetItem(self.qt_item)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(Config.icons_path, "global_well_tops.png")), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.tops_qt_item.setIcon(0, icon)
        if self.name == 'root':
            self.tops_qt_item.setText(0, 'Global well tops')
        else:
            self.tops_qt_item.setText(0, 'Local well tops')
        self.tops_qt_item.setCheckState(0, QtCore.Qt.Unchecked)
        setattr(self.tops_qt_item, 'previous_state', QtCore.Qt.Unchecked)
        self.tops_qt_item.UserType = 'top_aliases_dir'
        self.tops_qt_item.setFlags(
            self.tops_qt_item.flags() ^ QtCore.Qt.ItemIsDropEnabled ^ QtCore.Qt.ItemIsDragEnabled ^ QtCore.Qt.ItemIsSelectable)

        # global well logs (curves) tree_widget items
        self.curves_qt_items_list.clear()
        for curve in self.curves:
            curve_qt_item = QtWidgets.QTreeWidgetItem(self.curves_qt_item)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(os.path.join(Config.icons_path, "curve.png")), QtGui.QIcon.Normal,
                           QtGui.QIcon.Off)
            curve_qt_item.setIcon(0, icon)
            curve_qt_item.setText(0, curve)
            curve_qt_item.setCheckState(0, QtCore.Qt.Unchecked)
            setattr(curve_qt_item, 'previous_state', QtCore.Qt.Unchecked)
            curve_qt_item.UserType = 'curve_alias'
            curve_qt_item.setFlags(
                curve_qt_item.flags() ^ QtCore.Qt.ItemIsDropEnabled ^ QtCore.Qt.ItemIsDragEnabled ^ QtCore.Qt.ItemIsSelectable)
            self.curves_qt_items_list.append(curve_qt_item)

        # global well tops  tree_widget items
        self.tops_qt_items_list.clear()
        for top in self.tops:
            top_qt_item = QtWidgets.QTreeWidgetItem(self.tops_qt_item)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(os.path.join(Config.icons_path, "top.png")), QtGui.QIcon.Normal,
                           QtGui.QIcon.Off)
            top_qt_item.setIcon(0, icon)
            top_qt_item.setText(0, top)
            top_qt_item.setCheckState(0, QtCore.Qt.Unchecked)
            setattr(top_qt_item, 'previous_state', QtCore.Qt.Unchecked)
            top_qt_item.UserType = 'top_alias'
            top_qt_item.setFlags(
                top_qt_item.flags() ^ QtCore.Qt.ItemIsDropEnabled ^ QtCore.Qt.ItemIsDragEnabled ^ QtCore.Qt.ItemIsSelectable)
            self.tops_qt_items_list.append(top_qt_item)

        # go to sub wells
        for well in self.wells_list:
            well.set_qt_items(self.qt_item)

        # go to sub_dirs
        for sub_dir in self.sub_dirs_list:
            sub_dir.set_qt_items(self.qt_item)

    def refresh_qt_items(self):
        """ used for situation when wells or list of wells were moved in UI"""
        self.generate_global_well_logs_list()
        self.generate_global_well_tops_list()

        from PyQt5 import QtWidgets
        from PyQt5 import QtGui
        from PyQt5 import QtCore

        # global well logs (curves) tree_widget items

        for qt_curve in self.curves_qt_items_list:
            self.curves_qt_item.removeChild(qt_curve)

        self.curves_qt_items_list.clear()

        for curve in self.curves:
            curve_qt_item = QtWidgets.QTreeWidgetItem(self.curves_qt_item)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(os.path.join(Config.icons_path, "curve.png")), QtGui.QIcon.Normal,
                           QtGui.QIcon.Off)
            curve_qt_item.setIcon(0, icon)
            curve_qt_item.setText(0, curve)
            curve_qt_item.setCheckState(0, QtCore.Qt.Unchecked)
            setattr(curve_qt_item, 'previous_state', QtCore.Qt.Unchecked)
            curve_qt_item.UserType = 'curve_alias'
            curve_qt_item.setFlags(
                curve_qt_item.flags() ^ QtCore.Qt.ItemIsDropEnabled ^ QtCore.Qt.ItemIsDragEnabled ^ QtCore.Qt.ItemIsSelectable)
            self.curves_qt_items_list.append(curve_qt_item)

        # global well tops  tree_widget items
        for qt_top in self.tops_qt_items_list:
            self.tops_qt_item.removeChild(qt_top)

        self.tops_qt_items_list.clear()
        for top in self.tops:
            top_qt_item = QtWidgets.QTreeWidgetItem(self.tops_qt_item)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(os.path.join(Config.icons_path, "top.png")), QtGui.QIcon.Normal,
                           QtGui.QIcon.Off)
            top_qt_item.setIcon(0, icon)
            top_qt_item.setText(0, top)
            top_qt_item.setCheckState(0, QtCore.Qt.Unchecked)
            setattr(top_qt_item, 'previous_state', QtCore.Qt.Unchecked)
            top_qt_item.UserType = 'top_alias'
            top_qt_item.setFlags(
                top_qt_item.flags() ^ QtCore.Qt.ItemIsDropEnabled ^ QtCore.Qt.ItemIsDragEnabled ^ QtCore.Qt.ItemIsSelectable)
            self.tops_qt_items_list.append(top_qt_item)

        # go to sub_dirs
        for sub_dir in self.sub_dirs_list:
            sub_dir.refresh_qt_items()

    def get_checked_wells(self):
        checked_wells = list()
        for well in self.wells_list:
            if well.qt_item.checkState(0):
                checked_wells.append(well)
        for dir in self.sub_dirs_list:
            checked_wells += dir.get_checked_wells()
        return checked_wells

    def __repr__(self, shift=''):
        res = shift + self.name + '\n'
        shift += '   '
        for well in self.wells_list:
            res += shift + '--' + well.name + '\n'

        for dir in self.sub_dirs_list:
            res += dir.__repr__(shift) + '\n'

        return res
