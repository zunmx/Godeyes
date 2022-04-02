// 防止开发者工具断点调试
setInterval(function () {
    debugger;
}, 1)

// 服务器异常检测
function ServerError(rst) {
    if (String(rst).indexOf("GodEyes服务器错误") !== -1) {
        swal({
            title: "GodEyes服务器错误",
            text: '服务器错误，请联系网站管理员，细节见日志。如果是长时间未操作，请重新登录系统。',
            icon: "error",
            button: true,
            closeOnClickOutside: false,
            closeOnEsc: false
        });
        console.log("ERROR");
        throw "GodEyes服务器错误";
    }
}

function ajax_getInfo(req, code = null, arg1 = null, arg2 = null, arg3 = null) {
    $("#GEsystem-status").html("系统响应中...")
    var defer = $.Deferred();
    $.ajax({
        type: "get",
        url: "get_data",
        // async: false,
        data: {
            "req": req,
            "code": code,
            "arg1": arg1,
            "arg2": arg2,
            "arg3": arg3
        },
        timeout: 600000,
        xhrFields: {
            withCredentials: true // 发送Ajax时，Request header中会带上 Cookie 信息。
        },
        crossDomain: true, // 发送Ajax时，Request header 中会包含跨域的额外信息，但不会含cookie（作用不明，不会影响请求头的携带）
        success: function (backData) {
            defer.resolve(backData)
            $("#GEsystem-status").html("系统运行中...")
        }
    });

    return defer.promise();
    // return rst;
}

function ajax_setInfo(req, code = null, arg1 = null, arg2 = null, arg3 = null) {
    $("#GEsystem-status").html("系统响应中...")
    $.ajaxSetup({
        data: {csrfmiddlewaretoken: $.cookie('csrftoken')}
    })
    var rst = 1;
    $.ajax({
        type: "post",
        url: "set_data",
        async: false,
        data: {
            "req": req,
            "code": code,
            "arg1": arg1,
            "arg2": arg2,
            "arg3": arg3
        },
        xhrFields: {
            withCredentials: true // 发送Ajax时，Request header中会带上 Cookie 信息。
        },
        crossDomain: true, // 发送Ajax时，Request header 中会包含跨域的额外信息，但不会含cookie（作用不明，不会影响请求头的携带）
        success: function (data) {
            rst = data;
            $("#GEsystem-status").html("系统运行中...")
        },
    });
    return rst;

}

function ajax_dashBoardData_news(tp, ip, port, address, intime) {
    $("#dashboardData0").append(
        "<tr>" +
        "<td>" +
        "<div class=\"flag\">" +
        "<img src=\"../static/imgs/" + tp + ".png\"alt=\"http(s)\" title='" + tp + "'>" +
        "</div>" +
        "</td>" +
        "<td id>" + ip + "</td>" +
        "<td class=\"text-right\">" +
        port +
        "</td>" +
        "<td class=\"text-right\">" +
        address +
        "</td>" +
        "<td class=\"text-right\">" +
        intime +
        "</td>" +
        "</tr>"
    );
}

function getDashBoardUpload() {
    $.when(ajax_getInfo("db_http_total")).done(function (rst) {
        ServerError(rst);
        $("#db_http_total").html(rst);
    })
    $.when(ajax_getInfo("db_ssh_total")).done(function (rst) {
        ServerError(rst);
        $("#db_ssh_total").html(rst);

    })
    $.when(ajax_getInfo("db_mysql_total")).done(function (rst) {
        ServerError(rst);
        $("#db_mysql_total").html(rst);
    })
}

function ajax_Scanner_portlist(row, http, mysql, ssh, telnet) {
    if (http == null) {
        http = "---";
    }
    if (mysql == null) {
        mysql = "---";
    }
    if (ssh == null) {
        ssh = "---";
    }
    if (telnet == null) {
        telnet = "---";
    }
    $("#ScannerPortsListTable").append(
        "<tr role=\"row\" className=\"" + row + "\">\n" +
        "<td className=\"\">" + http + "</td>\n" +
        "<td className=\"\">" + mysql + "</td>\n" +
        "<td className=\"\">" + ssh + "</td>\n" +
        "<td className=\"sorting_1\">" + telnet + "</td>\n" +
        "</tr>"
    );
}

function loadDashBoardNews() {
    $("#dashboardData0").html("");

    $.when(ajax_getInfo("get_record", 'http', 'last', 2)).done(function (rst) {
        ServerError(rst);
        let json_data = rst;
        $.each(json_data, function (i, item) {
            ajax_dashBoardData_news('http', item.ip, item.port, item.address, item.intime);
        })
    });
    $.when(ajax_getInfo("get_record", 'mysql', 'last', 2)).done(function (rst) {
        ServerError(rst);
        let json_data = rst;
        $.each(json_data, function (i, item) {
            ajax_dashBoardData_news('mysql', item.ip, item.port, item.address, item.intime);
        })
    });
    $.when(ajax_getInfo("get_record", 'ssh', 'last', 2)).done(function (rst) {
        ServerError(rst);
        let json_data = rst;
        $.each(json_data, function (i, item) {
            ajax_dashBoardData_news('ssh', item.ip, item.port, item.address, item.intime);
        })
    });
    $.when(ajax_getInfo("get_record", 'telnet', 'last', 2)).done(function (rst) {
        ServerError(rst);
        let json_data = rst;
        $.each(json_data, function (i, item) {
            ajax_dashBoardData_news('telnet', item.ip, item.port, item.address, item.intime);
        })
    });

}

function loadDashBoardThreadNumber() {
    $.when(ajax_getInfo("get_thread_info")).done(function (rst) {
        ServerError(rst);
        let json_data = rst;
        $.each(json_data, function (i, item) {
            $("#thread_-total_num").html(item.totalThreadNum)
            $("#thread_http_num").html(item.httpThreadNum);
            $("#thread_mysql_num").html(item.mysqlThreadNum);
            $("#thread_ssh_num").html(item.sshThreadNum);
            $("#thread_telnet_num").html(item.telnetThreadNum);
        });
    })


}

function loadLogSWEInfo() {
    $.when(ajax_getInfo("getLogSWE")).done(function (rst) {
        ServerError(rst);
        let json_data = rst;
        $.each(json_data, function (i, item) {
            $("#dashboard_event_record").html(item.S);
            $("#dashboard_event_warning").html(item.W);
            $("#dashboard_event_error").html(item.E);
            if (parseInt(item.E) > parseInt(item.S) + parseInt(item.W)) {
                $("#system_status").attr("class", "badge badge-warning");
                $("#system_status").html("?");
            } else {
                $("#system_status").attr("class", "badge badge-success");
                $("#system_status").html("√");
            }
        })
    })


}

function getIpDetailsInfo() {
    var ipoCIDR = document.getElementById("ipScannerInputBox").value
    if (ipoCIDR == 'random') {
        $("#inputDetail").html("地址随机");
        return;
    }
    // var param = ipoCIDR.split(".")
    // for (let i = 0; i < param.length; i++) {
    //     if (param[i] == "/")
    //         continue
    //     if (param[i].length > 3) {
    //         $("#inputDetail").html("输入的地址不合法");
    //         return;
    //     }
    //
    // }
    // if (ipoCIDR.length > 18) {
    //
    //     $("#inputDetail").html("输入的地址不合法");
    //     return;
    // }

    // ip格式是否合法，总共包含多少个ip。
    $.when().done(function (rst) {
        ServerError(rst);

        $.when(ajax_getInfo("ipScannerInputBox", ipoCIDR)).done(function (rst) {
            ServerError(rst);
            $.each(rst, function (i, item) {

                if (item.ipCount > 0) {
                    $("#inputDetail").html("总共标记了：" + item.ipCount + " 个IP地址，其中起始地址为：" + item.start + " 结束地址为： " + item.end);
                } else {
                    $("#inputDetail").html("输入的地址不合法，详细返回值：" + item.details);
                }
            })
        })


    })


}

