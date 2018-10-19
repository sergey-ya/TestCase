#!/usr/bin/python
# coding: utf_8

import os, shutil, pwd, sys
import modules as tm



osf = u'Использование ресурсов'
name = u'Максимальные квоты'
osfNum = 8
num = 53
stages = 1
params = ['firstUserName', 'secondUserName', 'mntDevice']
progress = '1/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
secondUser = test.params['secondUserName']
mntDevice = test.params['mntDevice']


file1 = '/tmp/mem_test.perl'


file3 = '/mnt/quota_test/aquota.group'
file4 = '/mnt/quota_test/aquota.user'
file5 = '/mnt/quota_test/file1.dat'
file6 = '/mnt/quota_test/file2.dat'

file7 = '/etc/security/limits.conf'

mntPoint = '/mnt/quota_test'

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()

    test.installPack('quotatool')

    file = open(file1, 'w')
    file.write('#!/usr/local/bin/perl\n')
    file.write('print "My PID: $$\\n";\n')
    file.write('while (1){\n')
    file.write('$x.="x"x(1024 ** 2);\n')
    file.write('print length($x), "\\n"}\n')
    file.close()
    test.showActionMsg('create file %s' % file1)

    test.runCmdFromRoot(cmd="chmod 777 %s" % file1, code=0)

    test.createCopyFile(file7)



    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт а')
    test.mountDev(point=mntPoint, key='-o rw,relatime,seclabel,quota,usrquota,grpquota,data=ordered')
    test.runCmdFromRoot(cmd="chown -R %s:%s %s" % (secondUser, secondUser, mntPoint), code=0)


    res = test.runCmdFromRoot(cmd="mount | grep -E '%s.*%s.*%s'" % (mntDevice, 'usrquota', 'grpquota'),
                              code=0)['output']
    if res.find('usrquota,grpquota,') == -1:
        test.addResult(msg=u'Некорректно примонтирована файловая система.', wait='usrquota and grpquota', taken=res)


    test.runCmdFromRoot(cmd="quotacheck -cuvg %s" % mntDevice, code=0)
    test.runCmdFromRoot(cmd="quotaon %s" % mntDevice, code=0)


    test.runCmdFromRoot(cmd="quotatool -u %s -b -q 76800 -l 102400 %s" % (secondUser, mntDevice), code=0)
    test.runCmdSecondUser(cmd='cat /dev/urandom > %s' % file5, code=1)
    size = os.path.getsize(file5) / 1024
    if size > 102400 or size < 100000:
        test.addResult(msg=u'Несоответствует размер тестового файла.', wait='< 102400', taken=size)


    test.runCmdFromRoot(cmd="quotaoff %s" % mntDevice, code=0)
    test.runCmdFromRoot(cmd='rm %s' % file3, code=0)
    test.runCmdFromRoot(cmd='rm %s' % file4, code=0)
    test.runCmdFromRoot(cmd='rm %s' % file5, code=0)

    test.runCmdFromRoot(cmd="chown -R %s:%s %s" % (firstUser, firstUser, mntPoint), code=0)
    test.runCmdFromRoot(cmd="quotacheck -cuvg %s" % mntDevice, code=0)
    test.runCmdFromRoot(cmd="quotaon %s" % mntDevice, code=0)

    test.runCmdFromRoot(cmd="quotatool -g %s -b -q 768 -l 2048 %s" % (firstUser, mntDevice), code=0)



    test.runCmdFirstUser(cmd='cat /dev/urandom > %s' % file6, code=1)
    size = os.path.getsize(file6) / 1024
    if size > 2048 or size < 1900:
        test.addResult(msg=u'Несоответствует размер тестового файла.', wait=u'1900 %s до 2048', taken=size)




    test.runCmdFromRoot(cmd="quotaoff %s" % mntDevice, code=0)
    test.runCmdFromRoot(cmd='rm %s' % file3, code=0)
    test.runCmdFromRoot(cmd='rm %s' % file4, code=0)
    test.runCmdFromRoot(cmd='rm %s' % file6, code=0)


    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт б')

    def analysis(res=None, mem1=None, mem2=None):
        if res > mem2 or res < mem1:
            test.addResult(msg=u'Неверное значение конечной величины физической памяти.',
                           wait=u'от %s до %s' % (str(mem1), str(mem2)), taken=str(res))


    test.runCmdFromRoot(cmd='swapoff -a', code=0)



    memFree = test.runCmdFirstUser(cmd='free -m | grep Mem | tr -s " " | cut -f 7 -d " "', code=0)['output']
    res = test.runCmdFirstUser(cmd='perl %s' % file1, code=1)['output'].split('\n')
    res = int(res[len(res) - 1])
    analysis(res=res / 1024 / 1024, mem1=int(memFree) - 300, mem2=int(memFree) + 100)


    memFree = test.runCmdSecondUser(cmd='free -m | grep Mem | tr -s " " | cut -f 7 -d " "', code=0)['output']
    res = test.runCmdSecondUser(cmd='perl %s' % file1, code=1)['output'].split('\n')
    res = int(res[len(res) - 1])
    analysis(res=res / 1024 / 1024, mem1=int(memFree) - 300, mem2=int(memFree) + 100)




    test.runCmdFromRoot(cmd='echo "%s hard as 100000" >> %s' % (firstUser, file7), code=0)
    test.runCmdFromRoot(cmd='echo "@%s hard as 50000" >> %s' % (secondUser, file7), code=0)

    res = test.runCmdFirstUser(cmd='ulimit -v', code=0)['output']
    if int(res) != 100000:
        test.addResult(msg=u'Неверное значение ограничения оперативной памяти.', wait='756000', taken=res)

    res = test.runCmdSecondUser(cmd='ulimit -v', code=0)['output']
    if int(res) != 50000:
        test.addResult(msg=u'Неверное значение ограничения оперативной памяти.', wait='50000', taken=res)



    res = test.runCmdFirstUser(cmd='perl %s' % file1, code=1)['output'].split('\n')
    res = int(res[len(res) - 1])
    analysis(res=res / 1024 / 1024, mem1=50, mem2=100)


    res = test.runCmdSecondUser(cmd='perl %s' % file1, code=1)['output'].split('\n')
    res = int(res[len(res) - 1])
    analysis(res=res / 1024 / 1024, mem1=15, mem2=50)




except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        test.runCmdFromRoot(cmd='rm %s' % file1, code=0, remov=True)

        test.exchangeCopyFile(file7)

        test.umountDev(remov=True)

    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()


