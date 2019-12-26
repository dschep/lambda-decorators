from datetime import datetime
from mock import MagicMock

from lambda_decorators import dump_json_body


def test_dump_json_body_ok():
    @dump_json_body
    def hello(example, context):
        return {"statusCode": 200, "body": {"foobar": 42}}
    assert hello({}, MagicMock()) == {"statusCode": 200, "body": '{"foobar": 42}'}

def test_dump_json_body_no_response():
    @dump_json_body
    def hello(example, context):
        return
    assert hello({}, MagicMock()) == None

def test_dump_json_body_error():
    @dump_json_body
    def hello(example, context):
        raise Exception("barf")
    assert hello({}, MagicMock()) == {"statusCode": 500, "body": "barf"}

def datetime_json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()

testtime = datetime(2019, 1, 1)

def test_dump_json_body_ok_w_args():
    @dump_json_body(default=datetime_json_default)
    def hello(example, context):
        return {"statusCode": 200, "body": {"foobar": testtime}}
    assert hello({}, MagicMock()) == {"statusCode": 200, "body": '{"foobar": "2019-01-01T00:00:00"}'}

def test_dump_json_body_no_response_w_args():
    @dump_json_body(default=datetime_json_default)
    def hello(example, context):
        return
    assert hello({}, MagicMock()) == None

def test_dump_json_body_error_w_args():
    @dump_json_body(default=datetime_json_default)
    def hello(example, context):
        raise Exception("barf")
    assert hello({}, MagicMock()) == {"statusCode": 500, "body": "barf"}
