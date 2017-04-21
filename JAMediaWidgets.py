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

import gtk, os, gobject, cairo, platform
from gettext import gettext as _
import JAMediaGlobals as G
from JAMediaMixer import JAMediaMixer

class JAMediaButton(gtk.EventBox):
	__gsignals__ = {"clicked":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))}
	def __init__(self):
		gtk.EventBox.__init__(self)
		self.set_visible_window(True)
		self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
		self.set_border_width(1)

		# http://developer.gnome.org/pygtk/stable/gdk-constants.html#gdk-event-mask-constants
		self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK |
			gtk.gdk.ENTER_NOTIFY_MASK | gtk.gdk.LEAVE_NOTIFY_MASK)

		self.connect("button_press_event", self.button_press)
		self.connect("button_release_event", self.button_release)
		self.connect("enter-notify-event", self.enter_notify_event)
		self.connect("leave-notify-event", self.leave_notify_event)

	        self.imagen= gtk.Image()
        	self.add(self.imagen)

		self.show_all()

	# --------------------------- EVENTOS --------------------------
	def button_release(self, widget, event):
		self.modify_bg(gtk.STATE_NORMAL, G.AMARILLO)
	def leave_notify_event(self, widget, event):
		self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
	def enter_notify_event(self, widget, event):
		self.modify_bg(gtk.STATE_NORMAL, G.AMARILLO)
	def button_press(self, widget, event):
		if event.button == 1:
			self.modify_bg(gtk.STATE_NORMAL, G.NARANJA)
			self.emit("clicked", event)
	# --------------------------- EVENTOS --------------------------

	# --------------------------- SETEOS ---------------------------
	def set_tooltip(self, texto):
		tooltips = gtk.Tooltips()
		tooltips.set_tip(self, texto, tip_private=None)

	def set_imagen(self, archivo):
        	self.imagen.set_from_file(archivo)
	
	def set_tamanio(self, w, h):
		self.set_size_request(w,h)
	# --------------------------- SETEOS ---------------------------

class Superficie_de_Reproduccion(gtk.DrawingArea):
	__gsignals__ = {"ocultar_controles":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))}
	def __init__(self):
		gtk.DrawingArea.__init__(self)
		self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
		self.show_all()
		self.add_events(gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.POINTER_MOTION_HINT_MASK)

		self.img= cairo.ImageSurface.create_from_png(os.path.join(G.ICONOS, "fondo.png"))

		self.connect("motion-notify-event", self.mousemotion)

	def mousemotion(self, widget, event):
		x, y, state= event.window.get_pointer()
		xx,yy,ww,hh= self.get_allocation()
		if x in range(ww-60, ww) and y in range(yy,hh):
			self.emit("ocultar_controles", False)
			return
		else:
			self.emit("ocultar_controles", True)
			return

	def paint(self):
		imgpat= cairo.SurfacePattern(self.img)
		scaler= cairo.Matrix()

		x,y,w,h= self.get_allocation()
		width= float(self.img.get_width())
		height= float(self.img.get_height())
		ws= float(width/float(w))
		hs= float(height/float(h))

		#1 = 100% ; 2 = 50% ; 0.5 = 200%
		scaler.scale(ws, hs)
		imgpat.set_matrix(scaler)
		imgpat.set_filter(cairo.FILTER_BEST)

		cr= self.window.cairo_create()
		cr.set_source(imgpat)
		cr.paint()

