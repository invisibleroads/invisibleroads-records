import sys
from os.path import abspath, dirname, join
from setuptools import find_packages, setup


ENTRY_POINTS = """
[invisibleroads]
initialize = invisibleroads_records.scripts:InitializeRecordsScript
update = invisibleroads_records.scripts:UpdateRecordsScript
[paste.app_factory]
main = invisibleroads_records:main
"""
FOLDER = dirname(abspath(__file__))
DESCRIPTION = '\n\n'.join(open(join(FOLDER, x)).read().strip() for x in [
    'README.rst', 'CHANGES.rst'])


for command in ('register', 'upload'):
    if command in sys.argv:
        exit('cannot %s private repository' % command)


setup(
    name='invisibleroads-records',
    version='0.4.0',
    description='Database functionality',
    long_description=DESCRIPTION,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid :: InvisibleRoads',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='Roy Hyunjin Han',
    author_email='rhh@crosscompute.com',
    url='https://github.com/invisibleroads/invisibleroads-records',
    keywords='web wsgi bfg pylons pyramid invisibleroads',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    setup_requires=[
        'pytest-runner'
    ],
    install_requires=[
        'pyramid-tm',
        'SQLAlchemy',
        'zope.sqlalchemy',
    ] + [
        'arrow',
        'dogpile.cache',
        'invisibleroads-posts>=0.5.4.2',
        'pytest',
    ],
    tests_require=[
        'pytest-cov',
    ],
    entry_points=ENTRY_POINTS)
