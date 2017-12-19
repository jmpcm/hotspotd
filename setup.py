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
