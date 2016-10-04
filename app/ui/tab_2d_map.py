import matplotlib
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from app.domain import main_context
from app.util.logger import log


class Tab2DMap(FigureCanvas):
    """ Map is instance of PyQt5.QWidget produced by matplotlib.FigureCanvas """

    def __init__(self, dpi=90):
        self.figure = Figure(dpi=dpi, facecolor="black")
        super().__init__(self.figure)

        self.ax = self.figure.add_subplot(1, 1, 1)
        self.refresh()

    def refresh(self):
        """ executes every time when there was checked new well or new top """
        self.ax.clear()
        self.ax.set_ylabel("y-axis (m)", color="white")
        self.ax.set_xlabel("x-axis (m)", color="white")
        self.ax.set_axis_bgcolor("black")
        self.ax.tick_params(color='white', labelcolor='white')
        for spine in self.ax.spines.values():
            spine.set_color('white')
        self.ax.tick_params(axis='both', which='major', labelsize=8)
        self.ax.grid(color="gray")

        y_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
        self.ax.yaxis.set_major_formatter(y_formatter)

        # ----получаем два списка  x и y координат скважин----
        checked_wells = [well for well in main_context.wells_list if (well.qt_item.checkState(0) and len(well.md) > 0)]
        wells_x_list = [well.x[-1] for well in checked_wells]
        wells_y_list = [well.y[-1] for well in checked_wells]
        wells_names = [well.name for well in checked_wells]
        log.debug("(fileName, x, y) = {0}".format(list(zip(wells_names, wells_x_list, wells_y_list))))

        self.ax.scatter(wells_x_list, wells_y_list, marker=".",
                        c="#666600", edgecolors="#666600")

        for x, y, name in zip(wells_x_list, wells_y_list, wells_names):
            self.ax.annotate('{}'.format(name),
                             xy=(x, y), color='yellow', fontsize=10)

        # ----получаем два списка  x и y координат well_tops----
        checked_tops = [top for top in main_context.tops_list if top.qt_item.checkState(0)]
        tops_x_list = [top.x for top in checked_tops]
        tops_y_list = [top.y for top in checked_tops]
        tops_names = [top.well_name + ' ' + top.surface_id for top in checked_tops]

        self.ax.scatter(tops_x_list, tops_y_list, marker=".",
                        c="#89060D", edgecolors="#89060D")

        for x, y, name in zip(tops_x_list, tops_y_list, tops_names):
            self.ax.annotate('{}'.format(name),
                             xy=(x, y), color='red', fontsize=10)

        # ---------------- масштабируем --------------------------
        x_list = wells_x_list + tops_x_list
        y_list = wells_y_list + tops_y_list

        x_min = min(x_list, default=0)
        x_max = max(x_list, default=1)
        delta_x = x_max - x_min

        y_min = min(y_list, default=0)
        y_max = max(y_list, default=1)
        delta_y = y_max - y_min

        delta_max = max([delta_x, delta_y])

        self.ax.set_xlim([x_min - delta_max / 10, x_min + delta_max + delta_max / 10])
        self.ax.set_ylim([y_min - delta_max / 10, y_min + delta_max + delta_max / 10])
        start, end = self.ax.get_xlim()
        self.ax.xaxis.set_ticks(np.linspace(start, end, 13))
        start, end = self.ax.get_ylim()
        self.ax.yaxis.set_ticks(np.linspace(start, end, 13))

        self.draw()
