import json
import socket
import threading
import time
import traceback
import netaddr
import pymysql
import modules.GSystem as GEsys
import datetime
import re
import demjson
import os

DBSQL = """DROP TABLE IF EXISTS `godeyes_http`;
CREATE TABLE `godeyes_http`  (
  `ip` varchar(15) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `port` varchar(6) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `title` varchar(256) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `head` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `text` longtext CHARACTER SET utf8 COLLATE utf8_bin NULL,
  `address` varchar(128) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `intime` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`ip`, `port`) USING BTREE,
  INDEX `ip`(`ip`) USING BTREE,
  INDEX `addr`(`address`) USING BTREE,
  INDEX `intime`(`intime`) USING BTREE,
  INDEX `title`(`title`) USING BTREE,
  FULLTEXT INDEX `text`(`text`),
  FULLTEXT INDEX `head`(`head`)
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;
DROP TABLE IF EXISTS `godeyes_ipdb`;
CREATE TABLE `godeyes_ipdb`  (
  `startip` varchar(15) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `endip` varchar(15) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `startip_iton` varchar(11) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `endip_iton` varchar(11) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `address` varchar(256) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  INDEX `s`(`startip`) USING BTREE,
  INDEX `e`(`endip`) USING BTREE,
  INDEX `l`(`address`) USING BTREE,
  INDEX `si`(`startip_iton`) USING BTREE,
  INDEX `ei`(`endip_iton`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;
DROP TABLE IF EXISTS `godeyes_log`;
CREATE TABLE `godeyes_log`  (
  `scanner` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `source` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `ip` varchar(15) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `port` varchar(6) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `log` varchar(768) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `dtime` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`source`, `ip`, `port`, `log`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;
DROP TABLE IF EXISTS `godeyes_mysql`;
CREATE TABLE `godeyes_mysql`  (
  `ip` varchar(15) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `port` varchar(6) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `text` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `address` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `intime` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`ip`, `port`) USING BTREE,
  INDEX `ip`(`ip`) USING BTREE,
  INDEX `port`(`port`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;
DROP TABLE IF EXISTS `godeyes_slog`;
CREATE TABLE `godeyes_slog`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `module` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `detail` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `user` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `ip` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `dtime` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;
DROP TABLE IF EXISTS `godeyes_ssh`;
CREATE TABLE `godeyes_ssh`  (
  `ip` varchar(15) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `port` varchar(6) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `text` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `address` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `intime` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`ip`, `port`) USING BTREE,
  INDEX `ip`(`ip`) USING BTREE,
  INDEX `port`(`port`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;
DROP TABLE IF EXISTS `godeyes_telnet`;
CREATE TABLE `godeyes_telnet`  (
  `ip` varchar(15) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `port` varchar(6) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `text` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `address` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `intime` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`ip`, `port`) USING BTREE,
  INDEX `ip`(`ip`) USING BTREE,
  FULLTEXT INDEX `text`(`text`)
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;
DROP TABLE IF EXISTS `godeyes_users`;
CREATE TABLE `godeyes_users`  (
  `username` varchar(64)  CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL unique,
  `password` varchar(128) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `power` varchar(16) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`username`)
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;"""
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)


class fingerprint:
    def __init__(self):
        self.result = {}
        self.rawHeader = getHeader()
        self.headerItems = self.rawHeader.split("\n")
        self.threadStatus = 0
        self.count = len(self.headerItems)
        self.process = 0
        self.blacklist = set({})
        with open(BASE_DIR + "\\FingerPrint\\custom\\webFingerPrint\\blackList.txt", mode='r') as foper:
            for i in foper.readlines():
                self.blacklist.add(i.strip().lower())

    def innerJudge(self, str):
        fh = "_=!/-#$%^&*()+*\\~`<>,?' :;][{}"
        if str.isdigit():
            return 0
        if str.isupper():
            return 2
        if str.islower():
            return 1
        if str in fh:
            return 3
        else:
            return 4

    def calc(self, text):
        text = text.strip().replace(" ", "")
        blacklist = self.blacklist
        if text.find("\"") == 0:  # 大数据分析第一个为 " 的为垃圾项
            return 99999
        if text.find("W/") == 0:  # 大数据
            return 99999
        lens = len(text)
        if len == 0:
            return 999999
        if lens > 3 and text[1:lens - 1].isnumeric():
            return 999999
        if text.lower() in blacklist:
            return 999999
        if text.isdigit() or text.isnumeric():
            return 999999

        rst = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        v = 0
        idx = 0
        for i in range(0, lens - 5):
            a = self.innerJudge(str(text)[i])
            b = self.innerJudge(str(text)[i + 1])
            c = self.innerJudge(str(text)[i + 2])
            d = self.innerJudge(str(text)[i + 3])
            e = self.innerJudge(str(text)[i + 4])
            t = [a, b, c, d, e]

            for j in range(5):
                for k in range(j):
                    if idx == 9:
                        idx = 0
                    rst[idx] += (abs(int(t[j]) - int(t[k])))
                    if t[k] == 4:
                        idx += 1
                        rst[idx] += 1
            for k in range(10):
                v = v + rst[k]
                v /= 2
                if rst[k] == 0:
                    break
        entropy = (v / (lens + 1)) * 100
        if entropy is None:
            entropy = 0

        return entropy

    def getHeaders(self):
        return self.headerItems

    def judge(self):
        for item in self.getHeaders():
            self.process = self.process + 1
            try:
                item = demjson.decode(item)
            except Exception as e:
                print(e)
                continue

            for innerItem in item.items():
                # innerItem 是里面的值，例如nginx,close,chunked,text/html
                innerItem = str(innerItem[1])
                if len(innerItem) > 50:
                    continue
                value = self.calc(innerItem)
                if value < 157:
                    try:
                        self.result[innerItem + "{hashCode}" + str(value)]
                    except Exception:
                        self.result[innerItem + "{hashCode}" + str(value)] = 0
                    self.result[innerItem + "{hashCode}" + str(value)] = self.result[
                                                                             innerItem + "{hashCode}" + str(
                                                                                 value)] + 1
                else:
                    print(innerItem, value)
        d_order = sorted(self.result.items(), key=lambda x: x[1], reverse=True)
        return d_order


