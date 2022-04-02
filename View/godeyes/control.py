import json
import threading

from django.http import HttpResponse
from django.shortcuts import render

import modules.GSystem as GEsys
import modules.mysqlOper as GEdb
import modules.ipOper as GEip


def checkAccount(usr, pwd):
    return GEsys.login(usr, pwd)


def checkSession(request):
    try:
        if request.session['LoginStatues'] == '1':
            return True
        elif request.session is None:
            return False
        return False
    except Exception as e:
        return False


def modifyAccount(account, oldpassword, newpassword, repassword, request):
    c = {"title": "null", "info": "null"}
    if not checkAccount(account, oldpassword):
        c["title"] = "认证失败"
        c["info"] = "原账号的用户名和密码不匹配"
        return c
    elif newpassword != repassword:
        c["title"] = "新密码非法"
        c["info"] = "新密码不一致"
        return c
    if GEsys.modifyUserInfo(account, oldpassword, newpassword):
        c["title"] = "修改成功"
        c["info"] = "修改成功"
        return c
    else:
        c["title"] = "系统错误"
        c["info"] = "详情请查看log信息"
        return c


def get_data(request):
    arg3 = request.GET["arg3"]
    arg2 = request.GET["arg2"]
    arg1 = request.GET["arg1"]
    code = request.GET["code"]
    req = request.GET["req"]
    if req == "install":
        if code == 'checkDBLink':
            return GEdb.checkDBLink(arg1, arg2, arg3)

    GEsys.addLog("获取参数", req + "->" + code + "->" + arg1 + "->" + arg2 + "->" + arg3, request.session["username"],
                 request.META.get("REMOTE_ADDR"))
    if req == "db_http_total":
        return GEdb.getTotal('http')
    elif req == "db_ssh_total":
        return GEdb.getTotal('ssh')
    elif req == "db_mysql_total":
        return GEdb.getTotal('mysql')
    elif req == "get_record":
        return GEdb.getRecord(code, arg1, arg2)
    elif req == "get_thread_info":
        return GEsys.getThreadInfo()
    elif req == "getLogSWE":
        return GEdb.getLogSWE()
    elif req == "ipScannerInputBox":
        return GEip.checkIpInvalid(code)
    elif req == "getScannerPorts":
        return GEsys.getScannerPorts(code, arg1)
    ###################################################
    elif req == "getConfig" and code == 'req_constructor':
        return GEsys.Req_constructor_method(None, 'r')
    elif req == "getFile" and code == 'requestConstruct':
        return GEsys.Req_constructor_operation('r', None)
    elif req == "getConfig" and code == 'crackFile':
        return GEsys.Crack_File_Config('r', arg2, arg1)
    elif req == "getFile" and code == 'crackFile':
        return GEsys.Crack_File_Oper('r', arg1, arg2)
    ####################################################
    elif req == "getDBRecord":
        return GEsys.DBRecord_Oper(req, code, arg1, arg2, arg3)
    ####################################################
    elif req == "getIPDBRecord":
        return GEip.IPDRecord_Oper(req, code, arg1, arg2)
    elif req == 'getIPDBdashboard':
        return GEsys.getIPDBdashboard()
    elif req == 'checkIPDBVersion':
        return GEip.checkIPDBVersion()
    elif req == 'updateIPDBVersion':
        return GEip.updateIPDBVersion()
    elif req == 'getSystemStatus':
        return GEsys.System_Status
    elif req == 'getFingerPrint':
        return GEdb.getAllFingerPrint(code, request)
    elif req == 'getFingerprintBlackList':
        return GEsys.getFingerPrintBlacklist()
    elif req == 'getUserList':
        try:
            if request.session.get("power") == "SuperAdmin":
                return GEdb.getUserList()
            else:
                return json.dumps({"ojbk": {"code": -1, "detail": "此用户没有权限访问"}})
        except:
            return json.dumps({"ojbk": {"code": -1, "detail": "此用户没有权限访问"}})
    elif req == 'getScannerLog':
        try:
            if request.session.get("power") == "SuperAdmin":
                return GEdb.getScannerLog()
            else:
                return json.dumps({"ojbk": {"code": -1, "detail": "此用户没有权限访问"}})
        except:
            return json.dumps({"ojbk": {"code": -1, "detail": "此用户没有权限访问"}})

    elif req == 'getSystemLog':
        try:
            if request.session.get("power") == "SuperAdmin":
                return GEdb.getSystemLog()
            else:
                return json.dumps({"ojbk": {"code": -1, "detail": "此用户没有权限访问"}})
        except:
            return json.dumps({"ojbk": {"code": -1, "detail": "此用户没有权限访问"}})

    elif req == "getFile" and code == 'systemConfigure':
        try:
            if request.session.get("power") == "SuperAdmin":
                return GEsys.getSystemConfig()
            else:
                return json.dumps({"ojbk": {"code": -1, "detail": "此用户没有权限访问"}})
        except:
            return json.dumps({"ojbk": {"code": -1, "detail": "此用户没有权限访问"}})

    elif req == "getThreadDelay":
        return GEsys.getThreadDelay()


