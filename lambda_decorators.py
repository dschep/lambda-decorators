# -*- coding: utf-8 -*-
"""
🐍λ✨ - lambda_decorators
=========================
|Version|_ |Docs|_ |Build|_ |SayThanks|_

A collection of useful decorators for making AWS Lambda handlers

``lambda_decorators`` is a collection of useful decorators for writing Python
handlers for `AWS Lambda <https://aws.amazon.com/lambda/>`_. They allow you to
avoid boiler plate for common things such as CORS headers, JSON serialization,
etc.

Quick example
-------------
.. code:: python

    # handler.py

    from lambda_decorators import json_http_resp, load_json_body

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
If you are using `the serverless framework <https://github.com/serverless/serverless>`_
I recommend using
`serverless-python-requirements <https://github.com/UnitedIncome/serverless-python-requirements>`_

.. code:: shell

    sls plugin install -n serverless-python-requirements
    echo lambda-decorators >> requirements.txt

Or if using some other deployment method to AWS Lambda you can just download
the entire module because it's only one file.

.. code:: shell

    curl -O https://raw.githubusercontent.com/dschep/lambda-decorators/master/lambda_decorators.py

Included Decorators:
--------------------
``lambda_decorators`` includes the following decorators to avoid boilerplate
for common usecases when using AWS Lambda with Python.

* :func:`async_handler` - support for async handlers
* :func:`cors_headers` - automatic injection of CORS headers
* :func:`dump_json_body` - auto-serialization of http body to JSON
* :func:`load_json_body` - auto-deserialize of http body from JSON
* :func:`json_http_resp` - automatic serialization of python object to HTTP JSON response
* :func:`json_schema_validator` - use JSONSchema to validate request&response payloads
* :func:`load_urlencoded_body` - auto-deserialize of http body from a querystring encoded body
* :func:`no_retry_on_failure` - detect and stop retry attempts for scheduled lambdas
* :func:`ssm_parameter_store` - fetch parameters from the AWS SSM Parameter Store
* :func:`secrets_manager` - fetch secrets from the AWS Secrets Manager

See each individual decorators for specific usage details and the example_
for some more use cases. This library is also meant to serve as an example for how to write
decorators for use as lambda middleware. See the recipes_ page for some more niche examples of
using decorators as middleware for lambda.

.. _example: https://github.com/dschep/lambda-decorators/tree/master/example
.. _recipes: recipes.html

Writing your own
----------------
``lambda_decorators`` includes utilities to make building your own decorators
easier. The :func:`before`, :func:`after`, and :func:`on_exception` decorators
can be applied to your own functions to turn them into decorators for your
handlers. For example:


.. code:: python

    import logging
    from lambda_decorators import before

    @before
    def log_event(event, context):
        logging.debug(event)
        return event, context

    @log_event
    def handler(event, context):
        return {}

And if you want to make a decorator that provides two or more of
before/after/on_exception functionality, you can use
:class:`LambdaDecorator`:

.. code:: python

    import logging
    from lambda_decorators import LambdaDecorator

    class log_everything(LambdaDecorator):
        def before(self, event, context):
            logging.debug(event, context)
            return event, context
        def after(self, retval):
            logging.debug(retval)
            return retval
        def on_exception(self, exception):
            logging.debug(exception)
            return {'statusCode': 500}

    @log_everything
    def handler(event, context):
        return {}


Why
---
Initially, I was inspired by `middy <https://github.com/middyjs/middy>`_ which
I like using in JavaScript. So naturally, I thought I'd like to have something similar in Python
too. But then as I thought about it more, it seemed that when thinking of functions as the compute
unit, when using python, `decorators <https://wiki.python.org/moin/PythonDecorators>`_
pretty much are middleware! So instead of building a middleware engine and a few middlewares, I
just built a few useful decorators and utilities to build them.

-----

.. |Version| image:: https://img.shields.io/pypi/v/lambda-decorators.svg
.. _Version: https://pypi.org/project/lambda-decorators
.. |Docs| image:: http://readthedocs.org/projects/lambda-decorators/badge/?version=latest
.. _Docs: http://lambda-decorators.readthedocs.org/en/latest
.. |Build| image:: https://img.shields.io/travis/dschep/lambda-decorators/master.svg
.. _Build: https://travis-ci.org/dschep/lambda-decorators
.. |SayThanks| image:: https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg
.. _SayThanks: https://saythanks.io/to/dschep

"""