class Barra_de_Opciones_uno(gtk.HBox):
	__gsignals__ = {"set_video_resolucion":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_INT, gobject.TYPE_INT)),
		"salir":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,)),
		"download_streamings":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, ))}
	def __init__(self, ventanajamedia):
		gtk.HBox.__init__(self, False, 0)
		lado= int(G.BUTTONS*1.5)
		self.ventanadescargas= VentanaDescargas(ventanajamedia)
		self.ventanadescargas.connect("download_streamings", self.download_streamings)
		self.ventanadescargas.hide()

		self.salir= JAMediaButton()
		self.salir.set_tooltip(_("Salir"))
		self.salir.set_imagen(os.path.join(G.ICONOS, "salir.png"))
		self.salir.set_tamanio( lado, lado)
        	self.salir.connect("clicked", self.call_salir)

		self.descarga= JAMediaButton()
		self.descarga.set_tooltip(_("Descargas"))
		pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(G.ICONOS, "iconplay.png"))
		self.descarga.imagen.set_from_pixbuf(pixbuf.rotate_simple(gtk.gdk.PIXBUF_ROTATE_CLOCKWISE))
		self.descarga.set_tamanio( lado, lado)
        	self.descarga.connect("clicked", self.get_VentanaDescargas)

		self.escalar= JAMediaButton()
		self.escalar.set_tooltip(_("Resolución"))
		self.escalar.set_imagen(os.path.join(G.ICONOS, "monitor.png"))
		self.escalar.set_tamanio( lado, lado)
        	self.escalar.connect("clicked", self.set_video)

		self.pack_start(self.escalar, True, True, 0)
		self.pack_start(self.descarga, True, True, 0)
		self.pack_start(self.salir, True, True, 0)
		self.show_all()

	def get_VentanaDescargas(self, widget= None, event= None):
		self.ventanadescargas.present()

	def download_streamings(self, widget, datos):
		self.emit("download_streamings", datos)

	# -------------- Menu Resoluciones --------------------------
	def set_video(self, widget= None, event= None):
		boton = event.button
		pos = (event.x, event.y)
		tiempo = event.time
		self.menu(widget, boton, pos, tiempo)
		return

	def menu(self, widget, boton, pos, tiempo):
		menu = gtk.Menu()
		menu.set_title(_("Escalar Video a:"))

		ancho= gtk.gdk.screen_width()
		alto= gtk.gdk.screen_height()

		resoluciones = [(320,240), (640,480), (800,480), (800,600), (1024,768)]

		for res in resoluciones[0:-1]:
			if res[0]< ancho and res[1]< alto:
				item = gtk.MenuItem(str(res))
				menu.append(item)
				item.connect_object("activate", self.set_video_resolucion, res)

		item = gtk.MenuItem(_("Pantalla Completa"))
		menu.append(item)
		item.connect_object("activate", self.set_video_resolucion, "fullscreen")

		menu.show_all()
		menu.popup(None, None, None, boton, tiempo, None)

	def set_video_resolucion(self, datos):
		if datos== "fullscreen":
			self.emit("set_video_resolucion", 0, 0)
		else:
			self.emit("set_video_resolucion", int(datos[0]), int(datos[1]))
	# -------------- Menu Resoluciones --------------------------

	def call_salir(self, widget= None, event= None):
		self.emit("salir", True)

class Selector_de_Archivos (gtk.FileChooserDialog):
	def __init__(self, jamedia):
		self.jamedia = jamedia
		gtk.FileChooserDialog.__init__(self, title=_("Abrir Archivos de Audio o Video"), parent=self.jamedia,
			action=gtk.FILE_CHOOSER_ACTION_OPEN)
		self.set_default_size( 640, 480 )
		self.resize( 640, 480 )
		self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
		self.set_current_folder_uri("file:///media")
		self.set_select_multiple(True)
		# extras
		hbox = gtk.HBox()
		boton_abrir_directorio = gtk.Button(_("Abrir"))
		boton_seleccionar_todo = gtk.Button(_("Seleccionar Todos"))
		boton_salir = gtk.Button(_("Salir"))
		hbox.pack_end(boton_salir, True, True, 5)
		hbox.pack_end(boton_seleccionar_todo, True, True, 5)
		hbox.pack_end(boton_abrir_directorio, True, True, 5)
		self.set_extra_widget(hbox)
		filter = gtk.FileFilter()
		filter.set_name(_("Musica"))
		filter.add_mime_type("audio/*")
		self.add_filter(filter)
		filter = gtk.FileFilter()
		filter.set_name(_("Videos"))
		filter.add_mime_type("video/*")
		self.add_filter(filter)
		self.add_shortcut_folder_uri("file:///media/")
		# Callbacks
		boton_salir.connect("clicked", self.salir)
		boton_abrir_directorio.connect("clicked",self.abrir_directorio)
		boton_seleccionar_todo.connect("clicked",self.seleccionar_todos_los_archivos)

		self.show_all()
		self.resize( 640, 480 )

	def seleccionar_todos_los_archivos(self, widget):
		self.select_all()

	def abrir_directorio(self, widget):
        	self.jamedia.Lista_de_Archivos = self.get_filenames()
		self.jamedia.set_lista_archivos()
		self.salir(None)

	def salir(self, widget):
		self.destroy()

