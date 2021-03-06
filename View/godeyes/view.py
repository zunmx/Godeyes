import json
import os
import sys
import traceback

from django.http import HttpResponse, JsonResponse, HttpResponseServerError
from django.shortcuts import render
from django.template.context_processors import csrf
import View.godeyes.control as control
# import View.manage as mg
from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout
from django.views.decorators.gzip import gzip_page
import modules.GSystem as GEsys

@gzip_page
def index(request):
    if not control.checkInstall():
        response = redirect("/install/")
        return response

    if control.checkSession(request):
        request.session["LoginStatues"] = "1"
        response = redirect("/manager/")
        return response
    else:
        context = {"title": "GodEyes"}
        request.session.clear()
        request.session.flush()
        return render(request, "login.html", context)


def install(request):
    if not control.checkInstall():
        request.session["ip"] = request.META['REMOTE_ADDR']
        request.session["install"] = 'firstRun'
        context = {"title": "GodEyes"}
        return render(request, "install.html", context)
    else:
        c = {"title": "null", "info": "null"}
        c["title"] = "系统已经安装"
        c["info"] = "如需重新安装，请将sys.json中firstRun改为true"
        return render(request, "info.html", c)


@gzip_page
def login(request):
    c = {"title": "null", "info": "null"}
    c.update(csrf(request))
    if request.method == 'GET':
        c["title"] = "不允许的访问"
        c["info"] = "登陆页面不允许直接访问"
        return render(request, "info.html", c)
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            if not control.checkAccount(username, password):
                GEsys.addLog("登录", "登陆失败", username, request.META.get("REMOTE_ADDR"))
                c["title"] = "登陆失败"
                c["info"] = "用户名或密码错误"
                request.session["LoginStatues"] = "0"
                return render(request, "info.html", c)
            else:
                GEsys.addLog("登录", "登陆成功", username, request.META.get("REMOTE_ADDR"))
                request.session["username"] = username
                request.session["password"] = password
                request.session["LoginStatues"] = "1"
                request.session["power"] = control.get_user_power(username)
                request.session["ip"] = request.META['REMOTE_ADDR']
                response = redirect("/manager/")
                return response
    except Exception as e:
        c["title"] = "不允许的访问"
        c["info"] = "参数不合法"
        request.session["LoginStatues"] = "0"
        print(e)
        return render(request, "info.html", c)


@gzip_page
def logout(request):
    try:
        GEsys.addLog("登出", "登出成功", request.session["username"], request.META.get("REMOTE_ADDR"))
    except Exception as e:
        GEsys.addLog("系统异常", e, "None", request.META.get("REMOTE_ADDR"))
    response = redirect("/")
    request.session.clear()
    request.session.flush()
    auth_logout(request)
    return response


@gzip_page
def manager(request):
    c = {"title": "null", "info": "null", "power": "Vistor"}
    c.update(csrf(request))
    try:
        if request.session['LoginStatues'] is not None:
            if request.session['LoginStatues'] == '1':
                # 页面处理
                request, c = control.managerPageInit(request, c)
                return render(request, 'manager.html', c)
        GEsys.addLog("认证过期", "超时未操作", "None", request.META.get("REMOTE_ADDR"))
        c["title"] = "认证过期"
        c["info"] = "登录信息已经过期，请重新登录"
        return render(request, "info.html", c)
    except Exception as e:
        print(e)
        try:
            GEsys.addLog("系统异常", e, request.session["username"], request.META.get("REMOTE_ADDR"))
        except:
            GEsys.addLog("系统异常", e, "None", request.META.get("REMOTE_ADDR"))
        c["title"] = "认证过期"
        c["info"] = "登录信息已经过期，请重新登录"
        return render(request, "info.html", c)