function getScannerPorts(code, arg1, arg2) {
    $.when(ajax_getInfo("getScannerPorts", code, arg1)).done(function (rst) {
        ServerError(rst);
        let json_data = rst;
        let _http = {};
        let _mysql = {};
        let _ssh = {};
        let _telnet = {};
        $.each(json_data, function (i, item) {
            if (code === 'all') {
                _http = item.http;
                _mysql = item.mysql;
                _ssh = item.ssh;
                _telnet = item.telnet;
            } else {
                switch (code) {
                    case 'mysql':
                        _mysql = item.mysql;
                        break;
                    case 'ssh':
                        _ssh = item.ssh;
                        break;
                    case 'telnet':
                        _telnet = item.telnet;
                        break;
                    case 'http':
                        _http = item.http;
                        break;
                }
            }
            let max = (_http.length > _mysql.length ? _http.length : _mysql.length) >
            (_ssh.length > _telnet.length ? _ssh.length : _telnet.length) ?
                (_http.length > _mysql.length ? _http.length : _mysql.length) :
                (_ssh.length > _telnet.length ? _ssh.length : _telnet.length);
            if (arg2 === 'scanner') {
                for (let i = 0; i < max; i++) {
                    ajax_Scanner_portlist(i % 2 === 0 ? 'odd' : 'even', _http[i], _mysql[i], _ssh[i], _telnet[i])
                }
            } else if (arg2 === 'portSettings') {
                var tmp = ""
                if (code === 'http') {
                    // document.getElementById('httpsList').value = ""
                    for (let i = 0; i < _http.length; i++) {
                        tmp += _http[i] + "\n"
                        $("#httpsList").val(tmp)
                    }
                } else if (code === 'telnet') {
                    tmp = ""
                    for (let i = 0; i < _telnet.length; i++) {
                        tmp += _telnet[i] + "\n"
                        $("#telnetList").val(tmp)
                    }
                } else if (code === 'ssh') {
                    tmp = ""
                    for (let i = 0; i < _ssh.length; i++) {
                        tmp += _ssh[i] + "\n"
                        $("#sshList").val(tmp)
                    }
                } else if (code === 'mysql') {
                    tmp = ""
                    for (let i = 0; i < _mysql.length; i++) {
                        tmp += _mysql[i] + "\n"
                        $("#_mysqlList").val(tmp)
                    }
                } else if (code === 'all') {
                    tmp = ""
                    for (let i = 0; i < _mysql.length; i++) {
                        tmp += _mysql[i] + "\n"
                    }
                    $("#mysqlList").val(tmp)
                    tmp = ""
                    for (let i = 0; i < _ssh.length; i++) {
                        tmp += _ssh[i] + "\n"
                    }
                    $("#sshList").val(tmp)
                    tmp = ""
                    for (let i = 0; i < _telnet.length; i++) {
                        tmp += _telnet[i] + "\n"
                    }
                    $("#telnetList").val(tmp)
                    tmp = ""
                    for (let i = 0; i < _http.length; i++) {
                        tmp += _http[i] + "\n"
                    }
                    $("#httpsList").val(tmp)

                }

            }

        })
        $('#basic-datatables').DataTable({});
        $('#multi-filter-select').DataTable({
            "pageLength": 5, retrieve: true,
            initComplete: function () {
                this.api().columns().every(function () {
                    var column = this;

                    var select = $('<select class="form-control"><option value=""></option></select>')
                        .appendTo($(column.footer()).empty())
                        .on('change', function () {
                            var val = $.fn.dataTable.util.escapeRegex(
                                $(this).val()
                            );

                            column
                                .search(val ? '^' + val + '$' : '', true, false)
                                .draw();
                        });
                    column.data().unique().sort().each(function (d, j) {
                        select.append('<option value="' + d + '">' + d + '</option>')
                    });
                });
            }
        });
    })


}

function isIntNumber(num) {
    let str = num.toString()
    for (let i = 0; i < str.length; i++) {
        if (!(str[i] >= '0' && str[i] <= '9')) {
            return false;
        }
    }
    return true;
}

function checkScannerPortInvalid(func) {
    let targetList;
    let flag = true;
    switch (func) {
        case 'http':
            targetList = document.getElementById('httpsList');
            break;
        case 'mysql':
            targetList = document.getElementById('mysqlList');
            break;
        case 'ssh':
            targetList = document.getElementById('sshList');
            break;
        case 'telnet':
            targetList = document.getElementById('telnetList');
            break;
        default:
            swal({
                title: '不支持的接口',
                text: '尚未支持此接口',
                icon: "error",
                timer: 1000,
                buttons: false,
            });
            flag = false;
            break;
    }
    let box = targetList.value.split('\n');
    for (let i = 0; i < box.length; i++) {
        if (!isIntNumber(box[i]) && box[i] !== '') {
            let temp = document.getElementById(func + '_title').innerText
            $(info_i).text(temp + "[" + parseInt(i + 1) + "]" + "行错误")
            $(info_i).css("color", "red")
            flag = false;
            break;
        }
    }
    if (flag) {
        let temp = document.getElementById(func + '_title').innerText
        $(info_i).text(temp + " 检查无误。")
        $(info_i).css("color", "green")
    }
    return flag;
}

function save_portList(func) {
    let targetList;
    switch (func) {
        case 'http':
            targetList = document.getElementById('httpsList');
            break;
        case 'mysql':
            targetList = document.getElementById('mysqlList');
            break;
        case 'ssh':
            targetList = document.getElementById('sshList');
            break;
        case 'telnet':
            targetList = document.getElementById('telnetList');
            break;
        default:
            swal({
                title: '不支持的接口',
                text: '尚未支持此接口',
                icon: "error",
                timer: 1000,
                buttons: false,
            });
            break;
    }
    if (!checkScannerPortInvalid(func)) {

        swal({
            title: '错误',
            text: '保存校验错误，请检查端口合法性！',
            icon: "error",
            timer: 1000,
            buttons: false,
        });
        return false;
    } else {
        let json_data = ajax_setInfo("save_portList", func, targetList.value)
        $.each(json_data, function (i, item) {
            if (item.code === 0) {
                let temp = document.getElementById(func + '_title').innerText
                $(info_i).text(temp + " 保存成功")
                $(info_i).css("color", "green")
            }
        })
    }
}

function changeRCMode(who) {
    // if (String(who.getAttribute('class')).indexOf("active") !== -1)
    //     return;
    switch (who.id) {
        case 'req_constructor_normal_switch':
            $("#req_constructor_custom_switch").removeClass("active");
            $(who).addClass("active");
            ajax_setInfo("changeConfig", "req_constructor", "normal")
            $("#requestHeader").prop("contenteditable", false)
            break;

        case 'req_constructor_custom_switch':
            $("#req_constructor_normal_switch").removeClass("active");
            $(who).addClass("active");
            ajax_setInfo("changeConfig", "req_constructor", "custom")
            $("#requestHeader").prop("contenteditable", true)
            break;
    }
}

function getRCMode() {
    $("#req_constructor_custom_switch").removeClass("active");
    $("#req_constructor_normal_switch").removeClass("active");

    $.when(ajax_getInfo("getConfig", "req_constructor",)).done(function (rst) {
        ServerError(rst);
        let json_data = rst;
        $.each(json_data, function (i, item) {
            switch (item.HttpRequestHeaderMethod) {
                case 'custom':
                    $("#requestHeader").prop("contenteditable", true)
                    $("#req_constructor_custom_switch").addClass("active");
                    break;
                case 'normal':
                    $("#req_constructor_normal_switch").addClass("active");
                    $("#requestHeader").prop("contenteditable", false)
                    break;
            }
        })
    })


}

function ReqConstructOper(method, arg = null) {
    switch (method) {
        case 'r':
            $.when(ajax_getInfo("getFile", 'requestConstruct')).done(function (rst) {
                ServerError(rst)
                output(rst)
                if (arg !== null && arg !== 'firstRun') {
                    swal("操作成功", "重载加载操作执行成功", {
                        icon: "success",
                        buttons: {
                            confirm: {
                                className: 'btn btn-success'
                            }
                        },
                    });
                }

            })
            break;
        case 'w':
            let json_data = ajax_setInfo("setFile", 'requestConstruct', arg)
            $.each(json_data, function (i, item) {
                if (item.success)
                    swal({
                        title: '成功',
                        text: '保存成功',
                        icon: "success",
                        timer: 1000,
                        buttons: false,
                    });
                else
                    swal({
                        title: '失败',
                        text: '保存失败',
                        timer: 1000,
                        icon: "error",
                        buttons: false,
                    });
            })
            break;

        default:
            alert("非法请求！")
            break;
    }
}

function getCrackRulesSelected() {
    let box = document.getElementsByClassName("selectgroup-input");
    for (var i = 0; i < box.length; i++) {
        if (box[i].checked) {
            return box[i].value;
        }
    }
}

