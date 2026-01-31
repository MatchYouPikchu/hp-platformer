# Game Settings and Constants

import pygame

# Screen settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "Harry Potter Adventure"

# Level settings (much larger than screen for scrolling)
LEVEL_WIDTH = 7000  # Longer level for story-driven gameplay
LEVEL_HEIGHT = 768

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_BLUE = (173, 216, 230)
GOLD = (255, 215, 0)
DARK_GREEN = (0, 100, 0)
CRIMSON = (220, 20, 60)
SILVER = (192, 192, 192)
SKY_BLUE = (135, 206, 235)

# Background color
BG_COLOR = (30, 30, 50)

# Player controls
PLAYER1_CONTROLS = {
    'left': pygame.K_a,
    'right': pygame.K_d,
    'jump': pygame.K_w,
    'attack': pygame.K_SPACE,
    'special': pygame.K_e
}

PLAYER2_CONTROLS = {
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'jump': pygame.K_UP,
    'attack': pygame.K_RETURN,
    'special': pygame.K_RSHIFT
}

# Physics - Mario-style movement (legacy)
GRAVITY = 0.6
JUMP_STRENGTH = -14
MAX_FALL_SPEED = 15
PLAYER_SPEED = 5

# Player movement tuning (slower, more deliberate pace)
PLAYER_ACCELERATION = 0.4
PLAYER_DECELERATION = 0.35
PLAYER_AIR_ACCELERATION = 0.35
PLAYER_MAX_SPEED = 4.5
PLAYER_JUMP_VELOCITY = -12.0
PLAYER_JUMP_CUT = -4.0
PLAYER_GRAVITY_NORMAL = 0.45
PLAYER_GRAVITY_FALLING = 0.65
PLAYER_MAX_FALL_SPEED = 10
COYOTE_TIME_MS = 100
JUMP_BUFFER_MS = 120

# Player settings (larger for better visibility)
PLAYER_WIDTH = 48
PLAYER_HEIGHT = 72
INVINCIBILITY_TIME = 1500

# Co-op lockstep tuning
COOP_MARGIN = 120
MAX_COOP_GAP = SCREEN_WIDTH - (COOP_MARGIN * 2) - PLAYER_WIDTH

# Enemy settings
ENEMY_WIDTH = 35
ENEMY_HEIGHT = 50

# Platform settings
PLATFORM_HEIGHT = 20

# Attack settings
ATTACK_DURATION = 300
ATTACK_COOLDOWN = 200  # Fast attacks for satisfying combat feel
PROJECTILE_SPEED = 9
PROJECTILE_SIZE = 12
SPECIAL_COOLDOWN = 4000  # Reduced from 6000 - more impactful specials

# UI settings
FONT_SMALL = 24
FONT_MEDIUM = 36
FONT_LARGE = 72
HEALTH_BAR_WIDTH = 150
HEALTH_BAR_HEIGHT = 20
