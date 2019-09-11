from mock import MagicMock

from lambda_decorators import json_http_resp


def test_json_http_resp_no_response():
    @json_http_resp
    def hello(example, context):
        return
    assert hello({}, MagicMock()) == {"statusCode": 200, "body": "null"}