function CreateCrackFile(server, file) {
    swal({
        title: '新建',
        icon: "info",
        // closeOnClickOutside: false,
        content: {
            element: "input",
            attributes: {
                placeholder: "请输入要新建的文件名",
                type: "text",
                id: "context"
            },
        }, buttons: {
            Yes: {
                text: "确定",
                value: "yes",
                className: 'btn btn-success',
            },
            No: {
                text: "取消",
                value: 'no',
                className: 'btn btn-danger'
            }
        }
    }).then((value) => {
        switch (value) {
            case 'yes':
                crackFileOper(server, 'n', file, context.value)
                swal.stopLoading();
                break;
            case 'no':
            default:
                swal({
                    title: '取消操作',
                    text: '用户取消操作',
                    timer: 200,
                    buttons: false,
                });
                break;

        }
    })
}

function AddCrackListItem(item) {
    document.getElementById("UFilename").options.add(new Option(item, item));
    document.getElementById("PFilename").options.add(new Option(item, item));
}

function crackFileOper(type, method, uop, filename = null, context = null) {
    /**
     * type in mysql ssh telnet
     * method in r/w/d/n/l/c
     * uop in userFile/passwordFile
     * filename point file
     * context using to write file text
     */

    let text = "";
    switch (method) {
        case 'r':
            $.when(ajax_getInfo('getConfig', 'crackFile', "getCrackFilePath", type)).done(function (rst) {
                text = rst;
                $.each(text, function (i, item) {
                        for (let i = 0; i < UFilename.options.length; i++) {
                            if (UFilename.options[i].text === item.Ufile_name) {
                                UFilename.options[i].selected = true;
                            }
                            if (PFilename.options[i].text === item.Pfile_name) {
                                PFilename.options[i].selected = true;
                            }
                        }
                    }
                );
                let errcount = 0;
                $.when(ajax_getInfo('getFile', 'crackFile', "getCrackUserFile", type)).done(function (rst) {
                    lst1 = rst;
                    if (lst1 === '文件不存在') {
                        errcount += 1;
                        if (errcount === 2) {
                            swal({
                                title: '失败',
                                text: '账号/密码文件均不存在',
                                timer: 5000,
                                icon: "error",
                                buttons: {
                                    confirm: {
                                        text: '我知道了'
                                    }
                                }
                            });
                            return;
                        }
                        swal({
                            title: '失败',
                            text: '账号文件不存在',
                            timer: 5000,
                            icon: "error",
                            buttons: {
                                confirm: {
                                    text: '我知道了'
                                }
                            }
                        });
                        return;
                    } else {

                        AccountList.value = lst1;
                    }
                })
                $.when(ajax_getInfo('getFile', 'crackFile', "getCrackPasswordFile", type)).done(function (rst) {
                    lst2 = rst;
                    errcount += 1;
                    if (errcount === 2) {
                        swal({
                            title: '失败',
                            text: '账号/密码文件均不存在',
                            timer: 5000,
                            icon: "error",
                            buttons: {
                                confirm: {
                                    text: '我知道了'
                                }
                            }
                        });
                        return;
                    }
                    if (lst2 === '文件不存在') {
                        swal({
                            title: '失败',
                            text: '密码文件不存在',
                            timer: 5000,
                            icon: "error",
                            buttons: {
                                confirm: {
                                    text: '我知道了'
                                }
                            }
                        });
                        return;
                    } else {
                        PasswordList.value = lst2;
                    }
                })


            })


            break;  //读文件
        case 'n':
            text = ajax_setInfo('changeConfig', 'newCrackRules', type, uop, filename)
            $.each(text, function (i, item) {
                if (item.status === 'success') {
                    swal({
                        title: '创建成功',
                        text: '文件创建成功',
                        icon: "success",
                        timer: 1000,
                        buttons: false,
                    });
                    crackFileOper('', 'l')
                    crackFileOper(getCrackRulesSelected(), 'r')

                } else {
                    swal({
                        title: '创建失败',
                        text: item.status,
                        icon: "error",
                        timer: 1000,
                        buttons: false,
                    });
                }
            })
            break;  //新建
        case 'd':
            swal({
                title: '请求确认',
                icon: "warning",
                text: "要删除" + filename + "这个文件嘛？",
                buttons: {
                    confirm: {
                        text: '确定',
                        className: 'btn btn-success'
                    },
                    cancel: {
                        text: '取消',
                        visible: true,
                        className: 'btn btn-danger'
                    }
                }
            }).then((confirm) => {
                if (confirm) {
                    text = ajax_setInfo('setFile', 'delCrackFile', type, uop, context)
                    $.each(text, function (i, item) {
                        if (item.code === 0) {
                            crackFileOper('', 'l')
                            crackFileOper(getCrackRulesSelected(), 'r')
                            swal({
                                title: '请求成功',
                                text: item.details,
                                icon: 'success',
                                timer: 1000,
                                buttons: false
                            });
                        } else {
                            swal({
                                title: '请求成功',
                                text: item.details,
                                icon: 'error',
                                timer: 1000,
                                buttons: false
                            });
                        }
                    })

                } else {
                    swal({
                        title: '取消操作',
                        text: '用户取消操作',
                        timer: 200,
                        buttons: false,
                    });
                }
            });

            break;  //删除
        case 's':
            text = ajax_setInfo('setFile', 'saveCrackFile', type, uop, context)
            $.each(text, function (i, item) {
                if (item.details === 'Successfully') {
                    swal({
                        title: '保存成功',
                        text: '文件保存成功',
                        icon: "success",
                        timer: 1000,
                        buttons: false,
                    });
                } else {
                    swal({
                        title: '创建失败',
                        text: item.status,
                        icon: "error",
                        timer: 1000,
                        buttons: false,
                    });
                }
            });
            break;  //保存
        case 'l':
            $.when(ajax_getInfo('getConfig', 'crackFile', "getCrackFileList")).done(function (rst) {
                text = rst
                ServerError(rst)
                document.getElementById("UFilename").innerHTML = "";
                document.getElementById("PFilename").innerHTML = "";
                for (i in text["ojbk"]) {
                    AddCrackListItem(text["ojbk"][i]);
                }
            })


            break;  //列表  //选择
        case 'c':
            text = ajax_setInfo('changeConfig', 'saveCrackFilePath', type, uop, filename)
            $.each(text, function (i, item) {
                if (item.status === 'success') {
                    swal({
                        title: '修改成功',
                        text: '配置文件修改成功',
                        icon: "success",
                        timer: 1000,
                        buttons: false,
                    });


                    $.when(ajax_getInfo('getFile', 'crackFile', "getCrackUserFile", type)).done(function (rst) {
                        AccountList.value = rst;
                    })
                    $.when(ajax_getInfo('getFile', 'crackFile', "getCrackPasswordFile", type)).done(function (rst) {
                        PasswordList.value = rst;
                    })

                } else {
                    swal({
                        title: '修改失败',
                        text: item.status,
                        icon: "error",
                        timer: 1000,
                        buttons: false,
                    });
                }
            })
            break;  //
        default:
            swal({
                title: '请求非法',
                text: "未能识别的请求",
                icon: "error",
                timer: 1000,
                buttons: false,
            });
            break;
    }

}

function getDBMSelected() {
    return document.getElementById("DBMSelect").options.selectedIndex;
}

function getIPDSelected() {
    return document.getElementById("IPDSelect").options.selectedIndex;
}

