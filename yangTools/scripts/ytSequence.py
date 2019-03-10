#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : ytSequence.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 10.03.2019
# Last Modified Date: 10.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

class sequence():
    path = ''
    start = 0
    end = 0
    miss = []
    name = ''
    ext = ''
    seqMark = ''
    pattern = ''

    def setPath(self, path):
        self.path = path

    def setName(self, name):
        self.name = name


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
