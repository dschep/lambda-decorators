
lambda_decorators
*****************

🐍λ✨ - A collection of useful decorators for working with AWS Lambda.


Quick example
=============

::

   # handler.py

   from lambda_decorators import parse_json_body

   @cors
   @json_http_resp
   @load_json_body
   handler(event, context):
       return {'msg': f"hello {event['body']['name']}"}


Install
=======

::

   pip install lambda_decorators


Included Decorators:
====================

..

   * ``async_handler()`` - support for async handlers

   * ``cors()`` - automatic injection of CORS headers

   * ``dump_json_body()`` - auto-serialization of http body to JSON

   * ``json_http_resp()`` - automatic serialization of python object
     to HTTP JSON response

   * ``load_json_body()`` - auto-deserialize of http body from JSON

   * ``no_retry_on_failure()`` - detect and stop retry attempts for
     scheduled lambdas

See each individual decorator for specific usage details.

**lambda_decorators.async_handler(handler)**

   This decorator allows for use of async handlers by automatically
   running them in an event loop.

   Usage:

   ::

      @async_handler
      async def handler(event, context):
          return await foobar()

**lambda_decorators.cors(handler_or_origin)**

   Automatically injects Access-Control-Allow-Origin headers to http
   responses.

   Usage:

   ::

      @cors
      def hello(example, context):
          return {'body': 'foobar'}
      # or with custom domain
      @cors('https://example.com')
      def hello_custom_origin(example, context):
          return {'body': 'foobar'}

   the ``hello`` example returns

   ::

      {'body': 'foobar', 'headers': {'Access-Control-Allow-Origin': '*'}}

**lambda_decorators.dump_json_body(handler)**

   Automatically serialize response bodies with json.dumps.

   Returns a 500 error if the response cannot be serialized

   Usage:

   ::

      @dump_json_body
      @def handler(event, context):
          return {'statusCode': 200, 'body': {'hello': 'world'}}

   in this example, the decorators handler returns:

   ::

      {'statusCode': 200, 'body': '{"hello": "world"}'}

**lambda_decorators.json_http_resp(handler)**

   Automatically serialize return value to the body of a successfull
   HTTP response.

   Returns a 500 error if the response cannot be serialized

   Usage:

   ::

      @json_http_resp
      def handler(event, context):
          return {'hello': 'world'}

   in this example, the decorated handler returns:

   ::

      {'statusCode': 200, 'body': '{"hello": "world"}'}

**lambda_decorators.load_json_body(handler)**

   Automatically deserialize event bodies with json.loads.

   Automatically returns a 400 BAD REQUEST if there is an error while
   parsing.

   Usage:

   ::

      @load_json_body
      def handler(event, context):
          return event['body']['foobar']

   note that event[‘body’] is already a dictionary and didn’t have to
   explicitly be parsed.

**lambda_decorators.no_retry_on_failure(handler)**

   AWS Lambda retries scheduled lambdas that don’t execute
   succesfully.

   This detects this by storing requests IDs in memory and exiting
   early on duplicates. Since this is in memory, don’t use it on very
   frequently scheduled lambdas. It raises a ``RuntimeError``
