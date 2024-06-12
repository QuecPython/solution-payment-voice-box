import ujson
import utime
import _thread
from usr.utils import hmac
from usr.utils.hashlib import sha256
from umqtt import MQTTClient
from usr.common import get_logger
from usr.common import Abstract
from usr.EventMesh import subscribe, publish
from usr.const import sub_map, pub_map


class CloudManager(Abstract):
    """
    MQTT interface
    """

    def __init__(self):
        self.__server = " "   # mqtt服务器IP
        self.__port = 1883
        self.__mqtt_client = None
        self.product_key = ''  # 产品识别码
        self.product_secret = None  # 产品密钥
        self.device_name = ''  # 设备（备注）名称 (SN)
        self.device_secret = ''  # 设备密钥
        self.client_id = ''  # 客户端ID (SN)
        self.password = ""  # 密码
        self.clean_session = True  # 客户端类型 (False: 持久客户端，True: 临时的)
        self.keep_alive = 300  # 允许最长通讯时间（s）
        self.sub_topic = ''  # 订阅地址
        self.qos = 1  # 消息服务质量 0：发送者只发送一次消息，不进行重试 1：发送者最少发送一次消息，确保消息到达Broker
        self.conn_flag = False
        self.start_mqtt_flag = False
        # 订阅地址
        self.sub = {}
        self.pub = {}
        # 开机后收款笔数
        self.count = 0
        self.log = get_logger(__name__ + "." + self.__class__.__name__)

    def post_processor_after_initialization(self):
        subscribe("mqtt_connect", self.__start_mqtt_connect)
        # subscribe("cloud_pub", self.cloud_pub)
        self.device_name = publish("get_sn")  # 设备（备注）名称
        self.product_key = publish("persistent_config_get", "product_key")  # 产品识别码
        self.product_secret = publish("persistent_config_get", "product_secret")  # 产品密钥
        self.client_id = self.device_name  # 自定义
        # 订阅地址
        self.sub = sub_map
        self.pub = pub_map

    def __check_connect_param(self):
        if not self.product_key or not self.product_secret or not self.device_name:
            # 序列号未写入&串号异常&获取sn异常
            publish("audio_file_play", "DEVICE_NOPARAM")
            return False
        else:
            self.client_id = self.device_name
            self.password = hmac.new(self.product_secret.encode('utf-8'), (
                    'clientId{' + self.device_name + '}.{' + self.device_name + '}' + self.device_name + self.product_key + "2524608000000").encode(
                'utf-8'), digestmod=sha256).hexdigest().upper()
            return True

    def __start_mqtt_connect(self, topic=None, data=None):
        if self.start_mqtt_flag and self.conn_flag:
            self.log.info("重新连接MQTT")
            # 切换网络后重新连接mqtt云服务器
            try:
                self.__disconnect()
            except Exception as e:
                self.log.info("mqtt disconnect error, reason:  {}".format(e))
            self.log.info("关闭之前的MQTT连接")
            utime.sleep(1)
        self.start_mqtt_flag = True
        return self.__connect()

    def __connect(self, topic=None, data=None):
        if not self.__check_connect_param():
            return False
        if not self.conn_flag:
            self.conn_flag = True
        self.__mqtt_client = MQTTClient(self.client_id, self.__server, port=self.__port, user=self.device_name,
                                        password=self.password, keepalive=120, ssl=False, ssl_params={}, reconn=True)
        self.log.info("password: {} server: {} client_id: {} port: {} user: {}".format(self.password, self.__server,
                                                                                       self.device_name, self.__port,
                                                                                       self.device_name))
        try:
            con_state = self.__mqtt_client.connect()
        except ValueError as e:
            con_state = 1
            self.log.info("connect  error --{}".format(e))
        self.log.info("connect  con_state --{}".format(con_state))
        if con_state != 0:
            self.log.warn("mqtt connect failed!")
            return False
        self.__run()  # 持续监听消息
        self.__mqtt_client.set_callback(self.callback)
        for key, values in self.sub.items():
            try:
                print(values.format(self.product_key, self.device_name))
                self.__mqtt_client.subscribe(values.format(self.product_key, self.device_name), qos=self.qos)
            except OSError as e:
                self.log.warn("mqtt subscribe {} topic failed! error {}".format(key, e))
                return False
        self.log.info("mqtt connect success!")
        return True

    def publish(self, topic, msg):
        """mqtt 消息发布"""
        return self.__customer_pub(topic, msg)

    def callback(self, topic, msg):
        """mqtt 消息回调"""
        return self.__customer_sub(topic, msg)

    def __customer_pub(self, topic, msg):
        """publish test"""
        if not topic:
            topic = pub_map.get("ota").format(self.product_key, self.device_name)
        data = {"status": "0"}
        self.__mqtt_client.publish(topic, data, qos=0)

    def __customer_sub(self, topic, msg):
        """{"broadcast_type":2,"money":"0.01","biz_type":2,"request_id":"99711180000202012162212481044206"}"""
        if topic.decode() == sub_map.get("ota").format(self.product_key, self.device_name):
            time_stamp = "{}{:02d}{:02d}{:02d}{:02d}{:02d}".format(*utime.localtime())
            json_data = ujson.loads(msg)
            amount = json_data.get('money', "")
            request_id = json_data.get('request_id', "")
            self.log.info("json_data {}".format(json_data))
            play_list = ["收款", float(amount), "元"]
            if publish("Order_history_write",
                       {"TimeStamp": time_stamp, "MsgID": request_id, "Money": amount, "VoiceMsg": play_list}):
                self.count += 1
                publish("number_play", play_list)
                publish("set_money", amount)
                publish("set_count", self.count)
        elif topic.decode() == sub_map.get("ota").format(self.product_key, self.device_name):
            pass
            # TODO OTA demo
        else:
            pass
        return

    def __listen(self):
        while True:
            self.__mqtt_client.wait_msg()
            utime.sleep(1)

    def __run(self):
        _thread.start_new_thread(self.__listen, ())  # 监听线程

    def __disconnect(self):
        self.__mqtt_client.disconnect()


if __name__ == '__main__':
    a = CloudManager()
    a.post_processor_after_initialization()
