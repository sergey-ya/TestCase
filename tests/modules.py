#!/usr/bin/python
# coding: utf_8


from datetime import datetime, timedelta
from subprocess import Popen, PIPE, check_output
from timeit import default_timer as timer
import sys, getopt, datetime
import os, shutil, pwd
from threading import Thread
import json
import time

import re

startTime = None

clStandart = '\033[0m'
clRed = '\033[91m'
clYellow = '\033[93m'
clGreen = '\033[92m'

configFile = os.path.join(os.getcwd(), 'conffile')
logFile = os.path.join(os.getcwd(), 'logfile')
errFile = os.path.join(os.getcwd(), 'logerror')
pidfile = "/tmp/launch.pid"


reload(sys)
sys.setdefaultencoding('utf8')


# **********************************************************************************************************************
# BASE
# **********************************************************************************************************************
def runCmd(cmd=None, showOutput=False):
    #
    if showOutput:
        proc = Popen(cmd, shell=True)
    else:
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    output, error = proc.communicate()
    return dict(output=output, error=error, code=proc.returncode)


def checkOS():
    #
    res = runCmd('lsb_release -i')['output']
    if not 'RED SOFT' in res and not 'GosLinux' in res:
        showError(u'Ваша ОС не является разработкой компании РЕД СОФТ')
        showMsg(u'Тестирование невозможно\n')
        return False
    else:
        showTextCenter('%s' % getOSName())
        return True


def getOSName():
    #
    desc = runCmd('lsb_release -d')['output'].rstrip()
    return desc[13: len(desc)]


def getRunStage2():
    while True:
        status = raw_input("\n Предыдущее тестирование - не завершено, продолжить его? (y/n): ")
        if status == 'y':
            return True
        elif status == 'n':
            os.remove(logFile)
            return False


def getRebootOS():
    while True:
        showMsg(u"\nДля продолжения тестирования необходимо перезагрузить систему.")
        status = raw_input(" Произвести перезагрузку сейчас? (y/n): ")
        if status == 'y':
            return True
        elif status == 'n':
            return False



# **********************************************************************************************************************
# CHECKING CONFIG SYSTEM AND RUNNING COPIES
# **********************************************************************************************************************
def runSettingConfigOS(instParamiko=True, remGssapi=True, stopFileprotect=True, runSELinux=True):
    #
    if runSELinux:
        sys.stdout.write(u' - запуск SELinux\t\t\t')
        sys.stdout.flush()

        if runCmd('getenforce')['output'].rstrip() == 'Permissive':
            if runCmd('setenforce 1')['code'] == 0:
                showSuccess(u'[ok]')
            else:
                showError(u'[error]')
                return False
        else:
            showError(u'[error]')
            return False

    if stopFileprotect:
        sys.stdout.write(u' - останановка сервиса fileprotect\t')
        sys.stdout.flush()

        if runCmd('systemctl stop fileprotect')['code'] != 0:
            showError(u'[error]')
            return False
        else:
            showSuccess(u'[ok]')

    if instParamiko:
        sys.stdout.write(u' - установка пакета python paramiko\t')
        sys.stdout.flush()

        if runCmd('rpm -qi python2-pip')['code'] != 0:
            if runCmd('yum install python2-pip -y')['code'] != 0:
                showError(u'[error]')
                return False

        # if runCmd('pip install paramiko')['code'] != 0:
        if runCmd('pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org paramiko')['code'] != 0:
            showError(u'[error]')
            return False
        else:
            showSuccess(u'[ok]')

    if remGssapi:
        sys.stdout.write(u' - удаление пакета python-gssapi\t')
        sys.stdout.flush()

        if runCmd('yum remove python-gssapi -y')['code'] != 0:
            showError(u'[error]')
            return False
        else:
            showSuccess(u'[ok]')

    return True


def checkConfigOS():
    #
    runSELinux = True
    stopFileprotect = True

    installParamiko = True

    removeGssapi = True

    showMsg(' ')
    showTextCenter(u'\n\nПроверка конфигурации системы', '-')

    if runCmd('getenforce')['output'].rstrip() == 'Enforcing':
        runSELinux = False


    if runCmd('systemctl status fileprotect')['code'] != 0:
        stopFileprotect = False


    if runCmd('rpm -qi python2-pip')['code'] == 0:
        if runCmd('pip list | grep paramiko')['code'] == 0:
            installParamiko = False


    if runCmd('rpm -qi python-gssapi')['code'] != 0:
        removeGssapi = False


    if runSELinux or stopFileprotect or installParamiko or removeGssapi:
        while True:
            sys.stdout.write(u'\r Для запуска тестирования необходимо настроить систему.\n')
            if runSELinux:
                showMsg(u'- запустить SELinux')

            if stopFileprotect:
                showMsg(u'- остановить сервис fileprotect')

            if installParamiko:
                showMsg(u'- установить пакет python paramiko')

            if removeGssapi:
                showMsg(u'- удалить пакет gssapi')

            setup = raw_input('\n Настроить систему в автоматическом режиме? (y/n): ')

            if setup == 'y':
                res = runSettingConfigOS(instParamiko=installParamiko, remGssapi=removeGssapi,
                                          stopFileprotect=stopFileprotect, runSELinux=runSELinux)

            elif setup == 'n':
                res = False

            # showTextCenter('-\n', '-')
            return res

    else:
        showMsg('OK')
        # showTextCenter('-\n', '-')
        return True



def checkCopies():

    def check_pid(pid):
        try:
          os.kill(pid, 0)
        except OSError:
          return False
        else:
          return True

    pid = None

    if os.path.isfile(pidfile):
        pid = long(open(pidfile, 'r').read())

    if pid and check_pid(pid):
        return False

    pid = str(os.getpid())
    file(pidfile, 'w').write(pid)
    return True

def uncheckCopies():
    os.unlink(pidfile)


# **********************************************************************************************************************
# WORK WITH PARAMETERS / CONFIG FILE
# **********************************************************************************************************************
def getConfigParam(param=None):
    #
    if not os.path.isfile(configFile):
        return False
    else:
        file = open(configFile, 'r')
        data = json.loads(file.read())
        file.close()

        try:
            return str(data[param])
        except:
            return False


def getConfigParams(params=None):
    # getting params from config file
    if not os.path.isfile(configFile):
        return {}
    else:
        res = {}
        file = open(configFile, 'r')
        data = json.loads(file.read())
        file.close()

        for param in params:
            if param in data.keys():
                res.update({param: str(data.get(param))})

        return res


def updateConfigParam(param=None):
    # add param in config file
    if not os.path.isfile(configFile):
        file = open(configFile, 'w')
        file.write(json.dumps(param))
        file.close()
        return True
    else:
        file = open(configFile, 'r')
        data = json.loads(file.read())
        file.close()

        if data.update(param) == None:
            file = open(configFile, 'w')
            file.write(json.dumps(data))
            file.close()
            return True

    return False


