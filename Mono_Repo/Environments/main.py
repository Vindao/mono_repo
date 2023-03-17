
from os import getcwd, listdir
from os.path import dirname, isdir, join, exists, basename
from json import load, dump

from git import Repo

from Tools import find

from ..config import PACK_CONFIG_FILENAME

class Environment:

    cwd: str = None
    path: str = None
    repo: Repo = None
    json: dict = {}

    def __init__(self, master, path: str = getcwd()):
        self.master = master
        self.cwd = path
        self.path = self.__find_base_path(path)
        if self.path and exists(self.get_json_path()):
            self.json = self._load_json()
        if self.path and exists(join(self.path, '.git')): # New lines added
            self.repo = Repo(self.path)
            

    @staticmethod
    def detect(path: str):
        return False
    
    def find(self, path: str = getcwd()):
        if self.detect(path):
            # current path is a valid environment, don't look further
            return [path]
        found = []
        dirs = [join(path, p) for p in listdir(path) if isdir(join(path, p)) and not p.startswith('.') and not p in ['node_modules']]
        for d in dirs:
            found += self.find(d)
        return found
    
    def __find_base_path(self, path: str):
        if dirname(path) == path:
            return None
        return path if self.detect(path) else self.__find_base_path(dirname(path))
    
    def _update_json(self, data: dict, overwrite: bool = False):
        
        with open(self.get_json_path(), 'w+') as file:
            old_data = {}
            if not overwrite:
                try:
                    old_data = load(file)
                except:
                    pass
            dump({**old_data, **data}, file)

    def _load_json(self):
        
        with open(self.get_json_path(), 'r') as file:
            return load(file)
        
    def get_json_path(self):
        if not self.path:
            return None
        return join(self.path, PACK_CONFIG_FILENAME)

    def install(self, package):
        print(f"INSTALL not implemented by '{self.__class__.__name__}' Environment")

    
    def remove(self, package):
        print(f"REMOVE not implemented by '{self.__class__.__name__}' Environment")


    def setup(self):
        if not exists(join(self.path, '.git')):
            self.repo = Repo.init(self.path)
            print(f"Initialized empty Git repository in {self.path}/.git/")
        
        
        try:
            self._setup()
        except Exception as e:
            print(f"SETUP not implemented by '{self.__class__.__name__}' Environment")

        self.__check_remotes()
        # Add submodule to parent MonoRepo git repository only if there is a parent (i.e. repo_base is not None).
        print(self.repo.remotes)
        relative_path = self.path.replace(self.master.repo_base + '/', '')
        # branch_name = self.repo.head.ref.name

        # Add, commit and push all changes before adding submodule
        self.repo.index.add('*')
        commit_message = f"Adding package {relative_path} to parent MonoRepo"
        self.repo.index.commit(commit_message)
        origin = self.repo.remote()
        origin.push(self.repo.head, set_upstream=True)

        try:
            self.master.add_submodule(self)
            # self.master.repo.create_submodule(name=relative_path, path=self.path, url=self.repo.remotes[0].url, branch=branch_name)
            print(f"{relative_path} added as Git submodule to the parent MonoRepo git repository.")
            
        except Exception as e:
            # If there is any error, such as missing or invalid remote URL then inform the user.
            print(f"Could not add {relative_path} as Git submodule to the parent MonoRepo git repository due to the following error: {str(e)}")
                
    
    def __check_remotes(self):
        print(self.repo.remotes)
        if len(self.repo.remotes) == 0:
            name = self.json['name'] if 'name' in self.json else basename(self.path)
            print(name)
            url = self.master.github.create_new_repository(name, self.master.repo_json['organization'] if 'organization' in self.master.repo_json else None)
            if url:
                self.repo.create_remote('origin', url)

    def _setup_remote(self):
        pass

        