#!/usr/bin/python
# coding: utf_8

import os, shutil, time
from modules import MyThread
import modules as tm



osf = u'Использование ресурсов'
name = u'Ограниченный приоритет обслуживания'
osfNum = 8
num = 52
stages = 1
params = ['firstUserName', 'testDir']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
testDir = test.params['testDir']


file1 = '%s/nice_tst.sh' % testDir

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()

    file = open("%s" % file1, "w")
    file.write('#!/bin/bash\n')
    file.write('x="$1"\n')
    file.write('echo "$2" $(date)\n')
    file.write('while [ $x -gt 0 ]; do x=$(( x-1 )); done\n')
    file.write('echo "$2" $(date)\n')
    file.close()
    test.showActionMsg('create file %s' % file1)

    test.runCmdFromRoot(cmd="chown %s:%s %s" % (firstUser, firstUser, testDir), code=0)
    test.runCmdFromRoot(cmd="chown %s:%s %s" % (firstUser, firstUser, file1), code=0)
    test.runCmdFromRoot(cmd="chmod 777 %s" % file1, code=0)


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    def mean(numbers):
        return float(sum(numbers)) / max(len(numbers), 1)

    thread = MyThread(user=firstUser, cmd="%s/nice_tst.sh 1000000 A" % testDir)
    thread.start()
    time.sleep(3)

    res = []
    for i in [1, 2, 3, 4, 5]:
        out1 = test.runCmdFirstUser(cmd="ps -p " + str(thread.pid) + " -o %cpu", code=0)['output'].rsplit('\n')
        res.append(int(float(out1[1])))
        time.sleep(1)
    thread.join()

    if mean(res) < 75:
        test.addResult(msg=u'Значение доступного процессорного времени слишком мало.', wait='80', taken=str(mean(res)))


    start_time = time.time()

    threadA = MyThread(user=firstUser, cmd="%s/nice_tst.sh 1000000 A" % testDir)
    threadA.start()
    threadB = MyThread(user=firstUser, cmd="nice -n 2 %s/nice_tst.sh 1000000 B" % testDir)
    threadB.start()
    threadC = MyThread(user=firstUser, cmd="nice -n 12 %s/nice_tst.sh 1000000 C" % testDir)
    threadC.start()
    time.sleep(3)

    resA = []
    resB = []
    resC = []
    for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        outA = test.runCmdFirstUser(cmd="ps -p " + str(threadA.pid) + " -o %cpu", code=0)['output'].rsplit('\n')
        resA.append(float(outA[1]))
        outB = test.runCmdFirstUser(cmd="ps -p " + str(threadB.pid) + " -o %cpu", code=0)['output'].rsplit('\n')
        resB.append(float(outB[1]))
        outC = test.runCmdFirstUser(cmd="ps -p " + str(threadC.pid) + " -o %cpu", code=0)['output'].rsplit('\n')
        resC.append(float(outC[1]))
        time.sleep(1)

    threadA.join()
    end_timeA = (time.time() - start_time)

    threadB.join()
    end_timeB = (time.time() - start_time)

    threadC.join()
    end_timeC = (time.time() - start_time)


    if not (mean(resC) < mean(resB) and mean(resC) < mean(resA) and mean(resB) < mean(resA)):
        test.addResult(msg=u'Несоответствие значений доступного процессорного времени.',
                       wait=u'В порядке убывания',
                       taken='A:%s, B:%s, C:%s' % (str(mean(resA)), str(mean(resB)), str(mean(resC))))


    if not (end_timeC > end_timeB and end_timeC > end_timeA and end_timeB > end_timeA):
        test.addResult(msg=u'Неверный порядок завершения скриптов.',
                       wait=u'В порядке возрастания',
                       taken='A:%s, B:%s, C:%s' % (str(end_timeA), str(end_timeB), str(end_timeC)))


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



