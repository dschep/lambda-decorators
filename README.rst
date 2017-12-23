
🐍λ✨ - lambda_decorators
=========================

A collection of useful decorators for making AWS Lambda handlers

*NOTE: this is in very early stages of development. And only supports python3*

``lambda_decorators`` is a collection of useful decorators for writing Python
handlers for `AWS Lambda <https://aws.amazon.com/lambda/>`_. They allow you to
avoid boiler plate for common things such as CORS headers, JSON serialization,
etc.

These can be used as a library or simply copied and adapted to your needs.
If you want to write your own "middlewares" it's as easy as writing a
decorator. The documentation has links to the source of each decorator.
They also serve as handy examples for implemenenting your own
boilerplate-reducing decorators.

Quick example
-------------
.. code:: python

    # handler.py

    from lambda_decorators import cors_headers, json_http_resp, load_json_body

    @cors_headers
    @json_http_resp
    @load_json_body
    def handler(event, context):
        return {'hello': event['body']['name']}

When deployed to Lambda behind API Gateway and cURL'd:

.. code:: shell

   $ curl -d '{"name": "world"}' https://example.execute-api.us-east-1.amazonaws.com/dev/hello
   {"hello": "world"}

Install
-------
.. code:: shell

    pip install lambda-decorators

Why
---
Initially, I was inspired by `middy <https://github.com/middyjs/middy>`_ which
I've tried out in JavaScript and was happy with it. So naturally, I thought I'd
like to have something similar in Python too. But then as I thought about it
more, it seemed that when thinking of functions as the compute unit,
when using python, `decorators <https://wiki.python.org/moin/PythonDecorators>`_
pretty much are middleware! So instead of
building a middleware engine and a few middlewares, I just built a few
useful decorators.

Included Decorators:
--------------------
* `async_handler <http://lambda-decorators.rtfd.io#lambda_decorators.async_handler>`_ - support for async handlers
* `cors_headers <http://lambda-decorators.rtfd.io#lambda_decorators.cors_headers>`_ - automatic injection of CORS headers
* `dump_json_body <http://lambda-decorators.rtfd.io#lambda_decorators.dump_json_body>`_ - auto-serialization of http body to JSON
* `json_http_resp <http://lambda-decorators.rtfd.io#lambda_decorators.json_http_resp>`_ - automatic serialization of python object to HTTP JSON response
* `load_json_body <http://lambda-decorators.rtfd.io#lambda_decorators.load_json_body>`_ - auto-deserialize of http body from JSON
* `no_retry_on_failure <http://lambda-decorators.rtfd.io#lambda_decorators.no_retry_on_failure>`_ - detect and stop retry attempts for scheduled lambdas

See each individual decorators for specific usage details and the example_
for some more use cases.

.. _example: https://github.com/dschep/lambda-decorators/tree/master/example

-----


`Full API Documentation <http://lambda-decorators.readthedocs.io/en/latest/>`_
