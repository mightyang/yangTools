#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : pkgProj.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 10.03.2019
# Last Modified Date: 10.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

import os
import re
import nuke
import shutil
import threading
import sys
import time
import Queue
import inspect


class yLogging():
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

    def __init__(self):
        self.__level = self.DEBUG
        self.__activeLevel = self.__level
        self.__levelStr = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        self.__results = []
        self.setFormat('%(acstime)s %(funcname)s[%(lineno)d] %(levelname)s: %(message)s')
        self.__file = open('/home/yang/pkg.log', 'w')
        self.__handler = None

    def setFormat(self, yFormat):
        '''
        %(levelno)s: the number of log level
        %(levelname)s: the name of log level
        %(pathname)s: sys.argv[0]
        %(filename)s: file name
        %(funcname)s: function name of current running
        %(lineno)d: current line of log
        %(acstime)s: time of log
        %(thread)d: thread id
        %(threadname)s: thread name
        %(process)d: process id
        %(message)s: log message
        '''
        pattern = re.compile(
            r'(.*?)(%\(levelno\)s|%\(levelname\)s|%\(pathname\)s|%\(filename\)s|%\(funcname\)s|%\(lineno\)d|%\(acstime\)s|%\(thread\)d|%\(threadname\)s|%\(process\)d|%\(message\)s)(.*?)'
        )
        self.__results = [j for i in pattern.findall(yFormat) for j in i if j]

    def replaceTag(self, tag, info):
        if tag == '%(levelno)s':
            return self.__activeLevel
        elif tag == '%(levelname)s':
            return self.__levelStr[self.__activeLevel]
        elif tag == '%(pathname)s':
            return sys._getframe().f_code.co_filename
        elif tag == '%(filename)s':
            return os.path.basename(sys._getframe().f_code.co_filename)
        elif tag == '%(funcname)s':
            return sys._getframe().f_back.f_back.f_code.co_name
        elif tag == '%(lineno)d':
            return str(sys._getframe().f_back.f_back.f_lineno)
        elif tag == '%(acstime)s':
            return time.asctime()
        elif tag == '%(thread)d':
            return str(threading.currentThread().ident)
        elif tag == '%(threadname)s':
            return threading.currentThread().name
        elif tag == '%(process)d':
            return str(os.getpid())
        elif tag == '%(message)s':
            return info
        else:
            return tag

    def setLevel(self, level):
        if isinstance(level, int) and level >= 0 and level <= 3:
            self.level = level
        else:
            print '日志级别必须为 DEBUG, INFO, WARNING, ERROR.'

    def debug(self, info):
        if self.__level <= self.DEBUG:
            self.__activeLevel = self.DEBUG
            self.__write("".join([self.replaceTag(r, info) for r in self.__results]))

    def info(self, info):
        if self.__level <= self.INFO:
            self.__activeLevel = self.INFO
            self.__write("".join([self.replaceTag(r, info) for r in self.__results]))

    def warning(self, info):
        if self.__level <= self.WARNING:
            self.__activeLevel = self.WARNING
            self.__write("".join([self.replaceTag(r, info) for r in self.__results]))

    def error(self, info):
        if self.__level <= self.ERROR:
            self.__activeLevel = self.ERROR
            self.__write("".join([self.replaceTag(r, info) for r in self.__results]))

    def setHandler(self, handler):
        self.__handler = handler

    def __write(self, msg):
        self.__handler.write(msg + '\n')


yl = yLogging()
yl.setHandler(sys.stdout)

if nuke.NUKE_VERSION_MAJOR <= 10:
    yl.info('Nuke 版本为 %s, import PySide.' % nuke.NUKE_VERSION_STRING)
    from PySide import QtGui as QtGuiWidgets
    from PySide import QtCore
elif nuke.NUKE_VERSION_MAJOR > 10:
    yl.info('Nuke 版本为 %s, import PySide2.' % nuke.NUKE_VERSION_STRING)
    # from PySide2 import QtGui as QtGuiWidgets
    from PySide2 import QtWidgets as QtGuiWidgets
    from PySide2 import QtCore


class yCallbacks(object):
    valueChangedCallback = []
    statusChangedCallback = []
    countChangedCallback = []
    createCallback = []
    pkgFileCallback = []
    getFilesCompleteCallback = []
    pkgGuiCloseCallback = []
    pkgGuiShowCallback = []
    pkgItemThreadQueueEmptyCallback = []
    pkgItemThreadQueueNotEmptyCallback = []

    perNodeClassCallback = []
    perNodeFilePathCallback = []
    perFileCallback = []
    perSpaceCallback = []
    perPkgFileCallback = []
    startGetFilesCallback = []
    spaceRootCallback = []


searchNodes = [['Read', 'file', None, None], ['ReadGeo', 'file', None, None],
               ['ReadGeo2', 'file', None, None],
               ['Camera', 'file', 'read_from_file', True],
               ['Camera2', 'file', 'read_from_file', True],
               ['ModifyRIB', 'ribArchive', 'useRibArchive', True],
               ['Vectorfield', 'vfield_file', None, None],
               ['OCIOFileTransform', 'file', None, None],
               ['ParticleCache', 'file', None, None],
               ['AudioRead', 'file', None, None],
               ['Precomp', 'file', None, None]]