import json
import logging
import boto3
from functools import wraps, update_wrapper

try:
    import asyncio
except ImportError:
    pass

try:
    import jsonschema
except ImportError:
    jsonschema = None

try:
    from urllib.parse import parse_qs
except ImportError:
    from urlparse import parse_qs

try:
    basestring
except NameError:
    basestring = str


logger = logging.getLogger(__name__)

__version__ = "0.6.0"


class LambdaDecorator(object):
    """
    This is a class for simplifying the creation of decorators for use on
    Lambda handlers.

    You subclass :class:`LambdaDecorator` and add your own
    :meth:`~LambdaDecorator.before`,
    :meth:`~LambdaDecorator.after`, or :meth:`~LambdaDecorator.on_exception`
    methods.

    Usage::

        >>> from lambda_decorators import LambdaDecorator
        >>> class print_event_and_resp(LambdaDecorator):
        ...     def before(self, event, context):
        ...         print('event: ', event)
        ...         return event, context
        ...     def after(self, retval):
        ...         print('retval: ', retval)
        ...         return retval
        >>> @print_event_and_resp
        ... def handler(event, context):
        ...     return 'hello world'
        >>> handler({'foo': 'bar'}, object())
        event:  {'foo': 'bar'}
        retval:  hello world
        'hello world'
        >>>
        >>> # And exception handling:
        >>> class handle_exceptions(LambdaDecorator):
        ...     def on_exception(self, exception):
        ...         return {'statusCode': 500, 'body': 'uh oh, you broke it'}
        >>> @handle_exceptions
        ... def handler(event, context):
        ...     raise Exception
        >>> handler({}, object)
        {'statusCode': 500, 'body': 'uh oh, you broke it'}
    """

    def __init__(self, handler):
        update_wrapper(self, handler)
        self.handler = handler

    def __call__(self, event, context):
        try:
            return self.after(self.handler(*self.before(event, context)))
        except Exception as exception:
            return self.on_exception(exception)

    def before(self, event, context):
        return event, context

    def after(self, retval):
        return retval

    def on_exception(self, exception):
        raise exception


def before(func):
    """
    Run a function before the handler is invoked, is passed the event & context
    and must return an event & context too.

    Usage::

        >>> # to create a reusable decorator
        >>> @before
        ... def print_request_id(event, context):
        ...     print(context.aws_request_id)
        ...     return event, context
        >>> @print_request_id
        ... def handler(event, context):
        ...     pass
        >>> class Context:
        ...     aws_request_id = 'ID!'
        >>> handler({}, Context())
        ID!
        >>> # or a one off
        >>> @before(lambda e, c: (e['body'], c))
        ... def handler(body, context):
        ...     return body
        >>> handler({'body': 'BOOODYY'}, object())
        'BOOODYY'
    """

    class BeforeDecorator(LambdaDecorator):
        def before(self, event, context):
            return func(event, context)

    return BeforeDecorator


def after(func):
    """
    Run a function after the handler is invoked, is passed the response
    and must return an response too.

    Usage::

        >>> # to create a reusable decorator
        >>> @after
        ... def gnu_terry_pratchett(retval):
        ...     retval.setdefault('Headers', {})['X-Clacks-Overhead'] = 'GNU Terry Pratchett'
        ...     return retval
        >>> @gnu_terry_pratchett
        ... def handler(event, context):
        ...     return {'body': ''}
        >>> handler({}, object())
        {'body': '', 'Headers': {'X-Clacks-Overhead': 'GNU Terry Pratchett'}}
    """

    class AfterDecorator(LambdaDecorator):
        def after(self, retval):
            return func(retval)

    return AfterDecorator