function dataManager_db_oper(ip2port, func, content = null) {
    if (func === 'd') {
        swal({
            title: '请求确认',
            icon: "warning",
            text: "要删除" + $.cookie('innerSeleted') + "记录[" + ip2port + "]这条数据吗？？",
            buttons: {
                confirm: {
                    text: '确定',
                    className: 'btn btn-success'
                },
                cancel: {
                    text: '取消',
                    visible: true,
                    className: 'btn btn-danger'
                }
            }
        }).then((confirm) => {
            if (confirm) {
                $.when(ajax_setInfo('setDBItem', 'delRecord', $.cookie('innerSeleted'), ip2port,)).done(function (rst) {
                    try {
                        rst = JSON.parse(rst);
                    } catch {
                    }
                    ServerError(rst)
                    $.each(rst, function (i, item) {
                        try {
                            if (item.code == -1) {
                                swal({
                                    title: '请求不合法',
                                    text: item.detail,
                                    icon: 'error',
                                    timer: 1000,
                                    buttons: false
                                });
                                return;
                            }

                        } catch {

                        }
                        if (item.row !== 0) {
                            swal({
                                title: '请求成功',
                                text: "删除成功，受影响的记录：" + item.row,
                                icon: 'success',
                                timer: 1000,
                                buttons: false
                            });
                            dataManager_item_oper(
                                $.cookie('innerSeleted'),
                                1,
                                getDBMSelected(),
                                $.cookie('innerFinder')
                            );
                        } else {
                            swal({
                                title: '请求成功',
                                text: "删除失败，记录不存在",
                                icon: 'error',
                                timer: 1000,
                                buttons: false
                            });
                        }
                    })
                })
            } else {
                swal({
                    title: '取消操作',
                    text: '用户取消操作',
                    timer: 200,
                    buttons: false,
                });
            }
        });
    }
    if (func === 'c') {
        var text = ($.cookie('innerSeleted') === "http") ? "  要修改" + $.cookie('innerSeleted') + "记录[" + ip2port + "]中的数据吗？？\r\n数据均由GodEyes自动抓取，修改后可能影响结果的准确性。此结果将把内容存储到text中，造成标题和请求体冗余。" : "  要修改" + $.cookie('innerSeleted') + "记录[" + ip2port + "]中的数据吗？？\r\n数据均由GodEyes自动抓取，修改后可能影响结果的准确性。"
        swal({
            title: '请求修改',
            icon: "warning",
            text: text,
            buttons: {
                confirm: {
                    text: '确定',
                    className: 'btn btn-success'
                },
                cancel: {
                    text: '取消',
                    visible: true,
                    className: 'btn btn-danger'
                }
            }
        }).then((confirm) => {
            if (confirm) {
                $.when(ajax_setInfo('setDBItem', 'ChangeRecord', $.cookie('innerSeleted'), ip2port, document.getElementById(content).value)).done(function (rst) {
                    try {
                        rst = JSON.parse(rst);
                    } catch {
                    }
                    ServerError(rst)
                    $.each(rst, function (i, item) {
                        try {
                            if (item.code == -1) {
                                swal({
                                    title: '请求不合法',
                                    text: item.detail,
                                    icon: 'error',
                                    timer: 1000,
                                    buttons: false
                                });
                                return;
                            }

                        } catch {

                        }
                        if (item.row !== 0) {
                            swal({
                                title: '请求成功',
                                text: "修改成功，受影响的记录：" + item.row,
                                icon: 'success',
                                timer: 1000,
                                buttons: false
                            });
                            dataManager_item_oper(
                                $.cookie('innerSeleted'),
                                1,
                                getDBMSelected(),
                                $.cookie('innerFinder')
                            );

                        } else {
                            swal({
                                title: '请求成功',
                                text: "修改失败，记录不存在",
                                icon: 'error',
                                timer: 1000,
                                buttons: false
                            });
                        }
                    })
                })
            } else {
                swal({
                    title: '取消操作',
                    text: '用户取消操作',
                    timer: 200,
                    buttons: false,
                });
            }
        });
    }

}

function dataManager_addOper(swit, types, ip2port, address, text, time) {
    text = String(text).replaceAll("<", "[&lt;]")
    text = String(text).replaceAll(">", "[&gt;]")
    text = String(text).replaceAll("\"", "[&quot;]")
    let documentInner = "<div class=\"d-flex\">\n" +
        "                                <div class=\"avatar avatar-" + swit + "\">" +
        "                                    <span class=\"avatar-title rounded-circle border border-white bg-info GEData-type\">" + types + "</span>" +
        "                                </div>\n" +
        "                                <div class=\"flex-1 ml-3 pt-1 \">\n" +
        "                                    <h5 class=\"text-uppercase fw-bold mb-3 fas fa-globe GEData-Address\">\n" + ip2port +
        "                                        <span class=\"text-info pl-3\">" + address + "</span>\n" +
        "                                    </h5>\n" +
        "                                        <textarea class=\"form-control GEData-datas \" id='dataItem[" + ip2port + "]' rows=\"8\" " +
        "                                                  value=" + "text" + ">" + text + " </textarea>\n" +
        "                               <button class=\"btn btn-warning \" value='" + ip2port + "' style=\"float:right;margin-left:10px\" onclick=\"dataManager_db_oper(this.value,'d','')\" '>删除此项</button>" +
        "                               <button class=\"btn btn-info \" value='" + ip2port + "' style=\"float:right;margin-left:10px\" onclick=\"dataManager_db_oper(this.value,'c','dataItem[" + ip2port + "]')\"'>保存修改</button>" +
        "                                </div>\n" +
        "                                <div class=\"float-right pt-1 icon-eye \">\n" +
        "                                    <span class=\"text-muted GEData-insertDate\">" + time + "</span>\n" +
        "                                </div>\n" +
        "                            </div>" +
        "<div class=\"separator-dashed\"></div>"
    return documentInner;
}

function Page_Inner_Deal(len) {
    let ilen = 0;
    switch (len) {
        case 0:
            ilen = 5;
            break;
        case 1:
            ilen = 10;
            break;
        case 2:
            ilen = 15;
            break;
        case 3 :
            ilen = 20;
            break;
        case 4 :
            ilen = 50;
            break;
    }
    return ilen;
}

function dataManager_item_oper(entry, start, len, finder = '') {
    if (start === 1) {
        $.cookie('pg', 1);
        setDataManagerPageNav(1, 2, 3, 1)
    }
    // if (finder == "") {
    //     $.cookie('pg', 1);
    //     setDataManagerPageNav(1, 2, 3, 1)
    // }
    let swal_switch = true;
    let ilen = Page_Inner_Deal(len);
    if (swal_switch) {
        swal({
                title: "请稍等",
                text: '正在等待服务器响应...',
                icon: "info",
                button: false,
                closeOnClickOutside: false,
                closeOnEsc: false,
            }
        );
    }
    $.cookie('innerSeleted', entry);
    $.cookie('innerFinder', finder);
    document.getElementById('scanner-title').innerHTML = String(entry).toUpperCase() + "列表";
    $.when(ajax_getInfo("getDBRecord", entry, start, len, finder)).done(function (rst) {
        ServerError(rst)
        rst = JSON.parse(rst);
        let date = new Date();
        rst = rst["ojbk"];
        document.getElementById("DM-context").innerHTML = "";
        // let swit = "";
        if (swal_switch) {
            swal({
                    title: "请稍等",
                    text: '正在渲染...',
                    icon: "info",
                    button: false,
                    closeOnClickOutside: false,
                    closeOnEsc: false,
                }
            );
        }
        var lpg = Math.ceil(parseFloat(rst.count + ".0") / parseFloat(ilen))
        document.getElementById("dbManagerPageInfo").innerHTML = "共录入数据" + String(rst.count) + "数据，共" + lpg + "页"

        $.cookie('lpg', lpg);
        let queryPageCount = parseInt(rst.Tcount) - 1;
        if (queryPageCount === -1) {
            swal({
                    title: "档案不存在",
                    text: '遍历完成数据库，但是尚未找到相关项。',
                    icon: "error",
                    button: true,
                    closeOnClickOutside: false,
                    closeOnEsc: false,
                }
            );
            $.removeCookie('innerFinder');
            document.getElementById("DBM-search").value = "";
        }
        let documentInner = "";
        for (let i = 0; i <= queryPageCount; i++) {
            let dtdt = date - new Date((rst[i].intime));
            swit = (dtdt < 604800000) ? "online" : "offline";
            if (entry === "http") {
                rst[i].head = JSON.stringify(rst[i].head, null, "\t")
                documentInner += dataManager_addOper(swit, entry.charAt(0).toUpperCase(), rst[i].ip + ":" + rst[i].port, rst[i].addr, rst[i].title + "\r\n" + rst[i].head + "\r\n" + rst[i].text, rst[i].intime);
            } else {
                documentInner += dataManager_addOper(swit, entry.charAt(0).toUpperCase(), rst[i].ip + ":" + rst[i].port, rst[i].addr, rst[i].text + "\r\n", rst[i].intime);
            }

        }
        $("#DM-context").append(documentInner)
        if (swal_switch) {
            swal({
                    title: "完成",
                    text: '渲染成功',
                    icon: "info",
                    button: false,
                    timer: 800,
                }
            );
        }
    });

}

function dataManager_getSwitchChecked() {
    let box = document.getElementsByClassName("selectgroup-input");
    for (let i = 0; i < box.length; i++) {
        if (box[i].checked) {
            return String(box[i].value);
        }
    }
}

function setDataManagerPageNav(a, b, c, d) {
    $("#dbManagerToP1 a").replaceWith('<a class="page-link" href="#">' + a + '</a>');
    $("#dbManagerNow a").replaceWith('<a class="page-link" href="#">' + b + '</a>');
    $("#dbManagerToN1 a").replaceWith('<a class="page-link" href="#">' + c + '</a>');
    $("#dbManagerToP1").attr("class", "page-item")
    $("#dbManagerNow").attr("class", "page-item")
    $("#dbManagerToN1").attr("class", "page-item")

    switch (d) {
        case 1:
            $("#dbManagerToP1").attr("class", "page-item active");
            break;
        case 2:
            $("#dbManagerNow").attr("class", "page-item active");
            break;
        case 3:
            $("#dbManagerToN1").attr("class", "page-item active");
            break;
        default:
            swal({
                    title: "非法操作",
                    text: '非法操作...',
                    icon: "error",
                    button: false,
                    closeOnClickOutside: false,
                    closeOnEsc: false,
                }
            );
    }


}

