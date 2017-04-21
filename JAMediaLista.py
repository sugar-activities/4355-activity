#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMediaWidgets.py por:
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

import gtk, os, gobject

import JAMediaGlobals as G

'''cada elemento en la lista tiene:
	preview, texto, url, tipo'''

class JAMediaLista (gtk.ScrolledWindow):
	__gsignals__ = {"play":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
	"getmenu":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT,
	gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT))}
	def __init__(self):
		gtk.ScrolledWindow.__init__(self)
		self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.contenedor = gtk.VBox()
		self.add_with_viewport(self.contenedor)
		self.show_all()

	def set_lista(self, lista):
		for child in self.contenedor.get_children():
			self.contenedor.remove(child)
			child.destroy()
		for elemento in lista:
			preview, texto, url, tipo = elemento
			item = JAMediaItem(preview, texto, url, tipo)
			self.contenedor.pack_start(item, False, False, 1)
			item.connect("doble_click", self.select_item)
			item.connect("click_derecho", self.emit_get_menu_item)

	def next(self):
		if not self.contenedor.get_children(): return
		index = False
		for child in self.contenedor.get_children():
			if child.estado_select:
				index = self.contenedor.get_children().index(child)
				break
		if type(index) == int:
			if len(self.contenedor.get_children())-1 > index:
				index += 1
			else:
				index = 0
		else:
			index = 0
		item = self.contenedor.get_children()[index]
		self.select_item(item)

	def previous(self):
		if not self.contenedor.get_children(): return
		index = False
		for child in self.contenedor.get_children():
			if child.estado_select:
				index = self.contenedor.get_children().index(child)
				break
		if type(index) == int:
			if index > 0:
				index -= 1
			else:
				index = -1
		else:
			index = 0
		item = self.contenedor.get_children()[index]
		self.select_item(item)

	def select_item(self, item):
	# Cuando se hace doble click en un elemento de la lista.
		for child in self.contenedor.get_children():
			if child == item:
				child.select()
			else:
				child.de_select()
		self.emit("play", item)

	def get_active_item_or_play(self):
	# Retorna el item activo o selecciona y reproduce el primero.
		if not self.contenedor.get_children(): return None
		for child in self.contenedor.get_children():
			if child.estado_select:
				return child
		self.select_item(self.contenedor.get_children()[0])

	def emit_get_menu_item (self, item, event):
		boton = event.button
		pos = (event.x, event.y)
		tiempo = event.time
		self.emit("getmenu", item, boton, pos, tiempo)

class JAMediaItem(gtk.EventBox):
	__gsignals__ = {"click":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, []),
	"click_derecho":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
	"doble_click":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])}
	def __init__(self, preview, texto, url, tipo):
		gtk.EventBox.__init__(self)
		self.set_border_width(1)
		self.set_visible_window(True)

		self.colornormal = G.BLANCO
		self.colorselect = G.AMARILLO
		self.colorclicked = G.NARANJA

		self.modify_bg(gtk.STATE_NORMAL, self.colornormal)
		self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk._2BUTTON_PRESS | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK |
			gtk.gdk.ENTER_NOTIFY_MASK | gtk.gdk.LEAVE_NOTIFY_MASK)

		self.texto, self.url, self.tipo = (texto, url, tipo)

		self.estado_select = False

		if not preview or not os.path.exists(preview): preview = os.path.join(G.ICONOS, "fondo.png")
		self.set_layout(preview, texto)

		self.show_all()

		self.connect("button_press_event", self.button_press)
		self.connect("button_release_event", self.button_release)
		self.connect("enter-notify-event", self.enter_notify_event)
		self.connect("leave-notify-event", self.leave_notify_event)

	def set_layout(self, preview, texto):
		base = gtk.HBox()
		imagen = gtk.Image()
		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(preview, 45, 45)
		imagen.set_from_pixbuf(pixbuf)
		label = gtk.Label(texto)
		base.pack_start(imagen, False, False, 3)
		base.pack_start(label, False, False, 1)
		self.add(base)

	def button_release(self, widget, event):
		self.modify_bg(gtk.STATE_NORMAL, self.colorselect)
	def leave_notify_event(self, widget, event):
		self.modify_bg(gtk.STATE_NORMAL, self.colornormal)
	def enter_notify_event(self, widget, event):
		self.modify_bg(gtk.STATE_NORMAL, self.colorselect)
	def button_press(self, widget, event):
		if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
			self.emit("doble_click")
		if event.type == gtk.gdk.BUTTON_PRESS:
			if event.button == 1:
				self.modify_bg(gtk.STATE_NORMAL, self.colorclicked)
				self.emit("click")
			if event.button == 3:
				self.emit("click_derecho", event)

	def select(self):
		self.estado_select = True
		self.colornormal = G.NARANJA
		self.colorselect = G.AMARILLO
		self.colorclicked = G.NARANJA
		self.modify_bg(gtk.STATE_NORMAL, self.colornormal)

	def de_select(self):
		self.estado_select = False
		self.colornormal = G.BLANCO
		self.colorselect = G.AMARILLO
		self.colorclicked = G.NARANJA
		self.modify_bg(gtk.STATE_NORMAL, self.colornormal)

