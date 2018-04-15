#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2017 seamus tuohy, <code@seamustuohy.com>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the included LICENSE file for details.

import i3
import json
import tkinter as tk
from tkinter import font
from collections import namedtuple
import pretty_chars
import time
import logging
from os import getpid
import subprocess


class Application(tk.Frame):
    theme = {
        "background": '#292d2e',
        "foreground": '#00DA8E',
        "cmd_color": '#3F8AC2',
        "horiz_font_percent": 50,
        "vert_font_percent": 74,
        "font_family": "Robot",
        "font_weight": "bold"}

    ignored_modes = ['default', "resize"]

    def __init__(self, command_path, master=None, theme=None, log=None):
        super().__init__(master)
        if log is None:
            def _logger(x):
                pass
            _log = namedtuple("log", ["debug", 'error', 'warn', 'info'])
            self.log = _log(_logger, _logger, _logger, _logger)
        else:
            self.log = log
        self.window = master
        #self.configure(highlightthickness=0)
        #self.configure(borderwidth=0)
        self.mode_stack = []
        self.get_commands(command_path)
        self.current_mode = 'default'
        if theme:
            self.theme = theme
        self.set_theme()
        self.grid()
        self.text_widgets = []
        self.window.withdraw()

    def get_commands(self, path):
        with open(path, 'r') as cmd_ptr:
            cmd_data = json.load(cmd_ptr)[0]
        self.modes = cmd_data['modes']
        self.escapes = cmd_data['templates']['modes']['escapes']

    def redraw_window(self, data):
        self.log.debug("Redrawing window")
        self.current_mode = data
        self.refresh_command_text()
        self.window.deiconify()

    def go_last_mode(self):
        # Current mode needs to be removed
        # Don't want it added on the stack again
        self.current_mode = None
        # Exit if no stack
        if self.mode_stack == []:
            self.log.debug("No modes found to go back to entering default mode")
            i3.command('mode', "default")
        # Jump to the last mode on the stack
        else:
            last_mode = self.mode_stack.pop()
            self.log.debug("Going back to {0}".format(last_mode))
            i3.command('mode', last_mode)

    def set_theme(self):
        self.background = self.theme['background']
        self.foreground = self.theme['foreground']
        for i in i3.get_workspaces():
            if i['focused'] == True:
                workspace = i
        screen_width = workspace['rect']['width']
        screen_height = workspace['rect']['height']

        if screen_height > screen_width:
            self.horizontal = True
            font_size = int(screen_width/self.theme['horiz_font_percent'])
        else:
            self.horizontal = False
            font_size = int(screen_width/self.theme['vert_font_percent'])

        self.accent_width = font_size / 9
        self.font = font.Font(family=self.theme['font_family'],
                              size=font_size,
                              weight=self.theme["font_weight"])
        self.cmd_font = font.Font(family="Symbola",
                                  size=font_size)

        self.configure(background=self.background)


    def get_grid(self, num_items):
        Grid = namedtuple("Grid", ["col", "row", "gutter"])
        gutter_base = 10
        predefined_grids = [
            Grid(1, 1, gutter_base*0),
            Grid(1, 2, gutter_base*3),
            Grid(1, 3, gutter_base*3),
            Grid(2, 2, gutter_base*2),
            Grid(3, 2, gutter_base*2),
            Grid(3, 2, gutter_base*2),
            Grid(3, 3, gutter_base*2),
            Grid(3, 3, gutter_base*2),
            Grid(3, 3, gutter_base*2),
            Grid(3, 4, gutter_base*2),
            ]
        try:
            grid_template = predefined_grids[num_items - 1]
        except IndexError:
            grid_template = Grid(3, num_items/3, gutter_base*2)
        return grid_template

    def destroy_text_widgets(self):
        for widget in self.text_widgets:
            widget.destroy()
        self.text_widgets = []

    def refresh_command_text(self):
        # Destroy any existing text widgets
        self.destroy_text_widgets()
        self.log.debug("=============STARTING=============")
        # Get list of commands
        try:
            current_commands = self.modes[self.current_mode].get('commands', [])
        except KeyError:
            current_commands = []
        # Create an array of text options
        text_items = []
        # add current
        for item in current_commands:
            text_items.append(item)
        # add escape
        for esc in self.escapes:
            text_items.append({"name":esc.get("name"), "keycode":esc.get("keycode")})
        num_items = len(text_items)
        grid_template = self.get_grid(num_items)
        row = 0
        col = 0
        if self.horizontal is True:
            max_col = grid_template.row - 1
        else:
            max_col = grid_template.col - 1
        for item in text_items:
            self.create_label_frame_widget(item, row, col, grid_template.gutter)
            # self.create_text_widget(item, row, col, grid_template.gutter)
            if col >= max_col:
                col = 0
                row += 1
            else:
                col += 1

    def create_text_widget(self, item, row, col, pad):
        temp_text = tk.Label(self,
                             background=self.background,
                             foreground=self.foreground,
                             font=self.font)
        label_text = "{keycode} : {name}".format(**item)
        temp_text['text'] = label_text
        temp_text.grid(column=col,
                       row=row,
                       padx=pad,
                       pady=pad,
                       sticky=tk.W)
        self.text_widgets.append(temp_text)

    def create_label_frame_widget(self, item, row, col, pad):
        frame = tk.LabelFrame(self,
                                  background=self.background,
                                  labelanchor='w',
                                  foreground=self.theme["cmd_color"],
                                  #highlightbackground=self.theme["cmd_color"],
                                  #highlightcolor=self.theme["cmd_color"],
                                  #highlightthickness=self.accent_width,
                                  borderwidth=0,
                                  relief=tk.FLAT,
                                  font=self.cmd_font)
        label = tk.Label(frame,
                         background=self.background,
                         foreground=self.foreground,
                         font=self.font)
        label_text = "{name}".format(**item)
        keycode = "{0} : ".format(self.keycode_convert(item['keycode']))
        #frame_text = "{keycode} : ".format(**item)
        frame_text = keycode
        frame['text'] = frame_text
        label['text'] = label_text
        label.grid()
        frame.grid(column=col,
                   row=row,
                   padx=pad,
                   pady=pad,
                   sticky=tk.W)
        self.text_widgets.append(frame)

    def parse_subscription(self, event, mode, subscription):
        self.log.debug("> Mode Received <")
        if mode in self.ignored_modes:
            self.log.debug("Ignoring mode {0}".format(mode))
            self.current_mode = None
            self.mode_stack = []
            self.window.withdraw()
        elif mode == "go_back":
            self.log.debug("Go Back mode enabled")
            self.go_last_mode()
        else:
            self.log.debug("Entering mode {0}".format(mode))
            # add last mode on to mode stack
            if self.current_mode is not None:
                self.mode_stack.append(self.current_mode)
            self.redraw_window(mode)

    def keycode_convert(self, keycode):
        converted = []
        for k in keycode:
            converted.append(pretty_chars.convert(k))
        return "+".join(converted)