@gzip_page
def modAccount(request):
    c = {"title": "null", "info": "null"}
    c.update(csrf(request))
    try:
        c['account'] = request.session['username']
        if request.session["ip"] == request.META['REMOTE_ADDR']:
            return render(request, "modifyAccount.html", c)
        else:
            c["title"] = "认证过期"
            c["info"] = "登录信息已经过期，请重新登录"
            return render(request, "info.html", c)
    except Exception as e:
        GEsys.addLog("错误", "不允许的请求方式[modAccount]", request.session["username"], request.META.get("REMOTE_ADDR"))
        c["title"] = "不允许的访问"
        c["info"] = "登陆页面不允许直接访问"
        return render(request, "info.html", c)


@gzip_page
def get_data(request):  # Ajax 异步获取请求
    c = {"title": "null", "info": "null"}
    c.update()
    c.update(csrf(request))
    try:
        if request.COOKIES['csrftoken'] is not "" and (request.session["ip"] is not None) and request.session["ip"] == \
                request.META['REMOTE_ADDR']:
            if request.GET.get("req") == "install":  # 安装
                if request.session["install"] == 'firstRun':
                    if request.GET.get("code") == 'checkDBLink':
                        return JsonResponse(control.get_data(request), safe=False)
                    if request.GET.get("code") == 'getStatus':
                        cc = {}
                        cc['result'] = GEsys.System_Status
                        return render(request, "empty.html", context=cc)

            if not request.session.get("username"):
                GEsys.addLog("错误", "不允许的请求方式[GET]", request.session["username"], request.META.get("REMOTE_ADDR"))
                c["title"] = "不允许的访问"
                c["info"] = "请求无法直接访问"
                return render(request, "info.html", c)

            rst = control.get_data(request)
            if request.GET.get("req") == "get_record":
                return JsonResponse(rst)
            elif request.GET.get("req") == "get_thread_info":
                return JsonResponse(rst)
            elif request.GET.get("req") == "getLogSWE":
                return JsonResponse(rst)
            elif request.GET.get("req") == "ipScannerInputBox":
                return JsonResponse(rst)
            elif request.GET.get("req") == "getScannerPorts":
                return JsonResponse(rst)
            elif request.GET.get("req") == "getConfig":
                return JsonResponse(rst)
            elif request.GET.get("req") == "getFile":
                cc = {}
                cc['result'] = rst
                return render(request, "empty.html", context=cc)
            elif request.GET.get("req") == "getDBRecord":
                return JsonResponse(rst, safe=False)
            elif request.GET.get("req") == "getIPDBRecord":
                return JsonResponse(rst, safe=False)
            elif request.GET.get("req") == "getIPDBdashboard":
                return JsonResponse(rst)
            elif request.GET.get("req") == "checkIPDBVersion":
                return JsonResponse(rst)
            elif request.GET.get("req") == "updateIPDBVersion":
                return JsonResponse(rst, safe=False)
            elif request.GET.get("req") == "getSystemStatus":
                cc = {}
                cc['result'] = rst
                return render(request, "empty.html", context=cc)
            elif request.GET.get("req") == "getFingerPrint":
                return JsonResponse(rst, safe=False)
            elif request.GET.get("req") == "getFingerprintBlackList":
                cc = {}
                cc['result'] = rst
                return render(request, "empty.html", context=cc)
            elif request.GET.get("req") == "getUserList":
                return JsonResponse(rst, safe=False)
            elif request.GET.get("req") == "getScannerLog":
                return JsonResponse(rst, safe=False)
            elif request.GET.get("req") == "getSystemLog":
                return JsonResponse(rst, safe=False)
            elif request.GET.get("req") == "getThreadDelay":
                return JsonResponse(rst, safe=False)
            else:
                return HttpResponse(rst)
    except Exception as e:
        print(e)
        try:
            GEsys.addLog("系统异常", e, request.session["username"], request.META.get("REMOTE_ADDR"))
        except:
            GEsys.addLog("系统异常", e, "None", request.META.get("REMOTE_ADDR"))
        c["title"] = "GodEyes服务器错误"
        c["info"] = "服务器错误，请联系网站管理员，细节见日志。"
        return render(request, "info.html", c)


