from mock import MagicMock

from lambda_decorators import dump_json_body


def test_dump_json_body_no_response():
    @dump_json_body
    def hello(example, context):
        return
    assert hello({}, MagicMock()) is None
