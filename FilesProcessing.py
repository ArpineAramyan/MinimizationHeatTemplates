import yaml
import flatdict
import sys
import re
import os.path
import pathlib
from normalized_path import normalized_path
from copy_file import copy_file

key_word_env = 'resource_registry.*'
key_words_heat = '(.*get_file$|resources.*type$)'
heat_file_header = '^heat_template_version'
yaml_file_extension = '.*yaml$'


def used_services(roles_data_path):
    services = []
    with open(roles_data_path, 'r') as rd:
        roles_data_file = yaml.load(rd, Loader=yaml.Loader)
    for i in roles_data_file:
        for key, value in i.items():
            if 'ServicesDefault' in key:
                services = services + value
    return services


def plan_env_processing(plan_environment_path, resources, services_and_files, hot_home):
    full_path = os.path.join(hot_home, plan_environment_path)
    with open(full_path, 'r') as fd:
        plan_env_data = yaml.load(fd, Loader=yaml.Loader)
    plan_env_path = os.path.split(plan_environment_path)
    plan_env_dict = flatdict.FlatDict(plan_env_data, delimiter=' - ')
    for key, value in plan_env_dict.items():
        if key == 'environments':
            for i in value:
                if i.get('path'):
                    normalized = normalized_path(plan_env_path[0], i.get('path'))
                    abs_value = os.path.join(hot_home, normalized)
                    if os.path.isfile(abs_value) and normalized not in resources \
                            and normalized not in services_and_files.values():
                        resources.append(normalized)
    return


def environment_file_processing(environment_file, all_services, resources, services_and_files, hot_home):
    type_checking = True
    is_yaml = re.match(yaml_file_extension, environment_file)
    if is_yaml:
        full_path = os.path.join(hot_home, environment_file)
        with open(full_path, 'r') as fd:
            environment_file_data = yaml.load(fd, Loader=yaml.Loader)
        environment_file_path = os.path.split(environment_file)
        if isinstance(environment_file_data, dict):
            environment_file_dict = flatdict.FlatDict(environment_file_data, delimiter=' - ')
            for key, value in environment_file_dict.items():
                is_heat = re.match(heat_file_header, key)
                if is_heat:
                    type_checking = False
                    break
            if type_checking:
                for key, value in environment_file_dict.items():
                    re_match = re.match(key_word_env, key)
                    if re_match and isinstance(value, str):
                        if value == 'None':
                            services_and_files.pop(key.split()[-1], 1)
                        else:
                            normalized = normalized_path(environment_file_path[0], value)
                            abs_value = os.path.join(hot_home, normalized)
                            if os.path.isfile(abs_value) and normalized not in resources \
                                    and normalized not in services_and_files.values() \
                                    and key.split()[-1] in all_services:
                                services_and_files.update({key.split()[-1]: normalized})
    return


def heat_file_processing(heat_file, resources, services_and_files, hot_home):
    type_checking = False
    is_yaml = re.match(yaml_file_extension, heat_file)
    if is_yaml:
        full_path = os.path.join(hot_home, heat_file)
        with open(full_path, 'r') as fd:
            heat_file_data = yaml.load(fd, Loader=yaml.Loader)
        heat_file_path = os.path.split(heat_file)
        heat_file_dict = flatdict.FlatDict(heat_file_data, delimiter=' - ')
        for key, value in heat_file_dict.items():
            is_heat = re.match(heat_file_header, key)
            if is_heat:
                type_checking = True
                break
        if type_checking:
            for key, value in heat_file_dict.items():
                re_match = re.match(key_words_heat, key)
                if re_match and isinstance(value, str):
                    normalized = normalized_path(heat_file_path[0], value)
                    abs_value = os.path.join(hot_home, normalized)
                    if os.path.isfile(abs_value) and normalized not in resources \
                            and normalized not in services_and_files.values():
                        resources.append(normalized)
    return

                        
def environment_files_traversal(index, all_services, resources, services_and_files, hot_home):
    if len(resources) <= index:
        return
    environment_file_processing(resources[index], all_services, resources, services_and_files, hot_home)
    environment_files_traversal(index + 1, all_services, resources, services_and_files, hot_home)


def heat_files_traversal(index, resources, services_and_files, hot_home):
    if len(services_and_files.items()) <= index:
        return
    heat_file_processing(list(services_and_files.items())[index][1], resources, services_and_files, hot_home)
    heat_files_traversal(index + 1, resources, services_and_files, hot_home)

           
def main(roles_data_path, overcloud_path, overcloud_resource_registry_puppet_path, plan_environment_path, hot_home,
         copy_hot_home):
    resources = [roles_data_path, overcloud_path, overcloud_resource_registry_puppet_path, plan_environment_path]
    services_and_files = {}

    all_services = used_services(hot_home + '/' + roles_data_path)
    plan_env_processing(plan_environment_path, resources, services_and_files, hot_home)

    environment_files_traversal(0, all_services, resources, services_and_files, hot_home)
    heat_files_traversal(0, resources, services_and_files, hot_home)

    for i in resources:
        path = os.path.split(i)[0]
        file = os.path.split(i)[1]
        path_parts = pathlib.PosixPath(path)
        path_parts = list(path_parts.parts)
        copy_file(path, file, hot_home, copy_hot_home, path_parts, hot_home, copy_hot_home)

    for value in services_and_files.values():
        path = os.path.split(value)[0]
        file = os.path.split(value)[1]
        path_parts = pathlib.PosixPath(path)
        path_parts = list(path_parts.parts)
        copy_file(path, file, hot_home, copy_hot_home, path_parts, hot_home, copy_hot_home)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    