class Barra_de_Progreso(gtk.Frame):
	__gsignals__ = {"change-value":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_INT, ))}
	def __init__(self):
		gtk.Frame.__init__(self)
		self.set_label_align(0.5, 0.0)
		self.scale= ProgressBar(gtk.Adjustment(0.0, 0.0, 101.0, 0.1, 1.0, 1.0))

		self.scale.connect("button-press-event", self.buttonpressevent)
		self.scale.connect("change-value", self.changevalueprogressbar)
		self.scale.connect("button-release-event", self.buttonreleaseevent)

		self.valor= 0
		self.presion= False

		self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
		self.set_size_request(350, 30)

		self.add(self.scale)
		self.show_all()

	def buttonpressevent(self, widget, event):
		self.presion = True

	def buttonreleaseevent(self, widget, event):
		self.presion = False

	def set_progress(self, valor= 0):
		if not self.presion: self.scale.set_value(valor)

	def changevalueprogressbar(self, widget= None, flags= None, valor= None):
		valor = int(valor)
		if valor < 1 or valor > 99:
			return
		else:
			if valor != self.valor and not self.presion:
				self.valor = valor
				self.scale.set_value(self.valor)
				self.emit("change-value", self.valor)

class ProgressBar(gtk.HScale):
	def __init__(self, ajuste):
		gtk.HScale.__init__(self, ajuste)
		self.ajuste= ajuste
		self.set_digits(0)
		self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
		self.set_draw_value(False)

		self.x, self.y, self.w, self.h= (0,0,200,40)
		self.borde, self.ancho= (15, 10)

		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(G.ICONOS, "iconplay.png"), 25, 25)
		self.pixbuf = pixbuf.rotate_simple(gtk.gdk.PIXBUF_ROTATE_COUNTERCLOCKWISE)

		self.connect("expose_event", self.expose)
		self.connect("size-allocate", self.size_allocate)

	def expose( self, widget, event ):
		x, y, w, h= (self.x, self.y, self.w, self.h)
		ancho, borde= (self.ancho, self.borde)

		gc= gtk.gdk.Drawable.new_gc(self.window)
		# http://developer.gnome.org/pygtk/stable/class-gdkgc.html
		# http://developer.gnome.org/pygtk/stable/class-gdkdrawable.html#method-gdkdrawable--draw-rectangle
		# draw_rectangle(gc, filled, x, y, width, height)

		gc.set_rgb_fg_color(G.BLANCO)
		self.window.draw_rectangle( gc, True, x, y, w, h )

		gc.set_rgb_fg_color(G.AMARILLO)
		ww= w- borde*2
		xx= x+ w/2 - ww/2
		hh= ancho
		yy= y+ h/2 - ancho/2
		self.window.draw_rectangle( gc, True, xx, yy, ww, hh )

		anchoimagen, altoimagen= (self.pixbuf.get_width(), self.pixbuf.get_height())
		ximagen= int((xx- anchoimagen/2) + self.get_value() * (ww / (self.ajuste.upper - self.ajuste.lower)))
		yimagen= yy + hh/2 - altoimagen/2

		gc.set_rgb_fg_color(G.NARANJA)
		self.window.draw_rectangle( gc, True, xx, yy, ximagen, hh)

		gc.set_rgb_fg_color(G.NEGRO)
		self.window.draw_rectangle( gc, False, xx, yy, ww, hh )

		self.window.draw_pixbuf( gc, self.pixbuf, 0, 0, ximagen, yimagen, anchoimagen, altoimagen, gtk.gdk.RGB_DITHER_NORMAL, 0, 0 )

		return True

	def size_allocate( self, widget, allocation ):
		self.x, self.y, self.w, self.h= allocation
		return False

