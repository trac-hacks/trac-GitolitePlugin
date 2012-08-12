from setuptools import setup

try:
    long_description = open("README.txt").read()
except:
    long_description = ''
try:
    long_description += open("CHANGES.txt").read()
except:
    pass

setup(name='trac_gitolite',
      version='0.1dev',
      description="",
      long_description=long_description,
      packages=['trac_gitolite'],
      author='Ethan Jucovy',
      author_email='ejucovy@gmail.com',
      url="http://trac-hacks.org/wiki/GitolitePlugin",
      license='BSD',
      entry_points = {'trac.plugins': ['trac_gitolite = trac_gitolite']})
