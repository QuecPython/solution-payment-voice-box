import sim
import utime
import modem
import net
import _thread
import dataCall
import osTimer
import checkNet
import ql_fs
from machine import Pin, UART, ExtInt
from misc import PowerKey, Power
from usr.common import get_logger, Lock, Abstract
from usr.EventMesh import publish, subscribe
from usr.const import gpio_map, bat_table


class HistoryOrderManager(Abstract):
    def __init__(self, max_hist_num=10):
        self.file_name = "/usr/history_order.json"
        self.map = dict(order=[])
        self.Cnt = 0
        self.lock = Lock()
        self.__max_hist_num = max_hist_num

    def post_processor_after_initialization(self):
        if ql_fs.path_exists(self.file_name):
            file_map = ql_fs.read_json(self.file_name)
            self.map = file_map
        else:
            ql_fs.touch(self.file_name, self.map)
        subscribe("Order_history_read", self.__read)
        subscribe("Order_history_write", self.__write)
        subscribe("Order_history_exit", self.__exit)

    def __read(self, event, msg):
        """
        params : 0 上一笔  1 下一笔
        """
        with self.lock:
            order_len = len(self.map.get("order"))
            if order_len == 0:
                return False
            if msg == 0:
                if self.Cnt < order_len:
                    self.Cnt += 1
                print(self.Cnt)
            else:
                if self.Cnt > 1:
                    self.Cnt -= 1
                if self.Cnt == 0:
                    self.Cnt = 1
                print(self.Cnt)
            publish("number_play", ["收款", float(self.map.get("order")[self.Cnt * -1].get("Money")), "元"])
            publish("set_money", self.map.get("order")[self.Cnt * -1].get("Money"))
            # return self.map.get("order")[self.Cnt * -1]

    def __exit(self, event, msg):
        self.Cnt = 0

    def __write(self, event, msg):
        order_list = self.map.get("order", [])
        for k in reversed(order_list):
            if msg == k:
                return False
        order_list.append(msg)
        with self.lock:
            if len(order_list) > self.__max_hist_num:
                self.map.update({"order": order_list[-self.__max_hist_num:]})
            ql_fs.touch(self.file_name, self.map)
        return True


class DeviceInfoManager(Abstract):
    """设备信息管理"""

    def __init__(self):
        self.__iccid = ""
        self.__imei = ""
        self.__fw_version = ""
        self.__sn = ""
        self.log = get_logger(__name__ + "." + self.__class__.__name__)

    def post_processor_after_instantiation(self):
        # 注册事件
        subscribe("get_sim_iccid", self.get_iccid)
        subscribe("get_device_imei", self.get_imei)
        subscribe("get_fw_version", self.get_device_fw_version)
        subscribe("get_csq", self.get_csq)
        subscribe("get_sn", self.get_sn)

    def get_iccid(self, event=None, msg=None):
        """查询 ICCID"""
        if self.__iccid == "":
            msg = sim.getIccid()
            if msg != -1:
                self.__iccid = msg
            else:
                self.log.warn("get sim iccid fail, please check sim")
        return self.__iccid

    def get_imei(self, event=None, msg=None):
        """查询 IMEI"""
        if self.__imei == "":
            self.__imei = modem.getDevImei()
        return self.__imei

    def get_device_fw_version(self, event=None, msg=None):
        """查询 固件版本"""
        if self.__fw_version == "":
            self.__fw_version = modem.getDevFwVersion()
        return self.__fw_version

    @staticmethod
    def get_csq(self, event=None, msg=None):
        """查询 信号值"""
        return net.csqQueryPoll()

    def get_sn(self, event=None, msg=None):
        """查询SN"""
        if self.__sn == "":
            self.__sn = modem.getDevSN()
        return self.__sn


