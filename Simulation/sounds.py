import pygame
import os

SOUND_PATH = os.path.join(os.path.dirname(__file__), 'Assets', 'sounds', 'traffic1.mp3')

class TrafficSound:
    def __init__(self):
        pygame.mixer.init()
        self.sound = pygame.mixer.Sound(SOUND_PATH)
        self.channel = None

    def play(self, loops=-1):
        if not self.channel or not self.channel.get_busy():
            self.channel = self.sound.play(loops=loops)

    def stop(self):
        if self.channel:
            self.channel.stop()

    def is_playing(self):
        return self.channel and self.channel.get_busy()
