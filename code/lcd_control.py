import utime
import osTimer
from machine import Pin
from usr.EventMesh import subscribe
from usr.common import Abstract


class LcdManager(Abstract):
    RGB_ENABLE = Pin(Pin.GPIO21, Pin.OUT, Pin.PULL_DISABLE, 1)  # 3.3v供电
    RST = Pin(Pin.GPIO34, Pin.OUT, Pin.PULL_PU, 1)  # reset 默认低电平. 引脚64
    LED = Pin(Pin.GPIO15, Pin.OUT, Pin.PULL_PU, 1)  # 背光使能, 高电平有效. 引脚62
    CS = Pin(Pin.GPIO32, Pin.OUT, Pin.PULL_PU, 1)  # CS信号, 开机默认高.  引脚65
    SCK = Pin(Pin.GPIO33, Pin.OUT, Pin.PULL_PU, 1)  # WR信号, 开机默认高.  引脚67
    SDA = Pin(Pin.GPIO31, Pin.OUT, Pin.PULL_PU, 1)  # DATA信号, 开机默认高. 引脚66

    def __init__(self):
        self._close_process_flag = True
        self.icon_data = [[6, 13], [4, 13], [2, 13], [0, 13], [7, 13], [0, 12], [2, 12], [6, 12], [4, 12], [6, 0],
                          [6, 2]]
        # 分别是金额区从左右 中间三个左-右 时间区左-右
        self.number_data = [[[7, 11], [7, 10], [3, 10], [1, 10], [3, 11], [5, 11], [5, 10]],
                            [[7, 9], [7, 8], [3, 8], [1, 8], [3, 9], [5, 9], [5, 8]],
                            [[7, 7], [7, 6], [3, 6], [1, 6], [3, 7], [5, 7], [5, 6]],
                            [[7, 5], [7, 4], [3, 4], [1, 4], [3, 5], [5, 5], [5, 4], [1, 3]],
                            [[7, 3], [7, 2], [3, 2], [1, 2], [3, 3], [5, 3], [5, 2], [1, 1]],
                            [[7, 1], [7, 0], [3, 0], [1, 0], [3, 1], [5, 1], [5, 0]],
                            [[6, 9], [4, 9], [0, 9], [0, 8], [2, 8], [4, 8], [2, 9]],
                            [[6, 11], [4, 11], [0, 11], [0, 10], [2, 10], [4, 10], [2, 11]],
                            [[7, 12], [5, 12], [1, 12], [1, 13], [3, 13], [5, 13], [3, 12]],
                            [[6, 1], [4, 1], [0, 1], [0, 0], [2, 0], [4, 0], [2, 1]],
                            [[6, 3], [4, 3], [0, 3], [0, 2], [2, 2], [4, 2], [2, 3], [6, 4]],
                            [[6, 5], [4, 5], [0, 5], [0, 4], [2, 4], [4, 4], [2, 5]],
                            [[6, 7], [4, 7], [0, 7], [0, 6], [2, 6], [4, 6], [2, 7]]]
        self.signal_data = [[6, 13], [4, 13], [2, 13], [0, 13], [7, 13], [0, 12], [2, 12], [6, 12], [4, 12], [6, 0],
                            [6, 2]]
        self.number = {
            "0": [1, 1, 1, 1, 1, 1, 0],  # 0 = '0'
            "1": [0, 1, 1, 0, 0, 0, 0],  # 1 = '1'
            "2": [1, 1, 0, 1, 1, 0, 1],  # 2 = '2'
            "3": [1, 1, 1, 1, 0, 0, 1],  # 3 = '3'
            "4": [0, 1, 1, 0, 0, 1, 1],  # 4 = '4'
            "5": [1, 0, 1, 1, 0, 1, 1],  # 5 = '5'
            "6": [1, 0, 1, 1, 1, 1, 1],  # 6 = '6'
            "7": [1, 1, 1, 0, 0, 0, 0],  # 7 = '7'
            "8": [1, 1, 1, 1, 1, 1, 1],  # 8 = '8'
            "9": [1, 1, 1, 1, 0, 1, 1],  # 9 = '9'
            "E": [1, 0, 0, 1, 1, 1, 1],  # 14 = 'E'
        }
        self.lcd_ram = [0x00 for i in range(14)]
        self.__timer = osTimer()

    @staticmethod
    def _write(flag, data):
        LcdManager.CS.write(0)
        LcdManager.SDA.write(1) if flag else LcdManager.SDA.write(0)
        LcdManager.SCK.write(0)
        LcdManager.SCK.write(1)
        for i in range(8):
            LcdManager.SDA.write(1) if data & 0x80 else LcdManager.SDA.write(0)
            LcdManager.SCK.write(0)
            LcdManager.SCK.write(1)
            data <<= 1
        LcdManager.CS.write(1)

    def _write_data(self, data):
        self._write(1, data)

    def _write_cmd(self, data):
        self._write(0, data)

    def _st7567_init(self):
        LcdManager.LED.write(1)
        LcdManager.RST.write(1)
        LcdManager.RST.write(0)
        LcdManager.RST.write(1)
        # init cmd
        self._write_cmd(0xE2)
        self._write_cmd(0x2F)
        self._write_cmd(0xA2)
        self._write_cmd(0x23)
        self._write_cmd(0x81)
        self._write_cmd(0x28)
        self._write_cmd(0xC0)
        self._write_cmd(0xA0)
        self._write_cmd(0x40)
        self._write_cmd(0xA6)
        self._write_cmd(0xAF)

    def lcd_sleep(self, topic=None, data=None):
        """LCD休眠"""
        if data:
            self._write_cmd(0xAE)
            self._write_cmd(0xA5)
        else:
            self._write_cmd(0xA4)
            self._write_cmd(0xAF)

    def digit_flush(self):
        """写入屏幕数据"""
        self._write_cmd(0x10)
        self._write_cmd(0x00)
        self._write_cmd(0xb0)
        for i in self.lcd_ram:
            self._write_data(i)

    def digit_flush_null(self):
        """清屏"""
        self._write_cmd(0x10)
        self._write_cmd(0x00)
        self._write_cmd(0xb0)
        for i in self.lcd_ram:
            self._write_data(0x00)

    def _set_battery_signal(self, topic=None, data=None):
        """
        data: (type, value)
        type: 0: 设置电池电量, value: 有效值0-4
        type: 1: 设置信号值, value: 有效值0-5
        """
        type_index = [[5, 9], [0, 5]][data[0]]
        for i, element in enumerate(self.signal_data[type_index[0]: type_index[1]]):
            if data[1] < 0:
                return None
            if data[1] > i:
                self.lcd_ram[element[1]] += 2 ** element[0] if not self.lcd_ram[element[1]] & (2 ** element[0]) else 0
            else:
                self.lcd_ram[element[1]] -= 2 ** element[0] if self.lcd_ram[element[1]] & (2 ** element[0]) else 0
        self.digit_flush()

    def _set_4g_wifi(self, topic=None, data=None):
        """设置 0:4g & 1:wifi"""
        for i, element in enumerate(self.signal_data[9: 11]):
            if data == i:
                self.lcd_ram[element[1]] += 2 ** element[0] if not self.lcd_ram[element[1]] & (2 ** element[0]) else 0
            else:
                self.lcd_ram[element[1]] -= 2 ** element[0] if self.lcd_ram[element[1]] & (2 ** element[0]) else 0
        self.digit_flush()

    def _clear_buffer(self, data):
        """清除时间、金额、笔数显示缓存"""
        for i in self.number_data[data[0]: data[1]]:
            for j, element in enumerate(i):
                self.lcd_ram[i[j][1]] -= 2 ** i[j][0] if self.lcd_ram[i[j][1]] & (2 ** i[j][0]) else 0

    def _set_time(self, topic=None, data=None):
        """
        设置显示时间
        data: 时间
        "11:20"
        """
        self._clear_buffer([9, 13])
        data = "%04d" % int(data.replace(":", ""))
        self.lcd_ram[self.number_data[10][7][1]] += 2 ** self.number_data[10][7][0]    # 时间值中间的:使能
        for i, value in enumerate(self.number_data[9: 13]):
            for j, element in enumerate(self.number.get(data[i])):
                self.lcd_ram[value[j][1]] += 2 ** value[j][0] if element else 0
        self.digit_flush()

    def _set_count(self, topic=None, data=None):
        self._clear_buffer([6, 9])
        for i, value in enumerate(reversed("%03d" % int(data))):
            for j, element in enumerate(self.number.get(value)):
                self.lcd_ram[self.number_data[8 - i][j][1]] += 2 ** self.number_data[8 - i][j][0] if element else 0
        self.digit_flush()

    def _set_money(self, topic=None, data=None):
        """
        设置显示金额:str
        eg: 11.20 1123.34 23.8
        """
        self._clear_buffer([0, 6])
        dot = data.find(".")
        if dot >= 0:
            self.lcd_ram[self.number_data[6 - (len(data) - dot)][7][1]] += 2 ** self.number_data[6 - (len(data) - dot)][7][0]    # 使能小数点
        data = data.replace(".", "")
        for i, value in enumerate(reversed(data)):
            for j, element in enumerate(self.number.get(value)):
                self.lcd_ram[self.number_data[5 - i][j][1]] += 2 ** self.number_data[5 - i][j][0] if element else 0
        self.digit_flush()

    def refresh_time(self, args):
        self._set_time(None, "{}{:02d}{:02d}{:02d}:{:02d}{:02d}".format(*utime.localtime())[8:13])

    def post_processor_after_initialization(self):
        subscribe("set_battery_signal", self._set_battery_signal)
        subscribe("set_4g_wifi", self._set_4g_wifi)
        subscribe("set_money", self._set_money)
        subscribe("set_time", self._set_time)
        subscribe("set_count", self._set_count)
        self._st7567_init()
        self.digit_flush_null()
        self._set_time(None, "{}{:02d}{:02d}{:02d}:{:02d}{:02d}".format(*utime.localtime())[8:13])
        self._set_count(None, 0)
        self.__timer.start(60 * 1000, 1, self.refresh_time)


if __name__ == '__main__':
    ist = LcdManager()
    ist.post_processor_after_initialization()
