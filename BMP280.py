# Copyright (c) 2015 Sean K Sell and Adafruit Industries
# Author: Sean K Sell 
# Contributors Tony DiCola and Kevin Towsend
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import logging
import time


# BMP280 default address.
BMP280_I2CADDR           = 0x77

# Oversampling Setting
BMP280_SAMPLE_0          = 0 
BMP280_SAMPLE_1          = 1 
BMP280_SAMPLE_2          = 2 
BMP280_SAMPLE_4          = 3 
BMP280_SAMPLE_8          = 4 
BMP280_SAMPLE_16         = 7 


# Power Modes
BMP280_SLEEP_MODE         = 0 # mode[1:0] bits 00
BMP280_FORCED_MODE        = 2 # mode[1:0] bits 10 and 01
BMP280_NORMAL_MODE        = 3 # mode[1:0] bits 11

# BMP280 Registers
BMP280_CHIP_ID           = 0xD0  # R Chip Id 0x58 (8 bits)
BMP280_RESET             = 0xE0  # R always 0x00 W 0xB6 to Force Reset (8 bits)
BMP280_CONTROL           = 0xF4  # 7,6,5 osrs_t 4,3,2 osrs_p 1,0 mode(8 bits)
BMP280_CONFIG            = 0xF5  # 7,6,5 t_sb 4,3,2 filter 0 spi3w_en
BMP280_PRESSURE_MSB      = 0xF7
BMP280_PRESSURE_LSB      = 0xF8
BMP280_PRESSURE_XLSB     = 0xF9
BMP280_TEMP_MSB          = 0xFA
BMP280_TEMP_LSB          = 0xFB
BMP280_TEMP_XLSB         = 0xFC


BMP280_DIG_T1            = 0x88  # R   Unsigned Calibration data (16 bits)
BMP280_DIG_T2            = 0x8A  # R   Signed Calibration data (16 bits)
BMP280_DIG_T3            = 0x8C  # R   Signed Calibration data (16 bits)
BMP280_DIG_P1            = 0x8E  # R   Unsigned Calibration data (16 bits)
BMP280_DIG_P2            = 0x90  # R   Signed Calibration data (16 bits)
BMP280_DIG_P3            = 0x92  # R   Signed Calibration data (16 bits)
BMP280_DIG_P4            = 0x94  # R   Signed Calibration data (16 bits)
BMP280_DIG_P5            = 0x96  # R   Signed Calibration data (16 bits)
BMP280_DIG_P6            = 0x98  # R   Signed Calibration data (16 bits)
BMP280_DIG_P7            = 0x9A  # R   Signed Calibration data (16 bits)
BMP280_DIG_P8            = 0x9C  # R   Signed Calibration data (16 bits)
BMP280_DIG_P9            = 0x9E  # R   Signed Calibration data (16 bits)

