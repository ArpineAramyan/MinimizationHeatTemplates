import os
import shutil
import re
import pathlib


def copy_file(path, file, home, home_copy, path_parts, home_at_first, home_copy_at_first):
    file_path = os.path.join(home_at_first, path, file)
    new_file_path = os.path.join(home_copy_at_first, path, file)
    if len(path_parts) == 0:
        shutil.copyfile(file_path, new_file_path)
        return
    if not os.path.isdir(os.path.join(home_copy, path_parts[0])):
        os.mkdir(os.path.join(home_copy, path_parts[0]))
        copy_file(path, file, os.path.join(home, path_parts[0]), os.path.join(home_copy, path_parts[0]),
                   path_parts[1:], home_at_first, home_copy_at_first)
    else:
        copy_file(path, file, os.path.join(home, path_parts[0]), os.path.join(home_copy, path_parts[0]),
                   path_parts[1:], home_at_first, home_copy_at_first)
    return