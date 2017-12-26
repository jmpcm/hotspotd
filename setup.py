from setuptools import setup

setup(name='hotspotd',
      version='0.1.8',
      description="Simple daemon to create a WIFI hotspot on GNU/Linux",
      long_description=open('README.md').read(),
      author="Prahlad Yeri",
      author_email='prahladyeri@yahoo.com',
      url='https://github.com/prahladyeri/hotspotd.git',
      license='MIT',
      packages=['hotspotd'],
      package_dir={'hotspotd': 'src/hotspotd'},
      package_data={'hotspotd': ['cfg/hostapd.conf']},
      install_requires=["six >= 1.11.0"],
      entry_points={
          'console_scripts': [
              'hotspotd=hotspotd:main',
          ],
      },
      include_package_data=True,
      zip_safe=True,
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Unix Shell',
          'Topic :: System :: Networking',
      ])
