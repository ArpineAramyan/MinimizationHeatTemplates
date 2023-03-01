import argparse
import os


# # Create a shell script file
# with open('Minimize', 'w') as f:
#     f.write('#!/bin/bash\n')
#     f.write('python3 {} "$@"'.format(os.path.abspath('main.py')))
#
# # Make the file executable
# os.chmod('Minimize', 0o755)


def get_parser():
    parser = argparse.ArgumentParser(prog='Minimization')
    parser.add_argument('-th', '--templates_home',
                        metavar='<directory>',
                        type=str,
                        default='./',
                        help='Path to templates home directory')
    parser.add_argument('-m', '--minimized',
                        metavar='<directory>',
                        type=str,
                        default='../minimized-heat-templates',
                        help='Path to directory with minimized templates')
    parser.add_argument('-rd', '--roles_data',
                        metavar='<filename>',
                        type=str,
                        default='roles_data.yaml',
                        help='Path from templates home to roles_data file')
    parser.add_argument('-pe', '--plan_env',
                        metavar='<filename>',
                        type=str,
                        default='plan-environment.yaml',
                        help='Path from templates home to plan-environment file')
    return parser
