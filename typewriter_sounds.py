#!/usr/bin/env python
from __future__ import print_function
import sys
import os
import random
from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq
import sdl2
import sdl2.sdlmixer

class AudioPlayback (object):

    def __init__ (self):
        if sdl2.SDL_Init(sdl2.SDL_INIT_AUDIO) != 0:
            raise RuntimeError("Cannot initialize audio system: {}".format(sdl2.SDL_GetError()))
        fmt = sdl2.sdlmixer.MIX_DEFAULT_FORMAT
        if sdl2.sdlmixer.Mix_OpenAudio(44100, fmt, 2, 1024) != 0:
            raise RuntimeError("Cannot open mixed audio: {}".format(sdl2.sdlmixer.Mix_GetError()))
        sdl2.sdlmixer.Mix_AllocateChannels(64)
        self._bank = {}

    def load (self, filename):
        filename = os.path.abspath(filename)
        uuid = os.path.normcase(filename)
        if uuid not in self._bank:
            if not isinstance(filename, bytes):
                filename = filename.encode('utf-8')
            sample = sdl2.sdlmixer.Mix_LoadWAV(filename)
            if sample is None:
                return None
            self._bank[uuid] = sample
        return self._bank[uuid]

    def play (self, sample, channel=-1):
        channel = sdl2.sdlmixer.Mix_PlayChannel(channel, sample, 0)
        if channel < 0:
            return -1
        return channel

    def is_playing (self, channel):
        return sdl2.sdlmixer.Mix_Playing(channel)

    def set_volume (self, channel, volume = 1.0):
        if channel < 0:
            return False
        volint = int(volume * sdl2.sdlmixer.MIX_MAX_VOLUME)
        sdl2.sdlmixer.Mix_Volume(channel, volint)
        return True

class TypeWriterSounds:

    def __init__(self):
        # * Initialises pygame mixer. A buffer of 512 bytes is required for
        # * better performance

        self.ap = AudioPlayback()
        self.bellcount = 0

        # * Preloads sound samples
        self.keysounds = {
            'load' : self.ap.load('samples/manual_load_long.wav'),
            'shift' : self.ap.load('samples/manual_shift.wav'),
            'delete': self.ap.load('samples/manual_shift.wav'),
            'space': self.ap.load('samples/manual_space.wav'),
            'key': self.ap.load('samples/manual_key.wav'),
            'enter': self.ap.load('samples/manual_key.wav'),
            'bell': self.ap.load('samples/manual_bell.wav')
        }

        # * Get keynames from X11
        self.keys = {}
        for name in dir(XK):
            if name[:3] == "XK_" :
                self.keys[name] = getattr(XK, name) 


        print("TypeWriter Sounds Emulator. v1.0")
        print("type now and enjoy the vintage experience!...")
        self.ap.play(self.keysounds['bell'])
        self.ap.play(self.keysounds['enter'])


        # * Activates key grabber

        self.local_dpy = display.Display()
        self.record_dpy = display.Display()

        # Check if the extension is present
        if not self.record_dpy.has_extension("RECORD"):
            print ("RECORD extension not found")
            sys.exit(1)



        # Create a recording context; we only want key events
        self.ctx = self.record_dpy.record_create_context(
            0,
            [record.AllClients],
            [{
                'core_requests': (0, 0),
                'core_replies': (0, 0),
                'ext_requests': (0, 0, 0, 0),
                'ext_replies': (0, 0, 0, 0),
                'delivered_events': (0, 0),
                'device_events': (X.KeyPress, X.KeyPress),
                'errors': (0, 0),
                'client_started': False,
                'client_died': False,
            }])


        try:
            # Enable the context; this only returns after a call to 
            # record_disable_context,
            # while calling the callback function in the meantime
            self.record_dpy.record_enable_context(  self.ctx, \
                                                  self.record_callback)
        except KeyboardInterrupt:
            # Exits if CTRL-c is typed
            self.record_dpy.record_free_context(self.ctx)
            print('\nbye!')
            sys.exit(0)

    def record_callback(self, reply):
        if reply.category != record.FromServer:
            return
        if reply.client_swapped:
            print("* received swapped protocol data, cowardly ignored")
            return
        if not len(reply.data) or ord(reply.data[0]) < 2:
            # not an event
            return

        data = reply.data
        while len(data):
            event, data = rq.EventField(None).\
                parse_binary_value( data, 
                                   self.record_dpy.display, 
                                   None, None)

            if event.type == X.KeyPress:
                # * If a key is pressed, gets its keycode 
                pr = event.type == X.KeyPress and "Press" or "Release"
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
                

                # * Plays an audio sample according the keycode   

                # * - Enter      
                if keysym == self.keys['XK_Return']:
                    sound = self.keysounds['enter']
                    self.bellcount = 0
                
                # * - Spacebar
                elif keysym == self.keys['XK_space']:
                    sound = self.keysounds['space']
                    self.bellcount += 1
                
                # * - Delete and backspace   
                elif (keysym == self.keys['XK_Delete']) or \
                     (keysym == self.keys['XK_BackSpace']):
                    sound = self.keysounds['delete']
                    self.bellcount -= 1
                    if self.bellcount <= 0:
                        self.bellcount = 0
                
                # * - Shift (and other control keys) 
                elif    keysym == self.keys['XK_Up'] or \
                        keysym == self.keys['XK_Down'] or \
                        keysym == self.keys['XK_Left'] or \
                        keysym == self.keys['XK_Right'] or \
                        keysym == self.keys['XK_Control_L'] or \
                        keysym == self.keys['XK_Control_R'] or \
                        keysym == self.keys['XK_Shift_R'] or \
                        keysym == self.keys['XK_Shift_L'] or \
                        keysym == self.keys['XK_Alt_L'] or \
                        keysym == self.keys['XK_Alt_R'] or \
                        keysym == self.keys['XK_Tab'] or\
                        keysym == self.keys['XK_Caps_Lock'] or \
                        keysym == self.keys['XK_F1'] or \
                        keysym == self.keys['XK_F2'] or \
                        keysym == self.keys['XK_F3'] or \
                        keysym == self.keys['XK_F4'] or \
                        keysym == self.keys['XK_F5'] or \
                        keysym == self.keys['XK_F6'] or \
                        keysym == self.keys['XK_F7'] or \
                        keysym == self.keys['XK_F8'] or \
                        keysym == self.keys['XK_F9'] or \
                        keysym == self.keys['XK_F10'] or \
                        keysym == self.keys['XK_F11'] or \
                        keysym == self.keys['XK_F12'] or \
                        keysym == self.keys['XK_Super_L'] or\
                        keysym == self.keys['XK_Super_R'] or\
                        keysym == self.keys['XK_Escape'] or\
                        keysym > 65535:
                            
                    sound = self.keysounds['shift']
                
                # * - Page Up/Down, Home/End: play page load
                elif    keysym == self.keys['XK_Page_Up'] or \
                        keysym == self.keys['XK_Next'] or\
                        keysym == self.keys['XK_Home'] or \
                        keysym == self.keys['XK_End']:
                    sound = self.keysounds['load']
                
                # * - A simple key         
                else:
                    sound = self.keysounds['key']
                    self.bellcount += 1
                
                # * - After 70 consecutive keypresses, play the bell sound    
                if self.bellcount == 70:
                    sound = self.keysounds['bell']
                    self.bellcount = 0

                # volume = random.random() * 0.2 + 0.8
                # sound.set_volume(volume)
                # sound.play()
                self.ap.play(sound)

if __name__ == '__main__':
    TypeWriterSounds()