# проверить
def checkParams(params=None, stage=0):

    def createUser():
        def checkUserName(userName=None):
            for p in pwd.getpwall():
                if userName == p[0]:
                    return True
            return False

        def generateUserName():
            ind = 1
            while True:
                userName = 'user' + str(ind)
                if not checkUserName(userName):
                    return userName
                ind += 1

        def userAdd():
            userName = generateUserName()
            if runCmd('useradd %s' % userName)['code'] != 0 or \
                    runCmd('echo -e "qqqwww\nqqqwww\n" | passwd %s' % userName)['code'] != 0:
                return None
            return userName

        return userAdd()

    def checkUser(name=None):
        for p in pwd.getpwall():
            if userName == p[0]:
                return True
        return False


    def checkUsb(dev=None):
        # ПРОВЕРИТЬ РАБОТОСПОСОБНОСТЬ и возможно переписать
        for elem in runBashFromRoot("lsusb | awk '{print $6}'")['output'].rstrip().split('\n'):
            res = elem.split(':')
            if runBashFromRoot('smartctl -a %s | grep "%s.*%s"' % (dev[0: len(dev) - 1], res[0], res[1]))['code'] == 0:
                return True
        return False


    def checkExt4(dev=None):
        out = runBashFromRoot("blkid %s -s TYPE" % dev)['output']
        if out.rstrip() == '%s: TYPE="ext4"' % dev:
            return True
        else:
            return False


    def checkSSH(host=None, user=None, passwd=None, root=True):
        try:
            import paramiko
            sshClient = paramiko.SSHClient()
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.connect(hostname=host, username=user, password=passwd, port=22)

            stdin, stdout, stderr = sshClient.exec_command("id -un")
            output = stdout.read().rstrip()

            sshClient.close()

            if root:
                if 'root' in output:
                    return True
                else:
                    showError(u'Пользователь должен иметь root права')
                    return False
            else:
                return True

        except Exception as e:
            if e.__class__.__name__ == 'NoValidConnectionsError':
                pass
            elif e.__class__.__name__ == 'AuthenticationException':
                showError(u'Некорректно введены данные для авторизацции')
            else:
                showError(u'Ошибка соединения')
            return False


    def pingHost(host=None):

        if runBashFromRoot("ping %s -c1" % host)['code'] == 0:
            return True
        else:
            return False



    if params != []:

        showMsg(' ')
        showTextCenter(u'\n Проверка параметров ', '-')

        updateConfigParam(dict(testDir='/tmp/test_test'))

        if stage == 0:
            if 'firstUserName' in params:
                userName = createUser()
                if userName == None or not updateConfigParam(dict(firstUserName=userName)) \
                        or not updateConfigParam(dict(firstUserPass='qqqwww')):
                    raise Exception(u' Ошибка при создании первого пользователя')
                showMsg(u'Первый пользователь (создан автоматически): %s' % userName)

            if 'secondUserName' in params:
                userName = createUser()
                if userName == None or not updateConfigParam(dict(secondUserName=userName)) \
                        or not updateConfigParam(dict(secondUserPass='qqqwww')):
                    raise Exception(u' Ошибка при создании второго пользователя')
                showMsg(u'Второй пользователь (создан автоматически): %s' % userName)

            if 'mntDevice' in params:

                mntDevice = getConfigParam('mntDevice')

                if not mntDevice or not checkExt4(mntDevice) or not checkUsb(mntDevice):
                    while True:
                        mntDevice = raw_input("\n Внешний накопитель (имя раздела): ")
                        if runBashFromRoot('ls %s' % mntDevice)['code'] != 0:
                            showError(u'Раздел не найден')
                        else:
                            if not checkUsb(mntDevice):
                                showError(u'Раздел должен находиться на USB устройстве')
                            else:
                                if not checkExt4(mntDevice):
                                    showError(u'Внешний накопитель должен иметь формат ext4')
                                else:
                                    updateConfigParam(dict(mntDevice=mntDevice))
                                    break
                else:
                    showMsg(u'Внешний накопитель: %s' % mntDevice)

                mountPoint = runCmd(cmd="lsblk %s -n --output MOUNTPOINT" % mntDevice)['output'].rstrip()
                updateConfigParam(dict(mntPoint=mountPoint))
                if mountPoint != '':
                    runCmd(cmd="umount %s" % mntDevice)
                    time.sleep(3)
                    if os.path.exists(mountPoint):
                        os.rmdir(mountPoint)
                    showMsg(u'Точка монтирования внешнего накопителя: %s' % mountPoint)

            if 'sshHostName' in params:
                host = check_output(['hostname', '--all-ip-addresses']).rstrip()

                sshHost = getConfigParam('sshHostName')
                sshUser = getConfigParam('sshUserName')
                sshPass = getConfigParam('sshPasswd')

                if sshHost == False or not checkSSH(host=sshHost, user=sshUser, passwd=sshPass):
                    while True:
                        sshHost = raw_input("\n IP адрес первой удаленной машины: ")
                        if sshHost:
                            if not sshHost in host:
                                if pingHost(sshHost):
                                    sshUser = raw_input(" Имя root пользователя удаленной машины: ")
                                    if sshUser:
                                        while True:
                                            sshPass = raw_input(" Пароль root пользователя удаленной машины: ")
                                            if sshPass: break

                                        if checkSSH(host=sshHost, user=sshUser, passwd=sshPass):
                                            updateConfigParam(dict(sshHostName=sshHost))
                                            updateConfigParam(dict(sshUserName=sshUser))
                                            updateConfigParam(dict(sshPasswd=sshPass))
                                            break
                                else:
                                    showError(u'IP адрес не доступен или введен некорректно')
                            else:
                                showError(u'IP адрес не должен совпадать с IP адресом тестируемой машины')

                else:
                    showMsg(u'Первая удаленная машина: %s/%s/%s' % (sshHost, sshUser, sshPass))


            if 'sshHostName2' in params:
                host = check_output(['hostname', '--all-ip-addresses']).rstrip()
                host2 = getConfigParam('sshHostName')

                sshHost2 = getConfigParam('sshHostName2')
                sshUser2 = getConfigParam('sshUserName2')
                sshPass2 = getConfigParam('sshPasswd2')

                if sshHost2 == False or not checkSSH(host=sshHost2, user=sshUser2, passwd=sshPass2, root=False):
                    while True:
                        sshHost2 = raw_input("\n IP адрес второй удаленной машины: ")
                        if sshHost2:
                            if not sshHost2 in host:
                                if sshHost2 != host2:
                                    if pingHost(sshHost2):
                                        sshUser2 = raw_input(" Имя пользователя удаленной машины: ")
                                        if sshUser2:
                                            while True:
                                                sshPass2 = raw_input(" Пароль пользователя удаленной машины: ")
                                                if sshPass2: break

                                            if checkSSH(host=sshHost2, user=sshUser2, passwd=sshPass2, root=False):
                                                updateConfigParam(dict(sshHostName2=sshHost2))
                                                updateConfigParam(dict(sshUserName2=sshUser2))
                                                updateConfigParam(dict(sshPasswd2=sshPass2))
                                                break

                                    else:
                                        showError(u'IP адрес не доступен или введен некорректно')
                                else:
                                    showError(u'IP адрес не должен совпадать с IP адресом первой удаленной машины')
                            else:
                                showError(u'IP адрес не должен совпадать с IP адресом тестируемой машины')

                else:
                    showMsg(u'Вторая удаленная машина: %s/%s/%s' % (sshHost2, sshUser2, sshPass2))


                # while True:
                #     sshUser2 = raw_input(" Продолжить? (y/n): ")
                #     if sshUser2:
                #         while True:
                #             sshPass2 = raw_input(" Пароль пользователя удаленной машины: ")
                #             if sshPass2: break
                #
                #         if checkSSH(host=sshHost2, user=sshUser2, passwd=sshPass2, root=False):
                #             updateConfigParam(dict(sshHostName2=sshHost2))
                #             updateConfigParam(dict(sshUserName2=sshUser2))
                #             updateConfigParam(dict(sshPasswd2=sshPass2))
                #             break


        elif stage == 1:
            if 'firstUserName' in params:
                userName = getConfigParam('firstUserName')

                if not checkUser(userName):
                    userName = createUser()
                    if userName == None or not updateConfigParam(dict(firstUserName=userName)) \
                            or not updateConfigParam(dict(firstUserPass='qqqwww')):
                        raise Exception(u' Ошибка при создании первого пользователя')
                    showMsg(u'Первый пользователь (создан автоматически): %s' % userName)
            # else:

        # showTextCenter('-\n', '-')



