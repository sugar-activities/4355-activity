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

import gobject, time, os, subprocess, platform
from gettext import gettext as _
UPDATE_TIME = 30
STDOUT = "/tmp/jamediaout%d" % time.time()
STDERR = "/dev/null"
MPLAYER = "mplayer"
if "olpc" in platform.platform(): MPLAYER = "./mplayer"

class Mplayer_Reproductor(gobject.GObject):
	__gsignals__ = {"cambio_estado":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
	"update_progress":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_FLOAT,)),
	"video":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,)),
	"mplayer_info":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,))}
	''' Posibles estados: "playing Audio_Video", "paused Audio_Video", "stoped Audio_Video", "playing Radio", "playing TV", None '''
	def __init__(self, id_pantalla):
		self.__gobject_init__()
		self.ejecutable = MPLAYER
		self.id_pantalla = id_pantalla

		self.tipo_de_datos = None
		self.mplayer = None
		self.salida = None
		self.entrada = None
		self.Actualizador = False
		self.pista_actual = None

		self.estado= None
		self.progress= 0.0
		#self.name_origen= None

    		estado= property(self.get_estado, self.set_estado)
		progress= property(self.get_progress, self.set_progress)

		'''
		estructura= "%s -wid %i -slave -idle -nolirc -quiet −volume 100" % (self.ejecutable, self.id_pantalla)
		self.mplayer= subprocess.Popen(estructura, shell=True, stdin=subprocess.PIPE, 
			stdout=open(STDOUT,"w+b"), stderr=open(STDERR,"r+b"), universal_newlines=True)

		self.entrada= self.mplayer.stdin
		self.salida= open(STDOUT,"r")'''

		self.set_estado(None)

	# ----------- Propiedades -----------
	def get_estado(self):
		return self.estado
	def set_estado(self, valor= None):
		self.estado = valor
		self.emit("cambio_estado", self.get_estado())

	def get_progress(self):
		return self.progress
	def set_progress(self, valor):
		self.progress = valor
		self.emit("update_progress", self.get_progress())
	# ----------- Propiedades -----------

	# ------------------------ ACTUALIZACIONES De REPRODUCCION ------------------------
	def update_progress(self):
		if not self.entrada.closed:
			self.entrada.write("%s 0\n" % ("get_percent_pos"))
			self.entrada.flush()
			linea = self.salida.readline()
			if linea:
				if "ANS_PERCENT_POSITION" in linea:
					self.get_progress_in_mplayer(linea)
				elif "Video: no video" in linea or "Audio only file format detected" in linea:
					self.emit("video", False)
				elif "Cache" in linea:
					self.get_progress_cache_in_mplayer(linea)
				elif "Movie-Aspect" in linea:
					self.emit("video", True)
				elif "Starting playback" in linea:
					#self.emit("cambio_estado", self.get_estado())
					pass
				elif "Position:" in linea or "VO:" in linea or "AO:" in linea:
					# AO: [pulse] 22050Hz 2ch s16le (2 bytes per sample)
					# VO: [xv] 540x360 => 540x360 Planar YV12
					#self.emit("mplayer_info", linea)
					pass
				elif "Resolving" in linea or "Connecting" in linea:
					#self.emit("mplayer_info", linea)
					pass
				elif "Name" in linea:
					#self.name_origen= linea.split(": ")[-1]
					pass
				elif "Playing" in linea:
					#self.name_origen= linea.split("Playing ")[-1]
					pass
				elif "Opening" in linea or "AUDIO" in linea or "Selected" in linea \
				or "Genre" in linea or "Website" in linea or "Bitrate" in linea:
					'''
					Opening video decoder: [ffmpeg] FFmpeg's libavcodec codec family
					Selected video codec: [ffh264] vfm: ffmpeg (FFmpeg H.264)
					Opening audio decoder: [faad] AAC (MPEG2/4 Advanced Audio Coding)
					AUDIO: 44100 Hz, 2 ch, s16le, 119.9 kbit/8.50% (ratio: 14989->176400)
					Selected audio codec: [faad] afm: faad (FAAD AAC (MPEG-2/MPEG-4 Audio))'''
					#self.emit("mplayer_info", linea)
					pass
				else:
					'''
					mplayer: Symbol `ff_codec_bmp_tags' has different size in shared object, consider re-linking
					eos/Beautiful Liar - Beyonce ft Shakira.
					 stream 0: video (h264), -vid 0
					[lavf] stream 1: audio (aac), -aid 0
					VIDEOopen: No such file or directory
					[MGA] Couldn't open: /dev/mga_vid
					open: No such file or directory
					[MGA] Couldn't open: /dev/mga_vid
					[VO_TDFXFB] Can't open /dev/fb0: Permission denied.
					[VO_3DFX] Unable to open /dev/3dfx.
					Failed to open VDPAU backend libvdpau_nvidia.so: cannot open shared object file: No such file or 						directo==========================================================================
					==========================================================================
					==========================================================================
					==========================================================================
					AO: [pulse] 44100Hz 2ch s16le (2 bytes per sample)
					Starting playback...
					VO: [xv] 320x240 => 320x240 Planar YV12'''
					pass
		return True

	def get_progress_in_mplayer(self, linea):
		try:
			if "Cache size" in linea:
				return
			try:
				progress = float(linea[linea.index('=')+1:-1])
				if self.get_progress()!= progress:
					self.set_progress(progress)
					if self.get_progress() >= 100.0:
						self.set_estado("stoped Audio_Video")
			except Exception, e:
				print "Error en Progreso de Reproducción: %s" % (e)
				#print linea
		except Exception, e:
			print "Error en Progreso de Reproducción: %s" % (e)
			#print linea

	def get_progress_cache_in_mplayer(self, linea):
		if "Cache not responding" in linea: return
		try:
			if "Cache size" in linea: 
				return
			try:
				progress = float((linea.split(": ")[-1]).split("%")[0])/20*100
			except:
				return
			if self.get_progress()!= progress:
				self.set_progress(progress)
				#self.emit("mplayer_info", "Cargando Caché")
		except Exception, e:
			print "Error en Carga de Caché: %s" % (e)
			#print linea
	# ------------------------ ACTUALIZACIONES De REPRODUCCION ------------------------
	
	# ------------------------ REPRODUCCION -------------------------------------------
	def seek(self, valor):
		if self.Actualizador:
			gobject.source_remove(self.Actualizador)
			self.Actualizador = False
		self.entrada.write('seek %s 1 0\n' % (float(valor)))
		self.entrada.flush()
		self.set_estado("playing Audio_Video")
		self.Actualizador = gobject.timeout_add(UPDATE_TIME, self.update_progress)

	def play(self, direccion, tipo_de_datos):
		self.tipo_de_datos = tipo_de_datos
		if tipo_de_datos == "Radio":
			self.play_radio(direccion)
		elif tipo_de_datos == "TV":
			self.play_tv(direccion)
		elif tipo_de_datos == "Audio_Video":
			self.play_Audio_Video(direccion)
	def play_Audio_Video(self, direccion):
		self.pista_actual = "%s%s%s" % ("\"", direccion, "\"")
		self.play_archivo(self.pista_actual)
	def play_archivo(self, direccion):
		ejecutable_cache_pantalla = "%s -cache %i -wid %i" % (self.ejecutable, 1024, self.id_pantalla)
		estructura= "%s -slave -idle -nolirc -rtc -nomouseinput -noconsolecontrols -nojoystick" % (ejecutable_cache_pantalla)
		self.mplayer = subprocess.Popen(estructura, shell=True, stdin=subprocess.PIPE, 
			stdout=open(STDOUT,"w+b"), stderr=open(STDOUT,"r+b"), universal_newlines=True)
		self.entrada = self.mplayer.stdin
		self.salida = open(STDOUT,"r")
		self.entrada.write("loadfile %s 0\n" % direccion)
		self.entrada.flush()
		if self.Actualizador:
			gobject.source_remove(self.Actualizador)
			self.Actualizador = False
		self.Actualizador = gobject.timeout_add(UPDATE_TIME, self.update_progress)
		self.pista_actual = direccion
		self.set_estado("playing Audio_Video")
		self.emit("mplayer_info", self.pista_actual)

	def play_radio(self, direccion):
		ejecutable_cache_pantalla = "%s -cache %i" % (self.ejecutable, 32)
		estructura= "%s -slave -idle -nolirc -quiet -rtc -nomouseinput -noconsolecontrols -nojoystick" % (ejecutable_cache_pantalla)
		self.mplayer= subprocess.Popen(estructura, shell=True, stdin=subprocess.PIPE, 
			stdout=open(STDOUT,"w+b"), stderr=open(STDOUT,"r+b"), universal_newlines=True)
		self.entrada= self.mplayer.stdin
		self.salida= open(STDOUT,"r")
		self.entrada.write("loadfile %s 0\n" % direccion)
		self.entrada.flush()
		if self.Actualizador:
			gobject.source_remove(self.Actualizador)
			self.Actualizador = False
		#self.Actualizador= gobject.timeout_add(UPDATE_TIME, self.update_progress)
		self.pista_actual= direccion
		self.set_estado("playing Radio")
		self.emit("mplayer_info", self.pista_actual)

	def play_tv(self, direccion):
		ejecutable_cache_pantalla = "%s -cache %i -wid %i" % (self.ejecutable, 1024, self.id_pantalla)
		estructura= "%s -slave -idle -nolirc -quiet -rtc -nomouseinput -noconsolecontrols -nojoystick" % (ejecutable_cache_pantalla)
		self.mplayer= subprocess.Popen(estructura, shell=True, stdin=subprocess.PIPE, 
			stdout=open(STDOUT,"w+b"), stderr=open(STDOUT,"r+b"), universal_newlines=True)
		self.entrada= self.mplayer.stdin
		self.salida= open(STDOUT,"r")
		self.entrada.write("loadfile %s 0\n" % direccion)
		self.entrada.flush()
		if self.Actualizador:
			gobject.source_remove(self.Actualizador)
			self.Actualizador = False
		#self.Actualizador= gobject.timeout_add(UPDATE_TIME, self.update_progress)
		self.pista_actual= direccion
		self.set_estado("playing TV")
		self.emit("mplayer_info", self.pista_actual)

	def pause_play(self):
		try:
			if self.entrada:
				if self.get_estado() == "playing Audio_Video": # pausa
					self.entrada.write('pause 0\n')
					self.entrada.flush()
					if self.Actualizador:
						gobject.source_remove(self.Actualizador)
						self.Actualizador = False
					self.set_estado("paused Audio_Video")
					self.emit("mplayer_info", _("Reproducción Pausada"))
				elif self.get_estado() == "paused Audio_Video": 
					self.entrada.write('pause 0\n') # hace unpause
					self.entrada.flush()
					if self.Actualizador:
						gobject.source_remove(self.Actualizador)
						self.Actualizador = False
					self.Actualizador = gobject.timeout_add(UPDATE_TIME, self.update_progress)
					self.set_estado("playing Audio_Video")
					self.emit("mplayer_info", "%s: %s" % (_("Reproduciendo"), self.pista_actual))
		except Exception, e:
			print "HA OCURRIDO UN ERROR EN PAUSE_PLAY DEL REPRODUCTOR", e

	def quit(self, widget=None):
		try:
			if self.entrada:
				self.entrada.write('%s 0\n' % "quit")
				self.entrada.flush()
				if self.Actualizador:
					gobject.source_remove(self.Actualizador)
					self.Actualizador = False
		except Exception, e:
			print "HA OCURRIDO UN ERROR EN QUIT DEL REPRODUCTOR", e
		self.set_progress(0.0)
		if os.path.exists(STDOUT): os.unlink(STDOUT)
		self.pista_actual = None
		self.set_estado(None)
		self.emit("mplayer_info", _("Reproducción Detenida"))
	# ------------------------ REPRODUCCION -------------------------------------------