def unitePath(path):
    try:
        path = str(path)
    except Exception as e:
        yl.error(e.message)
    if os.path.isfile(path):
        return path.replace('\\', '/')
    elif os.path.isdir(path):
        if not path.endswith('/') or not path.endswith('\\'):
            path += '/'
        return path.replace('\\', '/')


class pkgStatus(object):
    NORMAL = 'pkg_status_normal'
    PKGED = 'pkg_status_pkged'
    NOEXISTS = 'pkg_status_file'


class pkgItemType(object):
    NORMAL = 'pkg_item_normal'
    SPACEROOT = 'pkg_item_spaceRoot'
    SPACE = 'pkg_item_SPACE'
    NODECLASS = 'pkg_item_nodeClass'
    NODE = 'pkg_item_node'
    NODEFILES = 'pkg_item_nodefiles'
    DIR = 'pkg_item_dir'
    FILE = 'pkg_item_file'
    SEQUENCE = 'pkg_item_sequence'


class pkgItemThreadQueueSignal(object):
    STOP_SIGNAL = 'PkgItemThreadQueue_Stop_Signal'


class pkgItemThreadQueue(threading.Thread):
    def __init__(self, queue):
        super(pkgItemThreadQueue, self).__init__()
        self.__queue = queue
        self.__wantTaskCount = 5
        self.__activeTaskCount = 0
        self.__stop = False
        self.daemon = True

    def setRunTaskCount(self, wantTaskCount):
        self.__wantTaskCount = wantTaskCount

    def empty(self):
        self.__queue.empty()

    def stop(self):
        self.__stop = True
        self.__queue.put(pkgItemThreadQueueSignal.STOP_SIGNAL)

    def run(self):
        runningTasks = []
        yl.debug('start pkgItemThreadQueue')
        while not self.__stop:
            taskIndex = 0
            while self.__activeTaskCount >= self.__wantTaskCount:
                yl.debug('acitveTaskCount is equal or greater than wantTaskCount, so loop until one thread complete')
                if taskIndex >= self.__wantTaskCount:
                    yl.debug('taskIndex turn to 0')
                    taskIndex = 0
                if runningTasks[taskIndex].isRunning():
                    yl.debug('task is running, next')
                    taskIndex += 1
                else:
                    yl.debug('task is complete, pop it form running tasks')
                    runningTasks.pop(taskIndex)
                    self.__activeTaskCount -= 1
                threading.Event().wait(0.1)
            yl.debug('prepare to get item')
            try:
                result = self.__queue.get()
            except Exception as e:
                threading.Event().wait(0.1)
                continue
            # stop if get pkgItemThreadQueueSignal.STOP_SIGNAL
            if isinstance(result, str) and result == pkgItemThreadQueueSignal.STOP_SIGNAL:
                break
            elif isinstance(result, pkgItemThread):
                yl.debug('get pkgItem: %s' % result.getPkgItem().getValue())
                runningTasks.append(result)
                self.__activeTaskCount += 1
                try:
                    result.start()
                except Exception as e:
                    yl.error(e.message)
            else:
                yl.warning('pkgItemThreadQueue need pkgItemThread，but receive %s' % str(type(result)))
            yl.debug('next pkgItemThread')
            if self.__queue.empty():
                yl.debug('pkgItemThreadQueue is empty')
                self.callback(0)
            else:
                yl.debug('pkgItemThreadQueue is not empty')
                self.callback(1)
            threading.Event().wait(0.1)
        yl.debug('stop pkgItemThreadQueue')

    def callback(self, n):
        '''
        n value:
            0: yCallbacks.pkgItemThreadQueueEmptyCallback
            1: yCallbacks.pkgItemThreadQueueNotEmptyCallback
        '''
        if n == 0 and yCallbacks.pkgItemThreadQueueEmptyCallback:
            yl.debug('call yCallbacks.pkgItemThreadQueueEmptyCallback')
            try:
                for c in yCallbacks.pkgItemThreadQueueEmptyCallback:
                    c[0](*c[1])
            except Exception as e:
                yl.error(e.message)
        elif n == 1 and yCallbacks.pkgItemThreadQueueNotEmptyCallback:
            yl.debug('call yCallbacks.pkgItemThreadQueueNotEmptyCallback')
            try:
                for c in yCallbacks.pkgItemThreadQueueNotEmptyCallback:
                    c[0](*c[1])
            except Exception as e:
                yl.error(e.message)


