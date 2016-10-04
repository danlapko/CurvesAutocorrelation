from app.domain.well import *


class Top:
    """ Top entity and their attributes """
    def __init__(self, well=None, well_name=None, surface_id=None, md=None):
        # basic fields
        self.well = well  # reference to well contains this top
        self.well_name = well_name  # ==self.well.name
        self.surface_id = surface_id  # top id
        self.md = md  # top md (measure depth)

        # addition fields  (coordinates)
        self.x = float()
        self.y = float()
        self.z = float()
        self.tvd = float()

        #  item for visualization in qt
        self.qt_item = None

    def add_well(self, well):
        """ add or change the reference to well contains this top
        :param well: well reference
        :return: True
        """
        assert isinstance(well, Well), '"well" expected to be item of Well, but {0} found'.format(well)
        self.well = well
        return True

    def calculate_addition_fields(self):
        """ calculates coordinates of the top using top md and well information
            if top is placed in space between two logging points of the well then
            we'll use the linear approximation """
        if not self.well:
            return

        if self.md < self.well.md[0]:
            self.x = self.well.x[0]
            self.y = self.well.y[0]
            self.z = self.well.z[0]
            self.tvd = self.well.tvd[0]

        elif self.md > self.well.md[-1]:
            self.x = self.well.x[-1]
            self.y = self.well.y[-1]
            self.z = self.well.z[-1]
            self.tvd = self.well.tvd[-1]

        else:
            for i, md in enumerate(self.well.md[:-1]):
                if self.well.md[i] <= self.md <= self.well.md[i + 1]:
                    delta_md = self.well.md[i + 1] - self.well.md[i]
                    actual_md = self.md - self.well.md[i]
                    koef = actual_md / delta_md

                    delta_x = self.well.x[i + 1] - self.well.x[i]
                    actual_x = delta_x * koef
                    self.x = self.well.x[i] + actual_x

                    delta_y = self.well.y[i + 1] - self.well.y[i]
                    actual_y = delta_y * koef
                    self.y = self.well.y[i] + actual_y

                    delta_z = self.well.z[i + 1] - self.well.z[i]
                    actual_z = delta_z * koef
                    self.z = self.well.z[i] + actual_z

                    delta_tvd = self.well.tvd[i + 1] - self.well.tvd[i]
                    actual_tvd = delta_tvd * koef
                    self.tvd = self.well.tvd[i] + actual_tvd
