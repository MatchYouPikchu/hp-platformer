# UI Components - Menus and HUD

import pygame
import math
import os
from settings import *
from characters import CHARACTERS, CHARACTER_ORDER


class UI:
    """Handles all UI rendering with cartoon polish."""

    def __init__(self):
        pygame.font.init()
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_title = pygame.font.Font(None, 96)

        # Character selection state
        self.selected_index = 0
        self.anim_timer = 0
        self.hover_offset = 0
        
        # Particle effects for menu
        self.particles = []
        for _ in range(30):
            self.particles.append({
                'x': pygame.time.get_ticks() % SCREEN_WIDTH,
                'y': pygame.time.get_ticks() % SCREEN_HEIGHT,
                'vx': (pygame.time.get_ticks() % 100) / 50 - 1,
                'vy': -0.5 - (pygame.time.get_ticks() % 100) / 100,
                'size': 2 + (pygame.time.get_ticks() % 4),
                'color': GOLD if pygame.time.get_ticks() % 3 == 0 else YELLOW
            })
        
        # Cache for character sprites
        self.char_sprites = {}
        self._load_character_sprites()

    def _load_character_sprites(self):
        """Load character sprites for selection screen."""
        for name in CHARACTER_ORDER:
            sheet_path = os.path.join(os.path.dirname(__file__), "assets", "characters", f"{name.lower()}_sheet.png")
            if os.path.exists(sheet_path):
                sheet = pygame.image.load(sheet_path).convert_alpha()
                # Get idle frame (first frame)
                frame = sheet.subsurface(pygame.Rect(0, 0, 48, 64)).copy()
                # Scale up for selection screen
                frame = pygame.transform.smoothscale(frame, (72, 96))
                self.char_sprites[name] = frame

    def _update_particles(self):
        """Update floating particles."""
        import random
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            if p['y'] < -10:
                p['y'] = SCREEN_HEIGHT + 10
                p['x'] = random.randint(0, SCREEN_WIDTH)
            if p['x'] < -10:
                p['x'] = SCREEN_WIDTH + 10
            elif p['x'] > SCREEN_WIDTH + 10:
                p['x'] = -10

    def _draw_particles(self, screen):
        """Draw floating magical particles."""
        for p in self.particles:
            pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), p['size'])
            # Glow
            glow_surf = pygame.Surface((p['size'] * 4, p['size'] * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*p['color'], 50), (p['size'] * 2, p['size'] * 2), p['size'] * 2)
            screen.blit(glow_surf, (int(p['x']) - p['size'] * 2, int(p['y']) - p['size'] * 2))

    def draw_text(self, screen, text, font, color, x, y, center=False):
        """Draw text on screen."""
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        screen.blit(surface, rect)
        return rect

    def draw_text_outlined(self, screen, text, font, color, outline_color, x, y, center=False):
        """Draw text with outline for better visibility."""
        # Draw outline
        for dx in [-2, 0, 2]:
            for dy in [-2, 0, 2]:
                if dx != 0 or dy != 0:
                    self.draw_text(screen, text, font, outline_color, x + dx, y + dy, center)
        # Draw main text
        return self.draw_text(screen, text, font, color, x, y, center)

    def draw_menu(self, screen):
        """Draw the main menu with magical theme."""
        self._update_particles()
        self.anim_timer += 1
        
        # Gradient background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(20 + ratio * 15)
            g = int(15 + ratio * 20)
            b = int(40 + ratio * 30)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Floating particles
        self._draw_particles(screen)
        
        # Magical glow behind title
        glow_size = 300 + int(math.sin(self.anim_timer * 0.03) * 20)
        glow_surf = pygame.Surface((glow_size * 2, glow_size), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (255, 215, 0, 30), (0, 0, glow_size * 2, glow_size))
        screen.blit(glow_surf, (SCREEN_WIDTH // 2 - glow_size, 100))
        
        # Title with glow effect
        title_y = 140 + int(math.sin(self.anim_timer * 0.02) * 5)
        self.draw_text_outlined(screen, "HARRY POTTER", self.font_title, GOLD, (100, 70, 0),
                               SCREEN_WIDTH // 2, title_y, center=True)
        self.draw_text_outlined(screen, "ADVENTURE", self.font_large, GOLD, (100, 70, 0),
                               SCREEN_WIDTH // 2, title_y + 80, center=True)

        # Subtitle with fade
        self.draw_text(screen, "Magical Platformer Adventure", self.font_medium, WHITE,
                      SCREEN_WIDTH // 2, 300, center=True)

        # Animated start prompt
        pulse = int(abs(math.sin(self.anim_timer * 0.05)) * 55) + 200
        start_color = (pulse, pulse, 0)
        self.draw_text_outlined(screen, "Press SPACE or ENTER to Start", self.font_medium, 
                               start_color, (60, 60, 0), SCREEN_WIDTH // 2, 420, center=True)

        # Decorative line
        line_y = 480
        pygame.draw.line(screen, GOLD, (SCREEN_WIDTH // 2 - 200, line_y), 
                        (SCREEN_WIDTH // 2 + 200, line_y), 2)
        pygame.draw.circle(screen, GOLD, (SCREEN_WIDTH // 2 - 200, line_y), 5)
        pygame.draw.circle(screen, GOLD, (SCREEN_WIDTH // 2 + 200, line_y), 5)
        pygame.draw.circle(screen, YELLOW, (SCREEN_WIDTH // 2, line_y), 8)
        
        # Controls boxes
        box_y = 530
        box_w, box_h = 280, 80
        
        # Player 1 box
        p1_box = pygame.Rect(SCREEN_WIDTH // 2 - box_w - 20, box_y, box_w, box_h)
        pygame.draw.rect(screen, (40, 60, 100), p1_box, border_radius=10)
        pygame.draw.rect(screen, LIGHT_BLUE, p1_box, 2, border_radius=10)
        self.draw_text(screen, "Player 1", self.font_medium, LIGHT_BLUE,
                      p1_box.centerx, box_y + 20, center=True)
        self.draw_text(screen, "WASD + Space + E", self.font_small, WHITE,
                      p1_box.centerx, box_y + 55, center=True)
        
        # Player 2 box
        p2_box = pygame.Rect(SCREEN_WIDTH // 2 + 20, box_y, box_w, box_h)
        pygame.draw.rect(screen, (80, 50, 40), p2_box, border_radius=10)
        pygame.draw.rect(screen, ORANGE, p2_box, 2, border_radius=10)
        self.draw_text(screen, "Player 2", self.font_medium, ORANGE,
                      p2_box.centerx, box_y + 20, center=True)
        self.draw_text(screen, "Arrows + Enter + RShift", self.font_small, WHITE,
                      p2_box.centerx, box_y + 55, center=True)

        # Footer
        self.draw_text(screen, "Press ESC to Quit", self.font_small, GRAY,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, center=True)

    def draw_mode_select(self, screen):
        """Draw the player mode selection screen."""
        self._update_particles()
        self.anim_timer += 1
        
        # Gradient background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(25 + ratio * 10)
            g = int(20 + ratio * 15)
            b = int(50 + ratio * 25)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Floating particles
        self._draw_particles(screen)
        
        # Title
        title_y = 120
        self.draw_text_outlined(screen, "SELECT MODE", self.font_title, GOLD, (100, 70, 0),
                               SCREEN_WIDTH // 2, title_y, center=True)
        
        # Mode boxes
        box_w, box_h = 320, 200
        box_y = 280
        gap = 80
        
        # Single Player Box
        p1_box = pygame.Rect(SCREEN_WIDTH // 2 - box_w - gap // 2, box_y, box_w, box_h)
        pygame.draw.rect(screen, (40, 60, 100), p1_box, border_radius=15)
        pygame.draw.rect(screen, LIGHT_BLUE, p1_box, 3, border_radius=15)
        
        # Player icon
        pygame.draw.circle(screen, LIGHT_BLUE, (p1_box.centerx, box_y + 60), 35)
        pygame.draw.circle(screen, (200, 220, 255), (p1_box.centerx, box_y + 60), 28)
        pygame.draw.circle(screen, LIGHT_BLUE, (p1_box.centerx, box_y + 45), 12)
        pygame.draw.ellipse(screen, LIGHT_BLUE, (p1_box.centerx - 20, box_y + 60, 40, 30))
        
        self.draw_text(screen, "SINGLE PLAYER", self.font_medium, WHITE,
                      p1_box.centerx, box_y + 120, center=True)
        
        pulse1 = int(abs(math.sin(self.anim_timer * 0.05)) * 55) + 200
        self.draw_text(screen, "Press [1]", self.font_large, (pulse1, pulse1, 0),
                      p1_box.centerx, box_y + 160, center=True)
        
        # Co-op Box
        p2_box = pygame.Rect(SCREEN_WIDTH // 2 + gap // 2, box_y, box_w, box_h)
        pygame.draw.rect(screen, (100, 60, 40), p2_box, border_radius=15)
        pygame.draw.rect(screen, ORANGE, p2_box, 3, border_radius=15)
        
        # Two player icons
        for offset in [-25, 25]:
            pygame.draw.circle(screen, ORANGE, (p2_box.centerx + offset, box_y + 60), 28)
            pygame.draw.circle(screen, (255, 220, 180), (p2_box.centerx + offset, box_y + 60), 22)
            pygame.draw.circle(screen, ORANGE, (p2_box.centerx + offset, box_y + 48), 10)
            pygame.draw.ellipse(screen, ORANGE, (p2_box.centerx + offset - 15, box_y + 60, 30, 25))
        
        self.draw_text(screen, "CO-OP (2 PLAYERS)", self.font_medium, WHITE,
                      p2_box.centerx, box_y + 120, center=True)
        
        pulse2 = int(abs(math.sin(self.anim_timer * 0.05 + 1)) * 55) + 200
        self.draw_text(screen, "Press [2]", self.font_large, (pulse2, pulse2, 0),
                      p2_box.centerx, box_y + 160, center=True)
        
        # Decorative line
        line_y = 520
        pygame.draw.line(screen, GOLD, (SCREEN_WIDTH // 2 - 250, line_y), 
                        (SCREEN_WIDTH // 2 + 250, line_y), 2)
        
        # Info text
        self.draw_text(screen, "Single player: Full keyboard control", self.font_small, GRAY,
                      SCREEN_WIDTH // 2, 560, center=True)
        self.draw_text(screen, "Co-op: Share keyboard with a friend!", self.font_small, GRAY,
                      SCREEN_WIDTH // 2, 590, center=True)
        
        # Footer
        self.draw_text(screen, "Press ESC to go back", self.font_small, GRAY,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, center=True)

    def draw_difficulty_select(self, screen):
        """Draw difficulty selection screen."""
        self._update_particles()
        self.anim_timer += 1

        # Gradient background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(25 + ratio * 10)
            g = int(20 + ratio * 15)
            b = int(50 + ratio * 25)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Floating particles
        self._draw_particles(screen)

        # Title
        title_y = 100
        self.draw_text_outlined(screen, "SELECT DIFFICULTY", self.font_title, GOLD, (100, 70, 0),
                               SCREEN_WIDTH // 2, title_y, center=True)

        # Difficulty boxes
        box_w, box_h = 280, 160
        box_y = 220
        gap = 30

        difficulties = [
            ('EASY', (50, 150, 50), GREEN, '[1]', 'More lives (5)', 'Enemies deal 75% damage'),
            ('NORMAL', (150, 150, 50), YELLOW, '[2]', 'Standard lives (3)', 'Balanced challenge'),
            ('HARD', (150, 50, 50), RED, '[3]', 'One life only!', 'Enemies deal 125% damage')
        ]

        total_w = box_w * 3 + gap * 2
        start_x = (SCREEN_WIDTH - total_w) // 2

        for i, (name, bg_color, border_color, key, line1, line2) in enumerate(difficulties):
            x = start_x + i * (box_w + gap)
            box = pygame.Rect(x, box_y, box_w, box_h)

            # Box background
            pygame.draw.rect(screen, bg_color, box, border_radius=15)
            pygame.draw.rect(screen, border_color, box, 3, border_radius=15)

            # Difficulty name
            self.draw_text(screen, name, self.font_large, WHITE, box.centerx, box_y + 35, center=True)

            # Description
            self.draw_text(screen, line1, self.font_small, WHITE, box.centerx, box_y + 80, center=True)
            self.draw_text(screen, line2, self.font_small, GRAY, box.centerx, box_y + 105, center=True)

            # Key prompt
            pulse = int(abs(math.sin(self.anim_timer * 0.05 + i)) * 55) + 200
            self.draw_text(screen, f"Press {key}", self.font_medium, (pulse, pulse, 0),
                          box.centerx, box_y + 140, center=True)

        # Decorative line
        line_y = 420
        pygame.draw.line(screen, GOLD, (SCREEN_WIDTH // 2 - 300, line_y),
                        (SCREEN_WIDTH // 2 + 300, line_y), 2)

        # Tip text
        self.draw_text(screen, "Tip: Start with Normal to learn the game!", self.font_small, GRAY,
                      SCREEN_WIDTH // 2, 460, center=True)

        # Footer
        self.draw_text(screen, "Press ESC to go back", self.font_small, GRAY,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, center=True)

    def draw_character_select(self, screen, state_manager):
        """Draw character selection screen with polished visuals."""
        self._update_particles()
        self.anim_timer += 1
        
        # Get selected character for theming
        selected_char = CHARACTERS[CHARACTER_ORDER[self.selected_index]]
        theme_color = selected_char.color
        
        # Dynamic Gradient background based on selection
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            # Blend between dark blue and theme color
            r = int(20 + ratio * (theme_color[0] * 0.3))
            g = int(20 + ratio * (theme_color[1] * 0.3))
            b = int(40 + ratio * (theme_color[2] * 0.3))
            pygame.draw.line(screen, (min(255, r), min(255, g), min(255, b)), (0, y), (SCREEN_WIDTH, y))
        
        # Spotlight effect behind selected character
        spotlight_x = SCREEN_WIDTH // 2
        spotlight_y = SCREEN_HEIGHT // 2 - 50
        
        # Rotating rays
        for i in range(12):
            angle = (self.anim_timer * 0.02) + (i * (math.pi * 2 / 12))
            end_x = spotlight_x + math.cos(angle) * 600
            end_y = spotlight_y + math.sin(angle) * 600
            
            # Triangle ray
            p1 = (spotlight_x, spotlight_y)
            p2 = (end_x + math.cos(angle + 0.2) * 50, end_y + math.sin(angle + 0.2) * 50)
            p3 = (end_x + math.cos(angle - 0.2) * 50, end_y + math.sin(angle - 0.2) * 50)
            
            ray_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(ray_surf, (*theme_color, 20), [p1, p2, p3])
            screen.blit(ray_surf, (0, 0))

        # Particles
        self._draw_particles(screen)
        
        # Title with player indicator
        if state_manager.num_players == 1:
            title = "CHOOSE YOUR HERO"
            title_color = (255, 215, 0)
        elif state_manager.player1_selecting:
            title = "PLAYER 1 SELECT"
            title_color = (100, 200, 255)
        else:
            title = "PLAYER 2 SELECT"
            title_color = (255, 150, 50)

        # Title Glow
        glow_size = 400 + math.sin(self.anim_timer * 0.1) * 20
        glow_surf = pygame.Surface((glow_size * 2, 100), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (*title_color, 40), (0, 0, glow_size * 2, 100))
        screen.blit(glow_surf, (SCREEN_WIDTH // 2 - glow_size, 20))

        self.draw_text_outlined(screen, title, self.font_title, title_color, (50, 30, 10),
                               SCREEN_WIDTH // 2, 45, center=True)

        # Show P1's selection if P2 is selecting (only in co-op)
        if state_manager.num_players == 2 and not state_manager.player1_selecting and state_manager.player1_character:
            p1_box = pygame.Rect(30, 30, 220, 60)
            pygame.draw.rect(screen, (30, 40, 60, 200), p1_box, border_radius=15)
            pygame.draw.rect(screen, (100, 200, 255), p1_box, 3, border_radius=15)
            self.draw_text(screen, "PLAYER 1", self.font_small, (100, 200, 255), p1_box.centerx, p1_box.y + 15, center=True)
            self.draw_text(screen, state_manager.player1_character, self.font_medium, WHITE, p1_box.centerx, p1_box.y + 38, center=True)

        # Draw character cards in arc layout
        card_width = 115
        card_height = 170
        total_width = card_width * 7 + 15 * 6
        start_x = (SCREEN_WIDTH - total_width) // 2
        base_y = 150

        for i, char_name in enumerate(CHARACTER_ORDER):
            char = CHARACTERS[char_name]
            x = start_x + i * (card_width + 15)
            
            # Focus effect
            is_selected = i == self.selected_index
            scale = 1.0
            
            if is_selected:
                y_offset = -20 + math.sin(self.anim_timer * 0.1) * 5
                scale = 1.1
            else:
                dist = abs(i - self.selected_index)
                y_offset = dist * 10
                scale = max(0.9, 1.0 - dist * 0.05)
            
            y = base_y + y_offset
            
            # Adjust dimensions for scale
            cw = int(card_width * scale)
            ch = int(card_height * scale)
            cx = x + (card_width - cw) // 2
            
            # Card Shadow
            shadow_rect = pygame.Rect(cx, y + 10, cw, ch)
            pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=12)

            # Card Background
            card_rect = pygame.Rect(cx, y, cw, ch)
            pygame.draw.rect(screen, (40, 40, 45), card_rect, border_radius=12)
            
            # Character Portrait Area
            portrait_h = int(ch * 0.65)
            portrait_rect = pygame.Rect(cx + 4, y + 4, cw - 8, portrait_h)
            pygame.draw.rect(screen, (20, 20, 25), portrait_rect, border_radius=8)
            
            # Draw Character Art
            # Use improved procedural portrait
            self._draw_character_portrait(screen, char_name, cx, y, cw, portrait_h)

            # Name Plate
            name_y = y + portrait_h + 10
            self.draw_text(screen, char_name, self.font_small if not is_selected else self.font_medium, 
                          WHITE if not is_selected else char.color,
                          cx + cw // 2, name_y + 15, center=True)
            
            # Selection Highlight
            if is_selected:
                pygame.draw.rect(screen, char.color, card_rect, 4, border_radius=12)
                # Outer glow
                glow_rect = card_rect.inflate(10, 10)
                pygame.draw.rect(screen, (*char.color, 100), glow_rect, 2, border_radius=15)
            else:
                pygame.draw.rect(screen, (80, 80, 80), card_rect, 2, border_radius=12)

        # Selected Character Detail Panel (Bottom)
        panel_y = base_y + card_height + 40
        panel_w = 800
        panel_h = 220
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        
        # Panel Glass Background
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (20, 20, 25, 230), (0, 0, panel_w, panel_h), border_radius=20)
        screen.blit(panel_surf, (panel_x, panel_y))
        
        # Border
        pygame.draw.rect(screen, theme_color, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=20)
        
        # Stats Layout
        # Left: Large Name & Description
        text_x = panel_x + 40
        self.draw_text_outlined(screen, selected_char.name.upper(), self.font_large, theme_color, (0, 0, 0),
                               text_x, panel_y + 30)
        
        type_text = f"Class: {selected_char.attack_type.title()}"
        if selected_char.can_fly: type_text += " | Flying"
        if selected_char.heals: type_text += " | Healer"
        
        self.draw_text(screen, type_text, self.font_medium, (200, 200, 200), text_x, panel_y + 70)
        
        # Ability Box
        ab_rect = pygame.Rect(text_x, panel_y + 110, 300, 80)
        pygame.draw.rect(screen, (40, 40, 50), ab_rect, border_radius=10)
        pygame.draw.rect(screen, selected_char.secondary_color, ab_rect, 2, border_radius=10)
        
        self.draw_text(screen, "SPECIAL ABILITY", self.font_small, selected_char.secondary_color, ab_rect.centerx, ab_rect.y + 15, center=True)
        self.draw_text(screen, selected_char.special_name, self.font_medium, WHITE, ab_rect.centerx, ab_rect.y + 38, center=True)
        self.draw_text(screen, selected_char.special_desc, self.font_small, (180, 180, 180), ab_rect.centerx, ab_rect.y + 60, center=True)

        # Right: Stats Bars
        stats_x = panel_x + 400
        stats_y = panel_y + 40
        
        self.draw_stat_bar(screen, "SPEED", selected_char.speed, 8, stats_x, stats_y, (100, 255, 255))
        self.draw_stat_bar(screen, "HEALTH", selected_char.health, 150, stats_x, stats_y + 50, (255, 100, 100))
        self.draw_stat_bar(screen, "DAMAGE", selected_char.damage, 50, stats_x, stats_y + 100, (255, 200, 50))

    def draw_stat_bar(self, screen, label, value, max_value, x, y, color):
        """Draw a sleek modern stat bar."""
        # Label
        self.draw_text(screen, label, self.font_small, (200, 200, 200), x, y)
        
        bar_x = x + 80
        bar_w = 280
        bar_h = 16
        
        # Track
        pygame.draw.rect(screen, (40, 40, 45), (bar_x, y, bar_w, bar_h), border_radius=8)
        
        # Fill
        fill_pct = min(1.0, value / max_value)
        fill_w = int(bar_w * fill_pct)
        
        if fill_w > 0:
            fill_rect = pygame.Rect(bar_x, y, fill_w, bar_h)
            pygame.draw.rect(screen, color, fill_rect, border_radius=8)
            # Shine
            pygame.draw.rect(screen, (255, 255, 255, 50), (bar_x, y, fill_w, bar_h // 2), border_radius=8)
            
        # Value text (right side)
        self.draw_text(screen, str(value), self.font_small, WHITE, bar_x + bar_w + 15, y)

    def draw_hud(self, screen, players, enemy_manager, camera, level_num=1, respawn_info=None, level=None):
        """Draw polished in-game HUD."""
        # Semi-transparent HUD background strips
        top_hud = pygame.Surface((SCREEN_WIDTH, 90), pygame.SRCALPHA)
        top_hud.fill((0, 0, 0, 100))
        screen.blit(top_hud, (0, 0))
        
        # Story Area Display (center top - prominent!)
        if level and hasattr(level, 'get_story_area'):
            story_area = level.get_story_area(camera.x)
            if story_area:
                area_name, subtitle = story_area
                # Area name banner
                banner_w = len(area_name) * 18 + 40
                banner_x = SCREEN_WIDTH // 2 - banner_w // 2
                pygame.draw.rect(screen, (40, 30, 60), (banner_x, 5, banner_w, 32), border_radius=8)
                pygame.draw.rect(screen, GOLD, (banner_x, 5, banner_w, 32), 2, border_radius=8)
                self.draw_text_outlined(screen, area_name, self.font_medium, GOLD, (80, 60, 20),
                                       SCREEN_WIDTH // 2, 12, center=True)
                # Subtitle
                self.draw_text(screen, subtitle, self.font_small, WHITE,
                              SCREEN_WIDTH // 2, 42, center=True)
        
        # Level indicator (left of center)
        level_text = f"Level {level_num}"
        pygame.draw.rect(screen, (60, 50, 30), (15, 68, 70, 22), border_radius=6)
        pygame.draw.rect(screen, GOLD, (15, 68, 70, 22), 2, border_radius=6)
        self.draw_text(screen, level_text, self.font_small, GOLD, 50, 72, center=True)
        
        # Respawn lives indicator (right side) with warning flash
        if respawn_info:
            respawns_left = respawn_info.get('respawns', 0)
            lives_x = SCREEN_WIDTH - 85

            # Flash effect when low on lives
            if respawns_left <= 1:
                flash = int(abs(math.sin(self.anim_timer * 0.15)) * 100) + 50
                bg_color = (flash, 30, 30)
                border_color = (255, flash, flash)
            else:
                bg_color = (50, 30, 30)
                border_color = RED

            pygame.draw.rect(screen, bg_color, (lives_x, 68, 70, 22), border_radius=6)
            pygame.draw.rect(screen, border_color, (lives_x, 68, 70, 22), 2, border_radius=6)

            # Show "LAST LIFE!" warning text
            if respawns_left <= 1:
                self.draw_text(screen, "LAST LIFE!", self.font_small, (255, 100, 100), lives_x + 35, 72, center=True)
            else:
                self.draw_text(screen, f"Lives: {respawns_left}", self.font_small, RED, lives_x + 35, 72, center=True)
        
        # Player 1 health (left side)
        if len(players) > 0:
            p1 = players[0]
            # Player frame
            p1_frame = pygame.Rect(15, 10, 180, 70)
            frame_color = (30, 50, 80, 180) if p1.is_alive() else (50, 30, 30, 180)
            border_color = LIGHT_BLUE if p1.is_alive() else (100, 50, 50)
            pygame.draw.rect(screen, frame_color, p1_frame, border_radius=10)
            pygame.draw.rect(screen, border_color, p1_frame, 2, border_radius=10)
            
            # Character sprite mini
            if p1.character.name in self.char_sprites:
                mini = pygame.transform.smoothscale(self.char_sprites[p1.character.name], (36, 48))
                if not p1.is_alive():
                    mini.set_alpha(100)
                screen.blit(mini, (20, 18))
            
            self.draw_text(screen, p1.character.name, self.font_small, LIGHT_BLUE, 65, 15)
            
            if p1.is_alive():
                self.draw_health_bar(screen, 65, 38, p1.health, p1.max_health, LIGHT_BLUE)
                # Special ready indicator with seconds remaining
                if p1.special_cooldown <= 0:
                    # Pulse effect when ready
                    pulse = int(abs(math.sin(self.anim_timer * 0.1)) * 50) + 205
                    pygame.draw.rect(screen, (pulse, int(pulse * 0.85), 0), (65, 62, 80, 14), border_radius=4)
                    self.draw_text(screen, "[E] READY!", self.font_small, BLACK, 105, 62, center=True)
                else:
                    cd_pct = p1.special_cooldown / SPECIAL_COOLDOWN
                    remaining_sec = p1.special_cooldown / 1000
                    pygame.draw.rect(screen, (40, 40, 50), (65, 62, 80, 14), border_radius=4)
                    pygame.draw.rect(screen, (80, 70, 30), (65, 62, int(80 * (1 - cd_pct)), 14), border_radius=4)
                    self.draw_text(screen, f"[E] {remaining_sec:.1f}s", self.font_small, GRAY, 105, 62, center=True)
            else:
                # Show respawn timer
                if respawn_info and respawn_info.get('respawns', 0) > 0:
                    timer = respawn_info.get('timers', [0, 0])[0]
                    delay = respawn_info.get('delay', 4000)
                    respawn_pct = min(1.0, timer / delay)
                    pygame.draw.rect(screen, (40, 40, 50), (65, 38, 110, 18), border_radius=4)
                    pygame.draw.rect(screen, (100, 150, 100), (65, 38, int(110 * respawn_pct), 18), border_radius=4)
                    self.draw_text(screen, "RESPAWNING...", self.font_small, WHITE, 120, 40, center=True)
                else:
                    self.draw_text(screen, "DEAD", self.font_small, RED, 120, 45, center=True)

        # Player 2 health (right side)
        if len(players) > 1:
            p2 = players[1]
            p2_frame = pygame.Rect(SCREEN_WIDTH - 195, 10, 180, 70)
            frame_color = (80, 50, 40, 180) if p2.is_alive() else (50, 30, 30, 180)
            border_color = ORANGE if p2.is_alive() else (100, 50, 50)
            pygame.draw.rect(screen, frame_color, p2_frame, border_radius=10)
            pygame.draw.rect(screen, border_color, p2_frame, 2, border_radius=10)
            
            # Character sprite mini
            if p2.character.name in self.char_sprites:
                mini = pygame.transform.smoothscale(self.char_sprites[p2.character.name], (36, 48))
                if not p2.is_alive():
                    mini.set_alpha(100)
                screen.blit(mini, (SCREEN_WIDTH - 55, 18))
            
            self.draw_text(screen, p2.character.name, self.font_small, ORANGE, SCREEN_WIDTH - 140, 15)
            
            if p2.is_alive():
                self.draw_health_bar(screen, SCREEN_WIDTH - 185, 38, p2.health, p2.max_health, ORANGE)
                # Special ready indicator with seconds remaining
                if p2.special_cooldown <= 0:
                    # Pulse effect when ready
                    pulse = int(abs(math.sin(self.anim_timer * 0.1)) * 50) + 205
                    pygame.draw.rect(screen, (pulse, int(pulse * 0.85), 0), (SCREEN_WIDTH - 185, 62, 80, 14), border_radius=4)
                    self.draw_text(screen, "[RS] READY!", self.font_small, BLACK, SCREEN_WIDTH - 145, 62, center=True)
                else:
                    cd_pct = p2.special_cooldown / SPECIAL_COOLDOWN
                    remaining_sec = p2.special_cooldown / 1000
                    pygame.draw.rect(screen, (40, 40, 50), (SCREEN_WIDTH - 185, 62, 80, 14), border_radius=4)
                    pygame.draw.rect(screen, (80, 70, 30), (SCREEN_WIDTH - 185, 62, int(80 * (1 - cd_pct)), 14), border_radius=4)
                    self.draw_text(screen, f"[RS] {remaining_sec:.1f}s", self.font_small, GRAY, SCREEN_WIDTH - 145, 62, center=True)
            else:
                # Show respawn timer
                if respawn_info and respawn_info.get('respawns', 0) > 0:
                    timer = respawn_info.get('timers', [0, 0])[1]
                    delay = respawn_info.get('delay', 4000)
                    respawn_pct = min(1.0, timer / delay)
                    pygame.draw.rect(screen, (40, 40, 50), (SCREEN_WIDTH - 185, 38, 110, 18), border_radius=4)
                    pygame.draw.rect(screen, (100, 150, 100), (SCREEN_WIDTH - 185, 38, int(110 * respawn_pct), 18), border_radius=4)
                    self.draw_text(screen, "RESPAWNING...", self.font_small, WHITE, SCREEN_WIDTH - 130, 40, center=True)
                else:
                    self.draw_text(screen, "DEAD", self.font_small, RED, SCREEN_WIDTH - 130, 45, center=True)

        # Score (center top) with fancy frame
        score_frame = pygame.Rect(SCREEN_WIDTH // 2 - 80, 8, 160, 35)
        pygame.draw.rect(screen, (50, 45, 30), score_frame, border_radius=8)
        pygame.draw.rect(screen, GOLD, score_frame, 2, border_radius=8)
        self.draw_text(screen, f"Score: {enemy_manager.score}", self.font_medium, GOLD,
                      SCREEN_WIDTH // 2, 25, center=True)

        # Progress bar with goal indicator
        from settings import LEVEL_WIDTH
        progress = min(1.0, camera.x / max(1, LEVEL_WIDTH - SCREEN_WIDTH))
        progress_width = 180
        progress_x = SCREEN_WIDTH // 2 - progress_width // 2
        
        pygame.draw.rect(screen, (30, 30, 40), (progress_x, 50, progress_width, 14), border_radius=5)
        fill_w = int(progress_width * progress)
        if fill_w > 0:
            pygame.draw.rect(screen, GREEN, (progress_x, 50, fill_w, 14), border_radius=5)
            pygame.draw.rect(screen, (150, 255, 150), (progress_x, 50, fill_w, 6), border_radius=5)
        pygame.draw.rect(screen, WHITE, (progress_x, 50, progress_width, 14), 1, border_radius=5)
        
        # Goal marker
        pygame.draw.polygon(screen, GOLD, [
            (progress_x + progress_width - 5, 47),
            (progress_x + progress_width + 5, 47),
            (progress_x + progress_width, 52)
        ])
        self.draw_text(screen, "GOAL", self.font_small, GOLD, progress_x + progress_width + 5, 55)

    def draw_health_bar(self, screen, x, y, health, max_health, color):
        """Draw a polished health bar with gradient."""
        bar_w = 110
        bar_h = 18
        
        # Background
        pygame.draw.rect(screen, (30, 30, 40), (x, y, bar_w, bar_h), border_radius=4)
        
        # Health fill
        health_ratio = max(0, health) / max(1, max_health)
        fill_width = int(bar_w * health_ratio)
        if fill_width > 0:
            # Main color
            pygame.draw.rect(screen, color, (x, y, fill_width, bar_h), border_radius=4)
            # Highlight (top half brighter)
            highlight = tuple(min(255, c + 70) for c in color)
            pygame.draw.rect(screen, highlight, (x, y, fill_width, bar_h // 2), border_radius=4)
        
        # Border
        pygame.draw.rect(screen, color, (x, y, bar_w, bar_h), 2, border_radius=4)
        
        # Health text centered
        health_text = f"{max(0, health)}/{max_health}"
        self.draw_text(screen, health_text, self.font_small, WHITE,
                      x + bar_w // 2, y + 1, center=True)

    def draw_game_over(self, screen, state_manager):
        """Draw polished game over screen."""
        self.anim_timer += 1
        
        # Dark red gradient overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(SCREEN_HEIGHT):
            alpha = int(180 + (y / SCREEN_HEIGHT) * 40)
            overlay.fill((40, 0, 0, min(220, alpha)), (0, y, SCREEN_WIDTH, 1))
        screen.blit(overlay, (0, 0))

        # Game Over text with dramatic effect
        shake = int(math.sin(self.anim_timer * 0.1) * 2) if self.anim_timer < 60 else 0
        self.draw_text_outlined(screen, "GAME OVER", self.font_title, RED, (80, 0, 0),
                               SCREEN_WIDTH // 2 + shake, 180, center=True)

        # Stats panel
        panel_w, panel_h = 400, 120
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = 280
        pygame.draw.rect(screen, (40, 30, 35), (panel_x, panel_y, panel_w, panel_h), border_radius=15)
        pygame.draw.rect(screen, RED, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=15)
        
        self.draw_text(screen, f"Final Score: {state_manager.final_score}",
                      self.font_medium, GOLD, SCREEN_WIDTH // 2, panel_y + 35, center=True)
        self.draw_text(screen, f"Progress: {state_manager.final_wave}%",
                      self.font_medium, WHITE, SCREEN_WIDTH // 2, panel_y + 80, center=True)

        # Option buttons
        btn_y = 450
        btn_w, btn_h = 300, 45
        
        # Restart button
        r_btn = pygame.Rect((SCREEN_WIDTH - btn_w) // 2, btn_y, btn_w, btn_h)
        pygame.draw.rect(screen, (40, 80, 40), r_btn, border_radius=10)
        pygame.draw.rect(screen, GREEN, r_btn, 2, border_radius=10)
        self.draw_text(screen, "[R] Quick Restart", self.font_medium, GREEN, r_btn.centerx, r_btn.centery, center=True)
        
        # New characters button
        c_btn = pygame.Rect((SCREEN_WIDTH - btn_w) // 2, btn_y + 60, btn_w, btn_h)
        pygame.draw.rect(screen, (40, 60, 80), c_btn, border_radius=10)
        pygame.draw.rect(screen, LIGHT_BLUE, c_btn, 2, border_radius=10)
        self.draw_text(screen, "[SPACE] New Characters", self.font_medium, LIGHT_BLUE, c_btn.centerx, c_btn.centery, center=True)
        
        # Menu button
        self.draw_text(screen, "[ESC] Main Menu", self.font_small, GRAY,
                      SCREEN_WIDTH // 2, btn_y + 130, center=True)

    def draw_pause(self, screen):
        """Draw polished pause overlay."""
        # Overlay with blur effect simulation
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 20, 40, 180))
        screen.blit(overlay, (0, 0))

        # Center panel
        panel_w, panel_h = 350, 230
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2
        
        pygame.draw.rect(screen, (40, 40, 60), (panel_x, panel_y, panel_w, panel_h), border_radius=20)
        pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=20)

        # Pause icon (two bars)
        icon_x = SCREEN_WIDTH // 2
        icon_y = panel_y + 50
        pygame.draw.rect(screen, WHITE, (icon_x - 25, icon_y - 20, 18, 50), border_radius=4)
        pygame.draw.rect(screen, WHITE, (icon_x + 7, icon_y - 20, 18, 50), border_radius=4)

        # Text
        self.draw_text(screen, "PAUSED", self.font_large, WHITE,
                      SCREEN_WIDTH // 2, panel_y + 100, center=True)
        self.draw_text(screen, "[P] or [SPACE] Resume", self.font_small, GRAY,
                      SCREEN_WIDTH // 2, panel_y + 145, center=True)
        self.draw_text(screen, "[ESC] or [Q] Main Menu", self.font_small, GRAY,
                      SCREEN_WIDTH // 2, panel_y + 170, center=True)

    def draw_victory(self, screen, state_manager):
        """Draw polished victory screen."""
        self.anim_timer += 1
        
        # Golden gradient overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(60 - ratio * 20)
            g = int(50 - ratio * 15)
            overlay.fill((r, g, 0, 200), (0, y, SCREEN_WIDTH, 1))
        screen.blit(overlay, (0, 0))

        # Sparkle particles
        import random
        for _ in range(3):
            px = random.randint(100, SCREEN_WIDTH - 100)
            py = random.randint(100, 500)
            size = random.randint(2, 5)
            pygame.draw.circle(screen, GOLD, (px, py), size)

        # Victory text with glow
        pulse = int(abs(math.sin(self.anim_timer * 0.05)) * 30) + 225
        glow_color = (pulse, int(pulse * 0.85), 0)
        self.draw_text_outlined(screen, "VICTORY!", self.font_title, glow_color, (100, 80, 0),
                               SCREEN_WIDTH // 2, 140, center=True)
        self.draw_text(screen, "You reached Hogwarts!", self.font_medium, WHITE,
                      SCREEN_WIDTH // 2, 220, center=True)

        # Trophy with animation
        trophy_x = SCREEN_WIDTH // 2
        trophy_y = 320 + int(math.sin(self.anim_timer * 0.04) * 5)
        
        # Trophy glow
        glow_surf = pygame.Surface((140, 100), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (255, 215, 0, 60), (0, 20, 140, 80))
        screen.blit(glow_surf, (trophy_x - 70, trophy_y - 30))
        
        # Trophy base
        pygame.draw.rect(screen, (180, 140, 30), (trophy_x - 35, trophy_y + 45, 70, 20), border_radius=3)
        pygame.draw.rect(screen, GOLD, (trophy_x - 25, trophy_y + 55, 50, 15), border_radius=3)
        # Trophy stem
        pygame.draw.rect(screen, GOLD, (trophy_x - 12, trophy_y + 20, 24, 30), border_radius=5)
        # Trophy cup
        pygame.draw.ellipse(screen, GOLD, (trophy_x - 45, trophy_y - 25, 90, 55))
        pygame.draw.ellipse(screen, YELLOW, (trophy_x - 35, trophy_y - 15, 70, 40))
        pygame.draw.ellipse(screen, (255, 250, 200), (trophy_x - 25, trophy_y - 5, 50, 25))
        # Star on trophy
        star_points = []
        for i in range(10):
            angle = (i / 10) * math.pi * 2 - math.pi / 2
            r = 12 if i % 2 == 0 else 6
            star_points.append((trophy_x + math.cos(angle) * r, trophy_y + 5 + math.sin(angle) * r))
        pygame.draw.polygon(screen, WHITE, star_points)

        # Score panel
        panel_w, panel_h = 300, 60
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = 420
        pygame.draw.rect(screen, (60, 50, 20), (panel_x, panel_y, panel_w, panel_h), border_radius=12)
        pygame.draw.rect(screen, GOLD, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=12)
        self.draw_text(screen, f"Final Score: {state_manager.final_score}",
                      self.font_medium, GOLD, SCREEN_WIDTH // 2, panel_y + 30, center=True)

        # Option buttons
        btn_y = 510
        btn_w, btn_h = 280, 40
        
        # Play again button
        r_btn = pygame.Rect((SCREEN_WIDTH - btn_w) // 2, btn_y, btn_w, btn_h)
        pygame.draw.rect(screen, (40, 80, 40), r_btn, border_radius=10)
        pygame.draw.rect(screen, GREEN, r_btn, 2, border_radius=10)
        self.draw_text(screen, "[R] Play Again", self.font_medium, GREEN, r_btn.centerx, r_btn.centery, center=True)
        
        # New characters button
        c_btn = pygame.Rect((SCREEN_WIDTH - btn_w) // 2, btn_y + 55, btn_w, btn_h)
        pygame.draw.rect(screen, (40, 60, 80), c_btn, border_radius=10)
        pygame.draw.rect(screen, LIGHT_BLUE, c_btn, 2, border_radius=10)
        self.draw_text(screen, "[SPACE] New Characters", self.font_medium, LIGHT_BLUE, c_btn.centerx, c_btn.centery, center=True)
        
        # Menu
        self.draw_text(screen, "[ESC] Main Menu", self.font_small, GRAY,
                      SCREEN_WIDTH // 2, btn_y + 115, center=True)

    def _draw_character_portrait(self, screen, name, x, y, w, h):
        """Draw a high-quality stylized character portrait."""
        cx, cy = x + w // 2, y + h // 2
        
        # Shadow
        pygame.draw.ellipse(screen, (0, 0, 0, 100), (cx - 25, cy + 20, 50, 15))

        if name == 'Harry':
            # Dynamic Pose Base
            pygame.draw.rect(screen, (160, 20, 40), (cx - 20, cy + 10, 40, 30), border_radius=8) # Robe body
            pygame.draw.circle(screen, (255, 215, 180), (cx, cy - 15), 22) # Head
            
            # Hair - messy and detailed
            hair_pts = [(cx-24, cy-20), (cx-15, cy-35), (cx, cy-38), (cx+18, cy-32), (cx+24, cy-18), 
                       (cx+22, cy-5), (cx+15, cy-15), (cx+10, cy-5), (cx, cy-12), (cx-10, cy-5), (cx-18, cy-12)]
            pygame.draw.polygon(screen, (20, 20, 20), hair_pts)
            
            # Glasses - thick round rims
            pygame.draw.circle(screen, (40, 40, 40), (cx - 8, cy - 12), 9, 3)
            pygame.draw.circle(screen, (40, 40, 40), (cx + 8, cy - 12), 9, 3)
            pygame.draw.line(screen, (40, 40, 40), (cx - 2, cy - 12), (cx + 2, cy - 12), 3)
            
            # Scar - vivid gold
            pygame.draw.lines(screen, (255, 215, 0), False, [(cx - 6, cy - 28), (cx - 2, cy - 22), (cx - 4, cy - 18)], 3)
            
            # Scarf
            pygame.draw.rect(screen, (180, 20, 40), (cx - 22, cy + 10, 44, 10), border_radius=5)
            for i in range(3):
                pygame.draw.rect(screen, (255, 215, 0), (cx - 15 + i*12, cy + 10, 6, 10))

        elif name == 'Ron':
            # Robe
            pygame.draw.rect(screen, (40, 40, 40), (cx - 20, cy + 12, 40, 30), border_radius=8)
            pygame.draw.circle(screen, (255, 220, 190), (cx, cy - 15), 21) # Head
            
            # Hair - messy orange
            pygame.draw.ellipse(screen, (255, 100, 20), (cx - 24, cy - 38, 48, 40))
            pygame.draw.ellipse(screen, (255, 100, 20), (cx - 26, cy - 25, 15, 25))
            pygame.draw.ellipse(screen, (255, 100, 20), (cx + 11, cy - 25, 15, 25))
            
            # Freckles
            for fx in [-12, -6, 6, 12]:
                pygame.draw.circle(screen, (200, 140, 100), (cx + fx, cy - 5), 1)
            
            # Sweater 'R'
            pygame.draw.rect(screen, (160, 60, 20), (cx - 22, cy + 10, 44, 25), border_radius=5)
            self.draw_text(screen, "R", self.font_small, (255, 200, 50), cx, cy + 22, center=True)

        elif name == 'Hermione':
            # Robe
            pygame.draw.rect(screen, (40, 40, 40), (cx - 18, cy + 12, 36, 30), border_radius=8)
            pygame.draw.circle(screen, (255, 215, 180), (cx, cy - 12), 20) # Head
            
            # Big bushy hair
            pygame.draw.circle(screen, (100, 60, 20), (cx, cy - 15), 32)
            pygame.draw.circle(screen, (255, 215, 180), (cx, cy - 12), 20) # Head redraw
            
            # Hair bangs
            pygame.draw.arc(screen, (100, 60, 20), (cx-20, cy-35, 40, 40), 0, 3.14, 8)
            
            # Tie
            pygame.draw.polygon(screen, (180, 20, 40), [(cx, cy+10), (cx-5, cy+25), (cx+5, cy+25)])
            pygame.draw.line(screen, (255, 215, 0), (cx-3, cy+18), (cx+3, cy+20), 2)

        elif name == 'Voldemort':
            # Aura
            s = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 255, 0, 30), (50, 50), 40)
            screen.blit(s, (cx-50, cy-50))
            
            # Robe - flowing dark
            pygame.draw.polygon(screen, (20, 20, 25), [(cx-25, cy+40), (cx-15, cy+10), (cx+15, cy+10), (cx+25, cy+40)])
            
            # Head - Pale
            pygame.draw.ellipse(screen, (230, 240, 240), (cx - 18, cy - 35, 36, 50))
            
            # Eyes - Red slits
            pygame.draw.line(screen, (255, 0, 0), (cx - 10, cy - 15), (cx - 4, cy - 12), 3)
            pygame.draw.line(screen, (255, 0, 0), (cx + 4, cy - 12), (cx + 10, cy - 15), 3)
            
            # Wand
            pygame.draw.line(screen, (240, 240, 220), (cx + 20, cy + 20), (cx + 35, cy + 5), 3)

        elif name == 'Hagrid':
            # Massive Coat
            pygame.draw.rect(screen, (80, 50, 30), (cx - 35, cy, 70, 45), border_radius=15)
            
            # Head
            pygame.draw.circle(screen, (240, 200, 180), (cx, cy - 20), 25)
            
            # Beard & Hair - huge
            pygame.draw.ellipse(screen, (40, 30, 20), (cx - 38, cy - 45, 76, 80))
            pygame.draw.circle(screen, (240, 200, 180), (cx, cy - 20), 15) # Face peek
            
            # Eyes (beetle black)
            pygame.draw.circle(screen, (0, 0, 0), (cx - 8, cy - 22), 3)
            pygame.draw.circle(screen, (0, 0, 0), (cx + 8, cy - 22), 3)

        elif name == 'Unicorn':
            # Body glow
            glow = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 255, 255, 60), (40, 40), 35)
            screen.blit(glow, (cx-40, cy-40))
            
            # Head
            pygame.draw.ellipse(screen, (255, 255, 255), (cx - 25, cy - 25, 50, 40)) # Snout
            pygame.draw.ellipse(screen, (255, 255, 255), (cx - 15, cy - 40, 30, 40)) # Neck/Head base
            
            # Mane - Rainbow
            colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255)]
            for i, col in enumerate(colors):
                pygame.draw.circle(screen, col, (cx - 20, cy - 35 + i*10), 8)
            
            # Horn
            pygame.draw.polygon(screen, (255, 255, 200), [(cx - 5, cy - 35), (cx + 5, cy - 35), (cx, cy - 65)])
            
            # Eye
            pygame.draw.circle(screen, (50, 0, 100), (cx, cy - 25), 4)

        elif name == 'Dragon':
            # Fire breath particles hint
            pygame.draw.circle(screen, (255, 100, 0), (cx + 30, cy + 10), 5)
            pygame.draw.circle(screen, (255, 200, 0), (cx + 38, cy + 5), 3)
            
            # Head - Scaly Red
            pygame.draw.polygon(screen, (200, 40, 40), [(cx-20, cy-20), (cx+10, cy-25), (cx+30, cy+10), (cx-10, cy+25)])
            
            # Horns
            pygame.draw.polygon(screen, (255, 200, 100), [(cx-15, cy-20), (cx-25, cy-45), (cx-5, cy-22)])
            
            # Eye - Fierce Yellow
            pygame.draw.ellipse(screen, (255, 255, 0), (cx - 5, cy - 10, 12, 8))
            pygame.draw.line(screen, (0, 0, 0), (cx + 1, cy - 10), (cx + 1, cy - 2), 2)
            
            # Smoke
            pygame.draw.circle(screen, (100, 100, 100), (cx + 25, cy - 5), 4)

    def move_selection(self, direction):
        """Move character selection."""
        self.selected_index += direction
        if self.selected_index < 0:
            self.selected_index = len(CHARACTER_ORDER) - 1
        elif self.selected_index >= len(CHARACTER_ORDER):
            self.selected_index = 0

    def get_selected_character(self):
        """Get currently selected character name."""
        return CHARACTER_ORDER[self.selected_index]

    def reset_selection(self):
        """Reset selection index."""
        self.selected_index = 0

    def draw_story_intro(self, screen, state_manager):
        """Draw a story intro screen for a new area."""
        self.anim_timer += 1
        
        # Get area data from state manager
        area_data = state_manager.current_story_area or {}
        
        # Dark overlay with gradient
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            overlay.fill((10, 10, 30, 220), (0, y, SCREEN_WIDTH, 1))
        screen.blit(overlay, (0, 0))
        
        # Animated border frame
        frame_expand = int(abs(math.sin(self.anim_timer * 0.03)) * 5)
        frame_rect = pygame.Rect(80 - frame_expand, 100 - frame_expand, 
                                SCREEN_WIDTH - 160 + frame_expand * 2, 
                                SCREEN_HEIGHT - 200 + frame_expand * 2)
        pygame.draw.rect(screen, (60, 50, 30), frame_rect, border_radius=20)
        pygame.draw.rect(screen, GOLD, frame_rect, 4, border_radius=20)
        
        # Decorative corners
        corner_size = 30
        for x, y in [(frame_rect.left + 10, frame_rect.top + 10),
                    (frame_rect.right - 10 - corner_size, frame_rect.top + 10),
                    (frame_rect.left + 10, frame_rect.bottom - 10 - corner_size),
                    (frame_rect.right - 10 - corner_size, frame_rect.bottom - 10 - corner_size)]:
            pygame.draw.rect(screen, GOLD, (x, y, corner_size, corner_size), 3, border_radius=5)
        
        # Area name with glow
        name = area_data.get('name', 'Unknown Area')
        subtitle = area_data.get('subtitle', '')
        description = area_data.get('description', '')
        
        # Glowing title
        glow_alpha = int(abs(math.sin(self.anim_timer * 0.04)) * 50) + 30
        glow_surf = pygame.Surface((len(name) * 40, 80), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (255, 215, 0, glow_alpha), glow_surf.get_rect())
        screen.blit(glow_surf, (SCREEN_WIDTH // 2 - len(name) * 20, 130))
        
        self.draw_text_outlined(screen, name, self.font_title, GOLD, (100, 80, 0),
                               SCREEN_WIDTH // 2, 160, center=True)
        
        # Subtitle
        self.draw_text(screen, subtitle, self.font_large, WHITE,
                      SCREEN_WIDTH // 2, 240, center=True)
        
        # Decorative line
        line_y = 280
        pygame.draw.line(screen, GOLD, (SCREEN_WIDTH // 2 - 150, line_y),
                        (SCREEN_WIDTH // 2 + 150, line_y), 2)
        
        # Description text (multi-line)
        desc_lines = description.split('\n')
        for i, line in enumerate(desc_lines):
            self.draw_text(screen, line.strip(), self.font_medium, (200, 200, 200),
                          SCREEN_WIDTH // 2, 320 + i * 35, center=True)
        
        # Continue prompt
        pulse = int(abs(math.sin(self.anim_timer * 0.06)) * 55) + 200
        self.draw_text(screen, "Press SPACE to continue", self.font_medium, (pulse, pulse, 0),
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT - 140, center=True)

    def draw_cutscene(self, screen, cutscene_data, progress=0):
        """Draw a story cutscene."""
        self.anim_timer += 1
        
        # Dark letterbox effect
        letterbox_h = 80
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, SCREEN_WIDTH, letterbox_h))
        pygame.draw.rect(screen, (0, 0, 0), (0, SCREEN_HEIGHT - letterbox_h, SCREEN_WIDTH, letterbox_h))
        
        # Dialogue box at bottom
        box_h = 180
        box_y = SCREEN_HEIGHT - letterbox_h - box_h - 20
        box_rect = pygame.Rect(60, box_y, SCREEN_WIDTH - 120, box_h)
        
        # Box background with gradient
        box_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        for y in range(box_rect.height):
            alpha = 200 - int(y * 0.3)
            box_surf.fill((20, 20, 40, alpha), (0, y, box_rect.width, 1))
        screen.blit(box_surf, box_rect.topleft)
        pygame.draw.rect(screen, GOLD, box_rect, 3, border_radius=15)
        
        title = cutscene_data.get('title', '')
        speaker = cutscene_data.get('speaker', '')
        text = cutscene_data.get('text', '')
        subtext = cutscene_data.get('subtext', '')
        
        # Title at top center (between letterboxes)
        if title:
            title_y = letterbox_h + 30
            self.draw_text_outlined(screen, title, self.font_large, GOLD, (80, 60, 0),
                                   SCREEN_WIDTH // 2, title_y, center=True)
        
        # Speaker name tab
        if speaker:
            speaker_rect = pygame.Rect(box_rect.left + 20, box_rect.top - 25, len(speaker) * 14 + 30, 30)
            pygame.draw.rect(screen, (50, 40, 70), speaker_rect, border_radius=8)
            pygame.draw.rect(screen, GOLD, speaker_rect, 2, border_radius=8)
            self.draw_text(screen, speaker, self.font_medium, GOLD, 
                          speaker_rect.centerx, speaker_rect.centery - 2, center=True)
        
        # Main dialogue text with typewriter effect
        if text:
            visible_chars = int(len(text) * min(1.0, progress * 2))
            visible_text = text[:visible_chars]
            self.draw_text(screen, visible_text, self.font_large, WHITE,
                          box_rect.left + 30, box_rect.top + 40)
        
        # Subtext
        if subtext and progress > 0.4:
            self.draw_text(screen, subtext, self.font_medium, (180, 180, 180),
                          box_rect.left + 30, box_rect.top + 100)
        
        # Skip prompt
        pulse = int(abs(math.sin(self.anim_timer * 0.08)) * 55) + 150
        self.draw_text(screen, "Press SPACE to skip", self.font_small, (pulse, pulse, pulse),
                      SCREEN_WIDTH - 140, SCREEN_HEIGHT - letterbox_h + 30, center=True)

    def draw_level_complete(self, screen, state_manager):
        """Draw level complete screen."""
        self.anim_timer += 1
        
        # Green/gold gradient overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(30 + ratio * 20)
            g = int(50 + ratio * 30)
            overlay.fill((r, g, 20, 190), (0, y, SCREEN_WIDTH, 1))
        screen.blit(overlay, (0, 0))

        # Title with animation
        bounce = int(abs(math.sin(self.anim_timer * 0.06)) * 10)
        self.draw_text_outlined(screen, f"LEVEL {state_manager.current_level}", self.font_title, 
                               GREEN, (0, 80, 0), SCREEN_WIDTH // 2, 150 - bounce, center=True)
        self.draw_text_outlined(screen, "COMPLETE!", self.font_large, 
                               GOLD, (100, 80, 0), SCREEN_WIDTH // 2, 230, center=True)

        # Stars animation
        for i in range(3):
            sx = SCREEN_WIDTH // 2 - 100 + i * 100
            sy = 320
            star_scale = 1.0 + abs(math.sin(self.anim_timer * 0.05 + i * 0.5)) * 0.2
            star_size = int(30 * star_scale)
            points = []
            for j in range(10):
                angle = (j / 10) * math.pi * 2 - math.pi / 2
                r = star_size if j % 2 == 0 else star_size // 2
                points.append((sx + math.cos(angle) * r, sy + math.sin(angle) * r))
            pygame.draw.polygon(screen, GOLD, points)
            pygame.draw.polygon(screen, YELLOW, points, 2)

        # Score panel
        panel_w, panel_h = 350, 80
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = 400
        pygame.draw.rect(screen, (40, 60, 40), (panel_x, panel_y, panel_w, panel_h), border_radius=15)
        pygame.draw.rect(screen, GREEN, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=15)
        
        self.draw_text(screen, f"Score: {state_manager.level_score}", self.font_medium, GOLD,
                      SCREEN_WIDTH // 2, panel_y + 25, center=True)
        self.draw_text(screen, f"Next: Level {state_manager.current_level + 1}", self.font_small, WHITE,
                      SCREEN_WIDTH // 2, panel_y + 55, center=True)

        # Continue button
        btn_y = 520
        btn_w, btn_h = 350, 50
        btn_rect = pygame.Rect((SCREEN_WIDTH - btn_w) // 2, btn_y, btn_w, btn_h)
        
        # Pulsing button
        pulse = int(abs(math.sin(self.anim_timer * 0.08)) * 20) + 235
        btn_color = (0, pulse // 2, 0)
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=12)
        pygame.draw.rect(screen, GREEN, btn_rect, 3, border_radius=12)
        self.draw_text(screen, "[SPACE/ENTER] Continue to Next Level", self.font_medium, WHITE,
                      btn_rect.centerx, btn_rect.centery, center=True)
