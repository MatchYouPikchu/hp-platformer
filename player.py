# Player Class with Mario-style movement and unique special attacks

import pygame
import math
import os
import random
from settings import *
from characters import get_character


class Projectile:
    """Projectile for ranged attacks with character-specific visuals."""

    def __init__(self, x, y, direction, damage, color, speed=PROJECTILE_SPEED, size=PROJECTILE_SIZE, 
                 vel_x=None, vel_y=0, character_name=None):
        self.x = float(x)
        self.y = float(y)
        self.direction = direction
        self.damage = damage
        self.color = color
        self.speed = speed
        self.size = size
        self.active = True
        self.rect = pygame.Rect(int(x), int(y), size + 10, size + 10)
        self.trail = []
        self.trail_max = 12
        self.character_name = character_name or 'default'
        self.age = 0
        self.vel_x = vel_x if vel_x is not None else speed * direction
        self.vel_y = vel_y

    def update(self):
        self.age += 1
        self.trail.append((self.x, self.y, self.age))
        if len(self.trail) > self.trail_max:
            self.trail.pop(0)
        
        self.x += self.vel_x
        self.y += self.vel_y
        self.rect.x = int(self.x) - 5
        self.rect.y = int(self.y) - 5
        if self.rect.right < -100 or self.rect.left > LEVEL_WIDTH + 100:
            self.active = False
        if self.rect.top > SCREEN_HEIGHT + 100 or self.rect.bottom < -100:
            self.active = False

    def draw(self, screen, camera_x):
        screen_x = int(self.x - camera_x)
        if -50 < screen_x < SCREEN_WIDTH + 50:
            center_x = screen_x + self.size // 2
            center_y = int(self.y) + self.size // 2
            
            if self.character_name == 'Voldemort':
                self._draw_avada_kedavra(screen, center_x, center_y, camera_x)
            elif self.character_name == 'Harry':
                self._draw_expelliarmus(screen, center_x, center_y, camera_x)
            elif self.character_name == 'Hermione':
                self._draw_stupefy(screen, center_x, center_y, camera_x)
            elif self.character_name == 'Dragon':
                self._draw_fireball(screen, center_x, center_y, camera_x)
            else:
                self._draw_default(screen, center_x, center_y, camera_x)

    def _draw_avada_kedavra(self, screen, cx, cy, camera_x):
        """Voldemort's deadly green beam - Killing Curse style."""
        # Long deadly green beam
        beam_length = 60
        beam_width = 8
        
        # Trail of death
        for i, (tx, ty, age) in enumerate(self.trail):
            trail_x = int(tx - camera_x) + self.size // 2
            trail_y = int(ty) + self.size // 2
            alpha = (i + 1) / len(self.trail) if self.trail else 1
            trail_len = int(beam_length * alpha * 0.6)
            # Green death trail
            for j in range(3):
                offset = j * 2
                color_intensity = int(200 * alpha) - j * 40
                pygame.draw.line(screen, (0, max(0, color_intensity), 0), 
                               (trail_x - trail_len * self.direction, trail_y + offset - 2),
                               (trail_x, trail_y + offset - 2), max(1, int(beam_width * 0.3)))
        
        # Main beam - thick green with black edges
        pygame.draw.line(screen, (0, 80, 0), (cx - beam_length * self.direction, cy), (cx + 20 * self.direction, cy), beam_width + 6)
        pygame.draw.line(screen, (0, 180, 0), (cx - beam_length * self.direction, cy), (cx + 20 * self.direction, cy), beam_width + 2)
        pygame.draw.line(screen, (0, 255, 0), (cx - beam_length * self.direction, cy), (cx + 15 * self.direction, cy), beam_width - 2)
        pygame.draw.line(screen, (150, 255, 150), (cx - beam_length * 0.5 * self.direction, cy), (cx + 10 * self.direction, cy), 3)
        
        # Death skull particle at tip
        skull_pulse = abs(math.sin(self.age * 0.3)) * 5
        pygame.draw.circle(screen, (0, 255, 0), (cx + int(15 * self.direction), cy), int(8 + skull_pulse))
        pygame.draw.circle(screen, (200, 255, 200), (cx + int(15 * self.direction), cy), int(4 + skull_pulse * 0.5))
        
        # Crackling dark energy around beam
        for _ in range(3):
            spark_x = cx + random.randint(-30, 20) * self.direction
            spark_y = cy + random.randint(-15, 15)
            pygame.draw.circle(screen, (0, 200, 0), (spark_x, spark_y), random.randint(1, 3))

    def _draw_expelliarmus(self, screen, cx, cy, camera_x):
        """Harry's red/gold disarming spell."""
        # Spiral red/gold energy
        for i, (tx, ty, age) in enumerate(self.trail):
            trail_x = int(tx - camera_x) + self.size // 2
            trail_y = int(ty) + self.size // 2
            alpha = (i + 1) / len(self.trail)
            # Alternating red/gold spiral
            offset_y = int(math.sin(age * 0.5 + i * 0.3) * 8 * alpha)
            trail_size = max(2, int(6 * alpha))
            if i % 2 == 0:
                pygame.draw.circle(screen, (255, int(100 * alpha), 0), (trail_x, trail_y + offset_y), trail_size)
            else:
                pygame.draw.circle(screen, (255, int(200 * alpha), 0), (trail_x, trail_y - offset_y), trail_size)
        
        # Main spell - swirling red/gold
        for i in range(4):
            angle = self.age * 0.4 + i * math.pi / 2
            offset_x = int(math.cos(angle) * 6)
            offset_y = int(math.sin(angle) * 6)
            color = (255, 50, 0) if i % 2 == 0 else (255, 200, 50)
            pygame.draw.circle(screen, color, (cx + offset_x, cy + offset_y), 6)
        
        # Bright center
        pygame.draw.circle(screen, (255, 150, 50), (cx, cy), 10)
        pygame.draw.circle(screen, (255, 220, 150), (cx, cy), 6)
        pygame.draw.circle(screen, (255, 255, 200), (cx, cy), 3)

    def _draw_stupefy(self, screen, cx, cy, camera_x):
        """Hermione's stunning spell - blue/purple magic."""
        # Magical spiral trail
        for i, (tx, ty, age) in enumerate(self.trail):
            trail_x = int(tx - camera_x) + self.size // 2
            trail_y = int(ty) + self.size // 2
            alpha = (i + 1) / len(self.trail)
            # Magic sparkles
            for j in range(2):
                spark_angle = age * 0.3 + j * math.pi
                spark_dist = 10 * alpha
                sx = trail_x + int(math.cos(spark_angle) * spark_dist)
                sy = trail_y + int(math.sin(spark_angle) * spark_dist)
                spark_size = max(1, int(4 * alpha))
                pygame.draw.circle(screen, (150, 100, 255), (sx, sy), spark_size)
        
        # Main orb with rings
        for ring in range(3):
            ring_size = 12 - ring * 3
            ring_color = (100 + ring * 50, 50 + ring * 30, 255)
            pygame.draw.circle(screen, ring_color, (cx, cy), ring_size)
        
        # Rotating magic symbols (simplified as small circles)
        for i in range(5):
            angle = self.age * 0.2 + i * math.pi * 2 / 5
            dist = 15
            symbol_x = cx + int(math.cos(angle) * dist)
            symbol_y = cy + int(math.sin(angle) * dist)
            pygame.draw.circle(screen, (200, 150, 255), (symbol_x, symbol_y), 3)
            pygame.draw.circle(screen, WHITE, (symbol_x, symbol_y), 1)

    def _draw_fireball(self, screen, cx, cy, camera_x):
        """Dragon's fireball with flames."""
        # Fire trail
        for i, (tx, ty, age) in enumerate(self.trail):
            trail_x = int(tx - camera_x) + self.size // 2
            trail_y = int(ty) + self.size // 2
            alpha = (i + 1) / len(self.trail)
            # Flame particles rising
            flame_y = trail_y - int((1 - alpha) * 15)
            flame_size = max(3, int(12 * alpha))
            # Orange to red gradient
            r = 255
            g = int(200 * alpha)
            pygame.draw.circle(screen, (r, g, 0), (trail_x, flame_y), flame_size)
            pygame.draw.circle(screen, (255, 255, int(100 * alpha)), (trail_x, flame_y), max(1, flame_size // 2))
        
        # Main fireball - layered flames
        for layer in range(4):
            layer_size = 16 - layer * 3
            # Color from outer (red) to inner (yellow-white)
            r = 255
            g = 100 + layer * 50
            b = layer * 30
            offset_x = int(math.sin(self.age * 0.5 + layer) * 3)
            offset_y = int(math.cos(self.age * 0.5 + layer) * 3)
            pygame.draw.circle(screen, (r, g, b), (cx + offset_x, cy + offset_y), layer_size)
        
        # Bright core
        pygame.draw.circle(screen, (255, 255, 200), (cx, cy), 5)
        pygame.draw.circle(screen, WHITE, (cx, cy), 2)
        
        # Ember particles
        for _ in range(2):
            ember_x = cx + random.randint(-20, 5) * self.direction
            ember_y = cy + random.randint(-10, 10)
            pygame.draw.circle(screen, (255, 150, 0), (ember_x, ember_y), random.randint(1, 3))

    def _draw_default(self, screen, cx, cy, camera_x):
        """Default magical projectile."""
        # Draw trail
        for i, (tx, ty, age) in enumerate(self.trail):
            trail_x = int(tx - camera_x) + self.size // 2
            trail_y = int(ty) + self.size // 2
            alpha_ratio = (i + 1) / len(self.trail) if self.trail else 1
            trail_size = max(1, int(self.size * 0.4 * alpha_ratio))
            fade_color = tuple(min(255, int(c * 0.5 + 127 * alpha_ratio)) for c in self.color)
            pygame.draw.circle(screen, fade_color, (trail_x, trail_y), trail_size)
        
        # Outer glow
        glow_color = tuple(min(255, c + 60) for c in self.color)
        pygame.draw.circle(screen, glow_color, (cx, cy), self.size // 2 + 4)
        # Main projectile
        pygame.draw.circle(screen, self.color, (cx, cy), self.size // 2 + 1)
        # Inner bright core
        core_color = tuple(min(255, c + 100) for c in self.color)
        pygame.draw.circle(screen, core_color, (cx, cy), max(3, self.size // 3))


class SpecialEffect:
    """Visual effect for special attacks with particles, glow, and damage."""

    def __init__(self, x, y, effect_type, duration, color, owner, damage=0, damage_radius=0):
        self.x = x
        self.y = y
        self.effect_type = effect_type
        self.duration = duration
        self.max_duration = duration
        self.color = color
        self.owner = owner
        self.active = True
        self.particles = []
        self.damage = damage
        self.damage_radius = damage_radius
        self.damaged_enemies = set()  # Track which enemies were hit (by id)
        self._init_particles()

    def _init_particles(self):
        import random
        if self.effect_type == 'lightning':
            # Main lightning bolts + electric sparks
            for _ in range(35):
                self.particles.append({
                    'x': random.randint(-50, 50), 'y': random.randint(-100, 30),
                    'vx': random.uniform(-4, 4), 'vy': random.uniform(-5, 2),
                    'life': random.uniform(0.4, 1.0), 'size': random.randint(3, 8),
                    'type': 'spark'
                })
            # Ground impact sparks
            for _ in range(15):
                self.particles.append({
                    'x': random.randint(-60, 60), 'y': random.randint(-10, 20),
                    'vx': random.uniform(-6, 6), 'vy': random.uniform(-10, -3),
                    'life': 1.0, 'size': random.randint(2, 5),
                    'type': 'ground'
                })
        elif self.effect_type in ('spell_burst', 'dark_magic'):
            # Multiple rings of magical orbs
            for ring in range(3):
                num_orbs = 8 + ring * 4
                for i in range(num_orbs):
                    angle = (i / num_orbs) * math.pi * 2
                    speed = 3 + ring * 2
                    self.particles.append({
                        'x': 0, 'y': 0, 'vx': math.cos(angle) * speed, 'vy': math.sin(angle) * speed,
                        'life': 1.0, 'size': 12 - ring * 2, 'ring': ring,
                        'angle': angle
                    })
            # Add trailing sparkles
            for _ in range(20):
                self.particles.append({
                    'x': random.randint(-20, 20), 'y': random.randint(-20, 20),
                    'vx': random.uniform(-2, 2), 'vy': random.uniform(-2, 2),
                    'life': random.uniform(0.5, 1.0), 'size': random.randint(2, 5),
                    'ring': -1
                })
        elif self.effect_type == 'fire_breath':
            # Intense multi-layered flame with upward spread
            for _ in range(50):
                self.particles.append({
                    'x': 0, 'y': random.randint(-25, 25),
                    'vx': self.owner.direction * random.uniform(10, 20),
                    'vy': random.uniform(-3, 3),
                    'life': random.uniform(0.5, 1.0), 'size': random.randint(8, 18),
                    'heat': random.uniform(0, 1)
                })
            # Add upward-rising flames for flying enemy coverage
            for _ in range(15):
                self.particles.append({
                    'x': self.owner.direction * random.randint(20, 80), 'y': 0,
                    'vx': self.owner.direction * random.uniform(5, 10),
                    'vy': random.uniform(-8, -4),  # Rises upward
                    'life': random.uniform(0.6, 1.0), 'size': random.randint(10, 16),
                    'heat': random.uniform(0.5, 1)
                })
            # Smoke particles
            for _ in range(15):
                self.particles.append({
                    'x': self.owner.direction * random.uniform(60, 100),
                    'y': random.randint(-30, 30),
                    'vx': self.owner.direction * random.uniform(2, 5),
                    'vy': random.uniform(-4, -1),
                    'life': random.uniform(0.3, 0.8), 'size': random.randint(15, 25),
                    'heat': -1  # smoke marker
                })
        elif self.effect_type == 'heal_aura':
            # Magical sparkles rising in spirals
            for i in range(25):
                angle = random.uniform(0, math.pi * 2)
                dist = random.uniform(15, 70)
                self.particles.append({
                    'x': math.cos(angle) * dist, 'y': math.sin(angle) * dist - 20,
                    'vx': math.cos(angle + math.pi/2) * 0.5, 'vy': random.uniform(-2, -4),
                    'life': random.uniform(0.6, 1.0), 'size': random.randint(4, 10),
                    'angle': angle, 'dist': dist
                })
            # Plus symbols (healing icons)
            for _ in range(6):
                self.particles.append({
                    'x': random.randint(-50, 50), 'y': random.randint(-60, 0),
                    'vx': 0, 'vy': random.uniform(-1.5, -3),
                    'life': 1.0, 'size': 12, 'is_cross': True
                })
        elif self.effect_type == 'ground_slam':
            # Rocks and debris
            for i in range(18):
                self.particles.append({
                    'x': (i - 9) * 20, 'y': 0,
                    'vx': (i - 9) * 3, 'vy': random.uniform(-12, -5),
                    'life': 1.0, 'size': random.randint(10, 22),
                    'rotation': random.uniform(0, math.pi * 2),
                    'rot_speed': random.uniform(-0.3, 0.3)
                })
            # Ground cracks
            for i in range(10):
                self.particles.append({
                    'x': (i - 5) * 30, 'y': 5,
                    'vx': 0, 'vy': 0,
                    'life': 1.0, 'size': random.randint(3, 6),
                    'is_crack': True, 'crack_len': random.randint(30, 60)
                })

    def update(self, dt):
        self.duration -= dt
        if self.duration <= 0:
            self.active = False
        # Update effect position to follow owner for certain effects
        if self.effect_type in ('fire_breath',):
            self.x = self.owner.rect.centerx + (30 * self.owner.direction)
            self.y = self.owner.rect.centery
        # Update particles
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= dt / self.max_duration

    def get_damage_rect(self):
        """Get the damage area for this effect."""
        if self.damage <= 0 or self.damage_radius <= 0:
            return None
        progress = 1 - (self.duration / self.max_duration)
        
        if self.effect_type == 'dark_magic':
            # Expanding circle centered on player
            current_radius = int(self.damage_radius * min(1.0, progress * 2))
            return pygame.Rect(int(self.x) - current_radius, int(self.y) - current_radius,
                             current_radius * 2, current_radius * 2)
        elif self.effect_type == 'shockwave':
            # Full circle expanding outward - hits flying enemies too
            current_radius = int(self.damage_radius * progress)
            return pygame.Rect(int(self.x) - current_radius, int(self.y) - current_radius,
                             current_radius * 2, current_radius * 2)
        elif self.effect_type == 'ground_slam':
            # Wide area with good vertical coverage for flying enemies
            width = int(self.damage_radius * 2 * min(1.0, progress * 3))
            height = 150  # Tall enough to hit flying enemies
            return pygame.Rect(int(self.x) - width // 2, int(self.y) - height, width, height + 30)
        elif self.effect_type == 'fire_breath':
            # Cone in front of owner - wider vertical spread to hit flying enemies
            length = int(self.damage_radius * min(1.0, progress * 1.5))
            height = 180  # Taller to reliably hit flying enemies
            # Offset upward slightly so flames reach higher
            if self.owner.direction > 0:
                return pygame.Rect(int(self.x), int(self.y) - height // 2 - 30, length, height)
            else:
                return pygame.Rect(int(self.x) - length, int(self.y) - height // 2 - 30, length, height)
        elif self.effect_type == 'lightning':
            # Patronus charging forward - wide horizontal area
            progress = 1 - (self.duration / self.max_duration)
            patronus_dist = int(progress * 250)
            direction = self.owner.direction
            if direction > 0:
                return pygame.Rect(int(self.x), int(self.y) - 60, patronus_dist + 80, 120)
            else:
                return pygame.Rect(int(self.x) - patronus_dist - 80, int(self.y) - 60, patronus_dist + 80, 120)
        elif self.effect_type == 'heal_aura':
            # Expanding circle around unicorn
            current_radius = int(self.damage_radius * min(1.0, progress * 2.5))
            return pygame.Rect(int(self.x) - current_radius, int(self.y) - current_radius,
                             current_radius * 2, current_radius * 2)
        elif self.effect_type == 'spell_burst':
            # Expanding magical burst
            current_radius = int(self.damage_radius * min(1.0, progress * 2))
            return pygame.Rect(int(self.x) - current_radius, int(self.y) - current_radius,
                             current_radius * 2, current_radius * 2)
        return None

    def check_enemy_hit(self, enemy):
        """Check if this effect hits an enemy and deal damage."""
        if self.damage <= 0 or id(enemy) in self.damaged_enemies:
            return False
        damage_rect = self.get_damage_rect()
        if damage_rect and damage_rect.colliderect(enemy.rect):
            self.damaged_enemies.add(id(enemy))
            return True
        return False

    def draw(self, screen, camera_x):
        screen_x = int(self.x - camera_x)
        if screen_x < -300 or screen_x > SCREEN_WIDTH + 300:
            return

        progress = 1 - (self.duration / self.max_duration)
        
        # Screen shake indicator for epic effects
        shake = 0
        if progress < 0.3 and self.effect_type in ('lightning', 'ground_slam', 'dark_magic'):
            shake = int((1 - progress / 0.3) * 4 * math.sin(progress * 50))

        if self.effect_type == 'lightning':
            # HARRY'S PATRONUS - Silver/white stag charging forward
            direction = self.owner.direction
            
            # Brilliant silver/white flash on cast
            if progress < 0.1:
                flash_alpha = int(200 * (1 - progress / 0.1))
                flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flash_surf.fill((200, 220, 255, flash_alpha))
                screen.blit(flash_surf, (0, 0))
            
            # Stag position - charges forward
            stag_x = screen_x + direction * int(progress * 250)
            stag_y = int(self.y) - 20
            
            # Ethereal trail behind the stag
            for i in range(15):
                trail_progress = max(0, progress - i * 0.03)
                if trail_progress > 0:
                    trail_x = screen_x + direction * int(trail_progress * 250)
                    trail_alpha = int(150 * (1 - i / 15))
                    trail_size = int(30 - i * 1.5)
                    if trail_size > 0:
                        trail_surf = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
                        pygame.draw.circle(trail_surf, (180, 200, 255, trail_alpha), (trail_size, trail_size), trail_size)
                        screen.blit(trail_surf, (trail_x - trail_size, stag_y - trail_size))
            
            # Draw the stag Patronus
            stag_scale = min(1.0, progress * 3)  # Grow into full size quickly
            
            # Body (elongated oval)
            body_w = int(60 * stag_scale)
            body_h = int(35 * stag_scale)
            body_surf = pygame.Surface((body_w + 20, body_h + 20), pygame.SRCALPHA)
            pygame.draw.ellipse(body_surf, (200, 220, 255, 200), (10, 10, body_w, body_h))
            pygame.draw.ellipse(body_surf, (230, 240, 255, 255), (15, 15, body_w - 10, body_h - 10))
            if direction < 0:
                body_surf = pygame.transform.flip(body_surf, True, False)
            screen.blit(body_surf, (stag_x - body_w // 2 - 10, stag_y - body_h // 2))
            
            # Neck and head
            head_x = stag_x + direction * int(35 * stag_scale)
            head_y = stag_y - int(15 * stag_scale)
            # Neck
            pygame.draw.line(screen, (220, 235, 255), 
                           (stag_x + direction * int(20 * stag_scale), stag_y - int(10 * stag_scale)),
                           (head_x, head_y), int(8 * stag_scale))
            # Head
            pygame.draw.circle(screen, (200, 220, 255), (head_x, head_y), int(12 * stag_scale))
            pygame.draw.circle(screen, (230, 245, 255), (head_x, head_y), int(8 * stag_scale))
            
            # Majestic antlers
            antler_base_x = head_x
            antler_base_y = head_y - int(8 * stag_scale)
            for side in [-1, 1]:
                # Main antler branch
                for branch in range(4):
                    branch_angle = math.radians(-70 + branch * 25) * side * direction
                    branch_len = int((20 + branch * 8) * stag_scale)
                    ax = antler_base_x + side * int(5 * stag_scale)
                    ay = antler_base_y
                    ex = ax + int(math.cos(branch_angle) * branch_len) * side * direction
                    ey = ay - int(abs(math.sin(branch_angle)) * branch_len)
                    thickness = max(1, int((4 - branch * 0.5) * stag_scale))
                    pygame.draw.line(screen, (220, 235, 255), (ax, ay), (ex, ey), thickness)
                    pygame.draw.line(screen, WHITE, (ax, ay), (ex, ey), max(1, thickness - 1))
                    # Sub-branches
                    if branch > 0:
                        sub_angle = branch_angle + side * direction * 0.4
                        sub_len = branch_len * 0.5
                        pygame.draw.line(screen, (200, 220, 255), 
                                       (ex, ey), 
                                       (ex + int(math.cos(sub_angle) * sub_len), ey - int(abs(math.sin(sub_angle)) * sub_len)),
                                       max(1, thickness - 1))
            
            # Legs (in running pose)
            leg_positions = [
                (-15, 0, -20, 25, progress * 8),      # Back leg 1
                (-5, 0, 5, 28, progress * 8 + 1),     # Back leg 2  
                (15, 0, 25, 22, progress * 8 + 2),    # Front leg 1
                (25, 0, 15, 26, progress * 8 + 3),    # Front leg 2
            ]
            for lx, ly, end_offset, leg_len, phase in leg_positions:
                leg_x = stag_x + direction * int(lx * stag_scale)
                leg_y = stag_y + int(5 * stag_scale)
                # Running animation
                leg_swing = math.sin(phase) * 15
                foot_x = leg_x + direction * int((end_offset + leg_swing) * stag_scale * 0.3)
                foot_y = leg_y + int(leg_len * stag_scale)
                pygame.draw.line(screen, (200, 220, 255), (leg_x, leg_y), (foot_x, foot_y), int(4 * stag_scale))
            
            # Ethereal glow around the stag
            glow_size = int(50 * stag_scale)
            glow_surf = pygame.Surface((glow_size * 3, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (180, 200, 255, 60), (0, 0, glow_size * 3, glow_size * 2))
            screen.blit(glow_surf, (stag_x - glow_size * 1.5, stag_y - glow_size))
            
            # Sparkles around the Patronus
            for i in range(8):
                spark_angle = progress * 10 + i * 0.8
                spark_dist = 40 + math.sin(spark_angle * 2) * 15
                sx = stag_x + int(math.cos(spark_angle) * spark_dist)
                sy = stag_y + int(math.sin(spark_angle) * spark_dist * 0.5)
                pygame.draw.circle(screen, (230, 240, 255), (sx, sy), 3)
                pygame.draw.circle(screen, WHITE, (sx, sy), 1)
            
            # Light rays emanating from stag
            if progress > 0.2:
                for i in range(6):
                    ray_angle = (i / 6) * math.pi * 2 + progress * 2
                    ray_len = 30 + progress * 40
                    rx = stag_x + int(math.cos(ray_angle) * 20)
                    ry = stag_y + int(math.sin(ray_angle) * 10)
                    rex = rx + int(math.cos(ray_angle) * ray_len)
                    rey = ry + int(math.sin(ray_angle) * ray_len * 0.5)
                    ray_alpha = int(100 * (1 - progress * 0.5))
                    pygame.draw.line(screen, (200, 220, 255), (rx, ry), (rex, rey), 2)

        elif self.effect_type == 'shockwave':
            # RON'S POWERFUL PUNCH - Orange/red force explosion
            # Initial flash
            if progress < 0.1:
                flash_alpha = int(150 * (1 - progress / 0.1))
                flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flash_surf.fill((255, 150, 0, flash_alpha))
                screen.blit(flash_surf, (0, 0))
            
            radius = int(progress * 200)
            
            # Ground cracks radiating outward
            for i in range(8):
                crack_angle = (i / 8) * math.pi * 2
                crack_len = int(progress * 120)
                for seg in range(5):
                    seg_start = seg * crack_len // 5
                    seg_end = (seg + 1) * crack_len // 5
                    jitter = random.randint(-8, 8) if seg > 0 else 0
                    sx = screen_x + int(math.cos(crack_angle) * seg_start)
                    sy = int(self.y) + int(math.sin(crack_angle) * seg_start * 0.3)
                    ex = screen_x + int(math.cos(crack_angle) * seg_end) + jitter
                    ey = int(self.y) + int(math.sin(crack_angle) * seg_end * 0.3)
                    pygame.draw.line(screen, (80, 40, 0), (sx, sy), (ex, ey), 4)
                    pygame.draw.line(screen, (150, 80, 20), (sx, sy), (ex, ey), 2)
            
            # Multiple shockwave rings
            for ring in range(5):
                r = max(1, radius - ring * 25)
                if r > 0:
                    thickness = max(2, 10 - ring * 2)
                    alpha = max(0, 255 - ring * 40 - int(progress * 100))
                    ring_surf = pygame.Surface((r * 2 + 20, r * 2 + 20), pygame.SRCALPHA)
                    color = (255, 200 - ring * 30, 50 - ring * 10, alpha)
                    pygame.draw.circle(ring_surf, color, (r + 10, r + 10), r, thickness)
                    screen.blit(ring_surf, (screen_x - r - 10, int(self.y) - r * 0.3 - 10))
            
            # Fist impact glow at center
            punch_glow = int(40 * (1 - progress * 0.7))
            pygame.draw.circle(screen, (255, 150, 50), (screen_x, int(self.y)), punch_glow)
            pygame.draw.circle(screen, (255, 220, 150), (screen_x, int(self.y)), punch_glow // 2)
            pygame.draw.circle(screen, WHITE, (screen_x, int(self.y)), punch_glow // 4)
            
            # Debris particles
            for i in range(16):
                angle = (i / 16) * math.pi * 2 + i * 0.3
                dist = 30 + progress * 100
                height = int(math.sin(progress * math.pi) * 40 * (1 - i % 3 * 0.2))
                dx = screen_x + int(math.cos(angle) * dist)
                dy = int(self.y) - height + int(math.sin(angle) * dist * 0.2)
                size = 3 + (i % 4)
                pygame.draw.circle(screen, (139, 90, 43), (dx, dy), size)

        elif self.effect_type == 'spell_burst':
            # HERMIONE'S SPELL BURST - Blue/purple magical knowledge
            # Brilliant blue flash
            if progress < 0.15:
                flash_alpha = int(180 * (1 - progress / 0.15))
                flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flash_surf.fill((100, 100, 255, flash_alpha))
                screen.blit(flash_surf, (0, 0))
            
            # Magic circle with runes
            circle_r = int(50 + progress * 100)
            # Outer circle
            pygame.draw.circle(screen, (100, 50, 200), (screen_x, int(self.y)), circle_r, 4)
            pygame.draw.circle(screen, (150, 100, 255), (screen_x, int(self.y)), circle_r - 8, 2)
            pygame.draw.circle(screen, (200, 150, 255), (screen_x, int(self.y)), circle_r - 20, 2)
            
            # Rotating runes around the circle
            for i in range(8):
                rune_angle = (i / 8) * math.pi * 2 + progress * 4
                rx = screen_x + int(math.cos(rune_angle) * (circle_r - 5))
                ry = int(self.y) + int(math.sin(rune_angle) * (circle_r - 5) * 0.7)
                # Draw rune symbol (diamond with cross)
                rune_size = 10
                pygame.draw.polygon(screen, (200, 180, 255), [
                    (rx, ry - rune_size), (rx + rune_size // 2, ry),
                    (rx, ry + rune_size), (rx - rune_size // 2, ry)
                ])
                pygame.draw.line(screen, WHITE, (rx - 4, ry), (rx + 4, ry), 2)
                pygame.draw.line(screen, WHITE, (rx, ry - 4), (rx, ry + 4), 2)
            
            # Expanding spell projectiles in star pattern
            for i in range(5):
                spell_angle = (i / 5) * math.pi * 2 - math.pi / 2 + progress * 2
                spell_dist = 20 + progress * 150
                sx = screen_x + int(math.cos(spell_angle) * spell_dist)
                sy = int(self.y) + int(math.sin(spell_angle) * spell_dist * 0.6)
                # Spell orb with trail
                for trail in range(5):
                    t_dist = spell_dist - trail * 15
                    if t_dist > 0:
                        tx = screen_x + int(math.cos(spell_angle) * t_dist)
                        ty = int(self.y) + int(math.sin(spell_angle) * t_dist * 0.6)
                        t_size = 10 - trail * 2
                        t_alpha = 255 - trail * 40
                        pygame.draw.circle(screen, (150, 100, 255), (tx, ty), t_size)
                        pygame.draw.circle(screen, (200, 150, 255), (tx, ty), max(1, t_size - 3))
                # Main orb
                pygame.draw.circle(screen, (100, 50, 200), (sx, sy), 15)
                pygame.draw.circle(screen, (180, 130, 255), (sx, sy), 10)
                pygame.draw.circle(screen, WHITE, (sx, sy), 5)
            
            # Floating book pages / sparkles
            for i in range(12):
                page_angle = (i / 12) * math.pi * 2 + progress * 3 + i * 0.5
                page_dist = 40 + math.sin(progress * 6 + i) * 20
                px = screen_x + int(math.cos(page_angle) * page_dist)
                py = int(self.y) + int(math.sin(page_angle) * page_dist * 0.5) - int(progress * 30)
                # Small square "page"
                page_size = 6
                pygame.draw.rect(screen, (230, 220, 255), (px - page_size // 2, py - page_size // 2, page_size, page_size))
                pygame.draw.rect(screen, (150, 130, 200), (px - page_size // 2, py - page_size // 2, page_size, page_size), 1)
            
            # Central knowledge burst
            burst_size = int(30 * (1 - progress * 0.5))
            pygame.draw.circle(screen, (200, 180, 255), (screen_x, int(self.y)), burst_size)
            pygame.draw.circle(screen, WHITE, (screen_x, int(self.y)), burst_size // 2)

        elif self.effect_type == 'dark_magic':
            # AVADA KEDAVRA - deadly green skull explosion
            # Green flash at start
            if progress < 0.2:
                flash_alpha = int(100 * (1 - progress / 0.2))
                flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flash_surf.fill((0, 255, 0, flash_alpha))
                screen.blit(flash_surf, (0, 0))
            
            # Expanding death ring
            ring_radius = int(progress * 150)
            for i in range(4):
                r = max(1, ring_radius - i * 15)
                thickness = max(1, 8 - i * 2)
                alpha = max(0, 255 - i * 50 - int(progress * 100))
                ring_surf = pygame.Surface((r * 2 + 20, r * 2 + 20), pygame.SRCALPHA)
                pygame.draw.circle(ring_surf, (0, 255, 0, alpha), (r + 10, r + 10), r, thickness)
                screen.blit(ring_surf, (screen_x - r - 10, int(self.y) - r - 10))
            
            # Green skull apparition in center
            skull_size = int(40 * min(1, progress * 2))
            skull_alpha = int(200 * (1 - progress * 0.5))
            # Skull shape (simplified)
            pygame.draw.circle(screen, (0, 180, 0), (screen_x, int(self.y) - 10), skull_size)  # Head
            pygame.draw.circle(screen, (0, 100, 0), (screen_x - skull_size // 3, int(self.y) - skull_size // 3), skull_size // 4)  # Eye
            pygame.draw.circle(screen, (0, 100, 0), (screen_x + skull_size // 3, int(self.y) - skull_size // 3), skull_size // 4)  # Eye
            pygame.draw.ellipse(screen, (0, 80, 0), (screen_x - skull_size // 4, int(self.y), skull_size // 2, skull_size // 3))  # Jaw
            
            # Swirling green death energy
            for i in range(16):
                angle = (i / 16) * math.pi * 2 + progress * 8
                dist = 40 + progress * 100
                px = screen_x + int(math.cos(angle) * dist)
                py = int(self.y) + int(math.sin(angle) * dist * 0.6)
                # Green death orbs
                pygame.draw.circle(screen, (0, 150, 0), (px, py), 10)
                pygame.draw.circle(screen, (0, 255, 0), (px, py), 6)
                pygame.draw.circle(screen, (150, 255, 150), (px, py), 3)
            
            # Snake-like energy trails
            for i in range(8):
                angle = (i / 8) * math.pi * 2 + progress * 5
                for seg in range(8):
                    seg_angle = angle + seg * 0.15
                    seg_dist = 30 + seg * 12 + progress * 60
                    sx = screen_x + int(math.cos(seg_angle) * seg_dist)
                    sy = int(self.y) + int(math.sin(seg_angle) * seg_dist * 0.5)
                    size = max(2, 8 - seg)
                    pygame.draw.circle(screen, (0, 200 - seg * 15, 0), (sx, sy), size)
                    pygame.draw.circle(screen, DARK_GREEN, (int(px), int(py)), size - 3)
            
            # Central dark vortex
            for ring in range(6):
                r = int(15 + ring * 12 + progress * 25 - ring * 3)
                if r > 0:
                    alpha = 255 - ring * 30
                    vortex_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
                    pygame.draw.circle(vortex_surf, (20, 50, 20, alpha), (r + 2, r + 2), r, 3)
                    screen.blit(vortex_surf, (screen_x - r - 2, int(self.y) - 15 - r - 2))
            
            # Evil runes floating
            for i in range(4):
                rune_angle = (i / 4) * math.pi * 2 + progress * 5
                rune_dist = 70 + progress * 30
                rx = screen_x + math.cos(rune_angle) * rune_dist
                ry = int(self.y) - 15 + math.sin(rune_angle) * 20
                # Simple rune shape
                pygame.draw.polygon(screen, (100, 200, 100), [
                    (rx, ry - 8), (rx + 6, ry), (rx, ry + 8), (rx - 6, ry)
                ], 2)

        elif self.effect_type == 'ground_slam':
            # HAGRID'S MIGHTY GROUND SLAM - Earthquake devastation
            # Brown/orange flash on impact
            if progress < 0.15:
                flash_alpha = int(150 * (1 - progress / 0.15))
                flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flash_surf.fill((139, 90, 43, flash_alpha))
                screen.blit(flash_surf, (0, 0))
            
            shake_y = int(math.sin(progress * 50) * 8 * (1 - progress))
            
            # MASSIVE shockwave on ground
            shockwave_r = int(progress * 200)
            for ring in range(4):
                r = max(1, shockwave_r - ring * 30)
                if r > 0:
                    thickness = max(2, 12 - ring * 3)
                    alpha = max(0, 200 - ring * 40 - int(progress * 80))
                    # Elliptical shockwave (ground level)
                    ring_surf = pygame.Surface((r * 2 + 20, r + 20), pygame.SRCALPHA)
                    pygame.draw.ellipse(ring_surf, (139, 90, 43, alpha), (10, 5, r * 2, r // 2), thickness)
                    screen.blit(ring_surf, (screen_x - r - 10, int(self.y) - r // 4 + shake_y))
            
            # Deep ground cracks radiating outward
            for i in range(12):
                crack_angle = (i / 12) * math.pi * 2
                crack_len = int(progress * 180)
                points = [(screen_x, int(self.y) + shake_y)]
                for seg in range(8):
                    dist = (seg + 1) * crack_len / 8
                    jitter_x = random.randint(-12, 12)
                    jitter_y = random.randint(-6, 6)
                    cx = screen_x + int(math.cos(crack_angle) * dist) + jitter_x
                    cy = int(self.y) + int(math.sin(crack_angle) * dist * 0.25) + jitter_y + shake_y
                    points.append((cx, cy))
                if len(points) > 1:
                    pygame.draw.lines(screen, (40, 25, 15), False, points, 5)
                    pygame.draw.lines(screen, (80, 50, 30), False, points, 3)
                    pygame.draw.lines(screen, (120, 80, 40), False, points, 1)
            
            # Flying boulders
            for i in range(15):
                angle = (i / 15) * math.pi * 2
                dist = 40 + progress * 120
                height = int(math.sin(progress * math.pi) * (80 + i * 5))
                bx = screen_x + int(math.cos(angle) * dist)
                by = int(self.y) - height + int(math.sin(angle) * dist * 0.2) + shake_y
                size = 8 + (i % 6) * 3
                # 3D rock shape
                pygame.draw.circle(screen, (80, 60, 40), (bx + 2, by + 2), size)  # Shadow
                pygame.draw.circle(screen, (139, 110, 70), (bx, by), size)
                pygame.draw.circle(screen, (180, 150, 100), (bx - 2, by - 2), size // 2)  # Highlight
            
            # Hagrid fist imprint at center
            fist_size = int(50 * min(1, progress * 3))
            pygame.draw.ellipse(screen, (60, 40, 20), 
                              (screen_x - fist_size, int(self.y) - fist_size // 3 + shake_y, fist_size * 2, fist_size))
            pygame.draw.ellipse(screen, (40, 25, 10), 
                              (screen_x - fist_size, int(self.y) - fist_size // 3 + shake_y, fist_size * 2, fist_size), 3)
            
            # Dust clouds
            for i in range(5):
                dust_x = screen_x + (i - 2) * 60
                dust_size = int(40 + progress * 50)
                dust_alpha = int(120 * (1 - progress * 0.8))
                dust_surf = pygame.Surface((dust_size * 2, dust_size), pygame.SRCALPHA)
                pygame.draw.ellipse(dust_surf, (180, 160, 130, dust_alpha), (0, 0, dust_size * 2, dust_size))
                screen.blit(dust_surf, (dust_x - dust_size, int(self.y) - dust_size // 2 - int(progress * 30) + shake_y))

        elif self.effect_type == 'heal_aura':
            # UNICORN'S RAINBOW BURST - Magical healing aurora
            # Rainbow flash
            if progress < 0.2:
                flash_alpha = int(120 * (1 - progress / 0.2))
                flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flash_surf.fill((255, 200, 255, flash_alpha))
                screen.blit(flash_surf, (0, 0))
            
            # Multiple rainbow rings expanding outward
            rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]
            for i, color in enumerate(rainbow_colors):
                ring_r = int(20 + progress * 150 - i * 15)
                if ring_r > 5:
                    alpha = max(0, 200 - int(progress * 100))
                    ring_surf = pygame.Surface((ring_r * 2 + 20, ring_r * 2 + 20), pygame.SRCALPHA)
                    pygame.draw.circle(ring_surf, (*color, alpha), (ring_r + 10, ring_r + 10), ring_r, 4)
                    screen.blit(ring_surf, (screen_x - ring_r - 10, int(self.y) - 30 - ring_r - 10))
            
            # Central unicorn horn glow
            horn_glow = int(40 * (1 + math.sin(progress * 15) * 0.3))
            for layer in range(5):
                layer_size = horn_glow - layer * 6
                if layer_size > 0:
                    alpha = 255 - layer * 40
                    glow_surf = pygame.Surface((layer_size * 2, layer_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (255, 255, 255, alpha), (layer_size, layer_size), layer_size)
                    screen.blit(glow_surf, (screen_x - layer_size, int(self.y) - 50 - layer_size))
            
            # Spiral rainbow sparkles rising
            for i in range(20):
                sparkle_angle = (i / 20) * math.pi * 6 + progress * 8
                sparkle_dist = 30 + (i / 20) * 60 * progress
                sparkle_height = int(i * 8 * progress)
                sx = screen_x + int(math.cos(sparkle_angle) * sparkle_dist)
                sy = int(self.y) - 30 - sparkle_height
                color = rainbow_colors[i % len(rainbow_colors)]
                pygame.draw.circle(screen, color, (sx, sy), 5)
                pygame.draw.circle(screen, WHITE, (sx, sy), 2)
            
            # Healing hearts floating up
            for i in range(6):
                heart_x = screen_x + int(math.sin(progress * 5 + i * 1.5) * 50)
                heart_y = int(self.y) - 20 - int(progress * 100) - i * 25
                heart_size = 8
                # Simple heart shape
                pygame.draw.circle(screen, (255, 150, 200), (heart_x - heart_size // 2, heart_y), heart_size // 2)
                pygame.draw.circle(screen, (255, 150, 200), (heart_x + heart_size // 2, heart_y), heart_size // 2)
                pygame.draw.polygon(screen, (255, 150, 200), [
                    (heart_x - heart_size, heart_y), (heart_x, heart_y + heart_size), (heart_x + heart_size, heart_y)
                ])
            
            # Magical stars
            for i in range(8):
                star_angle = (i / 8) * math.pi * 2 + progress * 3
                star_dist = 60 + progress * 50
                star_x = screen_x + int(math.cos(star_angle) * star_dist)
                star_y = int(self.y) - 30 + int(math.sin(star_angle) * star_dist * 0.4)
                # 4-point star
                star_size = 8
                pygame.draw.polygon(screen, (255, 255, 200), [
                    (star_x, star_y - star_size), (star_x + 2, star_y - 2),
                    (star_x + star_size, star_y), (star_x + 2, star_y + 2),
                    (star_x, star_y + star_size), (star_x - 2, star_y + 2),
                    (star_x - star_size, star_y), (star_x - 2, star_y - 2)
                ])
                pygame.draw.circle(screen, WHITE, (star_x, star_y), 3)

        elif self.effect_type == 'fire_breath':
            # DRAGON'S FIRE BREATH - Massive cone of dragonfire
            direction = self.owner.direction
            
            # Orange/red heat flash
            if progress < 0.15:
                flash_alpha = int(100 * (1 - progress / 0.15))
                flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flash_surf.fill((255, 100, 0, flash_alpha))
                screen.blit(flash_surf, (0, 0))
            
            # Smoke cloud behind the flames
            for i in range(8):
                smoke_x = screen_x + direction * (120 + i * 20 + progress * 40)
                smoke_y = int(self.y) + random.randint(-30, 30) - int(progress * 20)
                smoke_size = int(20 + i * 5 + progress * 15)
                smoke_alpha = int(60 * (1 - progress * 0.5))
                smoke_surf = pygame.Surface((smoke_size * 2, smoke_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(smoke_surf, (80, 80, 80, smoke_alpha), (smoke_size, smoke_size), smoke_size)
                screen.blit(smoke_surf, (smoke_x - smoke_size, smoke_y - smoke_size))
            
            # Massive flame cone - multiple layers
            flame_length = int(180 * min(1, progress * 1.5))
            
            # Layer 1: Dark red base
            for i in range(25):
                t = i / 25
                cone_x = screen_x + direction * int(t * flame_length)
                spread = t * 60 * progress
                wave = math.sin(i * 0.5 + progress * 20) * (10 + t * 20)
                cone_y = int(self.y) + wave + (random.random() - 0.5) * spread * 2
                size = int(20 - t * 8 + random.random() * 8)
                pygame.draw.circle(screen, (150, 30, 0), (cone_x, cone_y), size)
            
            # Layer 2: Orange flames
            for i in range(25):
                t = i / 25
                cone_x = screen_x + direction * int(t * flame_length * 0.9)
                spread = t * 50 * progress
                wave = math.sin(i * 0.6 + progress * 22 + 1) * (8 + t * 15)
                cone_y = int(self.y) + wave + (random.random() - 0.5) * spread * 2
                size = int(16 - t * 6 + random.random() * 6)
                pygame.draw.circle(screen, (255, 100, 0), (cone_x, cone_y), size)
            
            # Layer 3: Yellow/white hot core
            for i in range(20):
                t = i / 20
                cone_x = screen_x + direction * int(t * flame_length * 0.75)
                spread = t * 30 * progress
                wave = math.sin(i * 0.7 + progress * 25 + 2) * (5 + t * 10)
                cone_y = int(self.y) + wave + (random.random() - 0.5) * spread
                size = int(12 - t * 5 + random.random() * 4)
                pygame.draw.circle(screen, (255, 200, 50), (cone_x, cone_y), size)
            
            # Layer 4: White-hot center line
            for i in range(15):
                t = i / 15
                cone_x = screen_x + direction * int(t * flame_length * 0.6)
                wave = math.sin(i * 0.8 + progress * 28) * 5
                cone_y = int(self.y) + wave
                size = int(8 - t * 4)
                pygame.draw.circle(screen, (255, 255, 200), (cone_x, cone_y), size)
                pygame.draw.circle(screen, WHITE, (cone_x, cone_y), max(2, size - 3))
            
            # Rising flames - upward burst to hit flying enemies
            for i in range(10):
                t = i / 10
                rise_x = screen_x + direction * int(30 + t * flame_length * 0.6)
                rise_y = int(self.y) - int(t * 80 * progress) - 20  # Rises upward
                wave_x = math.sin(i * 0.9 + progress * 15) * 15
                size = int(14 - t * 8 + random.random() * 5)
                # Gradient from orange at bottom to red at top
                r = 255
                g = int(150 - t * 100)
                b = int(50 - t * 50)
                pygame.draw.circle(screen, (r, max(0, g), max(0, b)), (rise_x + int(wave_x), rise_y), size)
            
            # Dragon mouth glow
            mouth_glow = int(25 + math.sin(progress * 20) * 10)
            for layer in range(4):
                glow_size = mouth_glow - layer * 5
                if glow_size > 0:
                    glow_color = [(255, 50, 0), (255, 150, 0), (255, 220, 100), WHITE][layer]
                    pygame.draw.circle(screen, glow_color, (screen_x + direction * 10, int(self.y)), glow_size)
            
            # Ember particles flying off
            for i in range(12):
                ember_x = screen_x + direction * (40 + random.random() * flame_length)
                ember_y = int(self.y) + random.randint(-50, 50) - int(progress * 30)
                ember_size = random.randint(2, 5)
                ember_color = random.choice([(255, 200, 0), (255, 150, 0), (255, 100, 0)])
                pygame.draw.circle(screen, ember_color, (int(ember_x), int(ember_y)), ember_size)
            
            # Heat shimmer lines
            for i in range(6):
                shimmer_x = screen_x + direction * (30 + i * 25)
                shimmer_y = int(self.y) - 40 - int(progress * 20)
                shimmer_len = 20 + random.randint(0, 15)
                pygame.draw.line(screen, (255, 200, 150), 
                               (shimmer_x, shimmer_y), (shimmer_x + random.randint(-5, 5), shimmer_y - shimmer_len), 2)
            


class Player:
    """Player class with Mario-style movement."""

    SPRITE_FRAME_WIDTH = 48
    SPRITE_FRAME_HEIGHT = 64
    SPRITE_FRAMES = {
        "idle": [0, 1],
        "run": [2, 3, 4, 5],
        "jump": [6],
        "attack": [7, 8],
        "special": [9],
    }
    SPRITE_CACHE = {}

    def __init__(self, player_num, character_name, start_x, start_y):
        self.player_num = player_num
        self.character = get_character(character_name)

        # Controls
        self.controls = PLAYER1_CONTROLS if player_num == 1 else PLAYER2_CONTROLS

        # Position (float for smooth movement)
        self.x = float(start_x)
        self.y = float(start_y)
        self.rect = pygame.Rect(int(self.x), int(self.y), PLAYER_WIDTH, PLAYER_HEIGHT)

        # Velocity
        self.vel_x = 0.0
        self.vel_y = 0.0

        # State
        self.on_ground = False
        self.facing_right = True
        self.direction = 1
        self.jumping = False       # True while jump button held AND rising
        self.jump_held = False     # Track if jump button is being held
        self.coyote_time = 0       # Grace period after leaving platform
        self.jump_buffer = 0       # Buffer jump input

        # Animation state
        self.anim_state = "idle"
        self.anim_timer = 0
        self.anim_index = 0
        self.jump_stretch = 0
        self.landing_squash = 0

        # Character-specific speed multiplier
        self.speed_mult = self.character.speed / 5.0

        # Flying (Dragon)
        self.fly_energy = 100
        self.max_fly_energy = 100
        self.is_flying = False

        # Combat
        self.health = self.character.health
        self.max_health = self.character.max_health
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.projectiles = []
        self.attack_rect = None

        # Special attack
        self.special_cooldown = 0
        self.special_effects = []

        # Invincibility
        self.invincible = False
        self.invincible_timer = 0
        self.flash = False
        self.flash_timer = 0

        # Unicorn healing
        self.heal_timer = 0

    def handle_input(self, keys):
        """Handle player input with Mario-style physics."""

        # --- HORIZONTAL MOVEMENT ---
        move_input = 0
        if keys[self.controls['left']]:
            move_input = -1
            self.facing_right = False
            self.direction = -1
        if keys[self.controls['right']]:
            move_input = 1
            self.facing_right = True
            self.direction = 1

        # Apply acceleration/deceleration
        accel = PLAYER_ACCELERATION if self.on_ground else PLAYER_AIR_ACCELERATION
        max_speed = PLAYER_MAX_SPEED * self.speed_mult

        if move_input != 0:
            # Accelerate in input direction
            self.vel_x += move_input * accel * self.speed_mult
            # Clamp to max speed
            if self.vel_x > max_speed:
                self.vel_x = max_speed
            elif self.vel_x < -max_speed:
                self.vel_x = -max_speed
        else:
            # Decelerate (friction)
            if self.on_ground:
                if self.vel_x > 0:
                    self.vel_x = max(0, self.vel_x - PLAYER_DECELERATION)
                elif self.vel_x < 0:
                    self.vel_x = min(0, self.vel_x + PLAYER_DECELERATION)

        # --- JUMPING ---
        jump_pressed = keys[self.controls['jump']]

        # Buffer jump input (allows pressing jump slightly before landing)
        if jump_pressed and not self.jump_held:
            self.jump_buffer = JUMP_BUFFER_MS

        # Can jump if: on ground OR within coyote time, AND (just pressed OR buffered)
        can_jump = (self.on_ground or self.coyote_time > 0) and self.jump_buffer > 0

        if can_jump and not self.jumping:
            self.vel_y = PLAYER_JUMP_VELOCITY
            self.jumping = True
            self.on_ground = False
            self.coyote_time = 0
            self.jump_buffer = 0
            self.jump_stretch = 120

        # Variable jump height - cut jump short if button released
        if self.jumping and not jump_pressed:
            if self.vel_y < PLAYER_JUMP_CUT:
                self.vel_y = PLAYER_JUMP_CUT
            self.jumping = False

        self.jump_held = jump_pressed

        # Dragon flying (reduced energy cost for better usability)
        if self.character.can_fly and jump_pressed and not self.on_ground and self.fly_energy > 0:
            if self.vel_y > -5:  # Only boost if not already rising fast
                self.vel_y = -8
                self.fly_energy -= 1.5  # Reduced from 2 - flight feels more useful
                self.is_flying = True

        # --- ATTACKS ---
        if keys[self.controls['attack']] and self.attack_cooldown <= 0:
            self.start_attack()

        if keys[self.controls['special']] and self.special_cooldown <= 0:
            self.use_special()

    def start_attack(self):
        """Regular attack."""
        self.attacking = True
        self.attack_timer = ATTACK_DURATION
        # Melee attacks have faster cooldown to compensate for range disadvantage
        if self.character.attack_type == 'melee':
            self.attack_cooldown = int(ATTACK_COOLDOWN * 0.6)  # 40% faster
        else:
            self.attack_cooldown = ATTACK_COOLDOWN
        self.attack_anim_timer = ATTACK_DURATION

        if self.character.attack_type == 'ranged':
            proj_x = self.rect.right if self.facing_right else self.rect.left - PROJECTILE_SIZE
            proj_y = self.rect.centery - PROJECTILE_SIZE // 2
            self.projectiles.append(
                Projectile(proj_x, proj_y, self.direction, self.character.damage, 
                          self.character.secondary_color, character_name=self.character.name)
            )
        else:
            # Melee attack - wider range to compensate for risk
            melee_range = 70  # Increased from 50
            melee_height = self.rect.height + 20  # Slightly taller hitbox
            if self.facing_right:
                self.attack_rect = pygame.Rect(self.rect.right - 10, self.rect.top - 10, melee_range, melee_height)
            else:
                self.attack_rect = pygame.Rect(self.rect.left - melee_range + 10, self.rect.top - 10, melee_range, melee_height)

    def use_special(self):
        """Character-specific special attack."""
        self.special_cooldown = SPECIAL_COOLDOWN
        name = self.character.name

        if name == 'Harry':
            # Lightning Bolt - projectile + lightning area damage
            proj_x = self.rect.right if self.facing_right else self.rect.left - 20
            proj_y = self.rect.centery - 10
            self.projectiles.append(
                Projectile(proj_x, proj_y, self.direction, 40, YELLOW, speed=18, size=20, character_name='Harry')
            )
            self.special_effects.append(
                SpecialEffect(self.rect.centerx, self.rect.centery, 'lightning', 500, YELLOW, self,
                            damage=25, damage_radius=60)
            )
        elif name == 'Ron':
            # Strong Punch - shockwave area damage
            self.special_effects.append(
                SpecialEffect(self.rect.centerx + (40 * self.direction), self.rect.bottom, 'shockwave', 400, ORANGE, self,
                            damage=35, damage_radius=150)
            )
        elif name == 'Hermione':
            # Spell Burst - 5 projectiles in spread pattern
            for angle in [-30, -15, 0, 15, 30]:
                rad = math.radians(angle)
                speed = 12
                vx = math.cos(rad) * speed * self.direction
                vy = math.sin(rad) * speed
                proj = Projectile(self.rect.centerx, self.rect.centery, self.direction, 18, PURPLE, 
                                 speed=speed, size=15, vel_x=vx, vel_y=vy, character_name='Hermione')
                self.projectiles.append(proj)
            self.special_effects.append(
                SpecialEffect(self.rect.centerx, self.rect.centery, 'spell_burst', 600, PURPLE, self,
                            damage=20, damage_radius=80)
            )
        elif name == 'Voldemort':
            # Dark Magic - powerful area damage
            self.special_effects.append(
                SpecialEffect(self.rect.centerx, self.rect.centery, 'dark_magic', 800, DARK_GREEN, self,
                            damage=50, damage_radius=120)
            )
        elif name == 'Hagrid':
            # Ground Slam - massive area damage
            self.special_effects.append(
                SpecialEffect(self.rect.centerx, self.rect.bottom, 'ground_slam', 600, BROWN, self,
                            damage=40, damage_radius=150)
            )
        elif name == 'Unicorn':
            # Rainbow Burst - heals self AND damages nearby enemies
            self.health = min(self.max_health, self.health + 35)
            self.special_effects.append(
                SpecialEffect(self.rect.centerx, self.rect.centery, 'heal_aura', 1000, WHITE, self,
                            damage=25, damage_radius=100)
            )
        elif name == 'Dragon':
            # Fire Breath - continuous fire damage
            self.special_effects.append(
                SpecialEffect(self.rect.centerx + (30 * self.direction), self.rect.centery, 'fire_breath', 1000, ORANGE, self,
                            damage=30, damage_radius=150)
            )

    def update(self, platforms, dt):
        """Update player physics."""

        # --- GRAVITY ---
        # Apply stronger gravity when falling for snappier feel
        gravity = PLAYER_GRAVITY_FALLING if self.vel_y > 0 else PLAYER_GRAVITY_NORMAL
        self.vel_y += gravity

        if self.vel_y > PLAYER_MAX_FALL_SPEED:
            self.vel_y = PLAYER_MAX_FALL_SPEED

        # Update coyote time and jump buffer
        if self.coyote_time > 0:
            self.coyote_time -= dt
        if self.jump_buffer > 0:
            self.jump_buffer -= dt

        # Regenerate fly energy on ground
        if self.on_ground and self.character.can_fly:
            self.fly_energy = min(self.max_fly_energy, self.fly_energy + 0.5)
            self.is_flying = False

        # --- APPLY MOVEMENT ---
        # Store if we were on ground before moving
        was_on_ground = self.on_ground

        # Move horizontally
        self.x += self.vel_x
        self.rect.x = int(self.x)
        self.check_horizontal_collisions(platforms)

        # Move vertically
        self.y += self.vel_y
        self.rect.y = int(self.y)
        self.check_vertical_collisions(platforms)

        # Start coyote time if we just left the ground (walked off edge)
        if was_on_ground and not self.on_ground and self.vel_y >= 0:
            self.coyote_time = COYOTE_TIME_MS
        if not was_on_ground and self.on_ground:
            self.landing_squash = 120

        # Stop jumping state when we start falling
        if self.vel_y > 0:
            self.jumping = False

        # --- BOUNDS ---
        if self.x < 0:
            self.x = 0
            self.vel_x = 0
        if self.x > LEVEL_WIDTH - PLAYER_WIDTH:
            self.x = LEVEL_WIDTH - PLAYER_WIDTH
            self.vel_x = 0
        self.rect.x = int(self.x)

        # Vertical bounds (safety net)
        if self.y < -20:
            self.y = -20
            self.vel_y = 0
        self.rect.y = int(self.y)

        # --- TIMERS ---
        if self.attacking:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attacking = False
                self.attack_rect = None

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.special_cooldown > 0:
            self.special_cooldown -= dt

        if self.jump_stretch > 0:
            self.jump_stretch = max(0, self.jump_stretch - dt)
        if self.landing_squash > 0:
            self.landing_squash = max(0, self.landing_squash - dt)

        self._update_animation(dt)

        # Update projectiles
        for proj in self.projectiles[:]:
            proj.update()
            if not proj.active:
                self.projectiles.remove(proj)

        # Update special effects
        for effect in self.special_effects[:]:
            effect.update(dt)
            if not effect.active:
                self.special_effects.remove(effect)

        # Invincibility flashing
        if self.invincible:
            self.invincible_timer -= dt
            self.flash_timer += dt
            self.flash = (self.flash_timer % 100) < 50
            if self.invincible_timer <= 0:
                self.invincible = False
                self.flash = False

        # Unicorn passive healing
        if self.character.heals and self.health < self.max_health:
            self.heal_timer += dt
            if self.heal_timer >= 2000:
                self.heal_timer = 0
                self.health = min(self.max_health, self.health + 3)

    def check_horizontal_collisions(self, platforms):
        """Check horizontal collisions."""
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                    self.x = float(self.rect.x)
                    self.vel_x = 0
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
                    self.x = float(self.rect.x)
                    self.vel_x = 0

    def check_vertical_collisions(self, platforms):
        """Check vertical collisions."""
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:  # Falling
                    self.rect.bottom = platform.rect.top
                    self.y = float(self.rect.y)
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  # Jumping up
                    self.rect.top = platform.rect.bottom
                    self.y = float(self.rect.y)
                    self.vel_y = 0

    def take_damage(self, amount):
        if not self.invincible:
            self.health -= amount
            self.invincible = True
            self.invincible_timer = INVINCIBILITY_TIME
            self.flash_timer = 0
            if self.health < 0:
                self.health = 0
            return True
        return False

    def is_alive(self):
        return self.health > 0

    def respawn(self, x, y):
        """Respawn the player at given position with partial health."""
        self.x = float(x)
        self.y = float(y)
        self.rect.x = int(x)
        self.rect.y = int(y)
        self.vel_x = 0
        self.vel_y = 0
        # Respawn with 50% health
        self.health = self.max_health // 2
        # Brief invincibility after respawn
        self.invincible = True
        self.invincible_timer = 3000  # 3 seconds of invincibility
        # Clear any ongoing attacks
        self.attacking = False
        self.attack_rect = None
        self.projectiles.clear()
        self.special_effects.clear()

    def _ensure_sprites(self):
        name = self.character.name.lower()
        if name in self.SPRITE_CACHE:
            return True
        sheet_path = os.path.join(os.path.dirname(__file__), "assets", "characters", f"{name}_sheet.png")
        if not os.path.exists(sheet_path):
            return False
        sheet = pygame.image.load(sheet_path).convert_alpha()
        frames = []
        total_frames = sum(len(v) for v in self.SPRITE_FRAMES.values())
        for i in range(total_frames):
            rect = pygame.Rect(i * self.SPRITE_FRAME_WIDTH, 0, self.SPRITE_FRAME_WIDTH, self.SPRITE_FRAME_HEIGHT)
            frame = sheet.subsurface(rect).copy()
            frame = pygame.transform.smoothscale(frame, (PLAYER_WIDTH, PLAYER_HEIGHT))
            frames.append(frame)
        self.SPRITE_CACHE[name] = frames
        return True

    def _update_animation(self, dt):
        # Priority: special > attack > jump > run > idle
        if self.special_cooldown > SPECIAL_COOLDOWN - 300:
            state = "special"
        elif self.attacking:
            state = "attack"
        elif not self.on_ground:
            state = "jump"
        elif abs(self.vel_x) > 0.2:
            state = "run"
        else:
            state = "idle"

        if state != self.anim_state:
            self.anim_state = state
            self.anim_timer = 0
            self.anim_index = 0

        if state == "run":
            frame_time = 90
        elif state == "idle":
            frame_time = 350
        elif state == "attack":
            frame_time = 100
        elif state == "special":
            frame_time = 150
        else:
            return

        self.anim_timer += dt
        if self.anim_timer >= frame_time:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % len(self.SPRITE_FRAMES[state])

    def _get_current_frame(self):
        name = self.character.name.lower()
        frames = self.SPRITE_CACHE.get(name, [])
        if not frames:
            return None

        if self.anim_state == "jump":
            frame_index = self.SPRITE_FRAMES["jump"][0]
        else:
            frame_list = self.SPRITE_FRAMES[self.anim_state]
            frame_index = frame_list[self.anim_index % len(frame_list)]
        return frames[frame_index]

    def _draw_melee_effect(self, screen, camera_x):
        """Draw character-specific melee attack effects."""
        attack_screen_x = self.attack_rect.x - camera_x
        attack_w = self.attack_rect.width
        attack_h = self.attack_rect.height
        attack_progress = 1 - (self.attack_timer / ATTACK_DURATION) if ATTACK_DURATION > 0 else 1
        
        attack_surface = pygame.Surface((attack_w + 40, attack_h + 40), pygame.SRCALPHA)
        center_x = 20 if self.facing_right else attack_w + 20
        center_y = attack_h // 2 + 20
        
        name = self.character.name
        
        if name == 'Ron':
            # Ron - powerful orange fist punch with shockwave
            punch_extend = int(attack_progress * 40)
            fist_x = center_x + (punch_extend if self.facing_right else -punch_extend)
            
            # Shockwave rings
            for i in range(3):
                ring_progress = max(0, attack_progress - i * 0.15)
                if ring_progress > 0:
                    ring_r = int(ring_progress * 50)
                    ring_alpha = int(180 * (1 - ring_progress))
                    pygame.draw.circle(attack_surface, (255, 150, 50, ring_alpha), (fist_x, center_y), ring_r, 3)
            
            # Fist glow
            pygame.draw.circle(attack_surface, (255, 200, 100, 150), (fist_x, center_y), 25)
            pygame.draw.circle(attack_surface, (255, 150, 50, 200), (fist_x, center_y), 18)
            pygame.draw.circle(attack_surface, (255, 220, 150), (fist_x, center_y), 10)
            
            # Impact lines
            for i in range(6):
                angle = (i / 6) * math.pi * 2 + attack_progress * 3
                line_len = 15 + attack_progress * 20
                ex = fist_x + int(math.cos(angle) * line_len)
                ey = center_y + int(math.sin(angle) * line_len)
                pygame.draw.line(attack_surface, (255, 200, 100, int(200 * (1 - attack_progress))), 
                               (fist_x, center_y), (ex, ey), 3)
        
        elif name == 'Hagrid':
            # Hagrid - massive ground-shaking slam
            slam_y = center_y + int(attack_progress * 20)
            
            # Dust clouds
            for i in range(5):
                dust_x = center_x + (i - 2) * 25 * (1 if self.facing_right else -1)
                dust_y = slam_y + 20
                dust_size = int(15 + attack_progress * 20)
                dust_alpha = int(150 * (1 - attack_progress * 0.7))
                pygame.draw.circle(attack_surface, (139, 90, 43, dust_alpha), (dust_x, dust_y), dust_size)
            
            # Ground crack lines
            for i in range(4):
                crack_x = center_x + (i - 1.5) * 30 * (1 if self.facing_right else -1)
                crack_len = int(20 + attack_progress * 30)
                pygame.draw.line(attack_surface, (100, 60, 20, 200), 
                               (crack_x, slam_y + 15), (crack_x + random.randint(-10, 10), slam_y + 15 + crack_len), 3)
            
            # Big fist impact
            pygame.draw.circle(attack_surface, (139, 90, 43, 180), (center_x, slam_y), 30)
            pygame.draw.circle(attack_surface, (180, 120, 60), (center_x, slam_y), 20)
        
        elif name == 'Unicorn':
            # Unicorn - magical rainbow horn strike
            horn_extend = int(attack_progress * 50)
            horn_x = center_x + (horn_extend if self.facing_right else -horn_extend)
            
            # Rainbow trail
            colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (238, 130, 238)]
            for i, color in enumerate(colors):
                trail_offset = i * 3
                trail_x = center_x + ((horn_extend - trail_offset * 3) if self.facing_right else -(horn_extend - trail_offset * 3))
                pygame.draw.circle(attack_surface, (*color, int(200 - i * 25)), (trail_x, center_y + i - 3), 6 - i)
            
            # Sparkles around horn
            for i in range(8):
                angle = attack_progress * 10 + i * 0.8
                dist = 15 + int(math.sin(angle * 3) * 8)
                spark_x = horn_x + int(math.cos(angle) * dist)
                spark_y = center_y + int(math.sin(angle) * dist)
                pygame.draw.circle(attack_surface, WHITE, (spark_x, spark_y), 3)
            
            # Horn tip glow
            pygame.draw.circle(attack_surface, (255, 255, 255, 200), (horn_x, center_y), 12)
            pygame.draw.circle(attack_surface, (255, 200, 255), (horn_x, center_y), 7)
        
        elif name == 'Dragon':
            # Dragon - claw swipe with fire
            # Claw marks
            for i in range(4):
                claw_start_x = center_x - 10
                claw_start_y = center_y - 30 + i * 18
                claw_len = int(40 + attack_progress * 30)
                claw_end_x = claw_start_x + (claw_len if self.facing_right else -claw_len)
                claw_end_y = claw_start_y + int(attack_progress * 10)
                
                # Fire trail
                pygame.draw.line(attack_surface, (255, 100, 0, 150), 
                               (claw_start_x, claw_start_y), (claw_end_x, claw_end_y), 6)
                pygame.draw.line(attack_surface, (255, 200, 0, 200), 
                               (claw_start_x, claw_start_y), (claw_end_x, claw_end_y), 3)
            
            # Flame particles
            for _ in range(5):
                flame_x = center_x + random.randint(0, 40) * (1 if self.facing_right else -1)
                flame_y = center_y + random.randint(-25, 25)
                pygame.draw.circle(attack_surface, (255, random.randint(100, 200), 0, 180), 
                                 (flame_x, flame_y), random.randint(4, 10))
        
        else:
            # Default slash arc for other melee characters
            arc_color = (*self.character.secondary_color, int(180 * (1 - attack_progress * 0.5)))
            
            for i in range(3):
                arc_offset = i * 8 * attack_progress
                arc_alpha = max(0, int(180 - i * 50 - attack_progress * 100))
                arc_col = (*self.character.secondary_color, arc_alpha)
                start_angle = math.radians(-60 + attack_progress * 40) if self.facing_right else math.radians(120 - attack_progress * 40)
                end_angle = math.radians(60 + attack_progress * 40) if self.facing_right else math.radians(240 + attack_progress * 40)
                
                rect = pygame.Rect(center_x - 30 - arc_offset, 20 - arc_offset, 60 + arc_offset * 2, attack_h + arc_offset * 2)
                pygame.draw.arc(attack_surface, arc_col, rect, start_angle, end_angle, max(1, 6 - i * 2))
        
        screen.blit(attack_surface, (attack_screen_x - 20, self.attack_rect.y - 20))

    def _draw_fallback(self, screen, x, y, w, h):
        name = self.character.name
        if name == 'Harry':
            self._draw_harry(screen, x, y, w, h)
        elif name == 'Ron':
            self._draw_ron(screen, x, y, w, h)
        elif name == 'Hermione':
            self._draw_hermione(screen, x, y, w, h)
        elif name == 'Voldemort':
            self._draw_voldemort(screen, x, y, w, h)
        elif name == 'Hagrid':
            self._draw_hagrid(screen, x, y, w, h)
        elif name == 'Unicorn':
            self._draw_unicorn(screen, x, y, w, h)
        elif name == 'Dragon':
            self._draw_dragon(screen, x, y, w, h)

    def draw(self, screen, camera_x):
        """Draw player."""
        if self.flash:
            return

        screen_x = int(self.x - camera_x)
        screen_y = int(self.y)

        # Don't draw if off screen
        if screen_x < -PLAYER_WIDTH or screen_x > SCREEN_WIDTH + PLAYER_WIDTH:
            return

        w, h = PLAYER_WIDTH, PLAYER_HEIGHT
        if self._ensure_sprites():
            frame = self._get_current_frame()
            if frame:
                sprite = frame
                if not self.facing_right:
                    sprite = pygame.transform.flip(sprite, True, False)

                scale_x, scale_y = 1.0, 1.0
                if self.jump_stretch > 0:
                    scale_x, scale_y = 0.95, 1.08
                elif self.landing_squash > 0:
                    scale_x, scale_y = 1.05, 0.92

                if scale_x != 1.0 or scale_y != 1.0:
                    new_w = max(1, int(w * scale_x))
                    new_h = max(1, int(h * scale_y))
                    sprite = pygame.transform.smoothscale(sprite, (new_w, new_h))
                    draw_x = screen_x + (w - new_w) // 2
                    draw_y = screen_y + (h - new_h)
                else:
                    draw_x = screen_x
                    draw_y = screen_y

                screen.blit(sprite, (draw_x, draw_y))
            else:
                self._draw_fallback(screen, screen_x, screen_y, w, h)
        else:
            self._draw_fallback(screen, screen_x, screen_y, w, h)

        # Melee attack effect - character-specific
        if self.attacking and self.attack_rect:
            self._draw_melee_effect(screen, camera_x)

        # Projectiles
        for proj in self.projectiles:
            proj.draw(screen, camera_x)

        # Special effects
        for effect in self.special_effects:
            effect.draw(screen, camera_x)

        # Dragon fly energy bar
        if self.character.can_fly:
            pygame.draw.rect(screen, GRAY, (screen_x, screen_y - 8, w, 4))
            energy_width = int(w * (self.fly_energy / self.max_fly_energy))
            pygame.draw.rect(screen, LIGHT_BLUE, (screen_x, screen_y - 8, energy_width, 4))

        # Special cooldown indicator
        if self.special_cooldown > 0:
            cooldown_pct = self.special_cooldown / SPECIAL_COOLDOWN
            pygame.draw.rect(screen, DARK_GRAY, (screen_x, screen_y - 14, w, 4))
            pygame.draw.rect(screen, GOLD, (screen_x, screen_y - 14, int(w * (1 - cooldown_pct)), 4))

    # Character drawing methods - CHIBI STYLE with big heads, expressive faces
    # Proportions: Head = 40% of height, Body = 60%
    # Bold black outlines, large eyes, dynamic poses

    def _draw_chibi_base(self, screen, x, y, w, h, skin_color, outline_color=(30, 30, 35)):
        """Helper to draw basic chibi face shape."""
        # Chibi head is big - takes up about 40% of height
        head_h = int(h * 0.45)
        head_w = int(w * 0.9)
        head_x = x + (w - head_w) // 2
        head_y = y

        # Draw head with cel-shading
        pygame.draw.ellipse(screen, skin_color, (head_x, head_y, head_w, head_h))
        # Shading on left side
        shade_color = tuple(max(0, c - 25) for c in skin_color)
        pygame.draw.ellipse(screen, shade_color, (head_x, head_y + head_h // 4, head_w // 3, head_h // 2))
        # Bold outline
        pygame.draw.ellipse(screen, outline_color, (head_x, head_y, head_w, head_h), 3)

        return head_x, head_y, head_w, head_h

    def _draw_harry(self, screen, x, y, w, h):
        """Draw Harry Potter - chibi style with glasses, scar, Gryffindor robes."""
        t = pygame.time.get_ticks()
        dir = self.direction
        moving = abs(self.vel_x) > 0.5
        jumping = not self.on_ground

        # Animation variables
        run_cycle = math.sin(t / 80) if moving else 0
        bounce = abs(math.sin(t / 100)) * 2 if moving else 0

        # Dynamic pose - lean forward when running
        lean = 3 if moving else 0
        body_offset_x = lean * dir

        # Shadow
        shadow_w = w - 8 if not jumping else w - 16
        shadow_surf = pygame.Surface((shadow_w, 8), pygame.SRCALPHA)
        shadow_alpha = 80 if not jumping else 40
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, shadow_alpha), (0, 0, shadow_w, 8))
        screen.blit(shadow_surf, (x + (w - shadow_w) // 2, y + h - 4))

        OUTLINE = (25, 25, 30)
        skin = (255, 220, 195)

        # === LEGS (small, simple) ===
        leg_y = y + int(h * 0.68)
        leg_h = int(h * 0.28)
        leg_spread = 8 if moving else 4

        # Running animation - alternate legs
        left_leg_y = leg_y + int(run_cycle * 6)
        right_leg_y = leg_y - int(run_cycle * 6)

        # Left leg
        pygame.draw.ellipse(screen, (50, 50, 60), (x + w//2 - leg_spread - 6, left_leg_y, 10, leg_h))
        pygame.draw.ellipse(screen, OUTLINE, (x + w//2 - leg_spread - 6, left_leg_y, 10, leg_h), 2)
        # Shoe
        pygame.draw.ellipse(screen, (30, 30, 35), (x + w//2 - leg_spread - 8, left_leg_y + leg_h - 6, 12, 8))

        # Right leg
        pygame.draw.ellipse(screen, (50, 50, 60), (x + w//2 + leg_spread - 4, right_leg_y, 10, leg_h))
        pygame.draw.ellipse(screen, OUTLINE, (x + w//2 + leg_spread - 4, right_leg_y, 10, leg_h), 2)
        # Shoe
        pygame.draw.ellipse(screen, (30, 30, 35), (x + w//2 + leg_spread - 6, right_leg_y + leg_h - 6, 12, 8))

        # === BODY (small torso with Gryffindor robe) ===
        body_y = y + int(h * 0.38)
        body_h = int(h * 0.35)
        body_w = int(w * 0.7)
        body_x = x + (w - body_w) // 2 + body_offset_x

        # Black robe base
        pygame.draw.ellipse(screen, (35, 35, 40), (body_x - 2, body_y, body_w + 4, body_h))
        # Gray sweater showing
        pygame.draw.ellipse(screen, (110, 110, 120), (body_x + 4, body_y + 4, body_w - 8, body_h - 12))
        # Gryffindor tie
        pygame.draw.polygon(screen, (170, 40, 50), [
            (body_x + body_w//2 - 3, body_y + 2),
            (body_x + body_w//2 + 3, body_y + 2),
            (body_x + body_w//2 + 2, body_y + 18),
            (body_x + body_w//2 - 2, body_y + 18)
        ])
        pygame.draw.line(screen, (220, 180, 60), (body_x + body_w//2, body_y + 4), (body_x + body_w//2, body_y + 16), 2)
        # Body outline
        pygame.draw.ellipse(screen, OUTLINE, (body_x - 2, body_y, body_w + 4, body_h), 3)

        # === ARMS ===
        arm_swing = run_cycle * 8 if moving else 0

        # Back arm (simple)
        back_arm_x = body_x - 4 if dir > 0 else body_x + body_w - 2
        pygame.draw.ellipse(screen, (35, 35, 40), (back_arm_x, body_y + 4 - arm_swing, 10, 18))
        pygame.draw.ellipse(screen, skin, (back_arm_x + 1, body_y + 18 - arm_swing, 8, 8))
        pygame.draw.ellipse(screen, OUTLINE, (back_arm_x, body_y + 4 - arm_swing, 10, 18), 2)

        # Front arm with wand
        front_arm_x = body_x + body_w - 6 if dir > 0 else body_x
        wand_angle = -20 if self.attacking else 10
        pygame.draw.ellipse(screen, (35, 35, 40), (front_arm_x, body_y + 2 + arm_swing, 10, 20))
        pygame.draw.ellipse(screen, skin, (front_arm_x + 1, body_y + 18 + arm_swing, 8, 8))
        pygame.draw.ellipse(screen, OUTLINE, (front_arm_x, body_y + 2 + arm_swing, 10, 20), 2)

        # Wand
        wand_x = front_arm_x + (12 if dir > 0 else -2)
        wand_end_x = wand_x + 18 * dir
        pygame.draw.line(screen, (100, 70, 45), (wand_x, body_y + 20 + arm_swing), (wand_end_x, body_y + 12 + arm_swing), 4)
        pygame.draw.line(screen, (130, 95, 60), (wand_x, body_y + 19 + arm_swing), (wand_end_x, body_y + 11 + arm_swing), 2)

        # Wand glow when attacking
        if self.attacking:
            glow = pygame.Surface((28, 28), pygame.SRCALPHA)
            glow_pulse = int(abs(math.sin(t * 0.02)) * 60)
            pygame.draw.circle(glow, (255, 220, 100, 120 + glow_pulse), (14, 14), 12)
            pygame.draw.circle(glow, (255, 255, 200, 180), (14, 14), 6)
            screen.blit(glow, (wand_end_x - 14, body_y + 2 + arm_swing))

        # === BIG CHIBI HEAD ===
        head_h = int(h * 0.44)
        head_w = int(w * 0.92)
        head_x = x + (w - head_w) // 2 + body_offset_x
        head_y = y - int(bounce)

        # Head base
        pygame.draw.ellipse(screen, skin, (head_x, head_y, head_w, head_h))
        # Cel-shading
        pygame.draw.ellipse(screen, (240, 200, 175), (head_x + 2, head_y + head_h//3, head_w//3, head_h//2))
        # Bold outline
        pygame.draw.ellipse(screen, OUTLINE, (head_x, head_y, head_w, head_h), 3)

        # Messy black hair - spiky
        hair = (25, 25, 30)
        hair_light = (45, 45, 55)
        # Main hair mass
        pygame.draw.ellipse(screen, hair, (head_x - 2, head_y - 6, head_w + 4, head_h // 2 + 8))
        # Spiky bits
        spikes = [
            [(head_x + 4, head_y + 8), (head_x - 4, head_y - 8), (head_x + 14, head_y + 2)],
            [(head_x + head_w - 4, head_y + 8), (head_x + head_w + 4, head_y - 8), (head_x + head_w - 14, head_y + 2)],
            [(head_x + head_w//2 - 6, head_y + 2), (head_x + head_w//2 - 2, head_y - 12), (head_x + head_w//2 + 4, head_y + 2)],
            [(head_x + head_w//2 + 2, head_y + 4), (head_x + head_w//2 + 8, head_y - 8), (head_x + head_w//2 + 14, head_y + 6)],
        ]
        for spike in spikes:
            pygame.draw.polygon(screen, hair, spike)
        # Hair highlight
        pygame.draw.arc(screen, hair_light, (head_x + 8, head_y - 2, head_w - 16, 14), 0.3, 2.8, 3)
        # Hair outline
        pygame.draw.ellipse(screen, OUTLINE, (head_x - 2, head_y - 6, head_w + 4, head_h // 2 + 8), 2)

        # === BIG EXPRESSIVE EYES ===
        eye_offset_x = 3 * dir
        eye_y = head_y + head_h // 2 - 4

        # Glasses frames first
        glass_color = (50, 50, 55)
        pygame.draw.circle(screen, glass_color, (head_x + head_w//2 - 10 + eye_offset_x, eye_y + 2), 11, 3)
        pygame.draw.circle(screen, glass_color, (head_x + head_w//2 + 10 + eye_offset_x, eye_y + 2), 11, 3)
        pygame.draw.line(screen, glass_color, (head_x + head_w//2 - 1 + eye_offset_x, eye_y + 2),
                        (head_x + head_w//2 + 1 + eye_offset_x, eye_y + 2), 3)
        # Earpieces
        pygame.draw.line(screen, glass_color, (head_x + head_w//2 - 20 + eye_offset_x, eye_y),
                        (head_x + 4, eye_y - 4), 2)
        pygame.draw.line(screen, glass_color, (head_x + head_w//2 + 20 + eye_offset_x, eye_y),
                        (head_x + head_w - 4, eye_y - 4), 2)

        # Big white eyes
        pygame.draw.ellipse(screen, WHITE, (head_x + head_w//2 - 17 + eye_offset_x, eye_y - 5, 14, 16))
        pygame.draw.ellipse(screen, WHITE, (head_x + head_w//2 + 3 + eye_offset_x, eye_y - 5, 14, 16))

        # Green irises (Harry's famous green eyes)
        iris_offset = dir * 2
        pygame.draw.ellipse(screen, (50, 160, 80), (head_x + head_w//2 - 13 + eye_offset_x + iris_offset, eye_y, 9, 10))
        pygame.draw.ellipse(screen, (50, 160, 80), (head_x + head_w//2 + 6 + eye_offset_x + iris_offset, eye_y, 9, 10))

        # Pupils
        pygame.draw.ellipse(screen, (20, 60, 30), (head_x + head_w//2 - 11 + eye_offset_x + iris_offset, eye_y + 2, 5, 6))
        pygame.draw.ellipse(screen, (20, 60, 30), (head_x + head_w//2 + 8 + eye_offset_x + iris_offset, eye_y + 2, 5, 6))

        # Eye shine (important for expressive look!)
        pygame.draw.circle(screen, WHITE, (head_x + head_w//2 - 13 + eye_offset_x + iris_offset, eye_y + 1), 3)
        pygame.draw.circle(screen, WHITE, (head_x + head_w//2 + 4 + eye_offset_x + iris_offset, eye_y + 1), 3)
        pygame.draw.circle(screen, (200, 255, 220), (head_x + head_w//2 - 9 + eye_offset_x + iris_offset, eye_y + 5), 2)
        pygame.draw.circle(screen, (200, 255, 220), (head_x + head_w//2 + 8 + eye_offset_x + iris_offset, eye_y + 5), 2)

        # Eye outlines
        pygame.draw.ellipse(screen, OUTLINE, (head_x + head_w//2 - 17 + eye_offset_x, eye_y - 5, 14, 16), 2)
        pygame.draw.ellipse(screen, OUTLINE, (head_x + head_w//2 + 3 + eye_offset_x, eye_y - 5, 14, 16), 2)

        # Eyebrows - expressive
        brow_y = eye_y - 8
        if self.attacking:
            # Determined look
            pygame.draw.line(screen, OUTLINE, (head_x + head_w//2 - 16, brow_y + 2), (head_x + head_w//2 - 4, brow_y - 1), 3)
            pygame.draw.line(screen, OUTLINE, (head_x + head_w//2 + 4, brow_y - 1), (head_x + head_w//2 + 16, brow_y + 2), 3)
        else:
            pygame.draw.arc(screen, OUTLINE, (head_x + head_w//2 - 18, brow_y - 2, 14, 8), 0.5, 2.6, 3)
            pygame.draw.arc(screen, OUTLINE, (head_x + head_w//2 + 4, brow_y - 2, 14, 8), 0.5, 2.6, 3)

        # Mouth
        mouth_y = head_y + head_h - 12
        if self.attacking:
            # Battle cry
            pygame.draw.ellipse(screen, (180, 80, 80), (head_x + head_w//2 - 6, mouth_y - 2, 12, 8))
            pygame.draw.ellipse(screen, OUTLINE, (head_x + head_w//2 - 6, mouth_y - 2, 12, 8), 2)
        elif moving:
            # Determined smile
            pygame.draw.arc(screen, (200, 120, 120), (head_x + head_w//2 - 6, mouth_y, 12, 6), 3.14, 6.28, 2)
        else:
            # Slight smile
            pygame.draw.arc(screen, (200, 120, 120), (head_x + head_w//2 - 4, mouth_y, 8, 4), 3.14, 6.28, 2)

        # LIGHTNING SCAR - iconic!
        scar_x = head_x + head_w//2 + 2
        scar_y = head_y + 8
        scar_pts = [(scar_x, scar_y), (scar_x + 3, scar_y + 4), (scar_x, scar_y + 8), (scar_x + 3, scar_y + 12)]
        pygame.draw.lines(screen, (200, 50, 50), False, scar_pts, 3)
        pygame.draw.lines(screen, (255, 150, 100), False, scar_pts, 2)

        # Blush marks (cute chibi detail)
        blush = pygame.Surface((10, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(blush, (255, 180, 180, 100), (0, 0, 10, 6))
        screen.blit(blush, (head_x + 6, eye_y + 10))
        screen.blit(blush, (head_x + head_w - 16, eye_y + 10))

    def _draw_ron(self, screen, x, y, w, h):
        """Draw Ron Weasley - chibi style with orange hair, freckles, Weasley sweater."""
        t = pygame.time.get_ticks()
        dir = self.direction
        moving = abs(self.vel_x) > 0.5
        jumping = not self.on_ground

        run_cycle = math.sin(t / 80) if moving else 0
        bounce = abs(math.sin(t / 100)) * 2 if moving else 0
        lean = 3 if moving else 0
        body_offset_x = lean * dir

        # Shadow
        shadow_w = w - 8 if not jumping else w - 16
        shadow_surf = pygame.Surface((shadow_w, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80 if not jumping else 40), (0, 0, shadow_w, 8))
        screen.blit(shadow_surf, (x + (w - shadow_w) // 2, y + h - 4))

        OUTLINE = (25, 25, 30)
        skin = (255, 225, 200)

        # === LEGS ===
        leg_y = y + int(h * 0.68)
        leg_h = int(h * 0.28)
        leg_spread = 8 if moving else 4
        left_leg_y = leg_y + int(run_cycle * 6)
        right_leg_y = leg_y - int(run_cycle * 6)

        pygame.draw.ellipse(screen, (50, 50, 60), (x + w//2 - leg_spread - 6, left_leg_y, 10, leg_h))
        pygame.draw.ellipse(screen, OUTLINE, (x + w//2 - leg_spread - 6, left_leg_y, 10, leg_h), 2)
        pygame.draw.ellipse(screen, (30, 30, 35), (x + w//2 - leg_spread - 8, left_leg_y + leg_h - 6, 12, 8))

        pygame.draw.ellipse(screen, (50, 50, 60), (x + w//2 + leg_spread - 4, right_leg_y, 10, leg_h))
        pygame.draw.ellipse(screen, OUTLINE, (x + w//2 + leg_spread - 4, right_leg_y, 10, leg_h), 2)
        pygame.draw.ellipse(screen, (30, 30, 35), (x + w//2 + leg_spread - 6, right_leg_y + leg_h - 6, 12, 8))

        # === BODY - Weasley sweater ===
        body_y = y + int(h * 0.38)
        body_h = int(h * 0.35)
        body_w = int(w * 0.7)
        body_x = x + (w - body_w) // 2 + body_offset_x

        # Maroon Weasley sweater
        sweater_color = (160, 50, 40)
        sweater_dark = (120, 35, 28)
        sweater_light = (190, 70, 55)

        pygame.draw.ellipse(screen, sweater_color, (body_x, body_y, body_w, body_h))
        pygame.draw.ellipse(screen, sweater_dark, (body_x, body_y + 4, body_w // 3, body_h - 8))
        pygame.draw.arc(screen, sweater_light, (body_x + body_w - 14, body_y + 6, 12, body_h - 12), -1.5, 1.5, 3)

        # "R" on sweater
        font = pygame.font.Font(None, 18)
        r_surf = font.render("R", True, (255, 210, 100))
        screen.blit(r_surf, (body_x + body_w//2 - 5, body_y + body_h//2 - 6))

        pygame.draw.ellipse(screen, OUTLINE, (body_x, body_y, body_w, body_h), 3)

        # === ARMS ===
        arm_swing = run_cycle * 8 if moving else 0

        back_arm_x = body_x - 4 if dir > 0 else body_x + body_w - 2
        pygame.draw.ellipse(screen, sweater_color, (back_arm_x, body_y + 4 - arm_swing, 10, 18))
        pygame.draw.ellipse(screen, skin, (back_arm_x + 1, body_y + 18 - arm_swing, 8, 8))
        pygame.draw.ellipse(screen, OUTLINE, (back_arm_x, body_y + 4 - arm_swing, 10, 18), 2)

        front_arm_x = body_x + body_w - 6 if dir > 0 else body_x
        pygame.draw.ellipse(screen, sweater_color, (front_arm_x, body_y + 2 + arm_swing, 10, 20))
        pygame.draw.ellipse(screen, skin, (front_arm_x + 1, body_y + 18 + arm_swing, 8, 8))
        pygame.draw.ellipse(screen, OUTLINE, (front_arm_x, body_y + 2 + arm_swing, 10, 20), 2)

        # Wand
        wand_x = front_arm_x + (12 if dir > 0 else -2)
        wand_end_x = wand_x + 16 * dir
        pygame.draw.line(screen, (90, 65, 40), (wand_x, body_y + 20 + arm_swing), (wand_end_x, body_y + 14 + arm_swing), 4)
        pygame.draw.line(screen, (120, 90, 55), (wand_x, body_y + 19 + arm_swing), (wand_end_x, body_y + 13 + arm_swing), 2)

        if self.attacking:
            glow = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 200, 100, 140), (12, 12), 10)
            pygame.draw.circle(glow, (255, 240, 180, 180), (12, 12), 5)
            screen.blit(glow, (wand_end_x - 12, body_y + 4 + arm_swing))

        # === BIG CHIBI HEAD ===
        head_h = int(h * 0.44)
        head_w = int(w * 0.92)
        head_x = x + (w - head_w) // 2 + body_offset_x
        head_y = y - int(bounce)

        pygame.draw.ellipse(screen, skin, (head_x, head_y, head_w, head_h))
        pygame.draw.ellipse(screen, (240, 205, 180), (head_x + 2, head_y + head_h//3, head_w//3, head_h//2))
        pygame.draw.ellipse(screen, OUTLINE, (head_x, head_y, head_w, head_h), 3)

        # Bright orange Weasley hair - messy and wild
        hair = (230, 110, 35)
        hair_dark = (200, 85, 25)
        hair_light = (255, 140, 50)

        pygame.draw.ellipse(screen, hair, (head_x - 4, head_y - 8, head_w + 8, head_h // 2 + 12))
        # Messy tufts
        tufts = [
            [(head_x + 2, head_y + 6), (head_x - 8, head_y - 6), (head_x + 12, head_y)],
            [(head_x + head_w - 2, head_y + 6), (head_x + head_w + 8, head_y - 6), (head_x + head_w - 12, head_y)],
            [(head_x + head_w//2 - 8, head_y), (head_x + head_w//2 - 4, head_y - 14), (head_x + head_w//2 + 2, head_y)],
            [(head_x + head_w//2 + 4, head_y + 2), (head_x + head_w//2 + 10, head_y - 10), (head_x + head_w//2 + 16, head_y + 4)],
            [(head_x + 10, head_y + 4), (head_x + 6, head_y - 8), (head_x + 18, head_y + 2)],
        ]
        for tuft in tufts:
            pygame.draw.polygon(screen, hair, tuft)
        pygame.draw.arc(screen, hair_light, (head_x + 6, head_y - 4, head_w - 12, 12), 0.3, 2.8, 3)
        pygame.draw.ellipse(screen, OUTLINE, (head_x - 4, head_y - 8, head_w + 8, head_h // 2 + 12), 2)

        # === BIG EYES - wide and expressive ===
        eye_offset_x = 3 * dir
        eye_y = head_y + head_h // 2 - 4

        pygame.draw.ellipse(screen, WHITE, (head_x + head_w//2 - 17 + eye_offset_x, eye_y - 5, 14, 16))
        pygame.draw.ellipse(screen, WHITE, (head_x + head_w//2 + 3 + eye_offset_x, eye_y - 5, 14, 16))

        # Blue irises
        iris_offset = dir * 2
        pygame.draw.ellipse(screen, (100, 160, 220), (head_x + head_w//2 - 13 + eye_offset_x + iris_offset, eye_y, 9, 10))
        pygame.draw.ellipse(screen, (100, 160, 220), (head_x + head_w//2 + 6 + eye_offset_x + iris_offset, eye_y, 9, 10))
        pygame.draw.ellipse(screen, (50, 100, 160), (head_x + head_w//2 - 11 + eye_offset_x + iris_offset, eye_y + 2, 5, 6))
        pygame.draw.ellipse(screen, (50, 100, 160), (head_x + head_w//2 + 8 + eye_offset_x + iris_offset, eye_y + 2, 5, 6))

        # Eye shine
        pygame.draw.circle(screen, WHITE, (head_x + head_w//2 - 13 + eye_offset_x + iris_offset, eye_y + 1), 3)
        pygame.draw.circle(screen, WHITE, (head_x + head_w//2 + 4 + eye_offset_x + iris_offset, eye_y + 1), 3)

        pygame.draw.ellipse(screen, OUTLINE, (head_x + head_w//2 - 17 + eye_offset_x, eye_y - 5, 14, 16), 2)
        pygame.draw.ellipse(screen, OUTLINE, (head_x + head_w//2 + 3 + eye_offset_x, eye_y - 5, 14, 16), 2)

        # Eyebrows - often worried/surprised
        pygame.draw.arc(screen, OUTLINE, (head_x + head_w//2 - 18, eye_y - 12, 14, 10), 0.3, 2.8, 3)
        pygame.draw.arc(screen, OUTLINE, (head_x + head_w//2 + 4, eye_y - 12, 14, 10), 0.3, 2.8, 3)

        # FRECKLES - Ron's signature look
        freckle_color = (210, 140, 100)
        freckle_positions = [
            (head_x + 8, eye_y + 8), (head_x + 12, eye_y + 12), (head_x + 6, eye_y + 14),
            (head_x + head_w - 8, eye_y + 8), (head_x + head_w - 12, eye_y + 12), (head_x + head_w - 6, eye_y + 14),
        ]
        for fx, fy in freckle_positions:
            pygame.draw.circle(screen, freckle_color, (fx, fy), 2)

        # Mouth
        mouth_y = head_y + head_h - 12
        if self.attacking:
            pygame.draw.ellipse(screen, (180, 80, 80), (head_x + head_w//2 - 5, mouth_y - 2, 10, 8))
            pygame.draw.ellipse(screen, OUTLINE, (head_x + head_w//2 - 5, mouth_y - 2, 10, 8), 2)
        elif moving:
            pygame.draw.arc(screen, (200, 120, 120), (head_x + head_w//2 - 5, mouth_y, 10, 5), 3.14, 6.28, 2)
        else:
            # Slightly nervous/unsure expression
            pygame.draw.arc(screen, (200, 120, 120), (head_x + head_w//2 - 4, mouth_y + 1, 8, 4), 0, 3.14, 2)

        # Blush
        blush = pygame.Surface((10, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(blush, (255, 180, 180, 100), (0, 0, 10, 6))
        screen.blit(blush, (head_x + 6, eye_y + 10))
        screen.blit(blush, (head_x + head_w - 16, eye_y + 10))

    def _draw_hermione(self, screen, x, y, w, h):
        dir = self.direction
        moving = abs(self.vel_x) > 0.5

        # Shadow
        shadow_surf = pygame.Surface((w + 8, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, w + 8, 8))
        screen.blit(shadow_surf, (x - 4, y + h - 4))

        # Legs
        leg_offset = int(math.sin(pygame.time.get_ticks() / 100) * 3) if moving else 0
        pygame.draw.rect(screen, (50, 50, 60), (x + 12, y + 46 - leg_offset, 8, 18))
        pygame.draw.rect(screen, (50, 50, 60), (x + 28, y + 46 + leg_offset, 8, 18))
        pygame.draw.rect(screen, (30, 30, 35), (x + 12, y + 60 - leg_offset, 8, 6))
        pygame.draw.rect(screen, (30, 30, 35), (x + 28, y + 60 + leg_offset, 8, 6))

        # Skirt
        pygame.draw.polygon(screen, (60, 60, 70), [(x + 10, y + 40), (x + w - 10, y + 40), (x + w - 6, y + 50), (x + 6, y + 50)])
        pygame.draw.polygon(screen, (40, 40, 50), [(x + 10, y + 40), (x + w - 10, y + 40), (x + w - 6, y + 50), (x + 6, y + 50)], 2)

        # Body/Sweater
        pygame.draw.rect(screen, (100, 100, 110), (x + 10, y + 26, w - 20, 18))
        pygame.draw.rect(screen, (80, 80, 90), (x + 10, y + 26, 8, 18))
        pygame.draw.rect(screen, (50, 50, 60), (x + 10, y + 26, w - 20, 18), 2)

        # Gryffindor tie
        pygame.draw.polygon(screen, (180, 30, 50), [(x + w//2 - 3, y + 24), (x + w//2 + 3, y + 24), (x + w//2 + 2, y + 40), (x + w//2 - 2, y + 40)])
        pygame.draw.line(screen, (255, 200, 50), (x + w//2, y + 28), (x + w//2, y + 32), 2)
        pygame.draw.line(screen, (255, 200, 50), (x + w//2, y + 34), (x + w//2, y + 38), 2)

        # Arms
        pygame.draw.rect(screen, (100, 100, 110), (x + 6 if dir > 0 else x + w - 12, y + 28, 8, 14))
        pygame.draw.rect(screen, (100, 100, 110), (x + w - 8 if dir > 0 else x, y + 28, 8, 14))

        # Wand
        wand_x = x + w + 2 if dir > 0 else x - 12
        pygame.draw.line(screen, (180, 150, 120), (wand_x, y + 42), (wand_x + 10 * dir, y + 36), 3)
        if self.attacking:
            glow = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(glow, (150, 200, 255, 180), (8, 8), 6)
            screen.blit(glow, (wand_x + 8 * dir - 8, y + 28))

        # Head
        pygame.draw.ellipse(screen, (255, 215, 185), (x + 12, y + 6, w - 24, 22))
        pygame.draw.ellipse(screen, (240, 200, 170), (x + 12, y + 12, 8, 14))
        pygame.draw.ellipse(screen, (40, 30, 25), (x + 12, y + 6, w - 24, 22), 2)

        # Big bushy brown hair
        pygame.draw.ellipse(screen, (100, 60, 30), (x, y - 8, w, 28))
        pygame.draw.ellipse(screen, (120, 70, 35), (x + 4, y - 6, w - 8, 16))  # Highlight
        pygame.draw.ellipse(screen, (90, 50, 25), (x - 4, y + 2, 16, 22))  # Side
        pygame.draw.ellipse(screen, (90, 50, 25), (x + w - 12, y + 2, 16, 22))
        # Redraw face over hair
        pygame.draw.ellipse(screen, (255, 215, 185), (x + 12, y + 6, w - 24, 22))

        # Eyes - intelligent, focused
        eye_offset = 2 * dir
        pygame.draw.circle(screen, WHITE, (x + w//2 - 6 + eye_offset, y + 14), 4)
        pygame.draw.circle(screen, WHITE, (x + w//2 + 6 + eye_offset, y + 14), 4)
        pygame.draw.circle(screen, (120, 80, 50), (x + w//2 - 5 + eye_offset + dir, y + 14), 3)
        pygame.draw.circle(screen, (120, 80, 50), (x + w//2 + 7 + eye_offset + dir, y + 14), 3)
        pygame.draw.circle(screen, (80, 50, 30), (x + w//2 - 5 + eye_offset + dir, y + 14), 2)
        pygame.draw.circle(screen, (80, 50, 30), (x + w//2 + 7 + eye_offset + dir, y + 14), 2)
        pygame.draw.circle(screen, WHITE, (x + w//2 - 4 + eye_offset, y + 13), 1)
        pygame.draw.circle(screen, WHITE, (x + w//2 + 8 + eye_offset, y + 13), 1)

        # Determined eyebrows
        pygame.draw.line(screen, (80, 50, 30), (x + w//2 - 10 + eye_offset, y + 9), (x + w//2 - 3 + eye_offset, y + 8), 2)
        pygame.draw.line(screen, (80, 50, 30), (x + w//2 + 3 + eye_offset, y + 8), (x + w//2 + 10 + eye_offset, y + 9), 2)

        # Mouth
        if self.attacking:
            pygame.draw.line(screen, (180, 100, 100), (x + w//2 - 3, y + 22), (x + w//2 + 3, y + 21), 2)
        else:
            pygame.draw.arc(screen, (180, 100, 100), (x + w//2 - 3, y + 20, 6, 4), 3.14, 6.28, 1)

    def _draw_voldemort(self, screen, x, y, w, h):
        dir = self.direction
        moving = abs(self.vel_x) > 0.5

        # Dark aura effect
        aura = pygame.Surface((w + 30, h + 20), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (0, 50, 0, 40), (0, 0, w + 30, h + 20))
        screen.blit(aura, (x - 15, y - 10))

        # Shadow
        shadow_surf = pygame.Surface((w + 10, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), (0, 0, w + 10, 10))
        screen.blit(shadow_surf, (x - 5, y + h - 6))

        # Flowing dark robes
        robe_sway = int(math.sin(pygame.time.get_ticks() / 200) * 3)
        robe_points = [
            (x + 6, y + 24),
            (x + w - 6, y + 24),
            (x + w + robe_sway, y + h - 4),
            (x - robe_sway, y + h - 4)
        ]
        pygame.draw.polygon(screen, (20, 20, 25), robe_points)
        pygame.draw.polygon(screen, (40, 40, 50), robe_points, 2)
        # Robe folds
        pygame.draw.line(screen, (35, 35, 45), (x + 16, y + 30), (x + 12, y + h - 10), 2)
        pygame.draw.line(screen, (35, 35, 45), (x + w - 16, y + 30), (x + w - 12, y + h - 10), 2)

        # Arms in robes
        pygame.draw.polygon(screen, (25, 25, 30), [(x + 6 if dir > 0 else x + w - 12, y + 28),
                                                    (x - 4 if dir > 0 else x + w + 4, y + 40),
                                                    (x + 2 if dir > 0 else x + w - 8, y + 44)])

        # Wand arm
        wand_arm_x = x + w - 4 if dir > 0 else x - 4
        pygame.draw.polygon(screen, (25, 25, 30), [(x + w - 8 if dir > 0 else x + 2, y + 28),
                                                    (wand_arm_x + 8 * dir, y + 38),
                                                    (x + w - 4 if dir > 0 else x - 2, y + 44)])
        # Pale hand
        pygame.draw.circle(screen, (220, 220, 225), (wand_arm_x + 10 * dir, y + 40), 5)

        # Elder Wand
        wand_x = wand_arm_x + 12 * dir
        pygame.draw.line(screen, (240, 235, 220), (wand_x, y + 40), (wand_x + 18 * dir, y + 32), 3)
        pygame.draw.circle(screen, (200, 200, 200), (wand_x + 4 * dir, y + 38), 3)  # Wand detail
        if self.attacking:
            # Green killing curse glow
            glow = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(glow, (0, 255, 0, 150), (15, 15), 12)
            pygame.draw.circle(glow, (150, 255, 150, 200), (15, 15), 6)
            screen.blit(glow, (wand_x + 14 * dir - 15, y + 18))

        # Pale serpentine head
        pygame.draw.ellipse(screen, (220, 225, 230), (x + 8, y - 2, w - 16, 30))  # Main head
        pygame.draw.ellipse(screen, (200, 205, 210), (x + 8, y + 8, 12, 18))  # Shadow
        pygame.draw.ellipse(screen, (60, 60, 70), (x + 8, y - 2, w - 16, 30), 2)  # Outline

        # Red slit eyes - menacing
        eye_offset = 2 * dir
        # Eye sockets
        pygame.draw.ellipse(screen, (180, 180, 185), (x + w//2 - 10 + eye_offset, y + 8, 10, 12))
        pygame.draw.ellipse(screen, (180, 180, 185), (x + w//2 + eye_offset, y + 8, 10, 12))
        # Red iris with slit pupils
        pygame.draw.ellipse(screen, (200, 0, 0), (x + w//2 - 8 + eye_offset, y + 10, 6, 8))
        pygame.draw.ellipse(screen, (200, 0, 0), (x + w//2 + 2 + eye_offset, y + 10, 6, 8))
        pygame.draw.line(screen, (0, 0, 0), (x + w//2 - 5 + eye_offset, y + 10), (x + w//2 - 5 + eye_offset, y + 18), 2)
        pygame.draw.line(screen, (0, 0, 0), (x + w//2 + 5 + eye_offset, y + 10), (x + w//2 + 5 + eye_offset, y + 18), 2)
        # Eye glow
        pygame.draw.ellipse(screen, (255, 100, 100), (x + w//2 - 7 + eye_offset, y + 12, 4, 4))
        pygame.draw.ellipse(screen, (255, 100, 100), (x + w//2 + 3 + eye_offset, y + 12, 4, 4))

        # Nose slits
        pygame.draw.line(screen, (150, 150, 160), (x + w//2 - 2, y + 20), (x + w//2 - 1, y + 18), 2)
        pygame.draw.line(screen, (150, 150, 160), (x + w//2 + 2, y + 20), (x + w//2 + 1, y + 18), 2)

        # Thin cruel mouth
        if self.attacking:
            pygame.draw.arc(screen, (100, 50, 50), (x + w//2 - 6, y + 22, 12, 6), 0, 3.14, 2)
            pygame.draw.line(screen, (60, 30, 30), (x + w//2 - 5, y + 24), (x + w//2 + 5, y + 24), 1)
        else:
            pygame.draw.line(screen, (150, 100, 100), (x + w//2 - 5, y + 24), (x + w//2 + 5, y + 24), 2)

    def _draw_hagrid(self, screen, x, y, w, h):
        """Draw Hagrid - the lovable half-giant gamekeeper."""
        dir = self.direction
        moving = abs(self.vel_x) > 0.5
        t = pygame.time.get_ticks()

        # Large shadow for big character
        shadow_surf = pygame.Surface((w + 24, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), (0, 0, w + 24, 14))
        screen.blit(shadow_surf, (x - 12, y + h - 6))

        # Leg animation
        leg_offset = int(math.sin(t / 120) * 3) if moving else 0

        # Big sturdy boots with laces
        boot_color = (60, 40, 25)
        boot_highlight = (80, 55, 35)
        boot_shadow = (40, 25, 15)
        # Left boot
        pygame.draw.ellipse(screen, boot_color, (x + 4, y + h - 20 - leg_offset, 18, 22))
        pygame.draw.ellipse(screen, boot_shadow, (x + 4, y + h - 20 - leg_offset, 8, 22))
        pygame.draw.ellipse(screen, boot_highlight, (x + 14, y + h - 18 - leg_offset, 6, 8))
        pygame.draw.ellipse(screen, (30, 18, 10), (x + 4, y + h - 20 - leg_offset, 18, 22), 2)
        # Right boot
        pygame.draw.ellipse(screen, boot_color, (x + w - 22, y + h - 20 + leg_offset, 18, 22))
        pygame.draw.ellipse(screen, boot_shadow, (x + w - 22, y + h - 20 + leg_offset, 8, 22))
        pygame.draw.ellipse(screen, boot_highlight, (x + w - 12, y + h - 18 + leg_offset, 6, 8))
        pygame.draw.ellipse(screen, (30, 18, 10), (x + w - 22, y + h - 20 + leg_offset, 18, 22), 2)

        # Massive moleskin overcoat - layered for depth
        coat_base = (95, 65, 40)
        coat_shadow = (65, 45, 28)
        coat_highlight = (120, 85, 55)
        # Main coat body
        pygame.draw.ellipse(screen, coat_base, (x - 6, y + 16, w + 12, h - 20))
        # Shadow on left side
        pygame.draw.ellipse(screen, coat_shadow, (x - 6, y + 20, 18, h - 30))
        # Highlight on right
        pygame.draw.arc(screen, coat_highlight, (x + w - 20, y + 25, 20, h - 40), -1.5, 1.5, 4)
        # Outline
        pygame.draw.ellipse(screen, (45, 30, 18), (x - 6, y + 16, w + 12, h - 20), 3)

        # Coat texture - fur trim and patches
        for i in range(4):
            patch_x = x + 8 + i * 10 + random.randint(-2, 2)
            patch_y = y + 35 + (i % 2) * 12
            pygame.draw.ellipse(screen, (80, 55, 35), (patch_x, patch_y, 8, 6))
        # Fur collar
        pygame.draw.ellipse(screen, (70, 50, 30), (x, y + 14, w, 14))
        pygame.draw.ellipse(screen, (55, 38, 22), (x, y + 14, w, 14), 2)

        # Thick leather belt with big buckle
        pygame.draw.rect(screen, (50, 32, 18), (x - 2, y + 44, w + 4, 10))
        pygame.draw.rect(screen, (35, 22, 12), (x - 2, y + 44, w + 4, 10), 2)
        # Belt buckle (brass colored)
        pygame.draw.rect(screen, (200, 170, 80), (x + w//2 - 8, y + 42, 16, 14), border_radius=2)
        pygame.draw.rect(screen, (160, 130, 50), (x + w//2 - 8, y + 42, 16, 14), 2, border_radius=2)
        pygame.draw.rect(screen, (180, 150, 60), (x + w//2 - 4, y + 46, 8, 6))

        # Strong arms
        arm_swing = int(math.sin(t / 150) * 3) if moving else 0
        # Back arm
        back_arm_x = x - 12 if dir < 0 else x + w - 4
        pygame.draw.ellipse(screen, coat_base, (back_arm_x, y + 22 - arm_swing, 18, 32))
        pygame.draw.ellipse(screen, coat_shadow, (back_arm_x, y + 22 - arm_swing, 8, 32))
        # Front arm (holding umbrella)
        front_arm_x = x + w - 2 if dir > 0 else x - 14
        pygame.draw.ellipse(screen, coat_base, (front_arm_x, y + 20 + arm_swing, 18, 34))
        pygame.draw.ellipse(screen, coat_highlight, (front_arm_x + 10, y + 24 + arm_swing, 6, 20))
        # Big hands
        hand_color = (210, 175, 145)
        pygame.draw.circle(screen, hand_color, (back_arm_x + 9, y + 52 - arm_swing), 9)
        pygame.draw.circle(screen, hand_color, (front_arm_x + 9, y + 52 + arm_swing), 9)
        pygame.draw.circle(screen, (190, 155, 125), (back_arm_x + 9, y + 52 - arm_swing), 9, 2)
        pygame.draw.circle(screen, (190, 155, 125), (front_arm_x + 9, y + 52 + arm_swing), 9, 2)

        # Pink umbrella (hidden wand!)
        umbrella_x = x + w + 16 if dir > 0 else x - 24
        umbrella_tip = umbrella_x + (4 if dir > 0 else -4)
        # Handle
        pygame.draw.line(screen, (180, 100, 120), (umbrella_x, y + 28 + arm_swing), (umbrella_x, y + 65 + arm_swing), 5)
        pygame.draw.line(screen, (200, 130, 150), (umbrella_x - 1, y + 30 + arm_swing), (umbrella_x - 1, y + 60 + arm_swing), 2)
        # Curved handle end
        pygame.draw.arc(screen, (180, 100, 120), (umbrella_x - 8, y + 58 + arm_swing, 16, 14), 3.14, 6.28, 4)
        # Umbrella top (closed)
        pygame.draw.polygon(screen, (220, 140, 170), [
            (umbrella_x - 10, y + 28 + arm_swing),
            (umbrella_x, y + 14 + arm_swing),
            (umbrella_x + 10, y + 28 + arm_swing)
        ])
        pygame.draw.polygon(screen, (180, 100, 130), [
            (umbrella_x - 10, y + 28 + arm_swing),
            (umbrella_x, y + 14 + arm_swing),
            (umbrella_x + 10, y + 28 + arm_swing)
        ], 2)
        # Magic glow when attacking
        if self.attacking:
            glow = pygame.Surface((30, 30), pygame.SRCALPHA)
            glow_intensity = int(180 + math.sin(t * 0.02) * 50)
            pygame.draw.circle(glow, (255, 150, 200, glow_intensity), (15, 15), 12)
            pygame.draw.circle(glow, (255, 200, 230, glow_intensity), (15, 15), 6)
            screen.blit(glow, (umbrella_x - 15, y + 4 + arm_swing))

        # Big bushy hair - wild and unkempt
        hair_color = (50, 38, 28)
        hair_highlight = (70, 55, 40)
        # Main hair mass
        pygame.draw.ellipse(screen, hair_color, (x - 8, y - 16, w + 16, 38))
        # Hair texture - wild strands
        for i in range(6):
            strand_x = x - 4 + i * 8
            strand_h = 8 + (i % 3) * 4
            pygame.draw.ellipse(screen, hair_highlight if i % 2 else hair_color,
                              (strand_x, y - 18 + (i % 2) * 4, 10, strand_h))
        # Side hair/sideburns
        pygame.draw.ellipse(screen, hair_color, (x - 10, y + 2, 14, 22))
        pygame.draw.ellipse(screen, hair_color, (x + w - 4, y + 2, 14, 22))

        # Face peeking through hair
        face_color = (225, 190, 160)
        face_shadow = (200, 165, 135)
        pygame.draw.ellipse(screen, face_color, (x + 8, y, w - 16, 24))
        pygame.draw.ellipse(screen, face_shadow, (x + 8, y + 4, 10, 16))

        # Massive bushy beard
        beard_color = (50, 38, 28)
        beard_highlight = (65, 50, 38)
        # Main beard
        pygame.draw.ellipse(screen, beard_color, (x - 4, y + 12, w + 8, 34))
        # Beard texture - wavy strands
        for i in range(5):
            strand_x = x + 2 + i * 9
            pygame.draw.ellipse(screen, beard_highlight, (strand_x, y + 20 + (i % 2) * 4, 8, 18))
        pygame.draw.ellipse(screen, (40, 28, 18), (x - 4, y + 12, w + 8, 34), 2)

        # Small beetle-black eyes - kind and crinkly
        eye_offset = 3 * dir
        eye_y = y + 8
        # Eye sockets/crinkles
        pygame.draw.ellipse(screen, face_shadow, (x + w//2 - 12 + eye_offset, eye_y - 2, 10, 8))
        pygame.draw.ellipse(screen, face_shadow, (x + w//2 + 4 + eye_offset, eye_y - 2, 10, 8))
        # Eyes
        pygame.draw.circle(screen, (25, 22, 20), (x + w//2 - 7 + eye_offset, eye_y + 2), 5)
        pygame.draw.circle(screen, (25, 22, 20), (x + w//2 + 9 + eye_offset, eye_y + 2), 5)
        # Eye shine
        pygame.draw.circle(screen, (255, 255, 255), (x + w//2 - 8 + eye_offset, eye_y), 2)
        pygame.draw.circle(screen, (255, 255, 255), (x + w//2 + 8 + eye_offset, eye_y), 2)
        # Bushy eyebrows
        pygame.draw.ellipse(screen, hair_color, (x + w//2 - 14 + eye_offset, eye_y - 6, 12, 6))
        pygame.draw.ellipse(screen, hair_color, (x + w//2 + 2 + eye_offset, eye_y - 6, 12, 6))

        # Rosy cheeks (friendly!)
        cheek_surf = pygame.Surface((12, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(cheek_surf, (255, 180, 180, 100), (0, 0, 12, 8))
        screen.blit(cheek_surf, (x + 10, y + 10))
        screen.blit(cheek_surf, (x + w - 22, y + 10))

        # Big friendly smile visible through beard
        smile_y = y + 22
        pygame.draw.arc(screen, (180, 100, 100), (x + w//2 - 10, smile_y, 20, 12), 3.14, 6.28, 3)

    def _draw_unicorn(self, screen, x, y, w, h):
        dir = self.direction
        moving = abs(self.vel_x) > 0.5

        # Magical sparkle aura
        if self.character.heals:
            aura = pygame.Surface((w + 30, h + 20), pygame.SRCALPHA)
            for i in range(5):
                alpha = 60 - i * 10
                pygame.draw.ellipse(aura, (255, 255, 255, alpha), (i * 3, i * 2, w + 30 - i * 6, h + 20 - i * 4))
            screen.blit(aura, (x - 15, y - 10))

        # Shadow
        shadow_surf = pygame.Surface((w, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 40), (0, 0, w, 8))
        screen.blit(shadow_surf, (x, y + h - 4))

        # Legs with silver hooves - animated
        leg_anim = math.sin(pygame.time.get_ticks() / 100) * 4 if moving else 0
        for i, lx in enumerate([10, 20, w - 28, w - 18]):
            leg_y = y + h - 22 + (leg_anim if i % 2 == 0 else -leg_anim)
            pygame.draw.rect(screen, (250, 250, 255), (x + lx, leg_y, 8, 18))
            pygame.draw.rect(screen, (220, 220, 230), (x + lx, leg_y, 3, 18))  # Shading
            pygame.draw.rect(screen, (200, 210, 220), (x + lx, leg_y, 8, 18), 1)
            pygame.draw.ellipse(screen, (200, 200, 210), (x + lx - 1, y + h - 8, 10, 8))  # Hoof

        # Body - elegant
        pygame.draw.ellipse(screen, (255, 255, 255), (x + 4, y + 22, w - 8, h - 30))
        pygame.draw.ellipse(screen, (240, 240, 250), (x + 4, y + 30, 15, h - 40))  # Shading
        pygame.draw.ellipse(screen, (200, 200, 220), (x + 4, y + 22, w - 8, h - 30), 2)

        # Rainbow mane
        mane_colors = [(255, 100, 150), (255, 200, 100), (150, 255, 150), (150, 200, 255), (200, 150, 255)]
        mane_x = x + w - 15 if dir > 0 else x + 5
        for i, color in enumerate(mane_colors):
            wave = math.sin(pygame.time.get_ticks() / 200 + i) * 3
            pygame.draw.ellipse(screen, color, (mane_x - 5 + wave, y + 8 + i * 6, 14, 10))

        # Tail - flowing
        tail_x = x - 8 if dir > 0 else x + w
        tail_wave = math.sin(pygame.time.get_ticks() / 150) * 5
        for i, color in enumerate(mane_colors):
            pygame.draw.ellipse(screen, color, (tail_x + tail_wave - i * dir * 3, y + 35 + i * 4, 12, 8))

        # Head
        head_x = x + w - 18 if dir > 0 else x - 4
        pygame.draw.ellipse(screen, (255, 255, 255), (head_x, y + 6, 24, 24))
        pygame.draw.ellipse(screen, (240, 240, 250), (head_x + 2, y + 14, 10, 14))
        pygame.draw.ellipse(screen, (200, 200, 220), (head_x, y + 6, 24, 24), 2)

        # Snout
        snout_x = head_x + (18 if dir > 0 else -4)
        pygame.draw.ellipse(screen, (255, 250, 250), (snout_x, y + 16, 12, 10))
        pygame.draw.circle(screen, (220, 200, 210), (snout_x + 3, y + 20), 2)  # Nostril
        pygame.draw.circle(screen, (220, 200, 210), (snout_x + 8, y + 20), 2)

        # Golden horn with spiral
        horn_x = head_x + 12
        pygame.draw.polygon(screen, (255, 220, 100), [(horn_x, y + 6), (horn_x - 5, y - 18), (horn_x + 5, y - 18)])
        pygame.draw.polygon(screen, (255, 240, 150), [(horn_x, y + 6), (horn_x - 3, y - 14), (horn_x + 1, y + 4)])
        # Spiral detail
        for i in range(4):
            pygame.draw.arc(screen, (220, 180, 80), (horn_x - 4, y - 14 + i * 5, 8, 6), 0 if i % 2 == 0 else 3.14, 3.14 if i % 2 == 0 else 6.28, 1)

        # Beautiful eye
        eye_x = head_x + (16 if dir > 0 else 6)
        pygame.draw.ellipse(screen, WHITE, (eye_x - 4, y + 12, 10, 8))
        pygame.draw.ellipse(screen, (150, 100, 180), (eye_x - 2, y + 13, 6, 6))
        pygame.draw.ellipse(screen, (100, 50, 130), (eye_x - 1, y + 14, 4, 4))
        pygame.draw.circle(screen, WHITE, (eye_x, y + 14), 1)
        # Long eyelashes
        pygame.draw.line(screen, (100, 80, 100), (eye_x - 3, y + 11), (eye_x - 5, y + 8), 1)
        pygame.draw.line(screen, (100, 80, 100), (eye_x, y + 10), (eye_x, y + 7), 1)
        pygame.draw.line(screen, (100, 80, 100), (eye_x + 3, y + 11), (eye_x + 5, y + 8), 1)

    def _draw_dragon(self, screen, x, y, w, h):
        dir = self.direction
        moving = abs(self.vel_x) > 0.5
        is_flying = self.is_flying if hasattr(self, 'is_flying') else False

        # Fire glow when attacking
        if self.attacking:
            fire_glow = pygame.Surface((w + 40, h + 20), pygame.SRCALPHA)
            pygame.draw.ellipse(fire_glow, (255, 100, 0, 60), (0, 0, w + 40, h + 20))
            screen.blit(fire_glow, (x - 20, y - 10))

        # Shadow (smaller when flying)
        shadow_alpha = 30 if is_flying else 60
        shadow_surf = pygame.Surface((w + 10, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, shadow_alpha), (0, 0, w + 10, 10))
        screen.blit(shadow_surf, (x - 5, y + h - 6))

        # Tail - segmented with spikes
        tail_base_x = x - 5 if dir > 0 else x + w + 5
        tail_wave = math.sin(pygame.time.get_ticks() / 150) * 8
        for i in range(4):
            segment_x = tail_base_x - (i * 10 + tail_wave * (i / 4)) * dir
            segment_y = y + 30 + i * 3
            size = 12 - i * 2
            pygame.draw.ellipse(screen, (180, 40, 40), (segment_x - size//2, segment_y, size, size - 2))
            pygame.draw.ellipse(screen, (140, 30, 30), (segment_x - size//2, segment_y, size, size - 2), 1)
            # Tail spikes
            if i < 3:
                pygame.draw.polygon(screen, (200, 60, 40), [(segment_x, segment_y), (segment_x - 3, segment_y - 8), (segment_x + 3, segment_y - 6)])

        # Legs with claws
        if not is_flying:
            leg_anim = math.sin(pygame.time.get_ticks() / 100) * 3 if moving else 0
            # Back legs
            pygame.draw.ellipse(screen, (180, 40, 40), (x + 6, y + h - 20 - leg_anim, 14, 16))
            pygame.draw.ellipse(screen, (180, 40, 40), (x + w - 20, y + h - 20 + leg_anim, 14, 16))
            # Claws
            for lx in [x + 8, x + w - 18]:
                for cx in range(3):
                    pygame.draw.polygon(screen, (255, 220, 150), [(lx + cx * 4, y + h - 6), (lx + cx * 4 + 2, y + h), (lx + cx * 4 + 4, y + h - 6)])

        # Main body - scaled texture
        pygame.draw.ellipse(screen, (200, 50, 50), (x + 4, y + 18, w - 8, h - 24))
        pygame.draw.ellipse(screen, (160, 35, 35), (x + 4, y + 26, 15, h - 34))  # Shadow
        pygame.draw.ellipse(screen, (120, 25, 25), (x + 4, y + 18, w - 8, h - 24), 2)  # Outline
        # Scale pattern
        for row in range(3):
            for col in range(4):
                sx = x + 10 + col * 10
                sy = y + 24 + row * 8
                pygame.draw.arc(screen, (170, 45, 45), (sx, sy, 8, 6), 0, 3.14, 1)

        # Belly plates (lighter)
        pygame.draw.ellipse(screen, (230, 180, 120), (x + 14, y + 28, w - 28, h - 40))
        for i in range(4):
            pygame.draw.arc(screen, (210, 160, 100), (x + 16, y + 30 + i * 6, w - 32, 8), 0, 3.14, 1)

        # Wings - bat-like with membrane
        wing_flap = math.sin(pygame.time.get_ticks() / 100) * 15 if is_flying else math.sin(pygame.time.get_ticks() / 300) * 5
        # Left wing
        wing_pts_l = [(x + 8, y + 20), (x - 25, y + 5 - wing_flap), (x - 30, y + 20 - wing_flap // 2), (x - 20, y + 35), (x + 4, y + 30)]
        pygame.draw.polygon(screen, (180, 80, 60), wing_pts_l)
        pygame.draw.polygon(screen, (120, 50, 40), wing_pts_l, 2)
        # Wing bones
        pygame.draw.line(screen, (200, 100, 80), (x + 6, y + 22), (x - 25, y + 8 - wing_flap), 2)
        pygame.draw.line(screen, (200, 100, 80), (x + 6, y + 24), (x - 28, y + 22 - wing_flap // 2), 2)
        # Right wing
        wing_pts_r = [(x + w - 8, y + 20), (x + w + 25, y + 5 - wing_flap), (x + w + 30, y + 20 - wing_flap // 2), (x + w + 20, y + 35), (x + w - 4, y + 30)]
        pygame.draw.polygon(screen, (180, 80, 60), wing_pts_r)
        pygame.draw.polygon(screen, (120, 50, 40), wing_pts_r, 2)
        pygame.draw.line(screen, (200, 100, 80), (x + w - 6, y + 22), (x + w + 25, y + 8 - wing_flap), 2)
        pygame.draw.line(screen, (200, 100, 80), (x + w - 6, y + 24), (x + w + 28, y + 22 - wing_flap // 2), 2)

        # Head
        head_x = x + w - 18 if dir > 0 else x - 8
        pygame.draw.ellipse(screen, (200, 50, 50), (head_x, y + 4, 28, 22))
        pygame.draw.ellipse(screen, (160, 40, 40), (head_x + 2, y + 12, 10, 12))
        pygame.draw.ellipse(screen, (120, 25, 25), (head_x, y + 4, 28, 22), 2)

        # Snout
        snout_x = head_x + (22 if dir > 0 else -6)
        pygame.draw.ellipse(screen, (190, 45, 45), (snout_x, y + 10, 14, 12))
        # Nostrils with smoke
        pygame.draw.circle(screen, (60, 30, 30), (snout_x + 4, y + 14), 2)
        pygame.draw.circle(screen, (60, 30, 30), (snout_x + 10, y + 14), 2)
        # Smoke wisps
        smoke_offset = math.sin(pygame.time.get_ticks() / 200) * 3
        pygame.draw.circle(screen, (100, 100, 100), (snout_x + 7 + smoke_offset * dir, y + 8), 3)
        pygame.draw.circle(screen, (120, 120, 120), (snout_x + 10 + smoke_offset * dir * 1.5, y + 4), 2)

        # Horns
        horn_base_x = head_x + 8
        pygame.draw.polygon(screen, (255, 200, 120), [(horn_base_x, y + 6), (horn_base_x - 4, y - 12), (horn_base_x + 4, y + 4)])
        pygame.draw.polygon(screen, (255, 200, 120), [(horn_base_x + 12, y + 6), (horn_base_x + 16, y - 10), (horn_base_x + 10, y + 4)])
        # Back spikes
        for i in range(4):
            spike_x = x + 12 + i * 10
            pygame.draw.polygon(screen, (220, 80, 60), [(spike_x, y + 18), (spike_x - 3, y + 10), (spike_x + 3, y + 10)])

        # Fierce eye
        eye_x = head_x + (18 if dir > 0 else 8)
        pygame.draw.ellipse(screen, (255, 255, 100), (eye_x - 4, y + 10, 10, 7))
        pygame.draw.ellipse(screen, (255, 200, 50), (eye_x - 3, y + 11, 8, 5))
        pygame.draw.line(screen, (0, 0, 0), (eye_x, y + 10), (eye_x, y + 16), 2)  # Slit pupil
        pygame.draw.ellipse(screen, (0, 0, 0), (eye_x - 4, y + 10, 10, 7), 1)
        # Brow ridge
        pygame.draw.line(screen, (140, 35, 35), (eye_x - 6, y + 8), (eye_x + 6, y + 7), 3)

        # Fire breath when attacking
        if self.attacking:
            fire_x = snout_x + (14 if dir > 0 else -30) * dir
            # Multi-layered fire
            pygame.draw.ellipse(screen, (255, 100, 0), (fire_x, y + 6, 35, 16))
            pygame.draw.ellipse(screen, (255, 200, 50), (fire_x + 5 * dir, y + 8, 25, 12))
            pygame.draw.ellipse(screen, (255, 255, 150), (fire_x + 10 * dir, y + 10, 15, 8))
            # Fire particles
            for i in range(3):
                px = fire_x + (20 + i * 8) * dir + random.randint(-3, 3)
                py = y + 10 + random.randint(-4, 4)
                pygame.draw.circle(screen, (255, 200, 100), (px, py), 3 - i)
