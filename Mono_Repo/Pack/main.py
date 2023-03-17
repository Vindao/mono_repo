from os import getcwd
from os.path import dirname, isfile, join
from json import load

from Tools import find

from ..config import PACK_CONFIG_FILENAME


class Pack:

    def __init__(self, path: str = getcwd()):
        self.cwd = path
        self.base_path = self.__find_base_path()

    
    def __find_base_path(self):
        base = find('pack.json', walk_up=True)
        print(base)
        if (base):
            return dirname(base)
        return None
    

class Pack_Handler:

    def __init__(self, path: str):
        self.path = path

    def detect(self):
        if self.is_registered(self.path):
            return self.load_pack(self.path)

    @staticmethod
    def is_registered(path: str = getcwd()):
        return isfile(join(path, PACK_CONFIG_FILENAME))

    @staticmethod
    def load_pack(path: str = getcwd()):
        with open(join(path, PACK_CONFIG_FILENAME), 'r') as file:
            data = load(file)
            self.__get_pack(data['env'])

    def detect_Python(self, path: str):
        pass

