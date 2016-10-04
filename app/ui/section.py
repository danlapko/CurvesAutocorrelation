from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class Section(FigureCanvas):
    """ Object of this class displays one section """
    def __init__(self, well, dpi=90):
        """
        :type well: well which will be displayed
        """
        self.well = well

        self.figure = Figure(dpi=dpi, facecolor="white")
        super().__init__(self.figure)
        # self.ax = self.figure.add_subplot(1, 1,1)
        self.refresh()

    def refresh(self):
        """ executes every time when new curve have been checked"""
        self.figure.clear()
        if not self.well.las:
            self.hide()
            return
        checked_curves = list(
            filter(lambda curve: curve.mnemonic != "DEPT" and curve.qt_item.checkState(0), self.well.las.curves))
        if len(checked_curves) < 1:
            self.hide()
            return

        self.setFixedWidth(0)
        self.figure.set_figwidth(0)

        self.figure.suptitle('"' + self.well.name + '"', fontsize=10, fontweight='normal')
        number_of_curves = len(checked_curves)

        for i, curve in enumerate(checked_curves):
            if curve.qt_item.checkState(0):
                self.setFixedWidth(self.geometry().width() + 200)
                self.figure.set_figwidth(self.figure.get_figwidth() + 200 / self.figure.get_dpi())

                ax = self.figure.add_subplot(1, number_of_curves, i + 1)
                ax.set_title(curve.mnemonic, fontsize=8, fontweight='normal')
                ax.tick_params(axis='both', which='major', labelsize=7)
                ax.tick_params(axis='both', which='minor', labelsize=7)
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                # Only show ticks on the left and bottom spines
                ax.yaxis.set_ticks_position('left')
                ax.xaxis.set_ticks_position('bottom')

                ax.invert_yaxis()
                ax.grid(color="gray")
                ax.set_ylabel('depth (m)', fontsize=7)
                # t = np.arange(0.0, 3.0, 0.01)
                # s = np.sin(4 * np.pi * t)
                ax.plot(curve.data, self.well.las["DEPT"])

        self.figure.tight_layout(rect=(0, 0, 1, 0.98))