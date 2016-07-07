from os.path import abspath, dirname, join
from setuptools import find_packages, setup


ENTRY_POINTS = """
[invisibleroads]
initialize = invisibleroads_records.scripts:InitializeRecordsScript
update = invisibleroads_records.scripts:UpdateRecordsScript
"""
FOLDER = dirname(abspath(__file__))
DESCRIPTION = '\n\n'.join(open(join(FOLDER, x)).read().strip() for x in [
    'README.rst', 'CHANGES.rst'])
setup(
    name='invisibleroads-records',
    version='0.2.2',
    description='Database functionality',
    long_description=DESCRIPTION,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid :: InvisibleRoads',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='Roy Hyunjin Han',
    author_email='rhh@crosscompute.com',
    url='http://invisibleroads.com',
    keywords='web wsgi bfg pylons pyramid invisibleroads',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    setup_requires=[
        'pytest-runner',
    ],
    install_requires=[
        'pyramid_tm',
        'SQLAlchemy',
        'transaction',
        'zope.sqlalchemy',
    ] + [
        'dogpile.cache',
        'invisibleroads-posts>=0.4.8',
    ],
    tests_require=[
        'pytest',
    ],
    entry_points=ENTRY_POINTS)
