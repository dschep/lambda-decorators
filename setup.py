from setuptools import setup

long_description = open('README.rst').read()

setup(
    name='lambda-decorators',

    version='0.1a1',

    description='A collection of useful decorators for making AWS Lambda handlers',
    long_description=long_description,

    url='http://lambda-decorator.readthedocs.io',

    author='Daniel Schep',
    author_email='dschep@gmail.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Environment :: Other Environment',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='serverless lambda decorator aws',

    py_modules=['lambda_decorators'],
)
