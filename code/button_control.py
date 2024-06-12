from machine import Key
from usr.EventMesh import publish, subscribe
from usr.common import Abstract
from misc import PowerKey
from usr.const import key_map, gpio_map

Menu_map = {
    "BaseMenu":
        {
            "action":
                {
                    "enter": None,
                    "quit": None,
                },
            "event":
                {
                    "KEY_VOLUM_DOWN_SHORT": ["reduce_audio_volume", None],
                    "KEY_VOLUM_UP_SHORT": ["add_audio_volume", None],
                    "KEY_POWER_SHORT": ["bat_value_play", None],
                    "KEY_FUNC_SHORT": ["menu_enter", "OrderMenu"],
                }
        },
    "OrderMenu":
        {
            "action":
                {
                    "enter": None,
                    "quit": [["switch", 1], ["Order_history_exit", None]]
                },
            "event":
                {
                    "KEY_VOLUM_DOWN_SHORT": ["Order_history_read", 0],
                    "KEY_VOLUM_UP_SHORT": ["Order_history_read", 1],
                    "KEY_FUNC_SHORT": ["menu_enter", "BaseMenu"],
                }
        },
    "Default":
        {
            "event":
                {
                    "KEY_VOLUM_DOWN_SHORT": ["reduce_audio_volume", None],
                    "KEY_VOLUM_UP_SHORT": ["add_audio_volume", None],
                    "KEY_POWER_SHORT": ["bat_value_play", None],
                }
        }
}


class Event(object):
    PRESSED = "SHORT"
    RELEASED = "RELEASED"
    LONG_PRESSED = "LONG"
    DOUBLE_PRESSED = "DOUBLE"
    PWK_PRESSED = "SHORT"


# 开机按键事件
class PowerFunKey(object):
    def __init__(self) -> None:
        self._pwk = PowerKey()

    def enable(self):
        self._pwk.powerKeyEventRegister(self._pwk_callback)

    def _pwk_callback(self, status):
        if status == 0:
            self._pwk_func()
        elif status == 1:
            pass

    @staticmethod
    def _pwk_func():
        event_cb([74, 1],)


class KeyManage(object):
    def __init__(self) -> None:
        # 音量 “+” 按键 (单点亮灯、长按闪灯、双击读取LED状态)
        # 音量 “-” 按键 (单点灭灯、长按闪灯、双击闪灯)
        # 功能按键
        # 开机按键事件
        self.Key_list = [Key(gpio_map.get("KEY_VOLUM_UP")[0], gpio_map.get("KEY_VOLUM_UP")[1],
                             gpio_map.get("KEY_VOLUM_UP")[2], gpio_map.get("KEY_VOLUM_UP")[3],
                             gpio_map.get("KEY_VOLUM_UP")[4], event_cb),
                         Key(gpio_map.get("KEY_VOLUM_DOWN")[0], gpio_map.get("KEY_VOLUM_DOWN")[1],
                             gpio_map.get("KEY_VOLUM_DOWN")[2], gpio_map.get("KEY_VOLUM_DOWN")[3],
                             gpio_map.get("KEY_VOLUM_UP")[4], event_cb),
                         Key(gpio_map.get("KEY_FUNC")[0], gpio_map.get("KEY_FUNC")[1],
                             gpio_map.get("KEY_FUNC")[2], gpio_map.get("KEY_FUNC")[3], gpio_map.get("KEY_VOLUM_UP")[4],
                             event_cb),
                         PowerFunKey()
                         ]

    def enable(self):
        for i in self.Key_list:
            i.enable()


# 触发事件在此定义
def event_cb(*args):
    k, event = args[0][0], args[0][1]
    if event == 1:
        if type(k) == int:
            Key = key_map.get(k)
        else:
            Key = key_map.get(k.pin)
        print(Key + '_' + Event.PRESSED)
        publish("key_event", Key + '_' + Event.PRESSED)
    if event == 2:
        pass
        # TODO long press func
    if event == 3:
        pass
        # TODO double press func


class MenuManager(Abstract):
    def __init__(self):
        self.key = KeyManage()
        self.key.enable()
        self.menu = "BaseMenu"
        self.flag = 0
        subscribe("key_event", self.key_event)
        subscribe("time_event", self.time_event)
        subscribe("menu_enter", self.menu_enter)

    def key_event(self, topic=None, msg=None):
        # print("self.menu:", self.menu)
        # print("msg:", msg)
        args = Menu_map.get(self.menu).get("event").get(msg)
        if args:
            # print("args:", args)
            publish(args[0], args[1])
        else:
            args = Menu_map.get("Default").get("event").get(msg)
            if args:
                publish(args[0], args[1])

    def time_event(self, topic=None, msg=None):
        pass

    def menu_enter(self, topic=None, msg=None):
        if msg != self.menu:
            # 先退出当前模式,执行退出动
            args = Menu_map.get(self.menu).get("action").get("quit")
            if args:
                for i in range(len(args)):
                    publish(args[i][0], args[i][1])
            # 切换标题，并将flag置为0
            self.menu = msg
            # enter 执行进入动作
            args = Menu_map.get(self.menu).get("action").get("enter")
            if args:
                for i in range(len(args)):
                    publish(args[i][0], args[i][1])
                self.flag += 1
        else:
            pass


if __name__ == "__main__":
    menu = MenuManager()
    menu.post_processor_before_initialization()
