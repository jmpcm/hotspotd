from setuptools import setup

from src import __name__, __version__, __description__, __author__


setup(name=__name__,
      version=__version__,
      description=__description__,
      long_description=open('README.md').read(),
      author=__author__,
      author_email='prahladyeri@yahoo.com',
      url='https://github.com/prahladyeri/hotspotd.git',
      license='MIT',
      packages=['hotspotd'],
      package_dir={'hotspotd': 'src'},
      package_data={'': ['samples/hostapd.conf']},
      entry_points={
              'console_scripts': [
                      'hotspotd=hotspotd:main',
              ],
      },
      include_package_data=True,
      zip_safe=False,
      classifiers=[
              'Development Status :: 4 - Beta',
              'License :: OSI Approved :: MIT License',
              'Programming Language :: Python :: 2.7',
              'Topic :: System :: Networking',
      ])
