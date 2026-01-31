# Enemy Types for scrolling platformer

import pygame
import random
import math
from settings import *


class Enemy:
    """Enemy class."""

    def __init__(self, x, y, enemy_type='walker'):
        self.enemy_type = enemy_type
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(int(x), int(y), ENEMY_WIDTH, ENEMY_HEIGHT)

        # Set stats based on type
        if enemy_type == 'walker':
            self.speed = 1.5
            self.health = 30
            self.max_health = 30
            self.damage = 10
            self.color = DARK_GREEN
            self.secondary_color = RED
            self.flying = False
            self.display_name = "Dark Creature"
        elif enemy_type == 'flying':
            self.speed = 2.2
            self.health = 20
            self.max_health = 20
            self.damage = 8
            self.color = PURPLE
            self.secondary_color = LIGHT_BLUE
            self.flying = True
            self.display_name = "Bludger"
        elif enemy_type == 'tank':
            self.speed = 0.8
            self.health = 60
            self.max_health = 60
            self.damage = 15
            self.color = DARK_GRAY
            self.secondary_color = RED
            self.flying = False
            self.display_name = "Giant"
        # === THEMED HARRY POTTER ENEMIES ===
        elif enemy_type == 'malfoy':
            # Draco Malfoy - fast, annoying, shoots spells
            self.speed = 2.0
            self.health = 35
            self.max_health = 35
            self.damage = 12
            self.color = (180, 180, 180)  # Silver/blonde
            self.secondary_color = (0, 100, 0)  # Slytherin green
            self.flying = False
            self.display_name = "Malfoy"
            self.can_shoot = True
            self.shoot_cooldown = 0
            self.shoot_interval = 2000
        elif enemy_type == 'troll':
            # Mountain Troll - very slow, very strong, lots of HP
            self.speed = 0.5
            self.health = 120
            self.max_health = 120
            self.damage = 25
            self.color = (100, 110, 100)  # Grayish green
            self.secondary_color = (60, 70, 60)
            self.flying = False
            self.display_name = "Mountain Troll"
            self.rect = pygame.Rect(int(x), int(y), ENEMY_WIDTH + 20, ENEMY_HEIGHT + 30)  # Bigger
        elif enemy_type == 'fluffy':
            # Fluffy the three-headed dog - mini-boss
            self.speed = 1.2
            self.health = 200
            self.max_health = 200
            self.damage = 20
            self.color = (139, 90, 43)  # Brown
            self.secondary_color = (80, 50, 20)
            self.flying = False
            self.display_name = "Fluffy"
            self.rect = pygame.Rect(int(x), int(y), ENEMY_WIDTH + 30, ENEMY_HEIGHT + 20)
        elif enemy_type == 'devil_snare':
            # Devil's Snare - stationary, grabs players
            self.speed = 0
            self.health = 50
            self.max_health = 50
            self.damage = 15
            self.color = (20, 80, 20)  # Dark green
            self.secondary_color = (10, 50, 10)
            self.flying = False
            self.display_name = "Devil's Snare"
        elif enemy_type == 'flying_key':
            # Flying Key - fast, annoying, low HP
            self.speed = 3.5
            self.health = 15
            self.max_health = 15
            self.damage = 5
            self.color = GOLD
            self.secondary_color = (200, 180, 50)
            self.flying = True
            self.display_name = "Flying Key"
        elif enemy_type == 'chess_piece':
            # Chess piece - slow but powerful
            self.speed = 1.0
            self.health = 80
            self.max_health = 80
            self.damage = 18
            self.color = (30, 30, 30)  # Black
            self.secondary_color = (60, 60, 60)
            self.flying = False
            self.display_name = "Chess Knight"
            self.rect = pygame.Rect(int(x), int(y), ENEMY_WIDTH + 10, ENEMY_HEIGHT + 15)
        elif enemy_type == 'quirrell':
            # Professor Quirrell/Voldemort - mini-boss, aggressive and dangerous
            self.speed = 2.2
            self.health = 350
            self.max_health = 350
            self.damage = 25
            self.color = (80, 0, 80)  # Dark purple
            self.secondary_color = (150, 0, 0)  # Red (Voldemort)
            self.flying = False
            self.display_name = "Quirrell"
            self.rect = pygame.Rect(int(x), int(y), ENEMY_WIDTH + 15, ENEMY_HEIGHT + 10)
            self.can_shoot = True
            self.shoot_cooldown = 0
            self.shoot_interval = 1200  # Shoots faster
            self.special_attack_cooldown = 0
            self.special_attack_interval = 7000  # Special attack every 7 seconds (was 5s - too frequent)
            self.is_enraged = False  # Gets enraged at low health
        else:
            # Default fallback
            self.speed = 1.5
            self.health = 30
            self.max_health = 30
            self.damage = 10
            self.color = DARK_GREEN
            self.secondary_color = RED
            self.flying = False
            self.display_name = "Enemy"

        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.direction = random.choice([-1, 1])
        self.patrol_range = 200
        self.start_x = x
        self.attack_cooldown = 0
        self.attack_interval = 1000
        self.active = False  # Only active when player is near
        self.hover_offset = 0
        self.hover_direction = 1

        # Projectile system for ranged enemies
        self.projectiles = []

        # AI state for smarter behavior
        self.ai_state = 'idle'  # idle, chase, attack, retreat, strafe
        self.state_timer = 0
        self.strafe_direction = 1
        self.last_player_x = None  # Track player movement for prediction

        # Animation state
        self.anim_timer = 0
        self.walk_frame = 0
        self.hurt_timer = 0

    def activate(self, camera_x):
        """Activate enemy when on or near screen."""
        screen_x = self.x - camera_x
        if -200 < screen_x < SCREEN_WIDTH + 200:
            self.active = True
        return self.active

    def _check_edge_in_direction(self, platforms, direction):
        """Check if there's an edge (no ground) in the given direction."""
        check_x = self.x + (self.rect.width // 2) + (self.rect.width // 2 + 15) * direction
        check_y = self.y + self.rect.height + 10
        for platform in platforms:
            if (platform.rect.left - 5 <= check_x <= platform.rect.right + 5 and
                platform.rect.top <= check_y <= platform.rect.top + 30):
                return False  # Ground found
        return True  # Edge/no ground

    def _check_wall_in_direction(self, platforms, direction):
        """Check if there's a wall blocking movement in the given direction."""
        check_x = self.x + (self.rect.width if direction > 0 else 0) + (10 * direction)
        for platform in platforms:
            # Check if wall blocks at body height
            if (platform.rect.left <= check_x <= platform.rect.right and
                platform.rect.top < self.y + self.rect.height - 5 and
                platform.rect.bottom > self.y + 5):
                return True  # Wall found
        return False  # No wall

    def _is_player_reachable(self, player, platforms):
        """Check if player is on the same platform level (reachable by walking)."""
        if self.flying:
            return True
        # Check if player is roughly at same height (within jump range)
        height_diff = abs(player.y - self.y)
        return height_diff < 100  # Can reach if within ~100 pixels vertically

    def _check_hazard_in_direction(self, direction):
        """Check for hazards (spikes, lava) in the given direction."""
        # This is a placeholder - hazards are checked in main.py via level
        # For now, we'll check if there's a "danger zone" ahead
        check_x = self.x + (self.rect.width if direction > 0 else 0) + (30 * direction)
        check_y = self.y + self.rect.height + 5
        # Return False by default - actual hazard data comes from level
        return False  # Override in EnemyManager with actual hazard data

    def _shoot_at_player(self, player):
        """Fire a projectile at the player."""
        # Calculate direction to player
        dx = player.x - self.x
        dy = player.y - self.y
        dist = max(1, (dx * dx + dy * dy) ** 0.5)

        # Normalize and set projectile speed
        proj_speed = 5 if self.enemy_type == 'quirrell' else 4
        vx = (dx / dist) * proj_speed
        vy = (dy / dist) * proj_speed

        # Add some prediction - aim where player will be
        if hasattr(player, 'vel_x'):
            vx += player.vel_x * 0.3

        # Spawn projectile
        proj_x = self.x + self.rect.width // 2
        proj_y = self.y + self.rect.height // 3

        self.projectiles.append({
            'x': proj_x,
            'y': proj_y,
            'vx': vx,
            'vy': vy,
            'life': 3000,  # 3 seconds
            'damage': self.damage // 2,  # Projectiles do half damage
            'color': self.secondary_color if hasattr(self, 'secondary_color') else (255, 100, 100)
        })

    def _quirrell_special_attack(self, player):
        """Quirrell's special attack - spread burst of dark magic."""
        proj_x = self.x + self.rect.width // 2
        proj_y = self.y + self.rect.height // 3

        # Calculate base direction to player
        dx = player.x - self.x
        dy = player.y - self.y
        dist = max(1, (dx * dx + dy * dy) ** 0.5)
        base_vx = (dx / dist) * 6
        base_vy = (dy / dist) * 6

        # Fire 5 projectiles in a spread pattern
        spread_angles = [-30, -15, 0, 15, 30]
        for angle in spread_angles:
            rad = math.radians(angle)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)
            # Rotate velocity vector
            vx = base_vx * cos_a - base_vy * sin_a
            vy = base_vx * sin_a + base_vy * cos_a

            self.projectiles.append({
                'x': proj_x,
                'y': proj_y,
                'vx': vx,
                'vy': vy,
                'life': 2500,
                'damage': self.damage // 3,  # Each projectile does 1/3 damage
                'color': (200, 0, 200) if not self.is_enraged else (255, 50, 50)  # Purple/red
            })

    def update(self, platforms, players, dt, camera_x):
        """Update enemy."""
        if not self.activate(camera_x):
            return

        # Update animation timer
        self.anim_timer += dt
        if self.hurt_timer > 0:
            self.hurt_timer -= dt

        # Update shoot cooldown for ranged enemies
        if hasattr(self, 'shoot_cooldown') and self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

        # Update AI state timer
        self.state_timer += dt

        # Update enemy projectiles
        for proj in self.projectiles[:]:
            proj['x'] += proj['vx']
            proj['y'] += proj['vy']
            proj['life'] -= dt
            if proj['life'] <= 0:
                self.projectiles.remove(proj)

        # Stationary enemies (like Devil's Snare) don't move but can still attack
        if self.speed == 0:
            self.vel_x = 0
            self.vel_y = 0 if self.flying else self.vel_y
            if not self.flying:
                self.vel_y += GRAVITY
                if self.vel_y > MAX_FALL_SPEED:
                    self.vel_y = MAX_FALL_SPEED
                self.y += self.vel_y
                self.rect.y = int(self.y)
                self.check_collisions(platforms)
            return

        # Find nearest alive player
        nearest_player = None
        min_dist = float('inf')
        for player in players:
            if player.is_alive():
                dist = abs(self.x - player.x)
                if dist < min_dist:
                    min_dist = dist
                    nearest_player = player

        # Smart edge, wall, and HAZARD detection
        edge_left = self._check_edge_in_direction(platforms, -1) if not self.flying else False
        edge_right = self._check_edge_in_direction(platforms, 1) if not self.flying else False
        wall_left = self._check_wall_in_direction(platforms, -1) if not self.flying else False
        wall_right = self._check_wall_in_direction(platforms, 1) if not self.flying else False
        hazard_left = self._check_hazard_in_direction(-1) if not self.flying else False
        hazard_right = self._check_hazard_in_direction(1) if not self.flying else False

        # Combine all dangers
        danger_left = edge_left or wall_left or hazard_left
        danger_right = edge_right or wall_right or hazard_right

        # Determine behavior based on enemy type
        is_ranged = hasattr(self, 'can_shoot') and self.can_shoot
        is_boss_type = self.enemy_type in ('quirrell', 'fluffy', 'troll', 'chess_piece')

        if nearest_player and min_dist < 500:
            desired_dir = -1 if nearest_player.x < self.x else 1
            player_reachable = self._is_player_reachable(nearest_player, platforms)

            # Track player movement for prediction
            if self.last_player_x is not None:
                player_moving_toward = (nearest_player.x - self.last_player_x) * desired_dir < 0
            else:
                player_moving_toward = False
            self.last_player_x = nearest_player.x

            # RANGED ENEMIES - Actually shoot at the player!
            if is_ranged:
                ideal_distance = 200 if self.enemy_type == 'quirrell' else 150

                # Shoot at player if cooldown is ready and has line of sight
                if self.shoot_cooldown <= 0 and min_dist < 350:
                    self._shoot_at_player(nearest_player)
                    self.shoot_cooldown = self.shoot_interval if hasattr(self, 'shoot_interval') else 2000

                # Movement logic - strafe and reposition
                if min_dist < ideal_distance - 40:
                    # Too close - back away urgently
                    move_dir = -desired_dir
                    self.ai_state = 'retreat'
                elif min_dist > ideal_distance + 80:
                    # Too far - move closer
                    move_dir = desired_dir
                    self.ai_state = 'chase'
                else:
                    # Good distance - strafe to make harder target
                    if self.state_timer > 1500:
                        self.strafe_direction *= -1
                        self.state_timer = 0
                    move_dir = self.strafe_direction
                    self.ai_state = 'strafe'
                    self.direction = desired_dir  # Always face player while strafing

                # Check if movement is safe
                if move_dir != 0:
                    blocked = (move_dir < 0 and danger_left) or (move_dir > 0 and danger_right)
                    if blocked:
                        # Try the other direction for strafe, or stop
                        if self.ai_state == 'strafe':
                            self.strafe_direction *= -1
                            move_dir = self.strafe_direction
                            blocked = (move_dir < 0 and danger_left) or (move_dir > 0 and danger_right)
                        if blocked:
                            self.vel_x = 0
                        else:
                            self.vel_x = self.speed * move_dir * 0.8
                    else:
                        speed_mult = 1.0 if self.ai_state == 'retreat' else 0.7
                        self.vel_x = self.speed * move_dir * speed_mult
                        if self.ai_state != 'strafe':
                            self.direction = move_dir
                else:
                    self.vel_x = 0

            # BOSS-TYPE ENEMIES - Aggressive and tactical
            elif is_boss_type:
                # Quirrell special behavior - aggressive mini-boss
                if self.enemy_type == 'quirrell':
                    # Check for enrage at low health
                    if not self.is_enraged and self.health < self.max_health * 0.4:
                        self.is_enraged = True
                        self.speed = 2.8  # Faster when enraged
                        self.shoot_interval = 1000  # Shoot faster (was 800 - too spammy)

                    # Update special attack cooldown
                    if hasattr(self, 'special_attack_cooldown'):
                        if self.special_attack_cooldown > 0:
                            self.special_attack_cooldown -= dt
                        elif min_dist < 250:
                            # Special attack: burst fire of 3 projectiles
                            self._quirrell_special_attack(nearest_player)
                            self.special_attack_cooldown = self.special_attack_interval

                    # Regular shooting
                    if self.shoot_cooldown <= 0 and min_dist < 350:
                        self._shoot_at_player(nearest_player)
                        self.shoot_cooldown = self.shoot_interval

                    # Aggressive movement - chase more, retreat less
                    if min_dist > 80:
                        move_dir = desired_dir
                        self.ai_state = 'chase'
                    elif min_dist < 40:
                        # Too close - quick backstep
                        move_dir = -desired_dir
                        self.ai_state = 'retreat'
                    elif player_moving_toward:
                        # Player charging - sidestep aggressively
                        move_dir = self.strafe_direction
                        if self.state_timer > 600:
                            self.strafe_direction *= -1
                            self.state_timer = 0
                        self.direction = desired_dir  # Keep facing player
                    else:
                        # Good distance - strafe while shooting
                        move_dir = self.strafe_direction
                        if self.state_timer > 1000:
                            self.strafe_direction *= -1
                            self.state_timer = 0
                        self.direction = desired_dir

                else:
                    # Other boss types - aggressive chase
                    if player_reachable and min_dist > 50:
                        move_dir = desired_dir
                    else:
                        move_dir = 0
                        self.direction = desired_dir

                # Apply movement with danger awareness
                if move_dir != 0:
                    blocked = (move_dir < 0 and danger_left) or (move_dir > 0 and danger_right)
                    if blocked:
                        self.vel_x = 0
                        self.direction = desired_dir
                    else:
                        self.vel_x = self.speed * move_dir
                        self.direction = move_dir
                else:
                    self.vel_x = 0

            # REGULAR ENEMIES - Smarter chase with prediction
            else:
                blocked = (desired_dir < 0 and danger_left) or (desired_dir > 0 and danger_right)

                if blocked:
                    # Can't chase - wait for player, don't walk into hazards
                    self.vel_x = 0
                    self.direction = desired_dir
                    self.ai_state = 'wait'
                elif player_reachable:
                    # Chase with slight speed variation to prevent bunching
                    speed_var = 0.9 + random.random() * 0.2
                    self.vel_x = self.speed * desired_dir * speed_var
                    self.direction = desired_dir
                    self.ai_state = 'chase'
                else:
                    # Player on different level - patrol but face player
                    self.vel_x = self.speed * self.direction * 0.4
                    self.ai_state = 'patrol'

            # Flying enemies - more aggressive dive-bomb behavior
            if self.flying:
                # Dive attack pattern - swoop down when close
                if min_dist < 150 and self.y < nearest_player.y - 30:
                    # Dive attack!
                    self.vel_y = self.speed * 2.5
                    self.vel_x = self.speed * desired_dir * 1.5
                    self.ai_state = 'dive'
                elif min_dist < 100 and self.y > nearest_player.y + 20:
                    # Pull up after dive
                    self.vel_y = -self.speed * 2.0
                    self.ai_state = 'pullup'
                else:
                    # Normal hover positioning - circle around player
                    target_y = nearest_player.y - 60
                    # Add sinusoidal movement for unpredictability
                    wave_offset = math.sin(self.anim_timer / 500) * 30
                    target_y += wave_offset

                    if self.y < target_y - 20:
                        self.vel_y = self.speed * 1.3
                    elif self.y > target_y + 20:
                        self.vel_y = -self.speed * 1.3
                    else:
                        self.vel_y = math.sin(self.anim_timer / 300) * self.speed * 0.5

        else:
            # No player nearby - smart patrol mode
            self.ai_state = 'patrol'
            current_danger = danger_left if self.direction < 0 else danger_right

            if current_danger:
                # Turn around
                self.direction *= -1
                new_danger = danger_left if self.direction < 0 else danger_right
                if new_danger:
                    # Both directions blocked - stay still
                    self.vel_x = 0
                else:
                    self.vel_x = self.speed * self.direction * 0.5
            elif self.x < self.start_x - self.patrol_range:
                self.direction = 1
                self.vel_x = self.speed * self.direction * 0.5
            elif self.x > self.start_x + self.patrol_range:
                self.direction = -1
                self.vel_x = self.speed * self.direction * 0.5
            else:
                self.vel_x = self.speed * self.direction * 0.5

            if self.flying:
                self.hover_offset += 0.1 * self.hover_direction
                if abs(self.hover_offset) > 5:
                    self.hover_direction *= -1
                self.vel_y = 0

        # Apply gravity for ground enemies
        if not self.flying:
            self.vel_y += GRAVITY
            if self.vel_y > MAX_FALL_SPEED:
                self.vel_y = MAX_FALL_SPEED

        # Apply movement
        self.x += self.vel_x
        self.y += self.vel_y
        if self.flying:
            self.y += self.hover_offset * 0.5

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Collisions for ground enemies
        if not self.flying:
            self.check_collisions(platforms)

        # Keep in level bounds
        if self.x < 0:
            self.x = 0
            self.direction = 1
        if self.x > LEVEL_WIDTH - self.rect.width:
            self.x = LEVEL_WIDTH - self.rect.width
            self.direction = -1
        if self.y > SCREEN_HEIGHT + 100:
            self.health = 0  # Fell off level

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

    def check_collisions(self, platforms):
        """Check collisions with platforms."""
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.y = float(self.rect.y)
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.y = float(self.rect.y)
                    self.vel_y = 0

    def can_attack(self):
        return self.attack_cooldown <= 0

    def attack(self):
        self.attack_cooldown = self.attack_interval
        return self.damage

    def take_damage(self, amount, knockback_direction=0):
        """Take damage and apply knockback."""
        self.health -= amount
        self.hurt_timer = 200  # Flash when hurt
        # Apply knockback
        if knockback_direction != 0:
            self.vel_x = 5 * knockback_direction
        return self.health <= 0

    def is_alive(self):
        return self.health > 0

    def draw(self, screen, camera_x):
        """Draw the enemy."""
        if not self.active:
            return

        screen_x = int(self.x - camera_x)
        base_y = int(self.y)
        bob = int(math.sin(pygame.time.get_ticks() / 200 + self.x * 0.01) * (3 if self.enemy_type != 'tank' else 2))
        draw_y = base_y + bob

        # Only draw if on screen
        if screen_x < -50 or screen_x > SCREEN_WIDTH + 50:
            return

        # Flash white when hurt
        if self.hurt_timer > 0 and int(self.hurt_timer / 50) % 2 == 0:
            # Draw white silhouette
            pygame.draw.ellipse(screen, WHITE, (screen_x, draw_y, self.rect.width, self.rect.height))
            return

        # Draw based on type
        if self.enemy_type == 'walker':
            self._draw_walker(screen, screen_x, draw_y)
        elif self.enemy_type == 'flying':
            self._draw_flying(screen, screen_x, draw_y)
        elif self.enemy_type == 'tank':
            self._draw_tank(screen, screen_x, draw_y)
        elif self.enemy_type == 'malfoy':
            self._draw_malfoy(screen, screen_x, draw_y)
        elif self.enemy_type == 'troll':
            self._draw_troll(screen, screen_x, draw_y)
        elif self.enemy_type == 'fluffy':
            self._draw_fluffy(screen, screen_x, draw_y)
        elif self.enemy_type == 'devil_snare':
            self._draw_devil_snare(screen, screen_x, draw_y)
        elif self.enemy_type == 'flying_key':
            self._draw_flying_key(screen, screen_x, draw_y)
        elif self.enemy_type == 'chess_piece':
            self._draw_chess_piece(screen, screen_x, draw_y)
        elif self.enemy_type == 'quirrell':
            self._draw_quirrell(screen, screen_x, draw_y)
        else:
            # Default fallback
            self._draw_walker(screen, screen_x, draw_y)

        # Enemy name label above health bar (color-coded by threat)
        name_y = draw_y - 20
        # Threat color: red for high damage/tank, yellow for medium, green for weak
        if self.damage >= 20 or self.max_health >= 100:
            name_color = (255, 100, 100)  # Red - dangerous
        elif self.damage >= 12 or self.max_health >= 40:
            name_color = (255, 255, 100)  # Yellow - medium
        else:
            name_color = (100, 255, 100)  # Green - weak
        font = pygame.font.Font(None, 18)
        name_surf = font.render(self.display_name, True, name_color)
        name_x = screen_x + (self.rect.width - name_surf.get_width()) // 2
        screen.blit(name_surf, (name_x, name_y))

        # Health bar
        bar_width = self.rect.width
        bar_y = draw_y - 8
        pygame.draw.rect(screen, RED, (screen_x, bar_y, bar_width, 4))
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, GREEN, (screen_x, bar_y, health_width, 4))

        # Draw enemy projectiles
        for proj in self.projectiles:
            px = int(proj['x'] - camera_x)
            py = int(proj['y'])
            if 0 <= px <= SCREEN_WIDTH:
                color = proj.get('color', (255, 100, 100))
                # Outer glow
                pygame.draw.circle(screen, (color[0] // 2, color[1] // 2, color[2] // 2), (px, py), 10)
                # Inner bright
                pygame.draw.circle(screen, color, (px, py), 7)
                # Core
                pygame.draw.circle(screen, (255, 255, 200), (px, py), 3)

    def _draw_walker(self, screen, screen_x, y):
        """Draw a dark creature (dementor-like) with cel-shaded style."""
        t = pygame.time.get_ticks()
        w, h = ENEMY_WIDTH, ENEMY_HEIGHT

        # Ethereal shadow/glow
        shadow_surf = pygame.Surface((w + 20, 14), pygame.SRCALPHA)
        pulse = int(abs(math.sin(t * 0.003)) * 30)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80 + pulse), (0, 0, w + 20, 14))
        screen.blit(shadow_surf, (screen_x - 10, y + h - 6))

        # Ghostly aura
        aura_surf = pygame.Surface((w + 16, h + 10), pygame.SRCALPHA)
        aura_alpha = 30 + int(math.sin(t * 0.004) * 15)
        pygame.draw.ellipse(aura_surf, (30, 60, 30, aura_alpha), (0, 0, w + 16, h + 10))
        screen.blit(aura_surf, (screen_x - 8, y - 5))

        # Flowing tattered robes - multiple layers
        robe_base = self.color
        robe_dark = tuple(max(0, c - 50) for c in robe_base)
        robe_light = tuple(min(255, c + 20) for c in robe_base)

        # Main robe body
        pygame.draw.ellipse(screen, robe_base, (screen_x + 2, y + 12, w - 4, h - 12))
        # Dark shading on left
        pygame.draw.ellipse(screen, robe_dark, (screen_x + 2, y + 15, 12, h - 20))
        # Highlight on right
        pygame.draw.arc(screen, robe_light, (screen_x + w - 18, y + 20, 14, h - 30), -1.5, 1.5, 3)

        # Tattered bottom with flowing animation
        tatter_wave = math.sin(t * 0.008)
        for i in range(6):
            tx = screen_x + 2 + i * 6
            tatter_offset = int(math.sin(t * 0.006 + i * 0.8) * 3)
            pygame.draw.polygon(screen, robe_base, [
                (tx, y + h - 8),
                (tx + 3 + tatter_offset, y + h + 5 + abs(tatter_offset)),
                (tx + 6, y + h - 8)
            ])
            pygame.draw.polygon(screen, robe_dark, [
                (tx, y + h - 8),
                (tx + 3 + tatter_offset, y + h + 5 + abs(tatter_offset)),
                (tx + 6, y + h - 8)
            ], 1)

        # Shadowy tendrils reaching out
        for i in range(3):
            tendril_x = screen_x + 10 + i * 12
            tendril_wave = int(math.sin(t * 0.005 + i) * 4)
            pygame.draw.line(screen, robe_dark,
                           (tendril_x, y + h - 5),
                           (tendril_x + tendril_wave, y + h + 8), 2)

        # Deep hood with cel-shaded depth
        hood_outer = (screen_x + 2, y - 4, w - 4, 30)
        hood_mid = (screen_x + 5, y - 1, w - 10, 26)
        hood_inner = (screen_x + 8, y + 2, w - 16, 22)
        hood_void = (screen_x + 12, y + 6, w - 24, 16)

        pygame.draw.ellipse(screen, (25, 45, 25), hood_outer)
        pygame.draw.ellipse(screen, (18, 35, 18), hood_mid)
        pygame.draw.ellipse(screen, (12, 25, 12), hood_inner)
        pygame.draw.ellipse(screen, (5, 12, 5), hood_void)  # Dark void inside
        pygame.draw.ellipse(screen, robe_dark, hood_outer, 2)

        # Glowing menacing eyes with pulsing effect
        eye_offset = 4 if self.direction > 0 else -4
        eye_x = screen_x + w//2 - 8 + eye_offset
        eye_pulse = int(abs(math.sin(t * 0.008)) * 40)

        # Eye glow aura
        glow_surf = pygame.Surface((28, 16), pygame.SRCALPHA)
        glow_color = (*self.secondary_color[:3], 60 + eye_pulse)
        pygame.draw.ellipse(glow_surf, glow_color, (0, 0, 28, 16))
        screen.blit(glow_surf, (eye_x - 4, y + 8))

        # Eyes with inner glow
        eye_color = self.secondary_color
        eye_bright = tuple(min(255, c + 80) for c in eye_color)
        pygame.draw.circle(screen, eye_color, (eye_x + 4, y + 14), 5)
        pygame.draw.circle(screen, eye_color, (eye_x + 18, y + 14), 5)
        pygame.draw.circle(screen, eye_bright, (eye_x + 4, y + 14), 3)
        pygame.draw.circle(screen, eye_bright, (eye_x + 18, y + 14), 3)
        pygame.draw.circle(screen, (255, 255, 220), (eye_x + 4, y + 14), 1)
        pygame.draw.circle(screen, (255, 255, 220), (eye_x + 18, y + 14), 1)

    def _draw_flying(self, screen, screen_x, y):
        """Draw a Cornish Pixie - mischievous blue creature with cel-shaded style."""
        t = pygame.time.get_ticks()
        w, h = ENEMY_WIDTH, ENEMY_HEIGHT

        # Animated wing flap
        wing_flap = math.sin(t * 0.025) * 8
        wing_angle = math.cos(t * 0.025) * 0.3

        # Pixie dust trail
        for i in range(4):
            dust_x = screen_x + w//2 + int(math.sin(t * 0.01 + i) * 15)
            dust_y = y + h//2 + int(math.cos(t * 0.008 + i * 1.5) * 10)
            dust_alpha = int(100 - i * 20)
            dust_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(dust_surf, (200, 220, 255, dust_alpha), (3, 3), 3 - i//2)
            screen.blit(dust_surf, (dust_x, dust_y))

        # Wing glow aura
        wing_glow = pygame.Surface((w + 40, h + 20), pygame.SRCALPHA)
        glow_pulse = int(abs(math.sin(t * 0.006)) * 30)
        pygame.draw.ellipse(wing_glow, (*self.secondary_color[:3], 30 + glow_pulse), (0, 10, 25, 35))
        pygame.draw.ellipse(wing_glow, (*self.secondary_color[:3], 30 + glow_pulse), (w + 15, 10, 25, 35))
        screen.blit(wing_glow, (screen_x - 12, y - 5))

        # Delicate fairy wings - left
        wing_color = self.secondary_color
        wing_light = tuple(min(255, c + 60) for c in wing_color)
        wing_dark = tuple(max(0, c - 40) for c in wing_color)

        left_wing_pts = [
            (screen_x + 8, y + 20),
            (screen_x - 10 + int(wing_flap * 0.5), y + 8 - int(abs(wing_flap))),
            (screen_x - 15, y + 25),
            (screen_x - 5, y + 35),
            (screen_x + 5, y + 30)
        ]
        pygame.draw.polygon(screen, wing_color, left_wing_pts)
        pygame.draw.polygon(screen, wing_light, [(p[0] + 2, p[1] + 2) for p in left_wing_pts[:3]], 0)
        pygame.draw.polygon(screen, wing_dark, left_wing_pts, 2)
        # Wing veins
        pygame.draw.line(screen, wing_dark, left_wing_pts[0], left_wing_pts[1], 1)
        pygame.draw.line(screen, wing_dark, left_wing_pts[0], left_wing_pts[3], 1)

        # Right wing
        right_wing_pts = [
            (screen_x + w - 8, y + 20),
            (screen_x + w + 10 - int(wing_flap * 0.5), y + 8 - int(abs(wing_flap))),
            (screen_x + w + 15, y + 25),
            (screen_x + w + 5, y + 35),
            (screen_x + w - 5, y + 30)
        ]
        pygame.draw.polygon(screen, wing_color, right_wing_pts)
        pygame.draw.polygon(screen, wing_dark, right_wing_pts, 2)
        pygame.draw.line(screen, wing_dark, right_wing_pts[0], right_wing_pts[1], 1)
        pygame.draw.line(screen, wing_dark, right_wing_pts[0], right_wing_pts[3], 1)

        # Body - electric blue with cel-shading
        body_color = self.color
        body_dark = tuple(max(0, c - 50) for c in body_color)
        body_light = tuple(min(255, c + 40) for c in body_color)

        pygame.draw.ellipse(screen, body_color, (screen_x + 6, y + 16, w - 12, h - 22))
        pygame.draw.ellipse(screen, body_dark, (screen_x + 6, y + 18, 10, h - 28))
        pygame.draw.arc(screen, body_light, (screen_x + w - 20, y + 20, 12, h - 32), -1.5, 1.5, 3)
        pygame.draw.ellipse(screen, tuple(max(0, c - 60) for c in body_color),
                          (screen_x + 6, y + 16, w - 12, h - 22), 2)

        # Tiny arms
        pygame.draw.ellipse(screen, body_color, (screen_x + 2, y + 22, 8, 14))
        pygame.draw.ellipse(screen, body_color, (screen_x + w - 10, y + 22, 8, 14))
        # Tiny hands
        pygame.draw.circle(screen, body_light, (screen_x + 4, y + 35), 4)
        pygame.draw.circle(screen, body_light, (screen_x + w - 6, y + 35), 4)

        # Head - slightly larger with pointy ears
        head_color = body_color
        pygame.draw.ellipse(screen, head_color, (screen_x + 4, y + 4, w - 8, 20))
        pygame.draw.ellipse(screen, body_dark, (screen_x + 4, y + 6, 8, 14))
        pygame.draw.ellipse(screen, body_light, (screen_x + w - 16, y + 6, 8, 10))
        pygame.draw.ellipse(screen, tuple(max(0, c - 60) for c in head_color),
                          (screen_x + 4, y + 4, w - 8, 20), 2)

        # Pointy ears
        pygame.draw.polygon(screen, head_color, [
            (screen_x + 4, y + 10), (screen_x - 4, y + 4), (screen_x + 8, y + 8)
        ])
        pygame.draw.polygon(screen, head_color, [
            (screen_x + w - 4, y + 10), (screen_x + w + 4, y + 4), (screen_x + w - 8, y + 8)
        ])

        # Mischievous eyes - big and expressive
        eye_offset = 2 * self.direction
        # Eye whites
        pygame.draw.ellipse(screen, WHITE, (screen_x + 8 + eye_offset, y + 8, 10, 10))
        pygame.draw.ellipse(screen, WHITE, (screen_x + w - 18 + eye_offset, y + 8, 10, 10))
        # Irises - dark blue
        pygame.draw.circle(screen, (30, 50, 120), (screen_x + 13 + eye_offset, y + 13), 4)
        pygame.draw.circle(screen, (30, 50, 120), (screen_x + w - 13 + eye_offset, y + 13), 4)
        # Pupils
        pygame.draw.circle(screen, BLACK, (screen_x + 14 + eye_offset, y + 13), 2)
        pygame.draw.circle(screen, BLACK, (screen_x + w - 12 + eye_offset, y + 13), 2)
        # Eye shine
        pygame.draw.circle(screen, WHITE, (screen_x + 11 + eye_offset, y + 11), 2)
        pygame.draw.circle(screen, WHITE, (screen_x + w - 15 + eye_offset, y + 11), 2)
        # Mischievous eyebrows
        pygame.draw.arc(screen, body_dark, (screen_x + 7 + eye_offset, y + 4, 12, 8), 0.5, 2.5, 2)
        pygame.draw.arc(screen, body_dark, (screen_x + w - 19 + eye_offset, y + 4, 12, 8), 0.5, 2.5, 2)

        # Impish grin
        pygame.draw.arc(screen, (150, 100, 120), (screen_x + 10, y + 18, 14, 8), 3.14, 0, 2)
        # Tiny sharp teeth
        for i in range(3):
            tooth_x = screen_x + 12 + i * 4
            pygame.draw.polygon(screen, WHITE, [
                (tooth_x, y + 19), (tooth_x + 2, y + 22), (tooth_x + 4, y + 19)
            ])

    def _draw_tank(self, screen, screen_x, y):
        """Draw a Giant Rat - scruffy, menacing with cel-shaded fur texture."""
        t = pygame.time.get_ticks()
        w, h = ENEMY_WIDTH, ENEMY_HEIGHT

        # Scurrying animation
        scurry = int(math.sin(t * 0.015) * 2)

        # Shadow
        shadow_surf = pygame.Surface((w + 16, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 70), (0, 0, w + 16, 12))
        screen.blit(shadow_surf, (screen_x - 8, y + h - 6))

        # Long scaly tail
        tail_wave = math.sin(t * 0.008) * 8
        tail_start_x = screen_x + (0 if self.direction > 0 else w)
        tail_end_x = tail_start_x - 35 * self.direction
        tail_mid_x = (tail_start_x + tail_end_x) // 2
        tail_color = (180, 160, 150)
        tail_dark = (140, 120, 110)
        # Draw curved tail
        pygame.draw.line(screen, tail_color, (tail_start_x, y + h - 15),
                        (tail_mid_x, y + h - 8 + int(tail_wave)), 6)
        pygame.draw.line(screen, tail_color, (tail_mid_x, y + h - 8 + int(tail_wave)),
                        (tail_end_x, y + h - 20 + int(tail_wave * 1.5)), 4)
        pygame.draw.line(screen, tail_dark, (tail_start_x, y + h - 15),
                        (tail_mid_x, y + h - 8 + int(tail_wave)), 2)
        # Tail segments
        for i in range(5):
            seg_x = tail_start_x + (tail_mid_x - tail_start_x) * i // 5
            seg_y = y + h - 15 + (7 + int(tail_wave)) * i // 5
            pygame.draw.line(screen, tail_dark, (seg_x - 2, seg_y - 2), (seg_x + 2, seg_y + 2), 1)

        # Back legs
        leg_offset = scurry
        pygame.draw.ellipse(screen, self.color, (screen_x + 2, y + h - 20 - leg_offset, 14, 22))
        pygame.draw.ellipse(screen, self.color, (screen_x + w - 16, y + h - 20 + leg_offset, 14, 22))
        # Paws with claws
        paw_color = (180, 160, 150)
        pygame.draw.ellipse(screen, paw_color, (screen_x, y + h - 8 - leg_offset, 16, 10))
        pygame.draw.ellipse(screen, paw_color, (screen_x + w - 18, y + h - 8 + leg_offset, 16, 10))
        # Claws
        for i in range(3):
            pygame.draw.ellipse(screen, (60, 50, 45), (screen_x + 2 + i * 5, y + h - 4 - leg_offset, 3, 5))
            pygame.draw.ellipse(screen, (60, 50, 45), (screen_x + w - 16 + i * 5, y + h - 4 + leg_offset, 3, 5))

        # Body - hunched with fur texture
        body_color = self.color
        body_dark = tuple(max(0, c - 45) for c in body_color)
        body_light = tuple(min(255, c + 25) for c in body_color)

        pygame.draw.ellipse(screen, body_color, (screen_x - 2, y + 12, w + 4, h - 18))
        # Fur shading layers
        pygame.draw.ellipse(screen, body_dark, (screen_x - 2, y + 16, 14, h - 26))
        pygame.draw.arc(screen, body_light, (screen_x + w - 18, y + 18, 16, h - 30), -1.5, 1.5, 4)

        # Fur texture - multiple small strokes
        for i in range(8):
            fur_x = screen_x + 6 + i * 5
            fur_y = y + 18 + (i % 3) * 8
            fur_len = 6 + (i % 2) * 3
            pygame.draw.line(screen, body_dark, (fur_x, fur_y), (fur_x - 2, fur_y + fur_len), 2)
        # Belly fur (lighter)
        pygame.draw.ellipse(screen, body_light, (screen_x + 8, y + 28, w - 16, 18))
        for i in range(4):
            pygame.draw.line(screen, body_color, (screen_x + 12 + i * 6, y + 30),
                           (screen_x + 12 + i * 6, y + 42), 1)

        pygame.draw.ellipse(screen, tuple(max(0, c - 55) for c in body_color),
                          (screen_x - 2, y + 12, w + 4, h - 18), 2)

        # Front legs/arms
        pygame.draw.ellipse(screen, body_color, (screen_x - 6, y + 25 + scurry, 12, 20))
        pygame.draw.ellipse(screen, body_color, (screen_x + w - 6, y + 25 - scurry, 12, 20))
        pygame.draw.ellipse(screen, paw_color, (screen_x - 8, y + 42 + scurry, 12, 8))
        pygame.draw.ellipse(screen, paw_color, (screen_x + w - 4, y + 42 - scurry, 12, 8))

        # Head - pointed snout, beady eyes
        head_color = body_color
        head_y = y - 2

        # Main head shape
        pygame.draw.ellipse(screen, head_color, (screen_x + 4, head_y, w - 8, 24))
        pygame.draw.ellipse(screen, body_dark, (screen_x + 4, head_y + 4, 10, 16))

        # Pointed snout
        snout_x = screen_x + (w - 4 if self.direction > 0 else 4)
        snout_pts = [
            (screen_x + w//2 - 4, head_y + 12),
            (snout_x, head_y + 8),
            (snout_x + 4 * self.direction, head_y + 14),
            (screen_x + w//2 + 4, head_y + 16)
        ]
        pygame.draw.polygon(screen, (160, 140, 130), snout_pts)
        pygame.draw.polygon(screen, (120, 100, 90), snout_pts, 2)
        # Nose
        nose_x = snout_x + 2 * self.direction
        pygame.draw.ellipse(screen, (50, 40, 40), (nose_x - 4, head_y + 8, 8, 6))
        pygame.draw.ellipse(screen, (80, 60, 60), (nose_x - 2, head_y + 9, 3, 3))

        # Round ears
        pygame.draw.ellipse(screen, head_color, (screen_x + 2, head_y - 6, 12, 14))
        pygame.draw.ellipse(screen, (200, 160, 160), (screen_x + 4, head_y - 4, 8, 10))
        pygame.draw.ellipse(screen, head_color, (screen_x + w - 14, head_y - 6, 12, 14))
        pygame.draw.ellipse(screen, (200, 160, 160), (screen_x + w - 12, head_y - 4, 8, 10))

        # Beady red eyes - menacing
        eye_offset = 4 * self.direction
        eye_y = head_y + 8
        # Eye glow
        glow_surf = pygame.Surface((20, 12), pygame.SRCALPHA)
        glow_pulse = int(abs(math.sin(t * 0.008)) * 40)
        pygame.draw.ellipse(glow_surf, (255, 50, 50, 40 + glow_pulse), (0, 0, 20, 12))
        screen.blit(glow_surf, (screen_x + 10 + eye_offset, eye_y - 2))

        pygame.draw.ellipse(screen, self.secondary_color, (screen_x + 12 + eye_offset, eye_y, 8, 6))
        pygame.draw.ellipse(screen, self.secondary_color, (screen_x + w - 20 + eye_offset, eye_y, 8, 6))
        pygame.draw.ellipse(screen, (255, 200, 200), (screen_x + 14 + eye_offset, eye_y + 1, 3, 3))
        pygame.draw.ellipse(screen, (255, 200, 200), (screen_x + w - 18 + eye_offset, eye_y + 1, 3, 3))

        # Whiskers
        whisker_x = snout_x - 4 * self.direction
        for i in range(3):
            wy = head_y + 12 + i * 3
            pygame.draw.line(screen, (80, 70, 65), (whisker_x, wy),
                           (whisker_x - 12 * self.direction, wy - 4 + i * 3), 1)
            pygame.draw.line(screen, (80, 70, 65), (whisker_x, wy),
                           (whisker_x + 12 * self.direction, wy - 2 + i * 2), 1)

        # Teeth (when facing player)
        pygame.draw.polygon(screen, (250, 245, 235), [
            (screen_x + w//2 - 3, head_y + 16), (screen_x + w//2 - 1, head_y + 22), (screen_x + w//2 + 1, head_y + 16)
        ])
        pygame.draw.polygon(screen, (250, 245, 235), [
            (screen_x + w//2 + 1, head_y + 16), (screen_x + w//2 + 3, head_y + 21), (screen_x + w//2 + 5, head_y + 16)
        ])

    def _draw_malfoy(self, screen, screen_x, y):
        """Draw Draco Malfoy - sneering Slytherin student with cel-shaded style."""
        w, h = self.rect.width, self.rect.height
        t = pygame.time.get_ticks()

        # Shadow
        shadow_surf = pygame.Surface((w + 10, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, w + 10, 10))
        screen.blit(shadow_surf, (screen_x - 5, y + h - 5))

        # Slytherin robes - layered for depth
        robe_base = (25, 70, 30)
        robe_dark = (15, 45, 18)
        robe_light = (40, 95, 45)

        # Legs visible under robes
        pygame.draw.rect(screen, (50, 50, 55), (screen_x + 10, y + h - 18, 8, 18))
        pygame.draw.rect(screen, (50, 50, 55), (screen_x + w - 18, y + h - 18, 8, 18))
        pygame.draw.rect(screen, (30, 30, 35), (screen_x + 10, y + h - 6, 8, 6))  # Shoes
        pygame.draw.rect(screen, (30, 30, 35), (screen_x + w - 18, y + h - 6, 8, 6))

        # Main robe body
        pygame.draw.ellipse(screen, robe_base, (screen_x + 2, y + 18, w - 4, h - 22))
        # Shading
        pygame.draw.ellipse(screen, robe_dark, (screen_x + 2, y + 20, 12, h - 28))
        pygame.draw.arc(screen, robe_light, (screen_x + w - 16, y + 24, 12, h - 34), -1.5, 1.5, 3)
        pygame.draw.ellipse(screen, (10, 35, 12), (screen_x + 2, y + 18, w - 4, h - 22), 2)

        # Robe collar and details
        pygame.draw.rect(screen, robe_dark, (screen_x + 8, y + 18, w - 16, 8))
        # Silver Slytherin trim
        pygame.draw.line(screen, SILVER, (screen_x + 6, y + 18), (screen_x + 6, y + h - 10), 2)
        pygame.draw.line(screen, SILVER, (screen_x + w - 6, y + 18), (screen_x + w - 6, y + h - 10), 2)

        # Slytherin tie - silver and green stripes
        tie_points = [
            (screen_x + w//2 - 4, y + 18), (screen_x + w//2 + 4, y + 18),
            (screen_x + w//2 + 3, y + 38), (screen_x + w//2 - 3, y + 38)
        ]
        pygame.draw.polygon(screen, SILVER, tie_points)
        pygame.draw.line(screen, (0, 100, 0), (screen_x + w//2, y + 20), (screen_x + w//2, y + 24), 3)
        pygame.draw.line(screen, (0, 100, 0), (screen_x + w//2, y + 28), (screen_x + w//2, y + 32), 3)
        pygame.draw.polygon(screen, (140, 140, 150), tie_points, 1)

        # Arms
        arm_y = y + 22
        pygame.draw.ellipse(screen, robe_base, (screen_x - 2, arm_y, 12, 24))
        pygame.draw.ellipse(screen, robe_base, (screen_x + w - 10, arm_y, 12, 24))
        # Hands
        pygame.draw.circle(screen, (250, 230, 210), (screen_x + 2, arm_y + 24), 6)
        pygame.draw.circle(screen, (250, 230, 210), (screen_x + w - 2, arm_y + 24), 6)

        # Head - pale aristocratic features
        head_y = y
        face_color = (255, 235, 220)
        face_shadow = (235, 210, 195)

        pygame.draw.ellipse(screen, face_color, (screen_x + 6, head_y, w - 12, 24))
        pygame.draw.ellipse(screen, face_shadow, (screen_x + 6, head_y + 4, 8, 16))
        pygame.draw.ellipse(screen, (220, 195, 180), (screen_x + 6, head_y, w - 12, 24), 2)

        # Slicked back platinum blonde hair
        hair_color = (240, 235, 200)
        hair_dark = (210, 200, 160)
        hair_highlight = (255, 250, 230)

        pygame.draw.ellipse(screen, hair_color, (screen_x + 4, head_y - 4, w - 8, 16))
        pygame.draw.arc(screen, hair_highlight, (screen_x + 8, head_y - 2, w - 16, 10), 0.5, 2.5, 2)
        pygame.draw.arc(screen, hair_dark, (screen_x + 4, head_y - 4, w - 8, 16), 3.5, 6.0, 2)
        # Side part
        pygame.draw.line(screen, hair_dark, (screen_x + 12, head_y), (screen_x + 8, head_y + 8), 2)

        # Sneering face - arrogant expression
        eye_offset = 3 if self.direction > 0 else -3
        eye_y = head_y + 8

        # Angry/arrogant eyebrows
        pygame.draw.line(screen, hair_dark, (screen_x + 10 + eye_offset, eye_y - 2),
                        (screen_x + 16 + eye_offset, eye_y), 2)
        pygame.draw.line(screen, hair_dark, (screen_x + w - 10 + eye_offset, eye_y - 2),
                        (screen_x + w - 16 + eye_offset, eye_y), 2)

        # Narrowed contemptuous eyes
        pygame.draw.ellipse(screen, (240, 240, 245), (screen_x + 10 + eye_offset, eye_y, 8, 5))
        pygame.draw.ellipse(screen, (240, 240, 245), (screen_x + w - 18 + eye_offset, eye_y, 8, 5))
        # Grey-blue irises
        pygame.draw.ellipse(screen, (120, 130, 145), (screen_x + 12 + eye_offset, eye_y + 1, 4, 3))
        pygame.draw.ellipse(screen, (120, 130, 145), (screen_x + w - 16 + eye_offset, eye_y + 1, 4, 3))
        pygame.draw.ellipse(screen, (60, 70, 80), (screen_x + 10 + eye_offset, eye_y, 8, 5), 1)
        pygame.draw.ellipse(screen, (60, 70, 80), (screen_x + w - 18 + eye_offset, eye_y, 8, 5), 1)

        # Pointed nose
        pygame.draw.polygon(screen, face_shadow, [
            (screen_x + w//2, eye_y + 4),
            (screen_x + w//2 - 2, eye_y + 10),
            (screen_x + w//2 + 2, eye_y + 10)
        ])

        # Sneering smirk
        pygame.draw.arc(screen, (180, 120, 120), (screen_x + w//2 - 6, head_y + 14, 12, 6), 0.3, 2.8, 2)
        pygame.draw.arc(screen, (200, 140, 140), (screen_x + w//2 + 2, head_y + 15, 6, 4), 3.5, 6.0, 2)

        # Wand - hawthorn with unicorn hair
        wand_x = screen_x + (w + 4 if self.direction > 0 else -14)
        wand_end_x = wand_x + 16 * self.direction
        # Wand body
        pygame.draw.line(screen, (90, 60, 40), (wand_x, y + 28), (wand_end_x, y + 22), 4)
        pygame.draw.line(screen, (120, 85, 55), (wand_x + 2, y + 27), (wand_end_x, y + 21), 2)
        # Wand handle detail
        pygame.draw.circle(screen, (70, 45, 30), (wand_x, y + 28), 4)

        # Spell effect when attacking
        if hasattr(self, 'shoot_cooldown') and self.shoot_cooldown > self.shoot_interval * 0.8:
            glow_x = wand_end_x + 4 * self.direction
            # Slytherin green spell
            glow_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
            glow_intensity = int(150 + math.sin(t * 0.02) * 50)
            pygame.draw.circle(glow_surf, (0, 200, 50, glow_intensity), (12, 12), 10)
            pygame.draw.circle(glow_surf, (100, 255, 150, glow_intensity), (12, 12), 5)
            screen.blit(glow_surf, (glow_x - 12, y + 10))

    def _draw_troll(self, screen, screen_x, y):
        """Draw Mountain Troll - huge, dumb, and dangerous."""
        w, h = self.rect.width, self.rect.height

        # Big shadow
        shadow_surf = pygame.Surface((w + 20, 15), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, w + 20, 15))
        screen.blit(shadow_surf, (screen_x - 10, y + h - 8))

        # Massive body
        body_color = (90, 100, 85)
        pygame.draw.ellipse(screen, body_color, (screen_x - 5, y + 25, w + 10, h - 20))
        pygame.draw.ellipse(screen, (60, 70, 55), (screen_x - 5, y + 25, w + 10, h - 20), 3)

        # Belly
        belly_color = (110, 115, 100)
        pygame.draw.ellipse(screen, belly_color, (screen_x + 5, y + 40, w - 10, h - 50))

        # Stubby legs
        leg_color = (80, 85, 75)
        pygame.draw.ellipse(screen, leg_color, (screen_x, y + h - 25, 20, 30))
        pygame.draw.ellipse(screen, leg_color, (screen_x + w - 20, y + h - 25, 20, 30))

        # Small stupid head
        head_color = (95, 105, 90)
        pygame.draw.ellipse(screen, head_color, (screen_x + w//2 - 15, y, 30, 35))
        pygame.draw.ellipse(screen, (65, 75, 60), (screen_x + w//2 - 15, y, 30, 35), 2)

        # Tiny dumb eyes
        eye_x = screen_x + w//2 - 8
        pygame.draw.circle(screen, (200, 180, 100), (eye_x, y + 12), 5)
        pygame.draw.circle(screen, (200, 180, 100), (eye_x + 16, y + 12), 5)
        pygame.draw.circle(screen, BLACK, (eye_x, y + 12), 3)
        pygame.draw.circle(screen, BLACK, (eye_x + 16, y + 12), 3)

        # Big nose
        pygame.draw.ellipse(screen, (75, 85, 70), (screen_x + w//2 - 6, y + 16, 12, 10))

        # Dumb mouth
        pygame.draw.ellipse(screen, (50, 50, 45), (screen_x + w//2 - 8, y + 26, 16, 8))

        # Giant club
        club_x = screen_x + (w + 5 if self.direction > 0 else -25)
        # Club handle
        pygame.draw.rect(screen, (90, 60, 40), (club_x + 5, y + 15, 12, 60), border_radius=3)
        # Club head
        pygame.draw.ellipse(screen, (70, 50, 35), (club_x, y - 10, 25, 35))
        pygame.draw.ellipse(screen, (50, 35, 25), (club_x, y - 10, 25, 35), 2)

    def _draw_fluffy(self, screen, screen_x, y):
        """Draw Fluffy the three-headed dog - fearsome guardian."""
        w, h = self.rect.width, self.rect.height

        # Shadow
        shadow_surf = pygame.Surface((w + 10, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 55), (0, 0, w + 10, 12))
        screen.blit(shadow_surf, (screen_x - 5, y + h - 6))

        # Large furry body
        body_color = self.color
        pygame.draw.ellipse(screen, body_color, (screen_x, y + 25, w, h - 20))
        darker = tuple(max(0, c - 30) for c in body_color)
        pygame.draw.ellipse(screen, darker, (screen_x, y + 25, w, h - 20), 3)

        # Fur texture lines
        for i in range(5):
            fx = screen_x + 10 + i * 12
            pygame.draw.arc(screen, darker, (fx, y + 35, 10, 20), 0, 3.14, 2)

        # Three heads!
        head_positions = [
            (screen_x + 5, y - 5),      # Left head
            (screen_x + w//2 - 12, y - 15),  # Center head (higher)
            (screen_x + w - 30, y - 5)   # Right head
        ]

        for i, (hx, hy) in enumerate(head_positions):
            # Head
            pygame.draw.ellipse(screen, body_color, (hx, hy, 25, 30))
            pygame.draw.ellipse(screen, darker, (hx, hy, 25, 30), 2)

            # Ears
            pygame.draw.ellipse(screen, body_color, (hx - 3, hy - 5, 10, 15))
            pygame.draw.ellipse(screen, body_color, (hx + 18, hy - 5, 10, 15))

            # Eyes (angry!)
            pygame.draw.ellipse(screen, (255, 200, 50), (hx + 5, hy + 8, 6, 5))
            pygame.draw.ellipse(screen, (255, 200, 50), (hx + 14, hy + 8, 6, 5))
            pygame.draw.ellipse(screen, BLACK, (hx + 6, hy + 9, 4, 4))
            pygame.draw.ellipse(screen, BLACK, (hx + 15, hy + 9, 4, 4))

            # Angry eyebrows
            pygame.draw.line(screen, BLACK, (hx + 3, hy + 6), (hx + 10, hy + 8), 2)
            pygame.draw.line(screen, BLACK, (hx + 22, hy + 6), (hx + 15, hy + 8), 2)

            # Snout with fangs
            pygame.draw.ellipse(screen, (100, 70, 50), (hx + 6, hy + 15, 14, 12))
            # Open mouth with teeth
            pygame.draw.ellipse(screen, (60, 30, 30), (hx + 8, hy + 20, 10, 8))
            # Fangs
            pygame.draw.polygon(screen, WHITE, [(hx + 8, hy + 20), (hx + 6, hy + 28), (hx + 10, hy + 22)])
            pygame.draw.polygon(screen, WHITE, [(hx + 18, hy + 20), (hx + 20, hy + 28), (hx + 16, hy + 22)])

        # Paws
        paw_color = (120, 80, 40)
        pygame.draw.ellipse(screen, paw_color, (screen_x + 5, y + h - 15, 18, 12))
        pygame.draw.ellipse(screen, paw_color, (screen_x + w - 23, y + h - 15, 18, 12))

    def _draw_devil_snare(self, screen, screen_x, y):
        """Draw Devil's Snare - creepy tentacle plant."""
        w, h = self.rect.width, self.rect.height

        # Animated tendrils
        t = pygame.time.get_ticks() / 200

        # Base mound
        pygame.draw.ellipse(screen, (15, 50, 15), (screen_x - 5, y + h - 20, w + 10, 25))

        # Creepy tendrils reaching out
        tendril_color = self.color
        for i in range(6):
            angle = i * 0.9 + math.sin(t + i) * 0.3
            length = 30 + 15 * math.sin(t * 0.5 + i * 2)
            end_x = screen_x + w//2 + math.cos(angle) * length
            end_y = y + h - 15 + math.sin(angle) * length * 0.5 - length * 0.7

            # Draw curved tendril
            mid_x = screen_x + w//2 + math.cos(angle) * length * 0.5
            mid_y = y + h - 15 + math.sin(angle + 0.3) * length * 0.3 - length * 0.3

            pygame.draw.line(screen, tendril_color, (screen_x + w//2, y + h - 15), (mid_x, mid_y), 6)
            pygame.draw.line(screen, tendril_color, (mid_x, mid_y), (end_x, end_y), 4)
            pygame.draw.circle(screen, tendril_color, (int(end_x), int(end_y)), 5)

            # Darker outline
            darker = tuple(max(0, c - 20) for c in tendril_color)
            pygame.draw.circle(screen, darker, (int(end_x), int(end_y)), 5, 1)

        # Central mass
        pygame.draw.ellipse(screen, self.secondary_color, (screen_x + 5, y + h - 30, w - 10, 20))

        # Glowing spots (warning!)
        for i in range(3):
            spot_x = screen_x + 12 + i * 10
            spot_y = y + h - 22
            glow = int(abs(math.sin(t + i)) * 100)
            pygame.draw.circle(screen, (glow, 150 + glow//2, glow), (spot_x, spot_y), 4)

    def _draw_flying_key(self, screen, screen_x, y):
        """Draw Flying Key - ornate antique brass key with feathered wings."""
        w, h = self.rect.width, self.rect.height
        t = pygame.time.get_ticks()

        # Wing flap animation - smooth and bird-like
        wing_flap = math.sin(t * 0.025) * 15
        wing_tilt = math.cos(t * 0.025) * 0.2

        # Magical golden glow aura
        glow_surf = pygame.Surface((w + 30, h + 30), pygame.SRCALPHA)
        glow_pulse = int(abs(math.sin(t * 0.004)) * 40)
        pygame.draw.ellipse(glow_surf, (255, 215, 100, 40 + glow_pulse), (0, 0, w + 30, h + 30))
        pygame.draw.ellipse(glow_surf, (255, 230, 150, 25 + glow_pulse//2), (5, 5, w + 20, h + 20))
        screen.blit(glow_surf, (screen_x - 15, y - 15))

        # Sparkle trail
        for i in range(5):
            spark_angle = t * 0.01 + i * 1.2
            spark_dist = 18 + i * 4
            spark_x = screen_x + w//2 + int(math.cos(spark_angle) * spark_dist)
            spark_y = y + h//2 + int(math.sin(spark_angle) * spark_dist * 0.6)
            spark_alpha = 150 - i * 25
            spark_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(spark_surf, (255, 255, 200, spark_alpha), (3, 3), 3 - i//2)
            screen.blit(spark_surf, (spark_x - 3, spark_y - 3))

        # Detailed feathered wings - Left wing
        wing_base_color = (220, 200, 160)
        wing_gold = (240, 215, 140)
        wing_dark = (180, 155, 100)
        wing_highlight = (255, 245, 210)

        # Left wing - layered feathers
        left_wing_x = screen_x + w//2 - 6
        left_wing_offset = int(wing_flap)

        # Primary feathers (outer)
        for i in range(4):
            feather_x = left_wing_x - 8 - i * 6 + left_wing_offset // 3
            feather_y = y + 8 + i * 4 - abs(left_wing_offset) // 2
            feather_pts = [
                (left_wing_x, y + 18),
                (feather_x - 4, feather_y),
                (feather_x - 8, feather_y + 8),
                (left_wing_x - 5, y + 25)
            ]
            color = wing_gold if i % 2 == 0 else wing_base_color
            pygame.draw.polygon(screen, color, feather_pts)
            pygame.draw.polygon(screen, wing_dark, feather_pts, 1)

        # Secondary feathers (inner)
        for i in range(3):
            feather_x = left_wing_x - 4 - i * 5 + left_wing_offset // 4
            feather_y = y + 12 + i * 5 - abs(left_wing_offset) // 3
            pygame.draw.ellipse(screen, wing_highlight, (feather_x, feather_y, 10, 16))
            pygame.draw.ellipse(screen, wing_dark, (feather_x, feather_y, 10, 16), 1)

        # Right wing - mirror
        right_wing_x = screen_x + w//2 + 6
        right_wing_offset = -int(wing_flap)

        for i in range(4):
            feather_x = right_wing_x + 8 + i * 6 - right_wing_offset // 3
            feather_y = y + 8 + i * 4 - abs(right_wing_offset) // 2
            feather_pts = [
                (right_wing_x, y + 18),
                (feather_x + 4, feather_y),
                (feather_x + 8, feather_y + 8),
                (right_wing_x + 5, y + 25)
            ]
            color = wing_gold if i % 2 == 0 else wing_base_color
            pygame.draw.polygon(screen, color, feather_pts)
            pygame.draw.polygon(screen, wing_dark, feather_pts, 1)

        for i in range(3):
            feather_x = right_wing_x + 4 + i * 5 - right_wing_offset // 4
            feather_y = y + 12 + i * 5 - abs(right_wing_offset) // 3
            pygame.draw.ellipse(screen, wing_highlight, (feather_x - 10, feather_y, 10, 16))
            pygame.draw.ellipse(screen, wing_dark, (feather_x - 10, feather_y, 10, 16), 1)

        # Ornate key body
        key_gold = (230, 195, 80)
        key_dark = (180, 145, 40)
        key_highlight = (255, 235, 150)
        key_shadow = (140, 110, 30)

        # Key bow (ornate handle) - intricate design
        bow_x = screen_x + w//2
        bow_y = y + 6

        # Outer ornate frame
        pygame.draw.ellipse(screen, key_gold, (bow_x - 10, bow_y, 20, 22))
        pygame.draw.ellipse(screen, key_dark, (bow_x - 10, bow_y, 20, 22), 2)
        # Inner cutout
        pygame.draw.ellipse(screen, (60, 50, 30), (bow_x - 6, bow_y + 5, 12, 12))
        # Decorative details
        pygame.draw.circle(screen, key_highlight, (bow_x - 6, bow_y + 5), 3)
        pygame.draw.circle(screen, key_highlight, (bow_x + 6, bow_y + 5), 3)
        pygame.draw.circle(screen, key_highlight, (bow_x, bow_y + 2), 2)
        # Top crown
        pygame.draw.polygon(screen, key_gold, [
            (bow_x - 6, bow_y), (bow_x, bow_y - 5), (bow_x + 6, bow_y)
        ])
        pygame.draw.polygon(screen, key_dark, [
            (bow_x - 6, bow_y), (bow_x, bow_y - 5), (bow_x + 6, bow_y)
        ], 1)

        # Key shaft with detail
        shaft_x = bow_x - 3
        pygame.draw.rect(screen, key_gold, (shaft_x, bow_y + 20, 6, 22))
        pygame.draw.rect(screen, key_shadow, (shaft_x, bow_y + 20, 2, 22))
        pygame.draw.rect(screen, key_highlight, (shaft_x + 4, bow_y + 20, 2, 22))
        pygame.draw.rect(screen, key_dark, (shaft_x, bow_y + 20, 6, 22), 1)
        # Shaft ring detail
        pygame.draw.rect(screen, key_dark, (shaft_x - 1, bow_y + 26, 8, 3))
        pygame.draw.rect(screen, key_highlight, (shaft_x, bow_y + 27, 6, 1))

        # Key bit (teeth) - ornate
        bit_y = bow_y + 40
        pygame.draw.rect(screen, key_gold, (shaft_x - 6, bit_y, 10, 8))
        pygame.draw.rect(screen, key_gold, (shaft_x - 3, bit_y + 6, 6, 5))
        pygame.draw.rect(screen, key_gold, (shaft_x + 2, bit_y + 3, 6, 6))
        # Teeth details
        pygame.draw.rect(screen, key_shadow, (shaft_x - 6, bit_y, 3, 8))
        pygame.draw.rect(screen, key_highlight, (shaft_x + 1, bit_y + 1, 2, 6))
        pygame.draw.rect(screen, key_dark, (shaft_x - 6, bit_y, 10, 8), 1)
        pygame.draw.rect(screen, key_dark, (shaft_x - 3, bit_y + 6, 6, 5), 1)

        # Magical sparkle at key tip
        if int(t / 80) % 4 == 0:
            sparkle_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.line(sparkle_surf, (255, 255, 255, 200), (6, 0), (6, 12), 2)
            pygame.draw.line(sparkle_surf, (255, 255, 255, 200), (0, 6), (12, 6), 2)
            pygame.draw.line(sparkle_surf, (255, 255, 255, 150), (2, 2), (10, 10), 1)
            pygame.draw.line(sparkle_surf, (255, 255, 255, 150), (10, 2), (2, 10), 1)
            screen.blit(sparkle_surf, (bow_x - 6, bit_y + 6))

    def _draw_chess_piece(self, screen, screen_x, y):
        """Draw Chess Knight - imposing stone warrior."""
        w, h = self.rect.width, self.rect.height

        # Shadow
        shadow_surf = pygame.Surface((w + 10, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, w + 10, 10))
        screen.blit(shadow_surf, (screen_x - 5, y + h - 5))

        # Base pedestal
        pygame.draw.rect(screen, (40, 40, 45), (screen_x, y + h - 15, w, 15), border_radius=3)
        pygame.draw.rect(screen, (25, 25, 30), (screen_x, y + h - 15, w, 15), 2, border_radius=3)

        # Knight body (chess piece shape)
        body_color = self.color
        pygame.draw.ellipse(screen, body_color, (screen_x + 5, y + 30, w - 10, h - 45))
        pygame.draw.ellipse(screen, (20, 20, 25), (screen_x + 5, y + 30, w - 10, h - 45), 2)

        # Horse head shape
        head_pts = [
            (screen_x + w//2, y + 5),      # Top
            (screen_x + w - 8, y + 15),     # Ear
            (screen_x + w - 5, y + 35),     # Back of head
            (screen_x + w//2, y + 40),      # Neck
            (screen_x + 5, y + 30),         # Front neck
            (screen_x + 2, y + 15),         # Muzzle
            (screen_x + 10, y + 8),         # Forehead
        ]
        pygame.draw.polygon(screen, body_color, head_pts)
        pygame.draw.polygon(screen, (20, 20, 25), head_pts, 2)

        # Mane detail
        for i in range(4):
            mx = screen_x + w//2 + 5 + i * 4
            my = y + 15 + i * 5
            pygame.draw.line(screen, self.secondary_color, (mx, my), (mx + 5, my + 8), 2)

        # Eye (glowing)
        glow = int(abs(math.sin(pygame.time.get_ticks() / 300)) * 50)
        pygame.draw.circle(screen, (150 + glow, 50, 50), (screen_x + 15 + (5 if self.direction > 0 else 0), y + 18), 4)
        pygame.draw.circle(screen, (255, 150, 150), (screen_x + 15 + (5 if self.direction > 0 else 0), y + 18), 2)

        # Stone texture cracks
        pygame.draw.line(screen, (45, 45, 50), (screen_x + 15, y + 45), (screen_x + 25, y + 55), 1)
        pygame.draw.line(screen, (45, 45, 50), (screen_x + w - 15, y + 50), (screen_x + w - 25, y + 60), 1)

    def _draw_quirrell(self, screen, screen_x, y):
        """Draw Professor Quirrell with Voldemort on back - final boss aesthetic."""
        w, h = self.rect.width, self.rect.height
        t = pygame.time.get_ticks()

        # Dark aura effect
        aura_size = 8 + int(math.sin(t * 0.005) * 3)
        aura_surf = pygame.Surface((w + aura_size * 2, h + aura_size * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(aura_surf, (80, 0, 80, 40), (0, 0, w + aura_size * 2, h + aura_size * 2))
        screen.blit(aura_surf, (screen_x - aura_size, y - aura_size))

        # Shadow
        shadow_surf = pygame.Surface((w + 10, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 70), (0, 0, w + 10, 10))
        screen.blit(shadow_surf, (screen_x - 5, y + h - 5))

        # Purple robes
        robe_color = self.color
        pygame.draw.ellipse(screen, robe_color, (screen_x + 3, y + 20, w - 6, h - 18))
        pygame.draw.ellipse(screen, (50, 0, 50), (screen_x + 3, y + 20, w - 6, h - 18), 2)

        # Turban (hiding Voldemort)
        turban_color = (120, 80, 140)
        pygame.draw.ellipse(screen, turban_color, (screen_x + 8, y - 5, w - 16, 35))
        pygame.draw.ellipse(screen, (80, 50, 100), (screen_x + 8, y - 5, w - 16, 35), 2)
        # Turban wrappings
        for i in range(3):
            wrap_y = y + i * 8
            pygame.draw.arc(screen, (100, 60, 120), (screen_x + 10, wrap_y, w - 20, 12), 0, 3.14, 2)

        # Face (nervous/sweating)
        face_x = screen_x + w//2
        pygame.draw.ellipse(screen, (240, 220, 200), (screen_x + 12, y + 15, w - 24, 20))

        # Nervous eyes
        pygame.draw.ellipse(screen, WHITE, (screen_x + 16, y + 20, 8, 6))
        pygame.draw.ellipse(screen, WHITE, (screen_x + w - 24, y + 20, 8, 6))
        pygame.draw.circle(screen, BLACK, (screen_x + 20, y + 23), 2)
        pygame.draw.circle(screen, BLACK, (screen_x + w - 20, y + 23), 2)

        # Sweat drop
        if int(t / 500) % 2 == 0:
            pygame.draw.ellipse(screen, (150, 200, 255), (screen_x + w - 15, y + 18, 4, 6))

        # Voldemort's face on back of turban (creepy!)
        voldy_alpha = int(128 + math.sin(t * 0.003) * 50)
        voldy_surf = pygame.Surface((30, 30), pygame.SRCALPHA)

        # Snake-like face
        pygame.draw.ellipse(voldy_surf, (*self.secondary_color, voldy_alpha), (5, 0, 20, 28))
        # Red eyes
        pygame.draw.circle(voldy_surf, (255, 0, 0), (10, 10), 3)
        pygame.draw.circle(voldy_surf, (255, 0, 0), (20, 10), 3)
        # Slits for nose
        pygame.draw.line(voldy_surf, (100, 0, 0), (14, 16), (13, 20), 2)
        pygame.draw.line(voldy_surf, (100, 0, 0), (16, 16), (17, 20), 2)
        # Evil grin
        pygame.draw.arc(voldy_surf, (100, 0, 0), (8, 20, 14, 8), 3.14, 0, 2)

        # Position on back of head
        voldy_x = screen_x + w//2 - 15 - (10 if self.direction > 0 else -10)
        screen.blit(voldy_surf, (voldy_x, y))

        # Wand with dark magic
        wand_x = screen_x + (w + 5 if self.direction > 0 else -15)
        pygame.draw.line(screen, (60, 40, 30), (wand_x, y + 30), (wand_x + 12 * self.direction, y + 25), 3)

        # Dark magic particles
        for i in range(3):
            px = wand_x + 15 * self.direction + int(math.cos(t * 0.01 + i * 2) * 10)
            py = y + 20 + int(math.sin(t * 0.01 + i * 2) * 8)
            pygame.draw.circle(screen, (150, 0, 150), (px, py), 3)


class Boss:
    """Final boss enemy - Dark Wizard!"""
    
    WIDTH = 80
    HEIGHT = 120
    
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(int(x), int(y), self.WIDTH, self.HEIGHT)
        
        # Boss stats - VERY tough
        self.health = 500
        self.max_health = 500
        self.damage = 20
        self.speed = 2.0
        self.direction = -1
        
        # Boss phases
        self.phase = 1  # Phase 1: basic attacks, Phase 2: faster, Phase 3: enraged
        self.previous_phase = 1  # Track for phase transition effects
        self.phase_transition_timer = 0  # Timer for phase change popup

        # Attack patterns
        self.attack_cooldown = 0
        self.attack_pattern = 0  # 0: melee swing, 1: projectiles, 2: ground slam
        self.projectiles = []
        
        # Animation
        self.anim_timer = 0
        self.is_attacking = False
        self.attack_anim_timer = 0
        self.hover_offset = 0
        self.flash_timer = 0

        # Attack telegraphing (charge-up before attacks)
        self.is_charging = False
        self.charge_timer = 0
        self.charge_duration = 600  # 600ms charge before attack
        self.pending_attack_target = None

        # State
        self.active = True
        self.defeated = False

        # Death animation
        self.death_timer = 0
        self.death_duration = 2000  # 2 seconds death animation
        self.death_particles = []
        
    def _check_edge(self, platforms, direction):
        """Check if there's an edge in the given direction."""
        check_x = self.x + self.WIDTH // 2 + (self.WIDTH // 2 + 20) * direction
        check_y = self.y + self.HEIGHT + 10
        for platform in platforms:
            if (platform.rect.left - 10 <= check_x <= platform.rect.right + 10 and
                platform.rect.top <= check_y <= platform.rect.top + 40):
                return False  # Ground found
        return True  # Edge

    def update(self, players, dt, platforms=None):
        # Handle death animation
        if self.defeated:
            self.death_timer += dt
            # Update death particles
            for p in self.death_particles[:]:
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['vy'] += 0.2  # Gravity
                p['life'] -= dt
                p['alpha'] = max(0, int(255 * (p['life'] / 800)))
                if p['life'] <= 0:
                    self.death_particles.remove(p)
            # Spawn new particles during death
            if self.death_timer < 1500 and random.random() < 0.3:
                for _ in range(3):
                    self.death_particles.append({
                        'x': self.x + random.randint(0, self.WIDTH),
                        'y': self.y + random.randint(0, self.HEIGHT),
                        'vx': random.uniform(-3, 3),
                        'vy': random.uniform(-5, -1),
                        'life': random.randint(500, 1000),
                        'alpha': 255,
                        'color': random.choice([(150, 50, 150), (100, 0, 100), (200, 100, 200), (80, 0, 80)])
                    })
            return

        if not self.active:
            return

        self.anim_timer += dt

        # Update phase transition timer
        if self.phase_transition_timer > 0:
            self.phase_transition_timer -= dt

        # Update phase based on health (with transition detection)
        new_phase = self.phase
        if self.health <= self.max_health * 0.3:
            new_phase = 3
            self.speed = 3.5
        elif self.health <= self.max_health * 0.6:
            new_phase = 2
            self.speed = 2.8

        # Detect phase transition
        if new_phase != self.previous_phase:
            self.phase = new_phase
            self.previous_phase = new_phase
            self.phase_transition_timer = 2000  # Show "PHASE X!" for 2 seconds

        # Find nearest player
        nearest_player = None
        min_dist = float('inf')
        for p in players:
            if p.is_alive():
                dist = abs(p.x - self.x)
                if dist < min_dist:
                    min_dist = dist
                    nearest_player = p

        if not nearest_player:
            return

        # Face player
        if nearest_player.x < self.x:
            self.direction = -1
        else:
            self.direction = 1

        # Smart edge detection
        edge_left = self._check_edge(platforms, -1) if platforms else False
        edge_right = self._check_edge(platforms, 1) if platforms else False

        # Tactical movement - boss keeps optimal attack distance
        ideal_distance = 120
        move_direction = 0

        if min_dist > ideal_distance + 50:
            # Too far - move toward player
            move_direction = self.direction
        elif min_dist < ideal_distance - 30:
            # Too close - back away
            move_direction = -self.direction
        else:
            # Good distance - strafe occasionally
            if int(self.anim_timer / 1000) % 4 == 0:
                move_direction = 1 if random.random() > 0.5 else -1
            else:
                move_direction = 0

        # Apply movement with edge awareness
        if move_direction != 0:
            blocked = (move_direction < 0 and edge_left) or (move_direction > 0 and edge_right)
            if not blocked:
                self.x += self.speed * move_direction
            elif move_direction == self.direction:
                # Can't reach player - try the other direction or stay put
                opposite_blocked = (move_direction > 0 and edge_left) or (move_direction < 0 and edge_right)
                if not opposite_blocked:
                    # Strafe to the side that's safe
                    self.x += self.speed * (-move_direction) * 0.3

        # Keep boss in reasonable bounds
        if self.x < 50:
            self.x = 50
        if self.x > LEVEL_WIDTH - self.WIDTH - 50:
            self.x = LEVEL_WIDTH - self.WIDTH - 50

        # Hovering effect
        self.hover_offset = math.sin(self.anim_timer * 0.003) * 8

        # Attack logic with telegraph/charging
        if self.is_charging:
            # Currently charging up an attack
            self.charge_timer += dt
            if self.charge_timer >= self.charge_duration:
                # Charge complete - execute attack
                self.is_charging = False
                self.charge_timer = 0
                self._execute_attack(self.pending_attack_target)
        elif self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        else:
            # Start charging for new attack
            self._start_charge(nearest_player)

        # Update attack animation
        if self.attack_anim_timer > 0:
            self.attack_anim_timer -= dt
            if self.attack_anim_timer <= 0:
                self.is_attacking = False
        
        # Update projectiles
        for proj in self.projectiles[:]:
            proj['x'] += proj['vx']
            proj['y'] += proj['vy']
            proj['life'] -= dt
            if proj['life'] <= 0:
                self.projectiles.remove(proj)
        
        # Flash timer
        if self.flash_timer > 0:
            self.flash_timer -= dt
        
        self.rect.x = int(self.x)
        self.rect.y = int(self.y + self.hover_offset)
    
    def _start_charge(self, player):
        """Begin charging up for an attack (telegraph phase)."""
        self.is_charging = True
        self.charge_timer = 0
        self.pending_attack_target = player

        # Determine which attack pattern will be used
        if self.phase == 1:
            patterns = [0, 1]  # Melee and single projectile
        elif self.phase == 2:
            patterns = [0, 1, 1, 2]  # Add ground slam
        else:
            patterns = [0, 1, 1, 1, 2]  # More projectiles

        self.attack_pattern = patterns[int(self.anim_timer / 1000) % len(patterns)]

        # Adjust charge duration based on phase (faster in later phases)
        self.charge_duration = max(300, 600 - (self.phase - 1) * 100)

    def _execute_attack(self, player):
        """Execute an attack pattern after charge completes."""
        self.is_attacking = True
        self.attack_anim_timer = 500

        if self.attack_pattern == 0:
            # Melee swing - creates attack rect
            self.attack_cooldown = 1500 / self.phase
        elif self.attack_pattern == 1:
            # Fire projectiles
            num_projectiles = self.phase
            for i in range(num_projectiles):
                angle = -20 + (40 * i / max(1, num_projectiles - 1)) if num_projectiles > 1 else 0
                rad = math.radians(angle)
                self.projectiles.append({
                    'x': self.x + self.WIDTH // 2,
                    'y': self.y + self.HEIGHT // 3,
                    'vx': math.cos(rad) * 8 * self.direction,
                    'vy': math.sin(rad) * 8,
                    'life': 2000,
                    'damage': 15
                })
            self.attack_cooldown = 2000 / self.phase
        elif self.attack_pattern == 2:
            # Ground slam - shockwave (handled via projectiles going outward)
            for i in range(8):
                angle = (i / 8) * math.pi * 2
                self.projectiles.append({
                    'x': self.x + self.WIDTH // 2,
                    'y': self.y + self.HEIGHT,
                    'vx': math.cos(angle) * 5,
                    'vy': math.sin(angle) * 3 - 2,
                    'life': 1500,
                    'damage': 10,
                    'is_shockwave': True
                })
            self.attack_cooldown = 3000 / self.phase
    
    def get_attack_rect(self):
        """Get melee attack rect if attacking with melee."""
        if self.is_attacking and self.attack_pattern == 0:
            if self.direction > 0:
                return pygame.Rect(self.rect.right, self.rect.top, 80, self.HEIGHT)
            else:
                return pygame.Rect(self.rect.left - 80, self.rect.top, 80, self.HEIGHT)
        return None
    
    def take_damage(self, amount):
        self.health -= amount
        self.flash_timer = 150
        if self.health <= 0:
            self.health = 0
            self.defeated = True
            # Start death animation - spawn initial explosion of particles
            for _ in range(30):
                self.death_particles.append({
                    'x': self.x + random.randint(0, self.WIDTH),
                    'y': self.y + random.randint(0, self.HEIGHT),
                    'vx': random.uniform(-5, 5),
                    'vy': random.uniform(-8, -2),
                    'life': random.randint(600, 1200),
                    'alpha': 255,
                    'color': random.choice([(150, 50, 150), (100, 0, 100), (200, 100, 200), (255, 100, 255)])
                })
            return True
        return False
    
    def is_alive(self):
        return not self.defeated and self.health > 0

    def is_death_animation_complete(self):
        """Check if death animation has finished."""
        return self.defeated and self.death_timer >= self.death_duration
    
    def draw(self, screen, camera_x):
        screen_x = int(self.x - camera_x)
        y = int(self.y + self.hover_offset)

        if screen_x < -self.WIDTH or screen_x > SCREEN_WIDTH + self.WIDTH:
            return

        # Draw death animation
        if self.defeated:
            # Draw fading boss
            if self.death_timer < 1500:
                fade_alpha = max(0, int(255 * (1 - self.death_timer / 1500)))
                fade_surf = pygame.Surface((self.WIDTH + 20, self.HEIGHT + 20), pygame.SRCALPHA)

                # Draw shrinking/fading boss silhouette
                shrink = self.death_timer / 1500 * 0.5
                draw_w = int(self.WIDTH * (1 - shrink))
                draw_h = int(self.HEIGHT * (1 - shrink))
                offset_x = (self.WIDTH - draw_w) // 2
                offset_y = (self.HEIGHT - draw_h) // 2

                # Purple dissolving effect
                pygame.draw.ellipse(fade_surf, (100, 0, 100, fade_alpha),
                                   (offset_x + 10, offset_y + 10, draw_w, draw_h))
                screen.blit(fade_surf, (screen_x - 10, y - 10))

            # Draw death particles
            for p in self.death_particles:
                px = int(p['x'] - camera_x)
                py = int(p['y'])
                if 0 <= px <= SCREEN_WIDTH:
                    particle_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
                    alpha = max(0, min(255, int(p['alpha'])))
                    color_with_alpha = (p['color'][0], p['color'][1], p['color'][2], alpha)
                    pygame.draw.circle(particle_surf, color_with_alpha, (6, 6), 6)
                    screen.blit(particle_surf, (px - 6, py - 6))

            # "DEFEATED!" text
            if self.death_timer < 2000:
                font = pygame.font.Font(None, 48)
                text_alpha = min(255, int(self.death_timer / 500 * 255))
                if self.death_timer > 1500:
                    text_alpha = max(0, int(255 * (1 - (self.death_timer - 1500) / 500)))
                text_surf = font.render("DEFEATED!", True, (255, 200, 50))
                text_surf.set_alpha(text_alpha)
                text_x = screen_x + self.WIDTH // 2 - text_surf.get_width() // 2
                screen.blit(text_surf, (text_x, y - 50))
            return

        if not self.active:
            return

        # Flash when damaged
        if self.flash_timer > 0 and int(self.flash_timer / 50) % 2 == 0:
            return
        
        # Draw boss - Dark Wizard appearance
        # Robe body
        robe_color = (40, 20, 50) if self.phase == 1 else (60, 20, 40) if self.phase == 2 else (80, 20, 30)
        pygame.draw.ellipse(screen, robe_color, (screen_x + 10, y + 40, 60, 80))
        pygame.draw.ellipse(screen, (30, 15, 40), (screen_x + 10, y + 40, 60, 80), 2)
        
        # Hood/head
        hood_color = (50, 25, 60)
        pygame.draw.ellipse(screen, hood_color, (screen_x + 15, y + 5, 50, 50))
        pygame.draw.ellipse(screen, (30, 15, 35), (screen_x + 15, y + 5, 50, 50), 2)
        
        # Glowing eyes
        eye_color = (255, 50, 50) if self.phase < 3 else (255, 100, 100)
        eye_glow = int(abs(math.sin(self.anim_timer * 0.005)) * 50)
        pygame.draw.circle(screen, (eye_color[0], eye_glow, eye_glow), 
                          (screen_x + 28 + (5 if self.direction > 0 else 0), y + 25), 6)
        pygame.draw.circle(screen, (eye_color[0], eye_glow, eye_glow), 
                          (screen_x + 48 + (5 if self.direction > 0 else 0), y + 25), 6)
        pygame.draw.circle(screen, (255, 200, 100), 
                          (screen_x + 28 + (5 if self.direction > 0 else 0), y + 25), 3)
        pygame.draw.circle(screen, (255, 200, 100), 
                          (screen_x + 48 + (5 if self.direction > 0 else 0), y + 25), 3)
        
        # Staff/wand
        staff_x = screen_x + (self.WIDTH + 10 if self.direction > 0 else -20)
        pygame.draw.line(screen, (100, 70, 50), (staff_x, y + 30), (staff_x, y + 100), 4)
        pygame.draw.line(screen, (70, 50, 35), (staff_x, y + 30), (staff_x, y + 100), 2)
        # Staff orb
        orb_glow = 8 + int(abs(math.sin(self.anim_timer * 0.008)) * 6)

        # Charging telegraph effect - staff builds power before attack
        if self.is_charging:
            charge_progress = self.charge_timer / self.charge_duration
            charge_intensity = int(charge_progress * 255)
            # Growing orb glow
            charge_orb_size = orb_glow + int(charge_progress * 20)
            # Outer charging ring
            pygame.draw.circle(screen, (255, 100, 100, charge_intensity), (staff_x, y + 25), charge_orb_size + 12)
            pygame.draw.circle(screen, (255, 150, 50), (staff_x, y + 25), charge_orb_size + 8)
            # Boss body glow (pulsing warning)
            pulse = int(abs(math.sin(self.anim_timer * 0.02)) * 100 * charge_progress)
            glow_surf = pygame.Surface((self.WIDTH + 40, self.HEIGHT + 40), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (255, 100, 100, pulse), (0, 0, self.WIDTH + 40, self.HEIGHT + 40))
            screen.blit(glow_surf, (screen_x - 20, y - 20))
            # Warning text
            if charge_progress > 0.5:
                font = pygame.font.Font(None, 24)
                warn_text = font.render("!", True, (255, 50, 50))
                screen.blit(warn_text, (screen_x + self.WIDTH // 2 - 5, y - 45))

        pygame.draw.circle(screen, (100, 50, 150), (staff_x, y + 25), orb_glow + 4)
        pygame.draw.circle(screen, (180, 100, 220), (staff_x, y + 25), orb_glow)
        pygame.draw.circle(screen, (255, 200, 255), (staff_x, y + 25), orb_glow // 2)

        # Attack effect
        if self.is_attacking and self.attack_pattern == 0:
            # Melee swing arc
            arc_x = screen_x + (self.WIDTH if self.direction > 0 else -60)
            arc_alpha = int(200 * (self.attack_anim_timer / 500))
            arc_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.arc(arc_surf, (200, 50, 200, arc_alpha), (0, 0, 100, 100), 
                           0 if self.direction > 0 else math.pi, math.pi if self.direction > 0 else math.pi * 2, 8)
            screen.blit(arc_surf, (arc_x - 20, y + 10))
        
        # Draw projectiles
        for proj in self.projectiles:
            px = int(proj['x'] - camera_x)
            py = int(proj['y'])
            if proj.get('is_shockwave'):
                # Shockwave - ground energy
                pygame.draw.circle(screen, (150, 50, 150), (px, py), 12)
                pygame.draw.circle(screen, (200, 100, 200), (px, py), 8)
            else:
                # Dark magic projectile
                pygame.draw.circle(screen, (80, 40, 100), (px, py), 14)
                pygame.draw.circle(screen, (150, 80, 180), (px, py), 10)
                pygame.draw.circle(screen, (220, 150, 255), (px, py), 5)
        
        # Health bar above boss
        bar_width = 100
        bar_x = screen_x + (self.WIDTH - bar_width) // 2
        bar_y = y - 20
        # Background
        pygame.draw.rect(screen, (40, 40, 50), (bar_x - 2, bar_y - 2, bar_width + 4, 14), border_radius=4)
        # Health fill
        health_pct = self.health / self.max_health
        fill_color = (50, 200, 50) if health_pct > 0.5 else (200, 200, 50) if health_pct > 0.25 else (200, 50, 50)
        pygame.draw.rect(screen, fill_color, (bar_x, bar_y, int(bar_width * health_pct), 10), border_radius=3)
        pygame.draw.rect(screen, WHITE, (bar_x - 2, bar_y - 2, bar_width + 4, 14), 1, border_radius=4)
        
        # Phase indicator (small)
        phase_text = f"PHASE {self.phase}"
        font_small = pygame.font.Font(None, 20)
        text_surf = font_small.render(phase_text, True, (255, 150, 150))
        screen.blit(text_surf, (screen_x + self.WIDTH // 2 - text_surf.get_width() // 2, y - 35))

        # Phase transition popup (big dramatic text)
        if self.phase_transition_timer > 0:
            # Flash effect
            flash_alpha = min(255, int(self.phase_transition_timer / 2000 * 255))
            # Screen flash on transition
            if self.phase_transition_timer > 1800:
                flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                intensity = int((self.phase_transition_timer - 1800) / 200 * 150)
                phase_color = (150, 50, 50) if self.phase == 3 else (150, 150, 50)
                flash_surf.fill((*phase_color, intensity))
                screen.blit(flash_surf, (0, 0))

            # Big "PHASE X!" text
            font_big = pygame.font.Font(None, 64)
            phase_names = {1: "PHASE 1", 2: "PHASE 2 - ENRAGED!", 3: "PHASE 3 - FINAL FORM!"}
            big_text = phase_names.get(self.phase, f"PHASE {self.phase}")
            # Outline
            outline_surf = font_big.render(big_text, True, (0, 0, 0))
            outline_surf.set_alpha(flash_alpha)
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                screen.blit(outline_surf, (SCREEN_WIDTH // 2 - outline_surf.get_width() // 2 + dx, 200 + dy))
            # Main text
            color = (255, 100, 100) if self.phase == 3 else (255, 200, 50)
            text_surf_big = font_big.render(big_text, True, color)
            text_surf_big.set_alpha(flash_alpha)
            screen.blit(text_surf_big, (SCREEN_WIDTH // 2 - text_surf_big.get_width() // 2, 200))


class EnemyManager:
    """Manages all enemies in the level."""

    def __init__(self, level):
        self.enemies = []
        self.spawn_data = level.get_enemy_spawns()
        self.spawned_indices = set()
        self.score = 0
        
        # Boss handling
        self.boss = None
        self.boss_spawned = False
        self.level = level

    def update(self, platforms, players, dt, camera_x):
        """Update all enemies and spawn new ones."""
        # Spawn enemies that are near the camera
        for i, (x, y, enemy_type) in enumerate(self.spawn_data):
            if i not in self.spawned_indices:
                # Spawn when player approaches
                if x - camera_x < SCREEN_WIDTH + 300:
                    self.enemies.append(Enemy(x, y, enemy_type))
                    self.spawned_indices.add(i)

        # Update existing enemies
        for enemy in self.enemies[:]:
            if enemy.is_alive():
                enemy.update(platforms, players, dt, camera_x)
            else:
                self.enemies.remove(enemy)
        
        # Boss spawning and update
        if self.level.has_boss and not self.boss_spawned:
            # Check if any player has reached boss spawn point
            for player in players:
                if player.is_alive() and hasattr(self.level, 'boss_spawn_x'):
                    if player.x >= self.level.boss_spawn_x - 100:
                        # Spawn the boss!
                        self.boss = Boss(self.level.boss_spawn_x + 200, self.level.boss_spawn_y - Boss.HEIGHT)
                        self.boss_spawned = True
                        break
        
        # Update boss (including death animation)
        if self.boss:
            if self.boss.is_alive() or self.boss.defeated:
                self.boss.update(players, dt, platforms)
            # Clean up boss after death animation
            if self.boss.is_death_animation_complete():
                self.boss = None

    def check_collisions(self, players, enemy_damage_mult=1.0):
        """Check collisions between enemies and players. Returns hit events for feedback.

        Args:
            players: List of player objects
            enemy_damage_mult: Difficulty-based damage multiplier (0.75=Easy, 1.0=Normal, 1.25=Hard)
        """
        hit_events = []  # List of (x, y, damage, is_critical) for damage popups

        for enemy in self.enemies:
            if not enemy.is_alive() or not enemy.active:
                continue

            for player in players:
                if not player.is_alive():
                    continue

                # Enemy touching player
                if enemy.rect.colliderect(player.rect):
                    if enemy.can_attack():
                        base_damage = enemy.attack()
                        # Apply difficulty scaling to enemy damage
                        scaled_damage = int(base_damage * enemy_damage_mult)
                        player.take_damage(scaled_damage)

                # Enemy projectiles hitting player
                for proj in enemy.projectiles[:]:
                    proj_rect = pygame.Rect(int(proj['x']) - 8, int(proj['y']) - 8, 16, 16)
                    if proj_rect.colliderect(player.rect):
                        # Apply difficulty scaling to projectile damage
                        scaled_damage = int(proj['damage'] * enemy_damage_mult)
                        player.take_damage(scaled_damage)
                        enemy.projectiles.remove(proj)

                # Player melee attack hitting enemy
                if player.attacking and player.attack_rect:
                    if enemy.rect.colliderect(player.attack_rect):
                        damage = player.character.damage
                        knockback_dir = player.direction
                        if enemy.take_damage(damage, knockback_dir):
                            self.add_score(enemy.enemy_type)
                        hit_events.append((enemy.x + enemy.rect.width // 2, enemy.y, damage, True))

                # Player projectiles hitting enemy
                for proj in player.projectiles[:]:
                    if enemy.rect.colliderect(proj.rect):
                        knockback_dir = 1 if proj.vel_x > 0 else -1
                        if enemy.take_damage(proj.damage, knockback_dir):
                            self.add_score(enemy.enemy_type)
                        hit_events.append((enemy.x + enemy.rect.width // 2, enemy.y, proj.damage, False))
                        proj.active = False

                # Player special effects hitting enemy
                for effect in player.special_effects:
                    if effect.active and effect.check_enemy_hit(enemy):
                        knockback_dir = effect.owner.direction if hasattr(effect, 'owner') else 0
                        if enemy.take_damage(effect.damage, knockback_dir):
                            self.add_score(enemy.enemy_type)
                        hit_events.append((enemy.x + enemy.rect.width // 2, enemy.y, effect.damage, True))
        
        # Boss collisions
        if self.boss and self.boss.is_alive():
            for player in players:
                if not player.is_alive():
                    continue

                # Boss touching player (apply difficulty scaling)
                if self.boss.rect.colliderect(player.rect):
                    scaled_damage = int(self.boss.damage * enemy_damage_mult)
                    player.take_damage(scaled_damage)

                # Boss melee attack hitting player
                boss_attack_rect = self.boss.get_attack_rect()
                if boss_attack_rect and boss_attack_rect.colliderect(player.rect):
                    scaled_damage = int(self.boss.damage * enemy_damage_mult)
                    player.take_damage(scaled_damage)

                # Boss projectiles hitting player
                for proj in self.boss.projectiles[:]:
                    proj_rect = pygame.Rect(int(proj['x']) - 10, int(proj['y']) - 10, 20, 20)
                    if proj_rect.colliderect(player.rect):
                        scaled_damage = int(proj['damage'] * enemy_damage_mult)
                        player.take_damage(scaled_damage)
                        self.boss.projectiles.remove(proj)
                
                # Player attacking boss
                if player.attacking and player.attack_rect:
                    if self.boss.rect.colliderect(player.attack_rect):
                        damage = player.character.damage
                        if self.boss.take_damage(damage):
                            self.add_score('boss')
                        hit_events.append((self.boss.x + self.boss.WIDTH // 2, self.boss.y, damage, True))

                # Player projectiles hitting boss
                for proj in player.projectiles[:]:
                    if self.boss.rect.colliderect(proj.rect):
                        if self.boss.take_damage(proj.damage):
                            self.add_score('boss')
                        hit_events.append((self.boss.x + self.boss.WIDTH // 2, self.boss.y, proj.damage, False))
                        proj.active = False

                # Player special effects hitting boss
                for effect in player.special_effects:
                    if effect.active:
                        damage_rect = effect.get_damage_rect()
                        if damage_rect and damage_rect.colliderect(self.boss.rect):
                            if id(self.boss) not in effect.damaged_enemies:
                                effect.damaged_enemies.add(id(self.boss))
                                if self.boss.take_damage(effect.damage):
                                    self.add_score('boss')
                                hit_events.append((self.boss.x + self.boss.WIDTH // 2, self.boss.y, effect.damage, True))

        return hit_events

    def add_score(self, enemy_type):
        """Add score based on enemy type."""
        scores = {'walker': 10, 'flying': 15, 'tank': 25, 'boss': 500}
        self.score += scores.get(enemy_type, 10)
    
    def is_boss_defeated(self):
        """Check if boss has been defeated."""
        if not self.level.has_boss:
            return True  # No boss means "defeated"
        if not self.boss_spawned:
            return False  # Boss not yet spawned
        # Boss is defeated if it's None (cleaned up) or marked as defeated
        return self.boss is None or self.boss.defeated

    def draw(self, screen, camera_x):
        """Draw all enemies."""
        for enemy in self.enemies:
            if enemy.is_alive():
                enemy.draw(screen, camera_x)

        # Draw boss (including death animation)
        if self.boss:
            self.boss.draw(screen, camera_x)
