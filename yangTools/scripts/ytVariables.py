#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : ytVariables.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 04.03.2019
# Last Modified Date: 12.03.2019
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
    yt_widget_viewer = 'Viewer'
    yt_widget_toolbar = 'Toolbar'
    yt_widget_dopesheet = 'Dope Sheet'
    yt_widget_errorconsole = 'Error Console'
    yt_widget_backgroundrenders = 'Background Renders'
    yt_widget_progress = 'Progress'
    yt_widget_profile = 'Profile'
    yt_widget_curveeditor = 'Curve Editor'
    yt_widget_scripteditor = 'Script Editor'
    yt_widget_properties = 'Properties'
    yt_widget_pixelanalyzer = 'Pixel Analyzer'
    yt_widget_nodegraph = 'Node Graph'
    yt_current_widget = yt_widget_dopesheet
