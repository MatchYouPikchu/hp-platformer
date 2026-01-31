# Scrolling Level with Mario-style design - Enhanced Graphics

import pygame
import math
import random
from settings import *


class Platform:
    """A platform with polished wooden plank graphics and support beams."""

    def __init__(self, x, y, width, height, style='stone'):
        self.rect = pygame.Rect(x, y, width, height)
        self.style = style
        self.plank_variations = []
        self._generate_planks()

    def _generate_planks(self):
        """Generate plank pattern variations."""
        plank_w = 40
        num_planks = max(1, self.rect.width // plank_w + 1)
        random.seed(self.rect.x + self.rect.y)  # Consistent variation per platform
        for i in range(num_planks):
            self.plank_variations.append({
                'hue': random.randint(-15, 15),
                'grain_offset': random.randint(0, 10),
                'knot_pos': random.randint(5, 25) if random.random() > 0.6 else -1
            })
        random.seed()

    def draw(self, screen, camera_x):
        screen_x = self.rect.x - camera_x
        if screen_x + self.rect.width < -50 or screen_x > SCREEN_WIDTH + 50:
            return

        # Universal wooden platform style for polished look
        # Rich wood colors
        wood_base = (139, 90, 43)      # Warm brown
        wood_light = (180, 130, 70)    # Highlight
        wood_dark = (90, 55, 25)       # Shadow/grain
        wood_edge = (70, 40, 15)       # Dark edge

        plank_w = 40
        plank_h = self.rect.height

        # Draw support beams FIRST (behind platform)
        self._draw_supports(screen, screen_x)

        # Draw main platform surface (wooden planks)
        num_planks = max(1, self.rect.width // plank_w + 1)

        for i in range(num_planks):
            px = screen_x + i * plank_w
            pw = min(plank_w, self.rect.width - i * plank_w)
            if pw <= 0:
                break
            if px + pw < 0 or px > SCREEN_WIDTH:
                continue

            var = self.plank_variations[i % len(self.plank_variations)]

            # Plank base color with variation
            base = tuple(max(0, min(255, c + var['hue'])) for c in wood_base)
            light = tuple(max(0, min(255, c + var['hue'])) for c in wood_light)
            dark = tuple(max(0, min(255, c + var['hue'])) for c in wood_dark)

            # Main plank body
            pygame.draw.rect(screen, base, (px, self.rect.y, pw, plank_h))

            # Top highlight bevel
            pygame.draw.rect(screen, light, (px, self.rect.y, pw, 4))

            # Left edge highlight
            pygame.draw.rect(screen, light, (px, self.rect.y, 3, plank_h))

            # Bottom shadow
            pygame.draw.rect(screen, dark, (px, self.rect.y + plank_h - 4, pw, 4))

            # Right edge shadow (plank gap)
            pygame.draw.rect(screen, wood_edge, (px + pw - 2, self.rect.y, 2, plank_h))

            # Wood grain lines
            grain_y = var['grain_offset']
            for g in range(3):
                gy = self.rect.y + 6 + g * 7 + grain_y % 4
                if gy < self.rect.y + plank_h - 3:
                    pygame.draw.line(screen, dark, (px + 4, gy), (px + pw - 4, gy), 1)

            # Wood knot (on some planks)
            if var['knot_pos'] > 0:
                kx = px + var['knot_pos']
                ky = self.rect.y + plank_h // 2
                pygame.draw.circle(screen, dark, (kx, ky), 4)
                pygame.draw.circle(screen, (60, 35, 15), (kx, ky), 2)

        # Platform edge trim (top and bottom borders)
        pygame.draw.rect(screen, wood_edge, (screen_x, self.rect.y, self.rect.width, 2))
        pygame.draw.rect(screen, wood_edge, (screen_x, self.rect.y + plank_h - 2, self.rect.width, 2))

        # Decorative metal brackets on ends
        if self.rect.width > 60:
            self._draw_bracket(screen, screen_x + 5, self.rect.y)
            self._draw_bracket(screen, screen_x + self.rect.width - 15, self.rect.y)

    def _draw_supports(self, screen, screen_x):
        """Draw wooden support beams underneath platform."""
        beam_color = (100, 60, 30)
        beam_dark = (70, 40, 20)
        beam_light = (130, 85, 45)

        # Vertical support posts
        support_spacing = 100
        num_supports = max(2, self.rect.width // support_spacing + 1)

        for i in range(num_supports):
            if i == 0:
                sx = screen_x + 10
            elif i == num_supports - 1:
                sx = screen_x + self.rect.width - 20
            else:
                sx = screen_x + i * support_spacing

            if sx < -20 or sx > SCREEN_WIDTH + 20:
                continue

            # Support post (vertical beam going down)
            post_h = 50 + (i % 2) * 15  # Vary height slightly
            py = self.rect.y + self.rect.height

            # Main post
            pygame.draw.rect(screen, beam_color, (sx, py, 12, post_h))
            # Left highlight
            pygame.draw.rect(screen, beam_light, (sx, py, 3, post_h))
            # Right shadow
            pygame.draw.rect(screen, beam_dark, (sx + 9, py, 3, post_h))

            # Diagonal brace
            if i < num_supports - 1:
                brace_end_x = sx + support_spacing // 2
                brace_end_y = py + post_h - 10
                pygame.draw.line(screen, beam_dark, (sx + 6, py + 5),
                               (brace_end_x, brace_end_y), 4)
                pygame.draw.line(screen, beam_color, (sx + 6, py + 5),
                               (brace_end_x, brace_end_y), 2)

    def _draw_bracket(self, screen, x, y):
        """Draw decorative metal bracket."""
        metal = (80, 80, 90)
        metal_light = (120, 120, 130)
        # Bracket shape
        pygame.draw.rect(screen, metal, (x, y + 2, 10, self.rect.height - 4))
        pygame.draw.rect(screen, metal_light, (x + 1, y + 3, 3, self.rect.height - 6))
        # Rivets
        pygame.draw.circle(screen, metal_light, (x + 5, y + 6), 2)
        pygame.draw.circle(screen, metal_light, (x + 5, y + self.rect.height - 6), 2)


class Hazard:
    """Environmental hazards - spikes, lava pools."""

    def __init__(self, x, y, width, hazard_type='spikes'):
        self.x = x
        self.y = y
        self.width = width
        self.hazard_type = hazard_type
        self.damage = 25 if hazard_type == 'spikes' else 15  # Lava does less but continuous
        self.rect = pygame.Rect(x, y, width, 30 if hazard_type == 'spikes' else 20)
        self.anim_timer = random.random() * math.pi * 2
        self.damaged_players = {}  # Track damage cooldown per player

    def update(self, dt):
        self.anim_timer += dt * 0.005
        # Reset damage cooldown
        for player_id in list(self.damaged_players.keys()):
            self.damaged_players[player_id] -= dt
            if self.damaged_players[player_id] <= 0:
                del self.damaged_players[player_id]

    def check_collision(self, player):
        """Check if player touches hazard and deal damage."""
        if not player.is_alive():
            return False
        
        # Smaller collision box (player needs to really touch it)
        hazard_hitbox = pygame.Rect(self.rect.x + 5, self.rect.y + 5, 
                                    self.rect.width - 10, self.rect.height - 5)
        
        if player.rect.colliderect(hazard_hitbox):
            player_id = id(player)
            if player_id not in self.damaged_players:
                # Deal damage
                cooldown = 1000 if self.hazard_type == 'spikes' else 500  # Lava damages faster
                self.damaged_players[player_id] = cooldown
                return True
        return False

    def draw(self, screen, camera_x):
        screen_x = int(self.x - camera_x)
        if screen_x + self.width < -50 or screen_x > SCREEN_WIDTH + 50:
            return

        if self.hazard_type == 'spikes':
            # Draw metal spikes
            spike_width = 16
            num_spikes = max(1, self.width // spike_width)
            for i in range(num_spikes):
                sx = screen_x + i * spike_width + spike_width // 2
                sy = self.y
                # Spike triangle
                pygame.draw.polygon(screen, (100, 100, 110), [
                    (sx, sy), (sx - 7, sy + 28), (sx + 7, sy + 28)
                ])
                # Metallic highlight
                pygame.draw.polygon(screen, (150, 150, 160), [
                    (sx, sy), (sx - 3, sy + 14), (sx, sy + 14)
                ])
                # Dark edge
                pygame.draw.polygon(screen, (60, 60, 70), [
                    (sx, sy), (sx - 7, sy + 28), (sx + 7, sy + 28)
                ], 1)
            # Base
            pygame.draw.rect(screen, (80, 80, 90), (screen_x, self.y + 25, self.width, 8))
            pygame.draw.rect(screen, (50, 50, 60), (screen_x, self.y + 25, self.width, 8), 1)
            
        elif self.hazard_type == 'lava':
            # Animated lava pool
            # Base dark red
            pygame.draw.rect(screen, (100, 20, 10), (screen_x, self.y, self.width, 20))
            
            # Bubbling surface
            for i in range(0, self.width, 20):
                bubble_y = self.y + 5 + math.sin(self.anim_timer + i * 0.3) * 4
                bubble_size = 8 + math.sin(self.anim_timer * 2 + i) * 3
                # Bright orange/yellow center
                pygame.draw.ellipse(screen, (255, 150, 50), 
                                   (screen_x + i + 2, bubble_y, int(bubble_size * 2), int(bubble_size)))
                pygame.draw.ellipse(screen, (255, 220, 100), 
                                   (screen_x + i + 5, bubble_y + 2, int(bubble_size), int(bubble_size * 0.6)))
            
            # Glowing edge
            pygame.draw.rect(screen, (255, 100, 30), (screen_x, self.y, self.width, 3))
            
            # Occasional bright spot
            if math.sin(self.anim_timer * 3) > 0.7:
                spot_x = screen_x + int((math.sin(self.anim_timer * 1.5) + 1) * self.width * 0.4)
                pygame.draw.circle(screen, (255, 255, 150), (spot_x, self.y + 10), 6)


class Collectible:
    """Collectible items - coins and power-ups."""

    def __init__(self, x, y, collect_type='coin'):
        self.x = x
        self.y = y
        self.collect_type = collect_type
        self.collected = False
        self.rect = pygame.Rect(x, y, 24, 24)
        self.bob_offset = random.random() * math.pi * 2
        self.sparkle_timer = 0

    def update(self, dt):
        self.sparkle_timer += dt

    def draw(self, screen, camera_x):
        if self.collected:
            return
            
        screen_x = int(self.x - camera_x)
        if screen_x < -30 or screen_x > SCREEN_WIDTH + 30:
            return

        # Bob animation
        bob = math.sin(pygame.time.get_ticks() * 0.005 + self.bob_offset) * 4
        draw_y = int(self.y + bob)

        if self.collect_type == 'coin':
            # Golden coin with beautiful glow
            cx, cy = screen_x + 12, draw_y + 12

            # Outer glow (pulsing)
            glow_pulse = abs(math.sin(pygame.time.get_ticks() * 0.004 + self.bob_offset)) * 0.4 + 0.6
            glow_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
            glow_alpha = int(60 * glow_pulse)
            pygame.draw.circle(glow_surf, (255, 200, 50, glow_alpha), (20, 20), 18)
            pygame.draw.circle(glow_surf, (255, 220, 100, glow_alpha // 2), (20, 20), 14)
            screen.blit(glow_surf, (cx - 20, cy - 20))

            # Coin body - gradient effect
            pygame.draw.circle(screen, (180, 140, 20), (cx, cy), 13)  # Dark edge
            pygame.draw.circle(screen, (255, 200, 50), (cx, cy), 12)   # Main gold
            pygame.draw.circle(screen, (255, 220, 80), (cx - 1, cy - 1), 10)  # Lighter center
            pygame.draw.circle(screen, (255, 240, 150), (cx - 3, cy - 3), 5)   # Highlight

            # Inner ring detail
            pygame.draw.circle(screen, (200, 160, 40), (cx, cy), 7, 2)

            # Bright sparkle
            pygame.draw.circle(screen, (255, 255, 220), (cx - 4, cy - 4), 3)
            pygame.draw.circle(screen, WHITE, (cx - 4, cy - 4), 2)
            
        elif self.collect_type == 'health':
            # Health potion (red)
            pygame.draw.rect(screen, (180, 40, 40), (screen_x + 6, draw_y + 8, 12, 14), border_radius=3)
            pygame.draw.rect(screen, (220, 60, 60), (screen_x + 8, draw_y + 10, 8, 10), border_radius=2)
            pygame.draw.rect(screen, (100, 80, 70), (screen_x + 5, draw_y + 4, 14, 5), border_radius=2)
            # Cross
            pygame.draw.rect(screen, WHITE, (screen_x + 10, draw_y + 12, 4, 8))
            pygame.draw.rect(screen, WHITE, (screen_x + 8, draw_y + 14, 8, 4))
            
        elif self.collect_type == 'speed':
            # Speed boost (blue lightning)
            pygame.draw.circle(screen, (60, 120, 200), (screen_x + 12, draw_y + 12), 12)
            pygame.draw.circle(screen, (100, 160, 240), (screen_x + 12, draw_y + 12), 9)
            # Lightning bolt
            pygame.draw.polygon(screen, YELLOW, [
                (screen_x + 14, draw_y + 4), (screen_x + 8, draw_y + 13),
                (screen_x + 12, draw_y + 13), (screen_x + 10, draw_y + 22),
                (screen_x + 16, draw_y + 11), (screen_x + 12, draw_y + 11)
            ])
            
        elif self.collect_type == 'damage':
            # Damage boost (orange star)
            pygame.draw.circle(screen, (200, 100, 40), (screen_x + 12, draw_y + 12), 12)
            pygame.draw.circle(screen, ORANGE, (screen_x + 12, draw_y + 12), 9)
            # Star
            points = []
            for i in range(10):
                angle = (i / 10) * math.pi * 2 - math.pi / 2
                r = 7 if i % 2 == 0 else 3
                points.append((screen_x + 12 + math.cos(angle) * r, draw_y + 12 + math.sin(angle) * r))
            pygame.draw.polygon(screen, YELLOW, points)

        # Sparkle effect
        if int(self.sparkle_timer) % 500 < 100:
            sx = screen_x + random.randint(5, 19)
            sy = draw_y + random.randint(5, 19)
            pygame.draw.circle(screen, WHITE, (sx, sy), 2)


class Decoration:
    """Background decoration objects with improved graphics."""

    def __init__(self, x, y, dec_type):
        self.x = x
        self.y = y
        self.dec_type = dec_type

    def draw(self, screen, camera_x):
        screen_x = self.x - camera_x
        if screen_x < -150 or screen_x > SCREEN_WIDTH + 150:
            return

        if self.dec_type == 'tree':
            # Beautiful lush tree with depth
            tx = screen_x + 20
            ty = self.y

            # Trunk with detailed bark
            trunk_color = (90, 60, 35)
            trunk_dark = (60, 40, 25)
            trunk_light = (120, 80, 50)

            # Main trunk
            pygame.draw.rect(screen, trunk_color, (tx - 10, ty, 20, 70))
            # Bark texture - left shadow
            pygame.draw.rect(screen, trunk_dark, (tx - 10, ty, 6, 70))
            # Bark texture - right highlight
            pygame.draw.rect(screen, trunk_light, (tx + 4, ty, 4, 70))
            # Bark lines
            for i in range(5):
                by = ty + 10 + i * 12
                pygame.draw.line(screen, trunk_dark, (tx - 8, by), (tx + 6, by + 3), 2)

            # Root base
            pygame.draw.ellipse(screen, trunk_dark, (tx - 18, ty + 60, 36, 15))

            # Foliage - multiple layers for depth (back to front)
            foliage_dark = (25, 80, 30)
            foliage_mid = (40, 120, 45)
            foliage_light = (60, 150, 65)
            foliage_highlight = (90, 180, 95)

            # Back layer (darkest, largest)
            pygame.draw.circle(screen, foliage_dark, (tx - 15, ty - 15), 32)
            pygame.draw.circle(screen, foliage_dark, (tx + 18, ty - 10), 30)
            pygame.draw.circle(screen, foliage_dark, (tx, ty - 35), 28)

            # Mid layer
            pygame.draw.circle(screen, foliage_mid, (tx - 8, ty - 20), 28)
            pygame.draw.circle(screen, foliage_mid, (tx + 12, ty - 18), 26)
            pygame.draw.circle(screen, foliage_mid, (tx, ty - 40), 24)

            # Front layer (lightest)
            pygame.draw.circle(screen, foliage_light, (tx - 5, ty - 25), 22)
            pygame.draw.circle(screen, foliage_light, (tx + 8, ty - 22), 20)
            pygame.draw.circle(screen, foliage_light, (tx, ty - 42), 18)

            # Highlight spots
            pygame.draw.circle(screen, foliage_highlight, (tx - 12, ty - 35), 10)
            pygame.draw.circle(screen, foliage_highlight, (tx + 5, ty - 45), 8)
            pygame.draw.circle(screen, foliage_highlight, (tx + 15, ty - 28), 9)

        elif self.dec_type == 'castle_tower':
            # Stone tower with detail
            pygame.draw.rect(screen, (90, 90, 100), (screen_x, self.y, 65, 155))
            # Brick pattern
            for row in range(8):
                for col in range(2):
                    bx = screen_x + col * 32 + (16 if row % 2 else 0)
                    by = self.y + row * 20
                    pygame.draw.rect(screen, (75, 75, 85), (bx, by, 30, 18), 1)
            # Roof
            pygame.draw.polygon(screen, (60, 60, 70), [
                (screen_x - 8, self.y), (screen_x + 32, self.y - 50), (screen_x + 73, self.y)
            ])
            pygame.draw.polygon(screen, (80, 80, 90), [
                (screen_x + 32, self.y - 50), (screen_x + 32, self.y), (screen_x + 73, self.y)
            ])
            # Windows with glow
            for wy in [self.y + 30, self.y + 80, self.y + 120]:
                pygame.draw.rect(screen, (40, 40, 50), (screen_x + 22, wy, 22, 28), border_radius=5)
                pygame.draw.rect(screen, (255, 220, 150), (screen_x + 25, wy + 3, 16, 22), border_radius=3)
                pygame.draw.rect(screen, (255, 240, 200), (screen_x + 28, wy + 6, 10, 16), border_radius=2)

        elif self.dec_type == 'torch':
            t = pygame.time.get_ticks()
            tx = screen_x + 5
            ty = self.y

            # Wall mount bracket (metal)
            pygame.draw.rect(screen, (70, 60, 55), (tx - 4, ty + 25, 18, 10))
            pygame.draw.rect(screen, (50, 45, 40), (tx - 4, ty + 25, 18, 10), 2)

            # Torch handle (wood)
            pygame.draw.rect(screen, (100, 65, 40), (tx, ty, 10, 40))
            pygame.draw.rect(screen, (80, 50, 30), (tx, ty, 3, 40))
            pygame.draw.rect(screen, (120, 80, 50), (tx + 7, ty, 2, 40))

            # Torch top wrap
            pygame.draw.rect(screen, (60, 50, 45), (tx - 2, ty - 5, 14, 8))

            # Flame animation
            flicker = math.sin(t * 0.012) * 4
            flicker2 = math.sin(t * 0.018 + 1) * 3

            # Large outer glow
            glow_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            glow_pulse = int(abs(math.sin(t * 0.008)) * 25)
            pygame.draw.circle(glow_surf, (255, 150, 50, 35 + glow_pulse), (40, 40), 35)
            pygame.draw.circle(glow_surf, (255, 180, 80, 25 + glow_pulse), (40, 40), 25)
            pygame.draw.circle(glow_surf, (255, 200, 100, 20), (40, 40), 18)
            screen.blit(glow_surf, (tx - 35, ty - 60))

            # Flame layers (outer to inner)
            # Red outer
            pygame.draw.ellipse(screen, (200, 60, 20),
                              (tx - 8 + flicker2, ty - 35 + flicker, 26, 38))
            # Orange mid
            pygame.draw.ellipse(screen, (255, 120, 30),
                              (tx - 5 + flicker, ty - 30 + flicker, 20, 32))
            # Yellow inner
            pygame.draw.ellipse(screen, (255, 200, 50),
                              (tx - 2 + flicker, ty - 25 + flicker, 14, 24))
            # White core
            pygame.draw.ellipse(screen, (255, 250, 200),
                              (tx + 1 + flicker, ty - 18 + flicker, 8, 14))

        elif self.dec_type == 'banner':
            # Pole
            pygame.draw.rect(screen, (100, 70, 50), (screen_x + 14, self.y, 7, 85))
            pygame.draw.circle(screen, GOLD, (screen_x + 17, self.y - 5), 8)
            # Banner fabric with wave
            wave = math.sin(pygame.time.get_ticks() * 0.003) * 3
            points = [
                (screen_x - 2, self.y + 8), (screen_x + 38, self.y + 8),
                (screen_x + 40 + wave, self.y + 35), (screen_x + 38, self.y + 62),
                (screen_x + 18, self.y + 52), (screen_x - 2, self.y + 62)
            ]
            pygame.draw.polygon(screen, CRIMSON, points)
            pygame.draw.polygon(screen, (180, 30, 50), points, 2)
            # Hogwarts crest hint
            pygame.draw.circle(screen, GOLD, (screen_x + 18, self.y + 32), 12)
            pygame.draw.line(screen, GOLD, (screen_x + 8, self.y + 25), (screen_x + 8, self.y + 55), 2)
            pygame.draw.line(screen, GOLD, (screen_x + 28, self.y + 25), (screen_x + 28, self.y + 55), 2)

        elif self.dec_type == 'spooky_tree':
            # Gnarled trunk
            pygame.draw.polygon(screen, (45, 30, 20), [
                (screen_x + 5, self.y + 100), (screen_x + 35, self.y + 100),
                (screen_x + 30, self.y + 40), (screen_x + 40, self.y),
                (screen_x + 20, self.y + 30), (screen_x, self.y + 10),
                (screen_x + 10, self.y + 40)
            ])
            # Branches
            pygame.draw.polygon(screen, (40, 25, 18), [
                (screen_x + 25, self.y + 25), (screen_x + 60, self.y - 15), (screen_x + 55, self.y + 5)
            ])
            pygame.draw.polygon(screen, (40, 25, 18), [
                (screen_x + 10, self.y + 20), (screen_x - 25, self.y - 20), (screen_x - 15, self.y + 5)
            ])
            # Fog at base
            fog_surf = pygame.Surface((60, 30), pygame.SRCALPHA)
            pygame.draw.ellipse(fog_surf, (100, 100, 120, 60), (0, 0, 60, 30))
            screen.blit(fog_surf, (screen_x - 10, self.y + 80))

        elif self.dec_type == 'mushroom':
            # Stem
            pygame.draw.rect(screen, (240, 235, 220), (screen_x + 6, self.y + 10, 10, 18))
            pygame.draw.rect(screen, (220, 215, 200), (screen_x + 8, self.y + 10, 3, 18))
            # Cap
            pygame.draw.ellipse(screen, (200, 40, 40), (screen_x - 2, self.y - 2, 26, 16))
            pygame.draw.ellipse(screen, (220, 60, 60), (screen_x, self.y, 22, 12))
            # Spots
            pygame.draw.circle(screen, WHITE, (screen_x + 6, self.y + 4), 4)
            pygame.draw.circle(screen, WHITE, (screen_x + 16, self.y + 5), 3)
            pygame.draw.circle(screen, WHITE, (screen_x + 11, self.y + 2), 2)

        elif self.dec_type == 'goal_flag':
            # Pole with spiral
            pygame.draw.rect(screen, (180, 180, 190), (screen_x + 18, self.y - 220, 12, 270))
            for i in range(0, 270, 20):
                pygame.draw.arc(screen, (150, 150, 160), 
                              (screen_x + 16, self.y - 220 + i, 16, 20), 0, math.pi, 2)
            # Flag
            wave = math.sin(pygame.time.get_ticks() * 0.004) * 5
            flag_points = [
                (screen_x + 30, self.y - 210),
                (screen_x + 110 + wave, self.y - 180),
                (screen_x + 105 + wave * 0.5, self.y - 170),
                (screen_x + 30, self.y - 145)
            ]
            pygame.draw.polygon(screen, GOLD, flag_points)
            pygame.draw.polygon(screen, (200, 170, 50), flag_points, 3)
            # Star ornament
            pygame.draw.circle(screen, YELLOW, (screen_x + 24, self.y - 230), 18)
            pygame.draw.circle(screen, GOLD, (screen_x + 24, self.y - 230), 14)
            pygame.draw.circle(screen, (255, 250, 200), (screen_x + 24, self.y - 230), 8)
            # Platform base
            pygame.draw.rect(screen, (100, 100, 110), (screen_x, self.y + 40, 50, 15), border_radius=3)


class Level:
    """A scrolling Mario-style level with multiple areas."""

    def __init__(self, level_num=1):
        self.level_num = level_num
        self.platforms = []
        self.decorations = []
        self.collectibles = []
        self.hazards = []
        self.enemy_spawns = []
        self.goal_x = 0
        self.has_boss = False
        self.boss_triggered = False
        
        # Story areas - (start_x, end_x, area_name, subtitle)
        self.story_areas = []

        # Story intro triggers - set of area indices already shown
        self.shown_story_intros = set()

        # Cutscene triggers - (x_position, cutscene_data)
        self.cutscene_triggers = []
        self.triggered_cutscenes = set()

        # Checkpoint system - (x_position, y_position, name)
        self.checkpoints = []
        self.checkpoint_reached = set()  # Set of checkpoint indices reached

        self.create_level()

    def create_level(self):
        """Create the level based on level number."""
        if self.level_num == 1:
            self._create_level_1()
        else:
            self._create_level_2()

    def _create_level_1(self):
        """Level 1: The Sorcerer's Stone - Journey through Year One!"""
        ground_y = SCREEN_HEIGHT - PLATFORM_HEIGHT

        # ================================================================
        # STORY AREAS - Define narrative sections
        # ================================================================
        self.story_areas = [
            (0, 800, "PRIVET DRIVE", "Escape the Dursleys"),
            (800, 1800, "PLATFORM 9¾", "Catch the Hogwarts Express"),
            (1800, 3200, "HOGWARTS GROUNDS", "First Year Adventures"),
            (3200, 4200, "FORBIDDEN CORRIDOR", "Beware of Fluffy"),
            (4200, 5200, "THROUGH THE TRAPDOOR", "Devil's Snare & Flying Keys"),
            (5200, 5800, "GIANT CHESS", "The Ultimate Challenge"),
            (5800, 7000, "THE FINAL CHAMBER", "Confront Quirrell"),
        ]

        # Checkpoints at each major area transition
        self.checkpoints = [
            (100, ground_y - 60, "Start"),
            (1500, ground_y - 60, "Platform 9¾"),
            (2500, ground_y - 60, "Hogwarts Grounds"),
            (3900, ground_y - 60, "Forbidden Corridor"),
            (4800, ground_y - 60, "Trapdoor"),
            (5700, ground_y - 60, "Final Chamber"),
        ]

        # ================================================================
        # GROUND LAYOUT - Story-driven sections with gaps
        # ================================================================
        # AREA 1: Privet Drive (0-800)
        self.platforms.append(Platform(0, ground_y, 800, PLATFORM_HEIGHT, 'brick'))
        # AREA 2: Platform 9¾ & Hogwarts Express (800-1800)
        self.platforms.append(Platform(900, ground_y, 400, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(1400, ground_y, 400, PLATFORM_HEIGHT, 'wood'))  # Train
        # AREA 3: Hogwarts Grounds & Quidditch (1800-3200)
        self.platforms.append(Platform(1900, ground_y, 500, PLATFORM_HEIGHT, 'grass'))
        self.platforms.append(Platform(2500, ground_y, 400, PLATFORM_HEIGHT, 'grass'))
        self.platforms.append(Platform(3000, ground_y, 300, PLATFORM_HEIGHT, 'grass'))
        # AREA 4: Forbidden Corridor - Fluffy (3200-4200)
        self.platforms.append(Platform(3400, ground_y, 400, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(3900, ground_y, 350, PLATFORM_HEIGHT, 'stone'))
        # AREA 5: Through the Trapdoor - Challenges (4200-5800)
        self.platforms.append(Platform(4350, ground_y, 350, PLATFORM_HEIGHT, 'dark'))  # Devil's Snare
        self.platforms.append(Platform(4800, ground_y, 400, PLATFORM_HEIGHT, 'stone'))  # Flying Keys
        self.platforms.append(Platform(5300, ground_y, 300, PLATFORM_HEIGHT, 'stone'))  # Chess
        # AREA 6: The Final Chamber (5800-6800)
        self.platforms.append(Platform(5700, ground_y, 300, PLATFORM_HEIGHT, 'dark'))
        self.platforms.append(Platform(6100, ground_y, 700, PLATFORM_HEIGHT, 'dark'))

        # ================================================================
        # AREA 1: PRIVET DRIVE - Escape from the Dursleys (0-800)
        # "The cupboard under the stairs"
        # ================================================================
        # Suburban house platforms (Dursley's house)
        self.platforms.append(Platform(100, ground_y - 80, 120, PLATFORM_HEIGHT, 'brick'))
        self.platforms.append(Platform(280, ground_y - 150, 100, PLATFORM_HEIGHT, 'brick'))
        self.platforms.append(Platform(420, ground_y - 80, 100, PLATFORM_HEIGHT, 'brick'))
        self.platforms.append(Platform(580, ground_y - 130, 120, PLATFORM_HEIGHT, 'brick'))
        
        # Hogwarts letters floating down (coins represent letters)
        for x in [150, 220, 310, 380, 460, 530, 620, 700]:
            self.collectibles.append(Collectible(x, ground_y - 200 + (x % 50), 'coin'))
        
        # Dursley "obstacles" - moved back to give player space to learn controls
        self.enemy_spawns.append((600, ground_y - ENEMY_HEIGHT, 'walker'))
        self.enemy_spawns.append((750, ground_y - ENEMY_HEIGHT, 'walker'))
        
        # Decorations - suburban feel
        self.decorations.append(Decoration(50, ground_y - 65, 'tree'))
        self.decorations.append(Decoration(200, ground_y - 35, 'torch'))  # Streetlight
        self.decorations.append(Decoration(450, ground_y - 65, 'tree'))
        self.decorations.append(Decoration(700, ground_y - 35, 'torch'))

        # ================================================================
        # AREA 2: PLATFORM 9¾ & HOGWARTS EXPRESS (800-1800)
        # "The train leaving at eleven o'clock"
        # ================================================================
        # Gap to platform 9¾ (running through the barrier!)
        self.platforms.append(Platform(820, ground_y - 60, 80, PLATFORM_HEIGHT, 'brick'))
        
        # Train car platforms (the Hogwarts Express!)
        self.platforms.append(Platform(1000, ground_y - 100, 140, PLATFORM_HEIGHT, 'wood'))
        self.platforms.append(Platform(1180, ground_y - 160, 120, PLATFORM_HEIGHT, 'wood'))
        self.platforms.append(Platform(1340, ground_y - 100, 100, PLATFORM_HEIGHT, 'wood'))
        
        # High platform - Trolley witch's treats!
        self.platforms.append(Platform(1100, ground_y - 260, 100, PLATFORM_HEIGHT, 'wood'))
        self.collectibles.append(Collectible(1130, ground_y - 300, 'health'))  # Chocolate Frog!
        
        # Coins on the train (Bertie Bott's beans!)
        for x in [1020, 1100, 1200, 1280, 1360, 1440, 1520, 1600]:
            self.collectibles.append(Collectible(x, ground_y - 130, 'coin'))
        
        # Platform gap hazard
        self.hazards.append(Hazard(1305, ground_y + 5, 90, 'spikes'))  # Train gap danger
        
        # Enemies on train (Malfoy and friends!)
        self.enemy_spawns.append((1050, ground_y - ENEMY_HEIGHT, 'malfoy'))  # Draco!
        self.enemy_spawns.append((1400, ground_y - ENEMY_HEIGHT, 'walker'))  # Crabbe
        self.enemy_spawns.append((1200, ground_y - 260 - ENEMY_HEIGHT, 'walker'))  # Goyle
        
        self.decorations.append(Decoration(950, ground_y - 35, 'banner'))
        self.decorations.append(Decoration(1500, ground_y - 35, 'banner'))

        # ================================================================
        # AREA 3: HOGWARTS GROUNDS & QUIDDITCH (1800-3200)
        # "Welcome to Hogwarts" + First Quidditch Match
        # ================================================================
        # Gap between train and grounds
        self.platforms.append(Platform(1820, ground_y - 80, 90, PLATFORM_HEIGHT, 'stone'))
        
        # Castle exterior platforms
        self.platforms.append(Platform(1950, ground_y - 100, 130, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(2120, ground_y - 180, 140, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(2300, ground_y - 120, 100, PLATFORM_HEIGHT, 'stone'))
        
        # Quidditch pitch section - HIGH platforms like flying!
        self.platforms.append(Platform(2420, ground_y - 80, 80, PLATFORM_HEIGHT, 'wood'))
        self.platforms.append(Platform(2550, ground_y - 200, 100, 20, 'wood'))  # Goal hoop level
        self.platforms.append(Platform(2700, ground_y - 300, 120, 20, 'wood'))  # High flying
        self.platforms.append(Platform(2860, ground_y - 200, 100, 20, 'wood'))
        self.platforms.append(Platform(2950, ground_y - 100, 80, PLATFORM_HEIGHT, 'wood'))
        
        # Golden Snitch! (speed boost)
        self.collectibles.append(Collectible(2750, ground_y - 350, 'speed'))
        
        # Quidditch coins
        for x in [2000, 2150, 2340, 2580, 2730, 2890]:
            self.collectibles.append(Collectible(x, ground_y - 150, 'coin'))
        
        # Gap hazards
        self.hazards.append(Hazard(2405, ground_y + 5, 90, 'lava'))  # Lake below quidditch
        self.hazards.append(Hazard(2910, ground_y + 5, 80, 'lava'))
        
        # Flying enemies (Bludgers!)
        self.enemy_spawns.append((2000, ground_y - ENEMY_HEIGHT, 'walker'))
        self.enemy_spawns.append((2200, ground_y - ENEMY_HEIGHT, 'walker'))
        self.enemy_spawns.append((2600, ground_y - 270, 'flying'))  # Bludger!
        self.enemy_spawns.append((2800, ground_y - 350, 'flying'))  # Bludger!
        self.enemy_spawns.append((3050, ground_y - ENEMY_HEIGHT, 'walker'))
        
        # Castle decorations
        self.decorations.append(Decoration(1950, ground_y - 155, 'castle_tower'))
        self.decorations.append(Decoration(2400, ground_y - 35, 'banner'))  # Quidditch banner
        self.decorations.append(Decoration(2800, ground_y - 35, 'banner'))
        self.decorations.append(Decoration(3100, ground_y - 100, 'castle_tower'))

        # ================================================================
        # AREA 4: FORBIDDEN CORRIDOR - FLUFFY (3200-4200)
        # "The door on the right-hand side of the third-floor corridor"
        # ================================================================
        # Approach to forbidden corridor
        self.platforms.append(Platform(3150, ground_y - 80, 80, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(3250, ground_y - 140, 100, PLATFORM_HEIGHT, 'stone'))
        
        # Corridor platforms
        self.platforms.append(Platform(3450, ground_y - 100, 140, PLATFORM_HEIGHT, 'dark'))
        self.platforms.append(Platform(3620, ground_y - 170, 120, PLATFORM_HEIGHT, 'dark'))
        self.platforms.append(Platform(3780, ground_y - 100, 130, PLATFORM_HEIGHT, 'dark'))
        
        # Fluffy's lair - Fluffy the three-headed dog!
        self.enemy_spawns.append((3700, ground_y - ENEMY_HEIGHT - 20, 'fluffy'))  # FLUFFY!
        
        # Trapdoor platform
        self.platforms.append(Platform(3950, ground_y - 60, 100, PLATFORM_HEIGHT, 'wood'))
        
        # Gap - the trapdoor drop!
        self.hazards.append(Hazard(3305, ground_y + 5, 90, 'spikes'))
        self.hazards.append(Hazard(3810, ground_y + 5, 80, 'spikes'))
        
        # Coins in corridor
        for x in [3300, 3480, 3650, 3800, 3980]:
            self.collectibles.append(Collectible(x, ground_y - 120, 'coin'))
        
        # Health before challenges
        self.collectibles.append(Collectible(4000, ground_y - 100, 'health'))
        
        # Corridor enemies
        self.enemy_spawns.append((3500, ground_y - ENEMY_HEIGHT, 'walker'))
        self.enemy_spawns.append((3850, ground_y - ENEMY_HEIGHT, 'walker'))
        self.enemy_spawns.append((3600, ground_y - 240, 'flying'))
        
        # Dark atmosphere
        self.decorations.append(Decoration(3400, ground_y - 35, 'torch'))
        self.decorations.append(Decoration(3600, ground_y - 35, 'torch'))
        self.decorations.append(Decoration(3850, ground_y - 35, 'torch'))

        # ================================================================
        # AREA 5: THROUGH THE TRAPDOOR - The Challenges (4200-5800)
        # Devil's Snare → Flying Keys → Giant Chess
        # ================================================================
        
        # --- DEVIL'S SNARE (4200-4700) ---
        # "Relax! It's Devil's Snare!"
        # Vine-like platforms (wood = vines)
        self.platforms.append(Platform(4100, ground_y - 100, 80, 20, 'wood'))
        self.platforms.append(Platform(4200, ground_y - 180, 100, 20, 'wood'))
        self.platforms.append(Platform(4330, ground_y - 120, 80, 20, 'wood'))
        self.platforms.append(Platform(4450, ground_y - 200, 120, 20, 'wood'))
        self.platforms.append(Platform(4600, ground_y - 140, 100, 20, 'wood'))
        
        # Spike pit below (the snare!)
        self.hazards.append(Hazard(4260, ground_y + 5, 80, 'spikes'))
        self.hazards.append(Hazard(4710, ground_y + 5, 80, 'spikes'))
        
        # Devil's Snare enemies
        self.enemy_spawns.append((4400, ground_y - ENEMY_HEIGHT, 'devil_snare'))
        self.enemy_spawns.append((4550, ground_y - ENEMY_HEIGHT, 'devil_snare'))
        
        self.decorations.append(Decoration(4300, ground_y - 28, 'mushroom'))
        self.decorations.append(Decoration(4500, ground_y - 28, 'mushroom'))
        
        # --- FLYING KEYS (4700-5200) ---
        # "They're not birds, they're keys!"
        # High platforms with flying enemies (keys!)
        self.platforms.append(Platform(4750, ground_y - 80, 80, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(4870, ground_y - 180, 100, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(5020, ground_y - 280, 120, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(5180, ground_y - 180, 100, PLATFORM_HEIGHT, 'stone'))
        
        # Flying keys (the enchanted keys!) - reduced from 4 to 2 for fair difficulty
        self.enemy_spawns.append((4950, ground_y - 250, 'flying_key'))
        self.enemy_spawns.append((5100, ground_y - 300, 'flying_key'))

        # Health pickup before the flying keys section (fairness)
        self.collectibles.append(Collectible(4700, ground_y - 100, 'health'))

        # The right key! (damage boost)
        self.collectibles.append(Collectible(5080, ground_y - 340, 'damage'))
        
        # Coins among keys
        for x in [4800, 4920, 5060, 5200]:
            self.collectibles.append(Collectible(x, ground_y - 220, 'coin'))
        
        # --- GIANT CHESS (5200-5700) ---
        # "It's the only way... I've got to be taken"
        # Checkered pattern platforms
        self.platforms.append(Platform(5250, ground_y - 100, 100, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(5380, ground_y - 180, 100, PLATFORM_HEIGHT, 'dark'))
        self.platforms.append(Platform(5510, ground_y - 100, 100, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(5640, ground_y - 180, 100, PLATFORM_HEIGHT, 'dark'))
        
        # Giant Chess Pieces!
        self.enemy_spawns.append((5300, ground_y - ENEMY_HEIGHT - 15, 'chess_piece'))  # Rook
        self.enemy_spawns.append((5550, ground_y - ENEMY_HEIGHT - 15, 'chess_piece'))  # Knight
        self.enemy_spawns.append((5400, ground_y - 180 - ENEMY_HEIGHT, 'walker'))  # Pawn
        self.enemy_spawns.append((5680, ground_y - 180 - ENEMY_HEIGHT, 'walker'))  # Pawn
        
        # Gap hazard
        self.hazards.append(Hazard(5610, ground_y + 5, 80, 'spikes'))
        
        # Health before final chamber
        self.collectibles.append(Collectible(5700, ground_y - 130, 'health'))

        # ================================================================
        # AREA 6: THE FINAL CHAMBER - Mirror of Erised (5800-6800)
        # "The Stone! Use the Stone!"
        # ================================================================
        # Approach to mirror chamber
        self.platforms.append(Platform(5750, ground_y - 80, 80, PLATFORM_HEIGHT, 'dark'))
        self.platforms.append(Platform(5870, ground_y - 150, 100, PLATFORM_HEIGHT, 'dark'))
        self.platforms.append(Platform(6020, ground_y - 80, 90, PLATFORM_HEIGHT, 'dark'))
        
        # Final chamber - wide arena
        self.platforms.append(Platform(6150, ground_y - 150, 180, PLATFORM_HEIGHT, 'dark'))
        self.platforms.append(Platform(6380, ground_y - 250, 150, PLATFORM_HEIGHT, 'dark'))
        self.platforms.append(Platform(6200, ground_y - 350, 120, PLATFORM_HEIGHT, 'dark'))
        self.platforms.append(Platform(6550, ground_y - 150, 150, PLATFORM_HEIGHT, 'dark'))
        
        # Lava/fire hazards (Quirrell's fire!)
        self.hazards.append(Hazard(6010, ground_y + 5, 80, 'lava'))
        self.hazards.append(Hazard(6340, ground_y + 5, 100, 'lava'))
        
        # Final enemies (Quirrell's chamber!)
        self.enemy_spawns.append((6200, ground_y - ENEMY_HEIGHT, 'troll'))  # Troll guard
        self.enemy_spawns.append((6450, ground_y - 250 - ENEMY_HEIGHT, 'walker'))
        self.enemy_spawns.append((6300, ground_y - 400, 'flying'))
        self.enemy_spawns.append((6550, ground_y - 320, 'flying'))
        # QUIRRELL - Final boss of Level 1!
        self.enemy_spawns.append((6650, ground_y - ENEMY_HEIGHT - 10, 'quirrell'))
        
        # Final coins
        for x in [6180, 6280, 6420, 6580]:
            self.collectibles.append(Collectible(x, ground_y - 180, 'coin'))
        
        # The Sorcerer's Stone! (speed + damage = ultimate power)
        self.collectibles.append(Collectible(6500, ground_y - 300, 'speed'))
        self.collectibles.append(Collectible(6300, ground_y - 400, 'damage'))
        
        # Atmospheric torches
        self.decorations.append(Decoration(5900, ground_y - 35, 'torch'))
        self.decorations.append(Decoration(6200, ground_y - 35, 'torch'))
        self.decorations.append(Decoration(6450, ground_y - 35, 'torch'))
        self.decorations.append(Decoration(6650, ground_y - 35, 'torch'))

        # GOAL - The Mirror of Erised!
        self.goal_x = 6750
        self.decorations.append(Decoration(6750, ground_y, 'goal_flag'))
        
        # ================================================================
        # CUTSCENE TRIGGERS - Key story moments
        # ================================================================
        self.cutscene_triggers = [
            # Meeting Hagrid
            (100, {
                'title': "The Boy Who Lived",
                'speaker': "Hagrid",
                'text': "Yer a wizard, Harry!",
                'subtext': "You've been accepted to Hogwarts School of Witchcraft and Wizardry!",
                'duration': 4000
            }),
            # Platform 9 3/4
            (850, {
                'title': "Platform 9¾",
                'speaker': "Mrs. Weasley",
                'text': "Best do it at a bit of a run if you're nervous!",
                'subtext': "Run straight through the barrier between platforms 9 and 10...",
                'duration': 3500
            }),
            # Hogwarts arrival
            (1850, {
                'title': "Welcome to Hogwarts",
                'speaker': "Professor McGonagall",
                'text': "The Sorting Ceremony will begin momentarily.",
                'subtext': "Your house will be like your family while you're here.",
                'duration': 3500
            }),
            # Forbidden corridor warning
            (3250, {
                'title': "Warning!",
                'speaker': "Dumbledore",
                'text': "The third-floor corridor is out of bounds...",
                'subtext': "...to everyone who does not wish to die a most painful death.",
                'duration': 4000
            }),
            # Fluffy encounter
            (3650, {
                'title': "Fluffy",
                'speaker': "Hermione",
                'text': "It's standing on a trapdoor!",
                'subtext': "It's guarding something. We need to find a way past!",
                'duration': 3000
            }),
            # Final confrontation
            (6500, {
                'title': "The Final Chamber",
                'speaker': "Quirrell",
                'text': "I wondered whether I'd be meeting you here, Potter.",
                'subtext': "The Stone... give me the Stone!",
                'duration': 4000
            }),
        ]

    def _create_level_2(self):
        """Level 2: Dark Dungeons - Harder with BOSS FIGHT!"""
        ground_y = SCREEN_HEIGHT - PLATFORM_HEIGHT
        self.has_boss = True  # Enable boss fight!

        # Ground with MANY gaps (harder than level 1!)
        self.platforms.append(Platform(0, ground_y, 400, PLATFORM_HEIGHT, 'dark'))
        # GAP 1: Lava pit
        self.platforms.append(Platform(520, ground_y, 300, PLATFORM_HEIGHT, 'dark'))
        # GAP 2: Spike pit  
        self.platforms.append(Platform(950, ground_y, 350, PLATFORM_HEIGHT, 'dark'))
        # GAP 3: Double lava
        self.platforms.append(Platform(1500, ground_y, 300, PLATFORM_HEIGHT, 'dark'))
        # GAP 4: Long spike pit
        self.platforms.append(Platform(2000, ground_y, 400, PLATFORM_HEIGHT, 'dark'))
        # GAP 5: Lava before boss
        self.platforms.append(Platform(2600, ground_y, 300, PLATFORM_HEIGHT, 'dark'))
        # BOSS ARENA - Large solid ground
        self.platforms.append(Platform(3100, ground_y, 900, PLATFORM_HEIGHT, 'dark'))

        # ============================================
        # HAZARDS - Deadly gaps!
        # ============================================
        self.hazards.append(Hazard(410, ground_y + 5, 100, 'lava'))
        self.hazards.append(Hazard(830, ground_y - 5, 110, 'spikes'))
        self.hazards.append(Hazard(1310, ground_y + 5, 80, 'lava'))
        self.hazards.append(Hazard(1400, ground_y + 5, 90, 'lava'))
        self.hazards.append(Hazard(1810, ground_y - 5, 180, 'spikes'))
        self.hazards.append(Hazard(2410, ground_y + 5, 80, 'lava'))
        self.hazards.append(Hazard(2910, ground_y + 5, 180, 'lava'))

        # ============================================
        # AREA 1: Dungeon Entry (0 - 800)
        # ============================================
        self.platforms.append(Platform(350, ground_y - 80, 80, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(450, ground_y - 50, 80, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(150, ground_y - 100, 100, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(600, ground_y - 120, 100, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(750, ground_y - 80, 80, PLATFORM_HEIGHT, 'stone'))

        for x in [180, 380, 480, 630, 780]:
            self.collectibles.append(Collectible(x, ground_y - 140, 'coin'))

        self.enemy_spawns.append((200, ground_y - ENEMY_HEIGHT, 'walker'))
        self.enemy_spawns.append((550, ground_y - ENEMY_HEIGHT, 'walker'))
        self.enemy_spawns.append((700, ground_y - ENEMY_HEIGHT, 'walker'))

        for x in [100, 500, 800]:
            self.decorations.append(Decoration(x, ground_y - 35, 'torch'))

        # ============================================
        # AREA 2: Spike Gauntlet (800 - 1500)
        # ============================================
        # Platforms over spike pit
        self.platforms.append(Platform(840, ground_y - 100, 70, PLATFORM_HEIGHT, 'brick'))
        self.platforms.append(Platform(920, ground_y - 60, 60, PLATFORM_HEIGHT, 'brick'))

        # Tighter platforming
        for i in range(5):
            px = 980 + i * 100
            py = ground_y - 90 - (i % 2) * 70
            self.platforms.append(Platform(px, py, 80, PLATFORM_HEIGHT, 'brick'))
            self.collectibles.append(Collectible(px + 30, py - 40, 'coin'))

        self.collectibles.append(Collectible(1100, ground_y - 220, 'health'))

        self.enemy_spawns.append((1000, ground_y - ENEMY_HEIGHT, 'walker'))
        self.enemy_spawns.append((1150, ground_y - ENEMY_HEIGHT, 'tank'))
        self.enemy_spawns.append((1050, ground_y - 200, 'flying'))
        self.enemy_spawns.append((1250, ground_y - 250, 'flying'))

        # ============================================
        # AREA 3: Double Lava Hell (1500 - 2000)
        # ============================================
        # Platforms over double lava
        self.platforms.append(Platform(1300, ground_y - 120, 80, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(1380, ground_y - 80, 70, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(1460, ground_y - 60, 60, PLATFORM_HEIGHT, 'stone'))

        self.platforms.append(Platform(1550, ground_y - 100, 100, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(1700, ground_y - 180, 120, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(1860, ground_y - 120, 100, PLATFORM_HEIGHT, 'stone'))

        self.collectibles.append(Collectible(1750, ground_y - 230, 'speed'))
        
        self.enemy_spawns.append((1600, ground_y - ENEMY_HEIGHT, 'tank'))
        self.enemy_spawns.append((1800, ground_y - ENEMY_HEIGHT, 'tank'))
        self.enemy_spawns.append((1700, ground_y - 280, 'flying'))

        self.decorations.append(Decoration(1550, ground_y - 35, 'torch'))
        self.decorations.append(Decoration(1850, ground_y - 35, 'torch'))

        # ============================================
        # AREA 4: Final Gauntlet (2000 - 2900)
        # ============================================
        # Over long spike pit
        self.platforms.append(Platform(1800, ground_y - 80, 70, PLATFORM_HEIGHT, 'brick'))
        self.platforms.append(Platform(1880, ground_y - 120, 70, PLATFORM_HEIGHT, 'brick'))
        self.platforms.append(Platform(1960, ground_y - 80, 60, PLATFORM_HEIGHT, 'brick'))

        self.platforms.append(Platform(2050, ground_y - 150, 140, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(2250, ground_y - 220, 120, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(2450, ground_y - 150, 100, PLATFORM_HEIGHT, 'stone'))
        
        # Over lava before boss
        self.platforms.append(Platform(2550, ground_y - 100, 80, PLATFORM_HEIGHT, 'stone'))
        self.platforms.append(Platform(2650, ground_y - 60, 60, PLATFORM_HEIGHT, 'stone'))
        
        # Before boss: Health and damage boosts!
        self.collectibles.append(Collectible(2100, ground_y - 200, 'health'))
        self.collectibles.append(Collectible(2300, ground_y - 280, 'damage'))
        self.collectibles.append(Collectible(2500, ground_y - 200, 'health'))

        self.enemy_spawns.append((2100, ground_y - ENEMY_HEIGHT, 'tank'))
        self.enemy_spawns.append((2300, ground_y - ENEMY_HEIGHT, 'tank'))
        self.enemy_spawns.append((2200, ground_y - 300, 'flying'))
        self.enemy_spawns.append((2500, ground_y - 280, 'flying'))

        for x in [2100, 2350, 2600]:
            self.decorations.append(Decoration(x, ground_y - 35, 'torch'))

        # ============================================
        # AREA 5: BOSS ARENA (3100 - 3900)
        # ============================================
        # Large arena platforms for boss fight
        self.platforms.append(Platform(3200, ground_y - 150, 200, PLATFORM_HEIGHT, 'dark'))
        self.platforms.append(Platform(3500, ground_y - 250, 180, PLATFORM_HEIGHT, 'dark'))
        self.platforms.append(Platform(3300, ground_y - 350, 150, PLATFORM_HEIGHT, 'dark'))
        self.platforms.append(Platform(3700, ground_y - 150, 200, PLATFORM_HEIGHT, 'dark'))

        # Lava pits in arena for danger!
        self.hazards.append(Hazard(3150, ground_y + 5, 80, 'lava'))
        self.hazards.append(Hazard(3450, ground_y + 5, 80, 'lava'))
        self.hazards.append(Hazard(3750, ground_y + 5, 80, 'lava'))

        # Boss spawn marker (will spawn when player reaches this x)
        self.boss_spawn_x = 3200
        self.boss_spawn_y = ground_y - 150

        # Atmosphere
        for x in [3150, 3400, 3650, 3850]:
            self.decorations.append(Decoration(x, ground_y - 35, 'torch'))

        # Goal - only reachable after defeating boss
        self.goal_x = 3950
        self.decorations.append(Decoration(3950, ground_y, 'goal_flag'))

    def draw_background(self, screen, camera_x):
        """Draw enhanced parallax background with SMOOTH area transitions."""
        t = pygame.time.get_ticks()

        # Get current and nearby story areas for smooth blending
        current_area = self.get_story_area(camera_x) if self.story_areas else None
        area_name = current_area[0] if current_area else ""

        # Calculate transition blend factor for smooth area changes
        blend_factor = 1.0  # 1.0 = fully in current area
        next_area_name = ""
        transition_width = 200  # Pixels over which to blend

        # Find if we're near an area boundary
        for i, (start_x, end_x, name, subtitle) in enumerate(self.story_areas):
            # Check if near the end of current area (transitioning to next)
            if camera_x >= end_x - transition_width and camera_x < end_x:
                if i + 1 < len(self.story_areas):
                    next_area_name = self.story_areas[i + 1][2]
                    blend_factor = (end_x - camera_x) / transition_width
                    break
            # Check if near the start of current area (transitioning from previous)
            elif camera_x >= start_x and camera_x < start_x + transition_width:
                if i > 0:
                    next_area_name = self.story_areas[i - 1][2]
                    blend_factor = (camera_x - start_x) / transition_width
                    break

        # Determine if areas are indoor/outdoor
        def is_indoor_area(name):
            return any(x in name for x in ["FLUFFY", "TRAPDOOR", "CHESS", "FINAL", "QUIRRELL", "CORRIDOR", "CHAMBER"])

        is_indoor = is_indoor_area(area_name)
        next_is_indoor = is_indoor_area(next_area_name) if next_area_name else is_indoor
        is_great_hall = "GREAT" in area_name or "HALL" in area_name

        # Indoor transition factor (0 = fully outdoor, 1 = fully indoor)
        if is_indoor and next_is_indoor:
            indoor_factor = 1.0
        elif not is_indoor and not next_is_indoor:
            indoor_factor = 0.0
        elif is_indoor and not next_is_indoor:
            indoor_factor = blend_factor
        else:  # not is_indoor and next_is_indoor
            indoor_factor = 1.0 - blend_factor

        # Get color schemes for current and potentially blending areas
        def get_area_colors(name):
            if "PRIVET" in name:
                return (60, 30, 60), (100, 60, 70)
            elif "PLATFORM" in name:
                return (40, 35, 50), (70, 60, 80)
            elif "HOGWARTS GROUNDS" in name:
                return (15, 25, 55), (35, 50, 90)
            elif "FORBIDDEN" in name or "FLUFFY" in name:
                return (20, 15, 30), (40, 30, 45)
            elif "TRAPDOOR" in name or "CHESS" in name:
                return (10, 10, 20), (25, 20, 35)
            elif "FINAL" in name or "QUIRRELL" in name:
                return (30, 10, 15), (60, 25, 30)
            else:
                return (20, 30, 60), (50, 60, 100)

        # Get current and next area colors
        sky_top, sky_bottom = get_area_colors(area_name)

        # Blend colors if transitioning
        if next_area_name and blend_factor < 1.0:
            next_top, next_bottom = get_area_colors(next_area_name)
            sky_top = tuple(int(sky_top[i] * blend_factor + next_top[i] * (1 - blend_factor)) for i in range(3))
            sky_bottom = tuple(int(sky_bottom[i] * blend_factor + next_bottom[i] * (1 - blend_factor)) for i in range(3))

        if self.level_num != 1:
            sky_top = (15, 15, 25)
            sky_bottom = (35, 30, 50)

        # Draw gradient background
        for y_pos in range(0, SCREEN_HEIGHT, 2):
            ratio = y_pos / SCREEN_HEIGHT
            r = int(sky_top[0] + ratio * (sky_bottom[0] - sky_top[0]))
            g = int(sky_top[1] + ratio * (sky_bottom[1] - sky_top[1]))
            b = int(sky_top[2] + ratio * (sky_bottom[2] - sky_top[2]))
            pygame.draw.rect(screen, (r, g, b), (0, y_pos, SCREEN_WIDTH, 2))

        # SMOOTH TRANSITION between indoor/outdoor using alpha blending
        # Draw outdoor elements first (faded if transitioning to indoor)
        outdoor_alpha = int(255 * (1.0 - indoor_factor))
        indoor_alpha = int(255 * indoor_factor)

        # Create surfaces for blending
        if outdoor_alpha > 10:
            # OUTDOOR - Beautiful starry night sky
            # ============================================
            # STARS - Many more with varying sizes and brightness
            # ============================================
            star_offset = int(camera_x * 0.02) % 300
            random.seed(42)

            # Large bright stars (fewer)
            for i in range(15):
                star_x = (i * 150 + random.randint(0, 120) - star_offset) % (SCREEN_WIDTH + 400) - 200
                star_y = 20 + random.randint(0, 150)
                twinkle = abs(math.sin(t * 0.003 + i * 0.7)) * 0.4 + 0.6
                brightness = int(255 * twinkle)
                # Star with glow
                glow_color = (brightness // 3, brightness // 3, brightness // 2)
                pygame.draw.circle(screen, glow_color, (int(star_x), star_y), 4)
                pygame.draw.circle(screen, (brightness, brightness, brightness), (int(star_x), star_y), 2)
                # Cross sparkle on brightest stars
                if twinkle > 0.85:
                    pygame.draw.line(screen, (brightness, brightness, brightness),
                                   (int(star_x) - 4, star_y), (int(star_x) + 4, star_y), 1)
                    pygame.draw.line(screen, (brightness, brightness, brightness),
                                   (int(star_x), star_y - 4), (int(star_x), star_y + 4), 1)

            # Medium stars
            for i in range(40):
                star_x = (i * 60 + random.randint(0, 50) - star_offset * 0.8) % (SCREEN_WIDTH + 500) - 250
                star_y = 10 + random.randint(0, 200)
                twinkle = abs(math.sin(t * 0.004 + i * 1.3)) * 0.3 + 0.5
                brightness = int(220 * twinkle)
                pygame.draw.circle(screen, (brightness, brightness, brightness), (int(star_x), star_y), 1)

            # Tiny distant stars (many)
            for i in range(80):
                star_x = (i * 30 + random.randint(0, 25) - star_offset * 0.5) % (SCREEN_WIDTH + 600) - 300
                star_y = 5 + random.randint(0, 220)
                twinkle = abs(math.sin(t * 0.005 + i * 2.1)) * 0.4 + 0.3
                brightness = int(180 * twinkle)
                # Single pixel stars
                if 0 <= star_x < SCREEN_WIDTH and star_y < 250:
                    screen.set_at((int(star_x), star_y), (brightness, brightness, brightness))
            random.seed()

            # ============================================
            # MOON - Large and atmospheric with strong glow
            # ============================================
            moon_x = 680 - int(camera_x * 0.015)
            moon_y = 100
            moon_radius = 70  # Bigger moon!

            if -150 < moon_x < SCREEN_WIDTH + 150:
                # Outer atmospheric glow (large, soft)
                glow_surf = pygame.Surface((400, 400), pygame.SRCALPHA)
                glow_pulse = int(abs(math.sin(t * 0.0008)) * 15)

                # Multiple glow layers for atmosphere
                for i in range(8):
                    glow_r = 180 - i * 18
                    alpha = 12 + glow_pulse // 3 - i * 1
                    if alpha > 0:
                        pygame.draw.circle(glow_surf, (180, 200, 230, alpha), (200, 200), glow_r)

                # Warm inner glow
                for i in range(4):
                    inner_r = 100 - i * 15
                    alpha = 25 - i * 5
                    pygame.draw.circle(glow_surf, (220, 220, 200, alpha), (200, 200), inner_r)

                screen.blit(glow_surf, (moon_x - 200, moon_y - 200 + 50))

                # Moon body - gradient effect
                pygame.draw.circle(screen, (245, 245, 235), (moon_x, moon_y + 50), moon_radius)
                pygame.draw.circle(screen, (235, 235, 225), (moon_x - 10, moon_y + 45), moon_radius - 5)
                pygame.draw.circle(screen, (250, 250, 245), (moon_x - 20, moon_y + 35), moon_radius - 15)

                # Craters with depth
                crater_color = (215, 215, 200)
                crater_shadow = (200, 200, 185)
                pygame.draw.circle(screen, crater_color, (moon_x + 25, moon_y + 70), 12)
                pygame.draw.circle(screen, crater_shadow, (moon_x + 27, moon_y + 72), 9)
                pygame.draw.circle(screen, crater_color, (moon_x - 15, moon_y + 35), 10)
                pygame.draw.circle(screen, crater_shadow, (moon_x - 13, moon_y + 37), 7)
                pygame.draw.circle(screen, crater_color, (moon_x + 10, moon_y + 20), 6)
                pygame.draw.circle(screen, crater_color, (moon_x + 35, moon_y + 45), 5)
                pygame.draw.circle(screen, crater_color, (moon_x - 25, moon_y + 65), 8)

            # Distant Hogwarts castle silhouette
            castle_offset = int(camera_x * 0.08)
            self._draw_distant_castle(screen, castle_offset, t)

            # ============================================
            # MOUNTAINS - Detailed with snow caps and layers
            # ============================================
            self._draw_detailed_mountains(screen, camera_x, t)

        # INDOOR elements with smooth blending
        if indoor_alpha > 10:
            # Create semi-transparent surface for indoor elements
            if indoor_factor < 1.0:
                indoor_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                self._draw_stone_walls(indoor_surf, camera_x, t)
                self._draw_torches(indoor_surf, camera_x, t)

                if "CHESS" in area_name:
                    self._draw_chess_room_decor(indoor_surf, camera_x, t)
                elif "FINAL" in area_name or "QUIRRELL" in area_name:
                    self._draw_final_chamber_decor(indoor_surf, camera_x, t)

                # Apply alpha and blit
                indoor_surf.set_alpha(indoor_alpha)
                screen.blit(indoor_surf, (0, 0))
            else:
                # Fully indoor - draw directly
                self._draw_stone_walls(screen, camera_x, t)
                self._draw_torches(screen, camera_x, t)

                if "CHESS" in area_name:
                    self._draw_chess_room_decor(screen, camera_x, t)
                elif "FINAL" in area_name or "QUIRRELL" in area_name:
                    self._draw_final_chamber_decor(screen, camera_x, t)

        # Floating candles for indoor/Great Hall areas (with fade)
        if indoor_factor > 0.3:
            self._draw_floating_candles(screen, camera_x, t, alpha=int(255 * min(1.0, indoor_factor * 1.5)))

    def _draw_stone_walls(self, screen, camera_x, t):
        """Draw detailed stone wall background."""
        wall_offset = int(camera_x * 0.5) % 64

        # Stone colors with variation
        stone_base = (60, 55, 65)
        stone_dark = (40, 38, 48)
        stone_light = (80, 75, 88)
        mortar = (35, 32, 40)

        # Draw stone brick pattern
        for row in range(0, SCREEN_HEIGHT // 32 + 1):
            for col in range(-1, SCREEN_WIDTH // 64 + 2):
                bx = col * 64 - wall_offset + (32 if row % 2 else 0)
                by = row * 32

                # Skip if off screen
                if bx > SCREEN_WIDTH + 32 or bx < -64:
                    continue

                # Stone variation based on position
                variation = ((row * 7 + col * 13) % 20) - 10
                stone_color = tuple(max(0, min(255, c + variation)) for c in stone_base)

                # Main stone block
                pygame.draw.rect(screen, stone_color, (bx + 2, by + 2, 60, 28))

                # Shading - darker left/top edge
                pygame.draw.rect(screen, stone_dark, (bx + 2, by + 2, 60, 6))
                pygame.draw.rect(screen, stone_dark, (bx + 2, by + 2, 8, 28))

                # Highlight - lighter right/bottom
                pygame.draw.line(screen, stone_light, (bx + 58, by + 8), (bx + 58, by + 28), 2)
                pygame.draw.line(screen, stone_light, (bx + 10, by + 26), (bx + 58, by + 26), 2)

                # Stone texture - random cracks
                if (row + col) % 5 == 0:
                    crack_x = bx + 15 + (row * 3) % 30
                    pygame.draw.line(screen, stone_dark, (crack_x, by + 8),
                                   (crack_x + 8, by + 20), 1)
                if (row + col) % 7 == 0:
                    pygame.draw.circle(screen, stone_dark, (bx + 40, by + 15), 3)

        # Mortar lines
        for row in range(0, SCREEN_HEIGHT // 32 + 2):
            pygame.draw.line(screen, mortar, (0, row * 32), (SCREEN_WIDTH, row * 32), 2)

        # Moss/vine patches on walls
        moss_offset = int(camera_x * 0.4) % 200
        random.seed(123)
        for i in range(8):
            moss_x = (i * 180 - moss_offset) % (SCREEN_WIDTH + 200) - 100
            moss_y = 50 + random.randint(0, 150)
            moss_color = (30 + random.randint(0, 20), 60 + random.randint(0, 30), 25)

            # Hanging vines
            for v in range(random.randint(2, 5)):
                vine_x = moss_x + v * 8
                vine_len = 30 + random.randint(0, 40)
                wave = int(math.sin(t * 0.002 + v) * 3)
                pygame.draw.line(screen, moss_color, (vine_x, moss_y),
                               (vine_x + wave, moss_y + vine_len), 2)
                # Leaves
                for leaf in range(vine_len // 15):
                    ly = moss_y + leaf * 15 + 10
                    lx = vine_x + int(math.sin(t * 0.002 + leaf) * 2)
                    pygame.draw.ellipse(screen, moss_color, (lx - 3, ly, 6, 4))
        random.seed()

    def _draw_torches(self, screen, camera_x, t):
        """Draw wall-mounted torches with animated flames."""
        torch_spacing = 250
        torch_offset = int(camera_x) % torch_spacing

        for i in range(-1, SCREEN_WIDTH // torch_spacing + 2):
            tx = i * torch_spacing - torch_offset + 50
            ty = 120

            if tx < -50 or tx > SCREEN_WIDTH + 50:
                continue

            # Torch bracket (metal)
            pygame.draw.rect(screen, (60, 50, 45), (tx - 4, ty, 8, 30))
            pygame.draw.rect(screen, (80, 70, 60), (tx - 6, ty + 25, 12, 8))
            pygame.draw.rect(screen, (50, 40, 35), (tx - 4, ty, 8, 30), 1)

            # Torch handle
            pygame.draw.rect(screen, (100, 70, 45), (tx - 3, ty - 20, 6, 25))
            pygame.draw.rect(screen, (80, 55, 35), (tx - 3, ty - 20, 2, 25))

            # Animated flame
            flame_flicker = int(math.sin(t * 0.015 + i * 2) * 4)
            flame_colors = [
                (255, 200, 50),   # Yellow core
                (255, 150, 30),   # Orange mid
                (255, 80, 20),    # Orange-red outer
                (200, 50, 20),    # Red tip
            ]

            # Flame glow
            glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            glow_pulse = int(abs(math.sin(t * 0.01 + i)) * 30)
            pygame.draw.circle(glow_surf, (255, 150, 50, 40 + glow_pulse), (30, 30), 28)
            pygame.draw.circle(glow_surf, (255, 200, 100, 30 + glow_pulse), (30, 30), 20)
            screen.blit(glow_surf, (tx - 30, ty - 50))

            # Flame layers
            for j, color in enumerate(flame_colors):
                flame_h = 25 - j * 5 + flame_flicker
                flame_w = 12 - j * 2
                flame_y = ty - 20 - flame_h // 2
                wave = int(math.sin(t * 0.02 + j + i) * 2)

                pygame.draw.ellipse(screen, color,
                                  (tx - flame_w // 2 + wave, flame_y, flame_w, flame_h))

            # Sparks
            if int(t / 100 + i * 37) % 5 == 0:
                spark_x = tx + random.randint(-8, 8)
                spark_y = ty - 35 - random.randint(0, 15)
                pygame.draw.circle(screen, (255, 220, 100), (spark_x, spark_y), 2)

    def _draw_detailed_mountains(self, screen, camera_x, t):
        """Draw beautiful layered mountains with snow caps."""
        # Back layer - distant dark mountains
        hill_offset = int(camera_x * 0.08)
        back_color = (35, 40, 55)
        back_highlight = (45, 52, 70)

        for i in range(8):
            mx = i * 280 - (hill_offset % 280) - 140
            # Varied peak heights
            peak_heights = [180, 220, 160, 240, 190, 210, 170, 230]
            peak_h = peak_heights[i % len(peak_heights)]

            # Mountain silhouette
            points = [
                (mx, SCREEN_HEIGHT),
                (mx + 50, SCREEN_HEIGHT - peak_h * 0.6),
                (mx + 100, SCREEN_HEIGHT - peak_h * 0.85),
                (mx + 140, SCREEN_HEIGHT - peak_h),  # Peak
                (mx + 180, SCREEN_HEIGHT - peak_h * 0.8),
                (mx + 230, SCREEN_HEIGHT - peak_h * 0.5),
                (mx + 280, SCREEN_HEIGHT)
            ]
            pygame.draw.polygon(screen, back_color, points)

            # Subtle highlight on one side
            highlight_points = [
                (mx + 100, SCREEN_HEIGHT - peak_h * 0.85),
                (mx + 140, SCREEN_HEIGHT - peak_h),
                (mx + 145, SCREEN_HEIGHT - peak_h * 0.9),
                (mx + 105, SCREEN_HEIGHT - peak_h * 0.75)
            ]
            pygame.draw.polygon(screen, back_highlight, highlight_points)

        # Mid layer - main mountains with snow caps
        mid_offset = int(camera_x * 0.12)
        mid_color = (55, 60, 80)
        mid_shadow = (40, 45, 60)
        snow_color = (220, 225, 235)
        snow_shadow = (180, 185, 200)

        for i in range(6):
            mx = i * 350 - (mid_offset % 350) - 175
            # Taller peaks
            peak_heights = [260, 300, 240, 320, 280, 290]
            peak_h = peak_heights[i % len(peak_heights)]

            # Main mountain body
            left_base = mx - 20
            right_base = mx + 370
            peak_x = mx + 175

            # Left slope
            pygame.draw.polygon(screen, mid_color, [
                (left_base, SCREEN_HEIGHT),
                (peak_x, SCREEN_HEIGHT - peak_h),
                (peak_x, SCREEN_HEIGHT)
            ])
            # Right slope (slightly darker)
            pygame.draw.polygon(screen, mid_shadow, [
                (peak_x, SCREEN_HEIGHT - peak_h),
                (right_base, SCREEN_HEIGHT),
                (peak_x, SCREEN_HEIGHT)
            ])

            # Ridge details
            ridge_x = mx + 80
            ridge_h = peak_h * 0.7
            pygame.draw.polygon(screen, mid_shadow, [
                (ridge_x, SCREEN_HEIGHT - ridge_h),
                (ridge_x + 50, SCREEN_HEIGHT - ridge_h * 0.85),
                (ridge_x + 30, SCREEN_HEIGHT)
            ])

            # SNOW CAP
            snow_start_y = SCREEN_HEIGHT - peak_h
            snow_end_y = SCREEN_HEIGHT - peak_h * 0.65

            # Snow on peak
            pygame.draw.polygon(screen, snow_color, [
                (peak_x - 30, snow_end_y),
                (peak_x, snow_start_y),
                (peak_x + 25, snow_end_y + 10),
            ])
            # Snow shadow side
            pygame.draw.polygon(screen, snow_shadow, [
                (peak_x, snow_start_y),
                (peak_x + 25, snow_end_y + 10),
                (peak_x + 5, snow_end_y + 30)
            ])

            # Snow drip details
            for s in range(3):
                drip_x = peak_x - 20 + s * 18
                drip_y = snow_end_y + s * 8 + 5
                pygame.draw.polygon(screen, snow_color, [
                    (drip_x, drip_y),
                    (drip_x + 6, drip_y + 15),
                    (drip_x - 6, drip_y + 15)
                ])

        # Front layer - closer hills/foothills
        front_offset = int(camera_x * 0.2)
        front_color = (45, 50, 65)

        for i in range(10):
            hx = i * 200 - (front_offset % 200) - 100
            hill_h = 80 + (i % 4) * 25

            pygame.draw.polygon(screen, front_color, [
                (hx, SCREEN_HEIGHT),
                (hx + 50, SCREEN_HEIGHT - hill_h * 0.7),
                (hx + 100, SCREEN_HEIGHT - hill_h),
                (hx + 150, SCREEN_HEIGHT - hill_h * 0.6),
                (hx + 200, SCREEN_HEIGHT)
            ])

    def _draw_floating_candles(self, screen, camera_x, t, alpha=255):
        """Draw floating magical candles like in the Great Hall."""
        candle_offset = int(camera_x * 0.6) % 150
        random.seed(456)

        # Create surface if alpha needed
        if alpha < 255:
            candle_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            target = candle_surf
        else:
            target = screen

        for i in range(12):
            cx = (i * 120 - candle_offset) % (SCREEN_WIDTH + 200) - 100
            cy = 60 + random.randint(0, 100) + int(math.sin(t * 0.002 + i) * 8)

            if cx < -30 or cx > SCREEN_WIDTH + 30:
                continue

            # Candle body (cream colored)
            candle_h = 25 + random.randint(0, 15)
            pygame.draw.rect(target, (250, 245, 230), (cx - 4, cy, 8, candle_h))
            pygame.draw.rect(target, (230, 220, 200), (cx - 4, cy, 3, candle_h))
            pygame.draw.rect(target, (255, 250, 240), (cx + 1, cy, 2, candle_h))

            # Dripping wax
            for d in range(random.randint(1, 3)):
                drip_x = cx - 3 + d * 3
                drip_y = cy + candle_h - 5
                pygame.draw.ellipse(target, (250, 245, 230), (drip_x, drip_y, 4, 8))

            # Flame with glow
            flame_y = cy - 12
            flame_flicker = int(math.sin(t * 0.018 + i * 1.5) * 3)

            # Glow
            glow_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            glow_alpha = 50 + int(abs(math.sin(t * 0.012 + i)) * 30)
            pygame.draw.circle(glow_surf, (255, 200, 100, glow_alpha), (15, 15), 14)
            target.blit(glow_surf, (cx - 15, flame_y - 8))

            # Flame
            pygame.draw.ellipse(target, (255, 220, 100), (cx - 4 + flame_flicker, flame_y, 8, 14))
            pygame.draw.ellipse(target, (255, 250, 200), (cx - 2 + flame_flicker, flame_y + 4, 4, 8))

        random.seed()

        # Blit with alpha if using separate surface
        if alpha < 255:
            candle_surf.set_alpha(alpha)
            screen.blit(candle_surf, (0, 0))

    def _draw_distant_castle(self, screen, offset, t):
        """Draw distant Hogwarts castle silhouette."""
        castle_x = 500 - offset
        if castle_x < -300 or castle_x > SCREEN_WIDTH + 200:
            return

        castle_color = (35, 40, 55)
        castle_light = (45, 50, 65)

        # Main castle body
        pygame.draw.rect(screen, castle_color, (castle_x, 180, 200, 120))

        # Towers with pointed roofs
        tower_positions = [
            (castle_x - 20, 100, 40, 200),
            (castle_x + 50, 120, 35, 180),
            (castle_x + 120, 80, 45, 220),
            (castle_x + 180, 110, 38, 190),
        ]

        for tx, ty, tw, th in tower_positions:
            pygame.draw.rect(screen, castle_color, (tx, ty, tw, th))
            # Pointed roof
            pygame.draw.polygon(screen, castle_light, [
                (tx - 5, ty), (tx + tw // 2, ty - 40), (tx + tw + 5, ty)
            ])
            # Windows (glowing)
            for wy in range(ty + 20, ty + th - 30, 35):
                glow = int(abs(math.sin(t * 0.001 + tx * 0.1 + wy * 0.05)) * 50)
                pygame.draw.rect(screen, (180 + glow, 150 + glow, 80), (tx + tw // 2 - 4, wy, 8, 12))

        # Main tower (tallest, center)
        pygame.draw.rect(screen, castle_color, (castle_x + 80, 40, 50, 260))
        pygame.draw.polygon(screen, castle_light, [
            (castle_x + 75, 40), (castle_x + 105, -20), (castle_x + 135, 40)
        ])

    def _draw_chess_room_decor(self, screen, camera_x, t):
        """Draw chess room specific decorations."""
        # Checkered floor pattern hint in background
        check_offset = int(camera_x * 0.3) % 80
        for row in range(SCREEN_HEIGHT // 40, SCREEN_HEIGHT // 40 + 3):
            for col in range(-1, SCREEN_WIDTH // 40 + 2):
                cx = col * 40 - check_offset
                cy = SCREEN_HEIGHT - 100 + row * 20
                if (row + col) % 2 == 0:
                    pygame.draw.rect(screen, (30, 30, 35), (cx, cy, 40, 20))
                else:
                    pygame.draw.rect(screen, (50, 50, 55), (cx, cy, 40, 20))

    def _draw_final_chamber_decor(self, screen, camera_x, t):
        """Draw final chamber decorations - mirror, flames, etc."""
        # Eerie green/purple flames on sides
        for side in [0, 1]:
            fx = 50 if side == 0 else SCREEN_WIDTH - 50
            fy = 150

            # Flame pillar
            pygame.draw.rect(screen, (40, 35, 50), (fx - 15, fy, 30, 200))

            # Magical flames
            flame_h = 40 + int(math.sin(t * 0.01 + side * 3) * 10)
            colors = [(100, 0, 150), (80, 0, 120), (60, 0, 100)] if side == 0 else [(0, 150, 100), (0, 120, 80), (0, 100, 60)]

            for j, color in enumerate(colors):
                fh = flame_h - j * 10
                fw = 20 - j * 4
                wave = int(math.sin(t * 0.015 + j) * 4)
                pygame.draw.ellipse(screen, color, (fx - fw // 2 + wave, fy - fh, fw, fh))

    def draw(self, screen, camera_x):
        """Draw the level."""
        self.draw_background(screen, camera_x)

        # Decorations behind platforms
        for dec in self.decorations:
            dec.draw(screen, camera_x)

        # Platforms
        for platform in self.platforms:
            platform.draw(screen, camera_x)
        
        # Hazards (spikes, lava)
        for hazard in self.hazards:
            hazard.draw(screen, camera_x)

        # Collectibles
        for collectible in self.collectibles:
            collectible.draw(screen, camera_x)

    def update(self, dt):
        """Update level elements."""
        for collectible in self.collectibles:
            collectible.update(dt)
        for hazard in self.hazards:
            hazard.update(dt)

    def check_collectibles(self, players):
        """Check if players collected any items. Returns list of (player, type) tuples."""
        collected = []
        for player in players:
            if not player.is_alive():
                continue
            for collectible in self.collectibles:
                if not collectible.collected and player.rect.colliderect(collectible.rect):
                    collectible.collected = True
                    collected.append((player, collectible.collect_type))
        return collected

    def get_spawn_positions(self):
        """Get player spawn positions."""
        ground_y = SCREEN_HEIGHT - PLATFORM_HEIGHT
        return [
            (80, ground_y - PLAYER_HEIGHT - 5),
            (160, ground_y - PLAYER_HEIGHT - 5)
        ]

    def get_enemy_spawns(self):
        """Get all enemy spawn data."""
        return self.enemy_spawns

    def get_story_area(self, camera_x):
        """Get the current story area based on camera position."""
        for start_x, end_x, name, subtitle in self.story_areas:
            if start_x <= camera_x + SCREEN_WIDTH // 2 < end_x:
                return (name, subtitle)
        return None

    def get_story_area_index(self, camera_x):
        """Get the index of current story area."""
        for i, (start_x, end_x, name, subtitle) in enumerate(self.story_areas):
            if start_x <= camera_x + SCREEN_WIDTH // 2 < end_x:
                return i
        return -1

    def check_story_intro(self, camera_x):
        """Check if we should show a story intro for a new area."""
        area_idx = self.get_story_area_index(camera_x)
        if area_idx >= 0 and area_idx not in self.shown_story_intros:
            self.shown_story_intros.add(area_idx)
            area = self.story_areas[area_idx]
            # Return (name, subtitle, description)
            descriptions = self.get_area_descriptions()
            desc = descriptions.get(area[2], "Continue your adventure...")
            return (area[2], area[3], desc)
        return None

    def get_area_descriptions(self):
        """Get longer descriptions for each area."""
        return {
            "PRIVET DRIVE": "Harry has lived under the stairs at 4 Privet Drive.\nBut the Hogwarts letters are coming...\nEscape the Dursleys and find your destiny!",
            "PLATFORM 9¾": "Run through the barrier between platforms 9 and 10!\nThe Hogwarts Express awaits.\nWatch out for Malfoy and his cronies!",
            "HOGWARTS GROUNDS": "Welcome to Hogwarts School of Witchcraft and Wizardry!\nExplore the grounds and practice your skills.\nThe Quidditch pitch beckons...",
            "FORBIDDEN CORRIDOR": "The third-floor corridor is strictly forbidden!\nA three-headed dog named Fluffy guards the trapdoor.\nOnly music can calm the beast...",
            "THROUGH THE TRAPDOOR": "Devil's Snare, Flying Keys, and more challenges await!\nUse your wits and magic to survive.\nThe Philosopher's Stone is close...",
            "GIANT CHESS": "Professor McGonagall's enchanted chess set blocks your path!\nYou must play your way across...\nThis is wizard's chess!",
            "THE FINAL CHAMBER": "Professor Quirrell... or is it?\nThe Mirror of Erised holds the Stone.\nFace the Dark Lord's servant!"
        }

    def check_cutscene_trigger(self, player_x):
        """Check if player triggered a cutscene."""
        for i, (trigger_x, cutscene_data) in enumerate(self.cutscene_triggers):
            if i not in self.triggered_cutscenes:
                if player_x >= trigger_x:
                    self.triggered_cutscenes.add(i)
                    return cutscene_data
        return None

    def check_goal(self, players):
        """Check if any player reached the goal."""
        for player in players:
            if player.is_alive() and player.x >= self.goal_x:
                return True
        return False

    def check_checkpoints(self, players):
        """Check if players have reached any new checkpoints."""
        newly_reached = []
        for player in players:
            if player.is_alive():
                for i, (cp_x, cp_y, name) in enumerate(self.checkpoints):
                    if i not in self.checkpoint_reached and player.x >= cp_x:
                        self.checkpoint_reached.add(i)
                        newly_reached.append((i, name))
        return newly_reached

    def get_last_checkpoint(self):
        """Get the position of the last checkpoint reached."""
        if not self.checkpoint_reached:
            return None
        last_idx = max(self.checkpoint_reached)
        if last_idx < len(self.checkpoints):
            return self.checkpoints[last_idx]
        return None

    def draw_checkpoints(self, screen, camera_x):
        """Draw checkpoint flags."""
        for i, (cp_x, cp_y, name) in enumerate(self.checkpoints):
            screen_x = int(cp_x - camera_x)
            if screen_x < -50 or screen_x > SCREEN_WIDTH + 50:
                continue

            is_reached = i in self.checkpoint_reached

            # Flag pole
            pygame.draw.rect(screen, (150, 150, 160) if is_reached else (100, 100, 110),
                           (screen_x, cp_y - 80, 6, 90))

            # Flag
            flag_color = (50, 200, 50) if is_reached else (150, 50, 50)
            pygame.draw.polygon(screen, flag_color, [
                (screen_x + 6, cp_y - 80),
                (screen_x + 50, cp_y - 60),
                (screen_x + 6, cp_y - 40)
            ])

            # Glow effect for reached checkpoints
            if is_reached:
                glow_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (50, 255, 50, 80), (20, 20), 20)
                screen.blit(glow_surf, (screen_x - 15, cp_y - 70))


class Camera:
    """Camera that follows players - keeps everyone on screen."""

    def __init__(self):
        self.x = 0
        self.target_x = 0
        # Screen shake system
        self.shake_magnitude = 0
        self.shake_duration = 0
        self.shake_timer = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

    def shake(self, magnitude=5, duration=100):
        """Trigger screen shake effect."""
        self.shake_magnitude = magnitude
        self.shake_duration = duration
        self.shake_timer = duration

    def get_shake_offset(self):
        """Get current shake offset for rendering."""
        return (int(self.shake_offset_x), int(self.shake_offset_y))

    def update(self, players):
        """Update camera to keep all players visible."""
        if not players:
            return

        alive_players = [p for p in players if p.is_alive()]
        if not alive_players:
            return

        leftmost_x = min(p.x for p in alive_players)
        rightmost_x = max(p.x for p in alive_players)
        max_right_x = leftmost_x + MAX_COOP_GAP
        rightmost_for_camera = min(rightmost_x, max_right_x)

        center_x = (leftmost_x + rightmost_for_camera) / 2
        self.target_x = center_x - SCREEN_WIDTH // 2 + PLAYER_WIDTH // 2

        margin = COOP_MARGIN
        if leftmost_x - self.target_x < margin:
            self.target_x = leftmost_x - margin
        if rightmost_for_camera - self.target_x > SCREEN_WIDTH - margin - PLAYER_WIDTH:
            self.target_x = rightmost_for_camera - SCREEN_WIDTH + margin + PLAYER_WIDTH

        self.target_x = max(0, min(self.target_x, LEVEL_WIDTH - SCREEN_WIDTH))
        self.x += (self.target_x - self.x) * 0.2

        # Update screen shake using sine wave for smoother feel
        if self.shake_timer > 0:
            self.shake_timer -= 16  # Approximate dt
            progress = self.shake_timer / self.shake_duration if self.shake_duration > 0 else 0
            magnitude = self.shake_magnitude * progress
            # Use sine waves at different frequencies for organic shake
            elapsed = self.shake_duration - self.shake_timer
            self.shake_offset_x = magnitude * math.sin(elapsed * 0.05)
            self.shake_offset_y = magnitude * math.sin(elapsed * 0.07)  # Different freq for Y
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
