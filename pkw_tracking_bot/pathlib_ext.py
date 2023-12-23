# SPDX-FileCopyrightText: 2023 osfanbuff63
#
# SPDX-License-Identifier: Apache-2.0

"""Extends pathlib to work with json more easily."""
from pathlib import Path


class PathExt(Path):
    def __init__(self, *args) -> None:
        super().__init__(*args)

    def read(self):
        return self.read_bytes()

    def write(self, *args):
        return self.write_text(*args)
