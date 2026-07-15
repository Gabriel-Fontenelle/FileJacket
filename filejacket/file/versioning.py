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

from typing import Any


__all__ = [
    "migrate_schema"
]


class MigrateBaseFileToVersion2:

    @classmethod
    def migrate(cls, data: dict[str, Any]) -> dict:
        """
        Method to migrate BaseFile version 1 to BaseFile version 2.
        In version 2 the _meta was changed to meta.
        In version 1 there is a bug where thumbnail metadata is registered a
        second time in extra_data.
        """
        # Fix metadata attribute
        if "_meta" in data:
            data["meta"] = data["_meta"].copy()
            del data["_meta"]

        # Fix thumbnail attribute being duplicated in extra_data
        if (
            "meta" in data
            and "thumbnail" in data["meta"]
            and "extra_data" in data["meta"]
            and "thumbnail" in data["meta"]["extra_data"]
        ):
            del data["meta"]["extra_data"]["thumbnail"]

        return data


MIGRATOR_REGISTRY = {
    1: MigrateBaseFileToVersion2,
}
"""
Registry for migrating between versions.
"""


def migrate_schema(data: dict, current_version: int, version_key: str = "__version__") -> dict:
    """
    Function to allow migration of multiple versions of serialized object.
    """
    version: str = data.get(version_key, "1")

    for x in range(int(version), current_version):
        migrator = MIGRATOR_REGISTRY.get(x).migrate(data)
        if not migrator:
            raise ValueError(f"Unsupported version: {version}")
        data = migrator.migrate(data)

    return data
