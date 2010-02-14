from setuptools import setup, find_packages
import sys, os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1'

setup(name='hostout.cloud',
      version=version,
      description="all your hosts are belong to us!!!",
    long_description=(
        read('hostout', 'cloud', 'README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' 
        ),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='hostout',
      author='Dylan Jay',
      author_email='software@pretaweb.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages = ['hostout'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'collective.hostout',
          'apache-libcloud',
          'zope.interface>=0.1',
          'setuptools',
        ],
      entry_points = {'zc.buildout':
                    ['default = hostout.cloud:Recipe']},
      )
