"""
DISCLAIMER: This file should be preserved even when msq isn't available on PyPI because gavel uses pipx and pipx uses setup.py!!!
"""

from setuptools import setup, find_packages

def read_long_description():
    with open('README.md', encoding='utf-8') as f:
        return f.read()

from msq import version

setup(
    name='msq',
    version=version,
    author='FOSSIL',
    author_email='fossil-org1@gmail.com',
    description='an easy to understand language built from Python.',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
    install_requires=["pyinstaller"],
    entry_points={
        'console_scripts': [
            'msq=msq.internal.build:build_from_sys_argv'
        ]
    },
)