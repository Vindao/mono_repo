from os import getcwd
from os.path import isfile, join

def get_package_config(path: str = getcwd()):
    if isfile(join(path, 'mono.config.py')):
        return 


def set_package_config(*args, **kwargs):
    print(args)
    print(kwargs)
