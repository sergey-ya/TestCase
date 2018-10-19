#!/usr/bin/python
# coding: utf_8

import os, shutil
import collections
import modules as tm



osf = u'Защита ОО'
name = u'Защита от переполнения буфера - выделение памяти'
osfNum = 5
num = 42
stages = 1
params = ['firstUserName', 'testDir']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
testDir = test.params['testDir']


file1 = '%s/rnd_mem.c' % testDir
file2 = '%s/tst_mem' % testDir

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()

    test.installPack('gcc')


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()
    file = open("%s" % file1, "w")
    file.write('#include <stdio.h>\n')
    file.write('int main() {\n')
    file.write('\tregister int i asm("esp");\n')
    file.write('\tprintf("$esp = %#010x\\n", i);\n')
    file.write('\treturn 0;\n')
    file.write('}\n')
    file.close()
    test.showActionMsg('create file %s' % file1)


    test.runCmdFromRoot(cmd="chown %s:%s %s" % (firstUser, firstUser, testDir), code=0)
    test.runCmdFromRoot(cmd="chown %s:%s %s" % (firstUser, firstUser, file1), code=0)

    test.runCmdFirstUser(cmd="gcc %s -o %s" % (file1, file2), code=0)
    out1 = []
    out1.append(test.runCmdFirstUser(cmd="%s" % file2, code=0)['output'])
    out1.append(test.runCmdFirstUser(cmd="%s" % file2, code=0)['output'])
    out1.append(test.runCmdFirstUser(cmd="%s" % file2, code=0)['output'])
    out1.append(test.runCmdFirstUser(cmd="%s" % file2, code=0)['output'])

    test.runCmdFromRoot(cmd="echo 0 | sudo tee /proc/sys/kernel/randomize_va_space", code=0)

    out2 = []
    out2.append(test.runCmdFirstUser(cmd="%s" % file2, code=0)['output'])
    out2.append(test.runCmdFirstUser(cmd="%s" % file2, code=0)['output'])
    out2.append(test.runCmdFirstUser(cmd="%s" % file2, code=0)['output'])
    out2.append(test.runCmdFirstUser(cmd="%s" % file2, code=0)['output'])


    if len([item for item, count in collections.Counter(out1).items() if count > 1]) != 0:
        test.addResult(msg=u'Ошибка сравнения результатов первого блока', wait=u'Различные значения', taken=out1)


    if len([item for item, count in collections.Counter(out2).items() if count > 1]) != 1:
        test.addResult(msg=u'Ошибка сравнения результатов второго блока', wait=u'Одинаковые значения', taken=out2)



except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        test.runCmdFromRoot(cmd="echo 1 | sudo tee /proc/sys/kernel/randomize_va_space", code=0, remov=True)

        test.uninstallPack('gcc')
    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()



