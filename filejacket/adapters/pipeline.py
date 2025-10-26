"""
Handler is a package for creating files in an object-oriented way,
allowing extendability to any file system.

Copyright (C) 2021 Gabriel Fontenelle Senno Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Should there be a need for contact the electronic mail
`filejacket <at> gabrielfontenelle.com` can be used.
"""
# first-party
from __future__ import annotations

from inspect import isclass
from typing import TYPE_CHECKING, Type, Any

from ..engines.pipeline import PipelineEngine, Processor
from ..exception import ImproperlyConfiguredPipeline, ValidationError, ImproperlyConfiguredFile, PipelineError

if TYPE_CHECKING:
    from ..file import BaseFile

__all__ = [
    "PipelineContent",
    "PipelineOrderedDependency",
    "PipelineSequential",
    "ProcessorContent"
]


class PipelineSequential(PipelineEngine):
    ...


class PipelineParallel(PipelineEngine):
    pass


class PipelineOrderedDependency(PipelineEngine):
    """
    Class to initiate an ordered by dependency pipeline.
    """

    def load_processor_candidates(self):
        """
        Method to convert the processors candidates, informed at the class instantiator, to processors ready for use
        in the run method.
        The method accepts both string of a class` path and the class directly as the candidate for processor.

        This method will add attributes for the pipeline in the processor and validate if processor has the
        required attributes and methods for using it at `run`.

        This override will reorder the processors candidates according to the `dependencies` attribute.

        If there is a circular dependency it will raise ` toposort.CircularDependencyError` that inherent from
        `ValueError`.

        TODO: Support branching dependencies where a processor can depend in two or more dependencies that have the
              same hierarchic.
        """
        from toposort import toposort_flatten

        processor = self.processor
        processors = {}
        processors_to_sort = {}

        for candidate in self.processors_candidate:
            # Get parameters if there is any besides processor in list or tuple.
            if isinstance(candidate, (tuple, list)):
                if len(candidate) > 2:
                    raise ImproperlyConfiguredPipeline(
                        f"Invalid processor candidate {candidate}. "
                        "The processor candidate should not have more than two position"
                        " element."
                    )

                parameters_to_override, candidate_path = candidate[1], candidate[0]
            else:
                parameters_to_override, candidate_path = {}, candidate

            # Check if a class was informed instead of path.
            if isclass(candidate_path):
                candidate_class = candidate_path
            else:
                # Convert the dotted path to a class type.
                candidate_class = processor.import_class(candidate_path)

            # Add additional attributes with option to override some parameters.
            processor_object = processor.instantiate(
                candidate_class, parameters=parameters_to_override
            )

            # Validate that all attributes and methods required for `run` exist in the class.
            # A ValidationError will be raised if there is a problem.
            processor.validate(processor_object)

            processor_path = f"{processor_object.__module__}.{processor_object.__name__}"

            processors[processor_path] = processor_object

            processors_to_sort[
                f"{processor_object.__module__}.{processor_object.__name__}"
            ] = processor_object.dependencies

        sorted_processors = toposort_flatten(processors_to_sort)

        # Add the finished processor to the pipeline.
        try:
            self.pipeline_processors = [
                processors[processor_path]
                for processor_path in sorted_processors
            ]
        except KeyError as e:
            raise ImproperlyConfiguredPipeline(f"The dependency {e} is missing from the pipeline.")


class ProcessorContent(Processor):
    """
    Processor to validate classes for use with PipelineContent.
    """

    @classmethod
    def validate(cls, processor: object):
        """
        Method to validate if the processor object has the necessary attributes to allow the pipeline to be run.
        """
        # Check if processor has process_chunk and finish_process

        # Validate if processor has the method `process` to allow it to be used in pipeline.
        if not hasattr(processor, "process_block"):
            raise ValidationError(
                f"Class {processor.__class__.__name__} should implement the method `process_block` to be a "
                f"valid processor content class."
            )

        if not hasattr(processor, "finish_process"):
            raise ValidationError(
                f"Class {processor.__class__.__name__} should implement the attribute `finish_process` to be a "
                f"valid processor content class."
            )


class PipelineContent(PipelineEngine):
    """
    Class to initiate a pipeline that will run the content of object_to_process instead of the object.
    This class doesn't implement the stop pipeline resource as it cannot stop while the whole iterator of
    content is not consumed.
    """

    processor: Type[Processor] = ProcessorContent

    def run(self, object_to_process: BaseFile, **parameters: Any) -> None:
        """
        Method to run the entire pipeline.
        The processor will define if method will stop or not the pipelines.

        Not all pipelines are required to run this method, as example, Hasher Pipeline avoid
        its use when loading hashes from files.

        This method evaluate the processors.
        """
        if not hasattr(object_to_process, "_option") or (
            "FileOption" != object_to_process._option.__class__.__name__
            and "FileOption" not in (base.__name__ for base in object_to_process._option.__class__.__bases__)
        ):
            raise ImproperlyConfiguredFile(
                f"Object {type(object_to_process)} don`t have a option attribute of instance"
                "FileOption to allow the pipeline to run properly."
            )

        pipeline_raises_exception = object_to_process._option.pipeline_raises_exception

        # For each processor
        ran: int = 0
        result: bool | None = None
        errors_found: list = []

        if not self.pipeline_processors:
            self.load_processor_candidates()

        processors_initialized = [
            processor(object_to_process=object_to_process, **parameters)
            for processor in self.__iter__()
        ]

        # Using iter here allow for override of __iter__ to affect the running process.
        for block in object_to_process.content_as_iterator:
            for processor in processors_initialized:
                try:
                    processor.process_block(
                        block, **parameters
                    )
                except Exception as e:
                    message = f"An error occurred while running process {type(processor)} for block: {e}"

                    if pipeline_raises_exception:
                        raise PipelineError(message) from e

                    errors_found.append(message)

        for processor in processors_initialized:
            try:
                result = processor.finish_process(object_to_process=object_to_process, **parameters)
                ran += 1

            except Exception as e:
                message = f"An error occurred while running process {type(processor)}: {e}"

                if pipeline_raises_exception:
                    raise PipelineError(message) from e

                errors_found.append(message)

        # register statical data about pipelines.
        self.processors_ran = ran
        self.last_result = result
        self.errors = errors_found
