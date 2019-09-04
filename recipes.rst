Recipes and other decorators for lambda handlers
================================================

PostgreSQL db client
--------------------

Here is a sample decorator I wrote for a little side project that connects to a PostgreSQL database
and add the connection to the context object:

.. code:: python

    import os

    import boto3
    import records
    from lambda_decorators import LambdaDecorator


    class database(LambdaDecorator):
        def before(self, event, context):
            self.db = records.Database(boto3.client('ssm').get_parameter(
                Name='db_url', WithDecryption=True)['Parameter']['Value'])
            context.db = self.db

            return event, context

        def after(self, response):
            self.db.close()
            return response

        def on_exception(self, exception):
            if hasattr(self, 'db'):
                self.db.close()
            raise exception

Then, when defining your handler:

.. code:: python

    from database import database

    @database
    def handler(event, context):
        context.db.query('select 1')
        return {}


Raven/Sentry configuration
----------------------------
See `raven-python-lambda <https://github.com/Netflix-Skunkworks/raven-python-lambda>`_ for an
example of a library for aws lambda that also uses a decorator to configure logging to use
Raven/Sentry.
