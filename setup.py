from io import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
    
setup(
    name='dw-tap',
    version='0.0.1',
    description='dw-tap package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/NREL/dw-tap',
    author='Dmitry Duplyakin, Sagi Zisman, Jenna Ruzekowicz, Caleb Phillips, and the rest of the TAP team',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha Copy',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: BSD 3-Clause',

        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(),  
    install_requires=[],  
    project_urls={
        'Source': 'https://github.com/NREL/dw-tap',
    },
    package_data = {
        '': ['anl-lom-models/*', 'anl-lom-models/checkpoints/*'],
    },
)
