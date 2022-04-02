import random
import threading
from time import time
import time
import pymysql
import json
import os
from multiprocessing import Process, Manager
import socket

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def net_is_used(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False


class HttpRequestError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SystemError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class DatabaseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class scannerConstructor:
    def __init__(self):
        self.threadPool = None

    def test(self):
        print("test")


threadInfo = {"httpThreadNum": 0,
              "mysqlThreadNum": 0,
              "sshThreadNum": 0,
              "telnetThreadNum": 0
              }
coprocessorList = []
System_Status = "free"
global STOP
STOP = False


def getConfigData():
    if not os.path.exists(BASE_DIR + "/modules/sys.json"):
        raise SystemError("系统配置文件丢失")

    with open(BASE_DIR + "/modules/sys.json") as f:
        data = json.load(f)
        return data


def setConfigData(content):
    if not os.path.exists(BASE_DIR + "/modules/sys.json"):
        raise SystemError("系统配置文件丢失")
    with open(BASE_DIR + "/modules/sys.json", 'w') as fp:
        json.dump(content, fp)


def getDBInfo():
    data = getConfigData()
    database_info = data["database"]
    return database_info


def login(usr, pwd):
    import modules.mysqlOper as dbOper
    if dbOper.checkAccount(usr, pwd) == 1:
        return True
    else:
        return False


def modifyUserInfo(usr, opwd, npwd):
    import modules.mysqlOper as dbOper
    if login(usr, opwd):
        return dbOper.modAccountPwd(usr, opwd, npwd)


def checkSelf():
    if not os.path.exists(BASE_DIR + "/modules/sys.json"):
        raise SystemError("系统配置文件丢失")

    try:
        with open(BASE_DIR + "/modules/sys.json") as f:
            json.load(f)
    except json.decoder.JSONDecodeError:
        raise SystemError("系统配置文件解析失败")

    with open(BASE_DIR + "/modules/sys.json") as f:
        data = json.load(f)
        database_info = data["database"]
        try:
            db = pymysql.connect(database_info['url'], database_info['user'], database_info['passwd'],
                                 database_info['db'],
                                 charset=database_info['charset'])
            db.close()
        except pymysql.InternalError as e:
            raise DatabaseError("数据库不存在")
        except pymysql.err.OperationalError as e:
            raise DatabaseError("数据库连接失败")


def getThreadInfo():
    article_info = {}
    data = json.loads(json.dumps(article_info))
    s = "ojbk"
    article2 = {'httpThreadNum': threadInfo['httpThreadNum'],
                'mysqlThreadNum': threadInfo['mysqlThreadNum'],
                "sshThreadNum": threadInfo["sshThreadNum"],
                'telnetThreadNum': threadInfo['telnetThreadNum'],
                'totalThreadNum': int(threadInfo['httpThreadNum']) + int(threadInfo['mysqlThreadNum']) + int(
                    threadInfo['sshThreadNum']) + int(threadInfo['telnetThreadNum'])}
    data[str(s)] = article2
    return data


def GOSScannerPort(method, func, args=None):
    path = ""
    lists = []
    if method == 'http':
        path = BASE_DIR + "/FingerPrint/HttpPortList.txt"
    if method == 'ssh':
        path = BASE_DIR + "/FingerPrint/SshPortList.txt"
    if method == 'telnet':
        path = BASE_DIR + "/FingerPrint/TelnetPortList.txt"
    if method == 'mysql':
        path = BASE_DIR + "/FingerPrint/MysqlPortList.txt"
    if method == 'proxies':
        path = BASE_DIR + "/FingerPrint/proxies.txt"
    if not os.path.exists(path):
        raise SystemError("端口文件[" + method + "] 不存在")
    if func == 'r':
        with open(path, 'r') as f:
            for i in f:
                lists.append(i.strip())
        return lists
    if func == 'w':
        if not os.path.exists(path):
            raise SystemError("端口文件[http] 不存在")
        try:
            with open(path, 'w') as f:
                f.write(args)
        except Exception as e:
            return False
        return True


def getScannerPorts(code, arg):
    # code in [http/mysql/ssh/telnet]
    # arg  in [json/dict]
    s = "ojbk"
    if code not in ["http", "mysql", "ssh", "telnet", "all"] or arg not in ["json", "dict"]:
        article_info = {}
        data = json.loads(json.dumps(article_info))
        s = "Error"
        article2 = {'code': -1, 'details': "invalid request!"}
        data[str(s)] = article2
        return data
    if code == 'all':
        http = GOSScannerPort("http", 'r')
        telnet = GOSScannerPort("telnet", 'r')
        ssh = GOSScannerPort("ssh", 'r')
        mysql = GOSScannerPort("mysql", 'r')
        if arg == 'dict':
            return http, telnet, ssh, mysql
        elif arg == 'json':
            article_info = {}
            data = json.loads(json.dumps(article_info))
            article2 = {'http': http,
                        'mysql': mysql,
                        'ssh': ssh,
                        'telnet': telnet}
            data["ojbk"] = article2
            return data
    if code == 'http':
        http = GOSScannerPort("http", 'r')
        if arg == 'dict':
            return http
        elif arg == 'json':
            article_info = {}
            data = json.loads(json.dumps(article_info))
            article2 = {'http': http}
            data["ojbk"] = article2
            return data
    if code == 'mysql':
        mysql = GOSScannerPort("mysql", 'r')
        if arg == 'dict':
            return mysql
        elif arg == 'json':
            article_info = {}
            data = json.loads(json.dumps(article_info))
            article2 = {'mysql': mysql}
            data["ojbk"] = article2
            return data
    if code == 'telnet':
        telnet = GOSScannerPort("telnet", 'r')
        if arg == 'dict':
            return telnet
        elif arg == 'json':
            article_info = {}
            data = json.loads(json.dumps(article_info))
            article2 = {'telnet': telnet}
            data["ojbk"] = article2
            return data
    if code == 'ssh':
        ssh = GOSScannerPort("ssh", 'r')
        if arg == 'dict':
            return ssh
        elif arg == 'json':
            article_info = {}
            data = json.loads(json.dumps(article_info))
            article2 = {'ssh': ssh}
            data["ojbk"] = article2
            return data


def checkPortInvalid(portlist):
    rst = ""
    lst = portlist.split("\n")
    for i in lst:
        if str(i).strip() == "":
            continue
        if i is "":
            continue
        if not str.isdigit(i):
            return False
        else:
            rst += i + "\n"
    return rst


def setScannerPorts(code, arg):
    # code in [http/mysql/ssh/telnet]
    # arg  in [port]
    arg = arg.strip()
    rst = checkPortInvalid(arg)
    if rst == 'False':
        article_info = {}
        data = json.loads(json.dumps(article_info))
        s = "Error"
        article2 = {'code': -1, 'details': "invalid data"}
        data[str(s)] = article2
        return data

    if code not in ["http", "mysql", "ssh", "telnet", ]:
        article_info = {}
        data = json.loads(json.dumps(article_info))
        s = "Error"
        article2 = {'code': -1, 'details': "invalid request!"}
        data[str(s)] = article2
        return data

    if code == 'http':
        http = GOSScannerPort("http", 'w', rst)
        if http:
            article_info = {}
            data = json.loads(json.dumps(article_info))
            s = "ojbk"
            article2 = {'code': 0, 'details': "http Port list write success"}
            data[str(s)] = article2
            return data
        else:
            article_info = {}
            data = json.loads(json.dumps(article_info))
            s = "Error"
            article2 = {'code': -1, 'details': "File save failed"}
            data[str(s)] = article2
            return data
    if code == 'mysql':
        mysql = GOSScannerPort("mysql", 'w', rst)
        if mysql:
            article_info = {}
            data = json.loads(json.dumps(article_info))
            s = "ojbk"
            article2 = {'code': 0, 'details': "mysql Port list write success"}
            data[str(s)] = article2
            return data
        else:
            article_info = {}
            data = json.loads(json.dumps(article_info))
            s = "Error"
            article2 = {'code': -1, 'details': "File save failed"}
            data[str(s)] = article2
            return data
    if code == 'telnet':
        telnet = GOSScannerPort("telnet", 'w', rst)
        if telnet:
            article_info = {}
            data = json.loads(json.dumps(article_info))
            s = "ojbk"
            article2 = {'code': 0, 'details': "telnet Port list write success"}
            data[str(s)] = article2
            return data
        else:
            article_info = {}
            data = json.loads(json.dumps(article_info))
            s = "Error"
            article2 = {'code': -1, 'details': "File save failed"}
            data[str(s)] = article2
            return data
    if code == 'ssh':
        ssh = GOSScannerPort("ssh", 'w', rst)
        if ssh:
            article_info = {}
            data = json.loads(json.dumps(article_info))
            s = "ojbk"
            article2 = {'code': 0, 'details': "ssh Port list write success"}
            data[str(s)] = article2
            return data
        else:
            article_info = {}
            data = json.loads(json.dumps(article_info))
            s = "Error"
            article2 = {'code': -1, 'details': "File save failed"}
            data[str(s)] = article2
            return data


def getConfigItem(*section):
    try:
        num = len(section)
        conf = getConfigData()
        value = ''
        if num == 1:
            value = conf.get(section[0])
        if num == 2:
            value = conf.get(section[0]).get(section[1])
        return value
    except Exception as e:
        raise SystemError("系统配置文件丢失")


def setConfigItem(kwarg, *section):
    num = len(section)
    conf = getConfigData()
    if num == 1:
        conf[section[0]] = kwarg
    if num == 2:
        conf[section[0]][section[1]] = kwarg

    setConfigData(conf)


def Req_constructor_method(arg1, method):
    article_info = {}
    data = json.loads(json.dumps(article_info))
    s = "ojbk"
    if method == 'r':
        article2 = {'HttpRequestHeaderMethod': getConfigItem("httpScanners", "RequestHeaderMode")}
        data[str(s)] = article2
    if method == 'w':
        setConfigItem(arg1, "httpScanners", "RequestHeaderMode")
        article2 = {'setHttpRequestHeader': True}
        data[str(s)] = article2
    return data


def Req_constructor_operation(method, arg=None):
    article_info = {}
    data = json.loads(json.dumps(article_info))
    s = "ojbk"
    path = getConfigItem("httpScanners", "header")
    if not os.path.exists(BASE_DIR + "/" + path):
        raise SystemError("系统配置文件丢失")
    if method == 'r':  # read file
        with open(BASE_DIR + "/" + path, 'r') as f:
            data = json.load(f)
            data = str(data).replace("'", '"')
            return data
    elif method == 'w':
        tmp = json.loads(json.dumps(arg))
        try:
            with open(BASE_DIR + "/" + path, 'w') as fp:
                json.dump(tmp, fp)
            rst = True
        except Exception as e:
            rst = False

        article2 = {'success': rst}
        data[str(s)] = article2
        return data


def Crack_File_Config(method, file, arg1=None, arg2=None, arg3=None):
    article_info = {}
    data = json.loads(json.dumps(article_info))

    s = "ojbk"
    aim = ""
    if file == 'mysql':
        aim = 'mysqlScanners'
    elif file == 'ssh':
        aim = "sshScanners"
    elif file == 'telnet':
        aim = "telnetScanners"
    else:
        aim = file
    if method == 'r':
        if arg1 == 'getCrackFilePath':
            article2 = {'Ufile_name': getConfigItem(aim, "dictionary_user"),
                        'Pfile_name': getConfigItem(aim, "dictionary_pwd")}
            data[str(s)] = article2
            return data
        if arg1 == 'getCrackFileList':
            ls = os.listdir(BASE_DIR + "/FingerPrint/custom/dict/")
            sec = 1
            article2 = {}
            for i in ls:
                article2[str(sec)] = i
                sec += 1
            data[str(s)] = article2
            return data
    if method == 'w':
        if arg1 == 'saveCrackFilePath':
            if arg2 == 'CrackUserFile':
                setConfigItem(str(arg3), aim, "dictionary_user")
            if arg2 == 'CrackPasswordFile':
                setConfigItem(str(arg3), aim, "dictionary_pwd")
        article2 = {'status': "success"}
        data[str(s)] = article2
        return data
    if method == 'n':
        # print(method, file, arg1, arg2, arg3)
        tmp = str(arg2).split('.')
        if tmp[len(tmp) - 1] != 'txt':
            arg2 += '.txt'
        if os.path.exists(BASE_DIR + '/FingerPrint/custom/dict/' + arg2):
            article2 = {'status': "文件已存在"}
            data[str(s)] = article2
            return data
        else:
            try:
                with open(BASE_DIR + '/FingerPrint/custom/dict/' + arg2, 'w') as f:
                    f.write("")
                if arg1 == 'userFile':
                    Crack_File_Config('w', file, 'saveCrackFilePath', 'CrackUserFile', arg2)
                if arg1 == 'passwordFile':
                    Crack_File_Config('w', file, 'saveCrackFilePath', 'CrackPasswordFile', arg2)
            except Exception as e:
                article2 = {'status': "文件创建失败，请检查文件名规范。"}
                data[str(s)] = article2
            article2 = {'status': "success"}
            data[str(s)] = article2
            return data
    return None


def inside_Function_check_crack_file():
    count = 0
    for i in ['mysqlScanners', 'sshScanners', 'telnetScanners']:
        if not os.path.exists(BASE_DIR + "/FingerPrint/custom/dict/" + getConfigItem(i, "dictionary_user")):
            Crack_File_Config('w', i, "saveCrackFilePath", 'CrackUserFile', "default_user.txt")
            count += 1
        if not os.path.exists(BASE_DIR + "/FingerPrint/custom/dict/" + getConfigItem(i, "dictionary_pwd")):
            Crack_File_Config('w', i, "saveCrackFilePath", 'CrackPasswordFile', "default_pwd.txt")
            count += 1
    return count


def Crack_File_Oper(method, what, file, context=None):
    article_info = {}
    data = json.loads(json.dumps(article_info))
    if file == 'mysql':
        aim = 'mysqlScanners'
    elif file == 'ssh':
        aim = "sshScanners"
    elif file == 'telnet':
        aim = "telnetScanners"
    else:
        s = "Error"
        article2 = {'code': -1, 'details': "operation invalid"}
        data[str(s)] = article2
        return data
    # print("method: " + str(method) + "\nwhat: " + str(what) + "\nfile: " + str(file) + "\ncontext: " + str(
    #     context) + "\naim:" + aim)
    if method == 'r':
        try:
            if what == 'getCrackUserFile':
                with open(BASE_DIR + "/FingerPrint/custom/dict/" + getConfigItem(aim, "dictionary_user"), 'r',
                          encoding='utf8') as f:
                    return f.read()
            elif what == 'getCrackPasswordFile':
                with open(BASE_DIR + "/FingerPrint/custom/dict/" + getConfigItem(aim, "dictionary_pwd"), 'r',
                          encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            inside_Function_check_crack_file()
            return "文件不存在"
    if method == 'w':
        try:
            if what == 'userFile':
                with open(BASE_DIR + "/FingerPrint/custom/dict/" + getConfigItem(aim, "dictionary_user"), 'w',
                          encoding='utf8') as f:
                    f.write(context)
            elif what == 'passwordFile':
                with open(BASE_DIR + "/FingerPrint/custom/dict/" + getConfigItem(aim, "dictionary_pwd"), 'w',
                          encoding='utf-8') as f:
                    f.write(context)

            s = "ojbk"
            article2 = {'code': 0, 'details': "Successfully"}
            data[str(s)] = article2
            return data
        except Exception as e:
            s = "Error"
            article2 = {'code': -1, 'details': "unknown error"}
            data[str(s)] = article2
            return data
    if method == 'd':
        if what == "passwordFile":
            if getConfigItem(aim, "dictionary_pwd") == 'default_pwd.txt':
                s = "Error"
                article2 = {'code': -1, 'details': "默认字典不允许删除"}
                data[str(s)] = article2
                return data
        elif what == 'userFile':
            if getConfigItem(aim, "dictionary_user") == 'default_user.txt':
                s = "Error"
                article2 = {'code': -1, 'details': "默认字典不允许删除"}
                data[str(s)] = article2
                return data
        try:
            if what == 'userFile':
                os.remove(BASE_DIR + "/FingerPrint/custom/dict/" + getConfigItem(aim, "dictionary_user"))
            elif what == 'passwordFile':
                os.remove(BASE_DIR + "/FingerPrint/custom/dict/" + getConfigItem(aim, "dictionary_pwd"))
            ck = inside_Function_check_crack_file()

            s = "ojbk"
            if ck == 0:
                article2 = {'code': 0, 'details': "删除成功"}
            else:
                article2 = {'code': 0, 'details': "受影响的配置" + str(ck) + "条"}
            data[str(s)] = article2
            return data
        except Exception as e:
            print(e)
            s = "Error"
            article2 = {'code': -1, 'details': "不明确的错误:" + str(e)}
            data[str(s)] = article2
            return data
    if method == 'ir':  # 内部调用
        try:
            lists = []
            if what == 'getCrackUserFile':
                with open(BASE_DIR + "/FingerPrint/custom/dict/" + getConfigItem(aim, "dictionary_user"), 'r',
                          encoding='utf8') as f:
                    for i in f:
                        lists.append(i.strip())
            elif what == 'getCrackPasswordFile':
                with open(BASE_DIR + "/FingerPrint/custom/dict/" + getConfigItem(aim, "dictionary_pwd"), 'r',
                          encoding='utf-8') as f:
                    for i in f:
                        lists.append(i.strip())
            return lists
        except Exception as e:
            inside_Function_check_crack_file()
            return "文件不存在"


def DBRecord_Oper(req, code, arg1, arg2, arg3=None):
    if req == "getDBRecord":
        import modules.mysqlOper as dbOper
        return dbOper.getDBRecord(code, arg1, arg2, arg3)


def getIPDBdashboard():
    article_info = {}
    data = json.loads(json.dumps(article_info))
    s = "ojbk"
    source = getConfigItem("ipTable", "source")
    current = getConfigItem("ipTable", "currentVersion")

    article2 = {'source': source,
                'current': current}
    data[str(s)] = article2
    return data


def getSystemStatus():
    return System_Status


def addLog(code, arg1, arg2, arg3):
    import modules.mysqlOper as dbOper
    return dbOper.setLog(code, arg1, arg2, arg3)


def getFingerPrintBlacklist():
    result = ""
    with open(BASE_DIR + "\\FingerPrint\\custom\\webFingerPrint\\blackList.txt", mode='r') as foper:
        result = foper.read()
    return result


def setFingerprintBlackList(code):
    article_info = {}
    data = json.loads(json.dumps(article_info))
    try:
        with open(BASE_DIR + "\\FingerPrint\\custom\\webFingerPrint\\blackList.txt", mode='w') as foper:
            foper.write(code)
        s = "ojbk"
        article2 = {'code': 0}
    except:
        s = "err"
        article2 = {'code': -1}

    data[str(s)] = article2
    return data


def getSystemConfig():
    with open(BASE_DIR + "/modules/sys.json") as f:
        context = f.read()
        return context


def setSystemConfig(content):
    article_info = {}
    data = json.loads(json.dumps(article_info))
    try:
        with open(BASE_DIR + "/modules/sys.json", 'w') as fp:
            fp.write(content)
        s = "ojbk"
        article2 = {'code': 0, 'details': "保存成功"}
        data[str(s)] = article2
        return data
    except:
        s = "error"
        article2 = {'code': -1, 'details': "写入失败"}
        data[str(s)] = article2
        return data


def stopAllThreads():
    global STOP
    STOP = True
    keys = threadInfo.keys()
    sec = 0
    count = 0
    waitTime = getConfigItem("scannerStopWaitSecond")
    for i in coprocessorList:
        i.kill()
    while True:
        sec += 1
        count = 0
        for i in keys:
            count = count + threadInfo[i]
        if count <= 0 or sec == int(waitTime):
            break
        time.sleep(1)
        # print(sec, count, waitTime)
    if count != 0:
        return json.dumps(
            {"ojbk": {"code": 0, "detail": "线程关闭成功，由于启动中的线程没有结束，还剩下" + str(count) + "个线程，余下的线程执行完成后将会没有启动的线程"}})
    else:
        return json.dumps(
            {"ojbk": {"code": 0, "detail": "线程关闭成功。"}})


def startScanner(method, addr, coprocessor):
    global STOP
    STOP = False
    from modules import ipOper
    if addr != 'random':
        addr = ipOper.getIPList(addr)

    if coprocessor == 'true':
        if method == "quicklyScan":
            import modules.httpOper as httpOper
            p = Process(target=httpOper.startThread, args=("quicklyScan", addr,))
            coprocessorList.append(p)
            p.start()
        if method == "extendScan":
            import modules.httpOper as httpOper
            p = Process(target=httpOper.startThread, args=("quicklyScan", addr,))
            coprocessorList.append(p)
            p.start()
            import modules.mysqlOper as mysqlOper
            p = Process(target=mysqlOper.startThread, args=("quicklyScan", addr,))
            coprocessorList.append(p)
            p.start()
            import modules.sshOper as sshOper
            p = Process(target=sshOper.startThread, args=("quicklyScan", addr,))
            coprocessorList.append(p)
            p.start()
            import modules.telnetOper as telnetOper
            p = Process(target=telnetOper.startThread, args=("quicklyScan", addr,))
            coprocessorList.append(p)
            p.start()

        if method == "fullScan":
            import modules.httpOper as httpOper
            p = Process(target=httpOper.startThread, args=("fullScan", addr,))
            coprocessorList.append(p)
            p.start()
            import modules.mysqlOper as mysqlOper
            p = Process(target=mysqlOper.startThread, args=("fullScan", addr,))
            coprocessorList.append(p)
            p.start()
            import modules.sshOper as sshOper
            p = Process(target=sshOper.startThread, args=("fullScan", addr,))
            coprocessorList.append(p)
            p.start()
            import modules.telnetOper as telnetOper
            p = Process(target=telnetOper.startThread, args=("fullScan", addr,))
            coprocessorList.append(p)
            p.start()
    else:
        if method == "quicklyScan":
            import modules.httpOper as httpOper
            threading.Thread(target=httpOper.startThread, args=("quicklyScan", addr,)).start()

        if method == "extendScan":
            import modules.httpOper as httpOper
            threading.Thread(target=httpOper.startThread, args=("extendScan", addr,)).start()
            import modules.mysqlOper as mysqlOper
            threading.Thread(target=mysqlOper.startThread, args=("extendScan", addr,)).start()
            import modules.sshOper as sshOper
            threading.Thread(target=sshOper.startThread, args=("extendScan", addr,)).start()
            import modules.telnetOper as telnetOper
            threading.Thread(target=telnetOper.startThread, args=("extendScan", addr,)).start()

        if method == "fullScan":
            import modules.httpOper as httpOper
            threading.Thread(target=httpOper.startThread, args=("fullScan", addr,)).start()
            import modules.mysqlOper as mysqlOper
            threading.Thread(target=mysqlOper.startThread, args=("fullScan", addr,)).start()
            import modules.sshOper as sshOper
            threading.Thread(target=sshOper.startThread, args=("fullScan", addr,)).start()
            import modules.telnetOper as telnetOper
            threading.Thread(target=telnetOper.startThread, args=("fullScan", addr,)).start()


def getThreadDelay():
    return json.dumps(
        {"ojbk": {"code": 0, "detail": getConfigItem("scannerStopWaitSecond")}})


def getRandomIp():
    url = list()
    for i in range(0, 999999):
        t_ip = str(int(random.randint(0, 255))) + "." + str(int(random.randint(0, 255))) + "." + str(
            int(random.randint(0, 255))) + "." + str(int(random.randint(0, 255)))
        if t_ip.startswith("127."):
            t_ip = str(int(random.randint(0, 255))) + "." + str(int(random.randint(0, 255))) + "." + str(
                int(random.randint(0, 255))) + "." + str(int(random.randint(0, 255)))
        if t_ip.startswith("0."):
            t_ip = str(int(random.randint(0, 255))) + "." + str(int(random.randint(0, 255))) + "." + str(
                int(random.randint(0, 255))) + "." + str(int(random.randint(0, 255)))
        url.append(t_ip)
    return url


if __name__ == '__main__':
    startScanner("fullScan", 'random', 'true')
