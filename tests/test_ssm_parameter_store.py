from lambda_decorators import ssm_parameter_store

def test_single_param():
    @ssm_parameter_store('/dschep/test')
    def handler(event, context):
        return context.parameters

    class Context:
        pass
    assert handler({}, Context()) == {'/dschep/test': 'f00b4r'}

def test_multi_param():
    @ssm_parameter_store('/dschep/test', '/dschep/test2')
    def handler(event, context):
        return context.parameters

    class Context:
        pass
    assert handler({}, Context()) == {'/dschep/test': 'f00b4r', '/dschep/test2': 'baz'}

def test_aray_param():
    @ssm_parameter_store(['/dschep/test', '/dschep/test2'])
    def handler(event, context):
        return context.parameters

    class Context:
        pass
    assert handler({}, Context()) == {'/dschep/test': 'f00b4r', '/dschep/test2': 'baz'}
