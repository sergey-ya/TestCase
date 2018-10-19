#!/usr/bin/python
# coding: utf_8

import modules as tm


osf = u'Защита данных пользователя'
name = u'Экспорт данных пользователя с атрибутами безопасности'
osfNum = 2
num = 13
stages = 1
params = ['firstUserName', 'mntDevice']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
mntDevice = test.params['mntDevice']

dir1 = "/home/%s/backup_test" % firstUser
file1 = "/home/%s/backup_test/export.txt" % firstUser


mntDir1 = '/mnt/mnt1'
mntDir2 = '/mnt/mnt2'


try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    test.runCmdFirstUser(cmd="mkdir %s" % dir1, code=0)
    test.runCmdFirstUser(cmd="touch %s" % file1, code=0)
    test.runCmdFirstUser(cmd="chmod 700 %s" % dir1, code=0)
    test.runCmdFirstUser(cmd="chmod 600 %s" % file1, code=0)


    test.runCmdFromRoot(cmd="semanage fcontext -a -t samba_share_t %s" % dir1, code=0)
    test.runCmdFromRoot(cmd="restorecon -v %s" % dir1, code=0)


    res1 = test.runCmdFirstUser(cmd="ls -AZl /home/%s/ | grep backup_test" % firstUser,
                                code=0)['output'].replace(" ", "").rstrip('\n')
    res12 = test.runCmdFirstUser(cmd="ls -AZl %s | grep export.txt" % dir1,
                                 code=0)['output'].replace(" ", "").rstrip('\n')




    test.mountDev(point=mntDir1, user=firstUser)


    test.runCmdFirstUser(cmd="cp --preserve=context -R %s %s" % (dir1, mntDir1), code=0)

    test.umountDev()
    test.mountDev(point=mntDir2, user=firstUser)

    res2 = test.runCmdFirstUser(cmd="ls -AZl %s | grep backup_test" % mntDir2,
                                code=0)['output'].replace(" ", "").rstrip('\n')
    res22 = test.runCmdFirstUser(cmd="ls -AZl %s/backup_test | grep export.txt" % mntDir2,
                                code=0)['output'].replace(" ", "").rstrip('\n')


    if res1[0: len(res1)-18] != res2[0: len(res2)-18]:
        test.addResult(msg=u'Не соответствие атрибутов безопасности', wait=res1, taken=res2)

    if res12[0: len(res12)-15] != res22[0: len(res22)-15]:
        test.addResult(msg=u'Не соответствие атрибутов безопасности', wait=res12, taken=res22)



except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        test.runCmdFromRoot(cmd='rm -rf %s/backup_test' % mntDir2, code=0, remov=True)
        test.umountDev(remov=True)

    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()
