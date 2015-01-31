try:
    from setuptools import setup
except ImportError:
    try:
        import ez_setup
        ez_setup.use_setuptools()
    except ImportError:
        raise ImportError("Gizeh could not be installed, probably because"
            " neither setuptools nor ez_setup are installed on this computer."
            "\nInstall ez_setup ([sudo] pip install ez_setup) and try again.")

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
