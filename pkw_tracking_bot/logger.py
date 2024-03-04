# SPDX-FileCopyrightText: 2023 osfanbuff63
#
# SPDX-License-Identifier: Apache-2.0
"""Logger initialization."""

import logging

from pathlib import Path

file = Path("pkw_tracking_bot.log")
file.write_text("")
handler = logging.FileHandler(
    filename="pkw_tracking_bot.log", encoding="utf-8", mode="w"
)
logger = logging.getLogger("pkw_tracking_bot")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
