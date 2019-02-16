from mock import MagicMock

from lambda_decorators  import load_json_queryStringParameters


def test_queryStringParameters_empty():
    @load_json_queryStringParameters
    def hello(example, context):
        return example
    assert hello({}, MagicMock()) == {}


def test_queryStringParameters_no_parameters():
    @load_json_queryStringParameters
    def hello(example, context):
        return example

    query_parameters = '{}'
    result = {}
    assert hello({'queryStringParameters': query_parameters},
                  MagicMock()) == {'queryStringParameters': result}


def test_queryStringParameters_1level_str():
    @load_json_queryStringParameters
    def hello(example, context):
        return example

    query_parameters = '{"foo": "bar"}'
    result = {"foo": "bar"}
    assert hello({'queryStringParameters': query_parameters},
                  MagicMock()) == {'queryStringParameters': result}



def test_queryStringParameters_1level_list():
    @load_json_queryStringParameters
    def hello(example, context):
        return example

    query_parameters = '{"foo": ' + str(["bar1", "bar2"]) + '}'
    result = {"foo": ["bar1", "bar2"]}
    assert hello({'queryStringParameters': query_parameters},
                  MagicMock()) == {'queryStringParameters': result}


def test_queryStringParameters_2level_dict():
    @load_json_queryStringParameters
    def hello(example, context):
        return example

    query_parameters = '{"foo": {"bar1": "baz1", "bar2": "baz2"}}'
    result = {"foo": {"bar1": "baz1", "bar2": "baz2"}}
    assert hello({'queryStringParameters': query_parameters},
                  MagicMock()) == {'queryStringParameters': result}

def test_queryStringParameters_2level_list():
    @load_json_queryStringParameters
    def hello(example, context):
        return example

    query_parameters = '{"foo": {"bar1": ' + str(["(1.0)", "(1, 2)"]) + ', "bar2": "baz2"}}'
    result = {"foo": {"bar1": [(1.0), (1, 2)], "bar2": "baz2"}}
    assert hello({'queryStringParameters': query_parameters},
                  MagicMock()) == {'queryStringParameters': result}


def test_queryStringParameters_2level_None_bool():
    @load_json_queryStringParameters
    def hello(example, context):
        return example

    query_parameters = '{"foo": {"bar1": ' + str(["(1.0)", "(1, 2)"]) + ', "bar2": ' + str(("None", "True")) + '}}'
    result = {"foo": {"bar1": [(1.0), (1, 2)], "bar2": (None, True)}}
    assert hello({'queryStringParameters': query_parameters},
                  MagicMock()) == {'queryStringParameters': result}