class pkgItem(object):
    def __new__(cls, parent=None, value='', status=None, itemtype=None, count=0, pos=0):
        if not (parent is None or isinstance(parent, pkgItem)):
            yl.error('参数 parent 类型错误，需要 pkgItem')
        elif not isinstance(value, str):
            yl.error('参数 value 类型错误, 需要 string')
        elif status not in pkgStatus.__dict__.values():
            yl.error('参数 status 值错误, 需要 pkgStatus')
        elif itemtype not in pkgItemType.__dict__.values():
            yl.error('参数 itemtype 值错误, 需要 pkgItemType')
        elif not isinstance(count, int):
            yl.error('参数 count 类型错误, 需要 int')
        else:
            return object.__new__(cls, value, status, itemtype, count)

    def __init__(self, parent=None, value='', status=None, itemtype=None, count=0, pos=0):
        self.__value = value
        self.__dirPath = None
        self.__nodePath = None
        self.__status = status
        self.__count = count
        self.__type = itemtype
        self.__list = []
        self.__parent = parent
        self.__pos = pos
        self.callback(self, 3)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.__list[key]
        elif isinstance(key, str):
            for i in self.__list:
                if i.getValue() == key:
                    return i
        return None

    def __setitem__(self, key, item):
        if isinstance(item, pkgItem):
            if isinstance(key, int):
                self.__list[key] = item
            elif isinstance(key, str):
                for index, it in enumerate(self.__list):
                    if it.getValue() == key:
                        self.__list[index] = item
                    else:
                        yl.error('没有关键字: %s ' % key)
        else:
            yl.error('值必须是 pkgItem 类型')

    def __len__(self):
        return len(self.__list)

    def __str__(self):
        return self.__value

    def appendItem(self, item):
        callBackType = 2
        if isinstance(item, pkgItem):
            self.__list.append(item)
            self.__count += 1
            self.callback(self, callBackType)
        else:
            yl.error('item need pkgItem class.')

    def removeItem(self, item):
        callBackType = 2
        if item in self.__list:
            self.__list.remove(item)
            self.__count -= 1
            self.callback(self, callBackType)

    def popItem(self, index=-1):
        callBackType = 2
        try:
            self.__list.pop(index)
        except Exception as e:
            yl.error(e.message)
            return
        self.__count -= 1
        self.callback(self, callBackType)

    def insert(self, index, item):
        self.__list.insert(index, item)

    def children(self):
        return self.__list

    def setValue(self, val):
        callbackType = 0
        self.__val = val
        self.callback(val, callbackType)

    def setDirPath(self, path):
        self.__dirPath = path

    def setNodePath(self, path):
        self.__nodePath = path

    def setStatus(self, s):
        callbackType = 1
        if s in [i[1] for i in inspect.getmembers(pkgStatus, lambda a:not(inspect.isroutine(a))) if not(i[0].startswith('__') and i[0].endswith('__'))]:
            self.__status = s
            self.callback(s, callbackType)
        else:
            yl.error('pkgStatus 没有 %s 属性' % s)

    def setType(self, tp):
        self.__type = tp

    def setPos(self, pos):
        if isinstance(pos, int):
            self.__pos = pos
        else:
            yl.error('TypeError: pos need int, but receive a %s.' % type(pos))

    def callback(self, item, n):
        '''
        n value:
            0: valueChanged
            1: statusChanged
            2: countChanged
            3: create
        '''
        if n == 0 and yCallbacks.valueChangedCallback:
            try:
                for c in yCallbacks.valueChangedCallback:
                    c[0](item, *c[1])
            except Exception as e:
                yl.error(e.message)
        elif n == 1 and yCallbacks.statusChangedCallback:
            try:
                for c in yCallbacks.statusChangedCallback:
                    c[0](item, *c[1])
            except Exception as e:
                yl.error(e.message)
        elif n == 2 and yCallbacks.countChangedCallback:
            try:
                for c in yCallbacks.countChangedCallback:
                    c[0](item, *c[1])
            except Exception as e:
                yl.error(e.message)
        elif n == 3 and yCallbacks.createCallback:
            try:
                for c in yCallbacks.createCallback:
                    c[0](item, *c[1])
            except Exception as e:
                yl.error(e.message)

    def getValue(self):
        return self.__value

    def getStatus(self):
        return self.__status

    def getType(self):
        return self.__type

    def getCount(self):
        return self.__count

    def getPos(self):
        return self.__pos

    def getParent(self):
        return self.__parent

    def getDirPath(self):
        return self.__dirPath

    def getNodePath(self):
        return self.__nodePath


