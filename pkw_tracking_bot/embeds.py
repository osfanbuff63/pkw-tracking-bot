# SPDX-FileCopyrightText: 2023 osfanbuff63
#
# SPDX-License-Identifier: Apache-2.0
"""The embed constructors."""

from typing import Optional

import arrow
from discord import Embed, User, Member

from .database import Database
from .logger import logger
from pathlib import Path

database = Database(Path("database.toml"))


def error_embed(error, extra_info: Optional[str]) -> Embed:
    """An embed to be used when an error needs to be displayed.

    Args:
        error (_type_): The error.
        extra_info (Optional[str]): A user-friendly explanation of the error.

    Returns:
        Embed: The embed.
    """
    if not extra_info:
        extra_info = "No further information was available."
    embed = Embed(
        type="rich",
        title="Error",
        color=16711680,
        description=f"An error occurred while running this command: {extra_info}\n\nTechnical details: {error}",
    )
    return embed


def success_embed(description: str) -> Embed:
    """An embed to be used for a successful action.

    Args:
        description (str): The text of the embed.

    Returns:
        Embed: The embed.
    """
    embed = Embed(
        type="rich",
        title="Success",
        color=65280,
        description=description,
    )
    return embed


def leaderboard_embed(
    all_times: dict, best_time: str, registered_users: list, course: int
) -> Embed:
    """The leaderboard embed.

    Args:
        all_times (dict): All the times to display.
        best_time (str): The best time.
        registered_users (list): All the registered users.
        course (int): The course for all the data above.

    Returns:
        Embed: The embed.
    """
    all_times_1 = all_times.copy()
    registered_users_1 = registered_users.copy()
    logger.debug(f"All times: {str(all_times)}")
    logger.debug(f"Registered users (embeds): {registered_users}")
    users = 0
    for user in registered_users_1:
        if all_times[user] == best_time and all_times[user] != "99:99.99":
            best_time_user = user
            registered_users_1.remove(user)
            all_times_1.pop(user)
            logger.debug(f"First place user: {user}")
            logger.debug(f"Current all times (1): {str(all_times)}")
            logger.debug(f"Current registered users (1): {str(registered_users_1)}")
            second_best_time = min(all_times_1.values())
            users += 1
        else:
            continue
    try:
        for user in registered_users_1:
            if all_times[user] == second_best_time and all_times[user] != "99:99.99":
                second_best_time_user = user
                registered_users_1.remove(user)
                all_times_1.pop(user)
                logger.debug(f"Second place user: {user}")
                logger.debug(f"Current all times (2): {str(all_times)}")
                users += 1
            else:
                if all_times[user] != "99:99.99":
                    third_best_time_user = user
                    users += 1
                continue
    except UnboundLocalError:
        logger.exception("Caught UnboundLocalError!")
    now = arrow.now(tz="America/New_York")
    timestamp = arrow.get(
        now.year if now.month < 12 else now.year + 1,
        now.month + 1 if now.month < 12 else 1,
        1,
        10,
        0,
        0,
    ).int_timestamp
    # convert timestamp to an int because Discord doesn't accept decimal times
    description = f"**Courses reset <t:{timestamp}:R>.**\n\n"
    if users == 0:
        description += "*No times have been submitted on this course yet.*"
    else:
        description += f"1. <@{best_time_user}>: **{all_times[best_time_user]}**\n"
        try:
            if isinstance(second_best_time_user, int):
                description += f"2. <@{second_best_time_user}>: **{all_times[second_best_time_user]}**\n"
            if isinstance(third_best_time_user, int):
                description += (
                    f"3. <@{third_best_time_user}>: {all_times[third_best_time_user]}"
                )
        except UnboundLocalError:
            logger.exception("Caught UnboundLocalError.")
            pass
    embed = Embed(
        color=65280,
        type="rich",
        description=description,
        title=f"Leaderboard for Course {course}",
    )
    return embed


def stats_embed(user: User | Member, year: int, month: int) -> Embed:
    """Get the stats for the archive viewer.

    Args:
        user (User | Member): The user to look up.
        year (int): The year to look up.
        month (int): The month to look up.

    Returns:
        Embed: The embed.
    """
    id = user.id
    # dict of months, with corresponding humanified names
    months = {
        "1": "January",
        "2": "February",
        "3": "March",
        "4": "April",
        "5": "May",
        "6": "June",
        "7": "July",
        "8": "August",
        "9": "September",
        "10": "October",
        "11": "November",
        "12": "December",
        # repeat the first 9 with ones with leading zeros, just in case
        "01": "January",
        "02": "February",
        "03": "March",
        "04": "April",
        "05": "May",
        "06": "June",
        "07": "July",
        "08": "August",
        "09": "September",
    }
    database = Database(Path(f"./database_archive/{year}/{month}/database.toml"))
    stats = database.get(str(id))
    logger.debug(f"stats: {stats}")
    text = f"### Stats for <@{id}>\n\n"
    text += f"**Course 1**: {stats["course_1"].get("time") if stats["course_1"].get("time") != "99:99.99" else "*No time submitted*"}"
    text += f"{" (Advanced Completion)" if stats["course_1"].get("advanced") else ""}\n"
    text += f"**Course 2**: {stats["course_2"].get("time") if stats["course_2"].get("time") != "99:99.99" else "*No time submitted*"}"
    text += f"{" (Advanced Completion)" if stats["course_2"].get("advanced") else ""}\n"
    text += f"**Course 3**: {stats["course_3"].get("time") if stats["course_3"].get("time") != "99:99.99" else "*No time submitted*"}"
    text += f"{" (Advanced Completion)" if stats["course_3"].get("advanced") else ""}\n"
    text += f"**Course 4**: {stats["course_4"].get("time") if stats["course_4"].get("time") != "99:99.99" else "*No time submitted*"}"
    text += f"{" (Advanced Completion)" if stats["course_4"].get("advanced") else ""}\n"
    text += f"**Course 5**: {stats["course_5"].get("time") if stats["course_5"].get("time") != "99:99.99" else "*No time submitted*"}"
    text += f"{" (Advanced Completion)" if stats["course_5"].get("advanced") else ""}\n"
    text += f"**Course 6**: {stats["course_6"].get("time") if stats["course_6"].get("time") != "99:99.99" else "*No time submitted*"}"
    text += f"{" (Advanced Completion)" if stats["course_6"].get("advanced") else ""}\n"
    text += f"**Course 7**: {stats["course_7"].get("time") if stats["course_7"].get("time") != "99:99.99" else "*No time submitted*"}"
    text += f"{" (Advanced Completion)" if stats["course_7"].get("advanced") else ""}\n"
    embed = Embed(
        color=65280,
        type="rich",
        description=text,
        # title=f"**Stats for {months[f"{month}"]} {year}**",
    )
    return embed
