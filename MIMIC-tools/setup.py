from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='MIMICTools',
      version=version,
      description="MIMIC tools",
      long_description="""\
Utilities for parsing MIMIC data""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='mimic',
      author='Ankit Vani',
      author_email='ankit.vani@nyu.edu',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
