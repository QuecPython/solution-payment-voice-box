"""
LED 三色指示灯管理
"""

import utime
import _thread
from machine import Pin
from usr.EventMesh import subscribe
from usr.common import get_logger, Abstract


class Light(Abstract):
    def __init__(self):
        self.RGB_ENABLE = Pin(Pin.GPIO21, Pin.OUT, Pin.PULL_DISABLE, 1)
        self.R_light = Pin(Pin.GPIO11, Pin.OUT, Pin.PULL_PU, 0)
        self.G_light = Pin(Pin.GPIO13, Pin.OUT, Pin.PULL_PU, 0)
        self.B_light = Pin(Pin.GPIO14, Pin.OUT, Pin.PULL_PU, 0)
        self.RGB_RED = 0x01
        self.RGB_GREEN = 0x02
        self.RGB_BLUE = 0x04
        self.thread_id = None  # 闪烁线程ID
        self.log = get_logger(__name__ + "." + self.__class__.__name__)

    def light_enable(self, topic=None, data=None):
        if data:
            self.RGB_ENABLE.write(1)
        else:
            self.RGB_ENABLE.write(0)

    def switch(self, topic=None, data=None):
        self.R_light.write(1) if data & self.RGB_RED else self.R_light.write(0)
        self.G_light.write(1) if data & self.RGB_GREEN else self.G_light.write(0)
        self.B_light.write(1) if data & self.RGB_BLUE else self.B_light.write(0)

    def blink(self, topic=None, data=None):
        while True:
            self.thread_id = _thread.get_ident()
            blink_light = list()
            blink_light.append(self.R_light) if data[0] & self.RGB_RED else None
            blink_light.append(self.G_light)if data[0] & self.RGB_GREEN else None
            blink_light.append(self.B_light) if data[0] & self.RGB_BLUE else None
            for i in blink_light:
                i.write(1)
            utime.sleep(data[1])
            for i in blink_light:
                i.write(0)
            utime.sleep(data[1])

    def close(self, topic=None, data=None):
        _thread.stop_thread(self.thread_id)
        self.switch(None, 0)

    def post_processor_after_initialization(self):
        """订阅此类所有的事件到 EventMesh中"""
        subscribe("light_enable", self.light_enable)
        subscribe("light_switch", self.switch)
        subscribe("light_blink", self.blink)
        subscribe("blink_close", self.close)


if __name__ == '__main__':
    a = Light()
    a.post_processor_after_initialization()
    # publish("light_enable", 1)