class Barra_de_Reproduccion(gtk.HBox):
	__gsignals__ = {"activar":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,))}
	def __init__(self):
		gtk.HBox.__init__(self, False, 0)

		# ****** BOTON_ATRAS
		self.botonatras= JAMediaButton()
		self.botonatras.set_tooltip(_("Pista Anterior"))
		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(G.ICONOS, "siguiente.png"), 32, 32).flip(True)
		self.botonatras.imagen.set_from_pixbuf(pixbuf)
		self.botonatras.set_tamanio( G.BUTTONS, G.BUTTONS )
        	self.botonatras.connect("clicked", self.clickenatras)

		# ****** BOTON PLAY
		self.botonplay= JAMediaButton()
		self.botonplay.set_tooltip(_("Reproducir o Pausar"))
		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(G.ICONOS, "play.png"), 32, 32)
		self.botonplay.imagen.set_from_pixbuf(pixbuf)
		self.botonplay.set_tamanio( G.BUTTONS, G.BUTTONS )
        	self.botonplay.connect("clicked", self.clickenplay_pausa)

		# ****** BOTON SIGUIENTE
		self.botonsiguiente= JAMediaButton()
		self.botonsiguiente.set_tooltip(_("Pista Siguiente"))
		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(G.ICONOS, "siguiente.png"), 32, 32)
		self.botonsiguiente.imagen.set_from_pixbuf(pixbuf)
		self.botonsiguiente.set_tamanio( G.BUTTONS, G.BUTTONS )
        	self.botonsiguiente.connect("clicked", self.clickensiguiente)

		# ****** BOTON STOP
		self.botonstop= JAMediaButton()
		self.botonstop.set_tooltip(_("Detener Reproducción"))
		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(G.ICONOS, "stop.png"), 32, 32)
		self.botonstop.imagen.set_from_pixbuf(pixbuf)
		self.botonstop.set_tamanio( G.BUTTONS, G.BUTTONS )
        	self.botonstop.connect("clicked", self.clickenstop)

		self.pack_start(self.botonatras, True, True, 0)
		self.pack_start(self.botonplay, True, True, 0)
		self.pack_start(self.botonsiguiente, True, True, 0)
		self.pack_start(self.botonstop, True, True, 0)

        	self.show_all()

	def set_paused(self):
		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(G.ICONOS, "play.png"), 32, 32)
		self.botonplay.imagen.set_from_pixbuf(pixbuf)
	def set_playing(self):
		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(G.ICONOS, "pausa.png"), 32, 32)
		self.botonplay.imagen.set_from_pixbuf(pixbuf)

    	def clickenstop(self, widget= None, event= None):
		self.emit("activar", "stop")
	def clickenplay_pausa(self, widget= None, event= None):
		self.emit("activar", "pausa-play")
    	def clickenatras(self, widget= None, event= None):
		self.emit("activar", "atras")
    	def clickensiguiente(self, widget= None, event= None):
		self.emit("activar", "siguiente")

class ButtonJAMediaMixer(JAMediaButton):
	def __init__(self):
		JAMediaButton.__init__(self)
		self.set_tooltip("JAMediaMixer")

		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(G.ICONOS, "volumen.png"), 32, 32)
		self.imagen.set_from_pixbuf(pixbuf)
		self.set_tamanio(G.BUTTONS, G.BUTTONS)

	        self.jamediamixer= JAMediaMixer()
		self.jamediamixer.reset_sound()
		self.jamediamixer.hide()

		self.connect("clicked", self.get_jamediamixer)
		self.show_all()

	def get_jamediamixer(self, widget= None, event= None):
		self.jamediamixer.present()

