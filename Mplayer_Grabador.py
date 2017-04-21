#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Mplayer_Reproductor.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   CeibalJAM! - Uruguay

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gobject, os, sys, subprocess, platform, commands

MPLAYER = "mplayer"
if "olpc" in platform.platform(): MPLAYER = "./mplayer"

class Mplayer_Grabador(gobject.GObject):
	def __init__(self, direccion, archivo):
		self.__gobject_init__()
		self.ejecutable = MPLAYER
		self.mplayer = None
		self.archivo = archivo
		self.direccion = direccion

		estructura= "%s -dumpfile %s %s -dumpstream" % (self.ejecutable, self.archivo, self.direccion)
		self.mplayer= subprocess.Popen(estructura, shell=True, universal_newlines=True)

if __name__=="__main__":
	direccion= sys.argv[2].split("****")[0]
	archivo= sys.argv[2].split("****")[1]
	grabador= Mplayer_Grabador(direccion, archivo)

