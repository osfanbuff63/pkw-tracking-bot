# SPDX-FileCopyrightText: 2023 osfanbuff63
#
# SPDX-License-Identifier: Apache-2.0
"""The main bot."""

import asyncio
import logging
import sys
from string import Template
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from . import _constants
from .database import Database
from .embeds import error_embed, leaderboard_embed, success_embed, stats_embed
from .exceptions import (
    CourseException,
    DateException,
    DiscordLibException,
    TimeException,
)
from .logger import handler, logger
from .pathlib_ext import PathExt as Path

token = _constants.TOKEN
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot("!!", intents=intents)  # type: ignore


def run() -> None:
    """Run the bot."""
    bot.remove_command("sync")  # type: ignore
    asyncio.run(bot.add_cog(MainCog(bot)))  # type: ignore
    asyncio.run(bot.add_cog(Archive()))  # type: ignore
    try:
        asyncio.run(bot.run(token, log_handler=handler, log_level=logging.DEBUG))  # type: ignore
    except ValueError:
        print("KeyboardInterrupt, exiting!")
        logger.info("KeyboardInterrupt, exiting!")
        sys.exit(0)


class Buttons(discord.ui.View):
    """The leaderboard buttons."""

    def __init__(self, *, timeout=None, path: Path = Path("database.toml")):
        """Initialize the leaderboard buttons.

        Args:
            timeout (int, optional): The time in which the buttons will no longer work. Defaults to None.
            path (Path, optional): The path to the database to use. Defaults to the main database (database.toml).
        """
        super().__init__(timeout=timeout)
        self.database = Database(path)

    @discord.ui.button(  # type: ignore
        label="Refresh", style=discord.ButtonStyle.blurple, emoji="🔄"
    )  # or .primary
    async def refresh_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """The refresh button."""
        # why do i have to have so many type ignore comments...
        embeds = interaction.message.embeds  # type: ignore
        for embed in embeds:  # type: ignore
            if embed.title.find("Course 1") != -1:  # type: ignore
                course = 1
            if embed.title.find("Course 2") != -1:  # type: ignore
                course = 2
            if embed.title.find("Course 3") != -1:  # type: ignore
                course = 3
            if embed.title.find("Course 4") != -1:  # type: ignore
                course = 4
            if embed.title.find("Course 5") != -1:  # type: ignore
                course = 5
            if embed.title.find("Course 6") != -1:  # type: ignore
                course = 6
            if embed.title.find("Course 7") != -1:  # type: ignore
                course = 7
        all_times, best_time = self.database.leaderboard(course)
        registered_users = self.database.get("registered_users")
        embed = leaderboard_embed(all_times, best_time, registered_users, course)
        await interaction.response.edit_message(view=self, embed=embed)

    @discord.ui.button(  # type: ignore
        label="Previous Course", style=discord.ButtonStyle.gray, emoji="⬅️"
    )  # or .secondary/.grey
    async def previous_course_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """The previous course button."""
        embeds = interaction.message.embeds  # type: ignore
        for embed in embeds:  # type: ignore
            if embed.title.find("Course 1") != -1:  # type: ignore
                course = 1
            if embed.title.find("Course 2") != -1:  # type: ignore
                course = 2
            if embed.title.find("Course 3") != -1:  # type: ignore
                course = 3
            if embed.title.find("Course 4") != -1:  # type: ignore
                course = 4
            if embed.title.find("Course 5") != -1:  # type: ignore
                course = 5
            if embed.title.find("Course 6") != -1:  # type: ignore
                course = 6
            if embed.title.find("Course 7") != -1:  # type: ignore
                course = 7
        if course > 1:
            course -= 1
        else:
            await interaction.response.send_message(
                "You cannot decrement the course if it is 1!", ephemeral=True
            )
        all_times, best_time = self.database.leaderboard(course)
        registered_users = self.database.get("registered_users")
        embed = leaderboard_embed(all_times, best_time, registered_users, course)
        await interaction.response.edit_message(view=self, embed=embed)

    @discord.ui.button(  # type: ignore
        label="Next Course",
        style=discord.ButtonStyle.gray,
        emoji="➡️",
    )  # or .success
    async def next_course_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """The next course button."""
        embeds = interaction.message.embeds  # type: ignore
        for embed in embeds:  # type: ignore
            if embed.title.find("Course 1") != -1:  # type: ignore
                course = 1
            if embed.title.find("Course 2") != -1:  # type: ignore
                course = 2
            if embed.title.find("Course 3") != -1:  # type: ignore
                course = 3
            if embed.title.find("Course 4") != -1:  # type: ignore
                course = 4
            if embed.title.find("Course 5") != -1:  # type: ignore
                course = 5
            if embed.title.find("Course 6") != -1:  # type: ignore
                course = 6
            if embed.title.find("Course 7") != -1:  # type: ignore
                course = 7
        if course < 7:
            course += 1
        else:
            await interaction.response.send_message(
                "You cannot increment the course if it is 7!", ephemeral=True
            )
        all_times, best_time = self.database.leaderboard(course)
        registered_users = self.database.get("registered_users")
        embed = leaderboard_embed(all_times, best_time, registered_users, course)
        await interaction.response.edit_message(view=self, embed=embed)