class ModeSub(i3.Subscription):
    type_translation = {
        'workspace': 'get_workspaces',
        'output': 'get_outputs',
        'mode': 'mode'
    }


    def reinit_socket(self):
        self.close()
        time.sleep(2)
        event_socket = i3.Socket()
        self.event_socket = event_socket
        self.event_socket.subscribe(self.event_type, self.event)
        data_socket = i3.Socket()
        self.data_socket = data_socket
        self.subscribed = True

    def listen(self):
        """
        Runs a listener loop until self.subscribed is set to False.
        Calls the given callback method with data and the object itself.
        """
        self.subscribed = True
        while self.subscribed:
            try:
                event = self.event_socket.receive()
            except:
                self.reinit_socket()
                event = None
            if not event:  # skip an iteration if event is None
                continue
            # always return mode changes
            if self.event_type == 'mode':
                data = event['change']
            self.callback(event, data, self)
        self.close()


def set_logging(verbose=False, debug=False):
    if debug == True:
        log.setLevel("DEBUG")
    elif verbose == True:
        log.setLevel("INFO")

# Finish Logging Functions

def kill_existing_hydras():
    mypid = str(getpid())
    pgrep = subprocess.run(["pgrep", "-f", '^python3.*i3_hydra\/.*py$'], stdout=subprocess.PIPE)
    process_ids = pgrep.stdout.decode().split("\n")
    num_processes = len(process_ids) - 1 # Ignore empty output
    if num_processes > 0:
        log.debug("{0} Old hydra interfaces running. Killing now...".format(num_processes))
        for ID in process_ids:
            if ID != mypid: # Don't kill yourself
                log.info("Killing process {0}".format(ID))
                subprocess.run(["kill", ID])

if __name__ == '__main__':
    # Adding generic logging
    logging.basicConfig(level=logging.ERROR)
    log = logging.getLogger(__name__)
    log.setLevel("DEBUG")
    # If the hydra ever gets confused you can just restart i3 and it will start anew.
    kill_existing_hydras()
    # commands = parse_commands(test_commands)
    root = tk.Tk(className="I3hydra")
    app = Application(command_path="/home/s2e/.i3/main_mode.json",
                      master=root,
                      log=log)
    i3.EVENT_TYPES.append('mode')
    subscription = ModeSub(app.parse_subscription, 'mode')
    app.mainloop()
    subscription.close()



"""
client.focused          #3F8AC2 #096BAA #00BAA7 #00DA8E
client.focused_inactive #333333 #5F676A #ffffff #484e50
client.unfocused        #333333 #424242 #888888 #292d2e
client.urgent           #C10004 #900000 #ffffff #900000
"""
