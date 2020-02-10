from datetime import datetime
from mock import MagicMock

from lambda_decorators import json_http_resp


def test_json_http_resp_ok():
    @json_http_resp
    def hello(example, context):
        return {"foobar": 42}
    assert hello({}, MagicMock()) == {"statusCode": 200, "body": '{"foobar": 42}'}

def test_json_http_resp_no_response():
    @json_http_resp
    def hello(example, context):
        return
    assert hello({}, MagicMock()) == {"statusCode": 200, "body": "null"}

def test_json_http_resp_error():
    @json_http_resp
    def hello(example, context):
        raise Exception("barf")
    assert hello({}, MagicMock()) == {"statusCode": 500, "body": "barf"}

def datetime_json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()

testtime = datetime(2019, 1, 1)

def test_json_http_resp_ok_w_args():
    @json_http_resp(default=datetime_json_default)
    def hello(example, context):
        return {"foobar": testtime}
    assert hello({}, MagicMock()) == {"statusCode": 200, "body": '{"foobar": "2019-01-01T00:00:00"}'}

def test_json_http_resp_no_response_w_args():
    @json_http_resp(default=datetime_json_default)
    def hello(example, context):
        return
    assert hello({}, MagicMock()) == {"statusCode": 200, "body": "null"}

def test_json_http_resp_error_w_args():
    @json_http_resp(default=datetime_json_default)
    def hello(example, context):
        raise Exception("barf")
    assert hello({}, MagicMock()) == {"statusCode": 500, "body": "barf"}

def test_json_http_resp_w_status_code():
    @json_http_resp
    def hello(example, context):
        return {'foo': 'bar', 'statusCode': 403}
    assert hello({}, MagicMock()) == {"statusCode": 403, "body": '{"foo": "bar"}'}

def test_json_http_resp_w_list():
    @json_http_resp
    def hello(example, context):
        return [2,4,6]
    assert hello({}, MagicMock()) == {"statusCode": 200, "body": '[2, 4, 6]'}