def on_exception(func):
    """
    Run a function when a handler thows an exception. It's return value is
    returned to AWS.

    Usage::

        >>> # to create a reusable decorator
        >>> @on_exception
        ... def handle_errors(exception):
        ...     print(exception)
        ...     return {'statusCode': 500, 'body': 'uh oh'}
        >>> @handle_errors
        ... def handler(event, context):
        ...     raise Exception('it broke!')
        >>> handler({}, object())
        it broke!
        {'statusCode': 500, 'body': 'uh oh'}
        >>> # or a one off
        >>> @on_exception(lambda e: {'statusCode': 500})
        ... def handler(body, context):
        ...     raise Exception
        >>> handler({}, object())
        {'statusCode': 500}
    """

    class OnExceptionDecorator(LambdaDecorator):
        def on_exception(self, exception):
            return func(exception)

    return OnExceptionDecorator


def async_handler(handler):
    """
    This decorator allows for use of async handlers by automatically running
    them in an event loop. The loop is added to the context object for if the
    handler needs it.

    Usage::

        >>> from lambda_decorators import async_handler
        >>> async def foobar():
        ...     return 'foobar'
        >>> @async_handler
        ... async def handler(event, context):
        ...     return await foobar()
        >>> class Context:
        ...     pass
        >>> handler({}, Context())
        'foobar'


    *NOTE: Python 3 only*
    """

    @wraps(handler)
    def wrapper(event, context):
        context.loop = asyncio.get_event_loop()
        return context.loop.run_until_complete(handler(event, context))

    return wrapper


def cors_headers(handler_or_origin=None, origin=None, credentials=False):
    """
Automatically injects ``Access-Control-Allow-Origin`` headers to http
responses. Also optionally adds ``Access-Control-Allow-Credentials: True`` if
called with ``credentials=True``

Usage::

    >>> from lambda_decorators import cors_headers
    >>> @cors_headers
    ... def hello(example, context):
    ...     return {'body': 'foobar'}
    >>> hello({}, object())
    {'body': 'foobar', 'headers': {'Access-Control-Allow-Origin': '*'}}
    >>> # or with custom domain
    >>> @cors_headers(origin='https://example.com', credentials=True)
    ... def hello_custom_origin(example, context):
    ...     return {'body': 'foobar'}
    >>> hello_custom_origin({}, object())
    {'body': 'foobar', 'headers': {'Access-Control-Allow-Origin': 'https://example.com', 'Access-Control-Allow-Credentials': True}}
    """
    if isinstance(handler_or_origin, str) and origin is not None:
        raise TypeError(
            "You cannot include any positonal arguments when using"
            " the `origin` keyword argument"
        )
    if isinstance(handler_or_origin, str) or origin is not None:

        def wrapper_wrapper(handler):
            @wraps(handler)
            def wrapper(event, context):
                response = handler(event, context)
                if response is None:
                    response = {}
                headers = response.setdefault("headers", {})
                if origin is not None:
                    headers["Access-Control-Allow-Origin"] = origin
                else:
                    headers["Access-Control-Allow-Origin"] = handler_or_origin
                if credentials:
                    headers["Access-Control-Allow-Credentials"] = True
                return response

            return wrapper

        return wrapper_wrapper
    elif handler_or_origin is None:
        return cors_headers("*", credentials=credentials)
    else:
        return cors_headers("*")(handler_or_origin)


