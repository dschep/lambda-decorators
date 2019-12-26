from datetime import datetime
from mock import MagicMock

from lambda_decorators import load_json_body


def test_load_json_body_ok():
    @load_json_body
    def handler(event, context):
        assert event["body"] == {"foo": "bar"}
    handler({"body": '{"foo":"bar"}'}, MagicMock())


def datetime_decoder(d):
    if isinstance(d, list):
        pairs = enumerate(d)
    elif isinstance(d, dict):
        pairs = d.items()
    result = []
    for k,v in pairs:
        if isinstance(v, str):
            try:
                v = datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                try:
                    v = datetime.strptime(v, '%Y-%m-%d').date()
                except ValueError:
                    pass
        elif isinstance(v, (dict, list)):
            v = datetime_decoder(v)
        result.append((k, v))
    if isinstance(d, list):
        return [x[1] for x in result]
    elif isinstance(d, dict):
        return dict(result)


def test_load_json_body_w_args_ok():
    @load_json_body(object_hook=datetime_decoder)
    def handler(event, context):
        assert event["body"] == {"foo": datetime(2019, 1, 1)}
    handler({"body": '{"foo":"2019-01-01T00:00:00"}'}, MagicMock())
