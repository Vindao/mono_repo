from os import listdir
from os.path import join

from .main import Environment

from ..config import PACK_CONFIG_FILENAME

class Python(Environment):

    data_map: dict = {'name': str, 'version': str, 'description': str, 'author': str, 'author_email': str, 'url': str, 'download_url': str, 'keywords': str}

    @staticmethod
    def detect(path: str) -> bool:
        return 'setup.py' in listdir(path)

    def install(self, pack: str):
        print(pack)

    def remove(self, pack: str):
        print(pack)

    def _setup(self):
        print(self.path, 'setup')
        files = listdir(self.path)
        print(files, PACK_CONFIG_FILENAME)
        if not PACK_CONFIG_FILENAME in files:
            print('HEy')
            data = self.__get_data_from_setup()
            self._update_json(data)

    def __get_data_from_setup(self):
        with open(join(self.path, 'setup.py'), 'r') as f:
            vals = [x.strip().split('=') for x in f.read().split('setup(')[1].split(',') if '=' in x]
            return {x[0]: x[1].strip("""'\"""") for x in vals if x[0] in self.data_map.keys()}