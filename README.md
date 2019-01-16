Typewriter sounds emulator for Python
=====================================

Forked from [aizquier/typewriter-sounds](https://github.com/aizquier/typewriter-sounds).
Using SDL2 instead of pygame since pygame causes high CPU usage.

This program plays typewriter sounds each time a key is pressed, giving
the user the vintage experience of and old typewriter machine.

The code is inspired on the keylogger demo that comes in the The Python
X Library ( <http://python-xlib.sourceforge.net/> ). The logic is
simple: grab the keycode of a pressed key, and instead to record it (as
any keylogger does), just play a sound.

As the key detection is made using Xlib, this program should work on
those platforms that support X11. It was developed and tested under
Linux.

Sound samples come from <https://www.freesound.org/>, some were modified
for this project.

Requeriments
------------

-   Python 2.7
-   [X11 and Xlib bindings for Python](http://python-xlib.sourceforge.net/)
-   [PySDL2](http://pygame.org) (for sound)

Usage
-----

cd into the project's directory and type:

    $ python typewriter_sounds.py

to stop the program, just type CTRL-C.

Reference
----

Code and sounds samples come from:
- [aizquier/typewriter-sounds](https://github.com/aizquier/typewriter-sounds).
- [skywind3000/vim-keysound](https://github.com/skywind3000/vim-keysound).

