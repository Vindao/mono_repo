# Importing modules used in the script 
from os import getcwd
from os.path import basename, join, exists, dirname, isfile
from json import load, dump
from subprocess import run

from click import command, option, group, argument
from git import Repo as GitRepo
from github import Github
from dotenv import dotenv_values


from CLI import get_input
from Tools import find


# Importing classes from other files and packages 
from .config import REPO_CONFIG_FILENAME, PACK_CONFIG_FILENAME
from .Environments import Python, Node




class GitHub:

    def __init__(self, user: str = None, password: str = None, access_token:str = None):
        env = dotenv_values()
        if 'GITHUB_ACCESS_TOKEN' in env:
            access_token = env['GITHUB_ACCESS_TOKEN']
        if 'GITHUB_USER' in env and 'GITHUB_PASSWORD' in env:
            user = env['GITHUB_USER']
            password = env['GITHUB_PASSWORD']

        if access_token:
            self.gh = Github(access_token)
        elif user and password:
            self.gh = Github(user, password)
        else:
            creds = self.get_github_credentials()
            self.gh = Github(*creds)
    
    # A method for creating new repositories with a given name.
    def create_new_repository(self, repo_name: str, organisation: str = None):
        if organisation:
            user = self.gh.get_organization(organisation)
        else:
            user = self.gh.get_user()
        repo_names = [r.full_name for r in user.get_repos()]
     
        if repo_name in repo_names:
            raise Exception(f'Repo with name {repo_name} already exists')

        try:                
            g_repo = user.create_repo(name=repo_name)
            print(f"Created new GitHub repository: {g_repo.name}")
            return g_repo.ssh_url
        except Exception as e:
            print("Error occured while creating repository", str(e))

    @staticmethod
    def get_github_credentials():
        """
        Prompts the user for either a Github access token or their Github username and password.
        If an access token is provided, it will be used to authenticate with the Github API.
        If not, the username and password will be used to retrieve an access token and authenticate.
        """

        options = ['username/password', 'access_token']
        selection = get_input("How would you like to authenticate with Github?", items=options)

        if selection == 'access_token':
            access_token = get_input("Please enter your Github access token")
            return [access_token]
        else:
            username = get_input("Please enter your Github username:")
            password = get_input("Please enter your Github password:")
            return [username, password]
    


