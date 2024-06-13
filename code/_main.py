from usr.audio_control import AudioManager
from usr.cloud import CloudManager
from usr.common import ConfigStoreManager, Abstract
from usr.led_control import Light
from usr.button_control import MenuManager
from usr.lcd_control import LcdManager
from usr.mgr import DeviceInfoManager, DeviceActionManager, ChargeManager, LteNetManager, HistoryOrderManager


class App(object):
    def __init__(self):
        self.managers = []

    def append_manager(self, manager):
        if isinstance(manager, Abstract):
            manager.post_processor_after_instantiation()
            self.managers.append(manager)
        return self

    def start(self):
        for manager in self.managers:
            manager.post_processor_before_initialization()
            manager.initialization()
            manager.post_processor_after_initialization()


if __name__ == '__main__':
    app = App()
    # app initialization

    app.append_manager(ConfigStoreManager())
    app.append_manager(AudioManager())
    app.append_manager(Light())
    app.append_manager(LcdManager())
    app.append_manager(DeviceInfoManager())
    app.append_manager(DeviceActionManager())
    app.append_manager(CloudManager())
    app.append_manager(LteNetManager())
    app.append_manager(HistoryOrderManager())
    app.append_manager(ChargeManager())
    app.append_manager(MenuManager())

    # start
    app.start()
