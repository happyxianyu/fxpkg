from setuptools import *


setup(
    name='fxpkg',
    version='0.0.0',
    packages=find_namespace_packages('inc'),
    package_dir={'fxpkg': 'inc/fxpkg'},
    install_requires=[
        'cbutil'
        ],
    python_requires='>=3.8',

    url='https://github.com/happyxianyu/fxpkg',
    license='Apache License 2.0',
    author='happyxianyu',
    author_email=' happyxianyu623@outlook.com',
    description=''
)
