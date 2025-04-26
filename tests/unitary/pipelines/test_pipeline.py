from filejacket.pipelines import Processor, Pipeline


def test_class_processor_has_required_attribute():
    assert hasattr(Processor, 'import_class')
    assert hasattr(Processor, 'instantiate')
    assert hasattr(Processor, 'validate')
    assert hasattr(Processor, '_set_default_attributes')


def test_class_pipeline_has_required_attribute():
    assert hasattr(Pipeline, '__init__')
    assert hasattr(Pipeline, '__getitem__')
    assert hasattr(Pipeline, '__iter__')
    assert hasattr(Pipeline, '__serialize__')
    assert hasattr(Pipeline, 'load_processor_candidates')
    assert hasattr(Pipeline, 'run')
