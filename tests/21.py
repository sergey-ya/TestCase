#!/usr/bin/python
# coding: utf_8

import os, shutil, pwd, sys
import modules as tm


osf = u'Защита данных пользователя'
name = u'Контроль целостности запускаемых компонентов программного обеспечения'
osfNum = 2
num = 21
stages = 2
params = ['firstUserName']
progress = '0/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

stage = tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']


try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock(stage=stage)

    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    #yum install ima-manage keyutils attr

    #ПЕРЕЗАГРУЗКА

    if stage == 1:
        print('STAGE 1')



    if stage == 2:
        print('STAGE 2')


except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        if stage == 2:
            test.showEndBlock()

    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        if stage == 2:
            test.showResultBlock()
        else:
            sys.exit(3)


