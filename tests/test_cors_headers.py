from mock import MagicMock

from lambda_decorators import cors_headers


def test_cors_default():
    @cors_headers
    def hello(example, context):
        return {'body': 'foobar'}
    assert hello({}, MagicMock()) == {
        'body': 'foobar',
        'headers': {'Access-Control-Allow-Origin': '*'},
    }


def test_cors_noarg():
    @cors_headers()
    def hello(example, context):
        return {'body': 'foobar'}
    assert hello({}, MagicMock()) == {
        'body': 'foobar',
        'headers': {'Access-Control-Allow-Origin': '*'},
    }


def test_cors_positonal_origin():
    @cors_headers('https://example.com')
    def hello(example, context):
        return {'body': 'foobar'}
    assert hello({}, MagicMock()) == {
        'body': 'foobar',
        'headers': {'Access-Control-Allow-Origin': 'https://example.com'},
    }


def test_cors_keyword_origin():
    @cors_headers(origin='https://example.com')
    def hello(example, context):
        return {'body': 'foobar'}
    assert hello({}, MagicMock()) == {
        'body': 'foobar',
        'headers': {'Access-Control-Allow-Origin': 'https://example.com'},
    }


def test_cors_keyword_creds():
    @cors_headers(credentials=True)
    def hello(example, context):
        return {'body': 'foobar'}
    assert hello({}, MagicMock()) == {
        'body': 'foobar',
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
    }


def test_cors_keyword_origin_and_creds():
    @cors_headers(origin='https://example.com', credentials=True)
    def hello(example, context):
        return {'body': 'foobar'}
    assert hello({}, MagicMock()) == {
        'body': 'foobar',
        'headers': {
            'Access-Control-Allow-Origin': 'https://example.com',
            'Access-Control-Allow-Credentials': True,
        },
    }


def test_cors_empty():
    @cors_headers
    def hello(example, context):
        return
    assert hello({}, MagicMock()) == {
        'headers': {'Access-Control-Allow-Origin': '*'},
    }
