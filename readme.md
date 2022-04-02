# GodEyes 说明文档

## 介绍

​		本系统灵感源于shodan和zoomeye, 旨在实现网络空间资产搜索引擎, 但是不同点在于添加了内容摘要和穷举破解模块. 本系统为本人的毕业设计, 其中有可能存在一些问题, 请诸位使用者敬请谅解, 由于需要参与毕业答辩, 需要完成一切相关流程后, 本项目才会开源, 因此上线时间可能会推迟.

​		本系统是基于python语言实现的, 使用MySQL作为数据持久化存储, 因此需要安装python和MySQL. 尽可能版本与开发时版本一致, 这样才能极大可能的减少异常和错误.

## 开发环境

+ python==3.7.8
+ MySQL==5.7.31
+ demjson==2.2.4
+ paramiko==2.7.1
+ Django==2.1.3
+ requests==2.25.1
+ netaddr==0.8.0
+ urllib3==1.24.2
+ PyMySQL==0.9.3

## 目录结构介绍

```bash
--根目录--
> lastest.dat (ip库文件, 当系统IP库更新时将会生成此文件, 此文件为临时文件)
> main.py (GodEyes 傻瓜式运行程序, 打开后即可通过提示启动系统)
> requirements.txt (本系统需要安装的库文件, 首次运行建议在当前目录运行 pip install -r requirements.txt 进行运行库的安装)
> readme.md (系统的介绍文件)
> | FingerPrint (指纹信息存储目录)
> -- > __init__.py (指纹信息初始化模块)
> -- > HttpPortList.txt (http协议的端口号,遵循一行一条)
> -- > MysqlPortList.txt (MySQL协议的端口号,遵循一行一条)
> -- > SshPortList.txt (SSH协议的端口号,遵循一行一条)
> -- > TelnetPortList.txt (TELNET协议的端口号,遵循一行一条)
> -- > proxies.txt (代理服务器存储文件,遵循ip:port格式)
> -- | custom (自定义信息目录)
> -- | -- | dict (破解字典目录)
> -- | -- | -- > default_user.txt (默认的用户名字典,遵循一行一条)
> -- | -- | -- > default_pwd.txt (默认的密码字典,遵循一行一条)
> -- | -- | header (请求头目录)
> -- | -- | -- > default.json (HTTP协议请求头伪造文件,遵循json格式,设计前欲多文件选择,后期时间不足而未实现)
> -- | -- | webFingerPrint (web指纹目录)
> -- | -- | -- > blackList.txt (指纹判断的黑名单列表)
> -- | -- | -- > result.json (指纹构造后的结果存储文件)
> modules (核心模块类 系统后台部分)
> -- > __init__.py (后台初始化模块)
> -- > GSystem.py (定义系统文件处理, 配置处理, 扫描器连接等)
> -- > httpOper.py (HTTP请求扫描模块)
> -- > ipOper.py (IP信息处理模块, IP库管理模块)
> -- > mysqlOper.py (MySQL请求扫描模块, 数据库处理模块)
> -- > sshOper.py (SSH请求扫描模块)
> -- > telnetOper.py (TELNET请求扫描模块)
> -- > sys.json (系统配置文件)
> View (视图层, 基于DJango)
> -- > manage.py (DJango 服务器启动入口)
> -- > db.sqlite3 (SESSION 等服务器存储数据库)
> -- | templates (静态页面)
> -- | -- > ClearData.html (清除数据页面)
> -- | -- > Disclaimer.html (免责声明页面)
> -- | -- > crackRules.html (破解规则页面)
> -- | -- > dashBoard.html (仪表盘页面)
> -- | -- > dataManager.html (数据管理页面)
> -- | -- > empty.html (空页面 用于非json数据回显 后期另有用途)
> -- | -- > fingerPrint.html (指纹管理页面)
> -- | -- > help.html (帮助页面)
> -- | -- > info.html (错误提示页面)
> -- | -- > install.html (安装页面)
> -- | -- > ipTableManager.html (IP表管理页面)
> -- | -- > license.html (许可证页面)
> -- | -- > login.html (登录页面)
> -- | -- > manager.html (管理框架页面)
> -- | -- > modifyAccount.html (账户修改页面 [针对于自身修改])
> -- | -- > portSettings.html (端口设置页面)
> -- | -- > requestConstructor.html (请求头构造页面)
> -- | -- > scanner.html (扫描器页面)
> -- | -- > scannerLog.html (扫描器日志页面)
> -- | -- > systemConfig.html (系统高级配置页面)
> -- | -- > systemLog.html (系统日志页面)
> -- | -- > userManager.html (用户管理页面)
> -- | static (引用的js css font imgs信息 细节部分不做详细说明了)
> -- | -- | ... .... .... .... ...
> -- | -- | js (JavaScript脚本存放路径)
> -- | -- | font (字体存放路径)
> -- | -- | css (层叠样式表存放路径)
> -- | -- | imgs (图片存放路径)
> -- | godeyes (前后端关联模块)
> -- | -- | __init__.py (前后端连接初始化模块)
> -- | -- | control.py (控制层 预处理前端请求)
> -- | -- | settings.py (Django 设置文件)
> -- | -- | urls.py (url 地址处理模块)
> -- | -- | view.py (页面中转处理模块, 用于接收前端请求, 发送给控制层, 并且控制层信息回馈到页面)
> -- | -- | wsgi.py (然而并没有用到, 由Django自动生成)
```

