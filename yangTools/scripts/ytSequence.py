#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : ytSequence.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 10.03.2019
# Last Modified Date: 12.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

#  from ytLoggingSettings import yl


import re
import os
import string
from ytLoggingSettings import yl


class sequence():
    '''
    path : /home/test/abc.(###|%03d).exr.
    pattern : abc.\d{3,}.exr <= a regex format path
    prefix name : abc
    ext : exr
    seqMark : ### or %03d
    markLenth : len(###)
    '''

    def __init__(self, path='', start=0, last=0, frames=[], pattern='', regex=r'^(.*?\.?)((#+)|%(\d*)d)(\.?\w+)$'):
        self.__path = path
        self.__start = start
        self.__last = last
        self.__frames = frames[:]
        self.__pattern = pattern
        self.__regex = regex
        self.__seqMark = ''

    def __str__(self):
        lists = self.optimizeList()
        if lists:
            l = len(lists)
            if l == 1:
                return 'sequence: %s\nall: %d lost: 0\nlostFrames: [] existentFrames: [%d-%d]' % (self.__path, len(lists[0]), lists[0][0], lists[0][-1])
            existentFrames = ''
            lostFrames = ''
            i = 0
            while i < l - 1:
                existentFrames += '[%d-%d], ' % (lists[i][0], lists[i][-1])
                lostFrames += '[%d-%d], ' % (lists[i][-1]+1, lists[i + 1][0]-1)
                i += 1
            existentFrames += '[%d-%d], ' % (lists[i][0], lists[i][-1])

            return 'sequence: %s\nall: %d lost: %d\nlostFrames: %s\nexistentFrames: %s' % (self.__path, self.__last - self.__start + 1, self.__last - self.__start + 1 - len(self.__frames), lostFrames[:-2], existentFrames[:-2])
        else:
            return 'sequence: %s\nall: %d lost: 0\nlostFrames: [] existentFrames: [%d-%d]' % (self.__path, 0, 0, 0)

    def setPath(self, path):
        '''
        set sequence path
        '''
        self.__path = path

    def setFrames(self, frames):
        '''
        set sequence frames
        '''
        self.__frames = frames.sort()
        self.__start = min(frames)
        self.__last = max(frames)

    def setPattern(self, pattern):
        '''
        set pattern
        '''
        self.__pattern = pattern

    def actualFrames(self):
        '''
        get actual frames
        '''
        return self.__frames

    def start(self):
        return self.__start

    def last(self):
        return self.__last

    def seqMark(self):
        return self.__seqMark

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
        if len(self.__frames) > 0:
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
        else:
            yl.error('there is noting in frames, please ensure there are files in this path ,then call scan method to get frames')

    def path(self):
        '''
        return path
        '''
        return self.__path

    def pattern(self):
        '''
        return regex pattern that matched files
        '''
        return self.__pattern

    def scan(self, files, resetStartAndLast=True):
        '''
        use pattern to scan files in frame range
        '''
        if len(files) > 0:
            yl.debug('start scan sequence: %s' % self.__path)
            analizePathPattern = re.compile(self.__regex)
            result = analizePathPattern.match(os.path.basename(self.__path))
            self.__seqMark = result.group(2)
            yl.debug('path pattern: %s' % str(result.groups()))
            numLenth = (result.groups()[2] and len(result.groups()[2])) or (result.groups()[1] and ((result.groups()[3] and int(result.groups()[3])) or 1))
            preName =re.sub(r'([%s])' % string.punctuation, r'\\\1', result.group(1))
            self.__pattern = preName + r'\.?(\d{%d,})' % numLenth + r'\.?' + result.groups()[4] + '$'
            yl.debug('file pattern: %s' % self.__pattern)
            self.pathPattern = re.compile(self.__pattern)
            i = 0
            while i<len(files):
                result = self.pathPattern.match(files[i])
                if result and (len(result.groups()[0]) == numLenth or len(result.groups()[0]) > numLenth and not result.groups()[0].startswith('0')):
                    files.pop(i)
                    self.__frames.append(int(result.groups()[0]))
                    continue
                else:
                    i+=1
            self.__frames.sort()

            if resetStartAndLast and len(self.__frames) > 0:
                self.__start = min(self.__frames)
                self.__last = max(self.__frames)
            return files
        else:
            yl.debug('scan files is empty')


    def move(self, newName=None, newDirname=None, replace=False):
        '''
        move file
        if newName is None, keep name as source
        if newDirname is None, just like rename
        if replace is True, if destination path is exists, remove it, than move.
        '''
        # newName analize
        dirname = os.path.dirname(self.__path)
        if newDirname is None:
            newDirname = dirname
        if newName is None:
            newName = os.path.basename(self.__path)
        analizePathPattern = re.compile(self.__regex)
        newNameResult = analizePathPattern.match(newName)
        if newNameResult:
            result = analizePathPattern.match(os.path.basename(self.__path))
            for num in self.__frames:
                fileName = ''.join((result.group(1), str(seq2num(num, result.group(2))), result.group(5)))
                newName = ''.join((newNameResult.group(1), str(seq2num(num, newNameResult.group(2))), newNameResult.group(5)))
                if newName != fileName or newDirname != dirname:
                    if os.path.exists(os.path.join(newDirname, newName)):
                        if replace:
                            try:
                                os.remove(os.path.join(newDirname, newName))
                                yl.warning('destination is exists ,remove it')
                            except Exception, e:
                                yl.error(e.message)
                        else:
                            yl.warning('rename failed, destination is exists, pass')
                            continue
                    try:
                        os.rename(os.path.join(dirname, fileName), os.path.join(newDirname, newName))
                    except Exception, e:
                        yl.error(e.message)
                    yl.debug('rename file: {} => {}'.format(fileName, newName))
                else:
                    yl.warning('rename failed, destination name is the same as source name')
        else:
            yl.error('newName format error, for example: abc.###.dpx, abc.%05d.dpx')


def scanPath(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    regex = r'^(.*?\.?)(\d*)(\.?\w+)$'  # used to analize the path of sequence
    pattern = re.compile(regex)
    filePatterns = []
    seqs = []
    #  filePattern = []
    for f in files:
        result = pattern.match(f)
        if result:
            seqMarks = num2seq(result.group(2))
            for sm in seqMarks:
                compare = ''.join([result.group(1), sm, result.group(3)])
                if compare not in filePatterns:
                    filePatterns.append(compare)
                else:
                    break
    for fp in filePatterns:
        seq = sequence(path=os.path.join(path, fp).replace('\\', '/'))
        files = seq.scan(files, True)
        seqs.append(seq)
    return seqs


def num2seq(num):
    if num.isdigit():
        seqNum = []
        if len(num) == 1:
            seqNum.append('%d')
        elif (len(num) > 1 and not num.startswith('0')):
            seqNum.append('%d')
            seqNum.append('%0{}d'.format(len(num)))
        else:
            seqNum.append('%0{}d'.format(len(num)))
        return seqNum
    else:
        return ''

def seq2num(num, seqMark):
    if seqMark:
        if '#' in seqMark:
            if len(seqMark) == 1:
                return num
            else:
                return '{{:>0{}d}}'.format(len(seqMark)).format(num)
        else:
            return seqMark % num
    else:
        num


if __name__ == '__main__':
    #  seqs = scanPath(r'e:\CG1001')
    #  for seq in seqs:
    #      seq.rename('test')
    path = 'E:/CG1001/abc.#.dpx'
    test = sequence(path=path)
    test.scan(os.listdir(os.path.dirname(path)), True)
    test.move(newDirname='E:/CG1001/abc', replace=True)
