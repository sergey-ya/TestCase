#!/usr/bin/python
# coding: utf_8

import modules as tm



osf = u'Идентификация и аутентификация'
name = u'Аутентификация с защищенной обратной связью'
osfNum = 3
num = 27
stages = 0
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


except Exception as e:
    test.showError(e.message)



finally:
    # result out--------------------------------------------------------------------------------------------------------
    test.showResultBlock()



