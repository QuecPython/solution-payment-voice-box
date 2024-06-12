# -*- coding: UTF-8 -*-
"""
Audio TTS 功能

AUDIO_FILE_NAME :音频文件
TTS_CONTENT:TTS播报内容
AudioManager: audio 功能管理
"""

import audio
from machine import Pin
from usr.common import get_logger, Abstract
from usr.EventMesh import subscribe, publish
from usr.const import gpio_map, audio_array


class AudioManager(Abstract):
    """
    音频文件播放
    TTS 播报管理(拼接)
    """

    def __init__(self):
        self.__audio = audio.Audio(0)
        self.__audio_volume = 3
        self.__tts_priority = 3
        self.__tts_break_in = 0
        self.__audio_mode = ""
        self.__speak_en_pin = None
        self.__volume_level = {
            1: 1,
            2: 3,
            3: 6,
            4: 9,
            5: 11
        }
        self.__MERGE_MP3_FILE = "U:/audio_file/audio.bin"
        self.__MP3_HEAR = 'mp3files='
        self.amount_data = ['0', '1', '10', '100', '1000', '10000', '2', '3', '4', '5', '6', '7', '8', '9', '元', '到账',
                            '收款', '点']
        self.log = get_logger(__name__ + "." + self.__class__.__name__)

    def post_processor_after_initialization(self):
        self.__set_audio_pa()
        self.__audio_volume = publish("persistent_config_get", "volume")
        self.__audio_mode = publish("persistent_config_get", "audio_mode")
        if not self.__audio_volume:
            self.__audio_volume = 5
        # 设置TTS音量
        self.__audio.setVolume(self.__volume_level.get(self.__audio_volume))
        subscribe("audio_file_play", self.audio_file_play)
        subscribe("number_play", self.number_play)
        subscribe("audio_bat_play", self.audio_bat_play)
        subscribe("audio_play_stop", self.audio_play_stop)
        subscribe("get_audio_state", self.get_audio_state)
        subscribe("add_audio_volume", self.add_audio_volume)
        subscribe("reduce_audio_volume", self.reduce_audio_volume)
        self.audio_file_play(None, "DEVICE_START")

    def __set_audio_pa(self):
        """Set audio pa"""
        state = self.__audio.set_pa(Pin.GPIO12, 2)
        if not state:
            self.log.warn("set audio pa error!")

    def __audio_lib_play(self, play_list=None, merge_file=None, lib_list=None):
        """Play lib audio"""
        file_list = self.__MP3_HEAR
        for item in play_list:
            if isinstance(item, int) or isinstance(item, float):
                if len(file_list) == len(self.__MP3_HEAR):
                    file_list = file_list + self.__digital_to_audio_file(item, lib_list)
                else:
                    file_list = file_list + '+' + self.__digital_to_audio_file(item, lib_list)
            else:
                if len(file_list) == len(self.__MP3_HEAR):
                    file_list = file_list + self.__text_to_index(item, lib_list) + '.mp3'
                else:
                    file_list = file_list + '+' + self.__text_to_index(item, lib_list) + '.mp3'
        print(file_list)
        self.__audio.montage_play(merge_file, 3, 0, file_list)
        return True

    @staticmethod
    def __text_to_index(text, lib_list):
        try:
            text_index = str(lib_list.index(text))
            return text_index
        except ValueError as Error:
            print("[ERROR]: %s is not in audio" % text)
            return None

    def __digital_to_audio_file(self, number, lib_list):
        decimal, result = "", []
        if isinstance(number, float):
            lis = str(number).split(".")
            number = int(lis[0])
            decimal = lis[1][:2]
        if isinstance(number, int):
            if 10 >= number >= 0:
                result = [self.__text_to_index(str(number), lib_list) + '.mp3']
            elif number < 20:
                result = [self.__text_to_index(str(10), lib_list) + '.mp3',
                          self.__text_to_index(str(number % 10), lib_list) + '.mp3']
            elif 20 <= number < 100000:
                ns = str(number)
                text = []
                zero = self.__text_to_index("0", lib_list) + '.mp3'
                length = len(ns)
                for i in range(length):
                    if ns[i] == "0":
                        text.append(zero)
                    else:
                        if i == length - 1:
                            text.append(self.__text_to_index(ns[i], lib_list) + '.mp3')
                        else:
                            text.append(self.__text_to_index(ns[i], lib_list) + '.mp3' + '+' + self.__text_to_index(
                                "1" + "0" * (length - 1 - i), lib_list) + '.mp3')
                prev = object()
                for i in text:
                    if prev != i:
                        prev = i
                        result.append(prev)
                result = result[:-1] if result[-1] == zero else result
            else:
                print("invalid number:%d" % number)
                return False
        if decimal:
            result.append(self.__text_to_index("点", lib_list) + '.mp3')
            for i in decimal:
                result.append(self.__text_to_index(i, lib_list) + '.mp3')
        return "+".join(result)

    def audio_play(self, topic=None, filename=None):
        """Play audio"""
        if filename is None:
            return
        state = self.__audio.play(self.__tts_priority, self.__tts_break_in, filename)
        return True if state == 0 else False

    def number_play(self, topic=None, content=None):
        """Play tts number"""
        if content is None:
            return
        self.__audio_lib_play(content, self.__MERGE_MP3_FILE, self.amount_data)

    def audio_file_play(self, topic=None, msg=None):
        """Play File audio"""
        state = False
        for arg in audio_array:
            if arg[0] == msg:
                ture_filename = "U:/audio_file/" + arg[1]
                state = self.audio_play(None, ture_filename)
                self.log.info(msg)
                break
        else:
            self.log.info("待播音频文件不存在: {}".format(msg))
        return state

    def audio_bat_play(self, topic=None, number=None):
        """Play bat value audio"""
        self.audio_file_play(None, "DEVICE_BAT_VALUE")
        self.number_play(number)
        return True

    def audio_play_stop(self, topic=None, data=None):
        """audio stop"""
        state = self.__audio.stop()
        return True if state == 0 else False

    def get_audio_state(self, topic=None, data=None):
        """get audio state"""
        state = self.__audio.getState()
        return True if state == 0 else False

    def get_audio_volume(self, topic=None, data=None):
        """get audio volume"""
        return self.__audio_volume

    def add_audio_volume(self, topic=None, vol_num=None):
        """添加音量"""
        vol_num = self.__audio_volume + 1
        self.__audio_volume = 5 if vol_num > 5 else vol_num
        self.__set_audio_volume(self.__volume_level.get(self.__audio_volume))

    def reduce_audio_volume(self, topic=None, vol_num=None):
        """减少音量"""
        vol_num = self.__audio_volume - 1
        self.__audio_volume = 1 if vol_num < 1 else vol_num
        self.__set_audio_volume(self.__volume_level.get(self.__audio_volume))

    def __set_audio_volume(self, vol_num):
        """set audio volume"""
        print("__set_audio_volume vol num = %d" % self.__audio_volume)
        if self.__audio_volume >= 5:
            self.audio_file_play(None, "DEVICE_VOLUME_MAX")
        elif self.__audio_volume <= 1:
            self.audio_file_play(None, "DEVICE_VOLUME_MIN")
        else:
            self.audio_file_play(None, "DEVICE_VOLUME_KEY")
        self.__audio.setVolume(vol_num)
        publish("persistent_config_store", {"volume": self.__audio_volume})


if __name__ == '__main__':
    a = AudioManager()
    a.post_processor_after_initialization()
