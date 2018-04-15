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

import re

# http://www.fontspace.com/unicode-fonts-for-ancient-scripts/symbola/37632/charmap
# http://xahlee.info/comp/unicode_computing_symbols.html

alpha = {
    "a":"ⓐ",
    "b":"ⓑ",
    "c":"ⓒ",
    "d":"ⓓ",
    "e":"ⓔ",
    "f":"ⓕ",
    "g":"ⓖ",
    "h":"ⓗ",
    "i":"ⓘ",
    "j":"ⓙ",
    "k":"ⓚ",
    "l":"ⓛ",
    "m":"ⓜ",
    "n":"ⓝ",
    "o":"ⓞ",
    "p":"ⓟ",
    "q":"ⓠ",
    "r":"ⓡ",
    "s":"ⓢ",
    "t":"ⓣ",
    "u":"ⓤ",
    "v":"ⓥ",
    "w":"ⓦ",
    "x":"ⓧ",
    "y":"ⓨ",
    "z":"ⓩ",
}

numeric = {
    "1":"⓵",
    "2":"⓶",
    "3":"⓷",
    "4":"⓸",
    "5":"⓹",
    "6":"⓺",
    "7":"⓻",
    "8":"⓼",
    "9":"⓽",
    "0":"⓾",
}


commands = {
    "Alt":"✦",
    # "Alt_L":"",
    # "Alt_R":"",
    "BackSpace":"␈",
    "Backspace":"␈",
    # "Cancel":"",
    "Control":"✲", #"🛂",
    #"Control_L":"",
    #"Control_R":"",
    "Delete":"␡",
    "Down":"⮋",
    # "End":"",
    "Enter":"⏎",
    "Return":"⏎",
    "Escape":"␛",
    # "F1":"",
    # "F10":"",
    # "F11":"",
    # "F12":"",
    # "F2":"",
    # "F3":"",
    # "F4":"",
    # "F5":"",
    # "F6":"",
    # "F7":"",
    # "F8":"",
    # "F9":"",
    "Insert":"⎀",
    "Left":"⮈",
    "Menu":"▤",
    #"Num_Lock":"",
    "Right":"⮊",
    "Shift":"⇧",
    #"Shift_L":"🗛",
    #"Shift_R":"🗚",
    "Super":"⌘",
    #"Super_L":"⌘",
    #"Super_R":"⌘",
    "space":"␠",
    "Tab":"⭾",
    "Up":"⮉",
    "Print":"⎙",
    # "control":"",
    # "lock":"",
    # "mod1":"",
    # "mod2":"",
    # "mod3":"",
    # "mod4":"",
    # "mod5":"",
    # "shift":"🗚",
    }

def convert(key):
    if len(key) > 1:
        return commands.get(key, key)
    elif re.match("[a-zA-Z]", key):
        return alpha.get(key.lower(), key.lower())
    elif re.match("[0-9]", key):
        return numeric.get(key, key)
    else:
        return key
