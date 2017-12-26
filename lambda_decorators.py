# -*- coding: utf-8 -*-
"""
🐍λ✨ - lambda_decorators
=========================

A collection of useful decorators for making AWS Lambda handlers

*NOTE: this is in very early stages of development.*

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
* :meth:`async_handler` - support for async handlers
* :meth:`cors_headers` - automatic injection of CORS headers
* :meth:`dump_json_body` - auto-serialization of http body to JSON
* :meth:`json_http_resp` - automatic serialization of python object to HTTP JSON response
* :meth:`load_json_body` - auto-deserialize of http body from JSON
* :meth:`no_retry_on_failure` - detect and stop retry attempts for scheduled lambdas

See each individual decorators for specific usage details and the example_
for some more use cases.

.. _example: https://github.com/dschep/lambda-decorators/tree/master/example

-----

"""

import json
from functools import wraps

try:
    import asyncio
except ImportError:
    pass

__version__ = '0.1a4'


def async_handler(handler):
    """
    This decorator allows for use of async handlers by automatically running
    them in an event loop. The loop is added to the context object for if the
    handler needs it.

    Usage::

      from lambda_decorators import async_handler
      @async_handler
      async def handler(event, context):
          return await foobar()

    *NOTE: Python 3 only*
    """
    @wraps(handler)
    def wrapper(event, context):
        context.loop = asyncio.get_event_loop()
        return context.loop.run_until_complete(handler(event, context))

    return wrapper


def cors_headers(handler_or_origin):
    """
Automatically injects ``Access-Control-Allow-Origin`` headers to http
responses.

Usage::

        from lambda_decorators import cors_headers
        @cors_headers
        def hello(example, context):
            return {'body': 'foobar'}
        # or with custom domain
        @cors_headers('https://example.com')
        def hello_custom_origin(example, context):
            return {'body': 'foobar'}

the ``hello`` example returns

.. code:: python

    {'body': 'foobar', 'headers': {'Access-Control-Allow-Origin': '*'}}
    """
    if isinstance(handler_or_origin, str):
        def wrapper_wrapper(handler):
            @wraps(handler)
            def wrapper(event, context):
                response = handler(event, context)
                headers = response.setdefault('headers', {})
                headers['Access-Control-Allow-Origin'] = handler_or_origin
                return response

            return wrapper

        return wrapper_wrapper
    else:
        return cors_headers('*')(handler_or_origin)


def dump_json_body(handler):
    """
Automatically serialize response bodies with json.dumps.

Returns a 500 error if the response cannot be serialized

Usage::

  from lambda_decorators import dump_json_body
  @dump_json_body
  def handler(event, context):
      return {'statusCode': 200, 'body': {'hello': 'world'}}

in this example, the decorators handler returns:

.. code:: python

    {'statusCode': 200, 'body': '{"hello": "world"}'}
    """
    @wraps(handler)
    def wrapper(event, context):
        response = handler(event, context)
        if 'body' in response:
            try:
                response['body'] = json.dumps['body']
            except Exception as exc:
                return {'statusCode': 500, 'body': str(exc)}
        return response


def json_http_resp(handler):
    """
Automatically serialize return value to the body of a successfull HTTP
response.

Returns a 500 error if the response cannot be serialized

Usage::

    from lambda_decorators import json_http_resp
    @json_http_resp
    def handler(event, context):
        return {'hello': 'world'}

in this example, the decorated handler returns:

.. code:: python

    {'statusCode': 200, 'body': '{"hello": "world"}'}
    """
    @wraps(handler)
    def wrapper(event, context):
        response = handler(event, context)
        try:
            body = json.dumps(response)
        except Exception as exc:
            return {'statusCode': 500, body: str(exc)}
        return {'statusCode': 200, 'body': body}

    return wrapper

    return wrapper


def load_json_body(handler):
    """
    Automatically deserialize event bodies with json.loads.

    Automatically returns a 400 BAD REQUEST if there is an error while parsing.

    Usage::

      from lambda_decorators import load_json_body
      @load_json_body
      def handler(event, context):
          return event['body']['foobar']

    note that ``event['body']`` is already a dictionary and didn't have to
    explicitly be parsed.
    """
    @wraps(handler)
    def wrapper(event, context):
        if isinstance(event.get('body'), str):
            try:
                event['body'] = json.loads(event['body'])
            except:
                return {'statusCode': 400, 'body': 'BAD REQUEST'}
        return handler(event, context)

    return wrapper


def no_retry_on_failure(handler):
    """
    AWS Lambda retries scheduled lambdas that don't execute succesfully.

    This detects this by storing requests IDs in memory and exiting early on
    duplicates. Since this is in memory, don't use it on very frequently
    scheduled lambdas. It raises a ``RuntimeError``

    Usage::

      from lambda_decorators import no_retry_on_failure
      @no_retry_on_failure
      def scheduled_handler(event, context):
          do_something()

    """
    seen_request_ids = set()

    @wraps(handler)
    def wrapper(event, context):
        if context.aws_request_id in seen_request_ids:
            raise RuntimeError(('Retry attempt on request id '
                                '{} detected.').format(context.aws_request_id))
        seen_request_ids.add(context.aws_request_id)
        return handler(event, context)

    return wrapper