function dataManager_PageOper(func) {
    // reset \last \up \down \now
    let pg = $.cookie('pg')
    switch (func) {
        case "reset":
            if ($.cookie('pg') === '1') {
                return;
            }
            setDataManagerPageNav(1, 2, 3, 1);
            $.cookie('pg', 1)
            dataManager_item_oper($.cookie('innerSeleted'), 1, getDBMSelected(), $.cookie('innerFinder'));
            break;
        case "up":
            if (pg === '1') {
                return;
            } else if (pg === '2') {
                dataManager_PageOper("reset")
                setDataManagerPageNav(1, 2, 3, 1);
            } else if (pg === $.cookie('lpg')) {
                $.cookie('pg', (parseInt($.cookie('lpg')) - 2));
                setDataManagerPageNav((parseInt($.cookie('lpg')) - 3), (parseInt($.cookie('lpg')) - 2), (parseInt($.cookie('lpg')) - 1), 2);
                dataManager_item_oper(
                    $.cookie('innerSeleted'),
                    parseInt(Page_Inner_Deal(getDBMSelected())) * (parseInt($.cookie('pg')) - 2),
                    getDBMSelected(),
                    $.cookie('innerFinder'));
            } else {
                $.cookie('pg', (parseInt($.cookie('pg')) - 1));
                setDataManagerPageNav((parseInt($.cookie('pg')) - 1), (parseInt($.cookie('pg'))), (parseInt($.cookie('pg')) + 1), 2);
                dataManager_item_oper(
                    $.cookie('innerSeleted'),
                    parseInt(Page_Inner_Deal(getDBMSelected())) * (parseInt($.cookie('pg')) - 1),
                    getDBMSelected(),
                    $.cookie('innerFinder'));
            }
            break;
        case "now":
            if (pg === '1') {
                $.cookie('pg', 2)
                setDataManagerPageNav(1, 2, 3, 2);

                dataManager_item_oper(
                    $.cookie('innerSeleted'),
                    parseInt(Page_Inner_Deal(getDBMSelected())),
                    getDBMSelected(),
                    $.cookie('innerFinder'));
            } else if (pg === $.cookie('lpg')) {
                $.cookie('pg', parseInt($.cookie('lpg')) - 1)
                setDataManagerPageNav(parseInt($.cookie('lpg')) - 2, $.cookie('pg'), $.cookie('lpg'), 2);
                dataManager_item_oper(
                    $.cookie('innerSeleted'),
                    parseInt(Page_Inner_Deal(getDBMSelected())) * (parseInt($.cookie('pg') - 1)),
                    getDBMSelected(),
                    $.cookie('innerFinder'));
            } else {
                return;
            }
            break;
        case "down":
            if (pg === '1') {
                $.cookie("pg", 3);
                setDataManagerPageNav(2, 3, 4, 2);
                dataManager_item_oper(
                    $.cookie('innerSeleted'),
                    parseInt(Page_Inner_Deal(getDBMSelected())) * 2,
                    getDBMSelected(),
                    $.cookie('innerFinder'));
            } else if (pg == $.cookie('lpg')) {
                return;
            } else if (pg == (parseInt($.cookie('lpg')) - 1)) {
                dataManager_PageOper("last");
            } else {
                $.cookie('pg', (parseInt($.cookie('pg')) + 1));
                setDataManagerPageNav((parseInt($.cookie('pg')) - 1), (parseInt($.cookie('pg'))), (parseInt($.cookie('pg')) + 1), 2);
                dataManager_item_oper(
                    $.cookie('innerSeleted'),
                    parseInt(Page_Inner_Deal(getDBMSelected())) * (parseInt($.cookie('pg')) - 1),
                    getDBMSelected(),
                    $.cookie('innerFinder'));
            }
            break;
        case"last":
            if (pg == $.cookie('lpg')) {
                return;
            }
            $.cookie("pg", $.cookie("lpg"));
            setDataManagerPageNav((parseInt($.cookie('lpg')) - 2), (parseInt($.cookie('lpg')) - 1), (parseInt($.cookie('lpg'))), 3);
            dataManager_item_oper(
                $.cookie('innerSeleted'),
                parseInt(Page_Inner_Deal(getDBMSelected())) * (parseInt($.cookie('pg')) - 1),
                getDBMSelected(),
                $.cookie('innerFinder'));
    }

}

function IPDB_addOper(ips, ipe, sipi, eipi, addr) {

    let documentInner = "                    <tr>\n" +
        "                                <td>" + ips + "</td>\n" +
        "                                <td>" + ipe + "</td>\n" +
        "                                <td>" + sipi + "</td>\n" +
        "                                <td>" + eipi + "</td>\n" +
        "                                <td>" + addr + "</td>\n" +
        "                            </tr>"
    return documentInner;
}

function IPD_item_oper(len, page, finder = '') {
    if (page === 0) {
        $.cookie('pg', 1);
    }
    if (page === 1) {
        page = 0
        setDataManagerPageNav(1, 2, 3, 1)
    }
    let swal_switch = true;
    let ilen = Page_Inner_Deal(len);
    $.cookie('innerFinder', finder);
    $.when(ajax_getInfo("getIPDBRecord", page, len, finder)).done(function (rst) {
        ServerError(rst)
        rst = rst["ojbk"];
        document.getElementById("IPD-context").innerHTML = "";
        if (swal_switch) {
            swal({
                    title: "请稍等",
                    text: '正在渲染...',
                    icon: "info",
                    button: false,
                    closeOnClickOutside: false,
                    closeOnEsc: false,
                }
            );
        }
        var lpg = Math.ceil(parseFloat(rst.total + ".0") / parseFloat(ilen))
        document.getElementById("ipdbManagerPageInfo").innerHTML = "共录入数据" + String(rst.total) + "数据，共" + lpg + "页"
        if (parseInt($("#IPD-total").html()) < 10000 || $("#IPD-total").html() == "------") {
            $("#IPD-total").html(rst.total)
        }
        $.cookie('lpg', lpg);
        let queryPageCount = parseInt(rst.row) - 1;
        if (queryPageCount === -1) {
            swal({
                    title: "档案不存在",
                    text: '遍历完成数据库，但是尚未找到相关项。',
                    icon: "error",
                    button: true,
                    closeOnClickOutside: false,
                    closeOnEsc: false,
                }
            );
            $.removeCookie('innerFinder');
            document.getElementById("DBM-search").value = "";
        }
        let documentInner = "";
        for (let i = 0; i <= queryPageCount; i++) {
            documentInner += IPDB_addOper(rst[i].startip, rst[i].endip, rst[i].startip_iton, rst[i].endip_iton, rst[i].address)

        }
        $("#IPD-context").append(documentInner)
        if (swal_switch) {
            swal({
                    title: "完成",
                    text: '渲染成功',
                    icon: "info",
                    button: false,
                    timer: 800,
                }
            );
        }
    });

}

