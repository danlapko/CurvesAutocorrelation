""" Stores all current project variables and methods for them.
    This module realize singletones pattern. """
import pickle

from app.domain.wells_dir import WellsDir

root_dir = WellsDir(None, 'root')  # папка верхнего уровня настоящего проекта (имя = 'root')
wells_list = list()  # список всех скважин проекта
tops_list = list()  # список всех маркеров проекта
project_file = None  # файл сериализациии проекта (для сохранения проекта)


def reset_context():
    """ reset current project (delete all content) """
    global root_dir
    global wells_list
    global tops_list

    del root_dir, wells_list, tops_list
    root_dir = WellsDir(None, 'root')
    wells_list = list()
    tops_list = list()


class Project:
    """ current project accessory class (used for serialization)"""
    def __init__(self, root_dir=None, wells_list=None, tops_list=None, project_file=None):
        self.root_dir = root_dir
        self.wells_list = wells_list
        self.tops_list = tops_list
        self.project_file = project_file


def serialize(file):
    """ serialization with pickle
        file - target project path """
    global root_dir
    global wells_list
    global tops_list
    global project_file
    project_file = file

    current_project = Project(root_dir, wells_list, tops_list, file)
    f = open(file, 'wb')
    pickle.dump(current_project, f)


def deserialize(file):
    """ deserialization with pickle
        file - target project path """
    global root_dir
    global wells_list
    global tops_list
    global project_file

    f = open(file, 'rb')

    current_project = pickle.load(f)
    root_dir = current_project.root_dir
    wells_list = current_project.wells_list
    tops_list = current_project.tops_list
    project_file = current_project.project_file