class DeviceActionManager(Abstract):
    """
    设备行为
    """

    def __init__(self):
        self.__led_flag = 1
        self.__await_start_time = 0
        self.__lock = Lock()
        self.log = get_logger(__name__ + "." + self.__class__.__name__)

    def post_processor_after_initialization(self):
        # 注册事件
        subscribe("device_start", self.device_start)
        subscribe("device_shutdown", self.device_shutdown)
        subscribe("device_restart", self.device_restart)

    def device_shutdown(self, topic=None, data=None):
        # 设备关机
        # publish("audio_play", AUDIO_FILE_NAME.DEVICE_SHUTDOWN)
        pass
        utime.sleep(5)
        Power.powerDown()

    def device_start(self, topic=None, data=None):
        # 设备开机
        # publish("audio_play", AUDIO_FILE_NAME.DEVICE_START)
        pass

    def device_restart(self, topic=None, data=None):
        # 设备重启
        Power.powerRestart()


class ChargeManager(Abstract):
    """
    电池管理
    充电管理
    """

    def __init__(self):
        self.__bat_value = None
        self.__charge_full_pin = None
        self.__charge_check_pin = None
        self.__tip_charge_full = False
        self.__tip_low_power = True
        self.log = get_logger(__name__ + "." + self.__class__.__name__)

    def post_processor_after_initialization(self):
        if "KEY_CHARGE_FULL" in gpio_map:
            self.__charge_full_pin = Pin(gpio_map["KEY_CHARGE_FULL"][0], gpio_map["KEY_CHARGE_FULL"][1],
                                         gpio_map["KEY_CHARGE_FULL"][2], 0)  # 正常是False 充满是True
        if "KEY_CHARGE_CHECK" in gpio_map:
            self.__charge_check_pin = Pin(gpio_map["KEY_CHARGE_CHECK"][0], gpio_map["KEY_CHARGE_CHECK"][1],
                                          gpio_map["KEY_CHARGE_CHECK"][2], 0)  # 充电检测
        subscribe("bat_value_play", self.bat_value_play)
        # _thread.start_new_thread(self.check_charge_state_task, ())
        _thread.start_new_thread(self.check_battery_v, ())

    def check_charge_state_task(self):
        # 检查充电状态
        while True:
            if not self.__charge_check_pin.read():
                self.bat_charge_in()
                publish("green_on")
            else:
                self.bat_charge_out()
            utime.sleep_ms(1000)
            # TODO  CHARGE LED

    def check_battery_v(self):
        mv_list = list()
        while True:
            if self.__bat_value:
                utime.sleep(60)
            if self.__charge_full_pin.read():
                self.bat_charge_full()
            mv = Power.getVbatt()
            # self.log.info("Checking battery mv {}".format(mv))
            mv_list.append(mv)
            if len(mv_list) >= 6:
                self.__bat_value = self.check_battery_o(mv_list)
                mv_list = mv_list[1:]
                if self.__bat_value >= 8:
                    publish("set_battery_signal", (0, 4))
                elif 5 <= self.__bat_value < 8:
                    publish("set_battery_signal", (0, 3))
                elif 1 < self.__bat_value < 5:
                    publish("set_battery_signal", (0, 2))

                signal = publish("get_csq")
                if 25 < signal <= 31:
                    publish("set_battery_signal", (1, 5))
                elif 20 < signal <= 25:
                    publish("set_battery_signal", (1, 4))
                elif 16 < signal <= 20:
                    publish("set_battery_signal", (1, 3))
                elif 12 < signal <= 16:
                    publish("set_battery_signal", (1, 2))
                elif 9 < signal <= 12:
                    publish("set_battery_signal", (1, 1))
                else:
                    publish("set_battery_signal", (1, 0))

                if self.__bat_value > 1:
                    self.__tip_low_power = True
                elif self.__bat_value == 1:  # 请充电
                    if self.__tip_low_power:
                        self.__tip_low_power = False
                        publish("audio_file_play", "DEVICE_BAT_LOW")
                        publish("set_battery_signal", (0, 1))
                if self.__bat_value == 0:  # 关机
                    publish("device_shutdown")
            utime.sleep_ms(100)

    @staticmethod
    def check_battery_o(mv_list):
        # 检查电池电量
        # reduce max min value
        mv_list.remove(max(mv_list))
        mv_list.remove(min(mv_list))
        mv = float(sum(mv_list)) / len(mv_list)
        for vol in bat_table:
            if vol <= mv:
                continue
            else:
                return bat_table.index(vol)
        return len(bat_table)

    def bat_value_play(self, topic=None, data=None):
        """bat get value and play"""
        bat_val = (self.__bat_value - 1) * 10 if self.__bat_value > 2 else 0
        if 0 < bat_val[0]:
            publish("audio_file_play", "DEVICE_BAT_VALUE")
            publish("number_play", list(bat_val))
        print(bat_val)

    def bat_charge_in(self):
        if not self.__tip_charge_full:
            self.__tip_charge_full = True
            publish("audio_file_play", "DEVICE_CHARGE_IN")

    def bat_charge_out(self):
        self.__tip_charge_full = False
        publish("audio_file_play", "DEVICE_CHARGE_OUT")

    def bat_charge_full(self):
        if self.__tip_charge_full:
            self.__tip_charge_full = False
            publish("audio_file_play", "DEVICE_CHARGE_FULL")


