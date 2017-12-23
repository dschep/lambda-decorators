
🐍λ✨ - lambda_decorators
***********************

A collection of useful decorators for making AWS Lambda handlers

*NOTE: this is in very early stages of development.*

``lambda_decorators`` is a collection of useful decorators for writing
Python handlers for AWS Lambda. They allow you to avoid boiler plate
for common things such as CORS headers, JSON serialization, etc.

These can be used as a library or simply copied and adapted to your
needs. If you want to write your own “middlewares” it’s as easy as
writing a decorator. The documentation has links to the source of each
decorator. They also serve as handy examples for implemenenting your
own boilerplate-reducing decorators.


Quick example
=============

::

   # handler.py

   from lambda_decorators import cors, json_http_resp, load_json_body

   @cors
   @json_http_resp
   @load_json_body
   def handler(event, context):
       return {'hello': event['body']['name']}


Install
=======

::

   pip install git+https://github.com/dschep/lambda-decorators


Why
===

Initially, I was inspired by middy which I’ve tried out in JavaScript
and was happy with it. So naturally, I thought I’d like to have
something similar in Python too. But then as I thought about it more,
it seemed that when thinking of functions as the compute unit, when
using python, decorators pretty much are middleware! So instead of
building a middleware engine and a few middlewares, I just built a few
useful decorators.


Included Decorators:
====================

..

   * `async_handler() <https://lambda-decorators.readthedocs.org/#lambda_decorators.async_handler>`_ -
     support for async handlers

   * `cors() <https://lambda-decorators.readthedocs.org/#lambda_decorators.cors>`_ - automatic
     injection of CORS headers

   * `dump_json_body() <https://lambda-decorators.readthedocs.org/#lambda_decorators.dump_json_body>`_
     - auto-serialization of http body to JSON

   * `json_http_resp() <https://lambda-decorators.readthedocs.org/#lambda_decorators.json_http_resp>`_
     - automatic serialization of python object to HTTP JSON response

   * `load_json_body() <https://lambda-decorators.readthedocs.org/#lambda_decorators.load_json_body>`_
     - auto-deserialize of http body from JSON

   * `no_retry_on_failure()
     <https://lambda-decorators.readthedocs.org/#lambda_decorators.no_retry_on_failure>`_ - detect and
     stop retry attempts for scheduled lambdas

See each individual decorators for specific usage details and the
example for some more use cases.

======================================================================

`Full API Documentation <http://lambda-decorators.readthedocs.io/en/latest/>`_
