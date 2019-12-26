from datetime import datetime
from mock import MagicMock

from lambda_decorators import load_json_body


def test_load_json_body_ok():
    handler = MagicMock()
    decorated_handler = load_json_body(handler)
    context = MagicMock()
    decorated_handler({"body": '{"foo":"bar"}'}, context)
    handler.assert_called_with({"body": {"foo": "bar"}}, context)


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
    handler = MagicMock()
    decorated_handler = load_json_body(object_hook=datetime_decoder)(handler)
    context = MagicMock()
    decorated_handler({"body": '{"foo":"2019-01-01T00:00:00"}'}, context)
    handler.assert_called_with({"body": {"foo": datetime(2019, 1, 1)}}, context)
