import datetime
import json

import socket
import sys
import telnetlib
import threading
import time
import traceback

import netaddr

import modules.mysqlOper as dbOper
import modules.GSystem as GEsys

global threadInfo


class DateEnconding(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.date):
            return o.strftime('%Y/%m/%d')
        if isinstance(o, bytes):
            return str(o, encoding='utf-8')


class telnetConnector(object):

    def addDatabase(self, e=None, result=""):
        text = str(result)
        if e is not None:
            text = e
        elif self.ip != self.host:
            self.text = "Domain:" + self.host + "\n" + text
        dbOper.record_item('telnet', self.ip, self.port, text)

    def addDatabaseLog(self, e):
        dbOper.record_log('telnet', '[W]', self.ip, self.port, e)

    def __init__(self, host="127.0.0.1", port=23, username="_root_", password="_root_", timeout=30, crack=False,
                 final=False,
                 count=-1
                 ):
        self.host = host
        self.ip = socket.gethostbyname(self.host)
        self.port = int(port)
        self.username = username
        self.password = password
        self.crack = crack
        self.final = final
        self.timeout = timeout
        self.command_result = "Null"
        try:
            GEsys.System_Status = "尝试链接Telnet:" + self.ip + "-" + str(self.port)
            threadResult[self.ip + "-" + str(self.port)][2] = self.final
            if threadResult[self.ip + "-" + str(self.port)][3] > 5:
                self.addDatabaseLog("TELNET服务连接多次，但目标服务没有正确响应，跳过此端口" + self.ip + "-" + str(self.port))
                return
            self.tn = telnetlib.Telnet()
            self.tn.set_debuglevel(0)
            self.tn.open(self.ip, int(self.port), timeout=self.timeout)
            time.sleep(self.timeout)
            self.tn.write(self.username.encode('ascii') + "\r\n".encode('ascii'))
            time.sleep(self.timeout)
            self.tn.write(self.password.encode('ascii') + "\r\n".encode('ascii'))
            time.sleep(self.timeout)
            self.command_result = self.tn.read_very_eager().decode('ascii')
            threadResult[self.ip + "-" + str(self.port)][0] = True
            if not (str(self.command_result).find("Error") > 0 or str(self.command_result).find("incorrect") > 0):
                self.addDatabase(result=self.command_result)
                threadResult[self.ip + "-" + str(self.port)][0] = True
            else:
                if not threadResult[self.ip + "-" + str(self.port)][0] or threadResult[self.ip + "-" + str(self.port)][
                    1] > count:
                    self.addDatabase(self.command_result)
                elif not crack:
                    self.addDatabase(self.command_result)
            self.tn.close()
        except OSError as e:
            threadResult[self.ip + "-" + str(self.port)][3] += 1
            # traceback.print_exc()
        except Exception as e:
            self.addDatabase(self.command_result)
        finally:
            threadResult[self.ip + "-" + str(self.port)][1] = threadResult[self.ip + "-" + str(self.port)][1] + 1
            # if threadResult[self.ip + "-" + str(self.port)][1] >= count:
            #     threadResult.pop(self.ip + "-" + str(self.port))


