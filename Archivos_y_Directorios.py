#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Archivos_y_Directorios.py por:
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

import gtk, os, urllib

class Archivos_y_Directorios():
	def __init__(self, DIRECTORIO_DATOS, DIRECTORIO_MIS_ARCHIVOS):
		# Directorio para crear la base de datos
		self.directorio_base = DIRECTORIO_DATOS
		self.directorio_videos = DIRECTORIO_MIS_ARCHIVOS

		self.jamediatv = os.path.join(self.directorio_base, "jamediatv.txt")
		self.jamediaradio = os.path.join(self.directorio_base, "jamediaradio.txt")
		self.misradios = os.path.join(self.directorio_base, "misradios.txt")
		self.mistv = os.path.join(self.directorio_base, "mistv.txt")

	def Generar_Origenes_de_Datos(self):
	# crea los directorios y archivos necesarios
		if not os.path.exists(self.directorio_base):
			os.mkdir(self.directorio_base)
		if not os.path.exists(self.directorio_videos):
			os.mkdir(self.directorio_videos)

		if not os.path.exists(self.jamediatv):
			archivo = open(self.jamediatv, "w") 
			archivo.close()
			os.chmod(os.path.join(self.directorio_base, "jamediatv.txt"), 0666)
		if not os.path.exists(self.jamediaradio):
			archivo = open(self.jamediaradio, "w") 
			archivo.close()
			os.chmod(os.path.join(self.directorio_base, "jamediaradio.txt"), 0666)
		if not os.path.exists(self.misradios):
			archivo = open(self.misradios, "w") 
			archivo.close()
			os.chmod(os.path.join(self.directorio_base, "misradios.txt"), 0666)
		if not os.path.exists(self.mistv):
			archivo = open(self.mistv, "w") 
			archivo.close()
			os.chmod(os.path.join(self.directorio_base, "mistv.txt"), 0666)

		# verificar si las listas están vacías, si lo están se descargan las de JAMedia
		archivo = open(self.jamediaradio, "r") 
		lista = archivo.readlines() 
		archivo.close()
		if not lista: self.Actualizar_Streaming_de_JAMedia()
		archivo = open(self.jamediatv, "r") 
		lista = archivo.readlines() 
		archivo.close()
		if not lista: self.Actualizar_Streaming_de_JAMedia()

	def Actualizar_Streaming_de_JAMedia(self):
	# Descarga los streaming desde la web de JAMedia
		try:
			# streaming JAMediatv
			url = 'https://sites.google.com/site/sugaractivities/jamediaobjects/jam/CanalesJAMediaTV?attredirects=0&d=1'
			urllib.urlretrieve(url, self.jamediatv)
			os.chmod(os.path.join(self.directorio_base, "jamediatv.txt"), 0666)
			# streaming JAMediaradio
			url = 'https://sites.google.com/site/sugaractivities/jamediaobjects/jam/CanalesJAMediaRadios?attredirects=0&d=1'
			urllib.urlretrieve(url, self.jamediaradio)
			os.chmod(os.path.join(self.directorio_base, "jamediaradio.txt"), 0666)
		except:
			print "Error al descargar Streamings de JAMedia"

	def Cargar_Tabla(self, tabla):
	# Lee una tabla y devuelve sus elementos (nombre, streaming)
		if tabla == "Radios":
			archivo = open(self.jamediaradio, "r") 
			lista = archivo.readlines() 
			archivo.close()
			return lista
		elif tabla == "Television":
			archivo = open(self.jamediatv, "r") 
			lista = archivo.readlines() 
			archivo.close()
			return lista
		elif tabla == "MisRadios":
			archivo = open(self.misradios, "r") 
			lista = archivo.readlines() 
			archivo.close()
			return lista
		elif tabla == "MisTelevision":
			archivo = open(self.mistv, "r") 
			lista = archivo.readlines() 
			archivo.close()
			return lista

	def eliminar_streaming(self, stream, tipo):
	# elimina el stream seleccionado
		if tipo == "jamediaradio":
		# elimina un streaming en JAMediaradios
			archivo = open(self.jamediaradio, "r")
			lista = archivo.readlines()
			archivo.close()
			if stream in lista:
				lista.remove(stream)
				os.system("rm " + self.jamediaradio)
				self.Generar_Origenes_de_Datos()
				archivo = open(self.jamediaradio, "w")
				for x in lista:
					archivo.write(x)
				archivo.close()
		elif tipo == "jamediatv":
		# elimina un streaming en jamediatv
			archivo = open(self.jamediatv, "r")
			lista = archivo.readlines()
			archivo.close()

			if stream in lista:
				lista.remove(stream)
				os.system("rm " + self.jamediatv)
				self.Generar_Origenes_de_Datos()
				archivo = open(self.jamediatv, "w")
				for x in lista:
					archivo.write(x)
				archivo.close()
		elif tipo == "MisTelevision":
		# elimina un streaming en jamediatv
			archivo = open(self.mistv, "r")
			lista = archivo.readlines()
			archivo.close()
			if stream in lista:
				lista.remove(stream)
				os.system("rm " + self.mistv)
				self.Generar_Origenes_de_Datos()
				archivo = open(self.mistv, "w")
				for x in lista:
					archivo.write(x)
				archivo.close()
		elif tipo == "MisRadios":
		# elimina un streaming en jamediatv
			archivo = open(self.misradios, "r")
			lista = archivo.readlines()
			archivo.close()
			if stream in lista:
				lista.remove(stream)
				os.system("rm " + self.misradios)
				self.Generar_Origenes_de_Datos()
				archivo = open(self.misradios, "w")
				for x in lista:
					archivo.write(x)
				archivo.close()

	def agregar_streaming(self, streaming, archivo_destino):
	# agrega un streaming a una de las listas del usuario
		archivo = open(archivo_destino, "r")
		lista = archivo.readlines()
		archivo.close()
		if not streaming in lista:
			lista.append(streaming)
			archivo = open(archivo_destino, "w")
			for x in lista:
				archivo.write(x)
			archivo.close()