## 配置文件详细说明

```json
{
  "app": "应用名",
  "version": "版本",
  "firstRun": "是否首次运行(布尔类型)",
  "scannerStopWaitSecond": "扫描器停止等待时间,影响前端页面阻塞时间(数字类型)",
  "proxies": "代理模式(Enable/Disable)",
  "proxiesList": "代理文件路径(FingerPrint/proxies.txt)",
  "database": {
    "url": "数据库地址",
    "user": "数据库用户名",
    "passwd": "数据库密码",
    "db": "数据库名称",
    "charset": "数据库编码(默认utf8,如果后期需要修改,请手动修改)"  
},  "ipTable": {
    "source": "IP源名称(CZ88)",
    "currentVersion": "当前IP库版本信息(2021-01-12)",
    "commit_num": "更新IP表分组提交个数, 整数类型(5000)"
},  "httpScanners": {
    "enable": "http扫描器总开关(True)",
    "timeout": "请求超时时间,单位秒(3)",
    "threadCount": "线程总数,实际会比其多一个,单位个(数字类型)",
    "delay": "每此请求过后暂停时间",
    "header": "请求头路径(FingerPrint/custom/header/default.json)",
    "portList": "端口列表(FingerPrint/HttpPortList.txt)",
    "RequestHeaderMode": "请求头模式(custom/normal)"  
},  "mysqlScanners": {
    "enable":"http扫描器总开关(True)",,
    "threadCount": "线程总数,实际会比其多一个,单位个(数字类型)",,
    "delay":  "请求超时时间,单位秒(3)",,
    "crash": "破解开关(True/False)",
    "dictionary_user": "用户名规则文件名",
    "dictionary_pwd": "密码规则文件名"  
},  "sshScanners": {
    "enable": "ssh扫描器总开关(True)",
    "timeout":  "请求超时时间,单位秒(10)",
    "threadCount": "线程总数,实际会比其多一个,单位个(数字类型)",,
    "delay": "请求超时时间,单位秒(3)",
    "crash": "破解开关(True/False)",
    "dictionary_user": "用户名规则文件名",
    "dictionary_pwd": "密码规则文件名"  
},  "telnetScanners": {
    "enable": "telnet扫描器总开关(True)",
    "timeout":  "请求超时时间,单位秒(3)",
    "threadCount": "线程总数,实际会比其多一个,单位个(数字类型)",,
    "delay": "请求超时时间,单位秒(3)",,
    "crash": "破解开关(True/False)",
    "dictionary_user": "用户名规则文件名",
    "dictionary_pwd": "密码规则文件名"  
	}
}
```

