# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

import random
import time
from datetime import datetime, timedelta
from os import path, listdir
from os.path import abspath, dirname, splitext

from ovos_utils.log import LOG
from ovos_workshop.decorators import intent_handler
from ovos_workshop.intents import IntentBuilder
from ovos_workshop.skills import OVOSSkill
from tinytag import TinyTag

__author__ = 'aussieW'


class FartingSkill(OVOSSkill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.random_farting = False  # flag to indicate whether random farting mode is active
        self.counter = 0  # variable to increment to make the scheduled event unique

        # Search the sounds directory for sound files and load into a list.
        valid_codecs = ['.mp3', '.wav']
        self.path_to_sound_files = path.join(self.root_dir, 'sounds')
        self.sound_files = [
            f for f in listdir(self.path_to_sound_files)
            if splitext(f)[1] in valid_codecs
        ]

    def initialize(self):
        self.register_intent_file('accuse.intent', self.handle_accuse_intent)
        self.register_intent_file('request.intent', self.handle_request_intent)
        self.register_intent_file('random.intent', self.handle_random_intent)

    def handle_request_intent(self, message):
        # play a randomly selected sound file
        self.fart_and_comment()

    def handle_fart_event(self, message):
        # create a scheduled event to fart at a random interval between 1 minute and half an hour
        if not self.random_farting:
            return
        LOG.info("Farting skill: Handling fart event")

        self.cancel_scheduled_event('randon_fart' + str(self.counter))
        self.counter += 1
        self.schedule_event(self.handle_fart_event,
                            datetime.now() +
                            timedelta(seconds=random.randrange(60, 1800)),
                            name='random_fart' + str(self.counter))
        self.fart_and_comment()

    def handle_accuse_intent(self, message):
        # make a comment when accused of farting
        self.speak_dialog('apologise')

    def handle_random_intent(self, message):
        # initiate random farting
        LOG.info("Farting skill: Triggering random farting")
        self.speak("got it")
        time.sleep(.5)
        self.speak("don't worry, I'll be very discrete")
        self.random_farting = True
        self.schedule_event(self.handle_fart_event,
                            datetime.now() +
                            timedelta(seconds=random.randrange(30, 60)),
                            name='random_fart' + str(self.counter))

    def fart_and_comment(self):
        # play a randomly selected fart noise and make a comment
        LOG.info("Farting skill: Fart and comment")
        fart = path.join(self.path_to_sound_files, random.choice(self.sound_files))
        tag = TinyTag.get(fart)
        self.play_audio(fart, instant=True)
        LOG.info("Fart duration " + str(int(tag.duration)))
        delay = 2
        time.sleep(int(tag.duration) + delay)
        self.speak_dialog('noise')

    @intent_handler(IntentBuilder('halt_farting').require('halt').require('farting'))
    def halt_farting(self, message):
        # stop farting
        LOG.info("Farting skill: Stopping")
        # if in random fart mode, cancel the scheduled event
        if self.random_farting:
            LOG.info("Farting skill: Stopping random farting event")
            self.speak_dialog('cancel')
            self.random_farting = False
            self.cancel_scheduled_event('random_fart' + str(self.counter))