def dump_json_body(handler_or_none=None, **json_dumps_kwargs):
    """
Automatically serialize response bodies with json.dumps.

Returns a 500 error if the response cannot be serialized

Usage::

  >>> from lambda_decorators import dump_json_body
  >>> @dump_json_body
  ... def handler(event, context):
  ...     return {'statusCode': 200, 'body': {'hello': 'world'}}
  >>> handler({}, object())
  {'statusCode': 200, 'body': '{"hello": "world"}'}
  >>> from decimal import Decimal
  >>> @dump_json_body(default=str)
  ... def handler(event, context):
  ...     return {'statusCode': 200, 'body': {'hello': Decimal('4.2')}}
  >>> handler({}, object())
  {'statusCode': 200, 'body': '{"hello": "4.2"}'}
    """

    if handler_or_none is not None and len(json_dumps_kwargs) > 0:
        raise TypeError(
            "You cannot include both handler and keyword arguments. How did you even call this?"
        )
    if handler_or_none is None:

        def wrapper_wrapper(handler):
            @wraps(handler)
            def wrapper(event, context):
                try:
                    response = handler(event, context)
                    if response and "body" in response:
                        response["body"] = json.dumps(
                            response["body"], **json_dumps_kwargs
                        )
                    return response
                except Exception as exception:
                    if hasattr(context, "serverless_sdk"):
                        context.serverless_sdk.capture_exception(exception)
                    return {"statusCode": 500, "body": str(exception)}

            return wrapper

        return wrapper_wrapper
    else:
        return dump_json_body()(handler_or_none)


def json_http_resp(handler_or_none=None, **json_dumps_kwargs):
    """
Automatically serialize return value to the body of a successfull HTTP
response.

Returns a 500 error if the response cannot be serialized

Usage::

    >>> from lambda_decorators import json_http_resp
    >>> @json_http_resp
    ... def handler(event, context):
    ...     return {'hello': 'world'}
    >>> handler({}, object())
    {'statusCode': 200, 'body': '{"hello": "world"}'}
    >>> @json_http_resp
    ... def err_handler(event, context):
    ...     raise Exception('foobar')
    >>> err_handler({}, object())
    {'statusCode': 500, 'body': 'foobar'}
    >>> from decimal import Decimal
    >>> @json_http_resp(default=str)
    ... def handler(event, context):
    ...     return {'hello': Decimal('4.2')}
    >>> handler({}, object())
    {'statusCode': 200, 'body': '{"hello": "4.2"}'}

in this example, the decorated handler returns:

.. code:: python

    {'statusCode': 200, 'body': '{"hello": "world"}'}
    """

    if handler_or_none is not None and len(json_dumps_kwargs) > 0:
        raise TypeError(
            "You cannot include both handler and keyword arguments. How did you even call this?"
        )
    if handler_or_none is None:

        def wrapper_wrapper(handler):
            @wraps(handler)
            def wrapper(event, context):
                try:
                    resp = handler(event, context)
                    if isinstance(resp, dict):
                        status = resp.pop('statusCode', 200)
                    else:
                        status = 200
                    if isinstance(resp, dict):
                        headers = resp.pop('headers', None)
                    else:
                        headers = None
                    http_resp = {
                        "statusCode": status,
                        "body": json.dumps(
                            resp, **json_dumps_kwargs
                        ),
                    }
                    if headers:
                        http_resp["headers"] = headers
                    return http_resp
                except Exception as exception:
                    if hasattr(context, "serverless_sdk"):
                        context.serverless_sdk.capture_exception(exception)
                    return {"statusCode": 500, "body": str(exception)}

            return wrapper

        return wrapper_wrapper
    else:
        return json_http_resp()(handler_or_none)


def load_json_body(handler_or_none=None, **json_loads_kwargs):
    """
    Automatically deserialize event bodies with json.loads.

    Automatically returns a 400 BAD REQUEST if there is an error while parsing.

    Usage::

      >>> from lambda_decorators import load_json_body
      >>> @load_json_body
      ... def handler(event, context):
      ...     return event['body']['foo']
      >>> handler({'body': '{"foo": "bar"}'}, object())
      'bar'

    note that ``event['body']`` is already a dictionary and didn't have to
    explicitly be parsed.
    """
    if handler_or_none is not None and len(json_loads_kwargs) > 0:
        raise TypeError(
            "You cannot include both handler and keyword arguments. How did you even call this?"
        )
    if handler_or_none is None:

        def wrapper_wrapper(handler):
            @wraps(handler)
            def wrapper(event, context):
                if isinstance(event.get("body"), str):
                    try:
                        event["body"] = json.loads(event["body"], **json_loads_kwargs)
                    except Exception as exception:
                        if hasattr(context, "serverless_sdk"):
                            context.serverless_sdk.capture_exception(exception)
                        return {"statusCode": 400, "body": "BAD REQUEST"}
                return handler(event, context)

            return wrapper

        return wrapper_wrapper
    else:
        return load_json_body()(handler_or_none)


