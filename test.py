#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyespeak
e = pyespeak.eSpeak("en")
e.say("Hello World. This is the Python interface to eSpeak.")
e.say("I'm happy to see it is working.")
# This python script does not terminate until all the .say() calls are finished.
