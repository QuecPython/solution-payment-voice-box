import uos
from machine import Pin

# version, just modify app version, firmware version will auto get from api
firmware_version = {"firmware_version": uos.uname()[5][-5:] + "_" + "1.1.3"}

bat_table = [3400, 3550, 3605, 3650, 3705, 3755, 3805, 3855, 3875, 3905, 4015]
# 0:3400, #BATTERY_LOW_SECOND_LEVEL + BAT_LEVEL_DELTA * 8/100,   // level 0
# 10:3550, #BATTERY_LOW_SECOND_LEVEL + BAT_LEVEL_DELTA * 15/100,  // level 1   >= 3.45
# 20:3605, #BATTERY_LOW_SECOND_LEVEL + BAT_LEVEL_DELTA * 25/100,  // level 2   >= 3.60
# 30:3650, #BATTERY_LOW_SECOND_LEVEL + BAT_LEVEL_DELTA * 35/100,  // level 3   >= 3.67
# 40:3705, #BATTERY_LOW_SECOND_LEVEL + BAT_LEVEL_DELTA * 45/100,  // level 4   >= 3.70
# 50:3755, #BATTERY_LOW_SECOND_LEVEL + BAT_LEVEL_DELTA * 55/100,  // level 5   >= 3.73
# 60:3805, #BATTERY_LOW_SECOND_LEVEL + BAT_LEVEL_DELTA * 65/100,  // level 6   >= 3.78
# 70:3855, #BATTERY_LOW_SECOND_LEVEL + BAT_LEVEL_DELTA * 75/100,  // level 7   >= 3.85
# 80:3875, #/BATTERY_LOW_SECOND_LEVEL + BAT_LEVEL_DELTA * 85/100,  // level 8   >= 3.93
# 90:3905, #BATTERY_LOW_SECOND_LEVEL + BAT_LEVEL_DELTA * 90/100,  // level 9,  >= 4.00
# 100:4015


# GPIO 配置表，value 参数集合，格式[GPIO脚, 模式, 上拉配置,]
gpio_map = {
    "KEY_POWER": [Pin.GPIO1, Pin.IN, Pin.PULL_DISABLE],
    "KEY_FUNC": [Pin.GPIO17, 1, 0, 2, 200],
    "KEY_VOLUM_UP": [Pin.GPIO18, 1, 0, 2, 200],
    "KEY_VOLUM_DOWN": [Pin.GPIO29, 1, 0, 2, 200],
    "KEY_CHARGE_FULL": [Pin.GPIO26, Pin.IN, Pin.PULL_DISABLE],
    "KEY_CHARGE_CHECK": [Pin.GPIO28, Pin.IN, Pin.PULL_PU],
    "KEY_SPEAK_EN": [Pin.GPIO12, Pin.OUT, Pin.PULL_DISABLE],
}

# 按键GPIO配置表
key_map = {
    Pin.GPIO17: "KEY_FUNC",  # 69
    Pin.GPIO18: "KEY_VOLUM_UP",  # 70
    Pin.GPIO29: "KEY_VOLUM_DOWN",    # 57
    74: "KEY_POWER",   # 74
}
# 缺失音频文件
audio_array = [("DEVICE_START", "huanyingshiyongyunyinxiang.mp3", "欢迎使用云音箱"),  # 开机语音
               ("DEVICE_FACTORY", None, "工厂模式"),  # 工厂模式
               ("DEVICE_NOSIM", "weijiancedaoSIMka.mp3", "未检测到SIM卡"),
               ("DEVICE_NOPARAM", "qingxierushebeicanshu.mp3", "请写入设备参数"),
               ("DEVICE_VOLUME_MAX", "yinliangzuida.mp3", "音量最大"),
               ("DEVICE_VOLUME_MIN", "yinliangzuixiao.mp3", "音量最小"),
               ("DEVICE_VOLUME_KEY", "anjianyin.mp3", "D"),
               ("DEVICE_BAT_VALUE", "shengydlbfzhi.mp3", "剩余电量百分之"),
               ("DEVICE_BAT_LOW", "dianliangdi_qingchongdian.mp3", "电量低，请充电"),
               ("DEVICE_CHARGE_FULL", "chongdianyiwancheng.mp3", "充电已完成"),
               ("DEVICE_CHARGE_IN", "chongdianzhong.mp3", "充电中"),
               ("DEVICE_CHARGE_OUT", "chongdianyiyichu.mp3", "充电已移出"),
               ("DEVICE_NET_OK", "wangluolianjiechenggong.mp3", "网络连接成功"),
               ("DEVICE_NET_FAILED", "wangluolianjieshibai.mp3", "网络连接失败，请检查网络"),
               ("DEVICE_SERVER_OK", "fuwulianjiechenggong.mp3", "服务连接成功"),
               ("DEVICE_SERVER_FAILED", "fuwulianjieshibai.mp3", "服务连接失败"),
               ("DEVICE_NO_ORDER", "zanwushoukuanjilu.mp3", "暂无收款记录"),
               ("DEVICE_SHUTDOWN", "zhengzaiguanji.mp3", "正在关机"),
               ]

sub_map = {
    # "message":"/{}/{}/user/message",
    # "message": "/{}/{}/user/service/voiceBroadcast",
    # "update":"/{}/{}/user/update",
    # "update-err":"/{}/{}/user/update/error",
    # "get":"/{}/{}/user/get",
    "ota": "/ota/{}/{}/user/task",    # pk dn
}
pub_map = {
    # "message":"/{}/{}/user/message",
    # "get":"/{}/{}/user/get",
    "ota_info": "/ota/device/connection/{}/state",    # sn
}

