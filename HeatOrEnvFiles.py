import yaml
import flatdict
import sys
import re
import os.path
from normalized_path import norm_path

key_env =  'resource_registry.*'
key_words = '(.*get_file$|resources.*type$)'
h_f = '^heat_template_version'
y_f = '.*yaml$'

list_of_files = [{}]

def for_plan_env(eh_file):
    with open(eh_file, 'r') as fd:
        eh = yaml.load(fd, Loader=yaml.Loader)

    eh_path = os.path.split(eh_file)
    eh_dict = flatdict.FlatDict(eh, delimiter=' - ')
    for key, value in eh_dict.items():
        if key == 'environments':
            for i in value:
                if i.get('path'):
                    absvalue = norm_path(eh_path[0], i.get('path'))
                    if os.path.isfile(absvalue):
                        #print(env_path[1]) тут только plan-env
                        list_of_files.append(absvalue) 

def env_files_helper(dict_env, env_path):
    for key, value in dict_env.items():
        re_match = re.match(key_env, key)
        if re_match and isinstance(value, str):
            if value == 'None':
                list_of_files[0].pop(key, 1)
            else:
                absvalue = norm_path(env_path[0], value)
                if os.path.isfile(absvalue):
                    print(env_path[1])
                    list_of_files[0].update({key: absvalue}) 

def heat_files_helper(dict_heat, heat_path):
    for key, value in dict_heat.items():
        re_match = re.match(key_words, key)
        if re_match and isinstance(value, str):
            absvalue = norm_path(heat_path[0], value) 
            if os.path.isfile(absvalue):
                list_of_files.append(absvalue)  
                
def heat_or_env(eh_file):
    is_yaml = re.match(y_f, eh_file)
    if is_yaml:
        with open(eh_file, 'r') as fd:
            eh = yaml.load(fd, Loader=yaml.Loader)

        eh_path = os.path.split(eh_file)

        if isinstance(eh, dict):
            eh_dict = flatdict.FlatDict(eh, delimiter=' - ')
            for key, value in eh_dict.items():
                is_heat = re.match(h_f, key)
                if is_heat:
                    heat_files_helper(eh_dict, eh_path)
                    break
            else:
                env_files_helper(eh_dict, eh_path)
        else:
            for d in eh:
                eh_dict = flatdict.FlatDict(d, delimiter=' - ')
                env_files_helper(eh_dict, eh_path)   

def recursive_list(r_list, index):
    if len(r_list) <= index:
        return    
    heat_or_env(r_list[index])
    recursive_list(list_of_files[1:], index + 1)
    
def recursive_dict(r_dict, index):
    if len(r_dict) <= index:
        return
    heat_or_env(r_dict[index][1])
    recursive_dict(list(list_of_files[0].items()), index + 1)
                
def main(roles_data, overcloud, overcloud_resource_registry_puppet, plan_environment): 
    for_plan_env(plan_environment)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
