import request, fota
import uzlib as zlib
import ql_fs
import app_fota_download
import uos
import usys
from usr.EventMesh import publish
from misc import Power
import utime


class FileDecode(object):
    """整包升级"""

    def __init__(self, zip_file, parent_dir="/fota/usr/"):
        self.data = b''
        self.fp = open(zip_file, "rb")
        self.fileData = None
        self.parent_dir = parent_dir
        self.update_file_list = []

    def get_update_files(self):
        return self.update_file_list

    def unzip(self):
        """缓存到内存中"""
        self.fp.seek(10)
        self.fileData = zlib.DecompIO(self.fp, -15)

    @classmethod
    def _ascii_trip(cls, data):
        return data.decode('ascii').rstrip('\0')

    @classmethod
    def file_size(cls, data):
        """获取真实size数据"""
        size = cls._ascii_trip(data)
        if not len(size):
            return 0
        return int(size, 8)

    @classmethod
    def get_file_name(cls, file_name):
        """获取文件名称"""
        return cls._ascii_trip(file_name)

    def get_data(self):
        return self.fileData.read(0x200)

    def unpack(self):
        try:
            folder_list = set()
            self.data = self.get_data()
            while True:
                if not self.data:
                    # print("no data")
                    break
                print(self.data[124:135])
                size = self.file_size(self.data[124:135])
                file_name = "/usr/" + self.get_file_name(self.data[:100])
                full_file_name = self.parent_dir + file_name
                if not ql_fs.path_exists(ql_fs.path_dirname(full_file_name)):
                    ql_fs.mkdirs(ql_fs.path_dirname(full_file_name))
                if not size:
                    if len(full_file_name):
                        ql_fs.mkdirs(full_file_name)
                        if full_file_name not in folder_list and full_file_name != self.parent_dir:
                            folder_list.add(full_file_name)
                            print("Folder {} CREATED".format(full_file_name))
                    else:
                        return
                    self.data = self.get_data()
                else:
                    print("FILE {} WRITE BYTE SIZE = {}".format(full_file_name, size))
                    self.data = self.get_data()
                    update_file = open(full_file_name, "wb+")
                    total_size = size
                    while True:
                        size -= 0x200
                        if size <= 0:
                            update_file.write(self._ascii_trip(self.data))
                            break
                        else:
                            update_file.write(self.data)
                        self.data = self.get_data()
                    self.data = self.get_data()
                    update_file.close()
                    self.update_file_list.append({"file_name": file_name, "size": total_size})
        except Exception as e:
            usys.print_exception(e)
            print("unpack error = {}".format(e))
            return False
        else:
            return True

    def update_stat(self):
        for f in self.update_file_list:
            print("f = {}".format(f))
            app_fota_download.update_download_stat(f["file_name"], f["file_name"], f["size"])

    @staticmethod
    def set_flag():
        with open(app_fota_download.get_update_flag_file(), "w") as f:
            f.write("{upgrade}")


tar_src = "/usr/YM.zip"


class Upgrade(object):
    """OTA升级"""

    def __init__(self, url, version):
        self.fota_obj = fota(reset_disable=1)
        self.url = url
        self.version = version
        self.app_update()

    def app_update(self):
        # 升级软件接口
        resp = request.get(self.url)
        fp = open(tar_src, 'wb+')
        content = resp.content
        print("开始整包写入下载文件")
        try:
            while True:
                c = next(content)
                length = len(c)
                for i in range(0, length, 4096):
                    fp.write(c[i:i + 4096])
        except:
            fp.close()
            resp.close()
            download_result = 0
        else:
            fp.close()
            resp.close()
            uos.remove(tar_src)
            download_result = 1
        print("http下载升级文件结果为:{}".format(download_result))
        if download_result == 0:
            app_fota_download.app_fota_pkg_mount.mount_disk()
            fd = FileDecode(tar_src, parent_dir=app_fota_download.get_updater_dir())
            fd.unzip()
            stat = fd.unpack()
            if stat:
                uos.remove(tar_src)
                fd.update_stat()
                fd.set_flag()
                # Power...RESTART 操作
                print("整包解压缩success")
            else:
                print("整包解压缩failed")
                download_result = 1
        print("开始上报升级状态")
        if download_result == 0:
            self.update_stat(download_result)
        else:
            self.update_stat(download_result)

    def update_stat(self, result_code):
        """上报升级状态"""
        publish("persistent_config_store", {"ota": result_code, "firmware_version": self.version})
        # TODO 上报成功参数 待定
        utime.sleep(5)
        Power.powerRestart()