class pkgItemThread(threading.Thread):
    def __init__(self, pkgItem, pkgPath, pkgedFilePathList):
        super(pkgItemThread, self).__init__()
        self.__item = pkgItem
        self.__path = pkgPath
        self.__pkgedFilePathList = pkgedFilePathList
        self.__running = False
        self.daemon = True

    def getPkgItem(self):
        return self.__item

    def run(self):
        global searchNodes
        # 如果 item 类型为 文件 或者 文件夹，将 文件 或 文件夹 拷贝到目标路径下。
        self.__running = True
        yl.debug('start running pkgItemThread, package item: %s, type is: %s, status is: %s' % (self.__item.getValue(), self.__item.getType(), self.__item.getStatus()))
        if self.__item.getType() in (pkgItemType.FILE, pkgItemType.DIR):
            yl.debug('%s is a file or directory' % self.__item.getValue())
            if self.__item.getParent().getStatus() != pkgStatus.PKGED:
                pkgPath = os.path.join(self.__path, '/'.join(self.__item.getParent().getNodePath().split('.')), os.path.basename(self.__item.getDirPath()))
                yl.debug(pkgPath)
                if not os.path.exists(pkgPath):
                    try:
                        os.makedirs(pkgPath)
                    except Exception as e:
                        yl.error(e.message)
                # 拷贝文件
                dst = os.path.join(pkgPath, self.__item.getValue())
                if os.path.exists(dst):
                    yl.debug('%s is exist, try to remove it' % self.__item.getValue())
                    try:
                        shutil.rmtree(dst)
                    except Exception as e:
                        yl.error(e.message)
                yl.debug('copy %s to %s' % (os.path.join(self.__item.getDirPath(), self.__item.getValue()), dst))
                try:
                    shutil.copy(os.path.join(self.__item.getDirPath(), self.__item.getValue()), dst)
                    self.__item.setStatus(pkgStatus.PKGED)
                    self.__item.callback(self, 1)
                except Exception as e:
                    yl.error(e.message)
        # 如果 item 类型为 节点，替换节点的文件路径。
        elif self.__item.getType() == pkgItemType.NODE:
            yl.debug('%s is a node' % self.__item.getValue())
            pkgPath = os.path.join(self.__path, '/'.join(self.__item.getNodePath().split('.')))
            filePath = os.path.join(pkgPath, os.path.basename(os.path.dirname(self.__item.getDirPath())), os.path.basename(self.__item.getDirPath())).replace('\\', '/')
            if self.__item.getDirPath() not in self.__pkgedFilePathList:
                self.__pkgedFilePathList[self.__item.getDirPath()] = filePath
            else:
                filePath = self.__pkgedFilePathList[self.__item.getDirPath()]
                self.__item.setStatus(pkgStatus.PKGED)
            n = nuke.toNode(self.__item.getNodePath())
            for nodeClass, knob, conditionKnob, conditionKnobValue in searchNodes:
                if n.Class() == nodeClass:
                    n[knob].setValue(filePath)
        # 如果 item 类型为 spaceroot，则在目录下创建同名的文件夹。
        elif self.__item.getType() == pkgItemType.SPACEROOT:
            yl.debug('%s is a root namespace' % self.__item.getValue())
            pkgPath = self.__path
            if not os.path.exists(pkgPath):
                try:
                    os.makedirs(pkgPath)
                except Exception as e:
                    yl.error(e.message)
            try:
                # 保存 Nuke 脚本到该目录下
                nuke.scriptSaveAs(os.path.join(self.__path, self.__item.getValue()), 1)
                self.__item.setStatus(pkgStatus.PKGED)
                self.__item.callback(self, 1)
            except Exception as e:
                yl.error(e.message)
        else:
            yl.debug('%s is not a file or directory, pass' % self.__item.getValue())
        self.__running = False
        yl.debug('%s thread is completed' % self.__item.getValue())

    def isRunning(self):
        return self.__running


class pkgProcess(object):
    def __init__(self):
        self.__percent = 0

    def setPercent(self, p):
        self.__percent = p

    def callback(self, n):
        '''
        n value:
            0: valueChanged
        '''
        if n == 0 and yCallbacks.valueChangedCallback:
            try:
                for c in yCallbacks.valueChangedCallback:
                    c[0](*c[1])
            except Exception as e:
                yl.error(e.message)


