# SPDX-FileCopyrightText: 2023 osfanbuff63
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging
import os
import sys
from string import Template
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from . import constants
from .database import Database
from .embeds import error_embed, leaderboard_embed, success_embed
from .exceptions import CourseException, TimeException
from .logger import handler, logger
from .pathlib_ext import PathExt

token = constants.TOKEN
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot("!!", intents=intents)  # type: ignore


def run() -> None:
    bot.remove_command("sync")  # type: ignore
    asyncio.run(bot.add_cog(MainCog(bot)))  # type: ignore
    try:
        asyncio.run(bot.run(token, log_handler=handler, log_level=logging.DEBUG))  # type: ignore
    except ValueError:
        print("KeyboardInterrupt, exiting!")
        logger.info("KeyboardInterrupt, exiting!")
        sys.exit(0)


class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.database = Database(PathExt("database.toml"))

    @discord.ui.button(  # type: ignore
        label="Refresh", style=discord.ButtonStyle.blurple, emoji="🔄"
    )  # or .primary
    async def refresh_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
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
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.database = Database(PathExt("database.toml"))
        self.permissions = discord.Permissions(
            274877975616
        )  # send messages [in threads], read messages [history], add reactions

    @bot.event
    async def on_ready():  # type: ignore
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
        await self.bot.tree.sync()
        await ctx.reply("Synced application commands.")

    @app_commands.command(name="ping", description="Ping the bot.")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            f"Pong! Ping: {format(round(bot.latency, 1))}"  # type: ignore
        )

    @app_commands.command(name="submit")
    async def submit(
        self,
        interaction: discord.Interaction,
        time: str,
        course: int,
        advanced: bool = False,
    ):
        """Submit a time to be added to the leaderboard.

        Args:
            time (str): The time.
            course (int): The course number. Possible values are integers 1-7.
            advanced (bool, optional): Whether it was an advanced completion. Defaults to False.
        """
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
            f"Time being submitted by {interaction.user}: {time_data_fmt} (advanced: {advanced})"
        )
        try:
            self.database.write(interaction.user, time_data_fmt, course, advanced)
            await interaction.response.send_message(
                embed=success_embed(
                    "Your time was successfully added to the leaderboard."
                )
            )
        except TimeException as e:
            logger.exception("Stored time was shorter than the given time.")
            embed = error_embed(
                e,
                f"The time you entered was longer than the currently stored time. If this is in error, please let <@995310680909549598> know.",
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


run()
