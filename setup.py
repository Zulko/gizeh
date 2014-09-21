import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

exec(open('gizeh/version.py').read()) # loads __version__

setup(name='gizeh',
      version=__version__,
      author='Zulko',
    description='Simple vector graphics in Python',
    long_description=open('README.rst').read(),
    license='see LICENSE.txt',
    keywords="Cairo vector graphics",
    install_requires=['cairocffi', 'numpy'],
    packages= find_packages(exclude='docs'))