class MainCog(commands.Cog):
    """The main cog."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the main cog, which holds all the commands for the bot.

        Args:
            bot (commands.Bot): The affiliated bot object.
        """
        self.bot = bot
        self.database = Database(Path("database.toml"))
        self.permissions = discord.Permissions(
            274877975616
        )  # send messages [in threads], read messages [history], add reactions

    @bot.event
    async def on_ready():  # type: ignore
        """Things to do once the bot is ready."""
        logger.info(f"{bot.user} has connected to Discord!")
        url = discord.utils.oauth_url(
            bot.user.id,  # type: ignore
            permissions=discord.Permissions(274877975616),
            scopes=["bot", "applications.commands"],
        )
        logger.info(f"Invite link: {url}")

    @bot.command("sync")  # type: ignore
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: Context) -> None:
        """The sync command, which only works for the owner of the bot."""
        await self.bot.tree.sync()
        await ctx.reply("Synced application commands.")

    @app_commands.command(name="ping", description="Ping the bot.")
    async def ping(self, interaction: discord.Interaction) -> None:
        """Ping the bot to make sure it is online."""
        await interaction.response.send_message(
            f"Pong! Ping: {format(round(bot.latency, 1))}"  # type: ignore
        )

    @app_commands.command(name="submit")
    @app_commands.guild_only()
    async def submit(
        self,
        interaction: discord.Interaction,
        time: str,
        course: int,
        advanced: bool = False,
        user: Optional[discord.Member] = None,
    ):
        """Submit a time to be added to the leaderboard.

        Args:
            time (str): The time.
            course (int): The course number. Possible values are integers 1-7.
            advanced (bool, optional): Whether it was an advanced completion. Defaults to False.
            user: (Discord user, optional): Submit this time for another user. If not specified, it is assumed to be the user running the command. You must have the 'Moderate Members' permission to do this.
        """
        if isinstance(interaction.user, discord.Member):
            if interaction.user.guild_permissions.moderate_members:
                if user is None:
                    real_user = interaction.user
                elif isinstance(user, discord.Member):
                    real_user = user
            else:
                if user is not None:
                    try:
                        raise PermissionError(
                            "You must have Moderate Members permission in this guild to use the `user` property!"
                        )
                    except PermissionError as e:
                        logger.exception(
                            "User is specified and the user is not a moderator!"
                        )
                        embed = error_embed(
                            e,
                            "You don't have the Moderate Members permission on this server, which means you cannot submit times for other users. If this is in error, please let <@995310680909549598> know.",
                        )
                        await interaction.response.send_message(
                            embed=embed, ephemeral=True
                        )
                        raise PermissionError from e
                else:
                    real_user = interaction.user
        else:
            raise DiscordLibException(
                "The discord.py library did not give the expected value. Did you try to run it in a DM?"
            )
        # await interaction.response.defer()
        logger.debug(f"advanced: {advanced}")
        if course not in [1, 2, 3, 4, 5, 6, 7]:
            try:
                raise CourseException()
            except CourseException as e:
                logger.exception("The course given was invalid.")
                embed = error_embed(
                    e,
                    "The course number you gave was not valid. Make sure this is a valid course!\n*Note: This bot does not support the Daily Challenge right now.*\n",
                )
                await interaction.response.send_message(embed=embed)
                raise CourseException from e  # stops command from continuing to run
        time_str = Template("$minute:$second")
        time_data_fmt = time_str.substitute(
            minute=time.split(":")[0], second=time.split(":")[1]
        )
        logger.debug(
            f"Time being submitted by {real_user}: {time_data_fmt} (advanced: {advanced})"
        )
        try:
            self.database.write(real_user, time_data_fmt, course, advanced)
            if advanced is True:
                description = f"{real_user.mention}'s Advanced Completion time of **{time_data_fmt}** on Course {course} was successfully added to the leaderboard."
            else:
                description = f"{real_user.mention}'s time of **{time_data_fmt}** on Course {course} was successfully added to the leaderboard."
            await interaction.response.send_message(embed=success_embed(description))
        except TimeException as e:
            logger.exception("Stored time was shorter than the given time.")
            embed = error_embed(
                e,
                "The time you entered was longer than the currently stored time. If this is in error, please let <@995310680909549598> know.",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command()
    async def leaderboard(self, interaction: discord.Interaction, course: int = 1):
        """Get the leaderboard for this month's courses.

        Args:
            course (int, optional): The number of the course to start on. Defaults to 1.
        """
        if course not in [1, 2, 3, 4, 5, 6, 7]:
            try:
                raise CourseException()
            except CourseException as e:
                logger.exception("The course given was invalid.")
                embed = error_embed(
                    e,
                    "The course number you gave was not valid. Make sure this is a valid course!\n*Note: This bot does not support the Daily Challenge right now.*\n",
                )
                await interaction.response.send_message(embed=embed)
                raise CourseException from e  # stops command from continuing to run
        all_times, best_time = self.database.leaderboard(course)
        registered_users = self.database.get("registered_users")
        embed = leaderboard_embed(all_times, best_time, registered_users, course)
        view = Buttons()
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command()
    async def register(
        self, interaction: discord.Interaction, user: Optional[discord.User] = None
    ):
        """Registers the user for the leaderboard.

        Args:
            user (discord.User, optional): The user. Defaults to the user running this command.
        """
        if user is None:
            real_user = interaction.user
        else:
            real_user = user
        try:
            self.database.register_user(user=real_user)
        except TypeError as e:
            logger.exception(
                "Error while registering user. User was not a User/Member or a list."
            )
            await interaction.response.send_message(
                embed=error_embed(e, "Internal error: User was not an int")
            )
            raise TypeError from e
        await interaction.response.send_message(
            embed=success_embed(
                f"The user {real_user.mention} has been added to the registered users. Their times will now show on the leaderboard."
            )
        )


class Archive(commands.GroupCog, group_name="archive"):
    """The archive subcommands."""

    def __init__(self) -> None:
        """Initialize the archive subcommands."""
        pass

    @app_commands.command()
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        year: int,
        month: int,
        course: Optional[int] = 1,
    ):
        """Get the leaderboard for a certain time in the past.

        Args:
            year (int): The year to look up.
            month (int): The month to look up.
            course (int, optional): The course to start on. Defaults to 1.
        """
        if course not in [1, 2, 3, 4, 5, 6, 7]:
            try:
                raise CourseException()
            except CourseException as e:
                logger.exception("The course given was invalid.")
                embed = error_embed(
                    e,
                    "The course number you gave was not valid. Make sure this is a valid course!\n*Note: This bot does not support the Daily Challenge right now.*\n",
                )
                await interaction.response.send_message(embed=embed)
                raise CourseException from e  # stops command from continuing to run
        data_path = Path(f"./.archive/{year}/{month}/database.toml")
        if data_path.exists() is False:
            try:
                raise DateException()
            except DateException as e:
                logger.exception("The path to the year/date combination was not found.")
                await interaction.response.send_message(
                    embed=error_embed(
                        e,
                        "The path to the year/date combination was not found. This could mean you put in an invalid date, or there was an internal error.",
                    )
                )
                raise DateException from e  # stops command from continuing to run
        local_database = Database(data_path)
        all_times, best_time = local_database.leaderboard(course)
        registered_users = local_database.get("registered_users")
        embed = leaderboard_embed(all_times, best_time, registered_users, course)
        view = Buttons(path=data_path)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command()
    async def stats(
        self,
        interaction: discord.Interaction,
        year: int,
        month: int,
        user: Optional[discord.User | discord.Member] = None,
    ):
        """Get your or another user's statistics for a certain time in the past.

        Args:
            year (int): The year to look up.
            month (int): The month to look up.
            user (discord.User/discord.Member, optional): The user to look up.. Defaults to the user running the command.
        """
        if user is None:
            user = interaction.user
        data_path = Path(f"./.archive/{year}/{month}/database.toml")
        if data_path.exists() is False:
            try:
                raise DateException()
            except DateException as e:
                logger.exception("The path to the year/date combination was not found.")
                await interaction.response.send_message(
                    embed=error_embed(
                        e,
                        "The path to the year/date combination was not found. This could mean you put in an invalid date, or there was an internal error.",
                    )
                )
                raise DateException from e  # stops command from continuing to run
        embed = stats_embed(user, year, month)
        await interaction.response.send_message(embed=embed)


run()
