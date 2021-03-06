from setuptools import setup, find_packages
import os

long_desc = ""

with open(os.path.join(os.path.dirname(__file__), "README.md")) as f:
    long_desc = f.read()

setup(
    name='smt-env',
    version=1.2,
    description='A package for allowing an arbitrary PyGame (inherting from BaseGame) as an OpenAI Gym Environment.',
    url='https://github.com/0xSMT/smt-env',
    author='0xSMT',
    author_email='0xSMT97@gmail.com',
    packages=find_packages(),
    keywords = ['AI', 'OpenAI', 'PyGame', 'RL'],
    long_description = long_desc,
    install_requires=["numpy", "gym", "pygame"]
)