function IPDManager_PageOper(func) {
    // reset \last \up \down \now
    let pg = $.cookie('pg')
    if ($("lpg") == 1) {
        return;
    }
    switch (func) {
        case "reset":
            if ($.cookie('pg') === '1') {
                return;
            }
            setDataManagerPageNav(1, 2, 3, 1);
            $.cookie('pg', 1)
            IPD_item_oper(getIPDSelected(), 1, $.cookie('innerFinder'));
            break;
        case "up":
            if (pg === '1') {
                return;
            } else if (pg === '2') {
                IPDManager_PageOper("reset")
                setDataManagerPageNav(1, 2, 3, 1);
            } else if (pg === $.cookie('lpg')) {
                $.cookie('pg', (parseInt($.cookie('lpg')) - 2));
                setDataManagerPageNav((parseInt($.cookie('lpg')) - 3), (parseInt($.cookie('lpg')) - 2), (parseInt($.cookie('lpg')) - 1), 2);
                IPD_item_oper(
                    getIPDSelected(),
                    parseInt(Page_Inner_Deal(getIPDSelected())) * (parseInt($.cookie('pg')) - 2),
                    $.cookie('innerFinder'));
            } else {
                $.cookie('pg', (parseInt($.cookie('pg')) - 1));
                setDataManagerPageNav((parseInt($.cookie('pg')) - 1), (parseInt($.cookie('pg'))), (parseInt($.cookie('pg')) + 1), 2);
                IPD_item_oper(
                    getIPDSelected(),
                    parseInt(Page_Inner_Deal(getIPDSelected())) * (parseInt($.cookie('pg')) - 1),
                    $.cookie('innerFinder'));
            }
            break;
        case "now":
            if (pg === '1') {
                $.cookie('pg', 2)
                setDataManagerPageNav(1, 2, 3, 2);

                IPD_item_oper(
                    getIPDSelected(),
                    parseInt(Page_Inner_Deal(getIPDSelected())),
                    $.cookie('innerFinder'));
            } else if (pg === $.cookie('lpg')) {
                $.cookie('pg', parseInt($.cookie('lpg')) - 1)
                setDataManagerPageNav(parseInt($.cookie('lpg')) - 2, $.cookie('pg'), $.cookie('lpg'), 2);
                IPD_item_oper(
                    getIPDSelected(),
                    parseInt(Page_Inner_Deal(getIPDSelected())) * (parseInt($.cookie('pg') - 1)),
                    $.cookie('innerFinder'));
            } else {
                return;
            }
            break;
        case "down":
            if (pg === '1') {
                $.cookie("pg", 3);
                setDataManagerPageNav(2, 3, 4, 2);
                IPD_item_oper(
                    getIPDSelected(),
                    parseInt(Page_Inner_Deal(getIPDSelected())) * 2,
                    $.cookie('innerFinder'));
            } else if (pg == $.cookie('lpg')) {
                return;
            } else if (pg == (parseInt($.cookie('lpg')) - 1)) {
                IPDManager_PageOper("last");
            } else {
                $.cookie('pg', (parseInt($.cookie('pg')) + 1));
                setDataManagerPageNav((parseInt($.cookie('pg')) - 1), (parseInt($.cookie('pg'))), (parseInt($.cookie('pg')) + 1), 2);
                IPD_item_oper(
                    getIPDSelected(),
                    parseInt(Page_Inner_Deal(getIPDSelected())) * (parseInt($.cookie('pg')) - 1),
                    $.cookie('innerFinder'));
            }
            break;
        case"last":
            if (pg == $.cookie('lpg')) {
                return;
            }
            $.cookie("pg", $.cookie("lpg"));
            setDataManagerPageNav((parseInt($.cookie('lpg')) - 2), (parseInt($.cookie('lpg')) - 1), (parseInt($.cookie('lpg'))), 3);
            IPD_item_oper(
                getIPDSelected(),
                parseInt(Page_Inner_Deal(getIPDSelected())) * (parseInt($.cookie('pg')) - 1),
                $.cookie('innerFinder'));
    }
}

function IPDManager_dashBoard() {
    $.when(ajax_getInfo("getIPDBdashboard")).done(function (rst) {
        ServerError(rst)
        rst = rst["ojbk"];
        $("#IPD-source").html(rst.source);
        $("#IPD-current").html(rst.current);
    });
}

function getSystemStatus() {
    $.when(ajax_getInfo("getSystemStatus")).done(function (rst) {
        swal({
            title: "进行中，期间请勿操作",
            text: rst,
            icon: "info",
            button: false,
            closeOnClickOutside: false,
            closeOnEsc: false
        });
    });
}

function IPDManager_checkLasted(fc) {
    var handle;
    $.when(ajax_getInfo("checkIPDBVersion")).done(function (rst) {
            ServerError(rst)
            rst = rst["ojbk"];
            if (rst.code == 0) {
                $("#IPD-lasted").html(rst.version);
                if (fc == 1) {// 手动检查
                    if (rst.details == false) {  //存在更新
                        swal({
                            title: 'IP库更新',
                            icon: "info",
                            text: "ip库存在更新，是否进行更新",
                            buttons: {
                                confirm: {
                                    text: '更新',
                                    className: 'btn btn-success'
                                },
                                cancel: {
                                    text: '取消',
                                    visible: true,
                                    className: 'btn btn-danger'
                                }
                            }
                        }).then((confirm) => {
                            if (confirm) {
                                swal({
                                    title: "请知晓",
                                    text: "数据库更新时将停止GodEyes爬取和服务，更新完成后将会重新打开，期间请勿操作本系统。",
                                    icon: "info",
                                    buttons: {
                                        confirm: {
                                            text: '了解',
                                            className: 'btn btn-success'
                                        },
                                        cancel: {
                                            text: '取消',
                                            visible: true,
                                            className: 'btn btn-danger'
                                        }
                                    },
                                    closeOnClickOutside: false,
                                    closeOnEsc: false
                                }).then((confirm) => {
                                    if (confirm == true) {
                                        $.when(ajax_getInfo("updateIPDBVersion")).done(function (rst2) {
                                            if (String(rst2).indexOf("GodEyes服务器错误") !== -1) {
                                                swal({
                                                    title: "IP库更新失败",
                                                    text: "连接中断！",
                                                    icon: "error",
                                                    button: true,
                                                    closeOnClickOutside: false,
                                                    closeOnEsc: false
                                                });
                                                clearInterval(handle)
                                                return;
                                            }
                                            rst2 = rst2["ojbk"];
                                            clearInterval(handle)
                                            if (rst2.code == 0) {
                                                swal({
                                                    title: "IP库更新完毕",
                                                    text: rst.details,
                                                    icon: "info",
                                                    button: true,
                                                    closeOnClickOutside: false,
                                                    closeOnEsc: false
                                                });
                                                clearInterval(handle)
                                            } else {
                                                swal({
                                                    title: "IP库更新失败",
                                                    text: rst2.details,
                                                    icon: "error",
                                                    button: true,
                                                    closeOnClickOutside: false,
                                                    closeOnEsc: false
                                                });
                                                clearInterval(handle)
                                            }

                                        });

                                        handle = setInterval('getSystemStatus()', 1000);
                                    }
                                })
                            } else {
                                swal({
                                    title: '取消操作',
                                    text: '用户取消操作',
                                    timer: 200,
                                    buttons: false,
                                });
                            }

                        })
                    } else {
                        swal({
                            title: '最新版',
                            text: '此版本为最新版, 无需更新',
                            timer: 5000,
                            buttons: {
                                ok: '好的'
                            },
                        });
                    }
                }


            }
            if (rst.code == -1) {
                swal({
                    title: "GodEyes服务器错误",
                    text: rst.details,
                    icon: "error",
                    button: true,
                    closeOnClickOutside: false,
                    closeOnEsc: false
                });
            }
        }
    );
}

