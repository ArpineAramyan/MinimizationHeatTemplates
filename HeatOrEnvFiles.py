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

def default_services(roles_data):
    services = []
    with open(roles_data, 'r') as rd:
        roles_data_file = yaml.load(rd, Loader=yaml.Loader)
    for i in roles_data_file:
        for key, value in i.items():
            if 'ServicesDefault' in key:
                services = services + value
    return services

def for_plan_env(eh_file, list_of_files, dict_of_services_and_files):
    with open(eh_file, 'r') as fd:
        eh = yaml.load(fd, Loader=yaml.Loader)

    eh_path = os.path.split(eh_file)
    eh_dict = flatdict.FlatDict(eh, delimiter=' - ')
    for key, value in eh_dict.items():
        if key == 'environments':
            for i in value:
                if i.get('path'):
                    abs_value = norm_path(eh_path[0], i.get('path'))
                    if os.path.isfile(abs_value) and abs_value not in list_of_files and abs_value not in dict_of_services_and_files.values():
                        list_of_files.append(abs_value)

def env_files_helper(eh_file,  all_services, list_of_files, dict_of_services_and_files):
    a = 0
    is_yaml = re.match(y_f, eh_file)
    if is_yaml:
        with open(eh_file, 'r') as fd:
            eh = yaml.load(fd, Loader=yaml.Loader)

        env_path = os.path.split(eh_file)
        if isinstance(eh, dict):
            dict_env = flatdict.FlatDict(eh, delimiter=' - ')
            for key, value in dict_env.items():
                is_heat = re.match(h_f, key)
                if is_heat:
                    a = 1
                    break
            if a == 0:
                for key, value in dict_env.items():
                    re_match = re.match(key_env, key)
                    if re_match and isinstance(value, str):
                        if value == 'None':
                            dict_of_services_and_files.pop(key.split()[-1], 1)
                        else:
                            abs_value = norm_path(env_path[0], value)
                            if os.path.isfile(abs_value) and abs_value not in list_of_files and abs_value not in dict_of_services_and_files.values() and key.split()[-1] in all_services:
                                dict_of_services_and_files.update({key.split()[-1]: abs_value})

def heat_files_helper(eh_file, list_of_files, dict_of_services_and_files):
    a = 0
    is_yaml = re.match(y_f, eh_file)
    if is_yaml:
        with open(eh_file, 'r') as fd:
            eh = yaml.load(fd, Loader=yaml.Loader)
        heat_path = os.path.split(eh_file)
        
        if isinstance(eh, dict):
            dict_heat = flatdict.FlatDict(eh, delimiter=' - ')
            for key, value in dict_heat.items():
                is_heat = re.match(h_f, key)
                if is_heat:
                    a = 1
            if a == 1:
                for key, value in dict_heat.items():
                    re_match = re.match(key_words, key)
                    if re_match and isinstance(value, str):
                        abs_value = norm_path(heat_path[0], value)
                        if os.path.isfile(abs_value) and abs_value not in list_of_files and abs_value not in dict_of_services_and_files.values():
                            list_of_files.append(abs_value)

def recursive_list(r_list, index, all_services, list_of_files, dict_of_services_and_files):
    if len(r_list) <= index:
        return    
    env_files_helper(r_list[index], all_services, list_of_files, dict_of_services_and_files)
    recursive_list(list_of_files, index + 1, all_services, list_of_files, dict_of_services_and_files)
    
def recursive_dict(r_dict, index, list_of_files, dict_of_services_and_files):
    if len(r_dict) <= index:
        return
    heat_files_helper(r_dict[index][1], list_of_files, dict_of_services_and_files)
    recursive_dict(list(dict_of_services_and_files.items()), index + 1, list_of_files, dict_of_services_and_files)
                
def main(roles_data, overcloud, overcloud_resource_registry_puppet, plan_environment): 
    list_of_files = []
    dict_of_services_and_files = {}
    
    list_of_files.append(roles_data)
    list_of_files.append(overcloud)
    list_of_files.append(overcloud_resource_registry_puppet)
    list_of_files.append(plan_environment)

    all_services = default_services(roles_data)
    for_plan_env(plan_environment, list_of_files, dict_of_services_and_files)
    recursive_list(list_of_files, 0, all_services, list_of_files, dict_of_services_and_files)
    recursive_dict(list(dict_of_services_and_files.items()), 0, list_of_files, dict_of_services_and_files)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
