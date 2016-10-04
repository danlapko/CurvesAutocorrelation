import os

import pytest


from app.util.config import Config


@pytest.fixture(scope="module")
def well():
    from app.domain.well import Well
    return Well()


@pytest.fixture(scope="module")
def top():
    from app.domain.top import Top
    return Top()


def test_read_dev(well):
    well.read_dev(os.path.join(Config.test_data_path, './dev/810_1.dev'))


def test_read_las(well):
    well.read_las(os.path.join(Config.test_data_path, './las/810_1.las'))


def test_add_top(well, top):
    well.add_top(top)

# print(well.las.get_curve('DEPT'))