def dealFetchAllFormat(content):
    content = list(content)
    rst = []
    for i in content:
        i = str(i)[2:-3]
        rst.append(i)
    return rst


def closeConnection(db, cursor):
    cursor.close()
    db.close()
    db = None


def createConnect():
    database_info = GEsys.getDBInfo()
    try:
        db = pymysql.connect(host=database_info['url'],
                             port=database_info['port'],
                             user=database_info['user'],
                             password=database_info['passwd'],
                             db=database_info['db'],
                             charset=database_info['charset'])
        return db
    except pymysql.InternalError as e:
        raise GEsys.DatabaseError("数据库不存在")
    except pymysql.err.OperationalError as e:
        traceback.print_exc()
        raise GEsys.DatabaseError("连接数据库失败")
    except pymysql.err.ProgrammingError as e:
        raise GEsys.DatabaseError("数据表不存在")
    except OSError as e:
        print("系统错误")


def getUserPower(usr):
    db = createConnect()
    cursor = db.cursor()
    sql = 'select power from godeyes_users where username =%s'
    cursor.execute(sql, usr)
    num = cursor.fetchone()[0]
    closeConnection(db, cursor)
    return num


def checkAccount(usr, pwd):
    db = createConnect()
    cursor = db.cursor()
    sql = 'select * from godeyes_users where username =%s and password = %s'  # 参数化防注入
    cursor.execute(sql, (usr, pwd))
    usrlist = cursor.fetchall()
    closeConnection(db, cursor)
    return len(usrlist)


def modAccountPwd(usr, opwd, npwd):
    db = createConnect()
    cursor = db.cursor()
    sql = 'update godeyes_users set password = %s where username =%s and password =%s'  # 参数化防注入
    try:
        cursor.execute(sql, (npwd, usr, opwd,))
        db.commit()
        return True
    except Exception as e:
        raise GEsys.DatabaseError("未知错误" + e)
    finally:
        closeConnection(db, cursor)


def getTableColumnsName(table):
    db = createConnect()
    cursor = db.cursor()
    sql = "select COLUMN_NAME from information_schema.COLUMNS where table_name = %s;  "
    cursor.execute(sql, table)
    columnsNames = cursor.fetchall()
    closeConnection(db, cursor)
    return columnsNames


def getTotal(table):
    try:
        db = createConnect()
        cursor = db.cursor()
        sql = 'select count(*) from godeyes_' + table
        cursor.execute(sql)
        num = cursor.fetchone()[0]
        return num
    except pymysql.err.ProgrammingError:
        return 'Table missing'
    finally:
        closeConnection(db, cursor)


def checkTableExists(tableName):
    try:
        db = createConnect()
        cursor = db.cursor()
        sql = "SELECT * FROM information_schema.TABLES where TABLE_NAME =%s"
        cursor.execute(sql, tableName)
        num = len(cursor.fetchall())
        if num == 1:
            return True
        else:
            return False
    except pymysql.err.ProgrammingError as e:
        raise GEsys.SystemError("未知的错误" + str(e))
    finally:
        closeConnection(db, cursor)


