import re
import os.path


def normalized_rel_path(path_global, file_path):
    normalized = ''
    previous_match = re.match('^../', file_path)
    current_match = re.match('^./', file_path)

    if previous_match or current_match:
        directories = os.path.split(path_global)[0]
        if previous_match:
            normalized = os.path.join(directories, file_path[3:])
        elif current_match:
            normalized = os.path.join(path_global, file_path[2:])
        previous_match = re.match('^../', file_path[3:])
        if previous_match:
            normalized = normalized_rel_path(directories, file_path[3:])
    else:
        normalized = os.path.join(path_global, file_path)
    return normalized
