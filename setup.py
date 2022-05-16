import os
from setuptools import setup, find_packages


def requirements(path='requirements.txt'):
    with open(path, 'r') as f:
        deps = [line.strip() for line in f]
    return deps


def version(path=os.path.join('metas', '__init__.py')):
    with open(path, 'r') as f:
        for row in f:
            if not row.startswith('__version__'):
                continue
            return row.split(' = ')[-1].strip('\n').strip("'")


setup(
    name='metas',
    version=version(),
    description='Miscellaneous decorators, metclasses, and mixins to make '
        'programming in python a more convient and productive experience.',
    packages=find_packages(include=['metas']),
    zip_safe=False,
    install_requires=requirements(),
    # If installing speedup causes gcc error in docker image, try
    # adding `apt install build-essentials`.
    extras_require={'fuzzy': ['fuzzywuzzy'],
                    'speedup': ['fuzzywuzzy[speedup]']},
    entry_points={'console_scripts': ['metas=metas.cli:cli']}
)

