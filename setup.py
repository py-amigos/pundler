#!/usr/bin/env python

from setuptools import setup
import os.path


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


setupconf = dict(
    name='pundle',
    version='0.9.1',
    license='BSD',
    url='https://github.com/Deepwalker/pundler/',
    author='Deepwalker',
    author_email='krivushinme@gmail.com',
    description=('Requirements management tool.'),
    long_description=read('README.rst'),
    keywords='bundler virtualenv pip install package setuptools',

    install_requires=[
        # v39.0 - Removed long-deprecated support for iteration on Version
        # objects as returned by pkg_resources.parse_version. Removed the
        # SetuptoolsVersion and SetuptoolsLegacyVersion names as well. They
        # should not have been used, but if they were, replace with Version and
        # LegacyVersion from packaging.version.
        'setuptools<=38.7.0'
    ],
    py_modules=['pundle'],
    entry_points=dict(
        console_scripts=[
            'pundle = pundle:cli.run'
        ]
    ),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)

if __name__ == '__main__':
    setup(**setupconf)
