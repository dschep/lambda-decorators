🐍λ✨ lambda-decorators -  A Python decorator library for AWS Lambda
====================================================================

Quick example
-------------
.. code:: python

    # handler.py

    from lambda_decorators import parse_json_body

    @parse_json_body
    handler(event, context):
      return event['body']['already deserialized json']
