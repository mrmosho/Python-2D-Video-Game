import pygame
import math
import random
import os
import sys

# Initialize pygame with sound
pygame.init()
pygame.mixer.init()

# Game Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (0, 0, 255)
DOOR_COLOR = (255, 0, 0)
WINDOW_COLOR = (0, 255, 0)
BACK_RECT_COLOR = (200, 200, 0)
COIN_COLOR = (255, 215, 0)  # Gold color for coins
MENU_BG_COLOR = (25, 25, 50)
BUTTON_COLOR = (100, 100, 200)
BUTTON_HOVER_COLOR = (150, 150, 255)
WALL_COLOR = (100, 50, 25)  # Brown for walls
ENEMY_COLOR = (255, 0, 0)   # Red for enemies
PLAYER_SPEED = 5
ENEMY_SPEED = 3
TEXT_COLOR = (255, 255, 255)
FLASHLIGHT_ANGLE = math.radians(30)
FLASHLIGHT_LENGTH = 250

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Door Explorer")

# Fonts
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 24)

# Game Settings
game_settings = {
    "sound_enabled": True,
    "sound_volume": 0.5,  # 0.0 to 1.0
    "brightness": 0.4,     # 0.0 to 1.0 (affects flashlight darkness)
    "use_custom_models": True,
    "use_custom_backgrounds": True
}

# Sound handling
sounds = {}

def load_sounds():
    global sounds
    sound_files = {
        "coin": "coin.wav",
        "door": "door.wav",
        "hit": "hit.wav",
        "gameover": "gameover.wav",
        "menu": "menu.wav"  # Added menu sound
    }
    
    # Try to load each sound
    for name, file in sound_files.items():
        try:
            sounds[name] = pygame.mixer.Sound(file)
            print(f"Loaded sound: {file}")
        except:
            sounds[name] = None
            print(f"Could not load sound: {file}")

def play_sound(name):
    if game_settings["sound_enabled"] and name in sounds and sounds[name] is not None:
        try:
            sounds[name].set_volume(game_settings["sound_volume"])
            sounds[name].play()
        except Exception as e:
            print(f"Error playing sound '{name}': {e}")

def stop_sound(name):
    """
    Stops the playback of a sound if it is currently playing.

    Args:
        name (str): The name of the sound to stop (e.g., "menu", "coin").
                     This should be a key from your 'sounds' dictionary.
    """
    if name in sounds and sounds[name] is not None:
        try:
            sounds[name].stop()
            print(f"Stopped sound: {name}")  # Optional: Confirmation message
        except Exception as e:
            print(f"Error stopping sound '{name}': {e}")
    else:
        print(f"Sound '{name}' not loaded or not found to stop.")

# Custom models
player_sprites = {}
enemy_sprites = {}
item_sprites = {}
level_background_image = {}

def load_sprites():
    global player_sprites, enemy_sprites, item_sprites, level_background_image
    print("--- Attempting to load item sprites ---") # Debugging start

    # Try to load item sprites
    try:
        print("Trying to load coin.png...") # Debugging: Before load
        item_sprites["coin"] = pygame.image.load("coin.png")
        print("coin.png loaded successfully!") # Debugging: Success
        item_sprites["coin"] = pygame.transform.scale(item_sprites["coin"], (20, 20))
        print("coin.png scaled successfully.") # Debugging: Success

        item_sprites["door"] = pygame.image.load("door.png") # ... (rest of item loading)
        item_sprites["door"] = pygame.transform.scale(item_sprites["door"], (50, 100))
        item_sprites["window"] = pygame.image.load("window.png")
        item_sprites["window"] = pygame.transform.scale(item_sprites["window"], (80, 50))
        print("Loaded item sprites (all items)") # Success message (if all items load)

    except Exception as e: # Catch any exception
        item_sprites = {}
        print("!!! ERROR loading item sprites !!!") # Error message
        print(f"Exception details: {e}") # Print specific error details
        print("Using default shapes for items.") # Fallback message
    
    # Try to load player sprites
    try:
        player_sprites = {
            "right": pygame.image.load("player.png"),
            "left": pygame.image.load("player.png"),
            "up": pygame.image.load("player.png"),
            "down": pygame.image.load("player.png")
        }
        # Scale sprites to player size
        for direction in player_sprites:
            player_sprites[direction] = pygame.transform.scale(player_sprites[direction], (40, 40))
        print("Loaded player sprites")
    except:
        player_sprites = {}
        print("Could not load player sprites, using default shapes")
    
    # Try to load enemy sprites
    try:
        enemy_sprites["default"] = pygame.image.load("enemy.png")
        enemy_sprites["default"] = pygame.transform.scale(enemy_sprites["default"], (100, 100))
        print("Loaded enemy sprites")
    except:
        enemy_sprites = {}
        print("Could not load enemy sprites, using default shapes")
    
    print(f"Current working directory: {os.getcwd()}") 
    # Try to load item sprites
    try:
        item_sprites["coin"] = pygame.image.load("coin.png")
        item_sprites["coin"] = pygame.transform.scale(item_sprites["coin"], (40, 40))
        item_sprites["door"] = pygame.image.load("door.png")
        item_sprites["door"] = pygame.transform.scale(item_sprites["door"], (50, 100))
        item_sprites["window"] = pygame.image.load("window.png")
        item_sprites["window"] = pygame.transform.scale(item_sprites["window"], (80, 50))
        print("Loaded item sprites")
    except:
        item_sprites = {}
        print("Could not load item sprites, using default shapes")
        # Try to load background image
    try:
        level_background_image = pygame.image.load("background.png") # Load background.png
        level_background_image = pygame.transform.scale(level_background_image, (WIDTH, HEIGHT)) # Scale to screen size
        print("Loaded background image: background.png")
    except:
        level_background_image = None # Set to None if loading fails
        print("Could not load background image, using default level colors.")

