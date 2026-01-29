# Audio System for Harry Potter Adventure
# Handles background music and sound effects

import pygame
import os

# Sound effects - will be procedurally generated if files don't exist
SOUND_EFFECTS = {
    'jump': {'freq': 400, 'duration': 100},
    'attack': {'freq': 200, 'duration': 150},
    'special': {'freq': 600, 'duration': 300},
    'hit': {'freq': 150, 'duration': 100},
    'coin': {'freq': 800, 'duration': 80},
    'health': {'freq': 500, 'duration': 200},
    'enemy_death': {'freq': 100, 'duration': 200},
    'player_death': {'freq': 80, 'duration': 500},
    'level_complete': {'freq': 700, 'duration': 500},
    'area_enter': {'freq': 450, 'duration': 400},
}

# Area music themes (different moods)
AREA_THEMES = {
    'PRIVET DRIVE': {'tempo': 'slow', 'mood': 'tense', 'base_freq': 200},
    'PLATFORM 9¾': {'tempo': 'medium', 'mood': 'exciting', 'base_freq': 300},
    'HOGWARTS GROUNDS': {'tempo': 'medium', 'mood': 'magical', 'base_freq': 400},
    'FORBIDDEN CORRIDOR': {'tempo': 'slow', 'mood': 'scary', 'base_freq': 150},
    'THROUGH THE TRAPDOOR': {'tempo': 'fast', 'mood': 'danger', 'base_freq': 250},
    'GIANT CHESS': {'tempo': 'medium', 'mood': 'epic', 'base_freq': 350},
    'THE FINAL CHAMBER': {'tempo': 'fast', 'mood': 'boss', 'base_freq': 180},
}


class AudioManager:
    """Manages all game audio."""
    
    def __init__(self):
        self.enabled = True
        self.music_volume = 0.4
        self.sfx_volume = 0.6
        self.current_area = None
        self.sounds = {}
        
        # Try to initialize pygame mixer
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self._generate_sounds()
            self.enabled = True
        except Exception as e:
            print(f"Audio initialization failed: {e}")
            self.enabled = False
    
    def _generate_sounds(self):
        """Generate simple sound effects procedurally."""
        import array
        import math
        
        sample_rate = 22050
        
        for name, params in SOUND_EFFECTS.items():
            try:
                freq = params['freq']
                duration = params['duration']
                num_samples = int(sample_rate * duration / 1000)
                
                # Generate waveform
                samples = array.array('h')
                for i in range(num_samples):
                    t = i / sample_rate
                    # Envelope for smooth sound
                    envelope = min(1.0, (num_samples - i) / (num_samples * 0.3))
                    envelope *= min(1.0, i / (num_samples * 0.1))
                    
                    # Different waveforms for different sounds
                    if 'coin' in name or 'level' in name:
                        # Bright sine wave
                        value = math.sin(2 * math.pi * freq * t) * envelope
                    elif 'hit' in name or 'death' in name:
                        # Noise-like
                        value = math.sin(2 * math.pi * freq * t * (1 + 0.5 * math.sin(50 * t))) * envelope
                    else:
                        # Square-ish wave
                        value = (1 if math.sin(2 * math.pi * freq * t) > 0 else -1) * envelope * 0.7
                    
                    samples.append(int(value * 32767 * 0.5))
                
                # Create sound from samples
                sound = pygame.mixer.Sound(buffer=samples)
                sound.set_volume(self.sfx_volume)
                self.sounds[name] = sound
            except Exception as e:
                print(f"Failed to generate sound {name}: {e}")
    
    def play_sound(self, sound_name):
        """Play a sound effect."""
        if not self.enabled:
            return
        
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass
    
    def set_area(self, area_name):
        """Change background music based on area."""
        if area_name == self.current_area:
            return
        
        self.current_area = area_name
        
        if not self.enabled:
            return
        
        # Play area entrance sound
        self.play_sound('area_enter')
        
        # In a full game, we would load and play area-specific music here
        # For now, we just track the area for potential future use
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
    
    def toggle_mute(self):
        """Toggle audio mute."""
        self.enabled = not self.enabled
        if not self.enabled:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        return self.enabled
    
    def stop_all(self):
        """Stop all sounds."""
        if self.enabled:
            pygame.mixer.stop()
            pygame.mixer.music.stop()


# Global audio manager instance
audio_manager = None

def get_audio():
    """Get or create the global audio manager."""
    global audio_manager
    if audio_manager is None:
        audio_manager = AudioManager()
    return audio_manager