# 系统安装

## linux

```bash
apt-get install python pip # 其中apt-get为实例 具体根据系统的包管理器命令为准,此处仅作介绍
pip install -r requirement.txt
```

## windows

```
官方网站下载python3.7.8
安装pip包管理器
在此系统目录运行pip install -r requirement.txt
```

## 系统搭建

1. 运行main.py

2. 如果正常运行, 将会提示中英文的协议条款中部分内容, 回车键即可继续.

3. 如果没有异常, 将会显示 Starting development server at http://127.0.0.1:8000/ 字样 其中地址就是服务器地址, 可以在浏览器中打开

4. 打开后进入安装向导页面, 请认真阅读协议条款, 十秒内无法进行下一步

5. 同意后进入配置页面.

   > 数据库地址: 也就是MySQL服务器的地址
   >
   > 数据库用户: 登录到MySQL的用户名
   >
   > 数据库密码: 登录到指定用户的MySQL用户的密码
   >
   > 数据库名称: 该系统将会在数据库系统中创建一个数据库, 此项也就是您期望数据库的名称
   >
   > 默认管理员的用户名: 登录到该系统的用户名
   >
   > 默认管理员的密码:  登录到该系统默认管理员的密码

   其中校验时对于数据库连接的校验, 其中管理员密码至少六位, 设置完毕后即可进行安装

6. 安装过程可能需要大量时间, 请保证网络通畅, 因为系统安装的过程中不仅仅对于本地数据表的创建, 而且还会更新IP库, IP库通过网络进行下载. 此处加了限制, 如果IP库更新失败, 可能无法正常安装和使用系统, 倘若您不需要IP库, 可以手动修改sys.json, 讲firstRun项设置为false

7. 安装成功后跳转到登陆页面

# 功能说明

## 仪表盘

其中通过可视化界面显示系统当前状态, 数据表中表项存放的个数, 当前扫描器事件, 普通扫描器的活动线程数量以及最近加入数据库的项目列表

## 扫描器

对于扫描器的所有功能

### 综合扫描器

管理员可以通过数据IP或者是CIDR块进行IP段的扫描, 扫描分为三种扫描方式

- 快速扫描 此方式只会进行http协议的扫描
- 扩展扫描 此方式会对http\ssh\mysql\telnet协议进行扫描
- 完整扫描 在扩展扫描的基础上会对ssh\MySQL\telnet进行密码登录的破解

协扫描模式: 多进程扫描模式, 此方法对于前端页面响应影响较小, 但是此方法不会显示线程信息

已选中的端口仅为端口显示的提示,如果需要配置, 参见 3.2.2

### 端口设置

此页面分为4栏, 每个协议中均可设置扫描端口, 后台会根据换行(回车)进行逐一扫描, 因此需要您遵循程序解析的规范

+ 检查按钮: 此按钮即可检查是否符合解析规范, 结果将会在主标题下回显
+ 保存按钮: 此按钮即可将前端页面中输入的端口文本传递给后台服务器, 服务器进行保存, 保存结果将会在主标题下回显
+ 如果出现错误: 将会提示错误的协议名以及具体行, 红色代表错误, 绿色代表成功

### 请求构造

请求构造是针对性行为, 默认请求头为空, 并且无法修改请求体格式, 只有在自定义模式下才可以修改, 因为请求头格式为键值对, 因此您需要遵循JSON的语法格式, 我们也提供了格式的校验功能.

+ 重新加载: 重新从服务器中加载, 并且回显到前端页面, 此按钮将直接覆盖页面中的数据.
+ 格式化&校验: 格式化JSON文本, 并且校验是否符合JSON语法, 如果JSON非法, 将会弹出提示, 并且提示错误的具体位置
+ 保存: 将请求体中的数据上传到服务器, 服务器进行保存. 

