from setuptools import setup, find_packages
from makeitpop import __version__

setup(
    name='makeitpop',
    version=__version__,
    author='Chris Holdgraf',
    author_email='choldgraf@gmail.com',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
)
