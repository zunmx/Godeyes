# -*- coding:utf-8  -*-
import os
def showInfo():
    print("#上帝之眼控制台终端\n"
          "(GodEyes Command-line terminal)")
    print("#此项目遵循GPL许可\n"
          "(This license has been superseded by the GPL License)")
    print("#此项目包含危险的功能，请合法使用，一切后果自行承担。\n"
          "(This project contains dangerous functions. Please use it legally and bear all consequences.)")
    print("#回车即可进入系统\n"
          "(Press enter to continue.)")
    input()


if __name__ == '__main__':
    showInfo()
    os.system("python View/manage.py runserver 0.0.0.0:8000 --insecure")

