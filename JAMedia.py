#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMedia.py por:
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

# Necesita:
#	python 2.7.1 - gtk 2.0
#	mplayer
#	gstreamer-plugins-base
#	gstreamer-plugins-good
#	gstreamer-plugins-ugly
#	gstreamer-plugins-bad
#	gstreamer-ffmpeg

from sugar.activity import activity
from sugar.datastore import datastore
import gtk
import os
import sys
import gobject
import time
import datetime
import commands
import subprocess
#import string
import platform
from gettext import gettext as _
import JAMediaGlobals as G
from Archivos_y_Directorios import Archivos_y_Directorios
from Mplayer_Reproductor import Mplayer_Reproductor
from JAMediaLista import JAMediaLista
from JAMediaWidgets import *
from Mplayer_Grabador import Mplayer_Grabador
ISOLPC = False
if "olpc" in platform.platform(): ISOLPC = True
gobject.threads_init()
gtk.gdk.threads_init()

class JAMedia(activity.Activity):
	def __init__(self, handle):
		activity.Activity.__init__(self, handle, False)
		self.set_title("JAMedia 10")
		self.set_icon_from_file(os.path.join(G.ICONOS, "JAMedia.png"))
		self.modify_bg(gtk.STATE_NORMAL, G.GRIS)
        	self.connect("delete_event", self.delete_event)
		self.origenes_de_datos = Archivos_y_Directorios(G.DIRECTORIO_DATOS, G.DIRECTORIO_MIS_ARCHIVOS)
		self.origenes_de_datos.Generar_Origenes_de_Datos()
		self.Lista_de_Radios = self.origenes_de_datos.Cargar_Tabla("Radios")
		self.Lista_de_Television = self.origenes_de_datos.Cargar_Tabla("Television")
		self.Lista_de_Archivos = None
		self.Lista_de_MisRadios = self.origenes_de_datos.Cargar_Tabla("MisRadios")
		self.Lista_de_MisTelevision = self.origenes_de_datos.Cargar_Tabla("MisTelevision")
		self.volumen = ButtonJAMediaMixer()
		self.pantalla = Superficie_de_Reproduccion()
		self.barradeprogreso = Barra_de_Progreso()
		self.barradereproduccion = Barra_de_Reproduccion()
		self.barradeopcionesuno = Barra_de_Opciones_uno(self)
		self.lista_de_reproduccion = JAMediaLista()
		self.info_grabar = ControlGrabar(_("Grabador Detenido."))
		self.info_reproduccion = JAMediaInfo(_("Reproducción Detenida."))
		self.toolbar_list = ToolbarLista()
		self.hbox_barra_progreso = None
		self.vbox_lista_reproduccion = None
		self.set_layout()
		self.show_all()
		self.realize()
		self.mplayer_server = Mplayer_Reproductor(self.pantalla.window.xid)
		self.graba = None
		self.toolbar_list.connect("load_list", self.load_list)
		self.toolbar_list.connect("add_stream", self.add_stream)
		self.mplayer_server.connect("cambio_estado", self.cambio_estado)
		self.mplayer_server.connect("update_progress", self.update_progress)
		self.mplayer_server.connect("video", self.video)
		self.mplayer_server.connect("mplayer_info", self.mplayer_info)
		self.pantalla.connect("ocultar_controles", self.ver_controles)
		self.pantalla.connect('expose-event', self.paint_pantalla)
		self.barradeopcionesuno.connect("set_video_resolucion", self.set_video_resolucion)
		self.barradeopcionesuno.connect("download_streamings", self.download_streamings)
		self.barradeopcionesuno.connect("salir", self.dialog_salir)
		self.barradereproduccion.connect("activar", self.activar)
		self.lista_de_reproduccion.connect("play", self.load_and_play)
		self.lista_de_reproduccion.connect("getmenu", self.set_menu_list)
		self.info_grabar.connect ("stop", self.detener_grabacion)
		self.barradeprogreso.connect("change-value", self.changevalueprogressbar)
		self.item_activo_en_lista = None
		self.videoenfuente = False
		self.controlesview = True
		self.present()
		gobject.idle_add(self.load_list, None, 2)

	def read_file(self, file_path):
	# Cuando abro desde el Journal
		tipo = "Audio_Video"
		url = file_path
		texto = "Archivo desde Journal"
		lista = []
		elemento = [None, texto, url, tipo]
		lista.append(elemento)
		self.lista_de_reproduccion.set_lista(lista)
		self.toolbar_list.label.set_text(_("Archivo desde Journal"))
	def write_file(self, file_path):
	# Salir sin guardar en el Journal
		self.Salir(None)
        	gtk.main_quit()

	def set_layout(self):
		hpanel= gtk.HPaned()
		vbox= gtk.VBox()
		hbox= gtk.HBox()
		hbox.pack_start(self.barradeprogreso, True, True, 0)
		hbox.pack_start(self.volumen, False, False, 0)
		vbox.pack_start(self.info_grabar, False, False, 0)
		vbox.pack_start(self.pantalla, True, True, 0)
		vbox.pack_start(self.info_reproduccion, False, False, 0)
		vbox.pack_start(hbox, False, False, 0)
		hpanel.pack1(vbox, resize=False, shrink=True)
		vbox= gtk.VBox()
		vbox.pack_start (self.toolbar_list, False, False, 0)
		vbox.pack_start(self.lista_de_reproduccion, True, True, 0)
		vbox.pack_start(self.barradeopcionesuno, False, False, 0)
		vbox.pack_start(self.barradereproduccion, False, False, 0)
		hpanel.pack2(vbox, resize=False, shrink=False)
		self.hbox_barra_progreso= hbox
		self.vbox_lista_reproduccion= vbox
		self.hbox_barra_progreso.show_all()
		hpanel.show_all()
		self.set_canvas(hpanel)
		self.volumen.jamediamixer.set_transient_for(self)
		self.volumen.jamediamixer.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

	# ----------------- CAPTURA DE SEÑALES ------------------
	def mplayer_info(self, widget= None, valor= None):
		if self.info_reproduccion.label.get_text()!= valor: self.info_reproduccion.label.set_text(valor)
	def changevalueprogressbar(self, widget = None, valor = None):
		estados = ["playing Audio_Video", "paused Audio_Video", "stoped Audio_Video"]
		if self.mplayer_server.get_estado() in estados: self.mplayer_server.seek(valor)
	def paint_pantalla(self, widget, event):
		if not self.videoenfuente or self.item_activo_en_lista.tipo == "Radio" \
			or self.mplayer_server.get_estado() == "stoped Audio_Video":
			self.pantalla.paint()
		return True
	def video(self, widget, valor):
		self.videoenfuente = valor
		if not self.videoenfuente: self.pantalla.paint()
	def set_video_resolucion(self, widget, w, h):
		if w == 0 and h == 0:
			self.fullscreen()
		else:
			self.unfullscreen()
			self.unmaximize()
			self.resize(w, h)
			self.set_size_request(w, h)
	def download_streamings(self, widget, datos):
		mensaje = self.origenes_de_datos.Actualizar_Streaming_de_JAMedia()
		self.Lista_de_Radios = self.origenes_de_datos.Cargar_Tabla("Radios")
		self.Lista_de_Television = self.origenes_de_datos.Cargar_Tabla("Television")
		dialog = StandarDialog(self, "Mensaje JAMedia", _(mensaje))
		response = dialog.run()
		dialog.destroy()
	def cambio_estado(self, widget, valor):
		''' "playing Audio_Video", "paused Audio_Video", "stoped Audio_Video", "playing Radio", "playing TV", None '''
		if valor == "playing Audio_Video" or valor == "playing Radio" or valor == "playing TV":
			self.barradereproduccion.set_playing()
		elif valor == "paused Audio_Video" or valor == "stoped Audio_Video" or valor == None:
			self.barradereproduccion.set_paused()
	def ver_controles(self, widget, valor):
		if valor and self.controlesview:
			self.vbox_lista_reproduccion.hide()
			self.hbox_barra_progreso.hide()
			self.info_grabar.hide()
			self.info_reproduccion.hide()
			self.controlesview = False
		elif not valor and not self.controlesview:
			self.vbox_lista_reproduccion.show()
			self.hbox_barra_progreso.show()
			self.info_grabar.show()
			self.info_reproduccion.show()
			self.controlesview = True

	def load_and_play(self, widget, item):
		self.item_activo_en_lista = item
		self.mplayer_server.quit(None)
		if ISOLPC: self.videoenfuente = True # por compatibilidad con sugar
		self.mplayer_server.play(self.item_activo_en_lista.url, self.item_activo_en_lista.tipo)

    	def activar(self, widget = None, senial = None):
		if senial == "stop":
	        	self.mplayer_server.quit(None)
		elif senial == "pausa-play":
			active_item = self.lista_de_reproduccion.get_active_item_or_play()
			if active_item == None: return
			if active_item:
				if self.mplayer_server.get_estado() == "stoped Audio_Video" or self.mplayer_server.get_estado() == None:
					if ISOLPC: self.videoenfuente = True # por compatibilidad con sugar
					self.mplayer_server.play(self.item_activo_en_lista.url, self.item_activo_en_lista.tipo)
				elif self.mplayer_server.get_estado() in ["paused Audio_Video", "playing Audio_Video"]:
					self.mplayer_server.pause_play()
	    	elif senial == "atras":
			self.lista_de_reproduccion.previous()
		elif senial == "siguiente":
			self.lista_de_reproduccion.next()
	
	def update_progress(self, objetoemisor, valor):
		self.barradeprogreso.set_progress(float(valor))
		if valor >= 100.0: self.lista_de_reproduccion.next()
	# ----------------- CAPTURA DE SEÑALES ------------------


	# ------------- LISTAS DE REPRODUCCION -------------- #
	def load_list(self, widget, indice):
		# elemento = [None, texto, url, tipo]
		# El parámetro None, se agregó para los previews de la lista (JAMedia-10),
		# Para estandarizar todo con JAMediaTube y JAMediaVideo.
		self.toolbar_list.boton_agregar.hide()
		self.item_activo_en_lista = None
		if indice == 0:
			self.toolbar_list.boton_agregar.hide()
			tipo = "Radio"
			lista = []
			for x in self.Lista_de_Radios:
				elem = x.split(",")
				texto = elem[0]
				url = elem[1]
				elemento = [None, texto, url, tipo]
				lista.append(elemento)
			self.lista_de_reproduccion.set_lista(lista)
			self.toolbar_list.label.set_text(_("JAMedia Radio"))
		elif indice == 1:
		# llenar lista con TV
			self.toolbar_list.boton_agregar.hide()
			tipo = "TV"
			lista = []
			for x in self.Lista_de_Television:
				elem = x.split(",")
				texto = elem[0]
				url = elem[1]
				elemento = [None, texto, url, tipo]
				lista.append(elemento)
			self.lista_de_reproduccion.set_lista(lista)
			self.toolbar_list.label.set_text(_("JAMedia TV"))
		elif indice == 2:
		# llenar lista con Streaming del usuario
			self.toolbar_list.boton_agregar.show()
			tipo = "Radio"
			lista = []
			for x in self.Lista_de_MisRadios:
				elem = x.split(",")
				texto = elem[0]
				url = elem[1]
				elemento = [None, texto, url, tipo]
				lista.append(elemento)
			self.lista_de_reproduccion.set_lista(lista)
			self.toolbar_list.label.set_text(_("Mis Emisoras"))
		elif indice == 3:
		# llenar lista con Streaming del usuario
			self.toolbar_list.boton_agregar.show()
			tipo = "TV"
			lista = []
			for x in self.Lista_de_MisTelevision:
				elem = x.split(",")
				texto = elem[0]
				url = elem[1]
				elemento = [None, texto, url, tipo]
				lista.append(elemento)
			self.lista_de_reproduccion.set_lista(lista)
			self.toolbar_list.label.set_text(_("Mis Canales"))
		elif indice == 4:
		# llenar lista con archivos de videos en el directorio de jamedia
			archivos = sorted(os.listdir(G.DIRECTORIO_MIS_ARCHIVOS))
			tipo = "Audio_Video"
			lista = []
			for texto in archivos:
				url = os.path.join(G.DIRECTORIO_MIS_ARCHIVOS, texto)
				elemento = [None, texto, url, tipo]
				lista.append(elemento)
			self.lista_de_reproduccion.set_lista(lista)
			self.toolbar_list.label.set_text(_("Mis Archivos"))
		elif indice == 5:
			archivos = sorted(os.listdir(G.AUDIO_JAMEDIA_VIDEO))
			tipo = "Audio_Video"
			lista = []
			for texto in archivos:
				url = os.path.join(G.AUDIO_JAMEDIA_VIDEO, texto)
				elemento = [None, texto, url, tipo]
				lista.append(elemento)
			self.lista_de_reproduccion.set_lista(lista)
			self.toolbar_list.label.set_text(_("Audio-JAMediaVideo"))
		elif indice == 6:
			archivos = sorted(os.listdir(G.VIDEO_JAMEDIA_VIDEO))
			tipo = "Audio_Video"
			lista = []
			for texto in archivos:
				url = os.path.join(G.VIDEO_JAMEDIA_VIDEO, texto)
				elemento = [None, texto, url, tipo]
				lista.append(elemento)
			self.lista_de_reproduccion.set_lista(lista)
			self.toolbar_list.label.set_text(_("Video-JAMediaVideo"))
		elif indice == 7:
			archivos = sorted(os.listdir(G.DIRECTORIO_YOUTUBE))
			tipo = "Audio_Video"
			lista = []
			for texto in archivos:
				url = os.path.join(G.DIRECTORIO_YOUTUBE, texto)
				elemento = [None, texto, url, tipo]
				lista.append(elemento)
			self.lista_de_reproduccion.set_lista(lista)
			self.toolbar_list.label.set_text(_("JAMediaTube"))
		elif indice == 8:
			Selector_de_Archivos(self)
		else:
			print "hay acciones sin asignar para opciones del combo"
		return False
	# ------------- LISTAS DE REPRODUCCION -------------- # 

	def set_lista_archivos(self):
	# crea una lista de archivos y la selecciona para reproduccion.
		if self.Lista_de_Archivos:
			self.toolbar_list.boton_agregar.hide()
			tipo = "Audio_Video"
			lista = []
			for x in self.Lista_de_Archivos:
				texto = os.path.basename(x)
				url = x
				elemento = [None, texto, url, tipo]
				lista.append(elemento)
			self.lista_de_reproduccion.set_lista(lista)
			self.toolbar_list.label.set_text(_("Archivos Externos"))

	#----------------- Operaciones para la lista -------------------- #
	def set_menu_list(self, widget, item, boton, pos, tiempo):
		menu = gtk.Menu()
		if item.tipo == "Audio_Video":
			quitar = gtk.MenuItem(_("Quitar de la Lista"))
			menu.append(quitar)
			quitar.connect_object("activate", self.set_accion_archivos, item, "Quitar")
			Plectura, Pescritura, Pejecucion = self.origenes_de_datos.verificar_permisos(item.url)
			origen = "%s%s" % (os.path.dirname(item.url), "/")
			destino = "%s%s" % (G.DIRECTORIO_MIS_ARCHIVOS, "/")
			if Plectura and origen != destino:
				copiar = gtk.MenuItem(_("Copiar a JAMedia"))
				menu.append(copiar)
				copiar.connect_object("activate", self.set_accion_archivos, item, "Copiar")
			if Pescritura and origen != destino:
				mover = gtk.MenuItem(_("Mover a JAMedia"))
				menu.append(mover)
				mover.connect_object("activate", self.set_accion_archivos, item, "Mover")
			if Pescritura:
				borrar = gtk.MenuItem(_("Borrar el Archivo"))
				menu.append(borrar)
				borrar.connect_object("activate", self.set_accion_archivos, item, "Borrar")
		else:
			quitar = gtk.MenuItem(_("Quitar de la Lista"))
			menu.append(quitar)
			quitar.connect_object("activate", self.set_accion_stream, item, "Quitar")
			if self.toolbar_list.label.get_text() == _("JAMedia Radio")\
			or self.toolbar_list.label.get_text() == _("JAMedia TV"):
				copiar = gtk.MenuItem(_("Copiar a mis Streaming"))
				menu.append(copiar)
				copiar.connect_object("activate", self.set_accion_stream, item, "Copiar")
				mover = gtk.MenuItem(_("Mover a mis Streaming"))
				menu.append(mover)
				mover.connect_object("activate", self.set_accion_stream, item, "Mover")
			borrar = gtk.MenuItem(_("Eliminar Streaming"))
			menu.append(borrar)
			borrar.connect_object("activate", self.set_accion_stream, item, "Borrar")
			grabar = gtk.MenuItem(_("Grabar Transmisión"))
			menu.append(grabar)
			grabar.connect_object("activate", self.set_accion_stream, item, "Grabar")
		menu.show_all()
		gtk.Menu.popup(menu, None, None, None, boton, tiempo)

	def set_accion_stream(self, item, accion):
		stream = "%s,%s" % (item.texto, item.url)
		if accion == "Quitar":
			dialog = StandarDialog(self, "Mensaje JAMedia", _("¿ Confirmas que deseas Quitar de la Lista ?"))
			response = dialog.run()
			dialog.destroy()
			if response == gtk.RESPONSE_YES:
				item.destroy()
		elif accion == "Grabar":
			self.grabar_streaming(item)
		elif accion == "Borrar":
			dialog = StandarDialog(self, "Mensaje JAMedia", _("¿ Confirmas que deseas Borrar Definitivamente el Streaming ?"))
			response = dialog.run()
			dialog.destroy()
			if response == gtk.RESPONSE_YES:
			# borrar streaming del archivo segun self.tipo
				item.destroy()
				if self.toolbar_list.label.get_text() == _("JAMedia Radio"):
					self.origenes_de_datos.eliminar_streaming(stream, "jamediaradio")
					self.Lista_de_Radios = self.origenes_de_datos.Cargar_Tabla("Radios")
				elif self.toolbar_list.label.get_text() == _("JAMedia TV"):
					self.origenes_de_datos.eliminar_streaming(stream, "jamediatv")
					self.Lista_de_Television = self.origenes_de_datos.Cargar_Tabla("Television")
				elif self.toolbar_list.label.get_text() == _("Mis Emisoras"):
					self.origenes_de_datos.eliminar_streaming(stream, "MisRadios")
					self.Lista_de_MisRadios = self.origenes_de_datos.Cargar_Tabla("MisRadios")
				elif self.toolbar_list.label.get_text() == _("Mis Canales"):
					self.origenes_de_datos.eliminar_streaming(stream, "MisTelevision")
					self.Lista_de_MisTelevision = self.origenes_de_datos.Cargar_Tabla("MisTelevision")
		elif accion == "Copiar":
			dialog = StandarDialog(self, "Mensaje JAMedia", _("¿ Confirmas que deseas Copiar este streaming a tu Lista ?"))
			response = dialog.run()
			dialog.destroy()
			if response == gtk.RESPONSE_YES:
				if self.toolbar_list.label.get_text() == _("JAMedia Radio"):
					self.origenes_de_datos.agregar_streaming(stream, self.origenes_de_datos.misradios)
					self.Lista_de_MisRadios = self.origenes_de_datos.Cargar_Tabla("MisRadios")
				elif self.toolbar_list.label.get_text() == _("JAMedia TV"):
					self.origenes_de_datos.agregar_streaming(stream, self.origenes_de_datos.mistv)
					self.Lista_de_MisTelevision = self.origenes_de_datos.Cargar_Tabla("MisTelevision")
		elif accion == "Mover":
			dialog = StandarDialog(self, "Mensaje JAMedia", _("¿ Confirmas que deseas Mover este streaming a tu Lista ?"))
			response = dialog.run()
			dialog.destroy()
			if response == gtk.RESPONSE_YES:
				if self.toolbar_list.label.get_text() == _("JAMedia Radio"):
					self.origenes_de_datos.agregar_streaming(stream, self.origenes_de_datos.misradios)
					self.Lista_de_MisRadios = self.origenes_de_datos.Cargar_Tabla("MisRadios")
				elif self.toolbar_list.label.get_text() == _("JAMedia TV"):
					self.origenes_de_datos.agregar_streaming(stream, self.origenes_de_datos.mistv)
					self.Lista_de_MisTelevision = self.origenes_de_datos.Cargar_Tabla("MisTelevision")
				item.destroy()
				if self.toolbar_list.label.get_text() == _("JAMedia Radio"):
					self.origenes_de_datos.eliminar_streaming(stream, "jamediaradio")
					self.Lista_de_Radios = self.origenes_de_datos.Cargar_Tabla("Radios")
				elif self.toolbar_list.label.get_text() == _("JAMedia TV"):
					self.origenes_de_datos.eliminar_streaming(stream, "jamediatv")
					self.Lista_de_Television = self.origenes_de_datos.Cargar_Tabla("Television")
		elif accion == "Agregar":
			print "Agregar No Funciona"

	def add_stream(self, widget):
		boton_OK = gtk.Button("Si")
		boton_Cancel = gtk.Button("No")
		dialog = gtk.Dialog(title="Mensaje JAMedia",
			parent=self, flags=gtk.DIALOG_MODAL | gtk.DIALOG_NO_SEPARATOR , buttons=None)
		dialog.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
		#dialog.set_size_request(350, 100)
		dialog.set_resizable(False)
		#Nombre
		caja1 = gtk.HBox()
		label1 = gtk.Label(_("Nombre: "))
		texto1 = gtk.Entry()
		caja1.pack_start(label1, False, False, 0)
		caja1.pack_start(texto1, True, True, 0)
		#Direccion
		caja2 = gtk.HBox()
		label2 = gtk.Label(_("Direccion: "))
		texto2 = gtk.Entry()
		caja2.pack_start(label2, False, False, 0)
		caja2.pack_start(texto2, True, True, 0)
		#Botones
		caja3 = gtk.HBox()
		boton_guardar = gtk.Button(_("Guardar"))
		boton_cancelar = gtk.Button(_("Cancelar"))
		caja3.pack_start(boton_guardar, True, False, 0)
		caja3.pack_start(boton_cancelar, True, False, 0)
		dialog.vbox.pack_start(caja1, False, False, 0)
		dialog.vbox.pack_start(caja2, False, False, 0)
		dialog.vbox.pack_start(caja3, False, False, 10)
		boton_cancelar.connect("clicked", self.destroy, dialog)
		boton_guardar.connect("clicked", self.new_streaming, texto1, texto2)
		boton_guardar.connect("clicked", self.destroy, dialog)
		dialog.show_all()

	def new_streaming(self, widget, texto1, texto2):
		nombre = texto1.get_text()
		direccion = texto2.get_text()+"\n"
		if not nombre or not direccion:
			dialog = StandarDialog(self, "Mensaje JAMedia", _("Debes especificar un Nombre y una Dirección de Reproducción."))
			response = dialog.run()
			dialog.destroy()
			return
		stream = "%s,%s" % (nombre, direccion)
		dialog = StandarDialog(self, "Mensaje JAMedia", _("¿ Confirmas que deseas Agregar este streaming a tu Lista ?"))
		response = dialog.run()
		dialog.destroy()
		if response == gtk.RESPONSE_YES:
			if self.toolbar_list.label.get_text() == _("Mis Emisoras"):
				self.origenes_de_datos.agregar_streaming(stream, self.origenes_de_datos.misradios)
				self.Lista_de_MisRadios = self.origenes_de_datos.Cargar_Tabla("MisRadios")
				self.load_list(None, 2)
			elif self.toolbar_list.label.get_text() == _("Mis Canales"):
				self.origenes_de_datos.agregar_streaming(stream, self.origenes_de_datos.mistv)
				self.Lista_de_MisTelevision = self.origenes_de_datos.Cargar_Tabla("MisTelevision")
				self.load_list(None, 3)

	def set_accion_archivos(self, item, accion):
		if accion == "Copiar":
			dialog = StandarDialog(self, "Mensaje JAMedia", _("¿ Confirmas que Deseas Copiar el Archivo ?"))
			response = dialog.run()
			dialog.destroy()
			if response == gtk.RESPONSE_YES:
				self.origenes_de_datos.copiar_archivo_JAMedia_Video(item.url)
		elif accion == "Borrar":
			dialog = StandarDialog(self, "Mensaje JAMedia", _("¿ Confirmas que Deseas Borrar el Archivo ?"))
			response = dialog.run()
			dialog.destroy()
			if response == gtk.RESPONSE_YES:
				self.origenes_de_datos.borrar_archivo_JAMedia(item.url)
				item.destroy()
		elif accion == "Mover":
			dialog = StandarDialog(self, "Mensaje JAMedia", _("¿ Confirmas que Deseas Mover el Archivo ?"))
			response = dialog.run()
			dialog.destroy()
			if response == gtk.RESPONSE_YES:
				self.origenes_de_datos.mover_archivo_JAMedia(item.url)
				item.destroy()
		elif accion == "Quitar":
			dialog = StandarDialog(self, "Mensaje JAMedia", _("¿ Confirmas que deseas Quitar de la Lista ?"))
			response = dialog.run()
			dialog.destroy()
			if response == gtk.RESPONSE_YES:
				item.destroy()
	#----------------- Operaciones para la lista -------------------- #

	def grabar_streaming(self, item):
		extension = ""
		if item.tipo == "Radio":
			extension = ".mp3"
		elif item.tipo == "TV":
			extension = ".avi"

		hora = time.strftime("%H-%M-%S")
		fecha = str(datetime.date.today())
		archivo = "%s-%s-%s%s" % (fecha, hora, item.texto.split("(")[0], extension)
		archivo = archivo.split(" ")
		nombre = ""
		for a in archivo:
			nombre += a

		archivo = nombre
		archivo = os.path.join(G.DIRECTORIO_MIS_ARCHIVOS, archivo)
		dialog = StandarDialog(self, "Mensaje JAMedia", _("¿ Comenzar a Grabar ?"))
		response = dialog.run()
		dialog.destroy()
		if response == gtk.RESPONSE_YES:
			self.comenzar_grabacion(archivo, item.url.split("\n")[0])

	def comenzar_grabacion(self, archivo, direccion):
		ejecutable = os.path.join(G.DIRECTORIO_BASE, "Mplayer_Grabador.py")
		if self.graba: self.detener_grabacion()
		self.graba = subprocess.Popen('%s****%s' % (direccion, archivo), executable=ejecutable, shell=True)
		self.info_grabar.grabando(direccion)

	def detener_grabacion(self, widget= None):
		if self.info_grabar.label.get_text() == _("Grabador Detenido."): return
		estado = str(self.mplayer_server.get_estado())
		self.activar(None, "stop")
		try:
			self.mplayer_server.mplayer.kill()
			self.graba.kill()
		except:
			pass
		commands.getoutput('killall mplayer')
		self.origenes_de_datos.set_permisos()
		self.graba = None
		self.info_grabar.detenido()
		self.mplayer_server = Mplayer_Reproductor(self.pantalla.window.xid)
		self.mplayer_server.connect("cambio_estado", self.cambio_estado)
		self.mplayer_server.connect("update_progress", self.update_progress)
		self.mplayer_server.connect("video", self.video)
		#self.mplayer_server.connect("mplayer_info", self.mplayer_info)
		if "playing" in estado: self.activar(None, "pausa-play")

	def delete_event(self, widget, event, data=None):
		self.salir()
        	return False
	
	def destroy(self, widget= None, data=None):
		if data:
			data.destroy()
		else:
			widget.destroy()
		return True

	def dialog_salir(self, widget= None, valor= None):
		dialog = StandarDialog(self, "Mensaje JAMedia", _("¿ Salir de JAMedia ?"))
		response = dialog.run()
		dialog.destroy()
		if response == gtk.RESPONSE_YES:
			self.salir()

	def salir(self, widget= None, event= None):
		self.mplayer_server.quit()
		self.detener_grabacion()
		try:
			self.mplayer_server.mplayer.kill()
			self.graba.kill()
		except:
			pass
		self.origenes_de_datos.set_permisos() # por compatibilidad con sugar
		commands.getoutput('killall mplayer')
		sys.exit(0)

if __name__ == "__main__":
    	miventana = JAMedia()
    	gtk.main()