# ------------------ ARCHIVOS --------------------------------
	def verificar_permisos(self, path):
		# verificar:
		# 1- Si es un archivo o un directorio
		# 2- Si sus permisos permiten la copia, escritura y borrado
		# Comprobar existencia y permisos http://docs.python.org/library/os.html?highlight=os#module-os
		# os.access(path, mode)
		# os.F_OK # si existe la direccion
		# os.R_OK # Permisos de lectura
		# os.W_OK # Permisos de escritura
		# os.X_OK # Permisos de ejecucion
		try:
			if  os.access(path, os.F_OK):
				return os.access(path, os.R_OK), os.access(path, os.W_OK), os.access(path, os.X_OK)
			else:
				return False, False, False
		except:
			return False, False, False

	def copiar_archivo_JAMedia_Video(self, direccion):
	# copia un archivo al directorio de videos de JAMedia
		try:
			if os.path.exists(direccion):
				archivos = os.listdir(self.directorio_videos)
				if not os.path.basename(direccion) in archivos:
					os.system("cp \"" + direccion + "\" \"" + self.directorio_videos + "\"")
					self.get_mensaje_copiado()
					return
				else:
					dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO)
					dialog.set_title("Mensaje JAMedia")
					dialog.set_markup("El Archivo ya Existe en el Directorio Destino, ¿ Deseas Sobreescribirlo ?")
					response = dialog.run()
					dialog.destroy()
					if response == gtk.RESPONSE_YES:
						os.system("cp \"" + direccion + "\" \"" + self.directorio_videos + "\"")
						self.get_mensaje_copiado()
						return
			else:
				print "El archivo no existe"
		except Exception, e:
			print "Error al Copiar un Archivo", e

	def get_mensaje_copiado(self):
		dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK)
		dialog.set_title("Mensaje JAMedia")
		dialog.set_markup("Archivo Copiado")
		response = dialog.run()
		dialog.destroy()

	def borrar_archivo_JAMedia(self, direccion):
	# Borra un Archivo
		try:
			if os.path.exists(direccion):
				os.system("rm \"" + direccion  + "\"")
				self.get_mensaje_borrado()
			else:
				dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK)
				dialog.set_title("Mensaje JAMedia")
				dialog.set_markup("El Archivo no Existe")
				response = dialog.run()
				dialog.destroy()
		except Exception, e:
			print "Error al Borrar un Archivo", e

	def get_mensaje_borrado(self):
		dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK)
		dialog.set_title("Mensaje JAMedia")
		dialog.set_markup("Archivo Eliminado")
		response = dialog.run()
		dialog.destroy()

	def mover_archivo_JAMedia(self, direccion):
	# Mueve un Archivo
		try:
			if os.path.exists(direccion):
				archivos = os.listdir(self.directorio_videos)
				if not os.path.basename(direccion) in archivos:
					os.system("mv \"" + direccion + "\" \"" + self.directorio_videos + "\"")
					self.get_mensaje_movido()
				else:
					dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO)
					dialog.set_title("Mensaje JAMedia")
					dialog.set_markup("El Archivo ya Existe en el Directorio Destino, ¿ Deseas Sobreescribirlo ?")
					response = dialog.run()
					dialog.destroy()
					if response == gtk.RESPONSE_YES:
						os.system("mv \"" + direccion + "\" \"" + self.directorio_videos + "\"")
						self.get_mensaje_movido()
						return
			else:
				dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK)
				dialog.set_title("Mensaje JAMedia")
				dialog.set_markup("El Archivo no Existe")
				response = dialog.run()
				dialog.destroy()
		except Exception, e:
			print "Error al Mover un Archivo", e

	def get_mensaje_movido(self):
		dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK)
		dialog.set_title("Mensaje JAMedia")
		dialog.set_markup("Archivo Movido")
		response = dialog.run()
		dialog.destroy()

	def set_permisos(self):
	 # por compatibilidad con sugar
		for archivo in os.listdir(self.directorio_videos):
			os.chmod(os.path.join(self.directorio_videos, archivo), 0666)

