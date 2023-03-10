import yaml
import flatdict
import re
import os.path
import pathlib
from files_processing.normalized_rel_path import normalized_rel_path
from files_processing.copy_file import copy_file


key_word_resources = 'resource_registry.*'
key_word_param = 'parameter_defaults.*'
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


def overcloud_resource_registry_puppet_processing(extra_files, services_and_files, hot_home):
    overcloud_resource_registry_puppet_path = os.path.join(hot_home, extra_files[3])
    file_resources = {}
    other_resources = {}
    with open(overcloud_resource_registry_puppet_path, 'r') as fd:
        overcloud_resource_registry_puppet_data = yaml.load(fd, Loader=yaml.Loader)
    overcloud_resource_registry_puppet_dict = flatdict.FlatDict(
        overcloud_resource_registry_puppet_data, delimiter=' - ')
    for key, value in overcloud_resource_registry_puppet_dict.items():
        resources_match = re.match(key_word_resources, key)
        if resources_match and 'Services' not in key:
            if os.path.isfile(os.path.join(hot_home, value)) and value not in extra_files \
                    and value not in services_and_files.values():
                file_resources.update({key.split()[-1]: value})
            elif not os.path.isfile(os.path.join(hot_home, value)) and 'None' not in value:
                other_resources.update({key.split()[-1]: value})
    return file_resources, other_resources


# saving files that are used in plan_environment.yaml
def plan_env_processing(plan_env_path, extra_files, services_and_files, hot_home):
    full_path = os.path.join(hot_home, plan_env_path)
    with open(full_path, 'r') as fd:
        plan_env_data = yaml.load(fd, Loader=yaml.Loader)
    plan_env_path = os.path.split(plan_env_path)
    plan_env_dict = flatdict.FlatDict(plan_env_data, delimiter=' - ')
    extra_files.append(plan_env_dict['template'])
    for key, value in plan_env_dict.items():
        if key == 'environments':
            for file_path in value:
                if file_path.get('path'):
                    normalized = normalized_rel_path(plan_env_path[0], file_path.get('path'))
                    abs_value = os.path.join(hot_home, normalized)
                    if os.path.isfile(abs_value) and normalized not in extra_files \
                            and normalized not in services_and_files.values():
                        extra_files.append(normalized)
    return


# saving files that are used in environment files
def env_file_processing(env_file, all_services, extra_files, services_and_files, hot_home,
                        file_resources, other_resources, parameters_defaults):
    type_checking = True
    yaml_match = re.match(yaml_file_extension, env_file)
    if yaml_match:
        full_path = os.path.join(hot_home, env_file)
        with open(full_path, 'r') as fd:
            env_file_data = yaml.load(fd, Loader=yaml.Loader)
        env_file_path = os.path.split(env_file)
        if isinstance(env_file_data, dict):
            for key, value in env_file_data.items():
                parameters_match = re.match(key_word_param, key)
                if parameters_match:
                    for key_param, value_param in value.items():
                        if key_param not in parameters_defaults:
                            parameters_defaults.update({key_param: value_param})
                        else:
                            print("Oops! You did it again. Check this parameter :", key_param)
            env_file_dict = flatdict.FlatDict(env_file_data, delimiter=' - ')
            for key, value in env_file_dict.items():
                is_heat = re.match(heat_file_header, key)
                if is_heat:
                    type_checking = False
                    break
            if type_checking:
                for key, value in env_file_dict.items():
                    env_match = re.match(key_word_resources, key)
                    if env_match and isinstance(value, str):
                        normalized = normalized_rel_path(env_file_path[0], value)
                        abs_value = os.path.join(hot_home, normalized)
                        if 'Services' in key:
                            if 'None' in value:
                                services_and_files.pop(key.split()[-1], 1)
                            else:
                                if os.path.isfile(abs_value) and normalized not in extra_files \
                                        and normalized not in services_and_files.values() \
                                        and key.split()[-1] in all_services  \
                                        and normalized not in file_resources.values():
                                    services_and_files.update({key.split()[-1]: normalized})
                        else:
                            if 'None' in value:
                                file_resources.pop(key.split()[-1], 1)
                                other_resources.pop(key.split()[-1], 1)
                            else:
                                if os.path.isfile(abs_value) and normalized not in extra_files \
                                    and normalized not in services_and_files.values() \
                                        and normalized not in file_resources.values():
                                    file_resources.update({key.split()[-1]: normalized})
                                elif not os.path.isfile(abs_value):
                                    other_resources.update({key.split()[-1]: value})
    return


# saving files that are used in heat files
def heat_file_processing(heat_file, extra_files, services_and_files, hot_home, file_resources):
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
                    if os.path.isfile(abs_value) and normalized not in extra_files \
                            and normalized not in services_and_files.values() \
                            and normalized not in file_resources.values():
                        extra_files.append(normalized)
    return


def env_files_traversal(index, all_services, extra_files, services_and_files, hot_home,
                        file_resources, other_resources, parameters_defaults):
    if len(extra_files) <= index:
        return
    env_file_processing(extra_files[index], all_services, extra_files, services_and_files, hot_home,
                        file_resources, other_resources, parameters_defaults)
    env_files_traversal(index + 1, all_services, extra_files, services_and_files, hot_home,
                        file_resources, other_resources, parameters_defaults)


def heat_files_traversal(index, extra_files, services_and_files, hot_home, file_resources):
    if len(services_and_files.items()) <= index:
        return
    heat_file_processing(list(services_and_files.items())[index][1], extra_files, services_and_files, hot_home,
                         file_resources)
    heat_files_traversal(index + 1, extra_files, services_and_files, hot_home, file_resources)


def main(hot_home,  copy_hot_home, roles_data_path, plan_env_path):
    if not os.path.isdir(hot_home):
        hot_home = os.path.abspath(hot_home)
    if not os.path.isdir(copy_hot_home):
        copy_hot_home = os.path.abspath(copy_hot_home)
    extra_files = [roles_data_path, plan_env_path]
    parameters_defaults = {}

    services_and_files = {}
    all_services = used_services(os.path.join(hot_home, roles_data_path))

    plan_env_processing(plan_env_path, extra_files, services_and_files, hot_home)

    # in key resource type, in value file path
    file_resources, other_resources = overcloud_resource_registry_puppet_processing(extra_files, services_and_files,
                                                                                    hot_home)

    env_files_traversal(0, all_services, extra_files, services_and_files, hot_home, file_resources, other_resources,
                        parameters_defaults)
    heat_files_traversal(0, extra_files, services_and_files, hot_home, file_resources)

    # the next three cycles are for copying used files
    for resource in extra_files:
        path, file = os.path.split(resource)
        path_parts = pathlib.PosixPath(path)
        path_parts = list(path_parts.parts)
        copy_file(path, file, path_parts, hot_home, copy_hot_home)

    for file_path in services_and_files.values():
        path, file = os.path.split(file_path)
        path_parts = pathlib.PosixPath(path)
        path_parts = list(path_parts.parts)
        copy_file(path, file, path_parts, hot_home, copy_hot_home)

    for each_file in file_resources.values():
        path, file = os.path.split(each_file)
        path_parts = pathlib.PosixPath(path)
        path_parts = list(path_parts.parts)
        copy_file(path, file, path_parts, hot_home, copy_hot_home)
