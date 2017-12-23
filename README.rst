
lambda_decorators
*****************

🐍λ✨ - A collection of useful decorators for making AWS Lambda handlers

NOTE: this is in very early stages of development.


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
