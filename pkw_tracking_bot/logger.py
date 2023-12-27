# SPDX-FileCopyrightText: 2023 osfanbuff63
#
# SPDX-License-Identifier: Apache-2.0

import logging
import sys

from .pathlib_ext import PathExt as Path

file = Path("pkw_tracking_bot.log")
file.write("")
handler = logging.FileHandler(
    filename="pkw_tracking_bot.log", encoding="utf-8", mode="w"
)
handler2 = logging.StreamHandler(sys.stdout)
logger = logging.getLogger("pkw_tracking_bot")
logger.addHandler(handler)
logger.addHandler(handler2)
logger.setLevel(logging.DEBUG)
