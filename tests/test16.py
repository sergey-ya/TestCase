#!/usr/bin/python
# coding: utf_8

import os, shutil, pwd
import time
from datetime import datetime
import socket
import modules as tm



osf = u'Защита данных пользователя'
name = u'Защита остаточной информации — жесткий диск'
osfNum = 2
num = 16
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
    # работа с testdisk


except Exception as e:
    test.showError(e.message)


finally:
    # result out--------------------------------------------------------------------------------------------------------

    test.showCanNotResultBlock()
