#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="tap-spreadsheets-anywhere",
    version="0.1.0",
    description="Singer.io tap for extracting spreadsheet data from cloud storage",
    author="Eric Simmerman",
    url="https://github.com/ets/tap-spreadsheets-anywhere",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap_spreadsheets_anywhere"],
    install_requires=[
        "singer-python>=5.0.12",
        'smart_open>=2.1',
        'voluptuous>=0.10.5',
        'boto3>=1.15.5',
        'google-cloud-storage>=1.31.2',
        'xlrd==1.2.0',
        'tqdm==4.57.0'
    ],
    entry_points="""
    [console_scripts]
    tap-spreadsheets-anywhere=tap_spreadsheets_anywhere:main
    """,
    packages=find_packages(),
    package_data={
        'tap_spreadsheets_anywhere': [
            'files/xlsx/*.xlsm', 'files/xlsx/*.xls', 'files/xlsx/*.xlsx', 'files/csv/*.csv'
        ]
    }
)