import yaml
import flatdict
import sys
import re
import os.path
from normalized_path import norm_path

key_word_env = 'resource_registry.*'
key_words_heat = '(.*get_file$|resources.*type$)'
is_heat_file = '^heat_template_version'
is_yaml_file = '.*yaml$'


def used_services(roles_data):
    services = []
    with open(roles_data, 'r') as rd:
        roles_data_file = yaml.load(rd, Loader=yaml.Loader)
    for i in roles_data_file:
        for key, value in i.items():
            if 'ServicesDefault' in key:
                services = services + value
    return services


def plan_env_processing(plan_env, resources, services_and_files, hot_home):
    full_path = hot_home + '/' + plan_env
    with open(full_path, 'r') as fd:
        plan_env_data = yaml.load(fd, Loader=yaml.Loader)
    plan_env_path = os.path.split(plan_env)
    plan_env_dict = flatdict.FlatDict(plan_env_data, delimiter=' - ')
    for key, value in plan_env_dict.items():
        if key == 'environments':
            for i in value:
                if i.get('path'):
                    normalized = norm_path(plan_env_path[0], i.get('path'))
                    abs_value = hot_home + '/' + normalized
                    if os.path.isfile(abs_value) and normalized not in resources \
                            and normalized not in services_and_files.values():
                        resources.append(normalized)


def environment_file_processing(environment_file, all_services, resources, services_and_files, hot_home):
    type_checking = True
    is_yaml = re.match(is_yaml_file, environment_file)
    if is_yaml:
        full_path = hot_home + '/' + environment_file
        with open(full_path, 'r') as fd:
            environment_file_data = yaml.load(fd, Loader=yaml.Loader)
        environment_file_path = os.path.split(environment_file)
        if isinstance(environment_file_data, dict):
            environment_file_dict = flatdict.FlatDict(environment_file_data, delimiter=' - ')
            for key, value in environment_file_dict.items():
                is_heat = re.match(is_heat_file, key)
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
                            normalized = norm_path(environment_file_path[0], value)
                            abs_value = hot_home + '/' + normalized
                            if os.path.isfile(abs_value) and normalized not in resources \
                                    and normalized not in services_and_files.values() \
                                    and key.split()[-1] in all_services:
                                services_and_files.update({key.split()[-1]: normalized})


def heat_file_processing(heat_file, resources, services_and_files, hot_home):
    type_checking = False
    is_yaml = re.match(is_yaml_file, heat_file)
    if is_yaml:
        full_path = hot_home + '/' + heat_file
        with open(full_path, 'r') as fd:
            heat_file_data = yaml.load(fd, Loader=yaml.Loader)
        heat_file_path = os.path.split(heat_file)
        heat_file_dict = flatdict.FlatDict(heat_file_data, delimiter=' - ')
        for key, value in heat_file_dict.items():
            is_heat = re.match(is_heat_file, key)
            if is_heat:
                type_checking = True
                break
        if type_checking:
            for key, value in heat_file_dict.items():
                re_match = re.match(key_words_heat, key)
                if re_match and isinstance(value, str):
                    normalized = norm_path(heat_file_path[0], value)
                    abs_value = hot_home + '/' + normalized
                    if os.path.isfile(abs_value) and normalized not in resources \
                            and normalized not in services_and_files.values():
                        resources.append(normalized)

                        
def traversal_environment_files(index, all_services, resources, services_and_files, hot_home):
    if len(resources) <= index:
        return
    environment_file_processing(resources[index], all_services, resources, services_and_files, hot_home)
    traversal_environment_files(index + 1, all_services, resources, services_and_files, hot_home)


def traversal_heat_files(index, resources, services_and_files, hot_home):
    if len(services_and_files.items()) <= index:
        return
    heat_file_processing(list(services_and_files.items())[index][1], resources, services_and_files, hot_home)
    traversal_heat_files(index + 1, resources, services_and_files, hot_home)

           
def main(roles_data, overcloud, overcloud_resource_registry_puppet, plan_environment, hot_home): 
    resources = [roles_data, overcloud, overcloud_resource_registry_puppet, plan_environment]
    services_and_files = {}

    all_services = default_services(hot_home + '/' + roles_data)
    plan_env_processing(plan_environment, resources, services_and_files, hot_home)

    traversal_environment_files(0, all_services, resources, services_and_files, hot_home)
    traversal_heat_files(0, resources, services_and_files, hot_home)
    
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
