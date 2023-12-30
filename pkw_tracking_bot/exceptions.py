# SPDX-FileCopyrightText: 2023 osfanbuff63
#
# SPDX-License-Identifier: Apache-2.0
from discord import errors as discord_errors


class TimeException(Exception):
    """The time given was invalid or slower than the current time."""


class CourseException(Exception):
    """The course given was invalid."""


class AdvancedBoolException(Exception):
    """The advanced value was not a boolean."""


class DiscordLibException(discord_errors.DiscordException):
    """The discord.py library did not give the expected value."""
