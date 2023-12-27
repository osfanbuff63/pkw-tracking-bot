# SPDX-FileCopyrightText: 2023 osfanbuff63
#
# SPDX-License-Identifier: Apache-2.0


class TimeException(Exception):
    """The time given was invalid or slower than the current time."""


class CourseException(Exception):
    """The course given was invalid."""


class AdvancedBoolException(Exception):
    """The advanced value was not a boolean."""