# Game States
MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3
OPTIONS = 4
game_state = MENU

# Menu Buttons
start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 60)
resume_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 120, 200, 60)
options_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 40, 200, 60)
reset_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 40, 200, 60)
menu_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 60)
quit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 200, 200, 60)
retry_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 60)


# Options Menu Sliders
sound_toggle_rect = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 - 120, 30, 30)
volume_slider_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 20)
volume_handle_rect = pygame.Rect(WIDTH // 2 - 100 + int(game_settings["sound_volume"] * 200) - 10, HEIGHT // 2 - 65, 20, 30)
brightness_slider_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 20)
brightness_handle_rect = pygame.Rect(WIDTH // 2 - 100 + int(game_settings["brightness"] * 200) - 10, HEIGHT // 2 - 5, 20, 30)
models_toggle_rect = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 60, 30, 30)
back_options_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 60)

# Flag to track if a slider is being dragged
dragging_volume = False
dragging_brightness = False

# Player Setup
player = pygame.Rect(50, HEIGHT // 2, 40, 40)
player_direction = 0  # 0: right, 1: down, 2: left, 3: up
player_coins = 0  # Player starts with 0 coins
player_health = 3  # Player starts with 3 health points

# Enemy Setup
# Create a class for enemies
class Enemy:
    def __init__(self, x, y, level, patrol_points=None):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.level = level
        self.speed = ENEMY_SPEED
        self.direction = random.choice([0, 1, 2, 3])  # Random initial direction
        self.patrol_mode = patrol_points is not None
        self.patrol_points = patrol_points or []
        self.current_target = 0
        self.movement_timer = 0
    
    def update(self, player_rect, walls):
        # Only update if on current level
        if self.level != level:
            return False  # Not colliding
        
        # Move enemy
        if self.patrol_mode and self.patrol_points:
            # Patrol between points
            target = self.patrol_points[self.current_target]
            dx = target[0] - self.rect.x
            dy = target[1] - self.rect.y
            
            # Calculate distance to target
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 10:  # Close enough to target
                self.current_target = (self.current_target + 1) % len(self.patrol_points)
            else:
                # Normalize direction
                if distance > 0:
                    dx = dx / distance * self.speed
                    dy = dy / distance * self.speed
                
                new_x = self.rect.x + dx
                new_y = self.rect.y + dy
                
                # Check for wall collisions
                test_rect = pygame.Rect(new_x, self.rect.y, self.rect.width, self.rect.height)
                if not any(test_rect.colliderect(wall) for wall in walls):
                    self.rect.x = new_x
                
                test_rect = pygame.Rect(self.rect.x, new_y, self.rect.width, self.rect.height)
                if not any(test_rect.colliderect(wall) for wall in walls):
                    self.rect.y = new_y
        else:
            # Random movement
            self.movement_timer += 1
            if self.movement_timer >= 60:  # Change direction every ~2 seconds
                self.direction = random.choice([0, 1, 2, 3])
                self.movement_timer = 0
            
            # Move based on direction
            move_x, move_y = 0, 0
            if self.direction == 0:  # Right
                move_x = self.speed
            elif self.direction == 1:  # Down
                move_y = self.speed
            elif self.direction == 2:  # Left
                move_x = -self.speed
            elif self.direction == 3:  # Up
                move_y = -self.speed
            
            # Check wall collisions for X movement
            test_rect = pygame.Rect(self.rect.x + move_x, self.rect.y, self.rect.width, self.rect.height)
            if not any(test_rect.colliderect(wall) for wall in walls):
                self.rect.x += move_x
            else:
                # If collision, reverse direction
                if self.direction == 0:
                    self.direction = 2
                elif self.direction == 2:
                    self.direction = 0
            
            # Check wall collisions for Y movement
            test_rect = pygame.Rect(self.rect.x, self.rect.y + move_y, self.rect.width, self.rect.height)
            if not any(test_rect.colliderect(wall) for wall in walls):
                self.rect.y += move_y
            else:
                # If collision, reverse direction
                if self.direction == 1:
                    self.direction = 3
                elif self.direction == 3:
                    self.direction = 1
            
            # Keep enemy on screen
            self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
            self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))
        
        # Check for collision with player
        return self.rect.colliderect(player_rect)
    
    def draw(self, surface):
        if self.level == level:
            if game_settings["use_custom_models"] and "new_enemy" in enemy_sprites and enemy_sprites["new_enemy"] is not None:
                # **EDIT HERE 1:** Use your new sprite if it's loaded and models are enabled
                surface.blit(enemy_sprites["new_enemy"], self.rect)
            elif game_settings["use_custom_models"] and "default" in enemy_sprites:
                # **EDIT HERE 2:** Fallback to "default" enemy sprite if "new_enemy" is missing or not loaded correctly, but custom models are on
                surface.blit(enemy_sprites["default"], self.rect)
            else:
                # **EDIT HERE 3:** Default enemy shape (if custom models are off or no sprites loaded)
                pygame.draw.rect(surface, ENEMY_COLOR, self.rect)

                # Draw eyes to show direction (rest of the eye drawing logic is the same)
                eye_size = 6
                if self.direction == 0:  # Right
                    pygame.draw.circle(surface, WHITE, (self.rect.right - 10, self.rect.y + 10), eye_size)
                    pygame.draw.circle(surface, WHITE, (self.rect.right - 10, self.rect.y + 20), eye_size)
                elif self.direction == 1:  # Down
                    pygame.draw.circle(surface, WHITE, (self.rect.x + 10, self.rect.bottom - 10), eye_size)
                    pygame.draw.circle(surface, WHITE, (self.rect.x + 20, self.rect.bottom - 10), eye_size)
                elif self.direction == 2:  # Left
                    pygame.draw.circle(surface, WHITE, (self.rect.x + 10, self.rect.y + 10), eye_size)
                    pygame.draw.circle(surface, WHITE, (self.rect.x + 10, self.rect.y + 20), eye_size)
                elif self.direction == 3:  # Up
                    pygame.draw.circle(surface, WHITE, (self.rect.x + 10, self.rect.y + 10), eye_size)
                    pygame.draw.circle(surface, WHITE, (self.rect.x + 20, self.rect.y + 10), eye_size)

