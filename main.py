import time
import rp2
from machine import Pin, SPI

class EPD_5in65_simplified:
  def __init__(self):
    self.width = 600
    self.height = 448

    self.spi = SPI(1)
    self.spi.init(baudrate=4_000_000)

    self.rst_pin  = Pin(12, Pin.OUT)
    self.dc_pin   = Pin(8,  Pin.OUT)
    self.cs_pin   = Pin(9,  Pin.OUT)
    self.busy_pin = Pin(13, Pin.IN, Pin.PULL_UP)

  def reset(self):
    self.rst_pin.value(1)
    time.sleep_ms(200)
    self.rst_pin.value(0)
    time.sleep_ms(2)
    self.rst_pin.value(1)
    time.sleep_ms(200)

  def init_panel(self):
    self.busy_wait_high()
    self.send_command(0x00)
    self.send_data(0xEF)
    self.send_data(0x08)
    self.send_command(0x01)
    self.send_data(0x37)
    self.send_data(0x00)
    self.send_data(0x23)
    self.send_data(0x23)
    self.send_command(0x03)
    self.send_data(0x00)
    self.send_command(0x06)
    self.send_data(0xC7)
    self.send_data(0xC7)
    self.send_data(0x1D)
    self.send_command(0x30)
    self.send_data(0x3C)
    self.send_command(0x41)
    self.send_data(0x00)
    self.send_command(0x50)
    self.send_data(0x37)
    self.send_command(0x60)
    self.send_data(0x22)
    self.send_command(0x61)
    # width:600, height:448
    self.send_data(0x02)  # 600 >> 8 = 2
    self.send_data(0x58)  # 600 &0xFF = 0x58
    self.send_data(0x01)  # 448 >> 8 = 1
    self.send_data(0xC0)  # 448 &0xFF = 0xC0
    self.send_command(0xE3)
    self.send_data(0xAA)
    time.sleep_ms(100)
    self.send_command(0x50)
    self.send_data(0x37)

  def busy_wait_high(self):
      time.sleep_ms(200)

  def busy_wait_low(self):
    time.sleep_ms(200)

  def send_command(self, cmd):
    self.dc_pin.value(0)
    self.cs_pin.value(0)
    self.spi.write(bytearray([cmd]))
    self.cs_pin.value(1)

  def send_data(self, val):
    self.dc_pin.value(1)
    self.cs_pin.value(0)
    self.spi.write(bytearray([val]))
    self.cs_pin.value(1)

  def send_data_buf(self, buf):
    self.dc_pin.value(1)
    self.cs_pin.value(0)
    self.spi.write(buf)
    self.cs_pin.value(1)

  def clear(self, color=0x01):
    self.send_command(0x61)
    self.send_data(0x02)
    self.send_data(0x58)
    self.send_data(0x01)
    self.send_data(0xC0)

    self.send_command(0x10)
    line = bytearray([(color << 4) | color] * self.height)
    for _ in range(self.width // 2):
      self.send_data_buf(line)

    self.send_command(0x04)  # Power on
    self.busy_wait_high()
    self.send_command(0x12)  # Display Refresh
    self.busy_wait_high()
    self.send_command(0x02)  # Power off
    self.busy_wait_low()
    time.sleep_ms(500)


def main():
  epd = EPD_5in65_simplified()

  while True:
    if rp2.bootsel_button() == 1:
      epd.reset()
      epd.init_panel()
      epd.clear()
    time.sleep(1)
  
main()

