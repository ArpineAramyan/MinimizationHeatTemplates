import os
import shutil


def copy_file(path, file_name, path_parts, home, home_copy):
    """
    :param path: line with directories from home to file
    :param file_name: name of the file to be copied
    :param path_parts: every directory
    :param home_copy: path where all copies of files will be located
    :param home: home path
    """
    if len(path_parts) == 0:
        shutil.copyfile(os.path.join(home, file_name), os.path.join(home_copy, file_name))
        return
    if not os.path.isdir(os.path.join(home_copy, path_parts[0])):
        os.mkdir(os.path.join(home_copy, path_parts[0]))
        copy_file(path, file_name, path_parts[1:], os.path.join(home, path_parts[0]),
                  os.path.join(home_copy, path_parts[0]))
    else:
        copy_file(path, file_name, path_parts[1:], os.path.join(home, path_parts[0]),
                  os.path.join(home_copy, path_parts[0]))
    return
