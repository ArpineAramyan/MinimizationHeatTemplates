import yaml
import flatdict
import re
import os.path

key_env =  'resource_registry.*'
key_words = '(.*get_file$|resources.*type$)'
h_f = '^heat_template_version'
y_f = '.*yaml$'

list_of_files = [{}]

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

def env_files_helper(dict_env, env_path):
    for key, value in dict_env.items():
        if key == 'environments':
            for i in value:
                if i.get('path'):
                    absvalue = norm_path(env_path[0], i.get('path'))
                    if os.path.isfile(absvalue):
                        list_of_files.append(absvalue)
        else:
            re_match = re.match(key_env, key)
            if re_match and isinstance(value, str):
                if value == 'None':
                    list_of_files[0].pop(key, 1)
                else:    
                    absvalue = norm_path(env_path[0], value)
                    if os.path.isfile(absvalue):
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
                
root_files = ['/home/amp/ankap/or_not/asperitas-heat-templates-1666703206.8775902/roles_data.yaml', '/home/amp/ankap/or_not/asperitas-heat-templates-1666703206.8775902/overcloud.yaml', '/home/amp/ankap/or_not/asperitas-heat-templates-1666703206.8775902/overcloud-resource-registry-puppet.yaml', '/home/amp/ankap/or_not/asperitas-heat-templates-1666703206.8775902/plan-environment.yaml']

for i in root_files:
    heat_or_env(i)

recursive_list(list_of_files[1:], 0)
recursive_dict(list(list_of_files[0].items()), 0) 
