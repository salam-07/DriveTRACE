import pygame
from sounds import TrafficSound, IgnitionSound, CarSound

class SoundManager:
    def __init__(self):
        self.traffic_sound = TrafficSound()
        self.ignition_sound = IgnitionSound()
        self.car_sound = CarSound()
        self.car_sound_timer = pygame.time.get_ticks() + 4000  # 4 seconds after ignition
        self.car_sound_started = False
        
        # Play ignition sound at startup
        self.ignition_sound.play(loops=0)
    
    def update(self, traffic_enabled):
        """Update sound states based on game state"""
        # Play/stop traffic sound based on traffic enabled
        if traffic_enabled:
            if not self.traffic_sound.is_playing():
                self.traffic_sound.play()
        else:
            if self.traffic_sound.is_playing():
                self.traffic_sound.stop()

        # Start car sound 4 seconds after ignition
        now = pygame.time.get_ticks()
        if not self.car_sound_started and now >= self.car_sound_timer:
            self.car_sound.play(loops=-1)  # loop infinite times
            self.car_sound_started = True