# Walls by level
walls_by_level = {
    0: [
        # Border walls
        pygame.Rect(0, 0, WIDTH, 20),  # Top
        pygame.Rect(0, HEIGHT-20, WIDTH, 20),  # Bottom
        pygame.Rect(0, 0, 20, HEIGHT),  # Left
        pygame.Rect(WIDTH-20, 0, 20, HEIGHT),  # Right
        
        # Interior walls
        pygame.Rect(200, 100, 20, 150),
        pygame.Rect(400, 350, 150, 20),
    ],
    1: [
        # Border walls
        pygame.Rect(0, 0, WIDTH, 20),  # Top
        pygame.Rect(0, HEIGHT-20, WIDTH, 20),  # Bottom
        pygame.Rect(0, 0, 20, HEIGHT),  # Left
        pygame.Rect(WIDTH-20, 0, 20, HEIGHT),  # Right
        
        # Maze-like interior
        pygame.Rect(100, 100, 20, 200),
        pygame.Rect(100, 100, 300, 20),
        pygame.Rect(300, 100, 20, 150),
        pygame.Rect(300, 250, 200, 20),
        pygame.Rect(500, 100, 20, 170),
        pygame.Rect(300, 400, 300, 20),
    ],
    2: [
        # Border walls
        pygame.Rect(0, 0, WIDTH, 20),  # Top
        pygame.Rect(0, HEIGHT-20, WIDTH, 20),  # Bottom
        pygame.Rect(0, 0, 20, HEIGHT),  # Left
        pygame.Rect(WIDTH-20, 0, 20, HEIGHT),  # Right
        
        # Center room with multiple entrances
        pygame.Rect(200, 100, 20, 150),
        pygame.Rect(200, 100, 400, 20),
        pygame.Rect(600, 100, 20, 150),
        pygame.Rect(200, 350, 200, 20),
        pygame.Rect(500, 350, 100, 20),
    ],
}