def managerPageInit(request, c):
    c["username"] = request.session.get("username")
    c["power"] = request.session.get("power")
    return request, c


def get_user_power(username):
    return GEdb.getUserPower(username)


def set_data(request):
    arg3 = request.POST.get("arg3")
    arg2 = request.POST.get("arg2")
    arg1 = request.POST.get("arg1")
    code = request.POST.get("code")
    req = request.POST.get("req")
    if req == 'install':
        if request.session["install"] == 'firstRun':
            return GEdb.install(code)
    GEsys.addLog("设置参数", req + "->" + code + "->" + arg1 + "->" + arg2 + "->" + arg3, request.session["username"],
                 request.META.get("REMOTE_ADDR"))
    try:
        if request.session.get("power") != "SuperAdmin":
            return json.dumps({"ojbk": {"code": -1, "detail": "此用户没有权限访问"}})
    except:
        return json.dumps({"ojbk": {"code": -1, "detail": "此用户没有权限访问"}})

    if req == 'save_portList':
        return GEsys.setScannerPorts(code, arg1)
    elif req == 'changeConfig' and code == 'req_constructor':
        return GEsys.Req_constructor_method(arg1, 'w')
    elif req == 'setFile' and code == 'requestConstruct':
        return GEsys.Req_constructor_operation('w', arg1)
    elif req == 'changeConfig' and code == 'crackRules':
        return GEsys.Crack_File_Config('w', code, arg1, arg2)
    elif req == 'changeConfig' and code == 'newCrackRules':
        return GEsys.Crack_File_Config('n', arg1, arg2, arg3)
    elif req == 'setFile' and code == 'saveCrackFile':
        return GEsys.Crack_File_Oper('w', arg2, arg1, arg3)
    elif req == 'setFile' and code == 'delCrackFile':
        return GEsys.Crack_File_Oper('d', arg2, arg1, arg3)
    elif req == 'changeConfig' and code == 'saveCrackFilePath':
        return GEsys.Crack_File_Config('w', arg1, code, arg2, arg3)
    elif req == 'setDBItem':
        return GEdb.SRecordOper(code, arg1, arg2, arg3)
    elif req == 'addLog':
        return GEsys.addLog(code, arg1, request.session['username'], request.META.get("REMOTE_ADDR"))
    elif req == 'setFingerprintBlackList':
        return GEsys.setFingerprintBlackList(code)
    elif req == 'setUserInfo':
        return GEdb.setUserInfo(code, arg1, arg2)
    elif req == 'addUserInfo':
        return GEdb.addUserInfo(code, arg1, arg2)
    elif req == 'deleteUser':
        return GEdb.deleteUser(code, arg1, arg2)
    elif req == 'rebuildFingerPrint':
        threading.Thread(target=GEdb.getAllFingerPrint, args=("rebuild", request,)).start()
        article_info = {"ojbk": {"code": 0, "detail": "线程已启动,此过程时间与数据量成正比."}}
        data = json.loads(json.dumps(article_info))
        return data
    elif req == 'setFile' and code == 'systemConfigure':
        return GEsys.setSystemConfig(arg1)
    elif req == 'clearDataTable':
        return GEdb.clearDataTable(code)
    elif req == 'stopAllThreads':
        return GEsys.stopAllThreads()
    elif req == 'startScanner':
        threading.Thread(target=GEsys.startScanner, args=(code, arg1, arg2)).start()
        article_info = {"ojbk": {"code": 0, "detail": "后台接收到扫描指令, 扫描器线程已启动."}}
        data = json.loads(json.dumps(article_info))
        return data


def checkInstall():
    if GEsys.getConfigItem("firstRun"):
        return False
    else:
        return True