@gzip_page
def set_data(request):
    c = {"title": "null", "info": "null"}
    if request.method != "POST":
        GEsys.addLog("错误", "不允许的请求方式[SET]", request.session["username"], request.META.get("REMOTE_ADDR"))
        c["title"] = "不允许的访问"
        c["info"] = "请求无法直接访问"
        return render(request, "info.html", c)
    try:
        if request.COOKIES['csrftoken'] is not "" and (request.session["ip"] is not None) and request.session["ip"] == \
                request.META['REMOTE_ADDR']:
            if request.POST.get("req") == 'install':
                return JsonResponse(control.set_data(request), safe=False)

            if not request.session.get("username"):
                c["title"] = "不允许的访问"
                c["info"] = "请求无法直接访问"
                return render(request, "info.html", c)
            rst = control.set_data(request)
            if request.POST.get("req") == "save_portList":
                return JsonResponse(rst)
            if request.POST.get("req") == "changeConfig":
                return JsonResponse(rst)
            if request.POST.get("req") == "setFile":
                return JsonResponse(rst)
            if request.POST.get("req") == "setDBItem":
                return JsonResponse(rst, safe=False)
            if request.POST.get("req") == "setFingerprintBlackList":
                return JsonResponse(rst)
            if request.POST.get("req") == "rebuildFingerPrint":
                return JsonResponse(rst)
            if request.POST.get("req") == "setUserInfo":
                return JsonResponse(rst)
            if request.POST.get("req") == "deleteUser":
                return JsonResponse(rst)
            if request.POST.get("req") == "addUserInfo":
                return JsonResponse(rst)
            if request.POST.get("req") == "addLog":
                return JsonResponse(rst)
            if request.POST.get("req") == "clearDataTable":
                return JsonResponse(rst)
            if request.POST.get("req") == "startScanner":
                return JsonResponse(rst)
            if request.POST.get("req") == "stopAllThreads":
                return JsonResponse(rst, safe=False)
        else:
            GEsys.addLog("系统异常", "账号异地登陆", request.session["username"], request.META.get("REMOTE_ADDR"))
            logout()

    except Exception as e:
        traceback.print_exc()
        try:
            GEsys.addLog("系统异常", e, request.session["username"], request.META.get("REMOTE_ADDR"))
        except:
            GEsys.addLog("系统异常", e, "None", request.META.get("REMOTE_ADDR"))
        c["title"] = "GodEyes服务器错误"
        c["info"] = "服务器错误，请联系网站管理员，细节见日志。"
        return render(request, "info.html", c)


@gzip_page
def dashBoard(request):
    GEsys.addLog("仪表盘", "访问仪表盘(首页)页面", request.session["username"], request.META.get("REMOTE_ADDR"))
    c = {"title": "null", "info": "null", "power": request.session.get("power"), 'account': request.session['username']}
    return render(request, 'dashBoard.html', c)


@gzip_page
def modifyAccountDo(request):
    c = {"title": "null", "info": "null"}
    try:
        if request.session['username'] != request.POST.get("username"):
            c["title"] = "不允许的访问"
            c["info"] = "登陆页面不允许直接访问"
            return render(request, "info.html", c)
    except Exception as e:
        c["title"] = "不允许的访问"
        c["info"] = "登陆页面不允许直接访问"
        return render(request, "info.html", c)

    try:
        account = request.POST.get("username")
        oldpassword = request.POST.get("password")
        newpassword = request.POST.get("password1")
        repassword = request.POST.get("password2")
        c = control.modifyAccount(account, oldpassword, newpassword, repassword, request)
        if c["title"] == "修改成功":
            request.session.clear()
            request.session.flush()
        return render(request, "info.html", c)
    except Exception as e:
        c["title"] = "参数不完整"
        c["info"] = "请将4项内容填写完整"
        return render(request, "info.html", c)


