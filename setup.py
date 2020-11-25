# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tracedump', 'tracedump.perf', 'tracedump.tracedumpd']

package_data = \
{'': ['*'], 'tracedump': ['_pt/*']}

install_requires = \
['cffi>=1.1.0',
 'pwntools @ '
 'https://github.com/chaimleib/intervaltree/archive/51645530f281930c03936a3a1cd886e0ed481bc3.tar.gz']

entry_points = \
{'console_scripts': ['tracedumpd = tracedump.tracedumpd.__main__:main']}

setup_kwargs = {
    'name': 'tracedump',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'Mic92',
    'author_email': 'dontcontactme@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
