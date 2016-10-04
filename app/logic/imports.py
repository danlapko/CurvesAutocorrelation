""" module implements several types of import files """
import re

import lasio

from app.domain import main_context
from app.domain.top import Top
from app.domain.well import Well
from app.util.logger import log


def import_dev(files_list, wells_dir):
    """
    Looks if well with appropriate name (name from dev file) is in maincotext
      then parses this dev file into this well
    else if there is no appropriate well
      then creates new well and parse dev file into this well
    :param wells_dir: target dir to import to
    :param files_list: list of files paths
    """
    log.debug("i'm in import_dev()")
    broken_files = str()

    for file_name in files_list:
        well = Well()
        if not well.read_dev(file_name):
            broken_files += file_name + '\n'
            continue

        well_names = [well_in_list.name for well_in_list in main_context.wells_list]
        if well.name not in well_names:
            main_context.wells_list.append(well)
            wells_dir.add_well(well)

        else:
            exist_well = main_context.wells_list[well_names.index(well.name)]
            exist_well.read_dev(file_name)
    return broken_files


def import_las(files_list, wells_dir):
    """
    Looks if well with appropriate name (name from las file) is in maincotext
      then parses this las file into this well
    else if there is no appropriate well
      then creates new well and parse las file into this well
    :param wells_dir: target dir to import in
    :type files_list: list of files paths
    """
    log.debug("i'm in import_las()")
    broken_files = str()

    for file_name in files_list:
        try:
            las = lasio.read(file_name)
            if las["DEPT"] is None:
                log.debug('las["DEPT"]={0}'.format(las["DEPT"]))
                raise ValueError('las file has no DEPT curve')
            # log.debug(las.well['WELL'].value)
            if all(str(las.well['WELL'].value) != well.name for well in main_context.wells_list):
                well = Well(str(las.well['WELL'].value))
                well.las = las
                main_context.wells_list.append(well)
                wells_dir.add_well(well)
            else:
                well_dict = {well.name: well for well in main_context.wells_list}
                well = well_dict.get(str(las.well['WELL'].value))
                assert well, well_dict
                well.las = las
        except Exception:
            broken_files += file_name + '\n'

    return broken_files


def import_well_tops(files_list, wells_dir):
    """
    If there is well with appropriate name (name from tops file)
    then add this top to this well
    else ignore this top
    :type files_list: list of files paths
    """
    log.debug("i'm in import_well_tops()")
    broken_files = str()

    for file_name in files_list:
        try:
            f = open(file_name)
            lines = f.readlines()

            well_names = [well_in_list.name for well_in_list in main_context.wells_list]

            if not re.match(r'[-+]?\d+\.\d+', lines[0].split()[2]):
                lines.remove(lines[0])

            try:
                for line in lines:
                    m = re.match('\s*(?P<well_name>\S+)\s+(?P<surface_id>\S+)\s+(?P<md>[-+]?\d+\.\d+)\s*', line)
                    if not m:
                        log.warning('not match: %s' % line)
                        broken_files += file_name + '\n'
                        continue

                    well_name, surface_id, md = m.groups()

                    top = Top(well_name=well_name, surface_id=surface_id, md=float(md))
                    if top.well_name in well_names:
                        well = main_context.wells_list[well_names.index(top.well_name)]
                        if well.add_top(top):
                            top.add_well(well)
                            main_context.tops_list.append(top)
                            top.calculate_addition_fields()
            except ValueError as ex:
                log.error(line + '  ' + str(ex))
                broken_files += file_name + '\n'
        except Exception:
            broken_files += file_name + '\n'
    return broken_files