#Creating a class called Repo which is inherting from Mono class 
class Repo:
    packages: dict = {}
    repo_json: dict = {}
    repo_base: str = ''
    Environments: dict = {
        'Node': Node,
        'Python': Python
    }
    repo = None
   
    def __init__(self):
        self._load_repo_data()
        self.__load_environments()
        self.github = GitHub()
        if exists(join(self.repo_base, '.git')):
            self.repo = GitRepo(self.repo_base)

    # Defining a function called init with parameters name, description, authors, repository_url, license. 
    def init(self, name: str = None, description: str = '',authors: str = '', repository_url: str = None, license: str='MIT'):
        # Assigning directory base name to name field if it is not given.
        if not name:
            name = basename(self.repo_base)
        authors = authors.split(',')

        # Creating dictionary object to hold values for enabling them to be updated later.
        data = {'name': name,'description': description,
                'repository_url': repository_url, 'authors': authors,'license': license}

        # Updating the details for author, description, licence of repo in a JSON file
        self._update_repo_json(data, True)

        if not exists(join(self.repo_base, '.git')):
            self.repo = GitRepo.init(self.repo_base)
            print(f"Initialized empty Git repository in {self.repo_base}/.git/")
            
        else:
            self.repo = GitRepo(self.repo_base)
        
        if len(self.repo.remotes) == 0:
            answer = get_input(f"Do you want to create a GitHub remote repository?", accepted_answers=['y', 'n'])
            if answer == 'y':
                url = self.github.create_new_repository(self.repo_json['name'], self.repo_json['organization'] if 'organization' in self.repo_json else None)
                if url:
                    self.repo.create_remote('origin', url)

    # Defining a function called detect with path as its parameter  
    def detect(self, path: str = ''):
        if path == '':
            path = self.repo_base
        if path == '.':
            path = getcwd()

        # Retrieving all the unregistered packages (not included in repo yet) present in the given directory using find_packages method.
        packages = self._find_packages(path)

        # If there are any unregistered packages then user is asked whether they should be registered or not using get_input function.
        if len(packages['unregistered']) > 0:
            answer = get_input(f"We have detected {len(packages['unregistered'])} unregistered packages within your Repo. Do you want to initialize them?", accepted_answers=['y', 'n'])
            if answer == 'y':
                self.__register_packages(packages['unregistered'])
        print(packages)

    
    
    def add_submodule(self, Environment):
        relative_path = Environment.path.replace(self.repo_base + '/', '')
        t = f"git submodule add ./{relative_path} {relative_path}"
        print(t)
        run(t, cwd=self.repo_base, shell=True)

    # This method registers all the packages into main repo.
    def __register_packages(self, packs: list):
        for path in packs:
            print(path)
            self.__register_package(path)

    def __register_package(self, path: str):
        answer = get_input(f"Register Package at '{path}'", accepted_answers=['y', 'n'])

        # Only continue to register package if user's input is yes i.e  y
        if answer != 'y':
            return

        # Finding all available environments that can be used for this package.
        detected_envs = []

        for name, env in self.Environments.items():
            if env.detect(path):
                detected_envs.append(name)

        # Showing available environments for package registration.
        items = [f'{e} (detected)' if e in detected_envs else e for e in list(self.Environments.keys())]
        answer = get_input(f"What Environment do you want to use for the package?", items=items)
        answer = answer.replace(' (detected)', '')
        
        # Selecting an environment.
        environment = self.Environments[answer](self, path)

        # Setting up the selected environment.
        environment.setup()

    # A method for creating new repositories with a given name.
    def create(self, name):
        print(name)

    # A method to install packages into the mono-repo by specifying package name.
    def install(self, path: str, name: str):
        print(name, path)
    
    def _load_repo_data(self, path: str = getcwd()):
        repo_file = find(REPO_CONFIG_FILENAME, path, walk_down=False, walk_up=True, rules=[isfile])
        if not repo_file:
            raise Exception('No Parent repo found')
        with open(repo_file, 'r') as f:
            self.repo_json = load(f)
        self.repo_base = dirname(repo_file)
    
    def _add_environments(self, path:str = getcwd()):
        print('path')

    def __load_environments(self):
        if 'environments' in self.repo_json:
            # load custom environments
            for environ_path in self.repo_json['environments']:
                self._add_environments(environ_path)
        

    def _update_repo_json(self, data: dict, overwrite: bool = False):
        file_path = join(self.repo_base, REPO_CONFIG_FILENAME)
        with open(file_path, 'w+') as file:
            try:
                if not overwrite:
                    data = { **load(file), **data}
            except:
                pass
            dump(data, file, indent=4)
    
    def _find_packages(self, path: str = getcwd()):
        if not self.repo_base in path:
            print('You are outside of your monorepo')
        return {
            'registered': self._find_registered_packages(path),
            'unregistered': self._find_unregistered_packages(path)
        }
        

    def _find_registered_packages(self, path: str = getcwd()):
        packs = [dirname(p) for p in find(PACK_CONFIG_FILENAME, path, walk_down=True, rules=[isfile], multi=True, exclude=['node_modules', '.venv'])]
        return packs


    def _find_unregistered_packages(self, path: str = getcwd()):
        found = set()
        for env in self.Environments.values():
            environ = env(path)
            found.update(environ.find(path))
        return list(found)        

    @staticmethod
    def is_unregistered_package(path: str = getcwd()):
        return not isfile(join(path, PACK_CONFIG_FILENAME)) and not isfile(join(dirname(path), PACK_CONFIG_FILENAME))


mr = Repo()

# Creating Group in cli to add the commands below to via decorators.
@group()
def repo():
    pass


@command()
@option('--name', help='Name of your new Mono Repo', prompt="name", default=basename(getcwd()))
@option('--description', help='Description of your Mono repo', prompt="description", default="")
@option('--authors', help='Authors', prompt='authors', default="")
@option('--repository_url', help='Remote url of your repository', default="<create>", prompt="repository_url")
@option('--license', help='Remote url of your repository', default='MIT', prompt="license")

def init(name, description, authors, repository_url, license):
    # Calling the init function in Repo class with prompted parameters.
    mr.init(name, description, authors, repository_url, license)


@command()
@argument('path', default='')

def detect(path):
    # Calling detect() method with given argument.
    mr.detect(path)

# Adding commands to repo group
repo.add_command(init)
repo.add_command(detect)