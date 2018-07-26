import os
import re

from setuptools import setup

v = open(os.path.join(os.path.dirname(__file__), 'sqlalchemy_ocientdb', '__init__.py'))
VERSION = re.compile(r".*__version__ = '(.*?)'", re.S).match(v.read()).group(1)
v.close()

readme = os.path.join(os.path.dirname(__file__), 'README.rst')


setup(name='sqlalchemy_ocientdb',
      version=VERSION,
      description="OcientDb for SQLAlchemy",
      long_description=open(readme).read(),
      classifiers=[
      'Development Status :: 3 - Alpha',
      'Environment :: Console',
      'Intended Audience :: Developers',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: Implementation :: CPython',
      'Topic :: Database :: Front-Ends',
      ],
      keywords='SQLAlchemy OcientDb',
      author='Hank Calzaretta',
      author_email='hcalzaretta@ocient.com',
      license='MIT',
      packages=['sqlalchemy_ocientdb'],
      include_package_data=True,
      tests_require=['nose >= 0.11'],
      test_suite="nose.collector",
      zip_safe=False,
      entry_points={
         'sqlalchemy.dialects': [
              'ocientdb = sqlalchemy_ocientdb.pyodbc:OcientDbDialect_pyodbc',
              'ocientdb.pyodbc = sqlalchemy_ocientdb.pyodbc:OcientDbDialect_pyodbc',
              ]
        }
)
