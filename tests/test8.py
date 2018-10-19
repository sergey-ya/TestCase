#!/usr/bin/python
# coding: utf_8

import os, shutil, pwd
import time
from datetime import datetime
import socket
import modules as tm



osf = u'Аудит'
name = u'Предотвращение потери данных аудита'
osfNum = 1
num = 8
stages = 0
params = []
progress = '0/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock(auto=False)

    # NOT AUTOMATIC
    # переход в однопользователский режим

    tm.showTextCol([u'Измените файл /etc/audit/auditd.conf:'])
    tm.showTextCol([u'disk_full_action = SINGLE'])
    tm.showTextCol([u'disk_error_action = SINGLE'])
    tm.showTextCol([u'space_left = 100'])
    tm.showTextCol([u'admin_space_left = 99'])
    tm.showTextCol([u'admin_space_left_action = SINGLE\n'])

    tm.showTextCol([u'* значение параметра space_left должно быть больше значения параметра admin_space_left\n'])
    tm.showTextCol([u'Далее производятся действия на переполнение файловой системы, хранящей данные аудита.\n\n'])



    # result------------------------------------------------------------------------------------------------------------
    test.showResultBlock2()
    tm.showTextCol([u'При невозможности сохранения данных аудита система переходит в однопользовательский режим.'])



except Exception as e:
    test.showError(e.message)

finally:
    test.showCanNotResultBlock()
