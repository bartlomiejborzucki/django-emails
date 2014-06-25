#!/usr/bin/env python

from setuptools import setup, find_packages

tests_require = [
    'unittest2',
    'django',
]

setup(
    name='django-emails',
    version='0.1',
    author='Bartlomiej Borzucki',
    author_email='borzucki@gmail.com',
    url='',
    install_requires=[
        'django-templatetag-sugar>=0.1',
        'pycrypto',
        'django_ses'
    ],
    tests_require=tests_require,
    license='BSD',
    extras_require={'test': tests_require},
    test_suite='unittest2.collector',
    description='An efficient paginator that works.',
    packages=find_packages(),
    include_package_data=False,
    zip_safe=False,
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)