class LteNetManager(Abstract):
    """LTE 网络管理"""

    def __init__(self):
        self.__data_call = dataCall
        self.__net = net
        self.__data_call_flag = False
        self.__timer = osTimer()
        self.__net_error_mode = 0
        self.check_net = checkNet.CheckNetwork("QuecPython_yunlaba", "this latest version")
        self.check_net_timeout = 100 * 1000
        self.log = get_logger(__name__ + "." + self.__class__.__name__)

    def post_processor_after_initialization(self):
        self.data_call_start()

    def data_call_start(self):
        sim_state = False
        for i in range(1, 5):
            if sim.getStatus() == 1:
                sim_state = True
                break
            utime.sleep(1)
        if not sim_state:
            self.log.error("sim state is error")
            self.__net_error_mode = 0
            publish("audio_file_play", "DEVICE_NOSIM")
            return 0
        self.wait_connect(30)

    def data_call_stop(self, topic=None, data=None):
        self.net_error_audio_stop()

    def wait_connect(self, timeout):
        """等待设备找网"""
        self.log.info("wait net -----------")
        stagecode, subcode = self.check_net.wait_network_connected(timeout)
        if stagecode == 3 and subcode == 1:
            # 注网成功
            publish("audio_file_play", "DEVICE_NET_OK")
            publish("set_4g_wifi", 0)
            self.log.info("module net success, run mqtt connect")
            if publish('mqtt_connect'):
                publish("audio_file_play", "DEVICE_SERVER_OK")
            else:
                publish("audio_file_play", "DEVICE_SERVER_FAILED")
            self.net_error_audio_stop()
        else:
            # 注网失败
            self.__net_error_mode = 1
            self.log.error("module net fail, wait try again")
            self.net_error_audio_start()
            publish("audio_file_play", "DEVICE_NET_FAILED")
            self.net_fail_process()
        self.__data_call.setCallback(self.net_state_cb)

    def net_fail_process(self):
        # 注网失败，尝试Cfun后重新找网，若Cfun失败则模组重启
        state = net.setModemFun(0)
        if state == -1:
            self.log.error("cfun net mode error, device will restart.")
            utime.sleep(5)
            # Power.powerRestart()
        state = net.setModemFun(1)
        if state == -1:
            self.log.error("cfun net mode error, device will restart.")
            utime.sleep(5)
            # Power.powerRestart()
        self.log.info("cfun net mode success, note the net again")
        self.wait_connect(30)

    def net_error_audio_task(self, timer):
        if self.__net_error_mode:
            publish("audio_file_play", "DEVICE_NOSIM")
        else:
            publish("audio_file_play", "DEVICE_NET_FAILED")

    def net_error_audio_start(self):
        self.__timer.stop()
        self.__timer.start(60 * 1000, 1, self.net_error_audio_task)

    def net_error_audio_stop(self):
        self.__timer.stop()

    def net_state_cb(self, args):
        """网络状态变化，会触发该回调函数"""
        nw_sta = args[1]
        if nw_sta == 1:
            publish("audio_file_play", "DEVICE_NET_OK")
            self.log.info("network connected!")
            self.net_error_audio_stop()
        else:
            self.net_error_audio_start()
            publish("audio_file_play", "DEVICE_NET_FAILED")
            self.log.info("network not connected!")
