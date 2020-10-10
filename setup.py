from os.path import abspath, dirname, join
from setuptools import find_packages, setup


ENTRY_POINTS = '''
[invisibleroads]
initialize = invisibleroads_records.scripts:InitializeRecordsScript
'''
APPLICATION_CLASSIFIERS = [
    'Programming Language :: Python',
    'Framework :: Pyramid',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    'License :: OSI Approved :: MIT License',
]
APPLICATION_REQUIREMENTS = [
    # architecture
    'invisibleroads >= 0.3.3',
    'invisibleroads-posts >= 0.7.16.1',
    # web
    'pyramid',
    # database
    # 'alembic',
    'pyramid-retry',
    'pyramid-tm',
    'sqlalchemy',
    'transaction',
    'zope.sqlalchemy',
    # test
    'pytest',
    # shortcut
    'invisibleroads-macros-configuration >= 1.0.6',
    'invisibleroads-macros-log >= 1.0.3',
    'invisibleroads-macros-security >= 1.0.1',
]
TEST_REQUIREMENTS = [
    'pytest-cov',
]
FOLDER = dirname(abspath(__file__))
DESCRIPTION = '\n\n'.join(open(join(FOLDER, x)).read().strip() for x in [
    'README.md', 'CHANGES.md'])


setup(
    name='invisibleroads-records',
    version='0.5.9.2',
    description='Web application database defaults',
    long_description=DESCRIPTION,
    long_description_content_type='text/markdown',
    classifiers=APPLICATION_CLASSIFIERS,
    author='Roy Hyunjin Han',
    author_email='rhh@crosscompute.com',
    url='https://github.com/invisibleroads/invisibleroads-records',
    keywords='web wsgi bfg pylons pyramid invisibleroads',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    extras_require={'test': TEST_REQUIREMENTS},
    install_requires=APPLICATION_REQUIREMENTS,
    entry_points=ENTRY_POINTS)
