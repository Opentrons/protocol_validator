from setuptools import setup, find_packages

config = {
    'description': "A validator for protcol JSON files.",
    'author': "OpenTrons",
    'author_email': 'engineering@opentrons.com',
    'url': 'http://opentrons.com',
    'version': '1.0',
    'install_requires': [],
    'packages': find_packages(exclude=["tests"]),
    'package_data': {
        "protocol_validator": []
    },
    'scripts': [

    ],
    'name': 'protocol_validator',
    'test_suite': 'nose.collector',
    'zip_safe': False
}

setup(**config)
