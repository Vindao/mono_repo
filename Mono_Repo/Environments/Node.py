from os import listdir

from .main import Environment

class Node(Environment):

    @staticmethod
    def detect(path: str):
        return 'package.json' in listdir(path)

    def install(self, pack: str):
        print(pack)

    def remove(self, pack: str):
        print(pack)