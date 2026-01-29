# Harry Potter Adventure - Main Entry Point

import os
import sys

# Configure SDL before importing pygame (prevents macOS init crashes)
if sys.platform == "darwin":
    os.environ.setdefault("SDL_VIDEODRIVER", "cocoa")
    os.environ.setdefault("SDL_AUDIODRIVER", "coreaudio")

import pygame
from settings import *
from game_states import StateManager, GameState, Difficulty
from characters import CHARACTER_ORDER
from player import Player
from enemies import EnemyManager
from level import Level, Camera
from ui import UI
from audio import get_audio


class DamagePopup:
    """Floating damage number that rises and fades."""

    def __init__(self, x, y, damage, color=(255, 255, 100)):
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.lifetime = 800  # ms
        self.age = 0
        self.active = True

    def update(self, dt):
        self.age += dt
        self.y -= 1.5  # Float upward
        if self.age >= self.lifetime:
            self.active = False

    def draw(self, screen, camera_x):
        if not self.active:
            return
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y)
        if screen_x < -50 or screen_x > SCREEN_WIDTH + 50:
            return
        # Calculate fade
        alpha = max(0, 255 - int(255 * (self.age / self.lifetime)))
        # Scale based on damage (bigger numbers for bigger hits)
        font_size = min(36, 20 + self.damage // 5)
        font = pygame.font.Font(None, font_size)
        # Render text
        text = str(self.damage)
        text_surf = font.render(text, True, self.color)
        text_surf.set_alpha(alpha)
        # Draw with outline for visibility
        outline_surf = font.render(text, True, (0, 0, 0))
        outline_surf.set_alpha(alpha)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            screen.blit(outline_surf, (screen_x + dx, screen_y + dy))
        screen.blit(text_surf, (screen_x, screen_y))


class Game:
    """Main game class."""

    def __init__(self):
        # Simple init - pygame auto-detects the best drivers
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Game components
        self.state_manager = StateManager()
        self.ui = UI()
        self.audio = get_audio()
        self.level = None
        self.camera = None
        self.players = []
        self.enemy_manager = None
        self.damage_popups = []  # Floating damage numbers

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)

    def handle_keydown(self, key):
        """Handle key press events."""
        state = self.state_manager.current_state

        if state == GameState.MENU:
            if key == pygame.K_SPACE or key == pygame.K_RETURN:
                self.state_manager.start_mode_select()
            elif key == pygame.K_ESCAPE:
                self.running = False

        elif state == GameState.MODE_SELECT:
            if key == pygame.K_1:
                self.state_manager.select_mode(1)
            elif key == pygame.K_2:
                self.state_manager.select_mode(2)
            elif key == pygame.K_ESCAPE:
                self.state_manager.return_to_menu()

        elif state == GameState.DIFFICULTY_SELECT:
            if key == pygame.K_1:
                self.state_manager.select_difficulty(Difficulty.EASY)
                self.ui.reset_selection()
            elif key == pygame.K_2:
                self.state_manager.select_difficulty(Difficulty.NORMAL)
                self.ui.reset_selection()
            elif key == pygame.K_3:
                self.state_manager.select_difficulty(Difficulty.HARD)
                self.ui.reset_selection()
            elif key == pygame.K_ESCAPE:
                self.state_manager.change_state(GameState.MODE_SELECT)

        elif state == GameState.CHARACTER_SELECT:
            if key == pygame.K_LEFT or key == pygame.K_a:
                self.ui.move_selection(-1)
            elif key == pygame.K_RIGHT or key == pygame.K_d:
                self.ui.move_selection(1)
            elif key == pygame.K_SPACE or key == pygame.K_RETURN:
                selected = self.ui.get_selected_character()
                self.state_manager.select_character(selected)
                if self.state_manager.current_state == GameState.PLAYING:
                    self.start_game()
            elif key == pygame.K_ESCAPE:
                self.state_manager.go_back_selection()

        elif state == GameState.PLAYING:
            if key == pygame.K_ESCAPE:
                self.state_manager.toggle_pause()
            elif key == pygame.K_p:
                self.state_manager.toggle_pause()

        elif state == GameState.PAUSED:
            if key == pygame.K_p or key == pygame.K_SPACE:
                self.state_manager.toggle_pause()
            elif key == pygame.K_ESCAPE or key == pygame.K_q:
                self.state_manager.return_to_menu()

        elif state == GameState.GAME_OVER:
            if key == pygame.K_r:
                # Quick restart with same characters
                self.state_manager.quick_restart()
                self.start_game()
            elif key == pygame.K_SPACE or key == pygame.K_RETURN:
                # Go to character select
                self.state_manager.restart()
                self.ui.reset_selection()
            elif key == pygame.K_ESCAPE:
                self.state_manager.return_to_menu()

        elif state == GameState.VICTORY:
            if key == pygame.K_r:
                # Play again with same characters
                self.state_manager.quick_restart()
                self.start_game()
            elif key == pygame.K_SPACE or key == pygame.K_RETURN:
                # Go to character select
                self.state_manager.restart()
                self.ui.reset_selection()
            elif key == pygame.K_ESCAPE:
                self.state_manager.return_to_menu()

        elif state == GameState.LEVEL_COMPLETE:
            if key == pygame.K_SPACE or key == pygame.K_RETURN:
                # Advance to next level
                self.state_manager.advance_level()
                self.start_next_level()

    def start_game(self):
        """Initialize game for playing."""
        self.level = Level(self.state_manager.current_level)
        self.camera = Camera()
        spawn_positions = self.level.get_spawn_positions()

        # Create players based on mode
        self.players = [
            Player(1, self.state_manager.player1_character,
                  spawn_positions[0][0], spawn_positions[0][1])
        ]
        
        if self.state_manager.num_players == 2:
            self.players.append(
                Player(2, self.state_manager.player2_character,
                      spawn_positions[1][0], spawn_positions[1][1])
            )

        # Create enemy manager
        self.enemy_manager = EnemyManager(self.level)

        # Store difficulty settings for enemy damage scaling
        self.difficulty_settings = self.state_manager.difficulty_settings

        # Respawn system - use difficulty setting for respawn count
        self.respawn_timers = [0, 0]  # Timer for each player
        base_respawns = self.difficulty_settings['respawns']
        # Co-op gets more respawns
        self.respawns_remaining = base_respawns + (1 if self.state_manager.num_players == 2 else 0)
        self.RESPAWN_DELAY = 4000  # 4 seconds to respawn

        # Reset damage popups
        self.damage_popups = []
        
    def start_next_level(self):
        """Start the next level, keeping player stats."""
        old_players = self.players
        self.level = Level(self.state_manager.current_level)
        self.camera = Camera()
        spawn_positions = self.level.get_spawn_positions()

        # Create new players but preserve health
        self.players = []
        for i, old_p in enumerate(old_players):
            new_p = Player(old_p.player_num, old_p.character.name,
                          spawn_positions[i][0], spawn_positions[i][1])
            # Preserve some health (heal 30% for new level), revive dead players
            if old_p.is_alive():
                new_p.health = min(new_p.max_health, old_p.health + int(old_p.max_health * 0.3))
            else:
                new_p.health = new_p.max_health // 2  # Dead players revive with 50% HP
            self.players.append(new_p)

        # Create new enemy manager
        self.enemy_manager = EnemyManager(self.level)
        
        # Reset respawn system for new level
        self.respawn_timers = [0, 0]
        self.respawns_remaining = 3 if self.state_manager.num_players == 2 else 2

    def update(self, dt):
        """Update game state."""
        if self.state_manager.current_state == GameState.PLAYING:
            self.update_playing(dt)

    def update_playing(self, dt):
        """Update gameplay."""
        keys = pygame.key.get_pressed()

        # Update players
        for player in self.players:
            if player.is_alive():
                player.handle_input(keys)
                player.update(self.level.platforms, dt)

        # === CHECKPOINT SYSTEM ===
        # Check if players reached new checkpoints
        new_checkpoints = self.level.check_checkpoints(self.players)
        for cp_idx, cp_name in new_checkpoints:
            # Could add a "Checkpoint Reached!" popup here
            pass

        # === RESPAWN SYSTEM ===
        alive_players = [p for p in self.players if p.is_alive()]

        # Handle respawning dead players
        for i, player in enumerate(self.players):
            if not player.is_alive():
                # Start or continue respawn timer
                self.respawn_timers[i] += dt

                # Check if we can respawn
                if self.respawn_timers[i] >= self.RESPAWN_DELAY and self.respawns_remaining > 0:
                    # Determine spawn position - use checkpoint or living player
                    if alive_players:
                        spawn_near = alive_players[0]
                        # Spawn slightly behind the living player
                        spawn_x = max(100, spawn_near.x - 80)
                        spawn_y = spawn_near.y
                    else:
                        # All players dead - use last checkpoint
                        checkpoint = self.level.get_last_checkpoint()
                        if checkpoint:
                            spawn_x, spawn_y, _ = checkpoint
                        else:
                            # Fallback to level start
                            spawn_x, spawn_y = 100, SCREEN_HEIGHT - 100

                    # Respawn the player
                    player.respawn(spawn_x, spawn_y)
                    self.respawn_timers[i] = 0
                    self.respawns_remaining -= 1
            else:
                self.respawn_timers[i] = 0  # Reset timer if alive

        # Co-op lockstep: prevent the leader from outrunning the trailing player
        alive_players = [p for p in self.players if p.is_alive()]  # Refresh after respawn
        if len(alive_players) >= 2:
            leftmost_x = min(p.x for p in alive_players)
            max_allowed_x = leftmost_x + MAX_COOP_GAP
            for player in alive_players:
                if player.x > max_allowed_x:
                    player.x = max_allowed_x
                    if player.vel_x > 0:
                        player.vel_x = 0
                    player.rect.x = int(player.x)

        # Update camera
        self.camera.update(self.players)

        # Update level (collectibles animation)
        self.level.update(dt)

        # Check collectibles
        collected = self.level.check_collectibles(self.players)
        for player, collect_type in collected:
            if collect_type == 'coin':
                self.enemy_manager.score += 5
                self.audio.play_sound('coin')
            elif collect_type == 'health':
                player.health = min(player.max_health, player.health + 30)
                self.audio.play_sound('health')
            elif collect_type == 'speed':
                # Temporary speed boost (increase speed multiplier)
                player.speed_mult = min(2.0, player.speed_mult + 0.3)
                self.audio.play_sound('coin')
            elif collect_type == 'damage':
                # Boost damage for attacks
                player.character.damage += 5
                self.audio.play_sound('coin')

        # Update enemies
        self.enemy_manager.update(self.level.platforms, self.players, dt, self.camera.x)

        # Check collisions and get hit events for feedback
        hit_events = self.enemy_manager.check_collisions(self.players)

        # Process hit events for combat feedback
        for x, y, damage, is_critical in hit_events:
            # Spawn damage popup
            color = (255, 100, 100) if is_critical else (255, 255, 100)
            self.damage_popups.append(DamagePopup(x, y - 20, damage, color))
            # Screen shake for significant hits
            if is_critical or damage >= 15:
                self.camera.shake(magnitude=4, duration=80)
            # Play hit sound
            self.audio.play_sound('hit')

        # Update damage popups
        for popup in self.damage_popups[:]:
            popup.update(dt)
            if not popup.active:
                self.damage_popups.remove(popup)
        
        # Check hazard collisions (spikes, lava)
        for hazard in self.level.hazards:
            hazard.update(dt)
            for player in self.players:
                if player.is_alive() and hazard.check_collision(player):
                    player.take_damage(hazard.damage)
        
        # Check for players falling into pits (below screen = instant death!)
        for player in self.players:
            if player.is_alive() and player.y > SCREEN_HEIGHT + 50:
                # Fell into a pit - instant death!
                player.health = 0

        # Check goal (level complete or victory!)
        # If level has boss, must defeat boss first
        boss_check = self.enemy_manager.is_boss_defeated() if self.level.has_boss else True
        if boss_check and self.level.check_goal(self.players):
            self.audio.play_sound('level_complete')
            self.state_manager.level_complete(self.enemy_manager.score)
            return

        # Check game over
        alive_players = [p for p in self.players if p.is_alive()]
        if len(alive_players) == 0:
            progress = int((self.camera.x / max(1, LEVEL_WIDTH - SCREEN_WIDTH)) * 100)
            self.state_manager.game_over(
                self.enemy_manager.score,
                progress
            )

    def draw(self):
        """Draw the current frame."""
        state = self.state_manager.current_state

        if state == GameState.MENU:
            self.screen.fill(BG_COLOR)
            self.ui.draw_menu(self.screen)

        elif state == GameState.MODE_SELECT:
            self.screen.fill(BG_COLOR)
            self.ui.draw_mode_select(self.screen)

        elif state == GameState.DIFFICULTY_SELECT:
            self.screen.fill(BG_COLOR)
            self.ui.draw_difficulty_select(self.screen)

        elif state == GameState.CHARACTER_SELECT:
            self.screen.fill(BG_COLOR)
            self.ui.draw_character_select(self.screen, self.state_manager)

        elif state == GameState.PLAYING:
            self.draw_playing()

        elif state == GameState.PAUSED:
            self.draw_playing()
            self.ui.draw_pause(self.screen)

        elif state == GameState.GAME_OVER:
            self.draw_playing()
            self.ui.draw_game_over(self.screen, self.state_manager)

        elif state == GameState.VICTORY:
            self.draw_playing()
            self.ui.draw_victory(self.screen, self.state_manager)

        elif state == GameState.LEVEL_COMPLETE:
            self.draw_playing()
            self.ui.draw_level_complete(self.screen, self.state_manager)

        pygame.display.flip()

    def draw_playing(self):
        """Draw gameplay screen."""
        # Clear screen first to prevent smearing/ghosting
        self.screen.fill((0, 0, 0))

        # Get camera position with screen shake offset
        shake_x, shake_y = self.camera.get_shake_offset()
        camera_x = int(self.camera.x) - shake_x

        # Apply vertical shake by drawing to an offset surface
        if shake_y != 0:
            # Simple vertical shake via offset drawing
            pass  # Handled below in blit offsets

        # Draw level (includes background)
        self.level.draw(self.screen, camera_x)

        # Draw checkpoint flags
        self.level.draw_checkpoints(self.screen, camera_x)

        # Draw enemies
        self.enemy_manager.draw(self.screen, camera_x)

        # Draw players
        for player in self.players:
            if player.is_alive():
                player.draw(self.screen, camera_x)

        # Draw damage popups
        for popup in self.damage_popups:
            popup.draw(self.screen, camera_x)

        # Draw HUD with respawn info
        respawn_info = {
            'respawns': self.respawns_remaining,
            'timers': self.respawn_timers,
            'delay': self.RESPAWN_DELAY
        }
        self.ui.draw_hud(self.screen, self.players, self.enemy_manager, self.camera, 
                        self.state_manager.current_level, respawn_info, self.level)


if __name__ == '__main__':
    game = Game()
    game.run()
