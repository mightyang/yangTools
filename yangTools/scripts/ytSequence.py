#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : ytSequence.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 10.03.2019
# Last Modified Date: 11.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

#  from ytLoggingSettings import yl


import re
import os
from ytLoggingSettings import yl


class sequence():
    '''
    path : /home/test/abc.(###|%03d).exr.
    pattern : abc.\d+.exr <= a regexp format path
    name : abc
    ext : exr
    seqMark : ###
    '''
    __path = ''
    __start = 0
    __last = 0
    __frames = []
    __pattern = ''
    __regexp = r'^(.*?)\.?((#+)|%(\d*)d)\.?(\w+)$'  # used to analize the path of sequence

    def __str__(self):
        lists = self.optimizeList()
        l = len(lists)
        if l == 1:
            return 'all: %d lost: 0\nlostFrames: [] existentFrames: [%d-%d]' % (len(lists[0]), lists[0][0], lists[0][-1])
        existentFrames = ''
        lostFrames = ''
        i = 0
        while i < l-1:
            existentFrames += '[%d-%d], ' % (l[i][0], l[i][-1])
            lostFrames += '[%d-%d], ' % (l[i][-1], l[i+1][0])
            i += 1
        existentFrames += '[%d-%d], ' % (l[i+1][0], l[i+1][-1])

        return 'sequence: %s\nall: %d lost: %d\nlostFrames: %s\nexistentFrames: %s' % (self.__path,  self.__last - self.__start + 1, self.__last - self.__start + 1 - len(self.__frames), lostFrames[:-2], existentFrames[:-2])

    def setPath(self, path):
        '''
        set sequence path
        '''
        self.__path = path

    def setFrames(self, frames):
        '''
        set sequence frames
        '''
        self.__frames = frames

    def actualFrames(self):
        '''
        get actual frames
        '''
        return self.__frames

    def start(self):
        return self.__start

    def last(self):
        return self.__last

    def frames(self):
        return self.__frames

    def lostFrames(self):
        '''
        return lost frames list, or None
        '''
        lost = []
        for i in range(self.__start, self.__last + 1):
            if i not in self.__frames:
                lost.append(i)
        return lost

    def optimizeList(self):
        frameLen = len(self.__frames)
        if frameLen < 2:
            return [self.__frames]
        splittedFrame = []
        splittedList = [self.__frames[0]]
        i = 1
        while i < frameLen:
            if abs(self.__frames[i] - self.__frames[i - 1]) == 1:
                splittedList.append(self.__frames[i])
            else:
                splittedFrame.append(splittedList)
                splittedList = [self.__frames[i]]
            i += 1
        splittedFrame.append(splittedList)
        return splittedFrame

    def path(self):
        '''
        return path
        '''
        return self.__path

    def pattern(self):
        '''
        return regexp pattern that matched files
        '''
        return self.__pattern

    def scan(self, resetStartAndLast=False):
        '''
        use pattern to scan files in frame range
        '''
        yl.debug('start scan sequence: %s' % self.__path)
        analizePathPattern = re.compile(self.__regexp)
        result = analizePathPattern.match(os.path.basename(self.__path))
        yl.debug('path pattern: %s' % str(result.groups()))
        numLenth = (result.groups()[2] and len(result.groups()[2])) or (result.groups()[1] and ((result.groups()[3] and int(result.groups()[3])) or 1))
        self.__pattern = result.groups()[0] + r'\.?(\d{%d,})' % numLenth + r'\.?' + result.groups()[4] + '$'
        self.pathPattern = re.compile(self.__pattern)
        yl.debug('file pattern: %s' % self.pathPattern.pattern)
        for f in os.listdir(os.path.dirname(self.__path)):
            result = self.pathPattern.match(f)
            if result and (len(result.groups()[0]) == numLenth or len(result.groups()[0]) > numLenth and not result.groups()[0].startswith('0')):
                self.__frames.append(int(result.groups()[0]))
        self.__frames.sort()

        if resetStartAndLast:
            self.__start = min(self.__frames)
            self.__last = max(self.__frames)


if __name__ == '__main__':
    t = sequence()
    t.setPath(r'\\192.168.2.3\projects\hdsh\shots\R1\CG1001\B040C006_181012_R30T.MOV.########.dpx')
    t.scan(True)
    print t


#  def pathAnalysis(self, nodePathItem, path):
#      callbackType = 4
#      bn = os.path.basename(path)
#      pdir = os.path.dirname(path)
#      pattern = re.compile(r'^(.*)\.?((#+)|%(\d*)d)\.?(\w+)$')
#      result = pattern.match(bn)
#      if os.path.exists(path):
#          if os.path.isdir(path):
#              pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NORMAL, itemtype=pkgItemType.DIR, count=1)
#              pi.setDirPath(pdir)
#              yl.debug('create dir: %s' % pi.getValue())
#          else:
#              pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NORMAL, itemtype=pkgItemType.FILE, count=1)
#              pi.setDirPath(pdir)
#              yl.debug('create file: %s' % pi.getValue())
#          self.callback(pi, callbackType)
#          nodePathItem.appendItem(pi)
#      elif not os.path.exists(pdir):
#          pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NOEXISTS, itemtype=pkgItemType.FILE)
#          pi.setDirPath(pdir)
#          self.callback(pi, callbackType)
#          yl.debug('create do not exist file: %s' % pi.getValue())
#          nodePathItem.appendItem(pi)
#      elif result:
#          yl.debug('this is a sequence analysis')
#          numLenth = (result.groups()[2] and len(result.groups()[2])) or (result.groups()[1] and ((result.groups()[3] and int(result.groups()[3])) or 1))
#          if result:
#              fn = 0
#              newPattern = re.compile(result.groups()[0] + r'\.?(\d{%d,})' % numLenth + r'\.?' + result.groups()[4] + '$')
#              for obj in os.listdir(pdir):
#                  result = newPattern.match(obj)
#                  if result and (len(result.groups()[0]) == numLenth or len(result.groups()[0]) > numLenth and not result.groups()[0].startswith('0')):
#                      pi = pkgItem(parent=nodePathItem, value=obj, status=pkgStatus.NORMAL, itemtype=pkgItemType.FILE, count=1, pos=fn)
#                      pi.setDirPath(pdir)
#                      yl.debug('create a file from sequence: %s' % pi.getValue())
#                      self.callback(pi, callbackType)
#                      nodePathItem.appendItem(pi)
#                      fn += 1
#          if fn == 0:
#              pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NOEXISTS, itemtype=pkgItemType.FILE, count=0)
#              pi.setDirPath(pdir)
#              yl.debug('create do not exist file: %s' % pi.getValue())
#              self.callback(pi, callbackType)
#              nodePathItem.appendItem(pi)
#      else:
#          pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NOEXISTS, itemtype=pkgItemType.FILE, count=0)
#          pi.setDirPath(pdir)
#          yl.debug('create do not exist file: %s' % pi.getValue())
#          self.callback(pi, callbackType)
#          nodePathItem.appendItem(pi)
