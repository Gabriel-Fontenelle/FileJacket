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

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..file import BaseFile


__all__: list[str] = ["TransmuterEngine"]


class TransmuterEngine:
    """
    Class helper for converting values useful for serializer/deserializer classes that made use of it in its declarative
     attributes.
    This class uses __set_name__ as a way to organize the code and reference to those classes.
    """

    def __set_name__(self, owner, name):
        """
        Method to automatically set the attribute name in which it was declared and register it in owner list of attributes.
        The owner list of attributes will be created at the first call of a class that inherent BaseTransmuter.

        Usage:

        ```
        class Serializer:
            my_attribute = BaseTransmuter()

        ```
        """

        self.attribute_name = name
        self.serializer = owner

        if hasattr(owner, "transmuters"):
            owner.transmuters.add(name)
        else:
            owner.transmuters = {name}

    def from_data(self, value: Any) -> Any:
        """
        Method for the transmuter to serialize a value.
        This Method should be override in child classes.
        """
        raise NotImplementedError(
            "The method `from_data` must be implemented in child class."
        )

    def to_data(self, value: Any, reference: BaseFile) -> Any:
        """
        Method for the transmuter to deserialize a value.
        This Method should be override in child classes.
        """
        raise NotImplementedError(
            "The method `to_data` must be implemented in child class."
        )