class pkgGetFilesThread(threading.Thread):
    def __init__(self):
        super(pkgGetFilesThread, self).__init__()
        self.__spaceRoot = None
        self.__isRunning = False

    def run(self):
        self.__isRunning = True
        self.getFiles()
        self.__isRunning = False
        self.callback(self, 7)

    def isRunning(self):
        return self.__isRunning

    def spaceRoot(self):
        if not self.__isRunning:
            return self.__spaceRoot
        else:
            yl.info('正在获取文件信息，请稍后...')

    def getFiles(self):
        if not nuke.root()['name'].value():
            yl.warning('save script first')
            return
        yl.info('start getting file list')
        # get files callback
        self.callback(self, 6)
        # 初始化根 spaceRoot
        yl.debug('create script namespace')
        self.__spaceRoot = pkgItem(value=os.path.basename(nuke.root()['name'].value()), status=pkgStatus.NORMAL, itemtype=pkgItemType.SPACEROOT)
        self.__spaceRoot.setDirPath(os.path.dirname(nuke.root()['name'].value()))
        # spaceRootCallback
        self.callback(self.__spaceRoot, 0)
        yl.debug('get root and group node, named space')
        for spaces in self.getSpaces():
            for space in spaces:
                sp = pkgItem(parent=self.__spaceRoot, value=space, status=pkgStatus.NORMAL, itemtype=pkgItemType.SPACE)
                sp.setNodePath(space)
                yl.debug('create space: %s' % sp.getValue())
                # perSpaceCallback
                self.callback(sp, 2)
                self.__spaceRoot.appendItem(sp)
                self.getFilesInSpace(sp)
        yl.info('getting files list complete')
        return

    def getFilesInSpace(self, spaceItem):
        global searchNodes
        # perNodeClassCallback
        callbackType = 2
        yl.debug('get node class')
        for index, node in enumerate(searchNodes):
            pi = pkgItem(parent=spaceItem, value=node[0], status=pkgStatus.NORMAL, itemtype=pkgItemType.NODECLASS, pos=index)
            pi.setNodePath('.'.join((spaceItem.getNodePath(), pi.getValue())))
            yl.debug('create node class: %s' % pi.getValue())
            self.callback(pi, callbackType)
            spaceItem.appendItem(pi)
            self.getNodeFilePath(pi, node[1], node[2], node[3])

    def getNodeFilePath(self, nodeClassItem, knob, conditionKnob=None, conditionValue=None):
        # perNodeFilePathCallback
        callbackType = 3
        nodes = [n for n in nuke.toNode(nodeClassItem.getParent().getNodePath()).nodes() if n.Class() == nodeClassItem.getValue()]
        yl.debug('get nodes')
        for index, node in enumerate(nodes):
            if node.knob(knob) and (conditionKnob is None or (node.knob(conditionKnob) and node[conditionKnob].getValue() is conditionValue)):
                path = node[knob].getValue()
                pi = pkgItem(parent=nodeClassItem, value=node.name(), status=pkgStatus.NORMAL, itemtype=pkgItemType.NODE, pos=index)
                pi.setDirPath(node[knob].value())
                pi.setNodePath('.'.join((nodeClassItem.getParent().getNodePath(), node.name())))
                yl.debug('get node: %s' % pi.getValue())
                self.callback(pi, callbackType)
                nodeClassItem.appendItem(pi)
                self.pathAnalysis(pi, path)

    def pathAnalysis(self, nodePathItem, path):
        # this function used to get file one by one, so call perFileCallback.
        callbackType = 4
        bn = os.path.basename(path)
        pdir = os.path.dirname(path)
        pattern = re.compile(r'^(.*)\.?((#+)|%(\d*)d)\.?(\w+)$')
        result = pattern.match(bn)
        if os.path.exists(path):
            if os.path.isdir(path):
                pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NORMAL, itemtype=pkgItemType.DIR, count=1)
                pi.setDirPath(pdir)
                yl.debug('create dir: %s' % pi.getValue())
            else:
                pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NORMAL, itemtype=pkgItemType.FILE, count=1)
                pi.setDirPath(pdir)
                yl.debug('create file: %s' % pi.getValue())
            self.callback(pi, callbackType)
            nodePathItem.appendItem(pi)
        elif not os.path.exists(pdir):
            pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NOEXISTS, itemtype=pkgItemType.FILE)
            pi.setDirPath(pdir)
            self.callback(pi, callbackType)
            yl.debug('create do not exist file: %s' % pi.getValue())
            nodePathItem.appendItem(pi)
        elif result:
            yl.debug('this is a sequence analysis')
            numLenth = (result.groups()[2] and len(result.groups()[2])) or (result.groups()[1] and ((result.groups()[3] and int(result.groups()[3])) or 1))
            if result:
                fn = 0
                newPattern = re.compile(result.groups()[0] + r'\.?(\d{%d,})' % numLenth + r'\.?' + result.groups()[4] + '$')
                for obj in os.listdir(pdir):
                    result = newPattern.match(obj)
                    if result and (len(result.groups()[0]) == numLenth or len(result.groups()[0]) > numLenth and not result.groups()[0].startswith('0')):
                        pi = pkgItem(parent=nodePathItem, value=obj, status=pkgStatus.NORMAL, itemtype=pkgItemType.FILE, count=1, pos=fn)
                        pi.setDirPath(pdir)
                        yl.debug('create a file from sequence: %s' % pi.getValue())
                        self.callback(pi, callbackType)
                        nodePathItem.appendItem(pi)
                        fn += 1
            if fn == 0:
                pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NOEXISTS, itemtype=pkgItemType.FILE, count=0)
                pi.setDirPath(pdir)
                yl.debug('create do not exist file: %s' % pi.getValue())
                self.callback(pi, callbackType)
                nodePathItem.appendItem(pi)
        else:
            pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NOEXISTS, itemtype=pkgItemType.FILE, count=0)
            pi.setDirPath(pdir)
            yl.debug('create do not exist file: %s' % pi.getValue())
            self.callback(pi, callbackType)
            nodePathItem.appendItem(pi)

    def getSpaces(self):
        spaces = ['root']
        while len(spaces) > 0:
            yield spaces
            spaces = ['.'.join((s, n.name())) for s in spaces for n in nuke.toNode(s).nodes() if n.Class() == 'Group']

    def callback(self, item, n):
        '''
        n value:
            0: spaceRoot
            1: space
            2: nodeclass
            3: nodefilepath
            4: filepath
            5: package file
            6: start get files
            7: get files complete
        '''
        if n == 0 and yCallbacks.spaceRootCallback:
            try:
                for c in yCallbacks.spaceRootCallback:
                    c[0](item, *c[1])
            except Exception as e:
                yl.error(e.message)
        elif n == 1 and yCallbacks.perSpaceCallback:
            try:
                for c in yCallbacks.perSpaceCallback:
                    c[0](item, *c[1])
            except Exception as e:
                yl.error(e.message)
        elif n == 2 and yCallbacks.perNodeClassCallback:
            try:
                for c in yCallbacks.perNodeClassCallback:
                    c[0](item, *c[1])
            except Exception as e:
                yl.error(e.message)
        elif n == 3 and yCallbacks.perNodeFilePathCallback:
            try:
                for c in yCallbacks.perNodeFilePathCallback:
                    c[0](item, *c[1])
            except Exception as e:
                yl.error(e.message)
        elif n == 4 and yCallbacks.perFileCallback:
            try:
                for c in yCallbacks.perFileCallback:
                    c[0](item, *c[1])
            except Exception as e:
                yl.error(e.message)
        elif n == 5 and yCallbacks.perPkgFileCallback:
            try:
                for c in yCallbacks.perPkgFileCallback:
                    c[0](item, *c[1])
            except Exception as e:
                yl.error(e.message)
        elif n == 6 and yCallbacks.startGetFilesCallback:
            try:
                for c in yCallbacks.startGetFilesCallback:
                    c[0](item, *c[1])
            except Exception as e:
                yl.error(e.message)
        elif n == 7 and yCallbacks.getFilesCompleteCallback:
            try:
                for c in yCallbacks.getFilesCompleteCallback:
                    c[0](item, *c[1])
            except Exception as e:
                yl.error(e.message)


