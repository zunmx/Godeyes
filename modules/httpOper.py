import random
import sys
import threading
import time
import traceback
from datetime import datetime
import socket

import netaddr
import urllib3
import modules.mysqlOper as dbOper
import requests
import re
import json
import modules.GSystem as GEsys

urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 10
requests.DEFAULT_RETRIES = 5
s = requests.session()
s.keep_alive = False


class DateEnconding(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.date):
            return o.strftime('%Y/%m/%d')
        if isinstance(o, bytes):
            return str(o, encoding='utf-8')


class HttpConnector(object):
    def geturl(self):
        if self.agreement.find("https") != -1:
            self.url = "https://"
        elif self.agreement.find("http") - 1:
            self.url = "http://"
        else:
            raise HttpConnector("URL地址不合法")
        if len(self.host) > 3:
            self.url += self.host
        else:
            raise HttpConnector("URL地址不合法")
        if self.port != "80":
            self.url += ":" + self.port
        return self.url

    def SetHeaders(self):
        if self.headers is None:
            return
        if self.headers_mix == True:
            original = dict(requests.get(self.url).headers)
            provider = dict(self.headers)
            new_headers = dict()
            for item in original.items():
                new_headers[item[0]] = item[1]
            for item in provider.items():
                new_headers[item[0]] = item[1]
            self.headers = new_headers

    def getTitle(self):
        try:
            title = re.findall(r"(?<=title>).+?(?=</title)", self.text)
            if len(title) != 0:
                title = title[0]
            else:
                try:
                    tmp = self.text.split('<title>')
                    tmp2 = tmp[1].split("</title>")
                    tmp3 = tmp2[0].replace(' ', '')
                    title = tmp3
                except:
                    # traceback.print_exc()
                    title = "[ # ][Not Found Title]"
                finally:
                    if title == '':
                        title = "[ # ][Not Found Title]"

            if title == "[ # ][Not Found Title]":
                try:
                    tmp = self.text.split('<TITLE>')
                    tmp2 = tmp[1].split("</TITLE>")
                    tmp3 = tmp2[0].replace(' ', '')
                    title = tmp3
                except Exception as e:
                    self.addDatabaseLog("标题获取失败" + self.host + ":" + str(self.port) + str(e))
                    title = "[ # ][Not Found Title]"
                finally:
                    if title == '':
                        title = "[ # ][Not Found Title]"
        except:
            title = "[ # ][Not Found Title]"
        return title

    def addDatabase(self):
        if self.ip != self.host:
            self.text = "Domain:" + self.host + "\n" + self.text
        dbOper.record_http(self.ip, self.port, self.getTitle(), str(self.RPheaders), self.text)

    def addDatabaseLog(self, e):
        dbOper.record_log('http', '[W]', self.ip, self.port, e)

    def __init__(self, agreement="http", host="127.0.0.1", port=80, proxy=None, requestHeaders=None, headers_mix=False,
                 timeout=5):

        self.agreement = agreement
        self.host = host
        self.port = str(port)
        self.proxy = proxy
        self.RQheaders = requestHeaders
        self.RPheaders = None
        self.url = self.geturl()
        self.ip = socket.gethostbyname(self.host)
        self.content = None
        self.headers_mix = headers_mix

        if self.proxy is not None:
            self.proxy = {
                "http": "http://{}".format(proxy.strip()), "https": "https://{}".format(proxy.strip())
            }
        # print(host, proxy)

        try:
            GEsys.System_Status = "尝试链接HTTP(S):" + self.ip + "-" + str(self.port)
            self.request = requests.get(url=self.url, headers=self.RQheaders, verify=False, proxies=self.proxy,
                                        timeout=timeout)

            self.RPheaders = self.request.headers
            self.text = str(self.request.text)
            self.addDatabase()

        except (urllib3.exceptions.MaxRetryError, requests.exceptions.ConnectTimeout, socket.timeout) as e:
            pass  # 连接超时
        except requests.exceptions.ConnectionError as e:
            pass  # 端口可能不存在
        except Exception as e:
            traceback.print_exc()
            self.addDatabaseLog("连接异常:" + str(e))


def startThread(method, url):
    enable = GEsys.getConfigItem("httpScanners", "enable")
    proxies = GEsys.getConfigItem("proxies")
    proxiesList = None
    proxiesSize = 0
    if proxies == "Enable":
        proxiesList = GEsys.GOSScannerPort("proxies", "r")
        proxiesSize = len(proxiesList)

    timeout = GEsys.getConfigItem("httpScanners", "timeout")
    threadCount = int(GEsys.getConfigItem("httpScanners", "threadCount"))
    delay = GEsys.getConfigItem("httpScanners", "delay")
    portList = GEsys.GOSScannerPort("http", "r")
    RequestHeaderMode = GEsys.getConfigItem("httpScanners", "RequestHeaderMode")
    RequestHeader = None
    if RequestHeaderMode == "custom":
        RequestHeaderMode = True
        RequestHeader = (json.loads(GEsys.Req_constructor_operation("r")))
    else:
        RequestHeaderMode = False
    if enable != 'True':
        return
    if type(url) == netaddr.ip.IPNetwork:
        pass
    elif str(url) == 'random':
        url = GEsys.getRandomIp()

    if method == "quicklyScan" or method == "fullScan" or method == "extendScan":
        for u in url:
            for port in portList:
                if proxies == "Enable":
                    proxy = proxiesList[random.randint(0, proxiesSize - 1)]
                else:
                    proxy = None
                u = str(u)
                threading.Thread(target=innerHThread,
                                 args=(
                                     "http", u, port, proxy, RequestHeader, RequestHeaderMode,
                                     timeout,)).start()

                threading.Thread(target=innerHThread,
                                 args=(
                                     "https", u, port, proxy, RequestHeader, RequestHeaderMode,
                                     timeout,)).start()

                if GEsys.STOP:
                    return
                while GEsys.threadInfo["httpThreadNum"] > threadCount:
                    time.sleep(delay)


def innerHThread(agreement, host, port, proxy, requestHeaders, headers_mix, timeout):
    GEsys.threadInfo["httpThreadNum"] = GEsys.threadInfo["httpThreadNum"] + 1
    try:
        r = HttpConnector(agreement, host, port, proxy, requestHeaders, headers_mix, timeout)
    except Exception as e:
        traceback.print_exc()

    GEsys.threadInfo["httpThreadNum"] = GEsys.threadInfo["httpThreadNum"] - 1


if __name__ == '__main__':
    url = list()

    startThread("quicklyScan", netaddr.IPNetwork("123.56.0.0/24"))
    # req = HttpConnector(agreement="http", host="91.243.12.248", port=80, headers_mix=False)
    # # print(req.url, req.port, req.text, req.ip)
    # req.addDatabase()
