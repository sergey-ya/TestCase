#!/usr/bin/python
# coding: utf_8

import time, os
from datetime import datetime
from subprocess import check_output
import modules as tm

osf = u'Доступ к ОО'
name = u'Ограничение на параллельные сеансы'
osfNum = 6
num = 44
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
    # tty


except Exception as e:
    test.showError(e.message)


finally:
    # result out--------------------------------------------------------------------------------------------------------

    test.showCanNotResultBlock()
