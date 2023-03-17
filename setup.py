from setuptools import setup, find_packages

# from pack import get_readme, get_requirements

# print(get_requirements())

setup(
    name="Mono_Repo",
    version="0.0.1",
    description='Python Distribution Utilities',
    # long_description=get_readme(),
    long_description_context_type='text/markdown',
    author='Vincent Schmitt',
    author_email='vindao@outlook.com',
    url=None,
    download_url='',
    keywords=[],
    packages=find_packages(),
    install_requires=[
        'click', 'cookiecutter', 'Tools@file://localhost/home/vindao/Documents/Code/Repo/Python/Tools#egg=Tools', 'CLI@file://localhost/home/vindao/Documents/Code/Repo/Python/CLI#egg=CLI'
    ],
    entry_points={
        'console_scripts': ['repo=Mono_Repo.main:repo', 'pack=Mono_Repo.Pack:pack'],
    }
)
