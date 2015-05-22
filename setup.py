from os.path import join
from setuptools import setup, find_packages


long_description = (
    open('README.rst').read() + open('CHANGES.rst').read())


def get_version():
    with open(join('pgcrypto_expressions', '__init__.py')) as f:
        for line in f:
            if line.startswith('__version__ ='):
                return line.split('=')[1].strip().strip('"\'')


setup(
    name='django-pgcrypto-expressions',
    version=get_version(),
    description=(
        'PGCrypto support for Django 1.8+'
        ),
    long_description=long_description,
    author='ORCAS, Inc',
    author_email='orcastech@orcasinc.com',
    url='https://github.com/orcasgit/django-pgcrypto-expressions/',
    packages=find_packages(),
    install_requires=['Django>=1.8.2'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Framework :: Django',
    ],
    zip_safe=False,
)
