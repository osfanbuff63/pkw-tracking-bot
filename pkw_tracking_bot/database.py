# SPDX-FileCopyrightText: 2023 osfanbuff63
#
# SPDX-License-Identifier: Apache-2.0

from typing import Optional, Tuple

import arrow
import discord
import tomlkit

from .exceptions import TimeException
from .logger import logger
from .pathlib_ext import PathExt as Path


class Database:
    def __init__(self, file: Path) -> None:
        self.file: Path = file
        if self.file.exists() is False:
            self.file.write("")
        self.update_dict()

    def load(self):
        file = Path(self.file).resolve()
        toml_dict = tomlkit.load(file)
        return toml_dict

    def update_dict(self) -> None:
        toml_dict = self.load()
        self.toml_doc = toml_dict

    def write(
        self,
        user: discord.User | discord.Member,
        time: str,
        course_id: int,
        advanced: bool = False,
    ) -> None:
        id = user.id
        utc = arrow.utcnow()
        current_time = utc.to("US/Eastern")
        try:
            written_time = arrow.get(self.toml_doc["last_updated"])
        except:
            written_time = None
        if written_time != None:
            # ignore type checking because written_time cannot be None here
            if current_time.date().month != written_time.date().month:  # type: ignore
                # new month, reset the times
                logger.info("A new month was detected, resetting all times.")
                self._overwrite()
        try:
            if (
                self.toml_doc[f"{id}"][f"course_{course_id}"]["time"] < time
                or self.toml_doc[f"{id}"][f"course_{course_id}"]["time"] == ""
            ):
                raise TimeException()
        except KeyError:
            logger.error(
                "User did not exist for given course, assuming the time is newer."
            )
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
        self.toml_doc[f"{id}"][f"course_{course_id}"]["time"] = time
        self.toml_doc[f"{id}"][f"course_{course_id}"]["advanced"] = advanced
        # logger.debug(f"self.toml_doc: {self.toml_doc.as_string()}")
        self.toml_doc["last_updated"] = current_time.format("MM-DD-YYYY HH:mm:ss")
        self.file.write(self.toml_doc.as_string().rstrip())
        self.update_dict()

    def register_user(
        self,
        user: Optional[discord.User | discord.Member] = None,
        users: Optional[list[int | str]] = None,
    ):
        if user and users:
            raise TypeError("User and users cannot both be defined.")
        if user is None and users is None:
            raise TypeError("One of user and users must be defined.")
        registered_users = []
        try:
            if self.toml_doc["registered_users"] != []:
                for id in self.toml_doc["registered_users"]:
                    registered_users.append(id)
        except KeyError:
            logger.debug("KeyError on registered_users, continuing")
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
        logger.debug(f"registered_users: {str(registered_users)}")
        self.toml_doc["registered_users"] = registered_users
        self.file.write(self.toml_doc.as_string().replace("\\n", ""))
        self.update_dict()

    def _overwrite(self) -> None:
        registered_users = []
        try:
            for user in self.toml_doc["registered_users"]:
                registered_users.append(user)
        except KeyError:
            pass
        self.file.write("")
        self.update_dict()
        if registered_users != []:
            self.register_user(users=registered_users)

    def leaderboard(self, course: int) -> Tuple[dict, str]:
        current_state = self.load()
        registered_users = current_state.get("registered_users")
        logger.debug(f"Registered users (database): {registered_users}")
        times = {}
        for user in registered_users:
            times[user] = current_state[f"{user}"][f"course_{course}"]["time"]
        best_time = min(times.values())
        return times, best_time

    def get(self, key: str):
        return self.toml_doc[key]
