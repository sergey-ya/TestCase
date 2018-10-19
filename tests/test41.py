#!/usr/bin/python
# coding: utf_8

import modules as tm



osf = u'Защита ОО'
name = u'Защита хранимой аутентификационной информации'
osfNum = 5
num = 41
stages = 1
params = []
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()
    test.runCmdFromRoot(cmd='cat /etc/shadow', code=0)


except Exception as e:
    test.showError(e.message)


finally:
    # result out--------------------------------------------------------------------------------------------------------
    test.showResultBlock()