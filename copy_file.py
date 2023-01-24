import os
import shutil
import re
import pathlib


def copy_file(path, file_name, path_parts, home, home_copy, temporary_home, temporary_home_copy):
    """
    :param path: line with directories from home to file
    :param file_name: name of the file to be copied
    :param path_parts: every directory in path
    :param home:
    :param home_copy: path where all copies of files will be located
    :param temporary_home: home that will be changed during running
    :param temporary_home_copy: home_copy that will be changed during running
    """
    file_path = os.path.join(home, path, file_name)
    new_file_path = os.path.join(home_copy, path, file_name)
    if len(path_parts) == 0:
        shutil.copyfile(file_path, new_file_path)
        return
    if not os.path.isdir(os.path.join(temporary_home_copy, path_parts[0])):
        os.mkdir(os.path.join(temporary_home_copy, path_parts[0]))
        copy_file(path, file_name, path_parts[1:], home, home_copy, os.path.join(temporary_home, path_parts[0]),
                  os.path.join(temporary_home_copy, path_parts[0]))
    else:
        copy_file(path, file_name, path_parts[1:], home, home_copy, os.path.join(temporary_home, path_parts[0]),
                  os.path.join(temporary_home_copy, path_parts[0]))
    return