:warning: 本模块中保存并不具备校验功能, 因为JSON校验结果仅供参考, 如果您确信您的请求头没有问题, 可以直接保存. 我没有对保存加以校验限制.



### 穷举爆破规则

:warning: 此模块涉及到破解部分, 请合法使用

:tipping_hand_man: 提示: 穷举爆破的条目并不是越多越好, 如果过分的多会影响整体效率, 并且可能触发目标服务器的防火墙, 因此请先与渗透甲方进行协商

此模块中的TELNET破解为实验性功能, 无法保障成功的破解, 结果数据仅供参考

头部:

- MySQL 切换--查看并且修改MySQL 的规则
- Telnet 切换--查看并且修改Telnet 的规则
- SSH 切换--查看并且修改SSH 的规则

中部:

- 规则文件--账户: 下拉框可以选择已经存在的规则, 选中后即自动保存
- 新建: 新建指定规则的文件, 您需要保证用户名符合操作系统以及磁盘类型的规范
- 保存: 如果您对下面的规则文本进行了修改, 需要点击保存才能生效
- 删除: 此操作会提示确认, 删除当前选中的规则文件. 默认字典不允许删除

下部:

- 左侧为用户名回显以及修改区域
- 右侧为密码回显以及修改区域

## 数据中心

### 数据管理

上部: 选择需要管理的协议

中部:

- 搜索: 搜索在后台进行的是全字段的模糊查询

数据部分:

- 左侧: 显示协议名称, 图标右下角的颜色代表可靠程度, 灰色代表不可靠, 绿色代表可靠. 可靠判断规则为7天内均为可靠数据
- 顶部: IP:端口 以及IP对应的地理位置
- 右侧: 此纪录存入数据库的时间
- 下侧: 详细内容

导航分页:

- 您可以跳转到首页和尾页以及当前页的前一页和后一页
- 无法手动输入页码, 但是如果您非要这么做, 可以看一下cookies, 可能会有灵感呦

### IP表管理

IP库仪表盘: 显示当前数据源以及IP库的信息, 此页面可以进行IP库的升级操作, 当前作者只收录了一种IP源, 后期可能会增加IP源, 供用户选择

IP库升级: :warning:此操作会停止扫描器的工作, 并且此操作耗时与网络状态正相关

IP搜索: 您可以输入地理地址和IP地址, 我们会将您输入的数据进行数据库检索, IP必须输入完整的地址, 地理地址可以输入部分, 后台会进行模糊搜索.

导航分页:

- 此分页同数据管理

### 指纹管理

操作:

- 重新构建指纹列表: 因为指纹分析需要耗费大量时间, 因此并不是实时处理, 后续版本可能会实现实时处理指纹, 指纹为请求头中的关键字, 根据排名分析, 可以看到web服务器的信息, 例如服务器的构架, 操作系统等信息
- 指纹黑名单: 因为指纹识别模块需要处理大量的字符, 其中涉及到脏数据的清理, 因此算法可能不能完全胜任, 因此如果您不希望一些字样出现在指纹中, 可以通过指纹黑名单进行设置, 当重新构建指纹列表时就会跳过此字样. (服务器在重新构建指纹列表时,判断是不区分大小写的，字段按行分割)

## 系统设置

### 用户管理

管理员可以在此页面对用户信息进行设置, 甚至可以看到用户的密码, 但是只有管理员才会有这个权限, 管理员可以添加用户,并且可以修改用户的密码,甚至是级别. 但是删除的时候还是要保留一个管理员噢.

### 扫描器日志

此页面为扫描器生成的日志数据, 在页面中就可以直接看到扫描器工作状态, 可以通过搜索来进行级别筛选.

:warning: 如果页面加载速度过慢, 请考虑日志数量太多了, 是时候清理一下日志了.

### 系统日志:

此页面为系统事件产生的日志数据, 那个用户使用的IP是什么, 访问了哪些页面, 发送了那些请求.