class pkgProj(object):
    def __init__(self):
        self.__spaceRoot = None
        self.__perNodeClassCallback = ()
        self.__perNodeFilePathCallback = ()
        self.__perFileCallback = ()
        self.__isGettingFiles = False
        self.__pkgedFilePath = {}
        self.__itemThreadQueueEmpty = False
        self.__queue = Queue.Queue()
        self.__isPackaging = False
        self.__pkgThreadQueue = None
        self.setCallback()

    def __del__(self):
        self.queueStop()

    def printRootTree(self):
        if self.__spaceRoot:
            print self.__spaceRoot
            for idr, r in enumerate(self.__spaceRoot.children()):
                print '├─' + r.getValue()
                for idi, i in enumerate(r.children()):
                    print '│ ├─' + i.getValue()
                    for idj, j in enumerate(i.children()):
                        print '│ │ ├─' + j.getValue()
                        for idn, n in enumerate(j.children()):
                            print '│ │ │ ├─' + n.getValue()
        else:
            yl.warning('spaceRoot 不存在，请先保存工程')

    def getFiles(self):
        if not self.__isGettingFiles:
            self.__isGettingFiles = True
            yl.debug('create getting file thread')
            getFilesThread = pkgGetFilesThread()
            yl.debug('start get file list thread')
            getFilesThread.start()
        else:
            yl.warning('getting file list, please wait a moment...')

    def __getFilesComplete(self, getFilesThread):
        if isinstance(getFilesThread, pkgGetFilesThread):
            self.__spaceRoot = getFilesThread.spaceRoot()
            self.__isGettingFiles = False

    def queueStart(self):
        self.__pkgThreadQueue = pkgItemThreadQueue(self.__queue)
        self.__pkgThreadQueue.start()

    def queueStop(self):
        if isinstance(self.__pkgThreadQueue, pkgItemThreadQueue):
            self.__pkgThreadQueue.stop()

    def waittingGetFiles(self):
        while self.__isGettingFiles:
            yl.debug('获取文件线程正在运行，等待 0.5 秒')
            time.sleep(0.5)

    def waittingQueueEmpty(self):
        while not self.__itemThreadQueueEmpty:
            yl.debug('线程池中还有线程正在运行，等待 1 秒')
            time.sleep(1)

    def __setItemThreadQueueEmpty(self, empty):
        if empty in (1, 0, True, False):
            yl.debug('set __itemThreadQueueEmpty %s' % empty)
            self.__itemThreadQueueEmpty = empty
        else:
            yl.error('need boolean')

    def __setIsNotPackaging(self):
        self.__isPackaging = False

    def setCallback(self):
        yl.debug('put __getFilesComplete function in getFilesCompleteCallback')
        yCallbacks.getFilesCompleteCallback.append((self.__getFilesComplete, ()))
        yCallbacks.pkgGuiShowCallback.append((self.queueStart, ()))
        yCallbacks.pkgGuiCloseCallback.append((self.queueStop, ()))
        yCallbacks.pkgItemThreadQueueEmptyCallback.append((self.__setItemThreadQueueEmpty, (True,)))
        yCallbacks.pkgItemThreadQueueEmptyCallback.append((self.__setIsNotPackaging, ()))
        yCallbacks.pkgItemThreadQueueNotEmptyCallback.append((self.__setItemThreadQueueEmpty, (False,)))

    def pkgItems(self, path):
        if not self.__isPackaging:
            self.__isPackaging = True
            if os.path.isdir(path):
                self.__pkgedFilePath = {}
                for items in self.walkItems():
                    for index, item in enumerate(items):
                        yl.debug('add pkg item:%s to thread queue' % item.getValue())
                        self.__queue.put(pkgItemThread(item, path, self.__pkgedFilePath))
            else:
                yl.error('path: %s is not exists' % path)
        else:
            yl.warning('packaging, wait a moment')

    def walkItems(self):
        childrens = [self.__spaceRoot]
        while childrens:
            yield childrens
            childrens = [j for i in childrens for j in i.children()]


