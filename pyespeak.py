#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       pyespeak.py
#       
#       Copyright 2011 Raphael Michel <webmaster@raphaelmichel.de>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

"""Python Interface for the eSpeak speech synthesizer
	
@note: Built for eSpeak 1.44.04
@note: Not supported eSpeak commandline options: -w, -b, -q, -x, -X, --compile, --ipa, --pho, --phonout, --split, --stdout, --voices
@todo: Add a wait() method (if possible)"""
__author__ = "Raphael Michel"
__contact__ = "raphael@geeksfactory.de"
__copyright__ = "2011 geek's factory"
__version__ = "0.1.0"

ESPEAKCMD = "espeak"
VOICEDIR = "/usr/share/espeak-data/voices"

import subprocess
import os
import sys

class eSpeakException(Exception):
	"Base exception class"
	pass

class eSpeakExceptionClosed(eSpeakException):
	"This exception is raised when you try to use an eSpeak process which is already closed"
	pass

class eSpeak:
	"""The interface itself.
	
	@ivar open: Is the interface connected to an eSpeak process?
	@type open: bool
	"""
	
	open = False
	
	def __init__(self, voice = "default", amplitude = 100, gap = 1, capitals = 0, 
				linelength = 0, pitch = 50, speed = 175, markup = False,
				nofinalpause = False, path = False, punct = False):
		"""Initializes an eSpeak process
		
		@type voice: string
		@keyword voice: Voice to use (e.g. 'en' or 'de')
		@type amplitude: int
		@keyword amplitude: Amplitude, 0 to 200, default is 100
		@type gap: int
		@keyword gap: Word gap. Pause between words, units of 10mS at the default speed
		@type capitals: int
		@keyword capitals: Indicate capital letters with: 1=sound, 2=the word "capitals", higher values indicate a pitch increase.
		@type linelength: int
		@keyword linelength: Line length. If not zero (which is the default), consider lines less than this length as end-of-clause
		@type pitch: int
		@keyword pitch: Pitch adjustment, 0 to 99, default is 50
		@type speed: int
		@keyword speed: Speed in words per minute, 80 to 450, default is 175
		@type markup: bool
		@keyword markup: Interpret SSML markup, and ignore other < > tags
		@type nofinalpause: bool
		@keyword nofinalpause: No final sentence pause at the end of the text
		@type path: string
		@keyword path: Specifies the directory containing the espeak-data directory
		@type punct: string
		@keyword punct: Speak the names of punctuation characters during speaking. If this is C{True}, all punctuation is spoken.
		"""
		args = [ESPEAKCMD]
		
		if voice is not "default" and os.path.exists(VOICEDIR+'/'+voice):
			args += ['-v', voice]
		if amplitude is not 100 and amplitude >= 0 and amplitude <= 200:
			args += ['-a', str(amplitude)]
		if gap is not 1:
			args += ['-g', str(gap)]
		if capitals is not 0:
			args += ['-k', str(capitals)]
		if linelength is not 0:
			args += ['-l', str(linelength)]
		if pitch is not 50 and pitch < 100 and pitch >= 0:
			args += ['-p', str(pitch)]
		if speed is not 175 and speed > 79 and speed < 451:
			args += ['-s', str(speed)]
		if markup:
			args += ['-m']
		if nofinalpause:
			args += ['-z']
		if path:
			args += ['--path='+path]
		if punct is True:
			args += ['--punct']
		elif punct is not False:
			args += ['--punct='+punct]
		self.args = args
		self.sp = subprocess.Popen(self.args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		self.open = True
	
	def say(self, something):
		"""Says something (adds it to the queue). something can be any type of string or file-like object.
		
		@type something: str or file
		@param something: Text to be spoken
		"""
		if not self.open:
			raise eSpeakExceptionClosed('process already closed.')
		if (sys.version_info[0] == 2 and isinstance(something, basestring)) or isinstance(something, str):
			if sys.version_info[0] == 3:
				self.sp.stdin.write(bytes(something.strip()+"\n", "utf-8"))
				self.sp.stdin.flush()
			else:
				self.sp.stdin.write(something.strip()+"\n")
				self.sp.stdin.flush()
		elif hasattr(something, 'read'):
			if sys.version_info[0] == 3:
				self.sp.stdin.write(bytes(something.read().strip()+"\n", "utf-8"))
				self.sp.stdin.flush()
			else:
				self.sp.stdin.write(something.read().strip()+"\n")
				self.sp.stdin.flush()
		else:
			raise ValueError('I don\'t know what this is.')
	
	def reopen(self):
		"""Waits until everything in the queue is spoken and then closes the process and opens an new one.
		
		Unfortunately there doesn't seem to be any other way to wait for the end of the audio output without terminating the process.
		"""
		try:
			self.sp.communicate()
			self.sp.terminate()
		except:
			pass # don't worry, be happy.
		self.sp = subprocess.Popen(self.args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		self.open = True
	
	def close(self):
		"""Waits until everything in the queue is spoken and then closes the process.
		"""
		try:
			self.sp.communicate()
			self.sp.terminate()
		except:
			pass # don't worry, be happy.
		self.open = False
	
	def terminate(self):
		"""Close the process immediately.
		"""
		try:
			self.sp.terminate()
		except:
			pass # don't worry, be happy.
		self.open = False
		
	def __del__(self):
		"""Calls .close() before the script can end.
		"""
		self.close()