:warning: 如果页面加载速度过慢, 请考虑日志数量太多了, 是时候清理一下日志了.

:warning: 当修改密码的时候, 密码也会明文记录到日志中

### 配置文件

+ 重新加载: 重新从服务器中加载, 并且回显到前端页面, 此按钮将直接覆盖页面中的数据.
+ 格式化&校验: 格式化JSON文本, 并且校验是否符合JSON语法, 如果JSON非法, 将会弹出提示, 并且提示错误的具体位置
+ 保存: 将配置文本上传到服务器, 服务器进行保存. 

:warning:详细配置规则见1.4 , 手动修改开放性较强, 但是如果修改时出现错误, 可能导致系统无法正常使用, 甚至是无法启动

### 清空数据表

此页面中对于数据表进行了解释, 您需要手动选择要清空的数据表, 选择完成后, 需要勾选[我很清楚我在做什么( 复选框在页面加载成功后的十秒内无法点击)], 随后才能点击[删除选中项所对应的数据表]

## 帮助

### 帮助文档

也就是网页版的此文档, 本文档将会生成HTML页面, 存放到系统的帮助文档中

### 免责声明

您在安装过程中已经同意了的免责声明条款, 您可以在这个页面重新看到此声明

### 许可协议

本项目遵循的开源许可说明

# 疑难解答

## sys.json修复

:warning: 注意: 此配置为​重新安装的sys.json, 如果需要重新安装系统, 请替换此文件内容到sys.json

```json
{
  "app": "God Eyes",
  "version": "v1.0",
  "firstRun": true,
  "scannerStopWaitSecond": 1,
  "proxies": "Disable",
  "proxiesList": "FingerPrint/proxies.txt",
  "database": {
    "url": "localhost",
    "user": "root",
    "passwd": "root",
    "db": "godeyes",
    "charset": "utf8"  
},  "ipTable": {
    "source": "CZ88",
    "currentVersion": "0000-00-00",
    "commit_num": 5000  
},  "httpScanners": {
    "enable": "True",
    "timeout": 3,
    "threadCount": 50,
    "delay": 2,
    "header": "FingerPrint/custom/header/default.json",
    "portList": "FingerPrint/HttpPortList.txt",
    "RequestHeaderMode": "custom"  
},  "mysqlScanners": {
    "enable": "True",
    "threadCount": 50,
    "delay": 2,
    "crash": "True",
    "dictionary_user": "default_user.txt",
    "dictionary_pwd": "default_pwd.txt"  
},  "sshScanners": {
    "enable": "True",
    "timeout": 10,
    "threadCount": 50,
    "delay": 2,
    "crash": "True",
    "dictionary_user": "default_user.txt",
    "dictionary_pwd": "default_pwd.txt"  
},  "telnetScanners": {
    "enable": "True",
    "timeout": 10,
    "threadCount": 50,
    "delay": 2,
    "crash": "True",
    "dictionary_user": "default_user.txt",
    "dictionary_pwd": "default_pwd.txt"  
    }
}
```

## 提示GodEyes服务器错误

1. 可能您长时间登陆后没有操作, 导致当前会话过期, 您可以刷新页面, 也可以通过注销返回到登录页面, 重新登陆即可
2. 此错误既后台服务器错误, 如果您是使用者, 可以将控制台中的错误信息发送给开发者

## 正在等待服务器响应...时间过长

1. 这个问题可能是因为您的电脑配置过低, 导致数据库回调过慢, 可以考虑把数据存放到固态硬盘中, 甚至是读写效率更高的存储设备(内存盘, 磁带)
2. 如果等待时间过长, 可以在开发者视图重新复现, 观察Console项是否存在异常, 本项目测试过程已经预防了报错不提示, 如果仍然有漏网之鱼, 请反馈

## 页面加载不正常

由于开发过程中一致使用Chrome, 使用者尽量使用谷歌浏览器, 虽然做了适配, 但是难免存在漏网之鱼, 如果仍然不正常, 请反馈.