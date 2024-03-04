# SPDX-FileCopyrightText: 2023 osfanbuff63
#
# SPDX-License-Identifier: Apache-2.0
"""The database handler."""

from typing import Optional, Tuple
import arrow
import discord
import tomlkit

from .exceptions import TimeException
from .logger import logger
from pathlib import Path


class Database:
    """An access point to the database."""

    def __init__(self, file: Path | str) -> None:
        """Initialize the access point to the database.

        Args:
            file (Path): The path to the database file.
        """
        if isinstance(file, str):
            self.file = Path(file)
        elif isinstance(file, Path):
            self.file = file
        if self.file.exists() is False:
            self.file.write_text("")
        self.update_dict()

    def load(self) -> tomlkit.TOMLDocument:
        """Load the database."""
        file = Path(self.file).resolve()
        with file.open() as _file:
            toml_dict = tomlkit.load(_file)
        return toml_dict

    def update_dict(self) -> None:
        """Update the internal database."""
        toml_dict = self.load()
        self.toml_doc = toml_dict

    def write(
        self,
        user: discord.User | discord.Member,
        time: str,
        course_id: int,
        advanced: bool = False,
    ) -> None:
        """Write a time to the database.

        Args:
            user (discord.User | discord.Member): The Discord user to submit this time for.
            time (str): The time to submit.
            course_id (int): The course to submit this time to.
            advanced (bool, optional): Whether this was an advanced completion. Defaults to False.

        Raises:
            TimeException: If the time was slower than the currently stored time.
        """
        id = user.id
        utc = arrow.utcnow()
        current_time = utc.to("US/Eastern")
        try:
            written_time = arrow.get(self.toml_doc["last_updated"])  # type: ignore
        except:
            written_time = None
        if written_time is not None:
            # ignore type checking because written_time cannot be None here
            if current_time.date().month != written_time.date().month:  # type: ignore
                # new month, reset the times
                logger.info("A new month was detected, resetting all times.")
                self._overwrite(current_time)
        try:
            if (
                self.toml_doc[f"{id}"][f"course_{course_id}"]["time"] < time  # type: ignore
                or self.toml_doc[f"{id}"][f"course_{course_id}"]["time"] == ""  # type: ignore
            ):
                raise TimeException()
        except KeyError:
            logger.error(
                "User did not exist for given course, assuming the time is newer."
            )
            self.register_user(user)
        self.toml_doc[f"{id}"][f"course_{course_id}"]["time"] = time  # type: ignore
        self.toml_doc[f"{id}"][f"course_{course_id}"]["advanced"] = advanced  # type: ignore
        # logger.debug(f"self.toml_doc: {self.toml_doc.as_string()}")
        current_timestamp = current_time.int_timestamp
        # make backup
        self.backup(current_time)
        self.toml_doc["last_updated"] = current_timestamp
        self.file.write_text(self.toml_doc.as_string().rstrip())
        self.update_dict()

    def register_user(
        self,
        user: Optional[discord.User | discord.Member] = None,
        users: Optional[list[int | str]] = None,
    ):
        """Register a user or group of users to be in the database.

        Args:
            user (Optional[discord.User  |  discord.Member], optional): The Discord user to register. **Only one** of `user` and `users` can be specified. Defaults to None.
            users (Optional[list[int  |  str]], optional): A list of user IDs to register. **Only one** of `user` and `users` can be specified. Defaults to None.

        Raises:
            TypeError: If more than one or neither of `user` and `users` is specified.
        """
        if user and users:
            raise TypeError("User and users cannot both be defined.")
        if user is None and users is None:
            raise TypeError("One of user and users must be defined.")

        registered_users = []
        try:
            if self.toml_doc["registered_users"] != []:
                for id in self.toml_doc["registered_users"]:  # type: ignore
                    registered_users.append(id)
        except KeyError:
            logger.debug("KeyError on registered_users, continuing")
        user_already_registered = False
        try:
            for registered_user in self.toml_doc["registered_users"]:  # type: ignore
                if registered_user == id:
                    user_already_registered = True
                    break
                else:
                    continue
        except KeyError:
            # registered_users didn't exist, likely the database just reset
            pass
        if user_already_registered is False:
            if isinstance(user, discord.User):
                id = user.id
                registered_users.append(id)
            elif isinstance(user, discord.Member):
                id = user.id
                registered_users.append(id)
            elif users:
                for id in users:
                    registered_users.append(id)
            else:
                logger.debug(f"User: {user}")
                raise TypeError("User was not a list or a discord User.")
            table = tomlkit.table()
            table.append(tomlkit.key(["course_1", "time"]), "99:99.99")
            table.append(tomlkit.key(["course_1", "advanced"]), False)

            table.append(tomlkit.key(["course_2", "time"]), "99:99.99")
            table.append(tomlkit.key(["course_2", "advanced"]), False)

            table.append(tomlkit.key(["course_3", "time"]), "99:99.99")
            table.append(tomlkit.key(["course_3", "advanced"]), False)

            table.append(tomlkit.key(["course_4", "time"]), "99:99.99")
            table.append(tomlkit.key(["course_4", "advanced"]), False)

            table.append(tomlkit.key(["course_5", "time"]), "99:99.99")
            table.append(tomlkit.key(["course_5", "advanced"]), False)

            table.append(tomlkit.key(["course_6", "time"]), "99:99.99")
            table.append(tomlkit.key(["course_6", "advanced"]), False)

            table.append(tomlkit.key(["course_7", "time"]), "99:99.99")
            table.append(tomlkit.key(["course_7", "advanced"]), False)
            self.toml_doc.append(str(id), table)
        logger.debug(f"registered_users: {str(registered_users)}")
        # make backup
        date = arrow.get()
        self.backup(date)
        current_timestamp = date.int_timestamp
        self.toml_doc["registered_users"] = registered_users
        self.toml_doc["last_updated"] = current_timestamp
        self.file.write_text(self.toml_doc.as_string().replace("\\n", ""))
        self.update_dict()

    def backup(self, date: arrow.Arrow):
        """Backup the database."""
        # copy the current database to the archive folder so it can be viewed via /archive
        # and in case it breaks, we have a backup
        datetime = date.date()
        file_dir = str(self.file).strip(self.file.name)
        archive_path = Path(
            file_dir,
            f"database_archive/{datetime.year}/{datetime.month}/database.toml",
        )
        if not archive_path.exists():
            archive_path_dir = Path(
                file_dir, f"database_archive/{datetime.year}/{datetime.month}/"
            )
            archive_path_dir.mkdir(parents=True, exist_ok=True)
            archive_path.touch(exist_ok=True)
        archive_path.write_text(self.file.read_text())

    def _overwrite(self, date: arrow.Arrow) -> None:
        registered_users = []
        try:
            for user in self.toml_doc["registered_users"]:  # type: ignore
                registered_users.append(user)
        except KeyError:
            pass
        # make backup
        self.backup(date)
        self.file.write_text(f"last_updated = {date.int_timestamp}")
        self.update_dict()
        if registered_users != []:
            self.register_user(users=registered_users)

    def leaderboard(self, course: int) -> Tuple[dict, str]:
        """Get the statistics needed for the leaderboard command.

        Args:
            course (int): The course to get the statistics for,

        Returns:
            Tuple[dict, str]: All the times, and the best time.
        """
        current_state = self.load()
        registered_users = current_state.get("registered_users")
        logger.debug(f"Registered users (database): {registered_users}")
        times = {}
        for user in registered_users:  # type: ignore
            times[user] = current_state[f"{user}"][f"course_{course}"]["time"]  # type: ignore
            if current_state[f"{user}"][f"course_{course}"]["advanced"]:  # type: ignore
                str_times_user = str(times[user])
                logger.debug(f"str_times_user: {str_times_user}")
                times[user] = str_times_user + " [Advanced Completion]"
                logger.debug(f"times[user]: {times[user]}")
        best_time = min(times.values())  # type: ignore
        return times, best_time  # type: ignore

    def get(self, key: str):
        """Get a key from the database file."""
        return self.toml_doc[key]