class VentanaDescargas(gtk.Window):
	__gsignals__ = {"download_streamings":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, ))}
	def __init__(self, ventanajamedia):
		super(VentanaDescargas, self).__init__(gtk.WINDOW_POPUP)
		self.ventanajamedia= ventanajamedia
		self.set_title(_("Descargas"))
		self.set_resizable(False)
        	self.set_border_width(20)
		self.set_transient_for(self.ventanajamedia)
		self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		self.modify_bg(gtk.STATE_NORMAL, G.AMARILLO)

		self.set_layout()
		self.show_all()

	def set_layout(self):
		vbox1= gtk.VBox()
		downloadstreaming= gtk.Button(_("Actualizar Streamings de JAMedia"))
		salir= gtk.Button(_("Cerrar"))
		vbox1.pack_start(downloadstreaming, False, False, 5)
		vbox1.pack_start(salir, False, False, 5)

		downloadstreaming.connect("clicked", self.get_JAMedia_streamings)
		salir.connect("clicked", self.cerrar)
		self.add(vbox1)

	def get_JAMedia_streamings(self, widget):
		dialog= JAMediaDialog(_("¿ Descargar y Actualizar Streaming de JAMedia ?"), self.ventanajamedia)
		dialog.connect("ok", self.download_streamings)

	def download_streamings(self, widget, datos):
		self.emit("download_streamings", None)

	def cerrar(self, widget):
		self.hide()

class JAMediaDialog(gtk.Window):
	__gsignals__ = {"ok":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, ))}
	def __init__(self, etiqueta, ventanajamedia):
		super(JAMediaDialog, self).__init__(gtk.WINDOW_POPUP)
		self.set_transient_for(ventanajamedia)
		self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		self.set_resizable(False)
        	self.set_border_width(20)
		self.modify_bg(gtk.STATE_NORMAL, G.AMARILLO)

		vcaja= gtk.VBox()
		label= gtk.Label(etiqueta)
		vcaja.pack_start(label, True, True, 3)

		hbox= gtk.HBox()
		botonOK= gtk.Button("Si")
		botonNO= gtk.Button("No")
		botonOK.connect("clicked", self.ok_callback)
		botonNO.connect("clicked", self.cerrar)
		hbox.pack_start(botonOK, True, True, 3)
		hbox.pack_start(botonNO, True, True, 3)

		vcaja.pack_start(hbox, True, True, 3)

		self.add(vcaja)
		self.show_all()

	def ok_callback(self, widget= None, event= None):
		self.emit("ok", None)
		self.destroy()

	def cerrar(self, widget= None, event= None):
		self.destroy()

class JAMediaInfo(gtk.Toolbar):
	def __init__(self, etiqueta):
		gtk.Toolbar.__init__(self)
		self.modify_bg(gtk.STATE_NORMAL, G.NEGRO)

		separator = gtk.SeparatorToolItem()
		separator.props.draw = False
		separator.set_size_request(5, -1)
		separator.set_expand(False)
		self.insert(separator, -1)

		item = gtk.ToolItem()
		self.label = gtk.Label(etiqueta)
		self.label.modify_fg(gtk.STATE_NORMAL, G.BLANCO)
		self.label.show()
		item.add(self.label)
		self.insert(item, -1)

		self.show_all()

class ControlGrabar(gtk.Toolbar):
	__gsignals__ = {"stop":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])}
	def __init__(self, etiqueta):
		gtk.Toolbar.__init__(self)
		self.modify_bg(gtk.STATE_NORMAL, G.NEGRO)

		separator = gtk.SeparatorToolItem()
		separator.props.draw = False
		separator.set_size_request(5, -1)
		separator.set_expand(False)
		self.insert(separator, -1)

		item = gtk.ToolItem()
		self.label = gtk.Label(etiqueta)
		self.label.modify_fg(gtk.STATE_NORMAL, G.BLANCO)
		self.label.show()
		item.add(self.label)
		self.insert(item, -1)

		separator = gtk.SeparatorToolItem()
		separator.props.draw = False
		separator.set_size_request(0, -1)
		separator.set_expand(True)
		self.insert(separator, -1)

		boton = gtk.ToolButton()
		imagen = gtk.Image()
		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(G.ICONOS, "stop.png"), 32, 32)
		imagen.set_from_pixbuf(pixbuf)
		boton.set_icon_widget(imagen)
		imagen.show()
		self.insert(boton, -1)
		boton.show()
		tooltips = gtk.Tooltips()
		tooltips.set_tip(boton, _("Detener Grabación."), tip_private=None)
		self.show_all()
		boton.connect("clicked", self.ok_callback)

	def ok_callback(self, widget= None, event= None):
		self.emit("stop")

	def grabando(self, origen):
		self.label.set_text("%s: %s" % (_("Grabando"), origen))
		#self.modify_bg(gtk.STATE_NORMAL, G.NARANJA)

	def detenido(self, widget= None, event= None):
		self.label.set_text(_("Grabador Detenido."))
		#self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)