def uncheckParams(params=None):

    def delUser(name=None):
        try:
            if runCmd('userdel -r %s' % name)['code'] != 0:
                return False
            return True
        except:
            return False

    if params != []:

        showMsg(' ')
        showTextCenter(u'\n Откат параметров ', '-')

        if 'firstUserName' in params:
            userName = getConfigParam('firstUserName')
            if not delUser(userName):
                showError(u'Ошибка при удалении первого пользователя "%s"' % str(userName))
            else:
                showMsg(u'Первый пользователь "%s" успешно удален' % str(userName))

        if 'secondUserName' in params:
            userName = getConfigParam('secondUserName')
            if not delUser(userName):
                showError(u'Ошибка при удалении второго пользователя "%s"' % str(userName))
            else:
                showMsg(u'Второй пользователь "%s" успешно удален' % str(userName))

        if 'mntDevice' in params:
            mntDevice = getConfigParam('mntDevice')
            mntPoint = getConfigParam('mntPoint')
            if mntPoint != '':
                try:
                    os.mkdir(mntPoint)
                    res = runCmd(cmd="mount %s %s" % (mntDevice, mntPoint))
                    time.sleep(3)
                    if res['code'] == 0:
                        showMsg(u'Внешний накопитель %s примонтирован' % mntDevice)
                    else:
                        showError(u'Не удалось примонтировать внешний накопитель в "%s"' % mntPoint)
                except:
                    showError(u'Не удалось примонтировать внешний накопитель в "%s"' % mntPoint)
            else:
                showMsg(u'Устройство не было примонтировано')

        showMsg(' ')



# **********************************************************************************************************************
# LOG FILE
# **********************************************************************************************************************
def writeToLog(type=None, data=None):

    global startTime
    actTime = None

    if not startTime:
        startTime = timer()


    if type == 'start_testing':
        file = open(logFile, "w")
        actTime = startTime
        content = '[START TESTING OS] data:%s' % json.dumps(data)
        file.write('host: %s, date: %s\n' % ('host', runCmd(cmd='date')['output']))


    else:

        file = open(logFile, "a")
        if type == 'start_test':
            actTime = startTime
            content = '[START TEST] number:%s' % data['num']

        elif type == 'end_test':
            actTime = timer() - startTime
            content = '[END TEST] data:%s' % json.dumps(data)


        elif type == 'run_cmd':
            actTime = timer() - startTime
            data['cmd'] = data['cmd'].replace('\n', '\\n')
            content = '[run cmd] user:%s, cmd:%s, code:%s' % (data['user'], data['cmd'], data['code'])

        elif type == 'end_cmd':
            actTime = timer() - startTime
            content = '[end cmd] code:%s, pid:%s' % (data['code'], data['pid'])

        elif type == 'start_stage1':
            actTime = startTime
            content = '[START STAGE1]'

        elif type == 'end_stage1':
            actTime = timer() - startTime
            content = '[END STAGE1]'
            file.write('\nhost: %s, date: %s\n' % ('host', runCmd(cmd='date')['output']))


        elif type == 'start_stage2':
            actTime = startTime
            content = '[START STAGE2]'

        elif type == 'end_stage2':
            actTime = timer() - startTime
            content = '[END STAGE2]'

        elif type == 'end_testing':
            actTime = timer() - startTime
            content = '[END TESTING OS]'
            file.write('\nhost: %s, date: %s\n' % ('host', runCmd(cmd='date')['output']))


    file.write('%s %s\n' % (actTime, content))
    file.close()









def getStage():
    if not os.path.isfile(logFile):
        return 0

    file = open(logFile, "r")
    lines = file.readlines()
    file.close()

    for test in scanLogFile():
        if test['status'] == 3:
            res = lines[len(lines) - 1]
            if res.find('[END TESTING OS]') == -1:
                return 1
            else:
                return 0
    return 0



def getTestingData():
    if not os.path.isfile(logFile):
        return False

    file = open(logFile, "r")
    lines = file.readlines()
    file.close()

    res = lines[0].rstrip()
    return json.loads(res[res.find('data:')+5:])




def scanLogFile():
    file = open(logFile, "r")
    lines = file.readlines()
    file.close()

    res = []
    for line in lines:
        if '[END TEST]' in line:
            r = line.rstrip()
            res.append(json.loads(r[r.find('data:')+5: len(r)]))

    return res


def getTestingInformation():
    pass



# **********************************************************************************************************************
# ERROR LOG FILE
# **********************************************************************************************************************
def delErrorLog():
    # delete error log file
    if os.path.isfile(errFile):
        os.remove(errFile)
    return True


def checkErrorLog():
    # checking error log file
    return True if os.path.isfile(errFile) else False