function getFingerPrint() {
    swal({
            title: "请稍等",
            text: "由于指纹数据量过大,加载可能稍慢,请耐心等待",
            icon: "info",
            button: false,
            closeOnClickOutside: false,
            closeOnEsc: false,
        }
    );
    $.when(ajax_getInfo("getFingerPrint", "cache")).done(function (rst) {
        try {
            if (rst["ojbk"]["code"] == -1) {
                swal({
                        title: "错误",
                        text: rst["ojbk"]["result"],
                        icon: "error",
                        button: true,
                        closeOnClickOutside: false,
                        closeOnEsc: false,
                    }
                );
                return;
            }
        } catch {
        }
        try {
            if (rst["1"]["fingerprint"] != null) {

            }
        } catch {
            swal({
                    title: "错误",
                    text: '内容解析错误，可能文件损坏或数据为空',
                    icon: "error",
                    button: true,
                    closeOnClickOutside: false,
                    closeOnEsc: false,
                }
            );
            return;
        }
        if (rst.length < 5) {
            swal({
                    title: "错误",
                    text: "文件为空,请确定表中存在数据，并且已经重构",
                    icon: "error",
                    button: true,
                    closeOnClickOutside: false,
                    closeOnEsc: false,
                }
            );
            return;
        }
        swal({
                title: "请稍等",
                text: "由于指纹数据量过大,渲染可能稍慢,请耐心等待",
                icon: "info",
                button: false,
                closeOnClickOutside: false,
                closeOnEsc: false,
            }
        );
        new Chart(lineChart, {
            type: 'line',
            data: {
                labels: [
                    rst["1"]["fingerprint"],
                    rst["2"]["fingerprint"],
                    rst["3"]["fingerprint"],
                    rst["4"]["fingerprint"],
                    rst["5"]["fingerprint"],
                    rst["6"]["fingerprint"],
                    rst["7"]["fingerprint"],
                    rst["8"]["fingerprint"],
                    rst["9"]["fingerprint"],
                    rst["10"]["fingerprint"],
                    rst["11"]["fingerprint"],
                    rst["12"]["fingerprint"]
                ],
                datasets: [{
                    label: "累计总数",
                    borderColor: "#1d7af3",
                    pointBorderColor: "#FFF",
                    pointBackgroundColor: "#1d7af3",
                    pointBorderWidth: 2,
                    pointHoverRadius: 4,
                    pointHoverBorderWidth: 1,
                    pointRadius: 4,
                    backgroundColor: 'transparent',
                    fill: true,
                    borderWidth: 2,
                    data: [
                        rst["1"]["count"],
                        rst["2"]["count"],
                        rst["3"]["count"],
                        rst["4"]["count"],
                        rst["5"]["count"],
                        rst["6"]["count"],
                        rst["7"]["count"],
                        rst["8"]["count"],
                        rst["9"]["count"],
                        rst["10"]["count"],
                        rst["11"]["count"],
                        rst["12"]["count"]

                    ]
                },
                    {
                        label: "识别熵",
                        borderColor: "#3af6f0",
                        pointBorderColor: "#ffbfbf",
                        pointBackgroundColor: "#bf0c60",
                        pointBorderWidth: 2,
                        pointHoverRadius: 4,
                        pointHoverBorderWidth: 1,
                        pointRadius: 4,
                        backgroundColor: 'transparent',
                        fill: true,
                        borderWidth: 2,
                        data: [
                            rst["1"]["val"],
                            rst["2"]["val"],
                            rst["3"]["val"],
                            rst["4"]["val"],
                            rst["5"]["val"],
                            rst["6"]["val"],
                            rst["7"]["val"],
                            rst["8"]["val"],
                            rst["9"]["val"],
                            rst["10"]["val"],
                            rst["11"]["val"],
                            rst["12"]["val"]]
                    }]
            },
            options: {
                responsive: true,
                scaleShowValues: true,
                scales: {
                    xAxes: [{
                        ticks: {
                            autoSkip: false
                        }
                    }]
                },
                maintainAspectRatio: false,
                legend: {
                    position: 'top',
                    labels: {
                        padding: 5,
                        fontColor: '#1d7af3',
                    }
                },
                tooltips: {
                    bodySpacing: 4,
                    mode: "nearest",
                    intersect: 1,
                    position: "nearest",
                    xPadding: 10,
                    yPadding: 10,
                    caretPadding: 10
                },
                layout: {
                    padding: {left: 15, right: 15, top: 15, bottom: 15}
                }
            }
        });

        setTimeout(function () {
            var data = []
            $.each(rst, function (i, item) {
                data.push([rst[i]["fingerprint"], rst[i]["val"], rst[i]["count"]])
            })
            $('#basic-datatables').DataTable({data});
            $('#multi-filter-select').DataTable({
                "pageLength": 5,
                initComplete: function () {
                    this.api().columns().every(function () {
                        var column = this;
                        var select = $('<select class="form-control"><option value=""></option></select>')
                            .appendTo($(column.footer()).empty())
                            .on('change', function () {
                                var val = $.fn.dataTable.util.escapeRegex(
                                    $(this).val()
                                );

                                column
                                    .search(val ? '^' + val + '$' : '', true, false)
                                    .draw();
                            });

                        column.data().unique().sort().each(function (d, j) {
                            select.append('<option value="' + d + '">' + d + '</option>')
                        });
                    });
                }
            });
            swal({
                    title: "完成",
                    text: '渲染成功',
                    icon: "info",
                    button: false,
                    timer: 800,
                }
            );
        }, 1000)

    })
}

function hiddenFPBLS() {
    $("#blackList").modal('hide');
}

function setBlackListDialog() {
    $("#blackList").modal();
    $.when(ajax_getInfo("getFingerprintBlackList")).done(function (rst) {
        ServerError(rst)
        $("#fingerPrintBlackListText").text(rst)
    })
}

function saveFPBLS() {
    var rst = ajax_setInfo("setFingerprintBlackList", $("#fingerPrintBlackListText").val())
    ServerError(rst)
    if (rst["ojbk"]["code"] == 0) {
        hiddenFPBLS()
        swal({
            title: "成功",
            text: "指纹黑名单设置成功",
            icon: "success",
            button: true,
            closeOnClickOutside: true,
            closeOnEsc: true,
            timer: 500,
        });
    }
}

function rebuildFingerPrint() {
    swal({
        title: '请求确认',
        icon: "warning",
        text: "重建指纹是一个耗时操作，期间可能影响服务器性能，确定要重建吗？处理过程中此页面将会报错(格式错误),当重建完成后,方可正常访问此页面.",
        buttons: {
            confirm: {
                text: '了解',
                className: 'btn btn-success'
            },
            cancel: {
                text: '取消',
                visible: true,
                className: 'btn btn-danger'
            }
        }
    }).then((confirm) => {
        if (confirm) {
            var text = ajax_setInfo('rebuildFingerPrint')
            ServerError(text)
            $.each(text, function (i, item) {
                if (item.code === 0) {
                    swal({
                        title: '请求成功',
                        text: item.detail,
                        icon: 'success',
                        timer: 5000,
                        buttons: false
                    });
                } else {
                    swal({
                        title: '请求成功',
                        text: item.detail,
                        icon: 'error',
                        timer: 1000,
                        buttons: false
                    });
                }
            })

        } else {
            swal({
                title: '取消操作',
                text: '用户取消操作',
                timer: 200,
                buttons: false,
            });
        }
    });
}

function editUser(user, password, power) {
    $("#mod-title").text("修改用户信息")
    $("#modifyUser").modal();
    $("#mod-username").val(user).attr('readonly', 'true')
    $("#mod-password").val(password)
    $("#mod-repassword").val(password)
    if (power === "SuperAdmin") {
        $("#mod-super").prop("selected", "true")
    } else {
        $("#mod-vistor").prop("selected", "true")
    }
}

function addUser() {
    $("#mod-username").removeAttr("readonly").val("");
    $("#mod-title").text("添加用户信息")
    $("#modifyUser").modal();
    $("#mod-password").val("")
    $("#mod-repassword").val("")
}

function saveUser() {
    var user = $("#mod-username").val();
    var password = $("#mod-password").val();
    var repassword = $("#mod-repassword").val();
    var power_Super = $("#mod-super").prop("selected");
    if (password !== repassword) {
        swal({
            title: '错误',
            text: '两次密码不匹配',
            icon: "error",
            timer: 1000,
            buttons: false,
        });
        return;
    }
    if (password.length < 6) {
        swal({
            title: '错误',
            text: '两次密码长度不符合要求',
            icon: "error",
            timer: 1000,
            buttons: false,
        });
        return;
    }
    if ($("#mod-title").text() == "添加用户信息") {
        $.when(ajax_setInfo("addUserInfo", user, password, power_Super)).done(function (rst) {
            ServerError(rst)
            try {
                rst = $.parseJSON(rst)
                if (rst["ojbk"]["code"] == -1) {
                    swal({
                        title: '错误',
                        text: '用户没有此权限',
                        icon: "error",
                        timer: 3000,
                        buttons: false,
                    });
                    return;
                }
            } catch {

            }
            $("#modifyUser").modal('hide');
            swal({
                title: '添加成功',
                text: '用户信息添加成功',
                icon: "success",
                timer: 3000,
                buttons: false,
            });
            getUserList()
        })
        return;
    }
    $.when(ajax_setInfo("setUserInfo", user, password, power_Super)).done(function (rst) {
        ServerError(rst)
        try {
            rst = $.parseJSON(rst)
            if (rst["ojbk"]["code"] == -1) {
                swal({
                    title: '错误',
                    text: '用户没有此权限',
                    icon: "error",
                    timer: 3000,
                    buttons: false,
                });
                return;
            }
        } catch {

        }
        $("#modifyUser").modal('hide');
        swal({
            title: '修改成功',
            text: '用户信息修改成功',
            icon: "success",
            timer: 3000,
            buttons: false,
        });
        getUserList()
    })


}

function hiddenEditUser() {
    $("#modifyUser").modal('hide');
}

