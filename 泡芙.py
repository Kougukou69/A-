#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import shutil
import sys
import subprocess
import string
import random
import json
import re
import time
import argparse
import zipfile
from io import BytesIO

from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.decorators import MessageDecorator
from utils.provider import APIProvider

try:
    import requests
    from colorama import Fore, Style
except ImportError:
    print("\t某些依赖无法导入（可能未安装）")
    print(
        "输入 `pip3 install -r requirements.txt` 来"
        " 安装所有必需的包")
    sys.exit(1)


def readisdc():
    with open("isdcodes.json") as file:
        isdcodes = json.load(file)
    return isdcodes


def get_version():
    try:
        return open(".version", "r").read().strip()
    except Exception:
        return '1.0'


def clr():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def bann_text():
    clr()
    logo = """
┌───┬─┐┌─┬───┐▒▒┌───┬───┬┐▒▒┌┐▒▒▒┌──┐┌───┬─┐┌─┬──┐┌───┬───┐
│┌─┐││└┘││┌─┐│▒▒│┌─┐│┌─┐││▒▒││▒▒▒│┌┐││┌─┐││└┘││┌┐││┌──┤┌─┐│
│└──┤┌┐┌┐│└──┐▒▒││▒└┤│▒│││▒▒││▒▒▒│└┘└┤│▒││┌┐┌┐│└┘└┤└──┤└─┘│
└──┐│││││├──┐├──┤│▒┌┤└─┘││▒┌┤│▒┌┐│┌─┐││▒│││││││┌─┐│┌──┤┌┐┌┘
│└─┘││││││└─┘├──┤└─┘│┌─┐│└─┘│└─┘││└─┘│└─┘││││││└─┘│└──┤││└┐
└───┴┘└┘└┴───┘▒▒└───┴┘▒└┴───┴───┘└───┴───┴┘└┘└┴───┴───┴┘└─┘
作者: RAVI SHARMA"""
    if ASCII_MODE:
        logo = ""
    version = "版本: "+__VERSION__
    contributors = "贡献者: "+" ".join(__CONTRIBUTORS__)
    print(random.choice(ALL_COLORS) + logo + RESET_ALL)
    mesgdcrt.SuccessMessage(version)
    mesgdcrt.SectionMessage(contributors)
    print()

    
def check_intr():
    try:
        requests.get("https://motherfuckingwebsite.com", timeout=5)
    except Exception:
        bann_text()
        mesgdcrt.FailureMessage("检测到网络连接不良")
        sys.exit(2)


def format_phone(num):
    num = [n for n in num if n in string.digits]
    return ''.join(num).strip()


