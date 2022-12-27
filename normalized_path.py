import re
import os.path

def norm_path(path_global, file_path):
    ret = ''
    re_match1 = re.match('^../', file_path)
    re_match2 = re.match('^./', file_path)

    if re_match1 or re_match2:
        p1 = os.path.split(path_global)
        p2 = p1[0]
        if re_match1:
            ret = os.path.join(p2, file_path[3:])
        elif re_match2:
            ret = os.path.join(path_global, file_path[2:])
        re_match1 = re.match('^../', file_path[3:])
        if re_match1:
            ret = norm_path(p2, file_path[3:])        
    else:
        ret = os.path.join(path_global, file_path)
    return ret      
