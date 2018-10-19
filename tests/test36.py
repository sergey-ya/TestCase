#!/usr/bin/python
# coding: utf_8


import modules as tm



osf = u'Защита ОО'
name = u'Тестирование абстрактной машины'
osfNum = 5
num = 36
stages = 1
params = []
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()
    test.installPack('amtu')


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()
    test.runCmdFromRoot(cmd="amtu", code=0)
    test.runCmdFromRoot(cmd="amtu -d", code=0)


except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()
        test.uninstallPack('amtu')

    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()