def startThread(method, url):
    global threadResult, dbMutex
    dbMutex = threading.Lock()
    threadResult = {}

    enable = GEsys.getConfigItem("telnetScanners", "enable")
    threadCount = int(GEsys.getConfigItem("telnetScanners", "threadCount"))
    delay = GEsys.getConfigItem("telnetScanners", "delay")
    crash = GEsys.getConfigItem("telnetScanners", "crash")
    timeout = GEsys.getConfigItem("telnetScanners", "timeout")
    if crash == "True":
        userlist = GEsys.Crack_File_Oper("ir", "getCrackUserFile", "telnet")
        pwdlist = GEsys.Crack_File_Oper("ir", "getCrackPasswordFile", "telnet")
        combinCount = len(userlist) + len(pwdlist)
    portList = GEsys.GOSScannerPort("telnet", "r")

    if enable != 'True':
        return
    if type(url) == netaddr.ip.IPNetwork:
        pass
    elif str(url) == 'random':
        url = GEsys.getRandomIp()

    if method == "extendScan":
        for port in portList:
            if type(url) == str:
                t = url
                url = list()
                url.append(t)
            for u in url:
                u = str(u)
                try:
                    try:
                        if threadResult[u + "-" + str(port)][0]:
                            continue
                    except:
                        threadResult[u + "-" + str(port)] = [False, 0, False, 0]
                except Exception as e:
                    traceback.print_exc()
                    et, ev, tb = sys.exc_info()
                    msg = traceback.format_exception(et, ev, tb)
                    rst = ""
                    for m in msg:
                        rst += str(m).strip() + "\n"
                    dbOper.record_log('telnet', "[E]", u, port, str(e) + ":" + rst)
                threading.Thread(target=innerThread,
                                 args=(u, port, "root", "root", timeout, False, True, -1)).start()
                # print(GEsys.threadInfo, u, port, GEsys.threadInfo["telnetThreadNum"], threadCount)
                if GEsys.STOP:
                    return
                while GEsys.threadInfo["telnetThreadNum"] > threadCount:
                    time.sleep(delay)

    if method == "fullScan":
        for port in portList:
            if type(url) == str:
                t = url
                url = list()
                url.append(t)
            for u in url:
                u = str(u)
                try:
                    try:
                        if threadResult[u + "-" + str(port)][0]:
                            continue
                    except:
                        threadResult[u + "-" + str(port)] = [False, 0, False, 0]
                except Exception as e:
                    traceback.print_exc()

                if crash == "True":
                    for usr in userlist:
                        for pwd in pwdlist:
                            combinCount *= len(portList)
                            try:
                                if threadResult[u + "-" + str(port)][0]:
                                    continue
                            except:
                                threadResult[u + "-" + str(port)] = [False, 0, False, 0]
                            if usr == userlist[len(userlist) - 1] and pwd == pwdlist[len(pwdlist) - 1]:
                                threading.Thread(target=innerThread,
                                                 args=(u, port, usr, pwd, timeout, crash, True, combinCount,)).start()
                            else:
                                threading.Thread(target=innerThread,
                                                 args=(u, port, usr, pwd, timeout, crash, False, combinCount,)).start()
                            # print(GEsys.threadInfo, u, port, GEsys.threadInfo["telnetThreadNum"], threadCount)
                            if GEsys.STOP:
                                return
                            while GEsys.threadInfo["telnetThreadNum"] > threadCount:
                                time.sleep(delay)

                else:
                    threading.Thread(target=innerThread,
                                     args=(u, port, "root", "root", timeout, crash, True, -1,)).start()
                    # print(GEsys.threadInfo, u, port, GEsys.threadInfo["telnetThreadNum"], threadCount)
                    if GEsys.STOP:
                        return
                    while GEsys.threadInfo["telnetThreadNum"] > threadCount:
                        time.sleep(delay)


def innerThread(host, port, username, password, timeout, crack, final, Count=-1, ):
    GEsys.threadInfo["telnetThreadNum"] = GEsys.threadInfo["telnetThreadNum"] + 1

    try:
        telnetConnector(host, port, username, password, timeout, crack, final, Count)
    except Exception as e:

        et, ev, tb = sys.exc_info()
        msg = traceback.format_exception(et, ev, tb)
        rst = ""
        for m in msg:
            rst += str(m).strip() + "\n"
        dbOper.record_log('telnet', "[E]", host, port, str(e) + ":" + rst)

    GEsys.threadInfo["telnetThreadNum"] = GEsys.threadInfo["telnetThreadNum"] - 1


if __name__ == '__main__':
    # ip = list()
    # ip.append("183.224.48.37")
    # # startThread("fullScan", ip)
    startThread("fullScan", "116.39.161.78")
    # startThread("fullScan", "random")
