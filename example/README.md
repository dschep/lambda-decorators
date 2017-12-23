# `lambda_decorators` examples

This directory contains a [`handler.py`](./handler.py) file that contains
multiple handlers using various decorators provided by `lambda_decorators`.
There is also a [`serverless.yml`](./serverless.yml) for deploying with
[the serverless framework](https://github.com/serverless/serverless). It uses
the [serverless-python-requirements](https://github.com/UnitedIncome/serverless-python-requirements)
plugin to install necessary dependencies.

To install all of the above and deploy:
```
npm install -g serverless
npm install # installs the plugin, specified in package.json
sls deploy
```