def writeToErrorLog(type=None, data=None):
    # write record to error log file
    if not os.path.isfile(errFile):
        file = open(errFile, 'w')
        file.close()

    file = open(errFile, 'a')

    if type == 'ec':
        file.write('[ERROR INFO - CODE - TEST %s]\n' % data['testNum'])
        file.write('user: %s\n' % data['user'])
        data['cmd'] = data['cmd'].replace('\n', '\\n')
        file.write('cmd: %s\n' % data['cmd'])
        file.write('wait code: %s\n' % data['code'])
        file.write('res code: %s\n' % data['rescode'])
        file.write('res output: %s\n' % data['output'])
        file.write('res error: %s\n' % data['error'])

    elif type == 'er':
        file.write('[ERROR INFO - RESULT - TEST %s]\n' % data['testNum'])
        file.write('user: %s\n' % data['user'])
        data['cmd'] = data['cmd'].replace('\n', '\\n')
        file.write('cmd: %s\n' % data['cmd'])
        file.write('msg: %s\n' % data['msg'])
        file.write('wait: %s\n' % data['wait'])
        file.write('taken: %s\n' % data['taken'])

    elif type == 'ee':
        file.write('[ERROR INFO - EXCEPTION - TEST %s]\n' % data['testNum'])
        file.write('exception: %s\n' % data['error'])

    file.write('[END ERROR INFORMATION]\n\n')

    file.close()


def outErrorLog():
    # out error log file
    if os.path.isfile(errFile):
        file = open(errFile, 'r')
        lines = file.readlines()
        file.close()
        for line in lines:
            print(line.rstrip())
    else:
        showError(u'Не найден лог с ошибками')



# **********************************************************************************************************************
# FORMAT SHOW CONTENT
# **********************************************************************************************************************
def getWidthLine():
    #
    rows, columns = os.popen('stty size', 'r').read().split()
    res = int(columns)
    if res > 120:
        return 120
    else:
        return res


def showMsg(text=None):
    #
    if text[0] == '\n':
        text = text.lstrip('\n')
        print('\n')

    print(' {text}'.format(text=text))


def showError(text=None, showHelp=False):
    #
    print('{color} {text}{endcolor}'.format(color=clRed, text=text, endcolor=clStandart))

    if showHelp:
        showMsg(u'Для просмотра справки используйте ключ -h или --help\n')


def showSuccess(text=None):
    #
    print('{color} {text}{endcolor}'.format(color=clGreen, text=text, endcolor=clStandart))


def showTextCenter(text=None, marker=' '):
    if text.startswith('\n'):
        text = text.lstrip('\n')
        showMsg(' ')

    if text.endswith('\n'):
        text = text.rstrip('\n')
        print(text.center(getWidthLine(), marker))
        showMsg(' ')
    else:
        print(text.center(getWidthLine(), marker))


def showTextCol(text=None):

    width = getWidthLine()
    widthCol2 = width - 14

    if len(text) == 1:
        print(" {text:<{width}}".format(text=text[0], width=width - 1))

    if len(text) == 2:
        print(" {text1:<10}{text2:<{width}}".format(text1=text[0], text2=text[1], width=width - 11))

    if len(text) == 3:
        text[1] = text[1].replace('\n', ' ')
        if len(text[1]) > widthCol2:
            text[1] = text[1][:widthCol2 - 4] + '... '
        print(" {text1:<10}{text2:<{width}}{text3:<3}".format(text1=text[0], text2=text[1], text3=text[2], width=widthCol2))



def showTestName(num=None, name=None):
    #
    num = str(num)
    text = ' ' + num + '. ' + name
    sys.stdout.write(text)
    sys.stdout.flush()
    return len(text)


def showTestRes(res=None, ln=None, cl=None):
    #
    lin = '.' * (getWidthLine() - ln - len(res) - 1)
    sys.stdout.write(lin + '{cl}{text}{endcl}\n'.format(cl=cl, text=res, endcl=clStandart))
    sys.stdout.flush()


def showRunCmd(text=None):

    widthCol2 = getWidthLine() - 14

    text[1] = text[1].replace('\n', '\\n').decode('utf8')
    if len(text[1]) > widthCol2:
        text[1] = text[1][:widthCol2 - 4] + '... '

    sys.stdout.write(" {user:<10}{cmd:<{width}}".format(user=text[0], cmd=text[1], width=widthCol2))
    sys.stdout.flush()


def showRunCmdRes(res=None):
    sys.stdout.write('%s\n' % res)
    sys.stdout.flush()












# **********************************************************************************************************************
#
# **********************************************************************************************************************


















# получить параметры запуска вторго этапа
def getLaunchParams():

    def getParamsFromLogFile():
        file = open(logFile, "r+")
        rows = file.readlines()
        file.close()

        res = {}
        tst = []
        for row in rows:
            if row.find('debug') != -1:
                if row.find('True') != -1:
                    res.update(dict(debug=True))
                elif row.find('False') != -1:
                    res.update(dict(debug=False))

            pos1 = row.find('test')
            pos2 = row.find('status')
            if pos1 != -1 and pos2 != -1:
                s = row.rstrip()
                number = int(s[pos1 + 6: pos2 - 1])
                status = int(s[pos2 + 8: pos2 + 8 + 1])
                tst.append(dict(number=number, status=status))
        res.update(dict(tests=tst))
        return res

    res = {}
    if not os.path.isfile(logFile):
        res.update(dict(stage=1))
        return res
    else:
        file = open(logFile, "r+a")
        data = file.readlines()
        file.close()

        # if data[0].rstrip() == 'stage1' or data[0].rstrip() == 'stage0':
        #     res.update(dict(stage=1))
        #     return res

        if data[0].rstrip() == 'stage2':
            res.update(dict(stage=2))
            res.update(getParamsFromLogFile())
            return res


# получить статус запуска тестирования
def getStatusRunTest():
    if not os.path.isfile(logFile):
        file = open(logFile, "w")
        file.close()
        return 'new'
    else:
        file = open(logFile, "r+a")
        data = file.readlines()
        file.close()

        if data[0].rstrip() == 'new' or data[0].rstrip() == 'end':
            return 'new'

        if data[0].rstrip() == 'continue':
            return 'continue'


# очистить лог файл
def clearLogFile():
    file = open(logFile, "w")
    file.write('new\n')
    file.close()


# выбираем из лог файла тесты и их состояния
def parseLogFile():
    file = open(logFile, "r+")
    rows = file.readlines()
    file.close()

    res = []
    for row in rows:
        pos1 = row.find('test')
        pos2 = row.find('status')
        if pos1 != -1 and pos2 != -1:
            s = row.rstrip()
            number = int(s[pos1 + 6: pos2 - 1])
            status = int(s[pos2 + 8: pos2 + 8 + 1])
            res.append(dict(number=number, status=status))
    return res


# устанавливает статус continue
def setContinueLogFile(params={}):
    file = open(logFile, 'r')
    text = file.readlines()
    file.close()

    text[0] = 'continue\n'
    text[4] = json.dumps(params) + '\n'

    file = open(logFile, 'w')
    for row in text:
        file.write(row)

    file.close()


