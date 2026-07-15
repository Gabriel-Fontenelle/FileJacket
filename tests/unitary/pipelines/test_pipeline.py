from filejacket.engines.pipeline import Processor, PipelineEngine


def test_class_processor_has_required_attribute():
    assert hasattr(Processor, 'import_class')
    assert hasattr(Processor, 'instantiate')
    assert hasattr(Processor, 'validate')
    assert hasattr(Processor, '_set_default_attributes')


def test_class_pipeline_has_required_attribute():
    assert hasattr(PipelineEngine, '__init__')
    assert hasattr(PipelineEngine, '__getitem__')
    assert hasattr(PipelineEngine, '__iter__')
    assert hasattr(PipelineEngine, '__serialize__')
    assert hasattr(PipelineEngine, 'load_processor_candidates')
    assert hasattr(PipelineEngine, 'run')