def do_zip_update():
    success = False
    if DEBUG_MODE:
        zip_url = "https://github.com/ravisharma011/SMSBOMBING/archive/refs/heads/main.zip"
        dir_name = "SMSBOMBING-main"
    else:
        zip_url = "https://github.com/ravisharma011/SMSBOMBING/archive/refs/heads/main.zip"
        dir_name = "SMSBOMBING-main"
    print(ALL_COLORS[0]+"正在下载ZIP... "+RESET_ALL)
    response = requests.get(zip_url)
    if response.status_code == 200:
        zip_content = response.content
        try:
            with zipfile.ZipFile(BytesIO(zip_content)) as zip_file:
                for member in zip_file.namelist():
                    filename = os.path.split(member)
                    if not filename[1]:
                        continue
                    new_filename = os.path.join(
                        filename[0].replace(dir_name, "."),
                        filename[1])
                    source = zip_file.open(member)
                    target = open(new_filename, "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)
            success = True
        except Exception:
            mesgdcrt.FailureMessage("解压时发生错误！")
    if success:
        mesgdcrt.SuccessMessage("SMSBOMBING已更新到最新版本")
        mesgdcrt.GeneralMessage(
            "请再次运行脚本以加载最新版本")
    else:
        mesgdcrt.FailureMessage("无法更新SMSBOMBING。")
        mesgdcrt.WarningMessage(
            "请从 https://github.com/ravisharma011/SMSBOMBING.git 获取最新版本")

    sys.exit()


def do_git_update():
    success = False
    try:
        print(ALL_COLORS[0]+"正在更新 "+RESET_ALL, end='')
        process = subprocess.Popen("git checkout . && git pull ",
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        while process:
            print(ALL_COLORS[0]+'.'+RESET_ALL, end='')
            time.sleep(1)
            returncode = process.poll()
            if returncode is not None:
                break
        success = not process.returncode
    except Exception:
        success = False
    print("\n")

    if success:
        mesgdcrt.SuccessMessage("SMSBOMBING已更新到最新版本")
        mesgdcrt.GeneralMessage(
            "请再次运行脚本以加载最新版本")
    else:
        mesgdcrt.FailureMessage("无法更新SMSBOMBING。")
        mesgdcrt.WarningMessage("确保安装了'git'")
        mesgdcrt.GeneralMessage("然后运行命令:")
        print(
            "git checkout . && "
            "git pull https://github.com/ravisharma011/SMSBOMBING.git HEAD")
    sys.exit()


def update():
    if shutil.which('git'):
        do_git_update()
    else:
        do_zip_update()


def check_for_updates():
    if DEBUG_MODE:
        mesgdcrt.WarningMessage(
            "调试模式已启用！自动更新检查已禁用。")
        return
    mesgdcrt.SectionMessage("正在检查更新")
    try:
        response = requests.get(
            "https://raw.githubusercontent.com/ravisharma011/SMSBOMBING/main/.version",
            timeout=5
        )
        if response.status_code == 200:
            fver = response.text.strip()
            if fver != __VERSION__:
                mesgdcrt.WarningMessage("有可用的更新")
                mesgdcrt.GeneralMessage("正在开始更新...")
                update()
            else:
                mesgdcrt.SuccessMessage("SMSBOMBING已是最新版本")
                mesgdcrt.GeneralMessage("正在启动SMSBOMBING")
        else:
            mesgdcrt.WarningMessage("检查更新失败，继续启动...")
            mesgdcrt.GeneralMessage("正在启动SMSBOMBING")
    except Exception as e:
        mesgdcrt.WarningMessage("检查更新失败，继续启动...")
        mesgdcrt.GeneralMessage("正在启动SMSBOMBING")


def notifyen():
    try:
        if DEBUG_MODE:
            url = "https://raw.githubusercontent.com/ravisharma011/SMSBOMBING/main/.notify"
        else:
            url = "https://raw.githubusercontent.com/ravisharma011/SMSBOMBING/main/.notify"
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            noti = response.text.upper().strip()
            if len(noti) > 10 and not noti.startswith('<'):
                mesgdcrt.SectionMessage("通知: " + noti)
                print()
    except Exception:
        pass


def get_phone_info():
    while True:
        target = ""
        cc = input(mesgdcrt.CommandMessage(
            "输入你的国家代码 (不含+): "))
        cc = format_phone(cc)
        if not country_codes.get(cc, False):
            mesgdcrt.WarningMessage(
                "你输入的国家代码 ({cc})"
                " 无效或不支持".format(cc=cc))
            continue
        target = input(mesgdcrt.CommandMessage(
            "输入目标号码: +" + cc + " "))
        target = format_phone(target)
        if ((len(target) <= 6) or (len(target) >= 12)):
            mesgdcrt.WarningMessage(
                "你输入的电话号码 ({target})".format(target=target) +
                "无效")
            continue
        return (cc, target)


def get_mail_info():
    mail_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    while True:
        target = input(mesgdcrt.CommandMessage("输入目标邮箱: "))
        if not re.search(mail_regex, target, re.IGNORECASE):
            mesgdcrt.WarningMessage(
                "你输入的邮箱 ({target})".format(target=target) +
                " 无效")
            continue
        return target


def pretty_print(cc, target, success, failed):
    requested = success+failed
    mesgdcrt.SectionMessage("轰炸正在进行 - 请耐心等待")
    mesgdcrt.GeneralMessage(
        "轰炸期间请保持网络连接")
    mesgdcrt.GeneralMessage("目标       : " + cc + " " + target)
    mesgdcrt.GeneralMessage("已发送     : " + str(requested))
    mesgdcrt.GeneralMessage("成功       : " + str(success))
    mesgdcrt.GeneralMessage("失败       : " + str(failed))
    mesgdcrt.WarningMessage(
        "此工具仅用于娱乐和研究目的")
    mesgdcrt.SuccessMessage("SMSBOMBING由RaviSharma创建")


def workernode(mode, cc, target, count, delay, max_threads):

    api = APIProvider(cc, target, mode, delay=delay)
    clr()
    mesgdcrt.SectionMessage("正在启动轰炸机 - 请耐心等待")
    mesgdcrt.GeneralMessage(
        "轰炸期间请保持网络连接")
    mesgdcrt.GeneralMessage("API版本   : " + api.api_version)
    mesgdcrt.GeneralMessage("目标        : " + cc + target)
    mesgdcrt.GeneralMessage("数量        : " + str(count))
    mesgdcrt.GeneralMessage("线程       : " + str(max_threads) + " 个线程")
    mesgdcrt.GeneralMessage("延迟       : " + str(delay) +
                            " 秒")
    mesgdcrt.WarningMessage(
        "此工具仅用于大学研究目的")
    print()
    input(mesgdcrt.CommandMessage(
        "按 [CTRL+Z] 暂停轰炸机或按 [ENTER] 恢复"))

    if len(APIProvider.api_providers) == 0:
        mesgdcrt.FailureMessage("你的国家/目标暂不支持")
        mesgdcrt.GeneralMessage("欢迎与我们联系")
        input(mesgdcrt.CommandMessage("按 [ENTER] 退出"))
        bann_text()
        sys.exit()

    success, failed = 0, 0
    while success < count:
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            jobs = []
            for i in range(count-success):
                jobs.append(executor.submit(api.hit))

            for job in as_completed(jobs):
                result = job.result()
                if result is None:
                    mesgdcrt.FailureMessage(
                        "已达到目标的轰炸限制")
                    mesgdcrt.GeneralMessage("请稍后再试！")
                    input(mesgdcrt.CommandMessage("按 [ENTER] 退出"))
                    bann_text()
                    sys.exit()
                if result:
                    success += 1
                else:
                    failed += 1
                clr()
                pretty_print(cc, target, success, failed)
    print("\n")
    mesgdcrt.SuccessMessage("轰炸完成！")
    time.sleep(1.5)
    bann_text()
    sys.exit()


def selectnode(mode="sms"):
    mode = mode.lower().strip()
    try:
        clr()
        bann_text()
        check_intr()
        check_for_updates()
        notifyen()

        max_limit = {"sms": 500, "call": 15, "mail": 200}
        cc, target = "", ""
        if mode in ["sms", "call"]:
            cc, target = get_phone_info()
            if cc != "91":
                max_limit.update({"sms": 100})
        elif mode == "mail":
            target = get_mail_info()
        else:
            raise KeyboardInterrupt

        limit = max_limit[mode]
        while True:
            try:
                message = ("输入要发送的{type}数量".format(type=mode.upper()) +
                           " (最多 {limit}): ".format(limit=limit))
                count = int(input(mesgdcrt.CommandMessage(message)).strip())
                if count > limit or count == 0:
                    mesgdcrt.WarningMessage("你请求了 " + str(count)
                                            + " 条{type}".format(
                                                type=mode.upper()))
                    mesgdcrt.GeneralMessage(
                        "自动将数值限制为"
                        " {limit}".format(limit=limit))
                    count = limit
                delay = float(input(
                    mesgdcrt.CommandMessage("输入延迟时间 (单位:秒): "))
                    .strip())
                # delay = 0
                max_thread_limit = (count//10) if (count//10) > 0 else 1
                max_threads = int(input(
                    mesgdcrt.CommandMessage(
                        "输入线程数 (推荐: {max_limit}): "
                        .format(max_limit=max_thread_limit)))
                    .strip())
                max_threads = max_threads if (
                    max_threads > 0) else max_thread_limit
                if (count < 0 or delay < 0):
                    raise Exception
                break
            except KeyboardInterrupt as ki:
                raise ki
            except Exception:
                mesgdcrt.FailureMessage("请仔细阅读说明！")
                print()

        workernode(mode, cc, target, count, delay, max_threads)
    except KeyboardInterrupt:
        mesgdcrt.WarningMessage("收到中断信号 - 正在退出...")
        sys.exit()


mesgdcrt = MessageDecorator("icon")
if sys.version_info[0] != 3:
    mesgdcrt.FailureMessage("SMSBOMBING只能在Python v3中运行")
    sys.exit()

try:
    country_codes = readisdc()["isdcodes"]
except FileNotFoundError:
    update()


__VERSION__ = get_version()
__CONTRIBUTORS__ = ['Ravi Sharma']

ALL_COLORS = [Fore.GREEN, Fore.RED, Fore.YELLOW, Fore.BLUE,
              Fore.MAGENTA, Fore.CYAN, Fore.WHITE]
RESET_ALL = Style.RESET_ALL

ASCII_MODE = False
DEBUG_MODE = False

description = """SMSBOMBING - 你的友好垃圾邮件应用程序
SMSBOMBING可用于许多目的，包括 -
\t 暴露互联网上的易受攻击的API
\t 友好的垃圾邮件发送
\t 测试你的垃圾邮件检测器等等
SMSBOMBING不适用于恶意用途。
"""

parser = argparse.ArgumentParser(description=description,
                                 epilog='由Ravi Sharma编码！')
parser.add_argument("-sms", "--sms", action="store_true",
                    help="以短信轰炸模式启动SMSBOMBING")
parser.add_argument("-call", "--call", action="store_true",
                    help="以电话轰炸模式启动SMSBOMBING")
parser.add_argument("-mail", "--mail", action="store_true",
                    help="以邮件轰炸模式启动SMSBOMBING")
parser.add_argument("-ascii", "--ascii", action="store_true",
                    help="仅显示标准ASCII字符")
parser.add_argument("-u", "--update", action="store_true",
                    help="更新SMSBOMBING")
parser.add_argument("-c", "--contributors", action="store_true",
                    help="显示当前SMSBOMBING贡献者")
parser.add_argument("-v", "--version", action="store_true",
                    help="显示当前SMSBOMBING版本")


if __name__ == "__main__":
    args = parser.parse_args()
    if args.ascii:
        ASCII_MODE = True
        mesgdcrt = MessageDecorator("stat")
    if args.version:
        print("版本: ", __VERSION__)
    elif args.contributors:
        print("贡献者: ", " ".join(__CONTRIBUTORS__))
    elif args.update:
        update()
    elif args.mail:
        selectnode(mode="mail")
    elif args.call:
        selectnode(mode="call")
    elif args.sms:
        selectnode(mode="sms")
    else:
        choice = ""
        avail_choice = {
            "1": "短信",
            "2": "电话",
            "3": "邮件"
        }
        try:
            while (choice not in avail_choice):
                clr()
                bann_text()
                print("可用选项:\n")
                for key, value in avail_choice.items():
                    print("[ {key} ] {value} 轰炸".format(key=key,
                                                          value=value))
                print()
                choice = input(mesgdcrt.CommandMessage("输入选择: "))
            selectnode(mode=avail_choice[choice].lower())
        except KeyboardInterrupt:
            mesgdcrt.WarningMessage("收到中断信号 - 正在退出...")
            sys.exit()
    sys.exit()
