# SPDX-FileCopyrightText: 2023 osfanbuff63
#
# SPDX-License-Identifier: Apache-2.0

"""Extends pathlib to work with json more easily."""
from pathlib import Path


class PathExt(Path):
    """Extends pathlib to work with json more easily."""

    def __init__(self, *args) -> None:
        """Initalize."""
        super().__init__(*args)

    def read(self):
        """An alias for pathlib.read_bytes."""
        return self.read_bytes()

    def write(self, *args):
        """An alias for pathlib.write_text."""
        return self.write_text(*args)
