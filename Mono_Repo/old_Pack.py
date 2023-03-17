from os import getcwd, listdir
from os.path import basename, isdir, join, dirname

from json import load, dump

from click import command, option, group, argument

from .main import Mono

from Tools import toDict, find

class Pack(Mono):
    

    def __init__(self):
        self.cwd = getcwd()
        self.path = self.__find_base_path()



    def init(self, name: str = None, version: str ='0.0.1', description: str='', authors: str = None, repository_url: str = None, license: str = 'MIT',  environment: str = 'detect'):
        
        if not name:
            name = basename(self.path)
        if authors:
            authors = authors.split(',')
        if environment == 'detect':
            environment = self.__detect_environment()
        print(name, version, description, authors, repository_url, license, environment)
        data = toDict(name=name, version=version, description=description, authors=authors, repository_url=repository_url, license=license, environment=environment)
        print(data)
        self.__update_pack_json(data)


    def install(self, pack_name, prefer_local: bool = True):
        local_pack = self.find_local_pack(pack_name)

    def __detect_environment(self):
        if not isdir(self.path):
            return None
        files = listdir(self.path)
        if 'package.json' in files:
            return self.__get_js_environment(self.path)
        if 'setup.py' in files:
            return self.__get_py_environment(self.path)
        
    def __get_js_environment(self):
        with open(join(self.path, 'package.json'), 'r') as f:
            print(load(f))
        
    def __get_py_environment(self):
        
        return {
            "type": 'python', 
            "environment": "venv",
            "pack_manager": "pip3",
            "lang_version": ">=3.9"
            }

    def __update_pack_json(self, data, overwrite: bool = False):
        with open(join(self.path, 'pack.json'), 'w+') as f:
            old_data = load(f)
            if not overwrite:
                data = {**old_data, **data}
            dump(data, f)


    def __find_base_path(self):
        base = find('pack.json', walk_up=True)
        print(base)
        if (base):
            return dirname(base)
        return None


package = Pack()

@group()
def pack():
    pass

@command()
@option('--name', help='Name of your new Pack', prompt="name", default=basename(getcwd()))
@option('--version', help='The starting version of your new pack', prompt="version", default="0.0.1")
@option('--description', help='Description of your Pack', prompt="description", default="")
@option('--authors', help='Authors', prompt='authors', default="")
@option('--path', help="Your new Repo's path", default=getcwd())
@option('--repository_url', help='Remote url of your repository', default="<create>", prompt="repository_url")
@option('--environment', help='Environment for your package', default='<detect>', prompt="environment")
@option('--license', help='Remote url of your repository', default='MIT', prompt="license")

def init(name, version, description, authors, path, repository_url, license, environment):
    package.init(name, version, description, authors, path, repository_url, license, environment)

pack.add_command(init)