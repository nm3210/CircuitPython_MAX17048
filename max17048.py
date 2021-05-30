# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 nm3210
#
# SPDX-License-Identifier: MIT
"""
`max17048`
================================================================================

Interface to the MAX17048 fuel gauge IC over I2C. General code layout copied \
from the Adafruit_CircuitPython_LC709203F module (another IC fuel gauge).    \
The eventual implementation should mirror the arduino/c++ library here:      \
    https://github.com/sparkfun/SparkFun_MAX1704x_Fuel_Gauge_Arduino_Library


* Author(s): nm3210

Implementation Notes
--------------------

**Hardware:**

 * SparkFun Qwiic Fuel Gauge MAX17048: https://www.sparkfun.com/products/17715
 * SparkFun LiPo Fuel Gauge (MAX17043): https://www.sparkfun.com/products/10617
 * Also used in the SparkFun Thing Plus RP2040: https://www.sparkfun.com/products/17745

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

from micropython import const
from adafruit_bus_device.i2c_device import I2CDevice

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/nm3210/CircuitPython_MAX17048.git"

MAX17048_I2CADDR_DEFAULT = const(0x36) # 0b0110110
MAX17048_I2CWRITE        = const(0x6C)
MAX17048_I2CREAD         = const(0x6D)

MAX17048_CMD_VCELL       = const(0x02)
MAX17048_CMD_SOC         = const(0x04)
MAX17048_CMD_MODE        = const(0x06)
MAX17048_CMD_VERSION     = const(0x08)
MAX17048_CMD_HIBRT       = const(0x0A)
MAX17048_CMD_CONFIG      = const(0x0C)
MAX17048_CMD_VALRT       = const(0x14)
MAX17048_CMD_CRATE       = const(0x16)
MAX17048_CMD_VRESET_ID   = const(0x18)
MAX17048_CMD_STATUS      = const(0x1A)

def bytearrayToHex(valIn):
    return "".join(["{:02x}".format(itm) for itm in valIn])
    
def bytearrayToBin(valIn):
    return "".join(["{:08b}".format(itm) for itm in valIn])

def highByte(int16In):
    return (int16In >> 8) & 0x00FF
    
def lowByte(int16In):
    return int16In & 0x00FF

class MAX17048:
    """Interface library for MAX17048 battery monitoring and fuel gauge sensors"""

    def __init__(self, i2c_bus, address=MAX17048_I2CADDR_DEFAULT):
        self.i2c_device = I2CDevice(i2c_bus, address)
        
        # Preallocate buffers for sending/receiving I2C data
        self._bufSend = bytearray(2)
        self._bufSend[1] = MAX17048_I2CREAD # always use bufSend for reading
        self._bufData = bytearray(2)
        self._bufWrite = bytearray(3)

    @property
    def vcell(self):
        """Returns floating point voltage"""
        return self._read_word(MAX17048_CMD_VCELL) * 0.000078125

    @property
    def soc(self):
        """Returns floating point state of charge"""
        return self._read_word(MAX17048_CMD_SOC) * 0.00390625

    @property
    def crate(self):
        """Returns floating point charge rate"""
        return self._read_word(MAX17048_CMD_CRATE) * 0.208

    @property
    def ic_version(self):
        """Returns read-only chip version"""
        return lowByte(self._read_word(MAX17048_CMD_VERSION))

    def _read_word(self, command):
        self._bufSend[0] = command
        with self.i2c_device as i2c:
            i2c.write_then_readinto(self._bufSend, self._bufData)
        return (self._bufData[0]<<8 | self._bufData[1]) # convert value to 2-byte int

    def _write_word(self, command, data):
        self._bufWrite[0] = command
        self._bufWrite[1] = data & 0xFF
        self._bufWrite[2] = (data >> 8) & 0xFF
        with self.i2c_device as i2c:
            i2c.write(self._bufWrite)
