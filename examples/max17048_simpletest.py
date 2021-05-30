# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 nm3210
#
# SPDX-License-Identifier: Unlicense

import board
from max17048 import MAX17048
sensor = MAX17048(board.I2C())

sensor.vcell
sensor.soc
