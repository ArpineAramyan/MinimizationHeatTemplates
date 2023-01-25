import yaml
import flatdict
import sys
import re
import os.path
import pathlib
from normalized_rel_path import normalized_rel_path
from copy_file import copy_file


key_word_env = 'resource_registry.*'
key_words_heat = '(.*get_file$|resources.*type$)'
heat_file_header = '^heat_template_version'
yaml_file_extension = '.*yaml$'


# saving services that used in roles_data.yaml
def used_services(roles_data_path):
    services = []
    with open(roles_data_path, 'r') as rd:
        roles_data_file = yaml.load(rd, Loader=yaml.Loader)
    for i in roles_data_file:
        for key, value in i.items():
            if 'ServicesDefault' in key:
                services = services + value
    return services

# saving files that are used in plan_environment.yaml
def plan_env_processing(plan_env_path, resources, services_and_files, hot_home):
    full_path = os.path.join(hot_home, plan_env_path)
    with open(full_path, 'r') as fd:
        plan_env_data = yaml.load(fd, Loader=yaml.Loader)
    plan_env_path = os.path.split(plan_env_path)
    plan_env_dict = flatdict.FlatDict(plan_env_data, delimiter=' - ')
    for key, value in plan_env_dict.items():
        if key == 'environments':
            for file_path in value:
                if file_path.get('path'):
                    normalized = normalized_rel_path(plan_env_path[0], file_path.get('path'))
                    abs_value = os.path.join(hot_home, normalized)
                    if os.path.isfile(abs_value) and normalized not in resources \
                            and normalized not in services_and_files.values():
                        resources.append(normalized)
    return

# saving files that are used in environment files
def env_file_processing(env_file, all_services, resources, services_and_files, hot_home):
    type_checking = True
    yaml_match = re.match(yaml_file_extension, env_file)
    if yaml_match:
        full_path = os.path.join(hot_home, env_file)
        with open(full_path, 'r') as fd:
            env_file_data = yaml.load(fd, Loader=yaml.Loader)
        env_file_path = os.path.split(env_file)
        if isinstance(env_file_data, dict):
            env_file_dict = flatdict.FlatDict(env_file_data, delimiter=' - ')
            for key, value in env_file_dict.items():
                is_heat = re.match(heat_file_header, key)
                if is_heat:
                    type_checking = False
                    break
            if type_checking:
                for key, value in env_file_dict.items():
                    env_match = re.match(key_word_env, key)
                    if env_match and isinstance(value, str):
                        if value == 'None':
                            services_and_files.pop(key.split()[-1], 1)
                        else:
                            normalized = normalized_rel_path(env_file_path[0], value)
                            abs_value = os.path.join(hot_home, normalized)
                            if os.path.isfile(abs_value) and normalized not in resources \
                                    and normalized not in services_and_files.values() \
                                    and key.split()[-1] in all_services:
                                services_and_files.update({key.split()[-1]: normalized})
    return

# saving files that are used in heat files
def heat_file_processing(heat_file, resources, services_and_files, hot_home):
    type_checking = False
    yaml_match = re.match(yaml_file_extension, heat_file)
    if yaml_match:
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
                heat_match = re.match(key_words_heat, key)
                if heat_match and isinstance(value, str):
                    normalized = normalized_rel_path(heat_file_path[0], value)
                    abs_value = os.path.join(hot_home, normalized)
                    if os.path.isfile(abs_value) and normalized not in resources \
                            and normalized not in services_and_files.values():
                        resources.append(normalized)
    return


def env_files_traversal(index, all_services, resources, services_and_files, hot_home):
    if len(resources) <= index:
        return
    env_file_processing(resources[index], all_services, resources, services_and_files, hot_home)
    env_files_traversal(index + 1, all_services, resources, services_and_files, hot_home)


def heat_files_traversal(index, resources, services_and_files, hot_home):
    if len(services_and_files.items()) <= index:
        return
    heat_file_processing(list(services_and_files.items())[index][1], resources, services_and_files, hot_home)
    heat_files_traversal(index + 1, resources, services_and_files, hot_home)


def main(roles_data_path, overcloud_path, overcloud_resource_registry_puppet_path, plan_env_path, hot_home,
         copy_hot_home):
    resources = [roles_data_path, overcloud_path, overcloud_resource_registry_puppet_path, plan_env_path]
    services_and_files = {}

    all_services = used_services(os.path.join(hot_home, roles_data_path))
    plan_env_processing(plan_env_path, resources, services_and_files, hot_home)

    env_files_traversal(0, all_services, resources, services_and_files, hot_home)
    heat_files_traversal(0, resources, services_and_files, hot_home)

    # the next two cycles are for copying used files
    for resource in resources:
        path, file = os.path.split(resource)
        path_parts = pathlib.PosixPath(path)
        path_parts = list(path_parts.parts)
        copy_file(path, file, path_parts, hot_home, copy_hot_home)

    for file_path in services_and_files.values():
        path, file = os.path.split(file_path)
        path_parts = pathlib.PosixPath(path)
        path_parts = list(path_parts.parts)
        copy_file(path, file, path_parts, hot_home, copy_hot_home)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