# устанавливает статус end
def setEndLogFile():
    file = open(logFile, 'r')
    text = file.readlines()
    file.close()

    text[0] = 'end\n'

    file = open(logFile, 'w')
    for row in text:
        file.write(row)

    file.close()





# получить состояние debug
def getDebugLogFile():
    file = open(logFile, "r+a")
    data = file.readlines()
    file.close()

    if data[3].rstrip() == 'debug: True':
        return True
    elif data[3].rstrip() == 'debug: False':
        return False


# получить дополнительные параметры
def getAddParams():
    f = open(logFile, "r+")
    rows = f.readlines()
    f.close()

    return json.loads(rows[4])


















# замена строки в файле
def changeRowFile(path=None, oldRow=None, newRow=None, start=False):
    # чтобы возвращал результат выполнения false в случае провала
    f = open(path, "r+")
    rows = f.readlines()
    f.seek(0)
    for row in rows:
        if start:
            if row.rstrip().find(oldRow) == 0:
                f.write(newRow + '\n')
            else:
                f.write(row)
        else:
            if row.rstrip().find(oldRow) != -1:
                f.write(newRow + '\n')
            else:
                f.write(row)

    f.truncate()
    f.close()


#  добавление строки в файл
def addRowFile(path=None, oldRow=None, newRow=None):
    f = open(path, "r+")
    rows = f.readlines()
    f.seek(0)
    for row in rows:
        f.write(row)
        if row.rstrip() == oldRow:
            f.write(newRow + '\n')

    f.truncate()
    f.close()

# добавление строк в конец файла
def addRowToFile(file=None, text=None):
    f = open(file, "a")
    for row in text:
        f.write(row + '\n')
    f.close()


# создание файла с текстом
def createFile(path=None, text=None):
    f = open(path, "w")
    for row in text:
        f.write(row + '\n')
    f.close()


def runBashFromRoot(cmd=None):
        proc = Popen("sudo -S " + cmd, stdout=PIPE, stderr=PIPE, shell=True)
        output, error = proc.communicate()
        return {'output': output, 'error': error, 'code': proc.returncode}





# **********************************************************************************************************************
# EDITING FILE
# **********************************************************************************************************************
# замена строки в файле
def addRowToFile2(path=None, searchRow=None, addRow=None):
    # добавление строки в файл
    # поиск строки содержащей searchRow, в случае успеха добавляет строку после
    # если searchRow=None то строка добавляется в конец файла
    pass
    # f = open(path, "r+")
    # rows = f.readlines()
    # f.seek(0)
    # for row in rows:
    #     if row.rstrip().find(oldRow) != -1:
    #
    #     if start:
    #         if row.rstrip().find(oldRow) == 0:
    #             f.write(newRow + '\n')
    #         else:
    #             f.write(row)
    #     else:
    #         if row.rstrip().find(oldRow) != -1:
    #             f.write(newRow + '\n')
    #         else:
    #             f.write(row)
    #
    # f.truncate()
    # f.close()









































