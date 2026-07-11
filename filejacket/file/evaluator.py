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
from __future__ import annotations

from importlib import import_module
from json import loads

__all__ = ["evaluate_serializer_class_from_dict_or_json"]

from ..exception import SerializerError


DEFAULT_SERIALIZER_ATTRIBUTES = (
    '__serializer__',
    'serializer.class'
)
"""
Registry for the default attributes for searching the serializer class.   
"""


def find_source_in_dict_or_json(
    data: str | dict, default_serializer_attributes: tuple | list | set = DEFAULT_SERIALIZER_ATTRIBUTES
) -> str:
    """
    Function to find the serializer attribute in JSON string or dictionary.
    """

    match data:
        case str():
            data = loads(data)
        case dict():
            ...
        case _:
            raise SerializerError(
                "Content to be deserializer not found in evaluator `find_source_in_dict_or_json`. "
                "The evaluator only accept str or dict."
            )

    search_data = data
    for attribute in default_serializer_attributes:
        for part in attribute.split('.'):
            search_data = search_data[part] if part in search_data else data

        if search_data != data:
            break

    # We should return only if result is a class string
    if isinstance(search_data, str):
        return search_data

    raise SerializerError(
        "Attribute to be deserializer not found in evaluator `find_source_in_dict_or_json`."
    )


def evaluate_serializer_class_from_dict_or_json(
    data: str | dict, default_serializer_attributes: tuple | list | set = DEFAULT_SERIALIZER_ATTRIBUTES
) -> type:
    """
    Function to find and evaluate the serializer attribute in JSON string or dictionary.
    """
    try:
        class_path = find_source_in_dict_or_json(data=data, default_serializer_attributes=default_serializer_attributes)
        module, name = class_path.rsplit('.', 1)
        return getattr(import_module(module), name)
    except Exception as e:
        raise SerializerError(
            f"Evaluator `evaluate_serializer_class_from_dict_or_json` could not import serializer class: {e}"
        ) from e