def json_schema_validator(request_schema=None, response_schema=None):
    """
    Validate your request & response payloads against a JSONSchema.

    *NOTE: depends on the* `jsonschema <https://github.com/Julian/jsonschema>`_
    *package. If you're using* `serverless-python-requirements <https://github.com/UnitedIncome/serverless-python-requirements>`_
    *you're all set. If you cURLed* ``lambda_decorators.py`` *you'll have to
    install it manually in your service's root directory.*

    Usage::

      >>> from jsonschema import ValidationError
      >>> from lambda_decorators import json_schema_validator
      >>> @json_schema_validator(request_schema={
      ... 'type': 'object', 'properties': {'price': {'type': 'number'}}})
      ... def handler(event, context):
      ...     return event['price']
      >>> handler({'price': 'bar'}, object())
      {'statusCode': 400, 'body': "RequestValidationError: 'bar' is not of type 'number'"}
      >>> @json_schema_validator(response_schema={
      ... 'type': 'object', 'properties': {'price': {'type': 'number'}}})
      ... def handler(event, context):
      ...     return {'price': 'bar'}
      >>> handler({}, object())
      {'statusCode': 500, 'body': "ResponseValidationError: 'bar' is not of type 'number'"}
    """

    def wrapper_wrapper(handler):
        @wraps(handler)
        def wrapper(event, context):
            if request_schema is not None:
                if jsonschema is None:
                    logger.error(
                        "jsonschema is not installed, skipping request validation"
                    )
                else:
                    try:
                        jsonschema.validate(event, request_schema)
                    except jsonschema.ValidationError as exception:
                        if hasattr(context, "serverless_sdk"):
                            context.serverless_sdk.capture_exception(exception)
                        return {
                            "statusCode": 400,
                            "body": "RequestValidationError: {}".format(
                                exception.message
                            ),
                        }
            response = handler(event, context)
            if response_schema is not None:
                if jsonschema is None:
                    logger.error(
                        "jsonschema is not installed, skipping response validation"
                    )
                else:
                    try:
                        jsonschema.validate(response, response_schema)
                    except jsonschema.ValidationError as exception:
                        if hasattr(context, "serverless_sdk"):
                            context.serverless_sdk.capture_exception(exception)
                        return {
                            "statusCode": 500,
                            "body": "ResponseValidationError: {}".format(
                                exception.message
                            ),
                        }
            return response

        return wrapper

    return wrapper_wrapper


def load_urlencoded_body(handler):
    """
    Automatically deserialize application/x-www-form-urlencoded bodies

    Automatically returns a 400 BAD REQUEST if there is an error while parsing.

    Usage::

      >>> from lambda_decorators import load_urlencoded_body
      >>> @load_urlencoded_body
      ... def handler(event, context):
      ...     return event['body']['foo']
      >>> handler({'body': 'foo=spam&bar=answer&bar=42'}, object())
      ['spam']

    note that ``event['body']`` is already a dictionary and didn't have to
    explicitly be parsed.
    """

    @wraps(handler)
    def wrapper(event, context):
        if isinstance(event.get("body"), str):
            try:
                event["body"] = parse_qs(event["body"])
            except Exception as exception:
                if hasattr(context, "serverless_sdk"):
                    context.serverless_sdk.capture_exception(exception)
                return {"statusCode": 400, "body": "BAD REQUEST"}
        return handler(event, context)

    return wrapper


