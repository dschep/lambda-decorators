from unittest.mock import MagicMock, call

import lambda_decorators


def test_multiple_lambda_decorator_subclasses():
    mock = MagicMock()
    class first(lambda_decorators.LambdaDecorator):
        def before(self, event, context):
            mock('first')
            return event, context
    class second(lambda_decorators.LambdaDecorator):
        def before(self, event, context):
            mock('second')
            return event, context

    @first
    @second
    def handler(event, context):
        return 'foobar'

    assert handler({}, MagicMock()) == 'foobar'
    assert len(mock.mock_calls) == 2
    assert mock.mock_calls[0] == call('first')
    assert mock.mock_calls[1] == call('second')