# Interactable Objects by Level
# Level 0 - Main Hub
doors_by_level = {
    0: [
        {"rect": pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2, 50, 100), "cost": 5, "target": 1, "type": "door"},
        {"rect": pygame.Rect(WIDTH // 2 + 150, HEIGHT // 2 - 50, 50, 100), "cost": 10, "target": 2, "type": "door"},
    ],
    1: [
        {"rect": pygame.Rect(650, 300, 50, 100), "cost": 20, "target": 2, "type": "door"},
    ],
    2: [
        {"rect": pygame.Rect(100, 400, 50, 100), "cost": 15, "target": 0, "type": "door"},
    ]
}

windows_by_level = {
    0: [
        {"rect": pygame.Rect(WIDTH // 2 + 25, HEIGHT // 2, 80, 50), "cost": 3, "target": 1, "type": "window"},
        {"rect": pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 80, 50), "cost": 8, "target": 2, "type": "window"},
    ],
    1: [
        {"rect": pygame.Rect(400, 500, 80, 50), "cost": 12, "target": 0, "type": "window"},
    ],
    2: [
        {"rect": pygame.Rect(650, 200, 80, 50), "cost": 18, "target": 1, "type": "window"},
    ]
}

# Back to Level 0 Button
back_rect = pygame.Rect(WIDTH - 150, 50, 100, 50)

# Initialize enemies for each level
enemies = [
    # Level 0 enemies
    Enemy(300, 200, 0),
    Enemy(500, 400, 0, [(500, 400), (600, 400), (600, 500), (500, 500)]),  # Patrolling enemy
    
    # Level 1 enemies
    Enemy(150, 300, 1),
    Enemy(400, 150, 1),
    Enemy(600, 300, 1, [(600, 300), (700, 300), (700, 500), (600, 500)]),
    
    # Level 2 enemies
    Enemy(300, 200, 2),
    Enemy(500, 400, 2),
    Enemy(650, 300, 2),
    Enemy(400, 150, 2, [(400, 150), (500, 150), (500, 300), (400, 300)]),
]

# Function to generate coins for a level
def generate_coins(level_num, num_coins=10):
    level_coins = []
    for _ in range(num_coins):
        coin_x = random.randint(50, WIDTH - 50)
        coin_y = random.randint(50, HEIGHT - 50)
        
        # Ensure coins don't spawn on doors or windows
        valid_position = True
        for door in doors_by_level.get(level_num, []):
            if door["rect"].collidepoint(coin_x, coin_y):
                valid_position = False
                break
        
        for window in windows_by_level.get(level_num, []):
            if window["rect"].collidepoint(coin_x, coin_y):
                valid_position = False
                break
                
        if valid_position:
            level_coins.append({
                "rect": pygame.Rect(coin_x, coin_y, 20, 20),
                "level": level_num,
                "collected": False
            })
    
    return level_coins

# Game Variables
level = 0
running = True
display_text = False
interaction_target = None

# Background Colors per Level
level_colors = [(50, 50, 50), (100, 100, 255), (255, 100, 100)]

# Generate initial coins for level 0
coins = generate_coins(0, 15)
# Add some coins to other levels too
coins.extend(generate_coins(1, 20))
coins.extend(generate_coins(2, 25))

def draw_flashlight():
    center_x, center_y = player.x + player.width // 2, player.y + player.height // 2
    
    # Determine angle based on player direction
    angle = 0  # Default right
    if player_direction == 0:  # Right
        angle = 0
    elif player_direction == 1:  # Down
        angle = math.pi / 2
    elif player_direction == 2:  # Left
        angle = math.pi
    elif player_direction == 3:  # Up
        angle = 3 * math.pi / 2
    
    left_x = center_x + FLASHLIGHT_LENGTH * math.cos(angle - FLASHLIGHT_ANGLE)
    left_y = center_y + FLASHLIGHT_LENGTH * math.sin(angle - FLASHLIGHT_ANGLE)
    right_x = center_x + FLASHLIGHT_LENGTH * math.cos(angle + FLASHLIGHT_ANGLE)
    right_y = center_y + FLASHLIGHT_LENGTH * math.sin(angle + FLASHLIGHT_ANGLE)
    
    # Adjust darkness based on brightness setting (0.0 = pitch black, 1.0 = fully visible)
    darkness_alpha = int(255 * (1 - game_settings["brightness"]))
    
    darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    darkness.fill((0, 0, 0, darkness_alpha))
    pygame.draw.polygon(darkness, (0, 0, 0, 0), [(center_x, center_y), (left_x, left_y), (right_x, right_y)])
    screen.blit(darkness, (0, 0))

def draw_button(rect, text, hover_check=True):
    mouse_pos = pygame.mouse.get_pos()
    button_color = BUTTON_HOVER_COLOR if (hover_check and rect.collidepoint(mouse_pos)) else BUTTON_COLOR
    pygame.draw.rect(screen, button_color, rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=10)  # Border
    
    button_text = font.render(text, True, WHITE)
    button_text_rect = button_text.get_rect(center=rect.center)
    screen.blit(button_text, button_text_rect)

def draw_menu():
    screen.fill(MENU_BG_COLOR)
    
    # Draw title
    title_text = title_font.render("Door Explorer", True, WHITE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title_text, title_rect)
    
    # Draw start button
    draw_button(start_button, "Start Game")
    draw_button(options_button, "Options")
    draw_button(quit_button, "Quit Game")
    
    # Instructions
    instructions = [
        "Use WASD or Arrow Keys to move",
        "Collect coins to open doors and windows",
        "Press Enter to interact with objects",
        "Press ESC to pause game"
    ]
    
    for i, instruction in enumerate(instructions):
        inst_text = small_font.render(instruction, True, WHITE)
        screen.blit(inst_text, (WIDTH // 2 - 150, HEIGHT // 2 + 100 + i * 30))

def draw_options_menu():
    screen.fill(MENU_BG_COLOR)
    
    # Draw title
    title_text = title_font.render("Options", True, WHITE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 6))
    screen.blit(title_text, title_rect)
    
    # Sound toggle
    sound_text = font.render("Sound Enabled:", True, WHITE)
    screen.blit(sound_text, (WIDTH // 2 - 250, HEIGHT // 2 - 120))
    
    pygame.draw.rect(screen, WHITE, sound_toggle_rect, 2)
    if game_settings["sound_enabled"]:
        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(sound_toggle_rect.x + 5, sound_toggle_rect.y + 5, 20, 20))
    
    # Volume slider
    volume_text = font.render("Sound Volume:", True, WHITE)
    screen.blit(volume_text, (WIDTH // 2 - 250, HEIGHT // 2 - 60))
    
    pygame.draw.rect(screen, (100, 100, 100), volume_slider_rect, border_radius=5)
    pygame.draw.rect(screen, (150, 150, 255), pygame.Rect(volume_slider_rect.x, volume_slider_rect.y, 
                                                      int(game_settings["sound_volume"] * volume_slider_rect.width), 
                                                      volume_slider_rect.height), border_radius=5)
    pygame.draw.rect(screen, WHITE, volume_handle_rect, border_radius=5)
    
    # Brightness slider
    brightness_text = font.render("Brightness:", True, WHITE)
    screen.blit(brightness_text, (WIDTH // 2 - 250, HEIGHT // 2))
    
    pygame.draw.rect(screen, (100, 100, 100), brightness_slider_rect, border_radius=5)
    pygame.draw.rect(screen, (255, 255, 150), pygame.Rect(brightness_slider_rect.x, brightness_slider_rect.y, 
                                                      int(game_settings["brightness"] * brightness_slider_rect.width), 
                                                      brightness_slider_rect.height), border_radius=5)
    pygame.draw.rect(screen, WHITE, brightness_handle_rect, border_radius=5)
    
    # Custom models toggle
    models_text = font.render("Custom Models:", True, WHITE)
    screen.blit(models_text, (WIDTH // 2 - 250, HEIGHT // 2 + 60))
    
    pygame.draw.rect(screen, WHITE, models_toggle_rect, 2)
    if game_settings["use_custom_models"]:
        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(models_toggle_rect.x + 5, models_toggle_rect.y + 5, 20, 20))
    
    # Back button
    draw_button(back_options_button, "Back")

def draw_pause_menu():
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Draw title
    title_text = title_font.render("Game Paused", True, WHITE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 6))
    screen.blit(title_text, title_rect)
    
    # Draw buttons
    draw_button(resume_button, "Resume Game")
    draw_button(options_button, "Options")
    draw_button(reset_button, "Reset Game")
    draw_button(menu_button, "Main Menu")
    draw_button(quit_button, "Quit Game")

def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    # Draw title
    title_text = title_font.render("Game Over", True, (255, 50, 50))
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_text, title_rect)
    
    # Draw score
    score_text = font.render(f"Coins Collected: {player_coins}", True, COIN_COLOR)
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(score_text, score_rect)
    
    # Draw buttons
    draw_button(retry_button, "Try Again")
    draw_button(menu_button, "Main Menu")
    draw_button(quit_button, "Quit Game")

def draw_ui_elements():
    # Coin counter with border
    coin_bg = pygame.Rect(15, 15, 130, 40)
    pygame.draw.rect(screen, (50, 50, 50), coin_bg, border_radius=5)
    pygame.draw.rect(screen, COIN_COLOR, coin_bg, 2, border_radius=5)  # Gold border
    
    coin_text = font.render(f"Coins: {player_coins}", True, COIN_COLOR)
    screen.blit(coin_text, (25, 20))
    
    # Level indicator
    level_bg = pygame.Rect(15, 65, 130, 40)
    pygame.draw.rect(screen, (50, 50, 50), level_bg, border_radius=5)
    pygame.draw.rect(screen, WHITE, level_bg, 2, border_radius=5)  # White border
    
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(level_text, (25, 70))
    
    # Health indicator
    health_bg = pygame.Rect(15, 115, 130, 40)
    pygame.draw.rect(screen, (50, 50, 50), health_bg, border_radius=5)
    pygame.draw.rect(screen, (255, 50, 50), health_bg, 2, border_radius=5)  # Red border
    
    health_text = font.render(f"Health: {player_health}", True, (255, 50, 50))
    screen.blit(health_text, (25, 120))

            # --- NEW FUNCTION TO LOAD YOUR PISKEL ENEMY SPRITE ---
def load_new_enemy_sprite():
    """Loads the new enemy sprite from a PNG file (exported from Piskel)."""
    global enemy_sprites # We need to modify the global enemy_sprites dictionary

    try:
        # **IMPORTANT:**
        # 1.  **Export from Piskel as PNG:**  Make sure you export your enemy sprite from Piskel as a PNG file.
        # 2.  **Filename:**  Replace "your_new_enemy_sprite.png" with the actual filename of your exported PNG file.
        # 3.  **File Location:**  Place the PNG file in the same directory as your Python script
        enemy_sprites["new_enemy"] = pygame.image.load("enemy.png")

        # Scale the sprite to a suitable size (adjust as needed)
        enemy_sprites["new_enemy"] = pygame.transform.scale(enemy_sprites["new_enemy"], (30, 30))
        print("Loaded new enemy sprite: enemy.png")
    except pygame.error as e:
        print(f"Could not load new enemy sprite: enemy.png - {e}")
        enemy_sprites["new_enemy"] = None # Indicate that loading failed
    
    # Display interaction text
    if display_text and interaction_target:
        if interaction_target.get("type") in ["door", "window"]:
            text_bg = pygame.Rect(WIDTH // 2 - 330, 10, 660, 50)
            pygame.draw.rect(screen, (50, 50, 50, 200), text_bg, border_radius=5)
            
            if player_coins >= interaction_target["cost"]:
                interact_text = font.render(
                    f"Enter {interaction_target['type']} to Level {interaction_target['target']} (Cost: {interaction_target['cost']} coins - Press Enter)", 
                    True, TEXT_COLOR
                )
            else:
                interact_text = font.render(
                    f"Need {interaction_target['cost']} coins (you have {player_coins})", 
                    True, (255, 100, 100)  # Red text for warning
                )
            screen.blit(interact_text, (WIDTH // 2 - 320, 20))

# Function to reset the game
def reset_game():
    global player, player_coins, player_health, level, coins, game_state, last_hit_time
    
    # Reset player position and attributes
    player.x, player.y = 50, HEIGHT // 2
    player_direction = 0
    player_coins = 0
    player_health = 3
    level = 0
    last_hit_time = 0
    
    # Reset enemies
    for enemy in enemies:
        if hasattr(enemy, 'patrol_points') and enemy.patrol_points:
            enemy.rect.x, enemy.rect.y = enemy.patrol_points[0]
        else:
            enemy.rect.x = random.randint(100, WIDTH - 100)  # Corrected line - set enemy.rect.x
            enemy.rect.y = random.randint(100, HEIGHT - 100)  # Corrected line - set enemy.rect.y
    
    # Regenerate coins
    coins = []
    coins = generate_coins(0, 15)
    coins.extend(generate_coins(1, 20))
    coins.extend(generate_coins(2, 25))

# Initialize other variables
immunity_time = 1000  # ms of immunity after being hit
last_hit_time = 0

# Load resources
load_sounds()
load_sprites()
load_new_enemy_sprite() # Load your new enemy sprite after loading default sprites

# Game Loop
clock = pygame.time.Clock()
while running:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == PLAYING:
                    game_state = PAUSED
                   
                elif game_state == PAUSED:
                    game_state = PLAYING
                elif game_state == OPTIONS:
                    # If coming from pause menu, go back to pause
                    if level > 0:
                        game_state = PAUSED
                    else:
                        game_state = MENU
                    play_sound("menu")
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Main Menu buttons
            if game_state == MENU:
                if start_button.collidepoint(mouse_pos):
                    game_state = PLAYING
                    play_sound("menu")
                    # Reset player position when starting game
                    player.x, player.y = 50, HEIGHT // 2
                  
                elif options_button.collidepoint(mouse_pos):
                    game_state = OPTIONS
                  
                elif quit_button.collidepoint(mouse_pos):
                    running = False
            
            # Pause Menu buttons
            elif game_state == PAUSED:
                if resume_button.collidepoint(mouse_pos):
                    game_state = PLAYING
                    play_sound("menu")
                elif options_button.collidepoint(mouse_pos):
                    game_state = OPTIONS
                  
                elif reset_button.collidepoint(mouse_pos):
                    reset_game()
                    game_state = PLAYING
                    play_sound("menu")
                elif menu_button.collidepoint(mouse_pos):
                    reset_game()
                    game_state = MENU
                    
                elif quit_button.collidepoint(mouse_pos):
                    running = False
            
            # Game Over buttons
            elif game_state == GAME_OVER:
                if retry_button.collidepoint(mouse_pos):
                    reset_game()
                    game_state = PLAYING
                    play_sound("menu")
                elif menu_button.collidepoint(mouse_pos):
                    reset_game()
                    game_state = MENU
                    play_sound("menu")
                elif quit_button.collidepoint(mouse_pos):
                    running = False
            
            # Options Menu
            elif game_state == OPTIONS:
                if back_options_button.collidepoint(mouse_pos):
                    # If coming from pause menu, go back to pause
                    if level > 0:
                        game_state = PAUSED
                    else:
                        game_state = MENU
                    play_sound("menu")
                
                # Sound toggle
                elif sound_toggle_rect.collidepoint(mouse_pos):
                    game_settings["sound_enabled"] = not game_settings["sound_enabled"]
                    play_sound("menu")
                
                # Models toggle
                elif models_toggle_rect.collidepoint(mouse_pos):
                    game_settings["use_custom_models"] = not game_settings["use_custom_models"]
                    play_sound("menu")
                
                # Volume slider
                elif volume_slider_rect.collidepoint(mouse_pos):
                    # Set volume based on click position
                    rel_x = mouse_pos[0] - volume_slider_rect.x
                    game_settings["sound_volume"] = max(0, min(1, rel_x / volume_slider_rect.width))
                    volume_handle_rect.x = volume_slider_rect.x + int(game_settings["sound_volume"] * volume_slider_rect.width) - 10
                    play_sound("menu")
                    dragging_volume = True
                
                # Brightness slider
                elif brightness_slider_rect.collidepoint(mouse_pos):
                    # Set brightness based on click position
                    rel_x = mouse_pos[0] - brightness_slider_rect.x
                    game_settings["brightness"] = max(0, min(1, rel_x / brightness_slider_rect.width))
                    brightness_handle_rect.x = brightness_slider_rect.x + int(game_settings["brightness"] * brightness_slider_rect.width) - 10
                    dragging_brightness = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            # Stop dragging sliders
            dragging_volume = False
            dragging_brightness = False
        
        elif event.type == pygame.MOUSEMOTION:
            # Update sliders if dragging
            if dragging_volume:
                rel_x = event.pos[0] - volume_slider_rect.x
                game_settings["sound_volume"] = max(0, min(1, rel_x / volume_slider_rect.width))
                volume_handle_rect.x = volume_slider_rect.x + int(game_settings["sound_volume"] * volume_slider_rect.width) - 10
            
            if dragging_brightness:
                rel_x = event.pos[0] - brightness_slider_rect.x
                game_settings["brightness"] = max(0, min(1, rel_x / brightness_slider_rect.width))
                brightness_handle_rect.x = brightness_slider_rect.x + int(game_settings["brightness"] * brightness_slider_rect.width) - 10
    
    # Draw the appropriate screen based on game state
    if game_state == MENU:
        draw_menu()
    
    elif game_state == OPTIONS:
        draw_options_menu()
    
    elif game_state == GAME_OVER:
        draw_game_over()
    
    elif game_state == PAUSED:
        # Still draw the game in the background (but don't update it)
        draw_pause_menu()
    
    elif game_state == PLAYING:
        if game_settings["use_custom_backgrounds"] and level_background_image is not None:
            screen.blit(level_background_image, (0, 0)) # Blit background image
        else:
            screen.fill(level_colors[level % len(level_colors)]) # Fallback to level color
        
        
        # Get current level walls
        current_walls = walls_by_level.get(level, [])
        
        # Player Movement
        keys = pygame.key.get_pressed()
        moved = False
        
        new_x, new_y = player.x, player.y
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            new_x -= PLAYER_SPEED
            player_direction = 2  # Left
            moved = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            new_x += PLAYER_SPEED
            player_direction = 0  # Right
            moved = True
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_y -= PLAYER_SPEED
            player_direction = 3  # Up
            moved = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_y += PLAYER_SPEED
            player_direction = 1  # Down
            moved = True
        
        # Check wall collisions for X movement
        test_rect = pygame.Rect(new_x, player.y, player.width, player.height)
        if not any(test_rect.colliderect(wall) for wall in current_walls):
            player.x = new_x
        
        # Check wall collisions for Y movement
        test_rect = pygame.Rect(player.x, new_y, player.width, player.height)
        if not any(test_rect.colliderect(wall) for wall in current_walls):
            player.y = new_y
        
        # Keep player on screen
        player.x = max(0, min(WIDTH - player.width, player.x))
        player.y = max(0, min(HEIGHT - player.height, player.y))
        
        # Coin Collection
        for coin in coins:
            if coin["level"] == level and not coin["collected"]:
                if player.colliderect(coin["rect"]):
                    coin["collected"] = True
                    player_coins += 1
                    play_sound("coin")
        
        # Enemy collision and updates
        hit_by_enemy = False
        for enemy in enemies:
            if enemy.update(player, current_walls):
                # Check if we have immunity
                if current_time - last_hit_time > immunity_time:
                    hit_by_enemy = True
                    last_hit_time = current_time
        
        # Handle enemy collision
        if hit_by_enemy:
            player_health -= 1
            play_sound("hit")
            
            # Check for game over
            if player_health <= 0:
                stop_sound("menu")
                game_state = GAME_OVER
                play_sound("gameover")
                
        
        # Interaction Logic
        display_text = False
        interaction_target = None
        
        # Check door interactions for current level
        current_doors = doors_by_level.get(level, [])
        for door in current_doors:
            if player.colliderect(door["rect"]):
                display_text = True
                interaction_target = door
                if keys[pygame.K_RETURN]:  # Press Enter to interact
                    if player_coins >= door["cost"]:
                        player_coins -= door["cost"]
                        level = door["target"]
                        # Reset player position for new level
                        player.x, player.y = 50, HEIGHT // 2
                        play_sound("door")
        
        # Check window interactions for current level
        current_windows = windows_by_level.get(level, [])
        for window in current_windows:
            if player.colliderect(window["rect"]):
                display_text = True
                interaction_target = window
                if keys[pygame.K_RETURN]:  # Press Enter to interact
                    if player_coins >= window["cost"]:
                        player_coins -= window["cost"]
                        level = window["target"]
                        # Reset player position for new level
                        player.x, player.y = 50, HEIGHT // 2
                        play_sound("door")
        
        # Back to main level button
        if level > 0 and player.colliderect(back_rect):
            display_text = True
            if keys[pygame.K_RETURN]:
                level = 0
                player.x, player.y = 50, HEIGHT // 2
                play_sound("door")
        
        # Draw walls for current level
        for wall in walls_by_level.get(level, []):
            pygame.draw.rect(screen, WALL_COLOR, wall)
        
        # Draw doors and windows for the current level
        current_doors = doors_by_level.get(level, [])
        for door in current_doors:
            if game_settings["use_custom_models"] and "door" in item_sprites:
                screen.blit(item_sprites["door"], door["rect"])
            else:
                pygame.draw.rect(screen, DOOR_COLOR, door["rect"])
            
            # Cost text with background
            cost_bg = pygame.Rect(door["rect"].x - 10, door["rect"].y - 25, 70, 20)
            pygame.draw.rect(screen, (50, 50, 50), cost_bg, border_radius=3)
            cost_text = small_font.render(f"Cost: {door['cost']}", True, TEXT_COLOR)
            screen.blit(cost_text, (door["rect"].x - 5, door["rect"].y - 20))
            
        current_windows = windows_by_level.get(level, [])
        for window in current_windows:
            if game_settings["use_custom_models"] and "window" in item_sprites:
                screen.blit(item_sprites["window"], window["rect"])
            else:
                pygame.draw.rect(screen, WINDOW_COLOR, window["rect"])
            
            # Cost text with background
            cost_bg = pygame.Rect(window["rect"].x - 10, window["rect"].y - 25, 70, 20)
            pygame.draw.rect(screen, (50, 50, 50), cost_bg, border_radius=3)
            cost_text = small_font.render(f"Cost: {window['cost']}", True, TEXT_COLOR)
            screen.blit(cost_text, (window["rect"].x - 5, window["rect"].y - 20))
        
        if level > 0:
            # Draw the return button in other levels
            pygame.draw.rect(screen, BACK_RECT_COLOR, back_rect)
            
            # Return text with background
            back_bg = pygame.Rect(back_rect.x - 5, back_rect.y - 25, 110, 20)
            pygame.draw.rect(screen, (50, 50, 50), back_bg, border_radius=3)
            back_text = small_font.render("Return (Enter)", True, TEXT_COLOR)
            screen.blit(back_text, (back_rect.x, back_rect.y - 20))
        
        # Draw coins for current level
        for coin in coins:
            if coin["level"] == level and not coin["collected"]:
                if game_settings["use_custom_models"] and "coin" in item_sprites:
                    screen.blit(item_sprites["coin"], coin["rect"])
                else:
                    pygame.draw.ellipse(screen, COIN_COLOR, coin["rect"])
        
        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen)
        
        # Draw player (with flash effect if recently hit)
        if current_time - last_hit_time < immunity_time:
            if (current_time // 100) % 2 == 0:  # Flash effect
                if game_settings["use_custom_models"] and player_sprites:
                    # Choose sprite based on direction
                    sprite_key = "right"
                    if player_direction == 0:
                        sprite_key = "right"
                    elif player_direction == 1:
                        sprite_key = "down"
                    elif player_direction == 2:
                        sprite_key = "left"
                    elif player_direction == 3:
                        sprite_key = "up"
                    
                    if sprite_key in player_sprites:
                        screen.blit(player_sprites[sprite_key], player)
                    else:
                        screen.blit(player_sprites.get("right", player_sprites[list(player_sprites.keys())[0]]), player)
                else:
                    pygame.draw.rect(screen, PLAYER_COLOR, player)
        else:
            if game_settings["use_custom_models"] and player_sprites:
                # Choose sprite based on direction
                sprite_key = "right"
                if player_direction == 0:
                    sprite_key = "right"
                elif player_direction == 1:
                    sprite_key = "down"
                elif player_direction == 2:
                    sprite_key = "left"
                elif player_direction == 3:
                    sprite_key = "up"
                
                if sprite_key in player_sprites:
                    screen.blit(player_sprites[sprite_key], player)
                else:
                    screen.blit(player_sprites.get("right", player_sprites[list(player_sprites.keys())[0]]), player)
            else:
                pygame.draw.rect(screen, PLAYER_COLOR, player)
        
        # Flashlight Effect
        draw_flashlight()
        
        # Draw UI elements on top of flashlight overlay
        draw_ui_elements()
    
    # Update the display and cap the frame rate
    pygame.display.flip()
    clock.tick(60)  # Cap the frame rate at 60 FPS

pygame.quit()
sys.exit()