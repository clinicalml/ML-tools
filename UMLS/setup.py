try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(
      name = 'UMLS',
      version = '1.0',
      packages = find_packages(exclude = ['tests']),
      scripts = [],
      author = 'Yacine Jernite',
      author_email = 'jernite@cs.nyu.edu',
      description = 'UMLS concept parser'      
      )
