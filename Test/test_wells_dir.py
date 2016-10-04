import pytest


@pytest.fixture(scope="module")
def wells_dir():
    from app.domain.wells_dir import WellsDir
    return WellsDir(None, 'root')


@pytest.fixture(scope="module")
def well():
    from app.domain.well import Well
    return Well()


def test_init():
    from app.domain.wells_dir import WellsDir
    WellsDir(None, 'root')


def test_add_well(wells_dir, well):
    wells_dir.add_well(well)
    assert well in wells_dir.wells_list
    print(wells_dir.wells_list)


def test_remove_well(wells_dir, well):
    wells_dir.remove_well(well)
    assert not well in wells_dir.wells_list
    print(wells_dir.wells_list)
