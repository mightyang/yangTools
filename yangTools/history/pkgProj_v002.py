#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : pkgProj.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 31.12.2018
# Last Modified Date: 01.01.2019
# Last Modified By  : yang <mightyang@hotmail.com>


import os
import re
import nuke
import shutil
import threading


if nuke.NUKE_VERSION_MAJOR <= 10:
    print 'Nuke version is %s, import PySide.' % nuke.NUKE_VERSION_STRING
    from PySide import QtGui as QtGuiWidgets
    from PySide import QtCore
elif nuke.NUKE_VERSION_MAJOR > 10:
    print 'Nuke version is %s, import PySide2.' % nuke.NUKE_VERSION_STRING
    from PySide2 import QtGui as QtGuiWidgets
    from PySide2 import QtWidgets as QtGuiWidgets
    from PySide2 import QtCore

# (fun, (argvs))
valueChangedCallback = []
statusChangedCallback = []
countChangedCallback = []
createCallback = []
pkgFileCallback = []

perNodeClassCallback = []
perNodeFilePathCallback = []
perFileCallback = []
perSpaceCallback = []
perPkgFileCallback = []
startGetFilesCallback = []
spaceRootCallback = []
searchNodes = [['Read', 'file', None, None],
               ['ReadGeo', 'file', None, None],
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
    except Exception, e:
        print e.message
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


class pkgItem(object):
    def __new__(cls, parent=None, text='', status=None, count=0, pos=0):
        if not (parent is None or isinstance(parent, pkgItem)):
            print 'parameter type error: parent.'
        elif not isinstance(text, str):
            print 'parameter type error: value.'
        elif status not in pkgStatus.__dict__.values():
            print 'parameter type error: status.'
        elif not isinstance(count, int):
            print 'parameter type error: count.'
        else:
            return object.__new__(cls, text, status, count)

    def __init__(self, parent=None, text='', status=None, count=0, pos=0):
        self.__text = text
        self.__dirPath = None
        self.__status = status
        self.__count = count
        self.__nodePath = None
        self.__list = []
        self.__parent = parent
        self.__pos = pos
        self.callback(self, 3)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.__list[key]
        elif isinstance(key, str):
            for i in self.__list:
                if i.text() == key:
                    return i
        return None

    def __setitem__(self, key, item):
        if isinstance(item, pkgItem):
            if isinstance(key, int):
                self.__list[key] = item
            elif isinstance(key, str):
                for index, it in enumerate(self.__list):
                    if it.text() == key:
                        self.__list[index] = item
                    else:
                        print 'there is no %s key.' % key
        else:
            print 'value must be a pkgItem object.'

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
            print 'item need pkgItem class.'

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
        except Exception, e:
            print e.message
            return
        self.__count -= 1
        self.callback(self, callBackType)

    def insert(self, index, item):
        self.__list.insert(index, item)

    def setText(self, text):
        callbackType = 0
        self.__text = text
        self.callback(text, callbackType)

    def setDirPath(self, path):
        if self.__type in (pkgItemType.FILE, pkgItemType.DIR, pkgItemType.SPACEROOT, pkgItemType.SPACE):
            self.__dirPath = path
        else:
            print "item %s is not a file or dir, please set it's type to file or dir, than set dir path." % self.__value

    def setStatus(self, s):
        callbackType = 1
        if hasattr(pkgStatus, s):
            self.__status = s
            self.callback(s, callbackType)
        else:
            print 'pkgStatus do not have [%s] attribute.' % s

    def setPos(self, pos):
        if isinstance(pos, int):
            self.__pos = pos
        else:
            print 'TypeError: pos need int, but receive a %s.' % type(pos)

    def setNodePath(self, nodePath):
        self.__nodePath = nodePath

    def callback(self, item, n):
        '''
        n value:
            0: valueChanged
            1: statusChanged
            2: countChanged
            3: create
        '''
        global valueChangedCallback
        global statusChangedCallback
        global countChangedCallback
        global createCallback
        if n == 0 and valueChangedCallback:
            try:
                for c in valueChangedCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 1 and statusChangedCallback:
            try:
                for c in statusChangedCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 2 and countChangedCallback:
            try:
                for c in countChangedCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 3 and createCallback:
            try:
                for c in createCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message

    def text(self):
        return self.__text

    def status(self):
        return self.__status

    def count(self):
        return self.__count

    def pos(self):
        return self.__pos

    def parent(self):
        return self.__parent

    def children(self):
        return self.__list

    def dirPath(self):
        return self.__dirPath

    def nodePath(self):
        return self.__nodePath

    def pkg(self, path):
        if self.__type in (pkgItemType.FILE, pkgItemType.DIR, pkgItemType.SPACEROOT):
            pkgPath = os.path.join(path, os.path.basename(self.dirPath()))
            if not os.path.exists(pkgPath):
                try:
                    os.makedirs(pkgPath)
                except Exception, e:
                    print e.message
            try:
                shutil.copy(os.path.join(self.__dirPath, self.__value), os.path.join(pkgPath, self.__value))
                self.__status = pkgStatus.PKGED
                self.callback(self, 1)
            except Exception, e:
                print e.message
        else:
            print 'item %s is not a file or dir, set type to file or dir first.' % self.__value

    def replacePathForNuke(self):
        pass


class pkgSpaceRootItem(pkgItem):
    def __init__(self, parent=None, value='', status=None, count=0, pos=0):
        super(pkgSpaceRootItem).__init__(parent=parent, value=value, status=status, count=count, pos=pos)


class pkgSpaceItem(pkgItem):
    def __init__(self, parent=None, value='', status=None, count=0, pos=0):
        super(pkgSpaceItem).__init__(parent=parent, value=value, status=status, count=count, pos=pos)


class pkgNodeItem(pkgItem):
    def __init__(self, parent=None, value='', status=None, count=0, pos=0):
        super(pkgSpaceRootItem).__init__(parent=parent, value=value, status=status, count=count, pos=pos)


class pkgKnobItem(pkgItem):
    def __init__(self, parent=None, value='', status=None, count=0, pos=0):
        super(pkgSpaceRootItem).__init__(parent=parent, value=value, status=status, count=count, pos=pos)


class pkgFileItem(pkgItem):
    def __init__(self, parent=None, value='', status=None, count=0, pos=0):
        super(pkgSpaceRootItem).__init__(parent=parent, value=value, status=status, count=count, pos=pos)


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

        # add frames to main layout
        self.mainLayout.addWidget(self.pathFrame)
        self.mainLayout.addWidget(self.updateButtonFrame)
        self.mainLayout.addWidget(self.fileFrame)
        self.mainLayout.addWidget(self.packageButton)

    def setPkgPath(self, path):
        self.pathField.setText(unitePath(path))

    def browserPath(self):
        dirPath = QtGuiWidgets.QFileDialog.getExistingDirectory(None, 'Package Directory Path', QtCore.QDir.homePath(), QtGuiWidgets.QFileDialog.ShowDirsOnly)
        if dirPath:
            self.setPkgPath(dirPath)

    def updateTreeView(self, item):
        if isinstance(item, pkgItem):
            qitem = QtGuiWidgets.QTreeWidgetItem()
            qitem.setText(0, item.text())
            qitem.setText(1, str(item.count()))
            if item.getType() == pkgItemType.SPACEROOT:
                self.fileTreeWidget.addTopLevelItem(qitem)
            elif item.getType() == pkgItemType.SPACE:
                self.fileTreeWidget.topLevelItem(0).insertChild(item.pos(), qitem)
            elif item.getType() == pkgItemType.NODECLASS:
                self.fileTreeWidget.topLevelItem(0).child(item.parent().pos()).insertChild(item.pos(), qitem)
            elif item.getType() == pkgItemType.NODE:
                self.fileTreeWidget.topLevelItem(0).child(item.parent().parent().pos()).child(item.parent().pos()).insertChild(item.pos(), qitem)
            elif item.getType() in (pkgItemType.DIR, pkgItemType.FILE):
                self.fileTreeWidget.topLevelItem(0).child(item.parent().parent().parent().pos()).child(item.parent().parent().pos()).child(item.parent().pos()).insertChild(item.pos(), qitem)
        else:
            print 'TypeError: item need pkgItem, but recevie a %s.' % type(item)

    def updateItemCount(self, item):
        if isinstance(item, pkgItem):
            if item.getType() == pkgItemType.SPACEROOT:
                self.fileTreeWidget.topLevelItem(0).setText(1, str(item.count()))
            elif item.getType() == pkgItemType.SPACE:
                self.fileTreeWidget.topLevelItem(0).child(item.pos()).setText(1, str(item.count()))
            elif item.getType() == pkgItemType.NODECLASS:
                self.fileTreeWidget.topLevelItem(0).child(item.parent().pos()).child(item.pos()).setText(1, str(item.count()))
            elif item.getType() == pkgItemType.NODE:
                self.fileTreeWidget.topLevelItem(0).child(item.parent().parent().pos()).child(item.parent().pos()).child(item.pos()).setText(1, str(item.count()))
            elif item.getType() in (pkgItemType.DIR, pkgItemType.FILE):
                self.fileTreeWidget.topLevelItem(0).child(item.parent().parent().parent().pos()).child(item.parent().parent().pos()).child(item.parent().pos()).child(item.pos()).setText(1, str(item.count()))
        else:
            print 'TypeError: item need pkgItem, but recevie a %s.' % type(item)

    def clearTree(self):
        self.fileTreeWidget.clear()


class pkgProj(object):
    __perNodeClassCallback = ()
    __perNodeFilePathCallback = ()
    __perFileCallback = ()
    __isGettingFiles = False
    __spaceRoot = None

    def printRootTree(self):
        print self.__rootItem
        for idr, r in enumerate(self.__rootItem.children()):
            print '├─' + r.text()
            for idi, i in enumerate(r.children()):
                print '│ ├─' + i.text()
                for idj, j in enumerate(i.children()):
                    print '│ │ ├─' + j.text()

    def getFiles(self):
        if self.__isGettingFiles:
            print 'i am getting files, drink a coffee.'
            return
        if not nuke.root().name():
            print 'save project first.'
            return
        self.__isGettingFiles = True
        # start get files callback
        self.callback(self, 6)
        # 初始化根 spaceRoot
        self.__spaceRoot = pkgItem(value=os.path.basename(nuke.root()['name'].value()), status=pkgStatus.NORMAL, itemtype=pkgItemType.SPACEROOT)
        self.__spaceRoot.setDirPath(os.path.dirname(nuke.root()['name'].value()))
        # gst = getSpacesThread(self.__spaceRoot)
        # gnct = getNodeClassThread(self.__spaceRoot)
        # gnfpt = getNodeFilePathThread(self.__spaceRoot)
        # pat = pathAnalysisThread(self.__spaceRoot)
        self.__isGettingFiles = False

    def getFilesInSpace(self, spaceItem):
        # perNodeClassCallback
        callbackType = 2
        # [nodeClass, knob, condition knob, condition value]
        for index, node in enumerate(searchNodes):
            pi = pkgItem(parent=spaceItem, value=node[0], status=pkgStatus.NORMAL, itemtype=pkgItemType.NODECLASS, pos=index)
            self.callback(pi, callbackType)
            spaceItem.appendItem(pi)
            self.getNodeFilePath(pi, node[1], node[2], node[3])

    def getNodeFilePath(self, nodeClassItem, knob, conditionKnob=None, conditionValue=None):
        # perNodeFilePathCallback
        filePaths = []
        callbackType = 3
        nodes = [n for n in nuke.toNode(nodeClassItem.parent().dirPath()).nodes() if n.Class() == nodeClassItem.text()]
        for index, node in enumerate(nodes):
            if node.knob(knob) and (conditionKnob is None or (node.knob(conditionKnob) and node[conditionKnob].value() is conditionValue)):
                path = node[knob].value()
                if path not in filePaths:
                    pi = pkgItem(parent=nodeClassItem, value=node.name(), status=pkgStatus.NORMAL, itemtype=pkgItemType.NODE, pos=index)
                    self.callback(pi, callbackType)
                    nodeClassItem.appendItem(pi)
                    self.pathAnalysis(pi, path)
                    filePaths.append(path)
                else:
                    print "node: %s's path is exists, pass."

    def getSpaces(self):
        spaces = ['root']
        while len(spaces) > 0:
            yield spaces
            spaces = ['.'.join((s, n.name())) for s in spaces for n in nuke.toNode(s).nodes() if n.Class() == 'Group']

    def pathAnalysis(self, nodePathItem, path):
        # means this function used to get file one by one, so call perFileCallback.
        callbackType = 4
        bn = os.path.basename(path)
        pdir = os.path.dirname(path)
        pattern = re.compile(r'^(.*)\.?((#+)|%(\d*)d)\.?(\w+)$')
        result = pattern.match(bn)
        if os.path.exists(path):
            if os.path.isdir(path):
                pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NORMAL, itemtype=pkgItemType.DIR)
                pi.setDirPath(pdir)
            else:
                pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NORMAL, itemtype=pkgItemType.FILE)
                pi.setDirPath(pdir)
            self.callback(pi, callbackType)
            nodePathItem.appendItem(pi)
        elif not os.path.exists(pdir):
            pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NOEXISTS, itemtype=pkgItemType.FILE)
            pi.setDirPath(pdir)
            self.callback(pi, callbackType)
            nodePathItem.appendItem(pi)
        elif result:
            numLenth = (result.groups()[2] and len(result.groups()[2])) or (result.groups()[1] and ((result.groups()[3] and int(result.groups()[3])) or 1))
            if result:
                fn = 0
                newPattern = re.compile(result.groups()[0] + r'\.?(\d{%d,})' % numLenth + r'\.?' + result.groups()[4] + '$')
                for obj in os.listdir(pdir):
                    result = newPattern.match(obj)
                    if result and (len(result.groups()[0]) == numLenth or len(result.groups()[0]) > numLenth and not result.groups()[0].startswith('0')):
                        pi = pkgItem(parent=nodePathItem, value=obj, status=pkgStatus.NORMAL, itemtype=pkgItemType.FILE, count=1, pos=fn)
                        pi.setDirPath(pdir)
                        self.callback(pi, callbackType)
                        nodePathItem.appendItem(pi)
                        fn += 1
            if fn == 0:
                pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NOEXISTS, itemtype=pkgItemType.FILE)
                pi.setDirPath(pdir)
                self.callback(pi, callbackType)
                nodePathItem.appendItem(pi)
        else:
            pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NOEXISTS, itemtype=pkgItemType.FILE)
            pi.setDirPath(pdir)
            self.callback(pi, callbackType)
            nodePathItem.appendItem(pi)

    def walkItems(self):
        childrens = [self.__spaceRoot]
        while childrens:
            yield childrens
            childrens = [j for i in childrens for j in i.children()]

    def pkgItems(self, path):
        if os.path.isdir(path):
            for items in self.walkItems():
                for item in items:
                    item.pkg(path)
        else:
            print 'path: %s is not exists.' % path

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
        '''
        global perNodeClassCallback
        global perNodeFilePathCallback
        global perFileCallback
        global perSpaceCallback
        global perPkgFileCallback
        global startGetFilesCallback
        global spaceRootC
        if n == 0 and spaceRootCallback:
            try:
                for c in spaceRootCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 1 and perSpaceCallback:
            try:
                for c in perSpaceCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 2 and perNodeClassCallback:
            try:
                for c in perNodeClassCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 3 and perNodeFilePathCallback:
            try:
                for c in perNodeFilePathCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 4 and perFileCallback:
            try:
                for c in perFileCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 5 and perPkgFileCallback:
            try:
                for c in perPkgFileCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 6 and startGetFilesCallback:
            try:
                for c in startGetFilesCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message


class getSpacesThread(threading.Thread):
    def __init__(self, spaceRoot):
        super(getSpacesThread, self).__init__()
        self.__spaceRoot = spaceRoot

    def run(self):
        if isinstance(self.__spaceRoot, pkgItem):
            spacesIter = getSpaces()
            for spaces in spacesIter:
                for space in spaces:
                    sp = pkgItem(parent=self.__spaceRoot, value=space, status=pkgStatus.NORMAL, itemtype=pkgItemType.SPACE)
                    sp.setDirPath(space)
                    # perSpaceCallback
                    self.callback(sp)
                    self.__spaceRoot.appendItem(sp)
        else:
            print 'TypeError: need pkgItem, but receive %s.' % type(self.__spaceRoot)

    def callback(self, item):
        global perSpaceCallback
        if len(perSpaceCallback) > 0:
            try:
                for c in perSpaceCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message


class getNodeClassThread(threading.Thread):
    def __init__(self, spaceRoot):
        super(getNodeClassThread, self).__init__()
        self.__spaceRoot = spaceRoot

    def run(self):
        global searchNodes
        for spaceItem in self.__spaceItems:
            # [nodeClass, knob, condition knob, condition value]
            for index, node in enumerate(searchNodes):
                pi = pkgItem(parent=spaceItem, value=node[0], status=pkgStatus.NORMAL, itemtype=pkgItemType.NODECLASS, pos=index)
                self.callback(pi)
                spaceItem.appendItem(pi)

    def callback(self, item):
        global perNodeClassCallback
        if len(perNodeClassCallback) > 0:
            try:
                for c in perNodeClassCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message


class getNodeFilePathThread(threading.Thread):
    def __init__(self, nodeClassItems, knob, conditionKnob=None, conditionValue=None):
        super(getNodeFilePathThread, self).__init__()
        self.__nodeClassItems = nodeClassItems
        self.__knob = knob
        self.__conditionKnob = conditionKnob
        self.__conditionValue = conditionValue

    def run(self):
        for nodeClassItem in self.__nodeClassItems:
            # perNodeFilePathCallback
            filePaths = []
            callbackType = 3
            nodes = [n for n in nuke.toNode(nodeClassItem.parent().dirPath()).nodes() if n.Class() == nodeClassItem.text()]
            for index, node in enumerate(nodes):
                if node.knob(self.__knob) and (self.__conditionKnob is None or (node.knob(self.__conditionKnob) and node[self.__conditionKnob].text() is self._conditionValue)):
                    path = node[self.__knob].value()
                    if path not in filePaths:
                        pi = pkgItem(parent=nodeClassItem, value=node.name(), status=pkgStatus.NORMAL, itemtype=pkgItemType.NODE, pos=index)
                        self.callback(pi, callbackType)
                        nodeClassItem.appendItem(pi)
                        self.pathAnalysis(pi, path)
                        filePaths.append(path)
                    else:
                        print "node: %s's path is exists, pass."

    def callback(self, item):
        global perNodeFilePathCallback
        if len(perNodeFilePathCallback) > 0:
            try:
                for c in perNodeFilePathCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message


class pathAnalysisThread(threading.Thread):
    def __init__(self, nodeItem, path):
        super(pathAnalysisThread, self).__init__(self)
        self.__nodeItem = nodeItem
        self.__path = path

    def run(self):
        # means this function used to get file one by one, so call perFileCallback.
        bn = os.path.basename(self.__path)
        pdir = os.path.dirname(self.__path)
        pattern = re.compile(r'^(.*)\.?((#+)|%(\d*)d)\.?(\w+)$')
        result = pattern.match(bn)
        if os.path.exists(self.__path):
            if os.path.isdir(self._path):
                pi = pkgItem(parent=self.__nodeItem, value=bn, status=pkgStatus.NORMAL, itemtype=pkgItemType.DIR)
                pi.setDirPath(pdir)
            else:
                pi = pkgItem(parent=self.__nodeItem, value=bn, status=pkgStatus.NORMAL, itemtype=pkgItemType.FILE)
                pi.setDirPath(pdir)
            self.callback(pi)
            self.__nodeItem.appendItem(pi)
        elif not os.path.exists(pdir):
            pi = pkgItem(parent=self.__nodeItem, value=bn, status=pkgStatus.NOEXISTS, itemtype=pkgItemType.FILE)
            pi.setDirPath(pdir)
            self.callback(pi)
            self.__nodeItem.appendItem(pi)
        elif result:
            numLenth = (result.groups()[2] and len(result.groups()[2])) or (result.groups()[1] and ((result.groups()[3] and int(result.groups()[3])) or 1))
            if result:
                fn = 0
                newPattern = re.compile(result.groups()[0] + r'\.?(\d{%d,})' % numLenth + r'\.?' + result.groups()[4] + '$')
                for obj in os.listdir(pdir):
                    result = newPattern.match(obj)
                    if result and (len(result.groups()[0]) == numLenth or len(result.groups()[0]) > numLenth and not result.groups()[0].startswith('0')):
                        pi = pkgItem(parent=self.__nodeItem, value=obj, status=pkgStatus.NORMAL, itemtype=pkgItemType.FILE, count=1, pos=fn)
                        pi.setDirPath(pdir)
                        self.callback(pi)
                        self.__nodeItem.appendItem(pi)
                        fn += 1
            if fn == 0:
                pi = pkgItem(parent=self.__nodeItem, value=bn, status=pkgStatus.NOEXISTS, itemtype=pkgItemType.FILE)
                pi.setDirPath(pdir)
                self.callback(pi)
                self.__nodeItem.appendItem(pi)
        else:
            pi = pkgItem(parent=self.__nodeItem, value=bn, status=pkgStatus.NOEXISTS, itemtype=pkgItemType.FILE)
            pi.setDirPath(pdir)
            self.callback(pi)
            self.__nodeItem.appendItem(pi)

    def callback(self, item):
        global perFileCallback
        if len(perFileCallback) > 0:
            try:
                for c in perFileCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message


class getSpaces(threading.Thread):
    def __init__(self):
        super(getSpaces, self).__init__()

    def run(self, spaceRoot):
        pass

    def callback(self, item):
        global spaceRootCallback
        if len(spaceRootCallback) > 0:
            try:
                for c in spaceRootCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message


class pkgMain(object):
    def __init__(self):
        self.ypkg = pkgProj()
        self.ypkgGUI = pkgProjGUI()
        self.setCallback()
        self.connectButton()

    def show(self):
        self.ypkgGUI.show()

    def setCallback(self):
        spaceRootCallback.append((self.ypkgGUI.updateTreeView, ()))
        perSpaceCallback.append((self.ypkgGUI.updateTreeView, ()))
        perNodeClassCallback.append((self.ypkgGUI.updateTreeView, ()))
        perNodeFilePathCallback.append((self.ypkgGUI.updateTreeView, ()))
        perFileCallback.append((self.ypkgGUI.updateTreeView, ()))
        countChangedCallback.append((self.ypkgGUI.updateItemCount, ()))

    def connectButton(self):
        self.ypkgGUI.updateButton.clicked.connect(self.updateButtonFun)
        self.ypkgGUI.packageButton.clicked.connect(self.pkgButtonFun)

    def updateButtonFun(self):
        self.ypkgGUI.clearTree()
        self.ypkg.getFiles()

    def pkgButtonFun(self):
        pkgPath = self.ypkgGUI.pathField.text()
        self.ypkg.pkgItems(pkgPath)


if __name__ == '__main__':
    test = pkgMain()
    test.show()