# **********************************************************************************************************************
# TESTING
# **********************************************************************************************************************
class runTest(object):

    osf = None
    name = None
    osfNum = None
    num = None
    stages = None
    params = None

    sshClient = None
    sshHostName = None
    sshUserName = None

    packages = []
    sshPackages = []

    sshServices = []

    mountPoint = False

    result = []
    removResult = []
    errorResult = []

    runCmdInfo = {}

    fatalError = False

    statusNtpd = None
    actualTime = None
    currentTime = None

    sshStatusNtpd = None
    sshActualTime = None
    sshCurrentTime = None


    # ЗАПУСК КОМАНД-----------------------------------------------------------------------------------------------------
    # запуск и анализ команд
    def runCmd(self, ssh=False, user='root', cmd=None, code=None, remov=False):

        try:
            if ssh:
                if code != None:
                    showRunCmd([self.sshUserName, '%s: %s' % (self.sshHostName, cmd)])
                writeToLog(type='run_cmd', data=dict(user=self.sshUserName, cmd='%s: %s' % (self.sshHostName, cmd), code=code))
            else:
                if code != None:
                    showRunCmd([user, cmd])
                writeToLog(type='run_cmd', data=dict(user=user, cmd=cmd, code=code))


            if not ssh:
                if user == 'root':
                    cmd1 = "sudo -S " + cmd
                else:
                    cmd1 = "su -l " + user + " -c '" + cmd + "'"

                proc = Popen(cmd1, stdout=PIPE, stderr=PIPE, shell=True)
                output, error = proc.communicate()
                output = output.rstrip()
                error = error.rstrip()
                returnCode = proc.returncode
                pid = proc.pid

            else:
                stdin, stdout, stderr = self.sshClient.exec_command(cmd)
                output = stdout.read().rstrip()
                error = stderr.read().rstrip()
                returnCode = stdout.channel.recv_exit_status()
                pid = None
                user = '%s' % self.sshUserName
                cmd = '%s: %s' % (self.sshHostName, cmd)

            writeToLog(type='end_cmd', data=dict(code=code, pid=pid))

            if code != None:
                if returnCode == code:
                    showRunCmdRes('ok')
                else:
                    showRunCmdRes('no')


                    writeToErrorLog(type='ec', data=dict(testNum=self.num, user=user, cmd=cmd, code=code, rescode=returnCode,
                                                       output=output, error=error))

                    if remov:
                        self.removResult.append(dict(user=user, cmd=cmd, output=output, error=error, wait=code,
                                                     taken=returnCode))
                    else:
                        self.result.append(dict(type='code', user=user, cmd=cmd, output=output, error=error,
                                                wait=code, taken=returnCode))
                        raise Exception('err')


            self.runCmdInfo = dict(user=user, cmd=cmd)
            return {'output': output, 'error': error, 'code': returnCode, 'pid': pid}

        except Exception as e:
            raise Exception(e.message)





    # запуск команд от root
    def runCmdFromRoot(self, cmd=None, code=None, remov=False):
        return self.runCmd(cmd=cmd, code=code, remov=remov)

    # запуск команд от пользователя
    def runCmdFromUser(self, user=None, cmd=None, code=None):
        return self.runCmd(user=user, cmd=cmd, code=code)

    # запуск команд от первого пользователя
    def runCmdFirstUser(self, cmd=None, code=None):
        return self.runCmd(user=self.params['firstUserName'], cmd=cmd, code=code)

    # запуск команд от второго пользователя
    def runCmdSecondUser(self, cmd=None, code=None):
        return self.runCmd(user=self.params['secondUserName'], cmd=cmd, code=code)


    # РАБОТА ПО SSH-----------------------------------------------------------------------------------------------------
    # создание ssh соединения
    def sshConnect(self, host=None, user=None, passwd=None, port=22):
        import paramiko
        self.sshClient = paramiko.SSHClient()
        self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sshHostName = host
        self.sshUserName = user
        self.sshClient.connect(hostname=host, username=user, password=passwd, port=port)

    # выполнение команд по ssh
    def sshRunCmd(self, cmd=None, code=None, remov=False):
        return self.runCmd(ssh=True, cmd=cmd, code=code, remov=remov)

    # закрытие ssh соединения
    def sshDisconnect(self):
        self.sshClient.close()

    # создание копии файла на удаленной машине
    def sshCreateCopyFile(self, fileName=None):
        return self.runCmd(ssh=True, cmd="cp %s %s2" % (fileName, fileName), code=0)

    def sshExchangeCopyFile(self, fileName=None):
        self.runCmd(ssh=True, cmd='cp %s2 %s' % (fileName, fileName), code=0, remov=True)
        self.runCmd(ssh=True, cmd='rm %s2' % fileName, code=0, remov=True)



    def sshInstallPack(self, name=None):
        if self.runCmd(ssh=True, cmd="rpm -qi %s" % name)['code'] == 0:
            self.sshPackages.append(name)
        else:
            self.runCmd(ssh=True, cmd="yum install %s -y" % name, code=0)

    def sshUninstallPack(self, name=None):
        if name in self.sshPackages:
            self.sshPackages.remove(name)
        else:
            self.runCmd(ssh=True, cmd="yum remove %s -y" % name, code=0, remov=True)

    # работа со временем
    def sshRestartNtpd(self):
        self.runCmd(ssh=True, cmd='systemctl restart ntpd', code=0)
        while True:
            curr = self.runCmd(ssh=True, cmd='date +"%Y-%m-%d %H:%M:%S"', code=0)['output']
            datetime_object = datetime.datetime.strptime(curr, "%Y-%m-%d %H:%M:%S")
            res = self.runCmd(ssh=True, cmd='ntpstat')['code']
            if res == 1:
                time.sleep(2)
                break
        return datetime_object


    def sshTimeStart(self):
        if 'yes' in self.runCmd(ssh=True, cmd='timedatectl status | grep "NTP synchronized"')['output']:
            self.sshStatusNtpd = True
        else:
            self.sshStatusNtpd = False

        if not self.sshStatusNtpd:
            self.sshCurrentTime = self.sshRestartNtpd()

        curr = self.runCmd(ssh=True, cmd='date +"%Y-%m-%d %H:%M:%S"', code=0)['output']
        self.sshActualTime = datetime.datetime.strptime(curr, "%Y-%m-%d %H:%M:%S")


    def sshTimeEnd(self):
        self.sshRestartNtpd()
        if not self.sshStatusNtpd:
            curr = self.runCmd(ssh=True, cmd='date +"%Y-%m-%d %H:%M:%S"', code=0, remov=True)['output']
            sshActualTimeEnd = datetime.datetime.strptime(curr, "%Y-%m-%d %H:%M:%S")
            duration = sshActualTimeEnd - self.sshActualTime
            now3 = self.sshCurrentTime + timedelta(seconds=duration.total_seconds())
            self.runCmd(ssh=True, cmd='date -s "%s"' % datetime.datetime.strftime(now3, "%b %-d %Y %H:%M:%S"),
                        code=0, remov=True)
            self.runCmd(ssh=True, cmd='systemctl stop ntpd', code=0, remov=True)

    # запуск или остановка сервиса
    def sshActionService(self, name=None, action=None):
        state = self.runCmd(ssh=True, cmd='systemctl status %s' % name)['code']
        self.sshServices.append(dict(name=name, state=state))
        # if action == 'start':
        #     self.runCmd(ssh=True, cmd='systemctl restart %s' % name, code=0)
        if (action == 'stop') and state != 4:
            self.runCmd(ssh=True, cmd='systemctl stop %s' % name, code=0)


    def sshCheckService(self):
        print(self.sshServices)
        for serv in self.sshServices:
            if serv['state'] == 0:
                self.runCmd(ssh=True, cmd='systemctl start %s' % serv['name'], code=0, remov=True)

            elif serv['state'] == 3:
                self.runCmd(ssh=True, cmd='systemctl stop %s' % serv['name'], code=0, remov=True)





    # РАБОТА С ПАКЕТОМ--------------------------------------------------------------------------------------------------
    # установка пакета
    def installPack(self, name=None):
        if name == 'quotatool':
            if self.runCmd(cmd='rpm -qi quotatool')['code'] != 0:
                self.runCmd(cmd='yum install %s -y' % os.path.join(os.getcwd(), 'rpm/quotatool-1.6.2-3.el7.x86_64.rpm'),
                            code=0)

        else:
            if self.runCmdFromRoot(cmd="rpm -qi %s" % name)['code'] == 0:
                self.packages.append(name)
            else:
                self.runCmdFromRoot(cmd="yum install %s -y" % name, code=0)

    # удаление пакета
    def uninstallPack(self, name=None):
        if name in self.packages:
            self.packages.remove(name)
        else:
            self.runCmdFromRoot(cmd="yum remove %s -y" % name, code=0, remov=True)



    # РАБОТА С НОСИТЕЛЕМ------------------------------------------------------------------------------------------------
    # монтирование носителя
    def mountDev(self, point=None, key='', user=None):
        if not os.path.exists(point):
            os.mkdir(point)

        if key == '':
            key = '-t ext4 -o defaults'

        self.mountPoint = point
        self.runCmdFromRoot(cmd="mount %s %s %s" % (key, self.params['mntDevice'], point), code=0)
        time.sleep(3)
        if user != None:
            self.runCmdFromRoot(cmd="chown %s:%s %s" % (user, user, point), code=0)


    # отмонтирование носителя
    def umountDev(self, remov=False):
        self.runCmdFromRoot(cmd="umount %s" % self.params['mntDevice'], code=0, remov=remov)
        time.sleep(3)
        self.runCmdFromRoot(cmd='rm -rf %s' % self.mountPoint, code=0, remov=remov)


    # РАБОТА С РЕЗЕРВОМ ФАЙЛА-------------------------------------------------------------------------------------------
    # создание копии файла
    def createCopyFile(self, fileName=None):
        self.runCmdFromRoot(cmd="cp %s %s2" % (fileName, fileName), code=0)

    def exchangeCopyFile(self, fileName=None):
        self.runCmdFromRoot(cmd='cp %s2 %s' % (fileName, fileName), code=0, remov=True)
        self.runCmdFromRoot(cmd='rm %s2' % fileName, code=0, remov=True)

    # ВЫВОД ИНФОРМАЦИИ--------------------------------------------------------------------------------------------------
    def showInfoBlock(self, stage=0, auto=True):
        showTextCenter(u'ФБО "%s"' % self.osf)
        showTextCenter(u'"%s"' % self.name)

        if stage != 0:
            showTextCenter(u'\nЭтап %s из %s' % (stage, self.stages))

        if not auto:
            showTextCenter(u'\nТест не может быть выполнен в автоматическом режиме.')
            showTextCenter(u'Ниже приведена инструкция для тестирования.\n\n')
            showTextCenter(u'ПРОЦЕДУРА ТЕСТИРОВАНИЯ')


    def showSetUpBlock(self):
        showTextCenter(u'\nПОДГОТОВКА')

        if 'testDir' in self.params:
            self.createTestDir()


    def showTestingBlock(self):
        showTextCenter(u'\nТЕСТИРОВАНИЕ', ' ')


    def showEndBlock(self):
        showTextCenter(u'\nОТКАТ ПРОИЗВЕДЕННЫХ ИЗМЕНЕНИЙ', ' ')


    def showResultBlock(self, stage=0):

        if 'testDir' in self.params:
            self.delTestDir()

        if self.fatalError:
            sys.exit(10)

        showTextCenter(u'\nРЕЗУЛЬТАТ', ' ')

        status = 0

        if self.errorResult != []:
            showTextCol([u'Статус:', u'{cl}во время тестирования произошла ошибка{endcl}\n'.format(cl=clRed, endcl=clStandart)])
            for id, err in enumerate(self.errorResult):
                showTextCenter(u'Ошибка #' + str(id + 1))
                showTextCol(['msg:', err['msg']])
            status = 2
            writeToLog(type='end_test', data=dict(num=self.num, status=status))
            sys.exit(status)


        if self.result == [] and self.removResult == []:
            if stage == 1:
                showTextCol([u'Статус:', u'{cl}ПЕРВЫЙ ЭТАП ПРОЙДЕН УСПЕШНО{endcl}'.format(cl=clGreen, endcl=clStandart)])
                status = 3
                writeToLog(type='end_test', data=dict(num=self.num, status=status))
                sys.exit(status)
            else:
                showTextCol([u'Статус:', u'{cl}ПРОЙДЕН{endcl}'.format(cl=clGreen, endcl=clStandart)])

        elif self.result == [] and self.removResult != []:
            showTextCol([u'Статус:',
                         u'{cl}ПРОЙДЕН{endcl} / произошли ошибки во время отката\n'.format(cl=clGreen, endcl=clStandart)])
            status = 6

        elif self.result != [] and self.removResult == []:
            showTextCol([u'Статус:', u'{cl}НЕ ПРОЙДЕН{endcl}\n'.format(cl=clRed, endcl=clStandart)])
            status = 1

        elif self.result != [] and self.removResult != []:
            showTextCol([u'Статус:',
                         u'{cl}НЕ ПРОЙДЕН{endcl} / произошли ошибки во время отката\n'.format(cl=clRed, endcl=clStandart)])
            status = 7



        if self.result != []:
            showTextCenter(u'Ошибки тестирования')

            for id, err in enumerate(self.result):
                showTextCenter(u'Ошибка #' + str(id + 1))

                if err['type'] == 'code':
                    showTextCol(['user:', err['user']])
                    err['cmd'] = err['cmd'].replace('\n', '\\n')
                    showTextCol(['command:', err['cmd']])
                    showTextCol(['wait:', err['wait']])
                    showTextCol(['taken:', err['taken']])
                    if err['output'] != '':
                        showTextCol(['output:', err['output']])
                    if err['error'] != '':
                        showTextCol(['error:', err['error']])

                elif err['type'] == 'general':
                    showTextCol(['msg:', err['msg']])
                    if err['wait'] != '':
                        showTextCol(['wait:', err['wait']])
                    if err['taken'] != '':
                        showTextCol(['taken:', err['taken']])


        if self.removResult != []:
            showTextCenter(u'Ошибки отката')

            for id, err in enumerate(self.removResult):
                showTextCenter(u'Ошибка #' + str(id + 1))

                showTextCol(['user:', err['user']])
                err['cmd'] = err['cmd'].replace('\n', '\\n')
                showTextCol(['command:', err['cmd']])
                showTextCol(['wait:', err['wait']])
                showTextCol(['taken:', err['taken']])
                if err['output'] != '':
                    showTextCol(['output:', err['output']])
                if err['error'] != '':
                    showTextCol(['error:', err['error']])


        writeToLog(type='end_test', data=dict(num=self.num, status=status))
        sys.exit(status)

    def showResultBlock2(self):
        showTextCenter(u'РЕЗУЛЬТАТ ТЕСТИРОВАНИЯ')


    def showCanNotResultBlock(self):
        if self.errorResult:
            status = 2
        else:
            status = 4
        writeToLog(type='end_test', data=dict(num=self.num, status=status))
        sys.exit(status)





    # Работа с каталог тестовым
    def createTestDir(self):
        if os.path.exists(self.params['testDir']):
            shutil.rmtree(self.params['testDir'])

        self.runCmdFromRoot(cmd='mkdir %s' % self.params['testDir'], code=0)
        self.runCmdFromRoot(cmd='chmod 777 %s' % self.params['testDir'], code=0)



    def delTestDir(self):
        self.runCmdFromRoot(cmd='rm -R %s' % self.params['testDir'], code=0, remov=True)



    # --------------------------------------------------------------------------------------------------
    def addResult(self, msg=None, wait='', taken=''):
        self.result.append(dict(type='general', msg=msg, wait=wait, taken=taken))

        writeToErrorLog(type='er', data=dict(testNum=self.num, user=self.runCmdInfo['user'], cmd=self.runCmdInfo['cmd'],
                                           msg=msg, wait=wait, taken=taken))
        raise Exception('err')

    def showActionMsg(self, msg=None):
        showTextCol(['root', msg, 'ok'])



    def showError(self, error=None):
        try:
            if error == 'err':
                showError(u'Тестирование прервано')
            else:
                showError(u'Тестирование прервано, возникла ошибка')
                writeToErrorLog(type='ee', data=dict(testNum=self.num, error=error))
                self.errorResult.append(dict(msg=error))
        except:
            showError(u'Тестирование прервано, возникла внутренняя ошибка')
            showMsg(error)
            self.fatalError = True



    def setPause(self, params={}):
        setContinueLogFile(params=params)
        showMsg(u'Для продолжения тестирования необходимо произвести перезагрузку ОС.')
        sys.exit(3)

    def getAddParams(self):
        return getAddParams()



    # работа со временем
    def restartNtpd(self):
        self.runCmdFromRoot(cmd='systemctl restart ntpd', code=0)
        while True:
            curr = datetime.datetime.now()
            res = self.runCmdFromRoot(cmd='ntpstat')['code']
            if res == 1:
                time.sleep(2)
                break
        return curr


    def timeStart(self):
        if 'yes' in self.runCmdFromRoot(cmd='timedatectl status | grep "NTP synchronized"')['output']:
            self.statusNtpd = True
        else:
            self.statusNtpd = False

        if not self.statusNtpd:
            self.currentTime = self.restartNtpd()

        self.actualTime = datetime.datetime.now()


    def timeEnd(self):
        self.restartNtpd()
        if not self.statusNtpd:
            actualTimeEnd = datetime.datetime.now()
            duration = actualTimeEnd - self.actualTime
            now3 = self.currentTime + timedelta(seconds=duration.total_seconds())
            self.runCmdFromRoot(cmd='date -s "%s"' % datetime.datetime.strftime(now3, "%b %-d %Y %H:%M:%S"), code=0, remov=True)
            self.runCmdFromRoot(cmd='systemctl stop ntpd', code=0, remov=True)




    def __init__(self, testInfo=None):
        writeToLog(type='start_test', data=dict(num=testInfo['num']))
        self.osf = testInfo['osf']
        self.name = testInfo['name']
        self.osfNum = testInfo['osfNum']
        self.num = testInfo['num']
        self.stages = testInfo['stages']
        self.params = getConfigParams(testInfo['params'])