class StandarDialog(gtk.MessageDialog):
	def __init__(self, parent, title, label):
		gtk.MessageDialog.__init__(self, parent, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO)
		self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
		self.set_title(title)
		self.set_markup(label)

class ToolbarLista(gtk.Toolbar):
	__gsignals__ = {"load_list":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_INT,)),
	"add_stream":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])}
	def __init__(self):
		gtk.Toolbar.__init__(self)
		self.modify_bg(gtk.STATE_NORMAL, G.NEGRO)

		boton = gtk.ToolButton()
		imagen = gtk.Image()
		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(G.ICONOS, "lista.png"), 32, 32)
		imagen.set_from_pixbuf(pixbuf)
		boton.set_icon_widget(imagen)
		imagen.show()
		self.insert(boton, -1)
		boton.show()
		tooltips = gtk.Tooltips()
		tooltips.set_tip(boton, _("Selecciona una Lista."), tip_private=None)
		boton.connect("clicked", self.get_menu)

		item = gtk.ToolItem()
		self.label = gtk.Label("")
		self.label.modify_fg(gtk.STATE_NORMAL, G.BLANCO)
		self.label.show()
		item.add(self.label)
		self.insert(item, -1)

		separator = gtk.SeparatorToolItem()
		separator.props.draw = False
		separator.set_size_request(0, -1)
		separator.set_expand(True)
		self.insert(separator, -1)

		self.boton_agregar = gtk.ToolButton()
		imagen = gtk.Image()
		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(G.ICONOS, "agregar.png"), 32, 32)
		imagen.set_from_pixbuf(pixbuf)
		self.boton_agregar.set_icon_widget(imagen)
		imagen.show()
		self.insert(self.boton_agregar, -1)
		self.boton_agregar.show()
		tooltips = gtk.Tooltips()
		tooltips.set_tip(self.boton_agregar, _("Agregar Streaming"), tip_private=None)
		self.boton_agregar.connect("clicked", self.emit_add_stream)
		self.show_all()

	def get_menu(self, widget):
		menu = gtk.Menu()
		item = gtk.MenuItem(_("JAMedia Radio"))
		menu.append(item)
		item.connect_object("activate", self.emit_load_list, 0)

		item = gtk.MenuItem(_("JAMedia TV"))
		menu.append(item)
		item.connect_object("activate", self.emit_load_list, 1)

		item = gtk.MenuItem(_("Mis Emisoras"))
		menu.append(item)
		item.connect_object("activate", self.emit_load_list, 2)

		item = gtk.MenuItem(_("Mis Canales"))
		menu.append(item)
		item.connect_object("activate", self.emit_load_list, 3)

		item = gtk.MenuItem(_("Mis Archivos"))
		menu.append(item)
		item.connect_object("activate", self.emit_load_list, 4)

		item = gtk.MenuItem(_("Audio-JAMediaVideo"))
		menu.append(item)
		item.connect_object("activate", self.emit_load_list, 5)

		item = gtk.MenuItem(_("Video-JAMediaVideo"))
		menu.append(item)
		item.connect_object("activate", self.emit_load_list, 6)

		#item = gtk.MenuItem(_("JAMediaTube"))
		#menu.append(item)
		#item.connect_object("activate", self.emit_load_list, 7)

		item = gtk.MenuItem(_("Archivos Externos"))
		menu.append(item)
		item.connect_object("activate", self.emit_load_list, 8)

		menu.show_all()
		gtk.Menu.popup(menu, None, None, None, 1, 0)

	def emit_load_list(self, indice):
		self.emit("load_list", indice)

	def emit_add_stream(self, widget):
		self.emit("add_stream")