class BMP280(object):
	def __init__(self, mode=BMP280_NORMAL_MODE, address=BMP280_I2CADDR, i2c=None, **kwargs):
		self._logger = logging.getLogger('Adafruit_BMP.BMP280')
		# Check that mode is valid.
		if mode not in [BMP280_SLEEP_MODE, BMP280_FORCED_MODE, BMP280_NORMAL_MODE]:
			raise ValueError('Unexpected mode value {0}.  Set mode to one of BMP280_SLEEP_MODE, BMP280_FORCED_MODE, BMP280_NORMAL_MODE'.format(mode))
		self._mode = mode
		self._osrs_t = BMP280_SAMPLE_1
		self._osrs_p = BMP280_SAMPLE_4
		# Create I2C device.
		if i2c is None:
			import Adafruit_GPIO.I2C as I2C
			i2c = I2C
		self._device = i2c.get_i2c_device(address, **kwargs)
		# Load calibration values.
		self._load_calibration()

	def _load_calibration(self):
		self.cal_t1 = self._device.readU16(BMP280_DIG_T1)   # UINT16
		self.cal_t2 = self._device.readS16(BMP280_DIG_T2)   # INT16
		self.cal_t3 = self._device.readS16(BMP280_DIG_T3)   # INT16
		self.cal_p1 = self._device.readU16(BMP280_DIG_P1)   # UINT16
		self.cal_p2 = self._device.readS16(BMP280_DIG_P2)   # INT16
		self.cal_p3 = self._device.readS16(BMP280_DIG_P3)   # INT16
		self.cal_p4 = self._device.readS16(BMP280_DIG_P4)   # INT16
		self.cal_p5 = self._device.readS16(BMP280_DIG_P5)   # INT16
		self.cal_p6 = self._device.readS16(BMP280_DIG_P6)   # INT16
		self.cal_p7 = self._device.readS16(BMP280_DIG_P7)   # INT16
		self.cal_p8 = self._device.readS16(BMP280_DIG_P8)   # INT16
		self.cal_p9 = self._device.readS16(BMP280_DIG_P9)   # INT16
		self._logger.debug('T1 = {0:6d}'.format(self.cal_t1))
		self._logger.debug('T2 = {0:6d}'.format(self.cal_t2))
		self._logger.debug('T3 = {0:6d}'.format(self.cal_t3))
		self._logger.debug('P1 = {0:6d}'.format(self.cal_p1))
		self._logger.debug('P2 = {0:6d}'.format(self.cal_p2))
		self._logger.debug('P3 = {0:6d}'.format(self.cal_p3))
		self._logger.debug('P4 = {0:6d}'.format(self.cal_p4))
		self._logger.debug('P5 = {0:6d}'.format(self.cal_p5))
		self._logger.debug('P6 = {0:6d}'.format(self.cal_p6))
		self._logger.debug('P7 = {0:6d}'.format(self.cal_p7))
		self._logger.debug('P8 = {0:6d}'.format(self.cal_p8))
		self._logger.debug('P9 = {0:6d}'.format(self.cal_p9))
	def _load_datasheet_calibration(self):
		# Set calibration from values in the datasheet example.  Useful for debugging the
		# temp and pressure calculation accuracy.
		self.cal_t1 = 27504
		self.cal_t2 = 26435
		self.cal_t3 = -1000
		self.cal_p1 = 36477
		self.cal_p2 = -10685
		self.cal_p3 = 3024
		self.cal_p4 = 2855
		self.cal_p5 = 140
		self.cal_p6 = -7
		self.cal_p7 = 15500
		self.cal_p8 = -14500
		self.cal_p9 = 6000
	def read_chip_id(self):
		raw = self._device.readU8(BMP280_CHIP_ID)
		self._logger.debug('Chip Id 0x{0:X} ({1})'.format(raw & 0xFFFF, raw))
		return raw
	def read_raw_pressure(self):
		"""Reads the raw (uncompensated) pressure from the sensor."""
		self._device.write8(BMP280_CONTROL, self._mode + (self._osrs_p << 2) + (self._osrs_t << 5))
		#if self._mode == BMP085_ULTRALOWPOWER:
		#	time.sleep(0.005)
		#elif self._mode == BMP085_HIGHRES:
		#	time.sleep(0.014)
		#elif self._mode == BMP085_ULTRAHIGHRES:
		#	time.sleep(0.026)
		#else:
		#	time.sleep(0.008)
		msb = self._device.readU8(BMP280_PRESSURE_MSB)
		lsb = self._device.readU8(BMP280_PRESSURE_LSB)
		xlsb = self._device.readU8(BMP280_PRESSURE_XLSB)
		raw = ((msb << 16) + (lsb << 8) + xlsb) >> (8 - self._mode)
		self._logger.debug('Raw pressure 0x{0:04X} ({1})'.format(raw & 0xFFFF, raw))
		return raw
	def read_raw_temperature(self):
		"""Reads the raw (uncompensated) temperature level from the sensor."""
		self._device.write8(BMP280_CONTROL, self._mode + (self._osrs_p << 2) + (self._osrs_t << 5))
		#if self._mode == BMP085_ULTRALOWPOWER:
		#	time.sleep(0.005)
		#elif self._mode == BMP085_HIGHRES:
		#	time.sleep(0.014)
		#elif self._mode == BMP085_ULTRAHIGHRES:
		#	time.sleep(0.026)
		#else:
		#	time.sleep(0.008)
		msb = self._device.readU8(BMP280_TEMP_MSB)
		lsb = self._device.readU8(BMP280_TEMP_LSB)
		xlsb = self._device.readU8(BMP280_TEMP_XLSB)
		raw = ((msb << 16) + (lsb << 8) + xlsb) >> (4)
		self._logger.debug('Raw temperature 0x{0:04X} ({1})'.format(raw & 0xFFFF, raw))
		return raw
	def compensate_temperature(self, adc_t):
		"""Compensates the raw (uncompensated) temperature level from the sensor."""
		var1 = (((adc_t >> 3) - (self.cal_t1 << 1)) * self.cal_t2) >> 11
		self._logger.debug('var1 = {:10.1f}'.format(var1))
		var2 = (((adc_t >> 4) - self.cal_t1) * ((adc_t >> 4) - self.cal_t1) >> 12) * self.cal_t3 >> 14
		self._logger.debug('var2 = {:10.1f}'.format(var2))
		t_fine = var1 + var2
		self._logger.debug('t_fine = {:10.1f}'.format(t_fine))
		T = (((t_fine * 5 + 128) >> 8) / 100.0)
		self._logger.debug('T = {:10.2f}'.format(T))
		return T
