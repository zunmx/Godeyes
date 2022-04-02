import json
import re, requests
from netaddr import IPNetwork as ipTrans
import modules.mysqlOper as GEdb
from modules import GSystem as GEsys
import struct
import socket
from datetime import datetime
import zlib

source = GEsys.getConfigItem("ipTable", "source")
current = GEsys.getConfigItem("ipTable", "currentVersion")
if source == 'CZ88':
    ver_url = 'http://update.cz88.net/ip/copywrite.rar'
    db_url = 'http://update.cz88.net/ip/qqwry.rar'
    headers = {
        'User-agent': 'Mozilla/3.0 (compatible; Indy Library)',
        'Accept': 'text/html, */*',
        'Host': 'update.cz88.net'
    }


def int3(data, offset):
    return data[offset] + (data[offset + 1] << 8) + \
           (data[offset + 2] << 16)


def int4(data, offset):
    return data[offset] + (data[offset + 1] << 8) + \
           (data[offset + 2] << 16) + (data[offset + 3] << 24)


class wrydb:
    def __init__(self):
        self.clear()

    def clear(self):
        self.idx1 = None
        self.idx2 = None
        self.idxo = None
        self.data = None
        self.index_begin = -1
        self.index_end = -1
        self.index_count = -1
        self.__fun = None

    def load_file(self, filename, loadindex=False):
        self.clear()
        if type(filename) == bytes:
            self.data = buffer = filename
            filename = 'memory data'
        elif type(filename) == str:
            # read file
            try:
                with open(filename, 'br') as f:
                    self.data = buffer = f.read()
                    self.data2 = open(filename, 'rb')
            except Exception as e:
                print('[!] Open or load failed：', e)
                self.clear()
                return False

            if self.data == None:
                print('[!] %s load failed' % filename)
                self.clear()
                return False
        else:
            self.clear()
            return False

        if len(buffer) < 8:
            print('[!] %s load failed, file only %d bytes' %
                  (filename, len(buffer))
                  )
            self.clear()
            return False
        index_begin = int4(buffer, 0)
        index_end = int4(buffer, 4)
        if index_begin > index_end or \
                (index_end - index_begin) % 7 != 0 or \
                index_end + 7 > len(buffer):
            print('[!] %s index error' % filename)
            self.clear()
            return False
        self.index_begin = index_begin
        self.index_end = index_end
        self.index_count = (index_end - index_begin) // 7 + 1

        if not loadindex:
            print('[#] %s %s bytes, %d segments.' %
                  (filename, format(len(buffer), ','), self.index_count)
                  )
            self.__fun = self.raw_search
            return True

    def __get_addr(self, offset):
        # mode 0x01, full jump
        mode = self.data[offset]
        if mode == 1:
            offset = int3(self.data, offset + 1)
            mode = self.data[offset]
        if mode == 2:
            off1 = int3(self.data, offset + 1)
            c = self.data[off1:self.data.index(b'\x00', off1)]
            offset += 4
        else:
            c = self.data[offset:self.data.index(b'\x00', offset)]
            offset += len(c) + 1
        if self.data[offset] == 2:
            offset = int3(self.data, offset + 1)
        p = self.data[offset:self.data.index(b'\x00', offset)]
        return str(c.decode('gb18030', errors='replace')) + " " + str(p.decode('gb18030', errors='replace'))

    def raw_search(self, ip):
        l = 0
        r = self.index_count
        while r - l > 1:
            m = (l + r) // 2
            offset = self.index_begin + m * 7
            new_ip = int4(self.data, offset)
            if ip < new_ip:
                r = m
            else:
                l = m

        offset = self.index_begin + 7 * l
        ip_begin = int4(self.data, offset)
        offset = int3(self.data, offset + 4)
        ip_end = int4(self.data, offset)

        if ip_begin <= ip <= ip_end:
            return self.__get_addr(offset + 4)
        else:
            return None

    def toip(self, hexip):
        return socket.inet_ntoa(struct.pack(">I", hexip))

    def dump(self):
        db = GEdb.createConnect()
        l = 0
        r = self.index_count
        GEsys.System_Status = "[#] 清理数据表"
        cursor = db.cursor()
        cursor.execute("truncate table godeyes_ipdb")
        db.commit()
        GEsys.System_Status = "[#] 准备写入数据库"
        commit_num = GEsys.getConfigItem("ipTable", "commit_num")
        for m in range(l, r):
            offset = self.index_begin + m * 7
            ip_begin = int4(self.data, offset)
            offset = int3(self.data, offset + 4)
            ip_end = int4(self.data, offset)
            address = self.__get_addr(offset + 4)
            startip = self.toip(ip_begin)
            endip = self.toip(ip_end)
            startip_iton = ip_begin
            endip_iton = ip_end
            cursor = db.cursor()
            sql = "insert into godeyes_ipdb(startip, endip, startip_iton, endip_iton, address) values (%s,%s,%s,%s,%s)"
            cursor.execute(sql, (startip, endip, startip_iton, endip_iton, address))
            if m % commit_num == 0 or m == r - 1:
                db.commit()
                GEsys.System_Status = "已完成: " + str(m) + ", 总计: " + str(r) + "  百分比 : " + str(
                    "%.3f" % (int(m) / int(r) * 100))
        GEdb.closeConnection(db,cursor)
        return True


