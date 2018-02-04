from lambda_decorators import json_schema_validator


schema = {
    'type': 'object',
    'properties': {
        'price': {'type': 'number'},
    },
}


def test_request_schema_success():
    @json_schema_validator(request_schema=schema)
    def handler(event, context):
        return event['price']

    assert handler({'price': 1}, object()) == 1


def test_request_schema_error():
    @json_schema_validator(request_schema=schema)
    def handler(event, context):
        return event['price']

    assert handler({'price': 'foo'}, object()) == {
        'statusCode': 400,
        'body': "RequestValidationError: 'foo' is not of type 'number'",
    }


def test_response_schema_success():
    @json_schema_validator(response_schema=schema)
    def handler(event, context):
        return {'price': 1}

    assert handler({}, object()) == {'price': 1}


def test_response_schema_error():
    @json_schema_validator(response_schema=schema)
    def handler(event, context):
        return {'price': 'foo'}

    assert handler({}, object()) == {
        'statusCode': 500,
        'body': "ResponseValidationError: 'foo' is not of type 'number'",
    }