# **********************************************************************************************************************
# THREAD
# **********************************************************************************************************************
class MyThread(Thread):

    pid = None

    def run(self):
        showTextCol([self.user, 'run thread: %s' % self.cmd, 'ok'])
        proc = Popen("%s" % self.cmd, stdout=PIPE, shell=True)
        self.pid = proc.pid
        output, error = proc.communicate()
        showTextCol([self.user, 'stop thread: %s' % self.cmd, 'ok'])



    def __init__(self, user=None, cmd=None):
        Thread.__init__(self)
        self.user = user
        self.cmd = cmd


class MyThread2(Thread):

    pid = None

    def run(self):
        import paramiko
        sshClient = paramiko.SSHClient()
        sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        sshClient.connect(hostname=self.host, username=self.user, password=self.passwd, port=22)

        stdin, stdout, stderr = sshClient.exec_command(self.cmd)
        output = stdout.read().rstrip()
        error = stderr.read().rstrip()
        returnCode = stdout.channel.recv_exit_status()

        sshClient.close()


        # printTextCol([self.user, 'run thread: %s' % self.cmd, 'ok'])
        # proc = Popen("%s" % self.cmd, stdout=PIPE, shell=True)
        # self.pid = proc.pid
        # output, error = proc.communicate()
        # printTextCol([self.user, 'stop thread: %s' % self.cmd, 'ok'])

    def __init__(self, host=None, user=None, passwd=None, cmd=None):
        Thread.__init__(self)
        self.host = host
        self.passwd = passwd
        self.user = user
        self.cmd = cmd