function deleteUser(user, password, power) {
    swal({
        title: '请求确认',
        icon: "warning",
        text: "确定要删除[" + user + "]这个账户吗?",
        buttons: {
            confirm: {
                text: '确定!',
                className: 'btn btn-success'
            },
            cancel: {
                text: '取消',
                visible: true,
                className: 'btn btn-danger'
            }
        }
    }).then((confirm) => {
        if (confirm) {
            var text = ajax_setInfo('deleteUser', user, password, power);
            ServerError(text)
            $.each(text, function (i, item) {
                if (item.code === 0) {
                    swal({
                        title: '请求成功',
                        text: item.detail,
                        icon: 'success',
                        timer: 5000,
                        buttons: false
                    });
                } else {
                    swal({
                        title: '请求成功',
                        text: item.detail,
                        icon: 'error',
                        timer: 1000,
                        buttons: false
                    });
                }
                getUserList()

            })

        } else {
            swal({
                title: '取消操作',
                text: '用户取消操作',
                timer: 200,
                buttons: false,
            });
        }
    });
}

function getUserList() {
    $.when(ajax_getInfo("getUserList")).done(function (rst) {
        ServerError(rst)
        try {
            rst = $.parseJSON(rst)
            if (rst["ojbk"]["code"] == -1) {
                swal({
                    title: '错误',
                    text: '用户没有此权限',
                    icon: "error",
                    timer: 3000,
                    buttons: false,
                });
                return;
            }
        } catch {

        }
        ServerError(rst)
        var data = []
        $.each(rst, function (i, item) {
            var oper = "<div class=\"form-button-action\">" +
                "<button type=\"button\" data-toggle=\"tooltip\" title=\"\" class=\"btn btn-link btn-primary btn-lg\" data-original-title=\"Edit Task\">" +
                "<i class=\"fa fa-edit\" onclick=\"editUser(" +
                "\'" + rst[i]["username"] + "\',\'" + rst[i]["password"] + "\',\'" + rst[i]["power"] + "\'"
                + ")\"></i>" +
                "</button>" +
                "<button type=\"button\" data-toggle=\"tooltip\" title=\"\" class=\"btn btn-link btn-danger\" data-original-title=\"Remove\">" +
                "<i class=\"fa fa-times\"onclick=\"deleteUser(" +
                "\'" + rst[i]["username"] + "\',\'" + rst[i]["password"] + "\',\'" + rst[i]["power"] + "\'"
                + ")\"></i>" +
                "</button>" +
                "</div>"

            data.push([rst[i]["username"], rst[i]["password"], rst[i]["power"], oper])
        })
        $("#basic-datatables").dataTable().fnDestroy();
        $('#basic-datatables').DataTable({data});
        $('#multi-filter-select').DataTable({
            "pageLength": 5, destroy: true, retrieve: true,
            initComplete: function () {
                this.api().columns().every(function () {
                    var column = this;

                    var select = $('<select class="form-control"><option value=""></option></select>')
                        .appendTo($(column.footer()).empty())
                        .on('change', function () {
                            var val = $.fn.dataTable.util.escapeRegex(
                                $(this).val()
                            );
                            column
                                .search(val ? '^' + val + '$' : '', true, false)
                                .draw();
                        });
                    column.data().unique().sort().each(function (d, j) {
                        select.append('<option value="' + d + '">' + d + '</option>')
                    });
                });
            }
        });
    })
}

function getScannerLog() {
    swal({
        title: '提示',
        text: '由于日志数量原因，页面可能加载迟缓，如果日志数量较多，建议清除日志。',
        icon: "info",
        timer: 3000,
        buttons: false,
    });

    $.when(ajax_getInfo("getScannerLog")).done(function (rst) {
        ServerError(rst)
        try {
            rst = $.parseJSON(rst)
            if (rst["ojbk"]["code"] == -1) {
                swal({
                    title: '错误',
                    text: '用户没有此权限',
                    icon: "error",
                    timer: 3000,
                    buttons: false,
                });
                return;
            }
        } catch {

        }
        ServerError(rst)
        var data = []
        $.each(rst, function (i, item) {
            var level = "未知"
            switch (rst[i]["source"]) {
                case "[S]":
                    level = "成功";
                    break;
                case "[W]":
                    level = "警告";
                    break;
                case "[E]":
                    level = "错误";
                    break;
            }
            data.push([rst[i]["id"], level, rst[i]["ip"], rst[i]["port"], rst[i]["log"], rst[i]["dtime"],])
        })
        $("#basic-datatables").dataTable().fnDestroy();
        $('#basic-datatables').DataTable({data});
        $('#multi-filter-select').DataTable({
            "pageLength": 5, destroy: true, retrieve: true,
            initComplete: function () {
                this.api().columns().every(function () {
                    var column = this;

                    var select = $('<select class="form-control"><option value=""></option></select>')
                        .appendTo($(column.footer()).empty())
                        .on('change', function () {
                            var val = $.fn.dataTable.util.escapeRegex(
                                $(this).val()
                            );
                            column
                                .search(val ? '^' + val + '$' : '', true, false)
                                .draw();
                        });
                    column.data().unique().sort().each(function (d, j) {
                        select.append('<option value="' + d + '">' + d + '</option>')
                    });
                });
            }
        });
    })
}

function getSystemLog() {
    swal({
        title: '提示',
        text: '由于日志数量原因，页面可能加载迟缓，如果日志数量较多，建议清除日志。',
        icon: "info",
        timer: 3000,
        buttons: false,
    });
    $.when(ajax_getInfo("getSystemLog")).done(function (rst) {
        ServerError(rst)
        try {
            rst = $.parseJSON(rst)
            if (rst["ojbk"]["code"] == -1) {
                swal({
                    title: '错误',
                    text: '用户没有此权限',
                    icon: "error",
                    timer: 3000,
                    buttons: false,
                });
                return;
            }
        } catch {

        }
        ServerError(rst)
        var data = []
        $.each(rst, function (i, item) {
            data.push([rst[i]["id"], rst[i]["module"], rst[i]["detail"], rst[i]["user"], rst[i]["ip"], rst[i]["dtime"]])
        })
        $("#basic-datatables").dataTable().fnDestroy();
        $('#basic-datatables').DataTable({data});
        $('#multi-filter-select').DataTable({
            "pageLength": 5,
            destroy: true,
            retrieve: true,
            initComplete: function () {
                this.api().columns().every(function () {
                    var column = this;

                    var select = $('<select class="form-control"><option value=""></option></select>')
                        .appendTo($(column.footer()).empty())
                        .on('change', function () {
                            var val = $.fn.dataTable.util.escapeRegex(
                                $(this).val()
                            );
                            column
                                .search(val ? '^' + val + '$' : '', true, false)
                                .draw();
                        });
                    column.data().unique().sort().each(function (d, j) {
                        select.append('<option value="' + d + '">' + d + '</option>')
                    });
                });
            }
        });
    })
}

function systemConfigure(func, content) {
    if (func == 'r') {
        $.when(ajax_getInfo("getFile", 'systemConfigure')).done(function (rst) {
            ServerError(rst)
            output(rst)
            if (arg !== null && arg !== 'firstRun') {
                swal("操作成功", "重载加载操作执行成功", {
                    icon: "success",
                    buttons: {
                        confirm: {
                            className: 'btn btn-success'
                        }
                    },
                });
            }
        })
    } else if (func == "w") {
        let json_data = ajax_setInfo("setFile", 'systemConfigure', content)

        if (json_data["ojbk"]["code"] == 0)
            swal({
                title: '成功',
                text: json_data["ojbk"]["details"],
                icon: "success",
                timer: 1000,
                buttons: false,
            });
        else
            swal({
                title: '失败',
                text: json_data["ojbk"]["details"],
                timer: 1000,
                icon: "error",
                buttons: false,
            });
    }

}

function stopAllThreads() {
    $.when(ajax_getInfo("getThreadDelay")).done(function (rst) {
        ServerError(rst)
        rst = $.parseJSON(rst)
        var t = rst["ojbk"]["detail"]
        swal({
            title: '等待响应',
            text: "由服务器端配置等待时间" + t + "秒,期间可能无法操作.",
            icon: "info",
            buttons: false
        });
        setTimeout(function () {
            var json_data = ajax_setInfo("stopAllThreads");
            json_data = JSON.parse(json_data);
            if (json_data["ojbk"]["code"] === 0)
                swal({
                    title: '成功',
                    text: json_data["ojbk"]["detail"],
                    icon: "success",
                    timer: 1000,
                    buttons: false,
                });
            else
                swal({
                    title: '失败',
                    text: json_data["ojbk"]["detail"],
                    timer: 1000,
                    icon: "error",
                    buttons: false,
                });
        }, 100)
    })


}

function startScanner(method, addr) {

    var json_data = ajax_setInfo("startScanner", method, addr, $("#coprocessor").prop("checked"));
    if (json_data["ojbk"]["code"] === 0) {
        swal({
            title: '成功',
            text: json_data["ojbk"]["detail"],
            icon: "success",
            timer: 3000,
            buttons: false,
        });
    }


}