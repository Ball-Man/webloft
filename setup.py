from setuptools import setup

# README = open('README.md').read()
REQUIREMENTS = open('requirements.txt').read().splitlines()

setup(name='webloft',
      classifiers=['Programming Language :: Python :: 3 :: Only',
                   'Environment :: Console',
                   'License :: OSI Approved :: MIT License',
                   'Topic :: Internet :: WWW/HTTP :: Site Management'],
      version='1.0',
      description='A static website generator.',
      long_description='A static website generator with support for custom templates.',
      url='http://github.com/Ball-Man/webloft',
      author='Francesco Mistri',
      author_email='franc.mistri@gmail.com',
      license='MIT',
      packages=['webloft'],
      package_data={'webloft': ['templates/**/*', 'templates/*']},
      include_package_data=True,
      entry_points={
        'console_scripts': [
          'webloft = webloft.__main__:main'
        ]
      },
      install_requires=REQUIREMENTS
      )