def checkIpInvalid(iplist):
    try:
        iplist = ipTrans(iplist)
        article_info = {}
        data = json.loads(json.dumps(article_info))
        s = "ojbk"
        article2 = {'ipCount': len(iplist), "start": str(iplist[0]), "end": str(iplist[len(iplist) - 1])}
        data[str(s)] = article2
        return data
    except Exception as e:
        article_info = {}
        data = json.loads(json.dumps(article_info))
        s = "Error"
        article2 = {'code': -1, 'details': str(e)}
        data[str(s)] = article2
        return data


def getIPList(ip):
    try:
        return ipTrans(ip)
    except:
        return ip

def IPDRecord_Oper(req, code, arg1, arg2):
    if req == "getIPDBRecord":
        return GEdb.IPDBRecordOper(req, code, arg1, arg2)


def checkIPDBVersion(sourceFile =None):
    article_info = {}
    data = json.loads(json.dumps(article_info))
    s = "ojbk"
    if source == 'CZ88':
        try:
            res = requests.get(ver_url, headers=headers, timeout=5, verify=False)
        except:
            article2 = {'code': -1, 'details': "网络故障，IP源服务器故障或爬虫认证过期,请稍后重试."}
            data[str(s)] = article2
            return data
        res.encoding = "gbk"
        try:
            text = res.text
            year = re.findall(r'(?=20).+?(?=年)', text)[0]
            month = re.findall(r'(?=年).+.(?=月)', text)[0].split('年')[1]
            day = re.findall(r'(?=月).+.(?=日)', text)[0].split('月')[1]
            nowD = str(datetime.now().year) + "-" + str(datetime.now().month) + "-" + str(datetime.now().day)
            ipserviceD = str(year) + "-" + str(month) + "-" + str(day)
            if nowD != ipserviceD:
                last = (year + "-" + month + "-" + day)
                article2 = {'code': 0,
                            'version': last,
                            'details': (last == current)}
            else:
                article2 = {'code': -1, 'details': "IP源服务器故障或爬虫认证过期,请稍后重试."}
            data[str(s)] = article2
            return data
        except Exception as e:
            article2 = {'code': -1, 'details': "IP源服务器故障或爬虫认证过期,请稍后重试."}
            data[str(s)] = article2
            return data

def get_lasetst_db(filename):
    GEsys.STOP = True
    article_info = {}
    rst = json.loads(json.dumps(article_info))
    s = "ojbk"

    def get_content(url):
        res = requests.get(url, headers=headers, timeout=60)
        return res

    GEsys.System_Status = "[#] 正在下载版本文件..."
    data = get_content(ver_url)
    GEsys.System_Status = "[#] 正在检查版本文件..."
    if not data.content:
        article2 = {'code': -1,
                    'details': "下载版本信息失败"}
        data[str(s)] = article2
        return data

    data.encoding = "gbk"
    try:
        text = data.text
        year = re.findall(r'(?=20).+?(?=年)', text)[0]
        month = re.findall(r'(?=年).+.(?=月)', text)[0].split('年')[1]
        day = re.findall(r'(?=月).+.(?=日)', text)[0].split('月')[1]
        last = (year + "-" + month + "-" + day)
    except Exception as e:
        GEsys.System_Status = "解析失败"
        article2 = {'code': -1,
                    'details': "解析失败,可能是目标IP源服务器故障或爬虫认证过期,请稍后重试."}
        data[str(s)] = article2
        return data

    data = data.content
    if len(data) <= 24 or data[:4] != b'CZIP':
        article2 = {'code': -1,
                    'details': "解码版本信息文件失败"}
        rst[str(s)] = article2
        return rst
    version, unknown1, size, unknown2, key = \
        struct.unpack_from('<IIIII', data, 4)
    if unknown1 != 1:
        article2 = {'code': -1,
                    'details': "解码版本信息文件失败"}
        rst[str(s)] = article2
        return rst
    GEsys.System_Status = "[#] 正在下载数据文件..."
    data = get_content(db_url).content
    GEsys.System_Status = "[#] 正在校验数据文件..."
    if not data:
        article2 = {'code': -1,
                    'details': "下载数据文件失败"}
        rst[str(s)] = article2
        return rst
    if size != len(data):
        article2 = {'code': -1,
                    'details': "文件校验失败，尺寸不匹配"}
        rst[str(s)] = article2
        return rst
    head = bytearray(0x200)
    for i in range(0x200):
        key = (key * 0x805 + 1) & 0xff
        head[i] = data[i] ^ key
    data = head + data[0x200:]
    GEsys.System_Status = "[#] 加压缩文件..."
    try:
        data = zlib.decompress(data)
    except:
        article2 = {'code': -1,
                    'details': "解压缩失败"}
        rst[str(s)] = article2
        return rst
    if filename == None:
        return data
    elif type(filename) == str:
        GEsys.System_Status = "[#] 正在保存文件..."
        try:
            with open(filename, 'wb') as f:
                f.write(data)
        except:
            article2 = {'code': -1,
                        'details': "保存文件出错"}
            rst[str(s)] = article2
            return rst
    else:
        article2 = {'code': -1,
                    'details': "保存文件出错"}
        rst[str(s)] = article2
        return rst
    q = wrydb()
    q.load_file(filename)
    if q.dump():
        GEsys.setConfigItem(last, "ipTable", "currentVersion")

        q.clear()
        article2 = {'code': 0,
                    'details': "更新成功"}
        rst[str(s)] = article2
        return rst


def updateIPDBVersion():
    return get_lasetst_db('lastest.dat')
