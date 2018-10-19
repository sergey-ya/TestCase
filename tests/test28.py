#!/usr/bin/python
# coding: utf_8

import time, os
from datetime import datetime
from subprocess import check_output
import modules as tm

osf = u'Идентификация и аутентификация'
name = u'Выбор момента идентификации и идентификация до любых действий пользователя'
osfNum = 3
num = 28
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
    # cinnamon


except Exception as e:
    test.showError(e.message)


finally:
    # result out--------------------------------------------------------------------------------------------------------
    test.showCanNotResultBlock()
