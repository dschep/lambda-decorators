from setuptools import setup

long_description = open('README.rst').read()

setup(
    name='lambda-decorators',

    version='0.1a',

    description='A collection of useful decorators for making AWS Lambda handlers',
    long_description=long_description,

    url='https://github.com/dschep/lambda-decorators',

    author='Daniel Schep',
    author_email='dschep@gmail.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Alpha',

        'Environment :: Serverless',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='serverless lambda decorator aws',

    py_modules=['lambda_decorator'],
)
