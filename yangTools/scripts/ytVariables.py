#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : scriptsytVariables.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 04.03.2019
# Last Modified Date: 13.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>


class ytCaller():
    yt_caller_gui = 0
    yt_caller_nuke = 1
    yt_caller_isGuiCallback = False
    yt_caller_isNukeCallback = False


class ytIcon():
    ytIcon_status_running = 0
    ytIcon_status_stopped = 1


class ytNukeWidgets():
    yt_widgets = ['Viewer',
                  'Toolbar',
                  'Dope Sheet',
                  'Error Console',
                  'Background Renders',
                  'Progress',
                  'Profile',
                  'Curve Editor',
                  'Script Editor',
                  'Properties',
                  'Pixel Analyzer',
                  'Node Graph']
    yt_current_widget = yt_widgets[2]
