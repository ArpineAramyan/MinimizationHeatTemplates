import yaml
import flatdict
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
    else:
        ret = os.path.join(path_global, file_path)

    re_match1 = re.match('^../', file_path[3:])

    if re_match1:
        ret = norm_path(p2, file_path[3:])

    return ret      

key_env =  'resource_registry.*'
key_words = '(.*get_file$|resources.*type$)'

list_of_files = []

def env_files(env_file):
    with open(env_file, 'r') as fd2:
        env = yaml.load(fd2, Loader=yaml.Loader)

    env_path = os.path.split(env_file)
    dict_env = flatdict.FlatDict(env, delimiter=' - ')

    for key, value in dict_env.items():
        re_match = re.match(key_env, key)
        if re_match and isinstance(value, str):
            absvalue = os.path.join(env_path[0], value)
            if os.path.isfile(absvalue):
                list_of_files.append(absvalue)

def heat_files(heat_file):
    with open(heat_file, 'r') as fd:
        heat = yaml.load(fd, Loader=yaml.Loader)

    heat_path = os.path.split(heat_file)
    dict_heat = flatdict.FlatDict(heat, delimiter=' - ')
    
    for key, value in dict_heat.items():
        re_match = re.match(key_words, key)
        if re_match and isinstance(value, str):
            absvalue = norm_path(heat_path[0], value) 
            if os.path.isfile(absvalue):
                list_of_files.append(absvalue)  
