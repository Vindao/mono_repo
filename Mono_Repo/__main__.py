#!/usr/bin/env python

from sys import argv
from os import getcwd
from os.path import basename
from .Repo import Repo

from click import command, option, group, argument


args = argv[1:]

mr = Repo()

@group()
def repo():
    pass

@command()
@option('--name', help='Name of your new Mono Repo', prompt="name", default=basename(getcwd()))
@option('--description', help='Description of your Mono repo', prompt="description", default="")
@option('--authors', help='Authors', prompt='authors', default="")
@option('--path', help="Your new Repo's path", default=getcwd())
@option('--repository_url', help='Remote url of your repository', default="<create>", prompt="repository_url")
@option('--license', help='Remote url of your repository', default='MIT', prompt="license")

def init(name, description, authors, path, repository_url, license):
    mr.init(name, description, authors, path, repository_url, license)
    

@command()
@option('--name', help='Name of your new package', prompt='Name of your new package')
def create(name):
    mr.create(name)

repo.add_command(init)
repo.add_command(create)

@group()
def pack():
    pass

@command()
@option('--path', help='Package path', default=getcwd())
@argument('name')
def install(path, name):

    mr.install(path, name)


pack.add_command(install)

if __name__ == '__main__':
   repo()