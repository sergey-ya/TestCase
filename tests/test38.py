#!/usr/bin/python
# coding: utf_8


from datetime import datetime, timedelta
import time
import modules as tm


osf = u'Защита ОО'
name = u'Надежные метки времени'
osfNum = 5
num = 38
stages = 1
params = ['firstUserName']
progress = '2/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']

# statusService = None
# currentDate = None
# now1 = None

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()



    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()

    test.timeStart()



    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    test.runCmdFromRoot(cmd='ntpstat', code=1)
    res1 = test.runCmdFromRoot(cmd='timedatectl status', code=0)['output'].split('\n')[5]
    if res1.find('no') == -1:
        test.addResult(msg=u'Неверное состояние синхронизации', wait='NTP synchronized: no', taken=res1)


    list = test.runCmdFromRoot(cmd='ntpq -p', code=0)['output'].split('\n')


    # можно и переписать
    res = []
    for i in list:
        i = i[1: len(i)]
        if i[0:3] == 'ntp':
            pos = i.find(' ')
            res.append(i[1: pos])

    test.runCmdFromRoot(cmd='ntpdate -u %su' % res[0], code=1)

    test.runCmdFromRoot(cmd='systemctl restart ntpd', code=0)
    time.sleep(3)


    test.runCmdFromRoot(cmd='ntpstat', code=0)
    res2 = test.runCmdFromRoot(cmd='timedatectl status', code=0)['output'].split('\n')[5]
    if res2.find('yes') == -1:
        test.addResult(msg=u'Неверное состояние синхронизации', wait='NTP synchronized: yes', taken=res2)




except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        test.timeEnd()


    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()