def checkSelf():
    if not checkTableExists("godeyes_users"):
        raise GEsys.SystemError("数据表丢失： godeyes_users")
    elif not checkTableExists("godeyes_http"):
        raise GEsys.SystemError("数据表丢失： godeyes_http")
    elif not checkTableExists("godeyes_mysql"):
        raise GEsys.SystemError("数据表丢失： godeyes_mysql")
    elif not checkTableExists("godeyes_telnet"):
        raise GEsys.SystemError("数据表丢失： godeyes_telnet")
    elif not checkTableExists("godeyes_ssh"):
        raise GEsys.SystemError("数据表丢失： godeyes_ssh")
    elif not checkTableExists("godeyes_log"):
        raise GEsys.SystemError("数据表丢失： godeyes_log")
    elif not checkTableExists("godeyes_ipdb"):
        raise GEsys.SystemError("数据表丢失： godeyes_ipdb")
    else:
        return True


def record_log(scanner, source, ip, port, e):
    try:
        db = createConnect()
        cursor = db.cursor()
        sql = "REPLACE INTO godeyes_log(scanner,source, ip,port,log,dtime) VALUES(%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql,
                       (str(scanner), str(source), str(ip), str(port), str(e),
                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        db.commit()
    except pymysql.err.IntegrityError as e:
        if not str(e).find("Duplicate entry") > 0:
            record_log("system", source, ip, port, e)
    except Exception:
        record_log("system", source, ip, port, e, '[数据过长无法存入,细节请见控制台]')
        print("数据过长无法存入", source, ip, port, e)
    finally:
        closeConnection(db, cursor)


# def log_clean():
#     db = createConnect()
#     cursor = db.cursor()
#
#     try:
#         sql = 'DELETE FROM `godeyes_log`'
#         cursor.execute(sql)
#         sql = 'ALTER TABLE `godeyes`.`godeyes_log` AUTO_INCREMENT = 1'
#         cursor.execute(sql)
#         db.commit()
#         return True
#     except Exception as e:
#         raise GEsys.DatabaseError("Unknown Error" + e)


def record_http(ip, port, title, head, text):
    try:
        db = createConnect()
        cursor = db.cursor()
        sql = "REPLACE INTO godeyes_http(ip,port,title,head,text,intime) VALUES(%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (ip, port, title, head, text, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        db.commit()
        cursor = db.cursor()
        sql = "UPDATE godeyes_http SET address = ( SELECT godeyes_ipdb.address FROM godeyes_ipdb WHERE INET_ATON( '" + ip + "' ) BETWEEN godeyes_ipdb.startip_iton AND godeyes_ipdb.endip_iton ) WHERE ip =  '" + ip + "' AND PORT = '" + port + "' ;"
        cursor.execute(sql)
        db.commit()
        record_log('http', "[S]", ip, str(port), "添加了一条记录" + ip + ":" + str(port))
    except Exception as e:
        record_log('http', '[E]', ip, port, e)
    finally:
        closeConnection(db, cursor)


def record_item(table, ip, port, text):
    try:
        db = createConnect()
        cursor = db.cursor()
        sql = "REPLACE INTO godeyes_" + table + "(ip,port,text,intime) VALUES(%s,%s,%s,%s)"
        cursor.execute(sql, (ip, port, str(text), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        db.commit()
        cursor = db.cursor()
        sql = "UPDATE godeyes_" + table + " SET address = ( SELECT godeyes_ipdb.address FROM godeyes_ipdb WHERE INET_ATON( '" + ip + "' ) BETWEEN godeyes_ipdb.startip_iton AND godeyes_ipdb.endip_iton ) WHERE ip =  '" + ip + "' AND PORT = '" + str(
            port) + "' ;"
        cursor.execute(sql)
        db.commit()
        record_log(table, "[S]", ip, str(port), "添加了一条记录" + ip + ":" + str(port))
    except Exception as e:
        record_log(table, '[E]', ip, str(port), e)
    finally:
        closeConnection(db, cursor)


def getRecord(code, arg1, arg2):
    if arg1 == 'last':
        if code == "http" or code == 'telnet' or code == 'ssh' or code == 'mysql':
            db = createConnect()
            cursor = db.cursor()
            sql = "select ip,port,address,intime from godeyes_" + code + " order by intime DESC limit " + arg2
            cursor.execute(sql)
            content = cursor.fetchall()
            closeConnection(db, cursor)
    # 构造json
    article_info = {}
    data = json.loads(json.dumps(article_info))
    s = 0
    for i in content:
        s += 1
        article2 = {'ip': i[0], 'port': i[1], "address": i[2], 'intime': str(i[3])}
        data[str(s)] = article2

    return data


def getLogSWE():
    article_info = {}
    data = json.loads(json.dumps(article_info))
    s = "ojbk"
    db = createConnect()
    cursor = db.cursor()
    sql = "select count(*) from godeyes_log where source = '[S]'"
    cursor.execute(sql)
    content1 = cursor.fetchone()
    sql = "select count(*) from godeyes_log where source = '[W]'"
    cursor.execute(sql)
    content2 = cursor.fetchone()
    sql = "select count(*) from godeyes_log where source = '[E]'"
    cursor.execute(sql)
    content3 = cursor.fetchone()
    article2 = {'S': content1[0], 'W': content2[0], "E": content3[0]}
    data[str(s)] = article2
    closeConnection(db, cursor)
    return data


def len_translations(len):
    len = int(len)
    if len == 0:
        len = 5
    elif len == 1:
        len = 10
    elif len == 2:
        len = 15
    elif len == 3:
        len = 20
    elif len == 4:
        len = 50
    return len


def getDBRecord(entry, start, len, finder=None):
    start = int(start)
    len = len_translations(len)
    article_info = {}
    data = json.loads(json.dumps(article_info))
    s = "ojbk"
    db = createConnect()
    cursor = db.cursor()
    article2 = {}
    if finder is not None:
        #
        if entry == 'http':
            sql = '''
                        SELECT * FROM `godeyes_http` WHERE `ip` LIKE concat('%%',%s,'%%') OR `port` LIKE concat('%%',%s,'%%')  
                        OR `title` LIKE concat('%%',%s,'%%') 
                        OR `head` LIKE concat('%%',%s,'%%') 
                        OR `text` LIKE concat('%%',%s,'%%') 
                        OR `address` LIKE concat('%%',%s,'%%') ORDER BY `intime` DESC
                        limit %s,%s
            '''
            count = cursor.execute(sql, (finder, finder, finder, finder, finder, finder, start, len))
        else:
            sql = '''
                        SELECT * FROM `godeyes_''' + entry + '''`  WHERE `ip` LIKE concat('%%',%s,'%%')  OR `port` LIKE concat('%%',%s,'%%') 
                        OR `text` LIKE concat('%%',%s,'%%') 
                        OR `address` LIKE concat('%%',%s,'%%')  ORDER BY `intime` DESC
                        limit %s,%s
                        '''
            count = cursor.execute(sql, (finder, finder, finder, finder, start, len))
    else:
        sql = 'select * from godeyes_' + entry + ' ORDER BY `intime` DESC limit %s,%s'  #
        count = cursor.execute(sql, (start, len))
    ip = port = title = head = text = addr = intime = ""
    for i in range(count):
        record_one = cursor.fetchone()
        if entry == 'http':
            ip = record_one[0]
            port = record_one[1]
            title = record_one[2]
            head = record_one[3]
            text = record_one[4]
            addr = record_one[5]
            intime = record_one[6]
            article2[str(i)] = {"ip": ip,
                                "port": port,
                                "title": title,
                                "head": head,
                                "text": text,
                                "addr": addr,
                                "intime": intime}
        else:
            ip = record_one[0]
            port = record_one[1]
            text = record_one[2]
            addr = record_one[3]
            intime = record_one[4]
            article2[str(i)] = {"ip": ip,
                                "port": port,
                                "text": text,
                                "addr": addr,
                                "intime": intime}
    cursor = db.cursor()
    if entry == 'http':
        sql = '''
                    SELECT count(ip) FROM `godeyes_http` WHERE `ip` LIKE concat('%%',%s,'%%') OR `port` LIKE concat('%%',%s,'%%')  
                    OR `title` LIKE concat('%%',%s,'%%') 
                    OR `head` LIKE concat('%%',%s,'%%') 
                    OR `text` LIKE concat('%%',%s,'%%') 
                    OR `address` LIKE concat('%%',%s,'%%') 
        '''
        cursor.execute(sql, (finder, finder, finder, finder, finder, finder))
    else:
        sql = '''
                    SELECT count(ip) FROM `godeyes_''' + entry + '''` WHERE `ip` LIKE concat('%%',%s,'%%')  OR `port` LIKE concat('%%',%s,'%%') 
                    OR `text` LIKE concat('%%',%s,'%%') 
                    OR `address` LIKE concat('%%',%s,'%%') 
                    '''
        cursor.execute(sql, (finder, finder, finder, finder))
    article2["count"] = cursor.fetchone()[0]
    article2["Tcount"] = count
    data[str(s)] = article2
    closeConnection(db, cursor)
    return json.dumps(data, cls=DateEncoder, ensure_ascii=False)


def SRecordOper(options, table, ip2port, context=None):
    ip2port = str(ip2port).split(":")
    ip = ''
    port = ''
    article_info = {}
    data = json.loads(json.dumps(article_info))
    s = "ojbk"
    try:
        ip = ip2port[0]
        port = ip2port[1]
    except Exception as e:
        s = "Error"
        article2 = {'code': -1, 'details': "不明确的错误:" + str(e)}
        data[str(s)] = article2
        return data

    db = createConnect()
    cursor = db.cursor()
    if options == 'delRecord':
        sql = '''delete from `godeyes_''' + table + '''` WHERE ip =%s and port =%s'''
        cursor.execute(sql, (ip, port))
        article2 = {'row': cursor.rowcount}
        db.commit()
    elif options == 'ChangeRecord':
        sql = '''update `godeyes_''' + table + '''` set text =%s WHERE ip =%s and port =%s'''
        cursor.execute(sql, (context, ip, port))
        db.commit()
        article2 = {'row': cursor.rowcount}
    data[str(s)] = article2
    closeConnection(db, cursor)
    return data


def IPDBRecordOper(req, start=0, len=0, finder=""):
    article_info = {}
    data = json.loads(json.dumps(article_info))
    s = "ojbk"
    db = createConnect()
    start = int(start)
    len = len_translations(len)
    if req == "getIPDBRecord":
        if re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
                    finder):
            flag = '4'
        else:
            if re.match(r"^(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}$", finder, re.I):
                flag = '6'
            else:
                flag = 'addr'
        if req == "getIPDBRecord":
            queryCount = 0
            article2 = {}
            cursor = db.cursor()
            # get record count
            if finder == "":
                sql = '''SELECT count(*) FROM `godeyes_ipdb`'''
                cursor.execute(sql)
                recordCount = cursor.fetchone()
                article2["total"] = recordCount
            else:
                if flag == 'addr':
                    sql = '''select * from `godeyes_ipdb` where address LIKE concat('%%',%s,'%%')'''
                else:
                    sql = '''SELECT count(*) FROM `godeyes_ipdb` where inet_aton(%s) between godeyes_ipdb.startip_iton AND godeyes_ipdb.endip_iton'''
                recordCount = cursor.execute(sql, finder)
                article2["total"] = recordCount
            # get record
            if finder == "":
                sql = '''select * from `godeyes_ipdb` limit %s,%s'''
                queryCount = cursor.execute(sql, (start, len))
            else:
                if flag == 'addr':
                    sql = '''select * from `godeyes_ipdb` where address LIKE concat('%%',%s,'%%') limit %s,%s'''
                else:
                    sql = '''SELECT * FROM `godeyes_ipdb` where inet_aton(%s) between godeyes_ipdb.startip_iton AND godeyes_ipdb.endip_iton limit %s,%s'''
                queryCount = cursor.execute(sql, (finder, start, len))
            article2["row"] = queryCount
            for i in range(queryCount):
                record_one = cursor.fetchone()
                startip = record_one[0]
                endip = record_one[1]
                startip_iton = record_one[2]
                endip_iton = record_one[3]
                address = record_one[4]
                article2[str(i)] = {"startip": startip,
                                    "endip": endip,
                                    "startip_iton": startip_iton,
                                    "endip_iton": endip_iton,
                                    "address": address
                                    }
            data[str(s)] = article2
            closeConnection(db, cursor)
            return data


def getHeader():
    db = createConnect()
    cursor = db.cursor()
    sql = "select head from godeyes_http"
    count = cursor.execute(sql)
    result = ""
    for i in range(count):
        item = str(cursor.fetchone())
        item = item[2:len(item) - 3].replace("\\", "")
        item = json.loads(json.dumps(item))
        result += item + "\n"
    closeConnection(db, cursor)
    return result


def getAllFingerPrint(code, request):
    article_info = {}
    data = json.loads(json.dumps(article_info))
    if code == 'cache':
        if not os.path.exists(BASE_DIR + "\\FingerPrint\\custom\\webFingerPrint\\result.json"):
            data["ojbk"] = {"code": -1, "result": "文件不存在"}
            return data
        else:
            with open(BASE_DIR + "\\FingerPrint\\custom\\webFingerPrint\\result.json") as f:
                try:
                    data = json.load(f)
                except:
                    data["ojbk"] = {"code": -1, "result": "文件格式错误"}
                return data
    elif code == "rebuild":
        GEsys.addLog("指纹", "开始重建指纹列表", request.session["username"], request.META.get("REMOTE_ADDR"))
        with open(BASE_DIR + "\\FingerPrint\\custom\\webFingerPrint\\result.json", mode='w') as foper:
            fp = fingerprint()
            v = fp.judge()
            s = 0
            for i in v:
                s = s + 1
                t = i[0].split('{hashCode}')
                article2 = {'fingerprint': t[0], 'val': t[1], "count": i[1]}
                data[str(s)] = article2
            json.dump(data, foper)
            GEsys.addLog("指纹", "指纹重建结束", request.session["username"], request.META.get("REMOTE_ADDR"))


def setLog(code, arg1, arg2, arg3):
    db = createConnect()
    cursor = db.cursor()
    sql = "INSERT INTO godeyes_slog(module,detail,user,ip,dtime) VALUES(%s,%s,%s,%s,%s)"
    cursor.execute(sql,
                   (str(code), str(arg1), str(arg2), str(arg3), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    db.commit()
    article_info = {}
    data = json.loads(json.dumps(article_info))
    s = "ojbk"
    article2 = {'code': 0}
    data[str(s)] = article2
    closeConnection(db, cursor)
    return data


def getUserList():
    article_info = {}
    data = json.loads(json.dumps(article_info))
    db = createConnect()
    cursor = db.cursor()
    sql = "select * from godeyes_users"
    count = cursor.execute(sql)
    for i in range(count):
        dt = cursor.fetchone()
        data[str(i)] = {"username": str(dt[0]),
                        "password": str(dt[1]),
                        "power": str(dt[2])}
    closeConnection(db, cursor)
    return data


def setUserInfo(code, arg1, arg2):
    if arg2 == "true":
        arg2 = "SuperAdmin"
    else:
        arg2 = "Vistor"
    db = createConnect()
    cursor = db.cursor()
    sql = "UPDATE godeyes_users SET password=%s,power=%s where username =%s"
    cursor.execute(sql, (str(arg1), arg2, str(code)))
    db.commit()
    article_info = {}
    data = json.loads(json.dumps(article_info))
    s = "ojbk"
    article2 = {'code': 0}
    data[str(s)] = article2
    closeConnection(db, cursor)
    return data


def checkSAAccount():
    db = createConnect()
    cursor = db.cursor()
    sql = "select * from godeyes_users where power = 'SuperAdmin'"
    count = cursor.execute(sql)
    if count == 1:
        return True
    else:
        return False


def deleteUser(code, arg1, arg2):
    article_info = {}
    data = json.loads(json.dumps(article_info))
    try:
        if checkSAAccount() and arg2 == 'SuperAdmin':
            s = "ojbk"
            article2 = {'code': -1, "detail": "删除失败,至少一个SA账户"}
            data[str(s)] = article2
            return data
        db = createConnect()
        cursor = db.cursor()
        sql = "DELETE FROM godeyes_users WHERE username = %s and password=%s and power=%s "
        count = cursor.execute(sql, (str(code), str(arg1), str(arg2)))
        db.commit()

        if count == 0:
            s = "ojbk"
            article2 = {'code': -1, "detail": "删除失败"}
            data[str(s)] = article2
            return data
        s = "ojbk"
        article2 = {'code': 0, "detail": "删除成功"}
        data[str(s)] = article2
    except:
        s = "ojbk"
        article2 = {'code': -1, "detail": "删除失败"}
        data[str(s)] = article2
    finally:
        closeConnection(db, cursor)
    return data


def addUserInfo(code, arg1, arg2):
    if arg2 == "true":
        arg2 = "SuperAdmin"
    else:
        arg2 = "Vistor"
    article_info = {}
    data = json.loads(json.dumps(article_info))
    try:
        db = createConnect()
        cursor = db.cursor()
        sql = "INSERT INTO godeyes_users VALUES(%s,%s,%s) "
        cursor.execute(sql, (str(code), str(arg1), str(arg2)))
        db.commit()
        s = "ojbk"
        article2 = {'code': 0, "detail": "添加成功"}
        data[str(s)] = article2
    except Exception as e:
        print(e)
        s = "ojbk"
        article2 = {'code': -1, "detail": "添加失败"}
        data[str(s)] = article2
    finally:
        closeConnection(db, cursor)
    return data


def getScannerLog():
    article_info = {}
    data = json.loads(json.dumps(article_info))
    db = createConnect()
    cursor = db.cursor()
    sql = "select * from godeyes_log"
    count = cursor.execute(sql)
    for i in range(count):
        dt = cursor.fetchone()
        data[str(i)] = {"id": str(dt[0]),
                        "source": str(dt[1]),
                        "ip": str(dt[2]),
                        "port": str(dt[3]),
                        "log": str(dt[4]),
                        "dtime": str(dt[5])}

    closeConnection(db, cursor)
    return data


def getSystemLog():
    article_info = {}
    data = json.loads(json.dumps(article_info))
    db = createConnect()
    cursor = db.cursor()
    sql = "SELECT * FROM godeyes_slog"
    count = cursor.execute(sql)
    for i in range(count):
        dt = cursor.fetchone()
        data[str(i)] = {"id": str(dt[0]),
                        "module": str(dt[1]),
                        "detail": str(dt[2]),
                        "user": str(dt[3]),
                        "ip": str(dt[4]),
                        "dtime": str(dt[5])}
    closeConnection(db, cursor)
    return data


def clearDataTable(code):
    article_info = {}
    data = json.loads(json.dumps(article_info))
    try:
        for i in code.split(","):
            db = createConnect()
            cursor = db.cursor()
            sql = "truncate table " + i
            cursor.execute(sql)
        s = "ojbk"
        article2 = {'code': 0, "detail": "删除成功"}
        data[str(s)] = article2
        return data
    except Exception as e:
        print(e)
        s = "ojbk"
        article2 = {'code': -1, "detail": "删除失败"}
        data[str(s)] = article2
        return data
    finally:
        closeConnection(db, cursor)


def judgeMySqlItemExists(ip, port):
    db = createConnect()
    cursor = db.cursor()
    sql = "SELECT text FROM godeyes_mysql where ip =%s and port = %s"
    count = cursor.execute(sql, (ip, port))
    if count == 0:
        return "0"
    else:
        rst = cursor.fetchone()[0]
        if str(rst).find("Access denied for") > 0:
            return "null"
        else:
            return str(rst)
    closeConnection(db, cursor)


def judgeSSHItemExists(ip, port):
    db = createConnect()
    cursor = db.cursor()
    sql = "SELECT text FROM godeyes_ssh where ip =%s and port = %s"
    count = cursor.execute(sql, (ip, port))

    if count == 0:
        return "0"
    else:
        rst = cursor.fetchone()[0]
        closeConnection(db, cursor)
        if str(rst).find("<==u-k==>") > 0:
            return str(rst)
        else:
            return "null"


class DateEnconding(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.date):
            return o.strftime('%Y/%m/%d')
        if isinstance(o, bytes):
            return str(o, encoding='utf-8')


class mySQLConnector(threading.Thread):

    def addDatabase(self, e=None, result=None):
        global dbMutex
        dbMutex.acquire()
        text = str(self.username) + "<==u-k==>" + str(self.password)
        if self.ip != self.host:
            self.text = "Domain:" + self.host + "\n" + text
        if e is not None:
            if judgeMySqlItemExists(self.host, self.port) == '0':
                record_item("mysql", self.host, self.port, e)
        if result is not None:
            record_item("mysql", self.host, self.port, text)
        dbMutex.release()

    def addDatabaseLog(self, e):
        record_log("mysql", '[W]', self.ip, self.port, e)

    def __init__(self, host="127.0.0.1", port=3306, username="_root_", password="_root_", crack=False, final=False,
                 count=-1
                 ):
        self.host = host
        self.ip = socket.gethostbyname(self.host)
        self.port = int(port)
        self.username = username
        self.password = password
        self.crack = crack
        self.final = final
        self.text = ""
        try:
            GEsys.System_Status = "尝试链接MySQL:" + self.ip + "-" + str(self.port)
            threadResult[self.ip + "-" + str(self.port)][2] = self.final

            if threadResult[self.ip + "-" + str(self.port)][3] > 3:
                self.addDatabaseLog("MySQL服务连接多次，但目标服务没有正确响应，跳过此端口" + self.ip + "-" + str(self.port))
                return

            self.pyMysql = pymysql.connections.Connection(host=self.host, port=self.port, user=self.username,
                                                          password=self.password)
            # try:
            #     self.tempCursor = self.pyMysql.cursor()
            #     self.TempExecute = self.tempCursor.execute("show databases;")
            #     self.text = str(self.tempCursor.fetchall())
            # except:
            #     pass

            threadResult[self.ip + "-" + str(self.port)][0] = True
            self.pyMysql.close()

            self.addDatabase(result="yes")
        except pymysql.err.OperationalError as e:
            # traceback.print_exc()
            if str(e).find("Can't connect to MySQL server") > 0:
                self.addDatabaseLog("此端口不存在MySQL服务:" + str(e))
                # threadResult[self.ip + "-" + str(self.port)][3] += 1
                return
            else:
                self.addDatabase(e=str(e))
        except pymysql.err.InternalError as e:
            self.addDatabase(str(e))
        except Exception as e:
            traceback.print_exc()
            self.addDatabaseLog(str(e))
        except socket.timeout as e:
            self.addDatabaseLog("MySQL服务连接超时:" + str(e))
        # finally:
        # threadResult[self.ip + "-" + str(self.port)][1] += 1
        # if threadResult[self.ip + "-" + str(self.port)][1] >= count:
        #     threadResult.pop(self.ip + "-" + str(self.port))


def startThread(method, url):
    global threadResult, dbMutex
    dbMutex = threading.Lock()
    threadResult = {}

    enable = GEsys.getConfigItem("mysqlScanners", "enable")
    threadCount = int(GEsys.getConfigItem("mysqlScanners", "threadCount"))
    delay = GEsys.getConfigItem("mysqlScanners", "delay")
    crash = GEsys.getConfigItem("mysqlScanners", "crash")
    combinCount = 0
    if crash == "True":
        userlist = GEsys.Crack_File_Oper("ir", "getCrackUserFile", "mysql")
        pwdlist = GEsys.Crack_File_Oper("ir", "getCrackPasswordFile", "mysql")
        combinCount = len(userlist) + len(pwdlist)

    portList = GEsys.GOSScannerPort("mysql", "r")
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
                    except Exception as e:
                        threadResult[u + "-" + str(port)] = [False, 0, False, 0]
                    exists = judgeMySqlItemExists(u, port)
                    if exists != 'null' and exists != '0':
                        splitUK = exists.split("<==u-k==>")
                        threading.Thread(target=innerThread,
                                         args=(u, port, splitUK[0], splitUK[1], crash, False, combinCount,)).start()
                except:
                    traceback.print_exc()

                threading.Thread(target=innerThread,
                                 args=(u, port, "root", "root", False, True, -1)).start()
                # print(GEsys.threadInfo, u, port, GEsys.threadInfo["mysqlThreadNum"], threadCount)
                if GEsys.STOP:
                    return
                while GEsys.threadInfo["mysqlThreadNum"] > threadCount:
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
                    except Exception as e:
                        threadResult[u + "-" + str(port)] = [False, 0, False, 0]
                    exists = judgeMySqlItemExists(u, port)
                    if exists != 'null' and exists != '0':
                        splitUK = exists.split("<==u-k==>")
                        threading.Thread(target=innerThread,
                                         args=(u, port, splitUK[0], splitUK[1], crash, False, combinCount,)).start()
                except Exception as e:
                    traceback.print_exc()
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
                                                 args=(u, port, usr, pwd, crash, True, combinCount,)).start()
                            else:
                                threading.Thread(target=innerThread,
                                                 args=(u, port, usr, pwd, crash, False, combinCount,)).start()
                            # print(GEsys.threadInfo, u, port, GEsys.threadInfo["mysqlThreadNum"], threadCount)
                            if GEsys.STOP:
                                return
                            while GEsys.threadInfo["mysqlThreadNum"] > threadCount:
                                time.sleep(delay)

                else:
                    threading.Thread(target=innerThread,
                                     args=(u, port, "root", "root", crash, True, -1,)).start()
                    # print(GEsys.threadInfo, u, port, GEsys.threadInfo["mysqlThreadNum"], threadCount)
                    if GEsys.STOP:
                        return
                    while GEsys.threadInfo["mysqlThreadNum"] > threadCount:
                        time.sleep(delay)


def innerThread(host, port, username, password, crack, final, Count=-1, ):
    GEsys.threadInfo["mysqlThreadNum"] = GEsys.threadInfo["mysqlThreadNum"] + 1
    try:
        mySQLConnector(host, port, username, password, crack, final, Count)
    except Exception as e:
        traceback.print_exc()
        record_log('mysql', "[E]", host, port, e)
    GEsys.threadInfo["mysqlThreadNum"] = GEsys.threadInfo["mysqlThreadNum"] - 1


#
#
# if __name__ == '__main__':
#     ip = list()
#     startThread("fullScan", "127.0.0.1")


def checkDBLink(arg1, arg2, arg3):
    try:
        host_port = str(arg1).split(":")
        pymysql.connect(host=host_port[0], port=int(host_port[1]), user=arg2, password=arg3)
        return True
    except:
        return False


def install(code):
    if not GEsys.getConfigItem("firstRun"):
        return False
    try:
        GEsys.System_Status = "正在构造参数"
        rst = json.loads(code)
        host_port = rst.get("url").split(":")
        GEsys.System_Status = "正在写入配置"
        GEsys.setConfigItem(host_port[0], "database", "url")
        GEsys.setConfigItem(int(host_port[1]), "database", "port")
        GEsys.setConfigItem(rst.get("dbuser"), "database", "user")
        GEsys.setConfigItem(rst.get("dbpwd"), "database", "passwd")
        GEsys.setConfigItem(rst.get("dbname"), "database", "db")
        GEsys.setConfigItem('utf8', "database", "charset")
        GEsys.System_Status = "正在重建数据库"
        db = pymysql.connect(host=host_port[0], port=int(host_port[1]), user=rst.get("dbuser"),
                             password=rst.get("dbpwd"))
        db.cursor().execute("create database if not exists " + rst.get("dbname"))
        db.commit()
        db = createConnect()
        cursor = db.cursor()
        try:
            for line in DBSQL.replace("\n", " ").split(";"):
                if line == "":
                    continue
                cursor = db.cursor()
                cursor.execute(line)
                db.commit()
        except Exception as e:
            print(e)
        GEsys.System_Status = "正在重建管理员账号"
        addUserInfo(rst.get('geuser'), rst.get('gepwd'), "true")
        closeConnection(db, cursor)
        GEsys.System_Status = "正在更新IP数据表"
        import modules.ipOper as ipOper
        ipOper.updateIPDBVersion()
        GEsys.setConfigItem(False, "firstRun")
        return True
    except Exception as e:
        print(e)
        return False