def no_retry_on_failure(handler):
    """
    AWS Lambda retries scheduled lambdas that don't execute succesfully.

    This detects this by storing requests IDs in memory and exiting early on
    duplicates. Since this is in memory, don't use it on very frequently
    scheduled lambdas. It logs a critical message then exits with a statusCode
    of 200 to avoid further
    retries.

    Usage::

      >>> import logging, sys
      >>> from lambda_decorators import no_retry_on_failure, logger
      >>> logger.addHandler(logging.StreamHandler(stream=sys.stdout))
      >>> @no_retry_on_failure
      ... def scheduled_handler(event, context):
      ...     return {'statusCode': 500}
      >>> class Context:
      ...     aws_request_id = 1
      >>> scheduled_handler({}, Context())
      {'statusCode': 500}
      >>> scheduled_handler({}, Context())
      Retry attempt on request id 1 detected.
      {'statusCode': 200}

    """
    seen_request_ids = set()

    @wraps(handler)
    def wrapper(event, context):
        if context.aws_request_id in seen_request_ids:
            logger.critical(
                "Retry attempt on request id %s detected.", context.aws_request_id
            )
            return {"statusCode": 200}
        seen_request_ids.add(context.aws_request_id)
        return handler(event, context)

    return wrapper


def ssm_parameter_store(*parameters):
    """
    Get parameters from the `AWS SSM Parameter Store <https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-paramstore.html>`_.

    Secrets are added to a dictionary named ``ssm_params`` on the context object.

    This requires your lambda to have the ``ssm:GetParameters`` permission on for requested parameters and
    ``kms:Decrypt`` for any keys used to encrypt the parameters.

    Usage::

      >>> from lambda_decorators import ssm_parameter_store
      >>> @ssm_parameter_store('/dschep/test')
      ... def param_getter(event, context):
      ...     return context.parameters
      >>> class Context:
      ...     pass
      >>> param_getter({}, Context())
      {'/dschep/test': 'f00b4r'}

    For more advanced SSM use, see `ssm-cache <https://github.com/alexcasalboni/ssm-cache-python>`_

    """
    # support old list as 1st argument invocation style
    if len(parameters) == 1 and not isinstance(parameters[0], basestring):
        parameters = parameters[0]

    def wrapper_wrapper(handler):
        @wraps(handler)
        def wrapper(event, context):
            ssm = boto3.client("ssm")
            if not hasattr(context, "parameters"):
                context.parameters = {}
            for parameter in ssm.get_parameters(Names=parameters, WithDecryption=True)[
                "Parameters"
            ]:
                context.parameters[parameter["Name"]] = parameter["Value"]

            return handler(event, context)

        return wrapper

    return wrapper_wrapper


def secrets_manager(*secret_names):
    """
    Get secrets from the `AWS Secrets Manager <https://aws.amazon.com/secrets-manager/>`_.

    Secrets are added to a dictionary named ``secrets`` on the context object.

    This requires your lambda to have the ``secretsmanager:GetSecretValue`` permission for the
    requested secret and ``kms:Decrypt`` for any keys used to encrypt the secrets.

    Usage::

      >>> from lambda_decorators import secrets_manager
      >>> @secrets_manager('dschep/test')
      ... def secret_getter(event, context):
      ...     return context.secrets
      >>> class Context:
      ...     pass
      >>> secret_getter({}, Context())
      {'dschep/test': {'foo': 'b4r', 'floo': 'b4z'}}

    """

    def wrapper_wrapper(handler):
        @wraps(handler)
        def wrapper(event, context):
            if not hasattr(context, "secrets"):
                context.secrets = {}
            for secret_name in secret_names:
                secret_value = boto3.client(
                    service_name="secretsmanager"
                ).get_secret_value(SecretId=secret_name)
                if "SecretString" in secret_value:
                    context.secrets[secret_name] = json.loads(
                        secret_value["SecretString"]
                    )
                else:
                    context.secrets[secret_name] = secret_value["SecretBinary"]

            return handler(event, context)

        return wrapper

    return wrapper_wrapper


def secret_manager(secret_name):
    """
    Get a secret value from the AWS Secret Manager.

    .. deprecated:: 0.3
    Use the better spelled secrets_manager
    """
    return secrets_manager(secret_name)
