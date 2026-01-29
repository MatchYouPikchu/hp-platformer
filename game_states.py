# Game State Machine

from enum import Enum


class GameState(Enum):
    """Game states."""
    MENU = 1
    MODE_SELECT = 2
    DIFFICULTY_SELECT = 3  # New: Difficulty selection
    CHARACTER_SELECT = 4
    STORY_INTRO = 5       # Area intro screen
    PLAYING = 6
    CUTSCENE = 7          # Story cutscene
    GAME_OVER = 8
    PAUSED = 9
    VICTORY = 10
    LEVEL_COMPLETE = 11


class Difficulty:
    """Difficulty settings."""
    EASY = 'easy'
    NORMAL = 'normal'
    HARD = 'hard'

    @staticmethod
    def get_settings(difficulty):
        """Get difficulty-specific settings."""
        if difficulty == Difficulty.EASY:
            return {
                'enemy_damage_mult': 0.75,
                'respawns': 5,
                'name': 'Easy',
                'description': 'More lives, enemies deal less damage'
            }
        elif difficulty == Difficulty.HARD:
            return {
                'enemy_damage_mult': 1.25,
                'respawns': 1,
                'name': 'Hard',
                'description': 'One life, enemies deal more damage'
            }
        else:  # Normal
            return {
                'enemy_damage_mult': 1.0,
                'respawns': 3,
                'name': 'Normal',
                'description': 'Balanced challenge'
            }


class StateManager:
    """Manages game state transitions."""

    MAX_LEVELS = 2

    def __init__(self):
        self.current_state = GameState.MENU
        self.previous_state = None

        # Player mode
        self.num_players = 1  # 1 or 2 players

        # Difficulty
        self.difficulty = Difficulty.NORMAL
        self.difficulty_settings = Difficulty.get_settings(Difficulty.NORMAL)

        # Character selection data
        self.player1_character = None
        self.player2_character = None
        self.player1_selecting = True  # True if P1 is selecting

        # Game data
        self.final_score = 0
        self.final_wave = 0
        self.current_level = 1
        self.level_score = 0  # Score for current level transition
        
        # Story/Cutscene data
        self.current_story_area = None
        self.current_cutscene = None
        self.cutscene_queue = []  # Queue of cutscenes to show

    def change_state(self, new_state):
        """Change to a new state."""
        self.previous_state = self.current_state
        self.current_state = new_state

    def is_state(self, state):
        """Check if currently in a specific state."""
        return self.current_state == state

    def start_mode_select(self):
        """Show mode selection (1P or 2P)."""
        self.change_state(GameState.MODE_SELECT)
    
    def select_mode(self, num_players):
        """Select number of players."""
        self.num_players = num_players
        self.start_difficulty_select()

    def start_difficulty_select(self):
        """Show difficulty selection screen."""
        self.change_state(GameState.DIFFICULTY_SELECT)

    def select_difficulty(self, difficulty):
        """Select difficulty level."""
        self.difficulty = difficulty
        self.difficulty_settings = Difficulty.get_settings(difficulty)
        self.start_character_select()

    def start_character_select(self):
        """Begin character selection."""
        self.player1_character = None
        self.player2_character = None
        self.player1_selecting = True
        self.change_state(GameState.CHARACTER_SELECT)

    def select_character(self, character_name):
        """Handle character selection."""
        if self.player1_selecting:
            self.player1_character = character_name
            if self.num_players == 1:
                # Single player - start game immediately
                self.player2_character = None
                self.change_state(GameState.PLAYING)
            else:
                # Co-op - need P2 selection
                self.player1_selecting = False
        else:
            self.player2_character = character_name
            # Both players have selected, start game
            self.change_state(GameState.PLAYING)

    def go_back_selection(self):
        """Go back in character selection."""
        if not self.player1_selecting:
            # P2 is selecting, go back to P1
            self.player1_selecting = True
            self.player1_character = None
        else:
            # P1 is selecting, go back to mode select
            self.change_state(GameState.MODE_SELECT)

    def start_game(self):
        """Start the game from character select."""
        if self.num_players == 1:
            if self.player1_character:
                self.change_state(GameState.PLAYING)
        else:
            if self.player1_character and self.player2_character:
                self.change_state(GameState.PLAYING)

    def game_over(self, score, wave):
        """Trigger game over."""
        self.final_score = score
        self.final_wave = wave
        self.change_state(GameState.GAME_OVER)

    def level_complete(self, score):
        """Complete current level - may advance or trigger victory."""
        self.level_score = score
        if self.current_level >= self.MAX_LEVELS:
            # Completed all levels - victory!
            self.final_score = score
            self.change_state(GameState.VICTORY)
        else:
            # Advance to next level
            self.change_state(GameState.LEVEL_COMPLETE)

    def advance_level(self):
        """Advance to next level."""
        self.current_level += 1
        self.change_state(GameState.PLAYING)

    def victory(self, score):
        """Trigger victory!"""
        self.final_score = score
        self.change_state(GameState.VICTORY)

    def restart(self):
        """Restart from character selection."""
        self.current_level = 1
        self.start_character_select()

    def quick_restart(self):
        """Quick restart with same characters from level 1."""
        self.current_level = 1
        self.change_state(GameState.PLAYING)
        return True  # Signal to reinitialize game

    def return_to_menu(self):
        """Return to main menu."""
        self.change_state(GameState.MENU)

    def toggle_pause(self):
        """Toggle pause state."""
        if self.current_state == GameState.PLAYING:
            self.change_state(GameState.PAUSED)
        elif self.current_state == GameState.PAUSED:
            self.change_state(GameState.PLAYING)

    def show_story_intro(self, area_name, subtitle, description):
        """Show story intro for a new area."""
        self.current_story_area = {
            'name': area_name,
            'subtitle': subtitle,
            'description': description
        }
        self.change_state(GameState.STORY_INTRO)

    def end_story_intro(self):
        """End story intro and resume playing."""
        self.current_story_area = None
        self.change_state(GameState.PLAYING)

    def show_cutscene(self, cutscene_data):
        """Show a cutscene."""
        self.current_cutscene = cutscene_data
        self.change_state(GameState.CUTSCENE)

    def end_cutscene(self):
        """End cutscene and check for more in queue."""
        if self.cutscene_queue:
            self.current_cutscene = self.cutscene_queue.pop(0)
        else:
            self.current_cutscene = None
            self.change_state(GameState.PLAYING)

    def queue_cutscene(self, cutscene_data):
        """Add cutscene to queue."""
        self.cutscene_queue.append(cutscene_data)