class pkgQSignals(QtCore.QObject):
    logSignal = QtCore.Signal(str)


class pkgLogWidget(QtGuiWidgets.QTextEdit):
    def __init__(self, parent=None):
        super(pkgLogWidget, self).__init__(parent)

    def write(self, msg):
        self.textCursor().insertText(msg)


class pkgProjGUI(QtGuiWidgets.QWidget):
    def __init__(self):
        super(pkgProjGUI, self).__init__()
        self.init()

    def getNukeWindow(self):
        app = QtCore.QCoreApplication.instance()
        for w in app.topLevelWidgets():
            if w.metaObject().className() == 'Foundry::UI::DockMainWindow':
                return w

    def init(self):
        self.setParent(self.getNukeWindow())
        self.setWindowTitle('nuke 打包工具')
        self.resize(1000, 500)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.mainLayout = QtGuiWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # path widget
        self.pathFrame = QtGuiWidgets.QFrame()
        self.pathLayout = QtGuiWidgets.QHBoxLayout()
        self.pathLabel = QtGuiWidgets.QLabel('打包路径')
        self.pathField = QtGuiWidgets.QLineEdit('请输入打包路径')
        self.pathBrowserButton = QtGuiWidgets.QPushButton('浏览')
        self.pathBrowserButton.clicked.connect(self.browserPath)
        self.pathLayout.addWidget(self.pathLabel)
        self.pathLayout.addWidget(self.pathField)
        self.pathLayout.addWidget(self.pathBrowserButton)
        self.pathFrame.setLayout(self.pathLayout)

        # update list
        self.updateButtonFrame = QtGuiWidgets.QFrame()
        self.updateButtonLayout = QtGuiWidgets.QHBoxLayout()
        self.updateButtonFrame.setLayout(self.updateButtonLayout)
        self.updateButton = QtGuiWidgets.QPushButton('刷新')
        self.updateButtonLayout.addWidget(self.updateButton)

        # nodeClass, nodeName, files treeView
        self.fileFrame = QtGuiWidgets.QFrame()
        self.fileLayout = QtGuiWidgets.QVBoxLayout()
        self.fileFrame.setLayout(self.fileLayout)
        self.fileTreeWidget = QtGuiWidgets.QTreeWidget()
        self.fileTreeWidget.setColumnCount(2)
        self.fileTreeWidget.setHeaderLabels(['名称', '数量'])
        self.fileLayout.addWidget(self.fileTreeWidget)
        self.fileTreeWidget.setColumnWidth(0, 800)

        # infomation of node, files
        self.infoFrame = QtGuiWidgets.QFrame()
        self.infoLayout = QtGuiWidgets.QHBoxLayout()
        self.infoFrame.setLayout(self.infoLayout)
        self.infoNodeCountLabel = QtGuiWidgets.QLabel('节点总数:')
        self.infoFileCountLabel = QtGuiWidgets.QLabel('文件总数:')
        self.infoCopyedFileCountLabel = QtGuiWidgets.QLabel('已复制:')
        self.infoLayout.addWidget(self.infoNodeCountLabel)
        self.infoLayout.addWidget(self.infoFileCountLabel)
        self.infoLayout.addWidget(self.infoCopyedFileCountLabel)

        self.fileLayout.addWidget(self.infoFrame)

        # package button
        self.packageFrame = QtGuiWidgets.QFrame()
        self.packageLayout = QtGuiWidgets.QHBoxLayout()
        self.packageFrame.setLayout(self.packageLayout)
        self.packageButton = QtGuiWidgets.QPushButton('打包')
        self.packageLayout.addWidget(self.packageButton)

        # log
        self.logFrame = QtGuiWidgets.QFrame()
        self.logLayout = QtGuiWidgets.QVBoxLayout()
        self.logFrame.setLayout(self.logLayout)
        self.logWidget = pkgLogWidget()
        self.logWidget.setReadOnly(True)
        self.logLayout.addWidget(self.logWidget)

        # add frames to main layout
        self.mainLayout.addWidget(self.pathFrame)
        self.mainLayout.addWidget(self.updateButtonFrame)
        self.mainLayout.addWidget(self.fileFrame)
        self.mainLayout.addWidget(self.packageButton)
        self.mainLayout.addWidget(self.logFrame)

    def setPkgPath(self, path):
        self.pathField.setText(unitePath(path))

    def browserPath(self):
        dirPath = QtGuiWidgets.QFileDialog.getExistingDirectory(
            None, 'Package Directory Path', QtCore.QDir.homePath(),
            QtGuiWidgets.QFileDialog.ShowDirsOnly)
        if dirPath:
            self.setPkgPath(dirPath)

    def updateTreeView(self, item):
        if isinstance(item, pkgItem):
            qitem = QtGuiWidgets.QTreeWidgetItem()
            qitem.setText(0, item.getValue())
            qitem.setText(1, str(item.getCount()))
            if item.getType() == pkgItemType.SPACEROOT:
                self.fileTreeWidget.addTopLevelItem(qitem)
            elif item.getType() == pkgItemType.SPACE:
                self.fileTreeWidget.topLevelItem(
                    0).insertChild(item.getPos(), qitem)
            elif item.getType() == pkgItemType.NODECLASS:
                self.fileTreeWidget.topLevelItem(0).child(
                    item.getParent().getPos()).insertChild(item.getPos(), qitem)
            elif item.getType() == pkgItemType.NODE:
                self.fileTreeWidget.topLevelItem(0).child(
                    item.getParent().getParent().getPos()).child(item.getParent().getPos()).insertChild(item.getPos(), qitem)
            elif item.getType() in (pkgItemType.DIR, pkgItemType.FILE):
                self.fileTreeWidget.topLevelItem(0).child(item.getParent().getParent().getParent().getParent().getPos()).child(
                    item.getParent().getParent().getPos()).child(item.getParent().getPos()).insertChild(item.getPos(), qitem)
        else:
            yl.error(
                'TypeError: item need pkgItem, but recevie a %s.' % type(item))

    def updateItemCount(self, item):
        if isinstance(item, pkgItem):
            if item.getType() == pkgItemType.SPACEROOT:
                self.fileTreeWidget.topLevelItem(
                    0).setText(1, str(item.getCount()))
            elif item.getType() == pkgItemType.SPACE:
                self.fileTreeWidget.topLevelItem(0).child(
                    item.getPos()).setText(1, str(item.getCount()))
            elif item.getType() == pkgItemType.NODECLASS:
                self.fileTreeWidget.topLevelItem(0).child(item.getParent().getPos()).child(
                    item.getPos()).setText(1, str(item.getCount()))
            elif item.getType() == pkgItemType.NODE:
                self.fileTreeWidget.topLevelItem(0).child(item.getParent().getParent().getPos()).child(
                    item.getParent().getPos()).child(item.getPos()).setText(1, str(item.getCount()))
            elif item.getType() in (pkgItemType.DIR, pkgItemType.FILE):
                self.fileTreeWidget.topLevelItem(0).child(item.getParent().getParent().getParent().getPos()).child(item.getParent(
                ).getParent().getPos()).child(item.getParent().getPos()).child(item.getPos()).setText(1, str(item.getCount()))
        else:
            yl.error(
                'TypeError: item need pkgItem, but recevie a %s.' % type(item))

    def clearTree(self):
        self.fileTreeWidget.clear()

    def closeEvent(self, event):
        self.callback(0)

    def showEvent(self, event):
        self.callback(1)

    def callback(self, n):
        '''
        n value:
            0: close event
            1: show event
        '''
        if n == 0 and yCallbacks.pkgGuiCloseCallback:
            try:
                for c in yCallbacks.pkgGuiCloseCallback:
                    c[0](*c[1])
            except Exception as e:
                yl.error(e.message)
        if n == 1 and yCallbacks.pkgGuiShowCallback:
            try:
                for c in yCallbacks.pkgGuiShowCallback:
                    c[0](*c[1])
            except Exception as e:
                yl.error(e.message)


