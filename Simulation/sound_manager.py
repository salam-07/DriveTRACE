import pygame
from sounds import TrafficSound, IgnitionSound, CarSound, CrashSound

class SoundManager:
    def __init__(self):
        self.traffic_sound = TrafficSound()
        self.ignition_sound = IgnitionSound()
        self.car_sound = CarSound()
        self.crash_sound = CrashSound()
        self.car_sound_timer = pygame.time.get_ticks() + 4000  # 4 seconds after ignition
        self.car_sound_started = False
        self.paused = False
        self.was_traffic_playing = False
        self.was_car_playing = False
        
        # Play ignition sound at startup
        self.ignition_sound.play(loops=0)
    
    def pause_all_sounds(self):
        """Pause all currently playing sounds"""
        self.paused = True
        self.was_traffic_playing = self.traffic_sound.is_playing()
        self.was_car_playing = self.car_sound_started and hasattr(self.car_sound, 'sound') and self.car_sound.sound.get_num_channels() > 0
        
        if self.was_traffic_playing:
            self.traffic_sound.stop()
        if self.was_car_playing:
            self.car_sound.stop()
    
    def resume_all_sounds(self):
        """Resume previously playing sounds"""
        self.paused = False
        
        if self.was_traffic_playing:
            self.traffic_sound.play()
        if self.was_car_playing:
            self.car_sound.play(loops=-1)
    
    def play_crash_sound(self):
        """Play crash sound effect"""
        if not self.paused:
            self.crash_sound.play()
    
    def update(self, traffic_enabled):
        """Update sound states based on game state"""
        if self.paused:
            return  # Don't update sounds when paused
            
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
