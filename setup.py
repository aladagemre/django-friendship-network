# encoding: utf-8
import os
from setuptools import setup, find_packages

from friendship_network import VERSION


f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
readme = f.read()
f.close()

setup(
    name='django-friendship-network',
    version=".".join(map(str, VERSION)),
    description='django-friendship-network provides a friendship and following framework based on Neo4j',
    long_description=readme,
    author='Ahmet Emre Aladağ',
    url='https://github.com/aladagemre/django-friendship-network/',
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPL v2',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