class pkgMain(object):
    def __init__(self):
        self.signals = pkgQSignals()
        self.initPkg()
        self.setLogger(yl)
        self.setCallback()
        self.connectButton()
        self.connectSignals()

    def initPkg(self):
        self.ypkg = pkgProj()
        self.ypkgGUI = pkgProjGUI()

    def show(self):
        self.ypkgGUI.show()

    def setLogger(self, logger):
        logger.setHandler(self)

    def write(self, msg):
        self.signals.logSignal.emit(msg)

    def setCallback(self):
        yCallbacks.spaceRootCallback.append((self.ypkgGUI.updateTreeView, ()))
        yCallbacks.perSpaceCallback.append((self.ypkgGUI.updateTreeView, ()))
        yCallbacks.perNodeClassCallback.append((self.ypkgGUI.updateTreeView, ()))
        yCallbacks.perNodeFilePathCallback.append((self.ypkgGUI.updateTreeView, ()))
        yCallbacks.perFileCallback.append((self.ypkgGUI.updateTreeView, ()))
        yCallbacks.countChangedCallback.append((self.ypkgGUI.updateItemCount, ()))

    def connectButton(self):
        yl.debug('start to connect functions to buttons')
        self.ypkgGUI.updateButton.clicked.connect(self.updateButtonFun)
        self.ypkgGUI.packageButton.clicked.connect(self.pkgButtonFun)

    def connectSignals(self):
        self.signals.logSignal.connect(self.ypkgGUI.logWidget.write)

    def updateButtonFun(self):
        yl.debug('connect updateButtonFun function to update button')
        self.ypkgGUI.clearTree()
        self.ypkg.getFiles()

    def pkgButtonFun(self):
        pkgPath = self.ypkgGUI.pathField.text()
        self.ypkg.pkgItems(pkgPath)


if __name__ == '__main__':
    test = pkgMain()
    test.show()
