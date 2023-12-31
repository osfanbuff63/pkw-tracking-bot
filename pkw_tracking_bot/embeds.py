# SPDX-FileCopyrightText: 2023 osfanbuff63
#
# SPDX-License-Identifier: Apache-2.0

from typing import Optional

from discord import Embed

from .logger import logger


def error_embed(error, extra_info: Optional[str]) -> Embed:
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
    if users == 0:
        description = "*No times have been submitted on this course yet.*"
    else:
        description = f"1. <@{best_time_user}>: **{all_times[best_time_user]}**\n"
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
