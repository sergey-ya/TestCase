#!/usr/bin/python
# coding: utf_8

import time, os
from datetime import datetime
from subprocess import check_output
import modules as tm

osf = u'Защита данных пользователя'
name = u'Фильтрация сетевого потока'
osfNum = 2
num = 14
stages = 1
params = ['firstUserName', 'sshHostName', 'sshUserName', 'sshPasswd']
progress = '0/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
sshHost = test.params['sshHostName']
sshUser = test.params['sshUserName']
sshPass = test.params['sshPasswd']


ips = check_output(['hostname', '--all-ip-addresses']).rstrip()

thread = None

time1 = []

file1 = 'pinganalysis.py'
file2 = 'pinglog.file'
file3 = 'iptables.file'

statusNtpd = None
statusNtpd2 = None

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()

    # не сделан пункт в г д

    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()


    def clearIPTABLES():
        test.runCmdFromRoot(cmd='iptables -F', code=0)
        res = test.runCmdFromRoot(cmd='iptables -L -n')['output'].split('\n')
        if len(res) != 8:
            test.addResult(msg=u'Ошибка при очистке iptables', wait='no rules', taken=res)


    test.runCmdFromRoot(cmd='systemctl restart iptables', code=0)
    clearIPTABLES()


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()


    print(test.runCmdFromRoot(cmd="cat /home/my/test | nc -v -u 10.81.81.67 49001"))




except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()





    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()