# **********************************************************************************************************************
# GET TEST INFORMATION
# **********************************************************************************************************************
def launchTest(testInfo=None):
    # Test launch parameters
    try:
        options, args = getopt.getopt(sys.argv[1:], '', [])
        if 'info' in args:
            print(json.dumps(testInfo))
            sys.exit(10)

        elif 'run' in args:
            if '0' in args:
                return 0
            if '1' in args:
                return 1
            if '2' in args:
                return 2

        elif options == []:
            raise getopt.GetoptError('Не определены опции запуска')

    except getopt.GetoptError as e:
        showError(e)
        sys.exit(11)

















# **********************************************************************************************************************
# CHECK SYSTEM отслеживание системы не работает
# **********************************************************************************************************************
checklogFile = os.path.join(os.getcwd(), 'check.log')

def getDataSystem():

    def addUsers():
        p = pwd.getpwall()
        usersInfo = []
        for i in p:
            usersInfo.append('%s:%s:%s:%s:%s:%s:%s' % (i[0], i[1], i[2], i[3], i[4], i[5], i[6]))

        res.append(dict(type='user', info=usersInfo))
        # print('add users information')

    def addSELinux():
        info = runCmd(cmd='semanage user -l')['output'].rstrip().split('\n')
        res.append(dict(type='semanageuser', info=info))

    def addFile(path=None):
        size = os.path.getsize(path)
        res.append(dict(type='file', path=path, size=size))
        # print(path)

    def addDelete(path=None):
        res.append(dict(type='del', path=path))
        # print(path)


    # print('%s Getting of system information %s' % ((' ' * 32), (' ' * 31)))

    res = []

    if os.path.isfile(checklogFile):
        os.remove(checklogFile)

    addUsers()

    addSELinux()

    addFile('/etc/sudoers')
    addFile('/etc/audit/auditd.conf')


    addDelete('/tmp/suid_test.c')
    addDelete('/tmp/suid')
    addDelete('/etc/selinux/targeted/contexts/users/webadm_u')
    addDelete('/home/audit_create_dir2')
    addDelete('/tmp/iva_dir')
    # addDelete(testDir)


    file = open(checklogFile, 'a')
    file.write(json.dumps(res))
    file.close()

    # print('\n')


def checkDataSystem():

    def checkUser(info=None):
        # возможно добавить проверку групп
        usersInfo = []
        p = pwd.getpwall()
        for i in p:
            usersInfo.append('%s:%s:%s:%s:%s:%s:%s' % (i[0], i[1], i[2], i[3], i[4], i[5], i[6]))

        res = list(set(info) ^ set(usersInfo))

        if len(res) != 0:
            print('ERROR users info: %s' % res)

    def checkSELinux(info=None):
        pass
        # newInfo = runCmd(cmd='semanage user -l')['output'].rstrip().split('\n')
        #
        # res = list(set(info) ^ set(newInfo))
        #
        # if len(res) != 0:
        #     print(res)
        #     print('ERROR semanage user')

    def checkFile(path=None, size=None):
        newSize = os.path.getsize(path)
        if newSize != size:
            print('ERROR file: %s' % path)
        # else:
        #     print('CHECK file: %s' % path)

    def checkDel(path=None):
        if os.path.isfile(path):
            print('ERROR path: %s' % path)
            os.remove(path)
            print('DELETE path: %s' % path)

        elif os.path.exists(path):
            print('ERROR path: %s' % path)
            shutil.rmtree(path)
            print('DELETE path: %s' % path)

        # print('CHECK path: %s' % path)


    # print('%s Checking of system information %s' % ((' ' * 31), (' ' * 31)))

    if not os.path.isfile(checklogFile):
        print('Не найден файл с данными.')
        return False

    file = open(checklogFile, 'r')
    data = json.loads(file.read())
    file.close()

    for line in data:
        if line['type'] == 'semanageuser':
            checkSELinux(line['info'])

        if line['type'] == 'user':
            checkUser(line['info'])

        if line['type'] == 'file':
            checkFile(path=line['path'], size=line['size'])

        if line['type'] == 'del':
            checkDel(path=line['path'])



    os.remove(checklogFile)
    # print('\n')


# getDataSystem()
# checkDataSystem()