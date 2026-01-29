# Scrolling Level with Mario-style design - Enhanced Graphics

import pygame
import math
import random
from settings import *


class Platform:
    """A platform with improved graphics."""

    def __init__(self, x, y, width, height, style='stone'):
        self.rect = pygame.Rect(x, y, width, height)
        self.style = style
        self.tiles = []
        self._generate_tiles()

    def _generate_tiles(self):
        """Generate tile pattern for the platform."""
        tile_w = 32
        num_tiles = max(1, self.rect.width // tile_w)
        for i in range(num_tiles):
            # Slight variation in each tile
            variation = random.randint(-10, 10)
            self.tiles.append(variation)

    def draw(self, screen, camera_x):
        screen_x = self.rect.x - camera_x
        if screen_x + self.rect.width < 0 or screen_x > SCREEN_WIDTH:
            return

        tile_w = 32
        num_tiles = max(1, self.rect.width // tile_w)
        remainder = self.rect.width % tile_w

        if self.style == 'stone':
            base_color = (100, 100, 110)
            highlight = (130, 130, 140)
            shadow = (70, 70, 80)
        elif self.style == 'brick':
            base_color = (140, 80, 60)
            highlight = (170, 100, 75)
            shadow = (100, 55, 40)
        elif self.style == 'wood':
            base_color = (120, 80, 50)
            highlight = (150, 105, 70)
            shadow = (85, 55, 35)
        elif self.style == 'grass':
            base_color = (80, 60, 45)
            highlight = (100, 80, 55)
            shadow = (55, 40, 30)
        elif self.style == 'dark':
            base_color = (50, 50, 60)
            highlight = (70, 70, 85)
            shadow = (30, 30, 40)
        else:
            base_color = GRAY
            highlight = tuple(min(255, c + 30) for c in GRAY)
            shadow = tuple(max(0, c - 30) for c in GRAY)

        # Draw tiles
        for i in range(num_tiles):
            tx = screen_x + i * tile_w
            tw = tile_w if i < num_tiles - 1 or remainder == 0 else remainder + tile_w
            variation = self.tiles[i % len(self.tiles)] if self.tiles else 0
            
            # Tile base
            tile_color = tuple(max(0, min(255, c + variation)) for c in base_color)
            pygame.draw.rect(screen, tile_color, (tx, self.rect.y, tw, self.rect.height))
            
            # Brick pattern for brick/stone
            if self.style in ('stone', 'brick'):
                # Horizontal line
                pygame.draw.line(screen, shadow, (tx, self.rect.y + self.rect.height // 2),
                               (tx + tw, self.rect.y + self.rect.height // 2), 1)
                # Vertical lines (offset on alternate rows)
                if i % 2 == 0:
                    pygame.draw.line(screen, shadow, (tx + tw // 2, self.rect.y),
                                   (tx + tw // 2, self.rect.y + self.rect.height // 2), 1)
                else:
                    pygame.draw.line(screen, shadow, (tx + tw // 2, self.rect.y + self.rect.height // 2),
                                   (tx + tw // 2, self.rect.y + self.rect.height), 1)
            
            # Wood grain
            elif self.style == 'wood':
                for j in range(3):
                    gy = self.rect.y + 5 + j * 6
                    pygame.draw.line(screen, shadow, (tx + 2, gy), (tx + tw - 2, gy), 1)

        # Top highlight (grass top for grass style)
        if self.style == 'grass':
            pygame.draw.rect(screen, (60, 140, 60), (screen_x, self.rect.y, self.rect.width, 6))
            pygame.draw.rect(screen, (80, 180, 80), (screen_x, self.rect.y, self.rect.width, 3))
            # Grass blades
            for i in range(0, self.rect.width, 8):
                gx = screen_x + i + random.randint(0, 4)
                pygame.draw.line(screen, (50, 130, 50), (gx, self.rect.y), (gx + 2, self.rect.y - 4), 1)
        else:
            pygame.draw.rect(screen, highlight, (screen_x, self.rect.y, self.rect.width, 3))

            # Bottom shadow
        pygame.draw.rect(screen, shadow, (screen_x, self.rect.y + self.rect.height - 3, self.rect.width, 3))
        
        # Border
        pygame.draw.rect(screen, shadow, (screen_x, self.rect.y, self.rect.width, self.rect.height), 1)


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
            # Golden coin with shine
            pygame.draw.circle(screen, GOLD, (screen_x + 12, draw_y + 12), 12)
            pygame.draw.circle(screen, YELLOW, (screen_x + 12, draw_y + 12), 9)
            pygame.draw.circle(screen, (255, 250, 200), (screen_x + 9, draw_y + 8), 4)
            # Coin symbol
            pygame.draw.circle(screen, GOLD, (screen_x + 12, draw_y + 12), 5, 2)
            
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
            # Trunk with bark texture
            pygame.draw.rect(screen, (80, 50, 30), (screen_x + 8, self.y, 24, 65))
            pygame.draw.rect(screen, (60, 40, 25), (screen_x + 12, self.y, 4, 65))
            pygame.draw.rect(screen, (100, 65, 40), (screen_x + 24, self.y, 4, 65))
            # Foliage layers
            pygame.draw.circle(screen, (30, 100, 30), (screen_x + 20, self.y - 20), 38)
            pygame.draw.circle(screen, (40, 130, 40), (screen_x + 20, self.y - 10), 32)
            pygame.draw.circle(screen, (50, 150, 50), (screen_x + 20, self.y - 25), 25)
            pygame.draw.circle(screen, (70, 170, 70), (screen_x + 15, self.y - 30), 15)

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
            # Wall mount
            pygame.draw.rect(screen, (60, 50, 45), (screen_x - 2, self.y + 15, 14, 8))
            # Handle
            pygame.draw.rect(screen, (90, 60, 40), (screen_x, self.y, 10, 35))
            pygame.draw.rect(screen, (70, 45, 30), (screen_x + 2, self.y, 3, 35))
            # Flame animation
            flicker = math.sin(pygame.time.get_ticks() * 0.01) * 3
            pygame.draw.ellipse(screen, (255, 100, 30), (screen_x - 6, self.y - 28 + flicker, 22, 30))
            pygame.draw.ellipse(screen, ORANGE, (screen_x - 3, self.y - 22 + flicker, 16, 22))
            pygame.draw.ellipse(screen, YELLOW, (screen_x, self.y - 18 + flicker, 10, 16))
            pygame.draw.ellipse(screen, (255, 255, 200), (screen_x + 2, self.y - 14 + flicker, 6, 10))

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
        
        # Dursley "obstacles" (enemies as angry Dursleys/obstacles)
        self.enemy_spawns.append((300, ground_y - ENEMY_HEIGHT, 'walker'))
        self.enemy_spawns.append((550, ground_y - ENEMY_HEIGHT, 'walker'))
        
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
        
        # MANY flying keys (the enchanted keys!)
        self.enemy_spawns.append((4900, ground_y - 250, 'flying_key'))
        self.enemy_spawns.append((5050, ground_y - 350, 'flying_key'))
        self.enemy_spawns.append((5150, ground_y - 280, 'flying_key'))
        self.enemy_spawns.append((5000, ground_y - 180, 'flying_key'))
        
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
        """Draw enhanced parallax background with area-specific themes."""
        # Get current story area for theming
        current_area = self.get_story_area(camera_x) if self.story_areas else None
        area_name = current_area[0] if current_area else ""
        
        # Area-specific sky gradients for Level 1
        if self.level_num == 1:
            if "PRIVET" in area_name:
                # Suburban evening - orange/purple sunset
                sky_top = (60, 30, 60)
                sky_bottom = (100, 60, 70)
            elif "PLATFORM" in area_name:
                # Train station - steamy, warm
                sky_top = (40, 35, 50)
                sky_bottom = (70, 60, 80)
            elif "HOGWARTS GROUNDS" in area_name:
                # Beautiful Hogwarts night - deep blue
                sky_top = (15, 25, 55)
                sky_bottom = (35, 50, 90)
            elif "FORBIDDEN" in area_name or "FLUFFY" in area_name:
                # Creepy corridor - dark and ominous
                sky_top = (20, 15, 30)
                sky_bottom = (40, 30, 45)
            elif "TRAPDOOR" in area_name or "CHESS" in area_name:
                # Underground chambers - very dark
                sky_top = (10, 10, 20)
                sky_bottom = (25, 20, 35)
            elif "FINAL" in area_name or "QUIRRELL" in area_name:
                # Final chamber - fiery/dangerous
                sky_top = (30, 10, 15)
                sky_bottom = (60, 25, 30)
            else:
                sky_top = (20, 30, 60)
                sky_bottom = (50, 60, 100)
        else:
            sky_top = (15, 15, 25)
            sky_bottom = (35, 30, 50)

        for y in range(0, SCREEN_HEIGHT, 2):
            ratio = y / SCREEN_HEIGHT
            r = int(sky_top[0] + ratio * (sky_bottom[0] - sky_top[0]))
            g = int(sky_top[1] + ratio * (sky_bottom[1] - sky_top[1]))
            b = int(sky_top[2] + ratio * (sky_bottom[2] - sky_top[2]))
            pygame.draw.rect(screen, (r, g, b), (0, y, SCREEN_WIDTH, 2))

        # Stars (slow parallax)
        star_offset = int(camera_x * 0.03) % 200
        random.seed(42)  # Consistent star positions
        for i in range(25):
            star_x = (i * 120 + random.randint(0, 80) - star_offset) % (SCREEN_WIDTH + 400) - 200
            star_y = 20 + random.randint(0, 200)
            size = 1 + random.randint(0, 1)
            twinkle = abs(math.sin(pygame.time.get_ticks() * 0.002 + i)) * 0.5 + 0.5
            color = tuple(int(255 * twinkle) for _ in range(3))
            pygame.draw.circle(screen, color, (int(star_x), star_y), size)
        random.seed()

        # Moon with craters
        moon_x = 750 - int(camera_x * 0.02)
        if -80 < moon_x < SCREEN_WIDTH + 80:
            pygame.draw.circle(screen, (235, 235, 220), (moon_x, 90), 50)
            pygame.draw.circle(screen, (220, 220, 200), (moon_x - 15, 80), 42)
            # Craters
            pygame.draw.circle(screen, (210, 210, 195), (moon_x + 15, 100), 8)
            pygame.draw.circle(screen, (210, 210, 195), (moon_x - 5, 75), 6)

        # Distant mountains/hills (medium parallax)
        hill_offset = int(camera_x * 0.15)
        for layer in range(2):
            layer_offset = layer * 50
            color = (40 + layer * 15, 45 + layer * 15, 60 + layer * 15) if self.level_num == 1 else (30 + layer * 10, 30 + layer * 10, 40 + layer * 10)
            for i in range(12):
                hx = i * 220 - ((hill_offset + layer_offset) % 220) - 100
                height = 120 + (i % 4) * 35 + layer * 30
                pygame.draw.polygon(screen, color, [
                    (hx, SCREEN_HEIGHT),
                    (hx + 60, SCREEN_HEIGHT - height),
                    (hx + 120, SCREEN_HEIGHT - height + 20),
                    (hx + 180, SCREEN_HEIGHT - height - 10),
                    (hx + 240, SCREEN_HEIGHT)
                ])

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

        # Update screen shake
        if self.shake_timer > 0:
            self.shake_timer -= 16  # Approximate dt
            progress = self.shake_timer / self.shake_duration if self.shake_duration > 0 else 0
            magnitude = self.shake_magnitude * progress
            self.shake_offset_x = random.uniform(-magnitude, magnitude)
            self.shake_offset_y = random.uniform(-magnitude, magnitude)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