@gzip_page
def scanner(request):
    try:
        GEsys.addLog("扫描器", "访问综合扫描器页面", request.session["username"], request.META.get("REMOTE_ADDR"))
    except:
        c = {"title": "GodEyes服务器错误", "info": "服务器错误，请联系网站管理员，细节见日志。"}
        return render(request, "info.html", c)
    c = {"title": "null", "info": "null", "power": request.session.get("power"), 'account': request.session['username']}
    return render(request, 'scanner.html', c)


def test(request):
    pass


@gzip_page
def portSettings(request):
    try:
        GEsys.addLog("扫描器", "访问端口设置页面", request.session["username"], request.META.get("REMOTE_ADDR"))
    except:
        c = {"title": "GodEyes服务器错误", "info": "服务器错误，请联系网站管理员，细节见日志。"}
        return render(request, "info.html", c)
    c = {"title": "null", "info": "null", "power": request.session.get("power"), 'account': request.session['username']}
    return render(request, 'portSettings.html', c)


@gzip_page
def requestConstructor(request):
    try:
        GEsys.addLog("扫描器", "访问请求构造页面", request.session["username"], request.META.get("REMOTE_ADDR"))
    except:
        c = {"title": "GodEyes服务器错误", "info": "服务器错误，请联系网站管理员，细节见日志。"}
        return render(request, "info.html", c)
    c = {"title": "null", "info": "null", "power": request.session.get("power"), 'account': request.session['username']}
    return render(request, 'requestConstructor.html', c)


@gzip_page
def crackRules(request):
    try:
        GEsys.addLog("扫描器", "访问穷举爆破规则页面", request.session["username"], request.META.get("REMOTE_ADDR"))
    except:
        c = {"title": "GodEyes服务器错误", "info": "服务器错误，请联系网站管理员，细节见日志。"}
        return render(request, "info.html", c)

    c = {"title": "null", "info": "null", "power": request.session.get("power"), 'account': request.session['username']}
    return render(request, 'crackRules.html', c)


@gzip_page
def dataManager(request):
    try:
        GEsys.addLog("数据中心", "访问数据管理页面", request.session["username"], request.META.get("REMOTE_ADDR"))
    except:
        c = {"title": "GodEyes服务器错误", "info": "服务器错误，请联系网站管理员，细节见日志。"}
        return render(request, "info.html", c)

    c = {"title": "null", "info": "null", "power": request.session.get("power"), 'account': request.session['username']}
    return render(request, 'dataManager.html', c)


@gzip_page
def ipTableManager(request):
    try:
        GEsys.addLog("数据中心", "访问IP库页面", request.session["username"], request.META.get("REMOTE_ADDR"))
    except:
        c = {"title": "GodEyes服务器错误", "info": "服务器错误，请联系网站管理员，细节见日志。"}
        return render(request, "info.html", c)

    c = {"title": "null", "info": "null", "power": request.session.get("power"), 'account': request.session['username']}
    return render(request, 'ipTableManager.html', c)


@gzip_page
def fingerPrint(request):
    try:
        GEsys.addLog("数据中心", "访问指纹管理页面", request.session["username"], request.META.get("REMOTE_ADDR"))
    except:
        c = {"title": "GodEyes服务器错误", "info": "服务器错误，请联系网站管理员，细节见日志。"}
        return render(request, "info.html", c)

    c = {"title": "null", "info": "null", "power": request.session.get("power"), 'account': request.session['username']}
    return render(request, 'fingerPrint.html', c)


@gzip_page
def license(request):
    try:
        GEsys.addLog("帮助", "查看许可证信息", request.session["username"], request.META.get("REMOTE_ADDR"))
    except:
        c = {"title": "GodEyes服务器错误", "info": "服务器错误，请联系网站管理员，细节见日志。"}
        return render(request, "info.html", c)

    c = {"title": "null", "info": "null", "power": request.session.get("power"), 'account': request.session['username']}
    return render(request, 'license.html', c)


