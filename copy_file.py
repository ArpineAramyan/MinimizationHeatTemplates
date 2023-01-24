import os
import shutil
import re
import pathlib


def copy_file(path, file, temporary_home, temporary_home_copy, path_parts, home, home_copy):
    file_path = os.path.join(home, path, file)
    new_file_path = os.path.join(home_copy, path, file)
    if len(path_parts) == 0:
        shutil.copyfile(file_path, new_file_path)
        return
    if not os.path.isdir(os.path.join(temporary_home_copy, path_parts[0])):
        os.mkdir(os.path.join(temporary_home_copy, path_parts[0]))
        copy_file(path, file, os.path.join(temporary_home, path_parts[0]),
                  os.path.join(temporary_home_copy, path_parts[0]), path_parts[1:], home, home_copy)
    else:
        copy_file(path, file, os.path.join(temporary_home, path_parts[0]),
                  os.path.join(temporary_home_copy, path_parts[0]), path_parts[1:], home, home_copy)
    return
