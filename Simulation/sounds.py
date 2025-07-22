import pygame
import os

TRAFFIC_SOUND = os.path.join(os.path.dirname(__file__), 'Assets', 'sounds', 'traffic5.mp3')
IGNITION_SOUND = os.path.join(os.path.dirname(__file__), 'Assets', 'sounds', 'ignition.mp3')    
CAR_SOUND = os.path.join(os.path.dirname(__file__), 'Assets', 'sounds', 'car1.mp3')
SPLASH_SCREEN_SOUND = os.path.join(os.path.dirname(__file__), 'Assets', 'sounds', 'splash_screen.mp3')
CRASH_SOUND = os.path.join(os.path.dirname(__file__), 'Assets', 'sounds', 'crash1.mp3')

class TrafficSound:
    def __init__(self):
        pygame.mixer.init()
        self.sound = pygame.mixer.Sound(TRAFFIC_SOUND)
        self.sound.set_volume(0.5)  # Set volume to half
        self.channel = None

    def play(self, loops=-1):
        if not self.channel or not self.channel.get_busy():
            self.channel = self.sound.play(loops=loops)

    def stop(self):
        if self.channel:
            self.channel.stop()

    def is_playing(self):
        return self.channel and self.channel.get_busy()


class IgnitionSound:
    def __init__(self):
        pygame.mixer.init()
        self.sound = pygame.mixer.Sound(IGNITION_SOUND)
        self.channel = None

    def play(self, loops=-1):
        if not self.channel or not self.channel.get_busy():
            self.channel = self.sound.play(loops=loops)

    def stop(self):
        if self.channel:
            self.channel.stop()

    def is_playing(self):
        return self.channel and self.channel.get_busy()

class CarSound:
    def __init__(self):
        pygame.mixer.init()
        self.sound = pygame.mixer.Sound(CAR_SOUND)
        self.sound.set_volume(3)
        self.channel = None

    def play(self, loops=-1):
        if not self.channel or not self.channel.get_busy():
            self.channel = self.sound.play(loops=loops)

    def stop(self):
        if self.channel:
            self.channel.stop()

    def is_playing(self):
        return self.channel and self.channel.get_busy()

class SplashScreenSound:
    def __init__(self):
        pygame.mixer.init()
        self.sound = pygame.mixer.Sound(SPLASH_SCREEN_SOUND)
        self.channel = None

    def play(self, loops=-1):
        if not self.channel or not self.channel.get_busy():
            self.channel = self.sound.play(loops=loops)

    def stop(self):
        if self.channel:
            self.channel.stop()

    def is_playing(self):
        return self.channel and self.channel.get_busy()


class CrashSound:
    def __init__(self):
        pygame.mixer.init()
        self.sound = pygame.mixer.Sound(CRASH_SOUND)
        self.sound.set_volume(0.7)  # Set crash volume
        self.channel = None

    def play(self):
        # Always play crash sound, even if already playing
        self.channel = self.sound.play()

    def stop(self):
        if self.channel:
            self.channel.stop()

    def is_playing(self):
        return self.channel and self.channel.get_busy()