@gzip_page
def Disclaimer(request):
    try:
        GEsys.addLog("帮助", "查看免责声明信息", request.session["username"], request.META.get("REMOTE_ADDR"))
    except:
        c = {"title": "GodEyes服务器错误", "info": "服务器错误，请联系网站管理员，细节见日志。"}
        return render(request, "info.html", c)

    c = {"title": "null", "info": "null", "power": request.session.get("power"), 'account': request.session['username']}
    return render(request, 'Disclaimer.html', c)


@gzip_page
def help(request):
    try:
        GEsys.addLog("帮助", "查看帮助文档信息", request.session["username"], request.META.get("REMOTE_ADDR"))
    except:
        c = {"title": "GodEyes服务器错误", "info": "服务器错误，请联系网站管理员，细节见日志。"}
        return render(request, "info.html", c)

    c = {"title": "null", "info": "null", "power": request.session.get("power"), 'account': request.session['username']}
    return render(request, 'help.html', c)


@gzip_page
def userManager(request):
    try:
        GEsys.addLog("系统设置", "用户管理", request.session["username"], request.META.get("REMOTE_ADDR"))
    except:
        c = {"title": "GodEyes服务器错误", "info": "服务器错误，请联系网站管理员，细节见日志。"}
        return render(request, "info.html", c)

    c = {"title": "null", "info": "null", "power": request.session.get("power"), 'account': request.session['username']}
    return render(request, 'userManager.html', c)


@gzip_page
def scannerLog(request):
    try:
        GEsys.addLog("系统设置", "查看扫描器日志", request.session["username"], request.META.get("REMOTE_ADDR"))
    except:
        c = {"title": "GodEyes服务器错误", "info": "服务器错误，请联系网站管理员，细节见日志。"}
        return render(request, "info.html", c)

    c = {"title": "null", "info": "null", "power": request.session.get("power"), 'account': request.session['username']}
    return render(request, 'scannerLog.html', c)


@gzip_page
def systemLog(request):
    try:
        GEsys.addLog("系统设置", "查看系统日志", request.session["username"], request.META.get("REMOTE_ADDR"))
    except:
        c = {"title": "GodEyes服务器错误", "info": "服务器错误，请联系网站管理员，细节见日志。"}
        return render(request, "info.html", c)

    c = {"title": "null", "info": "null", "power": request.session.get("power"), 'account': request.session['username']}
    return render(request, 'systemLog.html', c)


@gzip_page
def systemConfig(request):
    try:
        GEsys.addLog("系统设置", "修改系统配置文件", request.session["username"], request.META.get("REMOTE_ADDR"))
    except:
        c = {"title": "GodEyes服务器错误", "info": "服务器错误，请联系网站管理员，细节见日志。"}
        return render(request, "info.html", c)

    c = {"title": "null", "info": "null", "power": request.session.get("power"), 'account': request.session['username']}
    return render(request, 'systemConfig.html', c)


@gzip_page
def ClearData(request):
    try:
        GEsys.addLog("系统设置", "访问清空数据表页面", request.session["username"], request.META.get("REMOTE_ADDR"))
    except:
        c = {"title": "GodEyes服务器错误", "info": "服务器错误，请联系网站管理员，细节见日志。"}
        return render(request, "info.html", c)

    c = {"title": "null", "info": "null", "power": request.session.get("power"), 'account': request.session['username']}
    return render(request, 'ClearData.html', c)


@gzip_page
def donate(request):
    try:
        GEsys.addLog("捐赠页面", "访问捐赠页面", request.session["username"], request.META.get("REMOTE_ADDR"))
    except:
        c = {"title": "GodEyes服务器错误", "info": "服务器错误，请联系网站管理员，细节见日志。"}
        return render(request, "info.html", c)

    c = {"title": "null", "info": "null", "power": request.session.get("power"), 'account': request.session['username']}
    return render(request, 'donate.html', c)


def errorPage(request,e =None):
    type, value, tb = sys.exc_info()
    print(traceback.format_exception(type, value, tb))
    c = {"title": "系统故障", "info": "服务器故障，可能是后台未及时响应或页面不存在"}
    return HttpResponseServerError(render(request, "info.html", c))
