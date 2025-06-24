import pygame
import math
import random
import os
import sys
import time # Import time module for cooldowns/timers

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
BOSS_COLOR = (150, 0, 150) # Purple for boss
PLAYER_SPEED = 5
ENEMY_SPEED = 2
BOSS_SPEED = 3 # Boss might need a different speed
TEXT_COLOR = (255, 255, 255)
FLASHLIGHT_ANGLE = math.radians(30)
FLASHLIGHT_LENGTH = 200

# Player Damage
PLAYER_BASIC_DAMAGE = 0.2
PLAYER_SKILL_DAMAGE = 2
PLAYER_SKILL_COOLDOWN = 3000 # milliseconds
BOSS_HEALTH_MAX = 6 # Player health units (6 hearts)

# Attack Damages (converted to player health units)
BOSS_LASER_DAMAGE = 1.5
BOSS_STOMP_DAMAGE = 1.0
BOSS_PUNCH_DAMAGE = 1.0

# Boss Attack Timers (milliseconds)
BOSS_IDLE_TIME = 500
BOSS_LASER_CHARGE_TIME = 1000
BOSS_LASER_FIRE_TIME = 500
BOSS_STOMP_PREP_TIME = 800
BOSS_STOMP_AOE_TIME = 300 # How long the AOE is active
BOSS_PUNCH_PREP_TIME = 600
BOSS_PUNCH_ACTIVE_TIME = 200 # How long the punch hitbox is active
BOSS_ATTACK_COOLDOWN = 1500 # Base cooldown between attacks

# Helper Ghost Spawning
GHOST_SPAWN_INTERVAL = 10000 # milliseconds
MAX_HELPER_GHOSTS = 3

# Coin requirement for Boss Door (Adjust as needed)
COINS_FOR_BOSS_DOOR = 20 # Total coins needed

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Door Explorer")

# Fonts
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 24)
boss_font = pygame.font.Font(None, 28) # Smaller font for boss info

# Game Settings
game_settings = {
    "sound_enabled": True,
    "sound_volume": 0.5,  # 0.0 to 1.0
    "brightness": 0.7,     # 0.0 to 1.0 (affects flashlight darkness)
    "use_custom_models": True,
    "use_custom_backgrounds": True
}

# Sound handling
sounds = {}
music = {} # Dictionary for music

def load_sounds():
    global sounds
    sound_files = {
        "coin": "coin.wav",
        "door": "door.wav",
        "hit": "hit.wav",
        "gameover": "gameover.wav",
        "menu": "menu.wav",
        # Add new sounds for boss fight
        "boss_hit": "boss_hit.wav", # Sound when boss takes damage
        "boss_laser_charge": "boss_laser_charge.wav",
        "boss_laser_fire": "boss_laser_fire.wav",
        "boss_stomp": "boss_stomp.wav",
        "boss_punch": "boss_punch.wav",
        "win": "win.wav" # Sound for winning the game
    }

    # Try to load each sound
    for name, file in sound_files.items():
        try:
            sounds[name] = pygame.mixer.Sound(file)
            print(f"Loaded sound: {file}")
        except:
            sounds[name] = None
            print(f"Could not load sound: {file}")

def load_music():
    global music
    music_files = {
        "menu_music": "menu.wav",
        "game_music": "game_music.ogg",
        "boss_music": "boss_music.ogg", # Add boss music
        "win_music": "win_music.ogg" # Music for winning
    }
    for name, file in music_files.items():
        try:
            music[name] = file # Store filename, load with mixer.music.load() later
            print(f"Found music file: {file}")
        except:
            music[name] = None
            print(f"Could not find music file: {file}")

def play_music(name, loop=-1):
    if game_settings["sound_enabled"] and name in music and music[name] is not None:
        try:
            pygame.mixer.music.stop() # Stop any currently playing music
            pygame.mixer.music.load(music[name])
            pygame.mixer.music.set_volume(game_settings["sound_volume"])
            pygame.mixer.music.play(loop)
            print(f"Playing music: {name}")
        except pygame.error as e:
             print(f"Error playing music '{name}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred while playing music '{name}': {e}")

def stop_music():
    pygame.mixer.music.stop()

def play_sound(name):
    if game_settings["sound_enabled"] and name in sounds and sounds[name] is not None:
        try:
            sounds[name].set_volume(game_settings["sound_volume"])
            sounds[name].play()
        except Exception as e:
            print(f"Error playing sound '{name}': {e}")

def stop_sound(name):
    if name in sounds and sounds[name] is not None:
        try:
            sounds[name].stop()
            # print(f"Stopped sound: {name}") # Optional: Confirmation message
        except Exception as e:
            print(f"Error stopping sound '{name}': {e}")
    # else:
        # print(f"Sound '{name}' not loaded or not found to stop.")

# Custom models
player_sprites = {}
enemy_sprites = {} # Will include default enemy and possibly helper ghosts
item_sprites = {}
level_background_image = {}
boss_sprites = {} # New dictionary for boss sprites

def load_sprites():
    global player_sprites, enemy_sprites, item_sprites, level_background_image, boss_sprites

    # --- Item Sprites ---
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

    # --- Player Sprites ---
    try:
        # Load sprites for each direction
        player_sprites = {
            "right": pygame.image.load("player_right.png"), # Assuming specific direction sprites
            "left": pygame.image.load("player_left.png"),
            "up": pygame.image.load("player_up.png"),
            "down": pygame.image.load("player_down.png")
        }
        # Scale sprites to player size
        for direction in list(player_sprites.keys()): # Iterate over a copy of keys
             if player_sprites[direction] is not None: # Only scale if loaded
                player_sprites[direction] = pygame.transform.scale(player_sprites[direction], (40, 40))
        print("Loaded player sprites")
    except:
        player_sprites = {}
        print("Could not load player sprites, using default shapes")

    # --- Enemy Sprites ---
    try:
        enemy_sprites["default"] = pygame.image.load("enemy.png") # Default enemy/ghost
        enemy_sprites["default"] = pygame.transform.scale(enemy_sprites["default"], (30, 30)) # Scale for regular enemies
        # If helper ghosts should look different, load another sprite here
        # enemy_sprites["helper_ghost"] = pygame.image.load("helper_ghost.png")
        # enemy_sprites["helper_ghost"] = pygame.transform.scale(enemy_sprites["helper_ghost"], (30, 30))
        print("Loaded enemy sprites")
    except:
        enemy_sprites = {}
        print("Could not load enemy sprites, using default shapes")

    # --- Boss Sprites ---
    try:
        boss_sprites["default"] = pygame.image.load("boss.png") # Load boss sprite
        # Scale boss sprite (adjust size as needed)
        boss_sprites["default"] = pygame.transform.scale(boss_sprites["default"], (100, 150))
        # Add other boss state sprites if available (e.g., "boss_attack1", "boss_damaged")
        print("Loaded boss sprites")
    except:
        boss_sprites = {}
        print("Could not load boss sprite, using default shape")

    # --- Background Image ---
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
BOSS_FIGHT = 5 # New state for the boss fight
GAME_WON = 6   # New state for winning the game
game_state = MENU

# Menu Buttons (adjust positions if adding more)
start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 80, 200, 60) # Shifted up
resume_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 120, 200, 60)
options_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 60) # Shifted down
reset_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 60) # Shifted down
menu_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 160, 200, 60) # Shifted down
quit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 240, 200, 60) # Shifted down
retry_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 60)

# Game Won Button
win_menu_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 60)
win_quit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 60)


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
player_max_health = 3 # Store max health

# Player Skill State
is_skilling = False
skill_ready = True
last_skill_time = 0

# Enemy Setup
# Create a class for enemies (used for helper ghosts)
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
        self.is_alive = True # Add status

    def update(self, player_rect, walls):
        if not self.is_alive or self.level != level:
            return False # Not alive or not on current level

        # Movement Logic (existing random or patrol)
        if self.patrol_mode and self.patrol_points:
             # Patrol between points (same as before)
            target = self.patrol_points[self.current_target]
            dx = target[0] - self.rect.x
            dy = target[1] - self.rect.y

            distance = math.sqrt(dx**2 + dy**2)

            if distance < self.speed: # Close enough to target
                self.current_target = (self.current_target + 1) % len(self.patrol_points)
            else:
                # Normalize direction
                if distance > 0:
                    dx = dx / distance * self.speed
                    dy = dy / distance * self.speed

                new_x = self.rect.x + dx
                new_y = self.rect.y + dy

                # Check for wall collisions (simplified for patrols)
                test_rect_x = pygame.Rect(new_x, self.rect.y, self.rect.width, self.rect.height)
                can_move_x = not any(test_rect_x.colliderect(wall) for wall in walls)
                if can_move_x:
                    self.rect.x = new_x

                test_rect_y = pygame.Rect(self.rect.x, new_y, self.rect.width, self.rect.height)
                can_move_y = not any(test_rect_y.colliderect(wall) for wall in walls)
                if can_move_y:
                    self.rect.y = new_y

                # If blocked in one direction, try the other? Or just stop movement?
                # For simplicity, we'll just let them move if possible.
        else:
            # Random movement (same as before)
            self.movement_timer += 1
            if self.movement_timer >= 60:
                self.direction = random.choice([0, 1, 2, 3])
                self.movement_timer = 0

            move_x, move_y = 0, 0
            if self.direction == 0: move_x = self.speed
            elif self.direction == 1: move_y = self.speed
            elif self.direction == 2: move_x = -self.speed
            elif self.direction == 3: move_y = -self.speed

            test_rect_x = pygame.Rect(self.rect.x + move_x, self.rect.y, self.rect.width, self.rect.height)
            can_move_x = not any(test_rect_x.colliderect(wall) for wall in walls)
            if can_move_x:
                self.rect.x += move_x
            else:
                if self.direction == 0: self.direction = 2
                elif self.direction == 2: self.direction = 0

            test_rect_y = pygame.Rect(self.rect.x, self.rect.y + move_y, self.rect.width, self.rect.height)
            can_move_y = not any(test_rect_y.colliderect(wall) for wall in walls)
            if can_move_y:
                self.rect.y += move_y
            else:
                if self.direction == 1: self.direction = 3
                elif self.direction == 3: self.direction = 1

            self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
            self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))

        # Check for collision with player
        return self.rect.colliderect(player_rect)

    def draw(self, surface):
         if self.is_alive and self.level == level:
            if game_settings["use_custom_models"] and "default" in enemy_sprites:
                surface.blit(enemy_sprites["default"], self.rect)
            else:
                pygame.draw.rect(surface, ENEMY_COLOR, self.rect)
                # Draw eyes if needed (same as before)
                eye_size = 6
                if self.direction == 0: pygame.draw.circle(surface, WHITE, (self.rect.right - 10, self.rect.y + 10), eye_size); pygame.draw.circle(surface, WHITE, (self.rect.right - 10, self.rect.y + 20), eye_size)
                elif self.direction == 1: pygame.draw.circle(surface, WHITE, (self.rect.x + 10, self.rect.bottom - 10), eye_size); pygame.draw.circle(surface, WHITE, (self.rect.x + 20, self.rect.bottom - 10), eye_size)
                elif self.direction == 2: pygame.draw.circle(surface, WHITE, (self.rect.x + 10, self.rect.y + 10), eye_size); pygame.draw.circle(surface, WHITE, (self.rect.x + 10, self.rect.y + 20), eye_size)
                elif self.direction == 3: pygame.draw.circle(surface, WHITE, (self.rect.x + 10, self.rect.y + 10), eye_size); pygame.draw.circle(surface, WHITE, (self.rect.x + 20, self.rect.y + 10), eye_size)

# --- New Boss Class ---
class Boss:
    def __init__(self, x, y, level):
        # Boss size (adjust based on sprite)
        self.rect = pygame.Rect(x, y, 100, 150)
        self.level = level
        self.health = BOSS_HEALTH_MAX # 6 hearts
        self.max_health = BOSS_HEALTH_MAX
        self.speed = BOSS_SPEED
        self.is_alive = True

        # Boss State Machine for Attacks/Movement
        self.state = "idle" # idle, charging_laser, firing_laser, stomp_prep, stomp_aoe, punch_prep, punch_active, dodging, cooldown
        self.state_timer = 0 # Timer for how long in current state
        self.attack_cooldown_timer = 0 # Timer for cooldown between attacks
        self.hits_taken_since_dodge = 0 # Counter for dodging logic

        # Attack Specifics (hitboxes, etc.)
        self.laser_rect = None
        self.stomp_rect = None # AOE rectangle
        self.punch_rect = None

    def update(self, player_rect, walls, current_time):
        if not self.is_alive or self.level != level:
            return # Only update if alive and on current level

        # Calculate attack speed multiplier based on health (slower when low health)
        # Max speed at full health, slowest at 0 health (never reached)
        # Let's make it linearly decrease attack_cooldown_timer by up to 50%
        health_ratio = self.health / self.max_health
        attack_speed_multiplier = 1 + (1 - health_ratio) * 0.5 # 1.0 (full health) to 1.5 (low health)
        current_attack_cooldown = BOSS_ATTACK_COOLDOWN * attack_speed_multiplier


        # --- State Machine Logic ---
        self.state_timer += clock.get_time() # Add delta time in milliseconds
        self.attack_cooldown_timer -= clock.get_time()

        if self.state == "idle":
            if self.state_timer >= BOSS_IDLE_TIME and self.attack_cooldown_timer <= 0:
                # Choose next attack
                available_attacks = ["laser", "stomp", "punch"] # Could make some attacks only available at certain health

                # Prioritize dodging if hits taken threshold is met
                # Let's implement the "dodges between every other basic attack"
                # Basic hits deal 0.5, so 2 basic hits = 1 health lost.
                # Let's dodge after 2 health units lost from basic hits (i.e., 4 basic hits)
                if self.hits_taken_since_dodge >= 4:
                     self.state = "dodging"
                     self.state_timer = 0
                     self.hits_taken_since_dodge = 0 # Reset counter
                     self.choose_dodge_target(walls) # Determine dodge location
                     play_sound("boss_stomp") # Use stomp sound for dodge? Or add a new one?
                else:
                    next_attack = random.choice(available_attacks)
                    if next_attack == "laser":
                        self.state = "charging_laser"
                        play_sound("boss_laser_charge")
                    elif next_attack == "stomp":
                        self.state = "stomp_prep"
                    elif next_attack == "punch":
                         self.state = "punch_prep"
                    self.state_timer = 0 # Reset state timer for new state

        elif self.state == "charging_laser":
            if self.state_timer >= BOSS_LASER_CHARGE_TIME:
                self.state = "firing_laser"
                self.state_timer = 0
                self.laser_rect = self.create_laser_rect(player_rect)
                play_sound("boss_laser_fire") # Play laser fire sound

        elif self.state == "firing_laser":
            # Laser is active, check collision with player
            if self.state_timer >= BOSS_LASER_FIRE_TIME:
                self.state = "cooldown"
                self.state_timer = 0
                self.attack_cooldown_timer = current_attack_cooldown # Start cooldown
                self.laser_rect = None # Deactivate laser hitbox

        elif self.state == "stomp_prep":
             if self.state_timer >= BOSS_STOMP_PREP_TIME:
                 self.state = "stomp_aoe"
                 self.state_timer = 0
                 self.stomp_rect = self.create_stomp_rect()
                 play_sound("boss_stomp") # Play stomp sound

        elif self.state == "stomp_aoe":
             if self.state_timer >= BOSS_STOMP_AOE_TIME:
                 self.state = "cooldown"
                 self.state_timer = 0
                 self.attack_cooldown_timer = current_attack_cooldown
                 self.stomp_rect = None # Deactivate stomp hitbox

        elif self.state == "punch_prep":
            if self.state_timer >= BOSS_PUNCH_PREP_TIME:
                self.state = "punch_active"
                self.state_timer = 0
                self.punch_rect = self.create_punch_rect() # Determine punch hitbox based on player position? Or fixed area? Let's make it a frontal area.
                play_sound("boss_punch") # Play punch sound

        elif self.state == "punch_active":
            # Punch hitbox is active, check collision with player
            if self.state_timer >= BOSS_PUNCH_ACTIVE_TIME:
                self.state = "cooldown"
                self.state_timer = 0
                self.attack_cooldown_timer = current_attack_cooldown
                self.punch_rect = None # Deactivate punch hitbox

        elif self.state == "dodging":
             # Simple dodge movement: move towards the dodge target
             if hasattr(self, 'dodge_target'): # Ensure target exists
                dx = self.dodge_target[0] - self.rect.centerx
                dy = self.dodge_target[1] - self.rect.centery
                distance = math.sqrt(dx**2 + dy**2)

                dodge_speed = self.speed * 2 # Dodge is faster
                if distance > dodge_speed:
                    move_x = dx / distance * dodge_speed
                    move_y = dy / distance * dodge_speed
                    self.rect.x += move_x
                    self.rect.y += move_y
                else:
                    # Reached target, finish dodging
                    self.rect.center = self.dodge_target
                    self.state = "cooldown"
                    self.state_timer = 0
                    self.attack_cooldown_timer = current_attack_cooldown # Add cooldown after dodge

        elif self.state == "cooldown":
            if self.attack_cooldown_timer <= 0:
                self.state = "idle"
                self.state_timer = 0

        # Keep boss within bounds (optional, depends on arena design)
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))


    def take_damage(self, amount):
        if self.is_alive:
            self.health -= amount
            play_sound("boss_hit") # Play boss hit sound
            if amount == PLAYER_BASIC_DAMAGE: # Only count basic hits for dodge counter
                 self.hits_taken_since_dodge += amount * 2 # Increment by 1 for each 0.5 damage
                 print(f"Basic hit. Hits since dodge: {self.hits_taken_since_dodge}")
            elif amount == PLAYER_SKILL_DAMAGE:
                 print("Skill hit.")

            if self.health <= 0:
                self.health = 0 # Prevent negative health
                self.is_alive = False
                print("Boss defeated!")


    def create_laser_rect(self, player_rect):
        # Creates a rectangle representing the laser's path or hitbox
        # A simple implementation: a thin rectangle from boss towards player
        start_pos = self.rect.center
        end_pos = player_rect.center # Target where player *is* when laser starts

        # Create a rectangle between start and end
        # Need to account for thickness.
        # A simple way is to create a long thin rect aligned with the axis, then rotate it.
        # More complex: create a polygon or segment collision.
        # Let's simplify: create a long narrow rect pointing vaguely towards the player.
        # This is a simplification and might not be accurate for diagonal lasers.

        # Direction vector
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        distance = math.sqrt(dx**2 + dy**2)

        if distance == 0: return None # Should not happen if player exists

        # Define a long, thin rect along the x-axis starting from the boss center
        laser_length = max(distance, 300) # Ensure it reaches player or beyond
        laser_thickness = 20 # Visual thickness
        # Rect position relative to start_pos
        laser_rect = pygame.Rect(start_pos[0], start_pos[1] - laser_thickness // 2, laser_length, laser_thickness)

        # To do proper collision for a rotated rect/line is tricky.
        # For simplicity, let's just make the laser a fat line and check collision with the player rect.
        # This isn't a standard Rect collision but a line-rect or segment-rect check.
        # Pygame doesn't have this built-in directly.
        # We can approximate with a long thin rect rotated, but rotation complicates collision.
        # A common simplification: check points along the line against the player rect, or use a polygon.

        # Simpler approach: Define the laser as a start point and end point. Collision check later.
        # This requires checking player_rect intersection with the line segment.
        # Let's store start and end points instead of a rect for laser collision.
        self.laser_start_pos = start_pos
        self.laser_end_pos = end_pos # Store the target position when laser fires

        # For drawing, we can draw a line.
        return None # Return None, collision handled differently

    def create_stomp_rect(self):
         # Creates a circular or rectangular AOE area around the boss
         stomp_radius = 150 # Radius of the AOE effect
         # Return a rect that represents the boundary of the AOE for simple collision check
         return pygame.Rect(self.rect.centerx - stomp_radius, self.rect.centery - stomp_radius,
                            stomp_radius * 2, stomp_radius * 2)

    def create_punch_rect(self):
        # Creates a rectangle for the punch hitbox, e.g., in front of the boss
        punch_width = 80
        punch_height = 60
        # Position relative to boss based on player direction? Or just a fixed area?
        # Let's make it a fixed area slightly in front of the boss's current facing
        # This requires tracking boss facing, which we don't currently have.
        # Let's make it a simple rect near the boss, maybe slightly offset?
        # For now, a simple rect near the boss body.
        return pygame.Rect(self.rect.right, self.rect.centery - punch_height // 2, punch_width, punch_height) # Example: punches to the right


    def draw(self, surface):
        if not self.is_alive:
            return # Don't draw if dead

        # Draw boss sprite or shape
        if game_settings["use_custom_models"] and "default" in boss_sprites:
             surface.blit(boss_sprites["default"], self.rect)
        else:
            pygame.draw.rect(surface, BOSS_COLOR, self.rect)

        # Draw boss health bar
        health_bar_width = self.rect.width
        health_bar_height = 10
        health_bar_x = self.rect.x
        health_bar_y = self.rect.y - health_bar_height - 5 # Above the boss

        # Background bar (red)
        pygame.draw.rect(surface, (200, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))

        # Foreground bar (green)
        current_health_width = (self.health / self.max_health) * health_bar_width
        pygame.draw.rect(surface, (0, 200, 0), (health_bar_x, health_bar_y, current_health_width, health_bar_height))

        # Health text
        health_text = boss_font.render(f"{int(self.health)}/{int(self.max_health)}", True, WHITE)
        text_rect = health_text.get_rect(center=(health_bar_x + health_bar_width // 2, health_bar_y + health_bar_height // 2))
        surface.blit(health_text, text_rect)


        # Draw attack visualizations (approximations)
        if self.state == "charging_laser":
            # Draw a line showing the target direction during charge
            start_pos = self.rect.center
            end_pos = player.center # Player's current position
            pygame.draw.line(surface, (255, 0, 0, 100), start_pos, end_pos, 5) # Semi-transparent red line

        elif self.state == "firing_laser" and hasattr(self, 'laser_start_pos') and hasattr(self, 'laser_end_pos'):
             # Draw the actual laser line
             pygame.draw.line(surface, (255, 0, 0), self.laser_start_pos, self.laser_end_pos, 10) # Solid red line

        elif self.state == "stomp_aoe" and self.stomp_rect:
             # Draw the AOE circle/rectangle
             pygame.draw.ellipse(surface, (255, 100, 0, 150), self.stomp_rect.inflate(20,20)) # Draw slightly bigger to show effect

        elif self.state == "punch_active" and self.punch_rect:
             # Draw the punch hitbox area
             pygame.draw.rect(surface, (255, 100, 0, 150), self.punch_rect) # Draw slightly bigger to show effect


    # Helper method to find a valid dodge target
    def choose_dodge_target(self, walls):
        # Find a random point within the arena bounds that is not too close to walls or the player
        arena_rect = pygame.Rect(20, 20, WIDTH - 40, HEIGHT - 40) # Example arena bounds

        for _ in range(50): # Try up to 50 times to find a valid spot
            target_x = random.randint(arena_rect.left + self.rect.width, arena_rect.right - self.rect.width)
            target_y = random.randint(arena_rect.top + self.rect.height, arena_rect.bottom - self.rect.height)
            test_rect = pygame.Rect(target_x - self.rect.width // 2, target_y - self.rect.height // 2, self.rect.width, self.rect.height) # Center the test rect on the target point

            # Check collision with walls
            collides_with_wall = any(test_rect.colliderect(wall) for wall in walls)

            # Check distance to player (don't dodge too close)
            distance_to_player = math.dist((target_x, target_y), player.center)
            too_close_to_player = distance_to_player < 200 # Minimum distance from player after dodging

            if not collides_with_wall and not too_close_to_player:
                self.dodge_target = (target_x, target_y)
                print(f"Boss dodging to {self.dodge_target}")
                return

        # If no valid target found after tries, just move randomly or stay put
        self.dodge_target = self.rect.center # Stay put if nowhere good to go
        print("Boss failed to find valid dodge target, staying put.")


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
    2: [ # This was level 2, now maybe a transition level or removed? Let's keep it for now.
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
    # --- New Boss Level Walls ---
    3: [
         # Border walls (maybe thicker or different color?)
        pygame.Rect(0, 0, WIDTH, 30),  # Top
        pygame.Rect(0, HEIGHT-30, WIDTH, 30),  # Bottom
        pygame.Rect(0, 0, 30, HEIGHT),  # Left
        pygame.Rect(WIDTH-30, 0, 30, HEIGHT),  # Right
        # Maybe some pillars or obstacles in the arena?
        pygame.Rect(WIDTH // 4 - 20, HEIGHT // 4 - 20, 40, 40),
        pygame.Rect(WIDTH * 3 // 4 - 20, HEIGHT // 4 - 20, 40, 40),
        pygame.Rect(WIDTH // 4 - 20, HEIGHT * 3 // 4 - 20, 40, 40),
        pygame.Rect(WIDTH * 3 // 4 - 20, HEIGHT * 3 // 4 - 20, 40, 40),
    ]
}

# Interactable Objects by Level
# Level 0 - Main Hub
doors_by_level = {
    0: [
        {"rect": pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2, 50, 100), "cost": 5, "target": 1, "type": "door"},
        {"rect": pygame.Rect(WIDTH // 2 + 150, HEIGHT // 2 - 50, 50, 100), "cost": 10, "target": 2, "type": "door"},
    ],
    1: [
        # Door to Level 2 (original)
        {"rect": pygame.Rect(650, 300, 50, 100), "cost": 20, "target": 2, "type": "door"},
        # --- New Boss Door in Level 1 ---
        {"rect": pygame.Rect(50, HEIGHT - 150, 50, 100), "cost": COINS_FOR_BOSS_DOOR, "target": 3, "type": "door", "is_boss_door": True}, # Door to boss level (Level 3)
    ],
    2: [
        {"rect": pygame.Rect(100, 400, 50, 100), "cost": 15, "target": 0, "type": "door"},
    ],
    # Level 3 (Boss Level) has no doors out initially, player must defeat boss or lose
    # Could add a specific "Exit Arena" door if desired, maybe only visible after boss defeat
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

# Back to Level 0 Button (only appears in levels 1 and 2)
back_rect = pygame.Rect(WIDTH - 150, 50, 100, 50)

# Initialize enemies for each level (excluding the boss)
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

    # Level 3 (Boss level) enemies - These will be helper ghosts spawned *during* the fight
    # We don't define them here, they are created dynamically
]

# --- New Boss Instance ---
boss = None # Boss variable, initialized to None

# Function to generate coins for a level
def generate_coins(level_num, num_coins=10):
    level_coins = []
    # Get walls, doors, windows for this level to avoid placing coins on them
    level_walls = walls_by_level.get(level_num, [])
    level_doors = [d["rect"] for d in doors_by_level.get(level_num, [])]
    level_windows = [w["rect"] for w in windows_by_level.get(level_num, [])]

    for _ in range(num_coins):
        attempts = 0
        while attempts < 100: # Limit attempts to avoid infinite loop
            coin_x = random.randint(50, WIDTH - 50)
            coin_y = random.randint(50, HEIGHT - 50)
            coin_rect = pygame.Rect(coin_x, coin_y, 20, 20)

            # Ensure coins don't spawn on walls, doors or windows
            valid_position = True
            if any(coin_rect.colliderect(wall) for wall in level_walls):
                valid_position = False
            if valid_position and any(coin_rect.colliderect(door_rect) for door_rect in level_doors):
                 valid_position = False
            if valid_position and any(coin_rect.colliderect(window_rect) for window_rect in level_windows):
                 valid_position = False

            if valid_position:
                level_coins.append({
                    "rect": coin_rect,
                    "level": level_num,
                    "collected": False
                })
                break # Found a valid spot, exit the while loop
            attempts += 1
        if attempts >= 100:
             print(f"Warning: Could not find a valid spot for a coin in level {level_num} after many attempts.")

    return level_coins

# Game Variables
level = 0
running = True
display_text = False
interaction_target = None # The door/window the player is near

# Background Colors per Level
level_colors = [(50, 50, 50), (100, 100, 255), (255, 100, 100), (50, 0, 50)] # Added color for boss level

# Generate initial coins for all levels
coins = []
coins.extend(generate_coins(0, 15))
coins.extend(generate_coins(1, 20))
coins.extend(generate_coins(2, 25))
# No coins needed in boss level

# Function to reset the game
def reset_game():
    global player, player_coins, player_health, level, coins, game_state, last_hit_time, enemies, boss, is_skilling, skill_ready, last_skill_time, last_ghost_spawn_time
    print("Resetting game...")

    # Stop any music playing
    stop_music()

    # Reset player position and attributes
    player.x, player.y = 50, HEIGHT // 2
    global player_direction # Need to global this if resetting
    player_direction = 0
    player_coins = 0
    player_health = player_max_health # Reset health
    level = 0
    last_hit_time = 0
    is_skilling = False # Reset skill state
    skill_ready = True
    last_skill_time = 0

    # Reset enemies
    enemies = [] # Clear existing enemies
    # Re-populate initial enemies for levels 0, 1, 2
    enemies.extend([
        Enemy(300, 200, 0),
        Enemy(500, 400, 0, [(500, 400), (600, 400), (600, 500), (500, 500)]),
        Enemy(150, 300, 1),
        Enemy(400, 150, 1),
        Enemy(600, 300, 1, [(600, 300), (700, 300), (700, 500), (600, 500)]),
        Enemy(300, 200, 2),
        Enemy(500, 400, 2),
        Enemy(650, 300, 2),
        Enemy(400, 150, 2, [(400, 150), (500, 150), (500, 300), (400, 300)]),
    ])
    print(f"Initial enemies reset. Total enemies: {len(enemies)}")


    # Reset boss
    boss = None # Clear boss instance
    last_ghost_spawn_time = 0 # Reset timer for helper ghosts

    # Regenerate coins
    coins = [] # Clear existing coins
    coins.extend(generate_coins(0, 15))
    coins.extend(generate_coins(1, 20))
    coins.extend(generate_coins(2, 25)) # No coins in boss level

    # Set initial game state
    game_state = MENU # Usually returns to menu after reset, but can be PLAYING if reset from pause


# --- Drawing Functions (Modified) ---

def draw_flashlight():
    center_x, center_y = player.x + player.width // 2, player.y + player.height // 2

    # Determine angle based on player direction
    angle = 0
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
    # In boss fight, maybe less darkness or a different effect? For now, keep consistent.
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
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4)) # Shifted up
    screen.blit(title_text, title_rect)

    # Draw buttons
    draw_button(start_button, "Start Game")
    draw_button(options_button, "Options")
    draw_button(quit_button, "Quit Game")

    # Instructions
    instructions = [
        "Use WASD or Arrow Keys to move",
        "Collect coins to open doors and windows",
        "Press Enter to interact with objects",
        "Press ESC to pause game",
        "Press Space to use Skill (Boss Fight)" # Add skill instruction
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

# --- New Game Won Drawing Function ---
def draw_game_won():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((50, 50, 150, 200)) # Blue-ish overlay
    screen.blit(overlay, (0, 0))

    # Draw title
    title_text = title_font.render("You Won!", True, (100, 255, 100)) # Green text
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_text, title_rect)

    # Draw score/stats
    score_text = font.render(f"Coins Collected: {player_coins}", True, COIN_COLOR)
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(score_text, score_rect)

    # Draw buttons
    draw_button(win_menu_button, "Main Menu")
    draw_button(win_quit_button, "Quit Game")


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

    health_text = font.render(f"Health: {int(player_health)}/{int(player_max_health)}", True, (255, 50, 50)) # Cast to int for display
    screen.blit(health_text, (25, 120))

    # Skill Cooldown Indicator (only show in boss fight or maybe always?)
    if game_state == BOSS_FIGHT or True: # Show always for testing
         skill_bg = pygame.Rect(WIDTH - 150, 15, 130, 40)
         pygame.draw.rect(screen, (50, 50, 50), skill_bg, border_radius=5)
         skill_color = (0, 255, 0) if skill_ready else (255, 255, 0) # Green if ready, Yellow if on cooldown
         pygame.draw.rect(screen, skill_color, skill_bg, 2, border_radius=5)

         skill_text = font.render("Skill", True, WHITE)
         screen.blit(skill_text, (WIDTH - 140, 20))

         if not skill_ready:
             # Display cooldown timer
             time_since_skill = pygame.time.get_ticks() - last_skill_time
             remaining_cooldown = max(0, PLAYER_SKILL_COOLDOWN - time_since_skill)
             cooldown_seconds = math.ceil(remaining_cooldown / 1000) # Round up to nearest second
             cooldown_text = small_font.render(f"CD: {cooldown_seconds}s", True, WHITE)
             screen.blit(cooldown_text, (WIDTH - 140, 45)) # Position below "Skill"


# Function to check line-rectangle collision (for laser)
# This is a simplified check, assuming axis-aligned rects and line segments
# A more robust solution might use a library or more complex geometry
def check_line_rect_collision(p1, p2, rect):
    # Check if any corner of the rect is on the same side of the line defined by p1-p2.
    # If corners are on different sides, the line segment might cross the rect.
    # Also check if the endpoints of the line are inside the rect.

    # Check if line endpoints are inside the rect
    if rect.collidepoint(p1) or rect.collidepoint(p2):
        return True

    # Check if the line intersects any of the rectangle's four segments
    lines = [
        ((rect.left, rect.top), (rect.right, rect.top)), # Top edge
        ((rect.left, rect.bottom), (rect.right, rect.bottom)), # Bottom edge
        ((rect.left, rect.top), (rect.left, rect.bottom)), # Left edge
        ((rect.right, rect.top), (rect.right, rect.bottom)) # Right edge
    ]

    def intersect(l1_p1, l1_p2, l2_p1, l2_p2):
        # Check if two line segments intersect
        # Simplified check: orientation test
        o1 = orientation(l1_p1, l1_p2, l2_p1)
        o2 = orientation(l1_p1, l1_p2, l2_p2)
        o3 = orientation(l2_p1, l2_p2, l1_p1)
        o4 = orientation(l2_p1, l2_p2, l1_p2)

        # General case
        if o1 != 0 and o1 == o2: return False # Same side, no intersection
        if o3 != 0 and o3 == o4: return False # Same side, no intersection
        if o1 != o2 and o3 != o4: return True # Different sides, likely intersect

        # Special cases
        if o1 == 0 and on_segment(l1_p1, l2_p1, l1_p2): return True # l2_p1 on l1
        if o2 == 0 and on_segment(l1_p1, l2_p2, l1_p2): return True # l2_p2 on l1
        if o3 == 0 and on_segment(l2_p1, l1_p1, l2_p2): return True # l1_p1 on l2
        if o4 == 0 and on_segment(l2_p1, l1_p2, l2_p2): return True # l1_p2 on l2

        return False

    def orientation(p, q, r):
        # 0: Collinear, 1: Clockwise, 2: Counterclockwise
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        if val == 0: return 0
        return 1 if val > 0 else 2

    def on_segment(p, q, r):
        # Check if point q lies on segment pr
        return (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
                q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))


    for line_segment in lines:
        if intersect(p1, p2, line_segment[0], line_segment[1]):
            return True

    return False # No intersection found


# Initialize other variables
immunity_time = 1000  # ms of immunity after being hit by regular enemy
last_hit_time = 0 # Time when player was last hit by *anything*

# Boss specific timers
last_ghost_spawn_time = 0

# Load resources
load_sounds()
load_music() # Load music files
load_sprites()

# Game Loop
clock = pygame.time.Clock()
running = True

# Start menu music
play_music("menu_music", -1) # Loop infinitely

while running:
    dt = clock.tick(60) # Delta time in milliseconds
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == PLAYING or game_state == BOSS_FIGHT: # Pause from playing or boss fight
                    game_state = PAUSED
                    stop_music() # Stop music on pause
                elif game_state == PAUSED:
                    game_state = PLAYING if level != 3 else BOSS_FIGHT # Resume to correct state
                    if level != 3: play_music("game_music", -1) # Resume game music
                    else: play_music("boss_music", -1) # Resume boss music
                elif game_state == OPTIONS:
                    # If coming from pause menu, go back to pause, otherwise main menu
                    if 'prev_state' in locals() and prev_state == PAUSED: # Check if prev_state exists and was PAUSED
                         game_state = PAUSED
                    elif level > 0 and game_state != MENU: # If in game (not menu) and paused before options
                         game_state = PAUSED # Assuming options from pause
                    else: # Options from main menu
                         game_state = MENU

                    play_sound("menu") # Play sound when exiting options
                    if game_state == MENU: play_music("menu_music", -1) # Resume menu music if going to menu
                    # Music resumes when exiting pause menu handled above

            # Player Skill Input (only in PLAYING or BOSS_FIGHT)
            if (game_state == PLAYING or game_state == BOSS_FIGHT) and event.key == pygame.K_SPACE:
                 if skill_ready:
                    is_skilling = True # Flag that skill is active for next hit
                    skill_ready = False
                    last_skill_time = current_time
                    print("Skill activated!")
                    # You might want a visual/sound effect here

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            # Menu buttons
            if game_state == MENU:
                if start_button.collidepoint(mouse_pos):
                    reset_game() # Reset game state before starting
                    game_state = PLAYING
                    play_music("game_music", -1) # Start game music
                elif options_button.collidepoint(mouse_pos):
                    prev_state = game_state # Store previous state
                    game_state = OPTIONS
                elif quit_button.collidepoint(mouse_pos):
                    running = False

            # Pause Menu buttons
            elif game_state == PAUSED:
                if resume_button.collidepoint(mouse_pos):
                    game_state = PLAYING if level != 3 else BOSS_FIGHT
                    if level != 3: play_music("game_music", -1)
                    else: play_music("boss_music", -1)
                elif options_button.collidepoint(mouse_pos):
                    prev_state = game_state # Store previous state
                    game_state = OPTIONS
                elif reset_button.collidepoint(mouse_pos):
                    reset_game()
                    game_state = PLAYING # Go back to playing state after reset
                    play_music("game_music", -1)
                elif menu_button.collidepoint(mouse_pos):
                    reset_game()
                    game_state = MENU
                    play_music("menu_music", -1)
                elif quit_button.collidepoint(mouse_pos):
                    running = False

            # Game Over buttons
            elif game_state == GAME_OVER:
                if retry_button.collidepoint(mouse_pos):
                    reset_game()
                    game_state = PLAYING
                    play_music("game_music", -1)
                elif menu_button.collidepoint(mouse_pos):
                    reset_game()
                    game_state = MENU
                    play_music("menu_music", -1)
                elif quit_button.collidepoint(mouse_pos):
                    running = False

            # Game Won buttons
            elif game_state == GAME_WON:
                 if win_menu_button.collidepoint(mouse_pos):
                     reset_game()
                     game_state = MENU
                     play_music("menu_music", -1)
                 elif win_quit_button.collidepoint(mouse_pos):
                     running = False


            # Options Menu
            elif game_state == OPTIONS:
                if back_options_button.collidepoint(mouse_pos):
                    # Restore previous state or default to MENU
                    if 'prev_state' in locals():
                         game_state = prev_state
                    elif level > 0: # If in game (not menu)
                         game_state = PAUSED # Assume options were from pause
                    else:
                         game_state = MENU

                    play_sound("menu")
                    if game_state == MENU: play_music("menu_music", -1)
                    # Music resumes when exiting pause menu handled above

                # Sound toggle
                elif sound_toggle_rect.collidepoint(mouse_pos):
                    game_settings["sound_enabled"] = not game_settings["sound_enabled"]
                    # Instantly apply music/sound volume change if music is playing
                    pygame.mixer.music.set_volume(game_settings["sound_volume"] if game_settings["sound_enabled"] else 0)
                    if game_settings["sound_enabled"]: play_sound("menu")

                # Models toggle
                elif models_toggle_rect.collidepoint(mouse_pos):
                    game_settings["use_custom_models"] = not game_settings["use_custom_models"]
                    if game_settings["sound_enabled"]: play_sound("menu")


                # Volume slider
                elif volume_slider_rect.collidepoint(mouse_pos):
                    rel_x = mouse_pos[0] - volume_slider_rect.x
                    game_settings["sound_volume"] = max(0, min(1, rel_x / volume_slider_rect.width))
                    volume_handle_rect.x = volume_slider_rect.x + int(game_settings["sound_volume"] * volume_slider_rect.width) - 10
                    pygame.mixer.music.set_volume(game_settings["sound_volume"] if game_settings["sound_enabled"] else 0)
                    if game_settings["sound_enabled"]: play_sound("menu")
                    dragging_volume = True

                # Brightness slider
                elif brightness_slider_rect.collidepoint(mouse_pos):
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
                pygame.mixer.music.set_volume(game_settings["sound_volume"] if game_settings["sound_enabled"] else 0)

            if dragging_brightness:
                rel_x = event.pos[0] - brightness_slider_rect.x
                game_settings["brightness"] = max(0, min(1, rel_x / brightness_slider_rect.width))
                brightness_handle_rect.x = brightness_slider_rect.x + int(game_settings["brightness"] * brightness_slider_rect.width) - 10

    # --- Game Logic Update (Only in PLAYING and BOSS_FIGHT states) ---
    if game_state == PLAYING or game_state == BOSS_FIGHT:

        # Get current level walls
        current_walls = walls_by_level.get(level, [])

        # Player Movement
        keys = pygame.key.get_pressed()
        # moved = False # Keep track if player moved (not used in final code, but useful for animations etc.)

        new_x, new_y = player.x, player.y

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            new_x -= PLAYER_SPEED
            player_direction = 2  # Left
            # moved = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            new_x += PLAYER_SPEED
            player_direction = 0  # Right
            # moved = True
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_y -= PLAYER_SPEED
            player_direction = 3  # Up
            # moved = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_y += PLAYER_SPEED
            player_direction = 1  # Down
            # moved = True

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

        # --- Skill State Update ---
        if is_skilling:
            # Skill effect is active for a short duration? Or only for the *next* hit?
            # Let's make it active until the player collides with an enemy/boss.
            # If you wanted a duration, you'd add a timer here:
            # if current_time - skill_active_start_time > SKILL_DURATION: is_skilling = False
            pass # Skill flag stays True until a hit is registered


        # --- Skill Cooldown Update ---
        if not skill_ready:
            if current_time - last_skill_time >= PLAYER_SKILL_COOLDOWN:
                skill_ready = True
                is_skilling = False # Ensure skill flag is off when cooldown finishes
                print("Skill ready!")


        # Coin Collection (Only in PLAYING state)
        if game_state == PLAYING:
            for coin in coins:
                if coin["level"] == level and not coin["collected"]:
                    if player.colliderect(coin["rect"]):
                        coin["collected"] = True
                        player_coins += 1
                        play_sound("coin")

        # Enemy Collision and Updates (Enemies on current level)
        # Use a list comprehension to keep only alive enemies
        active_enemies = [e for e in enemies if e.is_alive and e.level == level]

        for enemy in active_enemies:
            if enemy.update(player, current_walls):
                # Player hit by a regular enemy
                if current_time - last_hit_time > immunity_time:
                    player_health -= 1
                    play_sound("hit")
                    last_hit_time = current_time # Reset immunity timer
                    print(f"Player hit by enemy. Health: {player_health}")
                    # Check for game over after taking damage
                    if player_health <= 0:
                        stop_music() # Stop game music
                        game_state = GAME_OVER
                        play_sound("gameover")


        # --- Boss Logic (Only in BOSS_FIGHT state) ---
        if game_state == BOSS_FIGHT:
            if boss is None:
                 # Initialize boss when entering the boss level for the first time
                 boss = Boss(WIDTH // 2 - 50, HEIGHT // 4, level)
                 print("Boss spawned.")
                 last_ghost_spawn_time = current_time # Start ghost timer when boss spawns
                 stop_music() # Stop regular game music
                 play_music("boss_music", -1) # Start boss music

            if boss and boss.is_alive:
                boss.update(player, current_walls, current_time) # Pass current_time

                # Check player collision with boss body (basic hit)
                if player.colliderect(boss.rect):
                     if current_time - last_hit_time > immunity_time: # Use same immunity timer
                         # Check if boss is currently vulnerable to basic hits
                         # Based on the "dodges between every other basic attack" interpretation,
                         # let's say the boss is *not* vulnerable while dodging or in an attack state.
                         # It's only vulnerable during "idle" or "cooldown".
                         is_vulnerable_to_basic = boss.state in ["idle", "cooldown"] # or maybe just "idle"

                         if is_vulnerable_to_basic or is_skilling: # Skill hits can bypass basic vulnerability?
                             damage_dealt = 0
                             if is_skilling:
                                 damage_dealt = PLAYER_SKILL_DAMAGE
                                 is_skilling = False # Skill consumed on hit
                             elif is_vulnerable_to_basic:
                                 damage_dealt = PLAYER_BASIC_DAMAGE

                             if damage_dealt > 0:
                                 boss.take_damage(damage_dealt)
                                 print(f"Boss hit for {damage_dealt}. Boss Health: {boss.health}")


                # Check player collision with boss attacks (Laser, Stomp, Punch)
                if current_time - last_hit_time > immunity_time:
                     # Laser collision check
                     if boss.state == "firing_laser" and hasattr(boss, 'laser_start_pos') and hasattr(boss, 'laser_end_pos'):
                         # Check line segment collision with player rect
                         if check_line_rect_collision(boss.laser_start_pos, boss.laser_end_pos, player):
                            player_health -= BOSS_LASER_DAMAGE
                            play_sound("hit") # Use player hit sound
                            last_hit_time = current_time
                            print(f"Player hit by laser. Health: {player_health}")


                     # Stomp AOE collision check
                     if boss.state == "stomp_aoe" and boss.stomp_rect:
                         if player.colliderect(boss.stomp_rect):
                             player_health -= BOSS_STOMP_DAMAGE
                             play_sound("hit")
                             last_hit_time = current_time
                             print(f"Player hit by stomp. Health: {player_health}")

                     # Punch collision check
                     if boss.state == "punch_active" and boss.punch_rect:
                         if player.colliderect(boss.punch_rect):
                             player_health -= BOSS_PUNCH_DAMAGE
                             play_sound("hit")
                             last_hit_time = current_time
                             print(f"Player hit by punch. Health: {player_health}")


                     # Check for game over after taking damage from boss attack
                     if player_health <= 0:
                         stop_music()
                         game_state = GAME_OVER
                         play_sound("gameover")


                # Handle Helper Ghost Spawning
                if current_time - last_ghost_spawn_time >= GHOST_SPAWN_INTERVAL:
                    living_helper_ghosts = [e for e in enemies if e.level == level and e.is_alive]
                    if len(living_helper_ghosts) < MAX_HELPER_GHOSTS:
                        # Spawn a new ghost near the boss, but not on the boss
                        spawn_x = boss.rect.centerx + random.randint(-100, 100)
                        spawn_y = boss.rect.centery + random.randint(-100, 100)
                        new_ghost_rect = pygame.Rect(spawn_x, spawn_y, 30, 30)
                        # Ensure spawn location is valid (not on walls or boss)
                        if not any(new_ghost_rect.colliderect(wall) for wall in current_walls) and \
                           not new_ghost_rect.colliderect(boss.rect):
                             enemies.append(Enemy(spawn_x, spawn_y, level)) # Add to the main enemies list
                             last_ghost_spawn_time = current_time
                             print("Spawned helper ghost.")

            # Check for boss defeat (happens inside Boss.take_damage, but re-check state)
            if boss and not boss.is_alive:
                 game_state = GAME_WON # Transition to win state
                 stop_music() # Stop boss music
                 play_sound("win") # Play win sound
                 play_music("win_music", 0) # Play win music once

        # Interaction Logic (Doors, Windows, Back button)
        display_text = False
        interaction_target = None

        if game_state == PLAYING: # Only check interaction in non-boss playing state
             # Check door interactions for current level
            current_doors = doors_by_level.get(level, [])
            for door in current_doors:
                if player.colliderect(door["rect"]):
                    display_text = True
                    interaction_target = door
                    if keys[pygame.K_RETURN]:  # Press Enter to interact
                        # Check special condition for boss door
                        if door.get("is_boss_door") and player_coins < door["cost"]:
                            # Interaction text already shows cost, no change needed here
                            pass # Cannot enter yet
                        elif player_coins >= door["cost"]:
                            player_coins -= door["cost"]
                            prev_level = level # Store old level before changing
                            level = door["target"]
                            print(f"Entering level {level}")
                            # Reset player position for new level
                            player.x, player.y = 50, HEIGHT // 2
                            play_sound("door")

                            # Check if entering the boss level
                            if level == 3:
                                game_state = BOSS_FIGHT
                                boss = Boss(WIDTH // 2 - 50, HEIGHT // 4, level) # Create the boss instance
                                last_ghost_spawn_time = current_time
                                stop_music()
                                play_music("boss_music", -1)
                            # If transitioning between regular levels, ensure game music is playing
                            elif prev_level == 3 and level != 3: # Exiting boss level (unlikely with current door config, but good check)
                                stop_music()
                                play_music("game_music", -1)
                            elif level != 3 and pygame.mixer.music.get_busy() == 0: # Not boss level and no music
                                play_music("game_music", -1) # Ensure game music is playing


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
                            print(f"Entering level {level}")
                            # Reset player position for new level
                            player.x, player.y = 50, HEIGHT // 2
                            play_sound("door")
                            # Ensure game music is playing if not in boss level
                            if level != 3 and pygame.mixer.music.get_busy() == 0:
                                play_music("game_music", -1)


            # Back to main level button (only in levels 1 and 2)
            if level > 0 and level != 3 and player.colliderect(back_rect): # Don't show in boss level
                display_text = True
                # Simulate back button as an interaction target for text display
                interaction_target = {"type": "Back to Level 0", "cost": 0} # No cost, just for text
                if keys[pygame.K_RETURN]:
                    level = 0
                    print("Returning to level 0")
                    player.x, player.y = 50, HEIGHT // 2
                    play_sound("door")
                    if pygame.mixer.music.get_busy() == 0: # If no music is playing (e.g. stopped in options)
                         play_music("game_music", -1) # Ensure game music is playing


    # --- Drawing (based on game state) ---
    if game_state == MENU:
        draw_menu()

    elif game_state == OPTIONS:
        draw_options_menu()

    elif game_state == GAME_OVER:
        draw_game_over()

    elif game_state == GAME_WON:
        draw_game_won()

    elif game_state == PAUSED:
        # Draw the underlying game state first, then the pause menu overlay
        # Get current level walls
        current_walls = walls_by_level.get(level, [])
        if game_settings["use_custom_backgrounds"] and level_background_image is not None:
            screen.blit(level_background_image, (0, 0))
        else:
            screen.fill(level_colors[level % len(level_colors)])

        # Draw walls, objects, enemies, player (static - not updated)
        for wall in current_walls:
            pygame.draw.rect(screen, WALL_COLOR, wall)

        current_doors = doors_by_level.get(level, [])
        for door in current_doors:
            if game_settings["use_custom_models"] and "door" in item_sprites:
                screen.blit(item_sprites["door"], door["rect"])
            else:
                pygame.draw.rect(screen, DOOR_COLOR, door["rect"])
            cost_text = small_font.render(f"Cost: {door['cost']}", True, TEXT_COLOR)
            screen.blit(cost_text, (door["rect"].x - 5, door["rect"].y - 20))

        current_windows = windows_by_level.get(level, [])
        for window in current_windows:
             if game_settings["use_custom_models"] and "window" in item_sprites:
                 screen.blit(item_sprites["window"], window["rect"])
             else:
                 pygame.draw.rect(screen, WINDOW_COLOR, window["rect"])
             cost_text = small_font.render(f"Cost: {window['cost']}", True, TEXT_COLOR)
             screen.blit(cost_text, (window["rect"].x - 5, window["rect"].y - 20))

        if level > 0 and level != 3:
             pygame.draw.rect(screen, BACK_RECT_COLOR, back_rect)
             back_text = small_font.render("Return (Enter)", True, TEXT_COLOR)
             screen.blit(back_text, (back_rect.x, back_rect.y - 20))

        # Draw coins (if in PLAYING state originally)
        if level != 3: # Only draw coins if not the boss level
            for coin in coins:
                if coin["level"] == level and not coin["collected"]:
                    if game_settings["use_custom_models"] and "coin" in item_sprites:
                        screen.blit(item_sprites["coin"], coin["rect"])
                    else:
                        pygame.draw.ellipse(screen, COIN_COLOR, coin["rect"])

        # Draw enemies and boss (if they exist and were in the current level)
        for enemy in enemies:
             if enemy.level == level and enemy.is_alive:
                 enemy.draw(screen)

        if level == 3 and boss and boss.is_alive: # Draw boss if in boss level
             boss.draw(screen)

        # Draw player
        # Apply flash effect if recently hit, even if paused
        if current_time - last_hit_time < immunity_time:
             if (current_time // 100) % 2 == 0:
                 if game_settings["use_custom_models"] and player_sprites:
                     sprite_key = {0:"right", 1:"down", 2:"left", 3:"up"}.get(player_direction, "right")
                     screen.blit(player_sprites.get(sprite_key, player_sprites["right"]), player)
                 else:
                     pygame.draw.rect(screen, PLAYER_COLOR, player)
        else:
             if game_settings["use_custom_models"] and player_sprites:
                 sprite_key = {0:"right", 1:"down", 2:"left", 3:"up"}.get(player_direction, "right")
                 screen.blit(player_sprites.get(sprite_key, player_sprites["right"]), player)
             else:
                 pygame.draw.rect(screen, PLAYER_COLOR, player)


        draw_flashlight() # Draw flashlight effect
        draw_ui_elements() # Draw UI (coins, health, level)
        # Draw boss health bar if boss exists and level is 3
        if level == 3 and boss and boss.is_alive:
             # Boss health bar is drawn within the boss.draw method, but it's drawn on the *screen* surface,
             # so it appears correctly above the boss in the paused state.
             pass # Nothing extra needed here if boss draws itself and its bar

        # Finally, draw the pause menu overlay on top
        draw_pause_menu()


    elif game_state == PLAYING or game_state == BOSS_FIGHT: # Draw game state if not paused/menu/gameover/won
        # Get current level walls
        current_walls = walls_by_level.get(level, [])

        # Draw background
        if game_settings["use_custom_backgrounds"] and level_background_image is not None:
            screen.blit(level_background_image, (0, 0))
        else:
            screen.fill(level_colors[level % len(level_colors)])

        # Draw walls for current level
        for wall in current_walls:
            pygame.draw.rect(screen, WALL_COLOR, wall)

        # Draw doors and windows for the current level
        current_doors = doors_by_level.get(level, [])
        for door in current_doors:
            if game_settings["use_custom_models"] and "door" in item_sprites:
                screen.blit(item_sprites["door"], door["rect"])
            else:
                pygame.draw.rect(screen, DOOR_COLOR, door["rect"])

            # Cost text with background
            # Position cost text relative to the door
            cost_x = door["rect"].x + door["rect"].width // 2 - 35
            cost_y = door["rect"].y - 25
            cost_bg = pygame.Rect(cost_x, cost_y, 70, 20)
            pygame.draw.rect(screen, (50, 50, 50), cost_bg, border_radius=3)
            cost_text = small_font.render(f"Cost: {door['cost']}", True, TEXT_COLOR)
            screen.blit(cost_text, (cost_x + 5, cost_y + 2)) # Adjust text position inside bg


        current_windows = windows_by_level.get(level, [])
        for window in current_windows:
            if game_settings["use_custom_models"] and "window" in item_sprites:
                screen.blit(item_sprites["window"], window["rect"])
            else:
                pygame.draw.rect(screen, WINDOW_COLOR, window["rect"])

            # Cost text with background
            cost_x = window["rect"].x + window["rect"].width // 2 - 35
            cost_y = window["rect"].y - 25
            cost_bg = pygame.Rect(cost_x, cost_y, 70, 20)
            pygame.draw.rect(screen, (50, 50, 50), cost_bg, border_radius=3)
            cost_text = small_font.render(f"Cost: {window['cost']}", True, TEXT_COLOR)
            screen.blit(cost_text, (cost_x + 5, cost_y + 2)) # Adjust text position inside bg

        # Draw the return button if not in level 0 or boss level
        if level > 0 and level != 3:
            pygame.draw.rect(screen, BACK_RECT_COLOR, back_rect)
            # Return text with background
            back_bg = pygame.Rect(back_rect.x - 5, back_rect.y - 25, 110, 20)
            pygame.draw.rect(screen, (50, 50, 50), back_bg, border_radius=3)
            back_text = small_font.render("Return (Enter)", True, TEXT_COLOR)
            screen.blit(back_text, (back_rect.x, back_rect.y - 20))


        # Draw coins for current level (only in PLAYING state, not BOSS_FIGHT)
        if game_state == PLAYING:
            for coin in coins:
                if coin["level"] == level and not coin["collected"]:
                    if game_settings["use_custom_models"] and "coin" in item_sprites:
                        screen.blit(item_sprites["coin"], coin["rect"])
                    else:
                        pygame.draw.ellipse(screen, COIN_COLOR, coin["rect"])

        # Draw enemies (helper ghosts in boss level, regular enemies elsewhere)
        for enemy in enemies:
            enemy.draw(screen) # Enemy draw method checks if it's on the current level and alive

        # Draw boss (only in BOSS_FIGHT state)
        if game_state == BOSS_FIGHT and boss and boss.is_alive:
            boss.draw(screen) # Boss draw method includes its health bar and attack visuals

        # Draw player (with flash effect if recently hit)
        # The immunity time prevents player from taking damage *during* the flash, not just the flash itself.
        is_flashing = (current_time - last_hit_time < immunity_time) and ((current_time // 100) % 2 == 0)

        if not is_flashing:
            if game_settings["use_custom_models"] and player_sprites:
                # Choose sprite based on direction
                sprite_key = {0:"right", 1:"down", 2:"left", 3:"up"}.get(player_direction, "right") # Default to right
                screen.blit(player_sprites.get(sprite_key, player_sprites["right"]), player) # Use default if sprite key missing
            else:
                 pygame.draw.rect(screen, PLAYER_COLOR, player)
        else:
             # Draw player when flashing
             if game_settings["use_custom_models"] and player_sprites:
                sprite_key = {0:"right", 1:"down", 2:"left", 3:"up"}.get(player_direction, "right") # Default to right
                # Maybe draw semi-transparent or a different color?
                # For simplicity, just draw the sprite normally if flashing
                screen.blit(player_sprites.get(sprite_key, player_sprites["right"]), player)
             else:
                 pygame.draw.rect(screen, (255, 100, 100), player) # Draw a lighter red rect when flashing


        # Flashlight Effect
        draw_flashlight() # Draw flashlight effect on top of everything except UI


        # Display interaction text on top of flashlight
        if display_text and interaction_target:
            # Need to adjust position/size based on text content
            text_content = ""
            is_cost_warning = False

            if interaction_target.get("type") in ["door", "window"]:
                 # Check if it's the boss door and the coin requirement is not met
                 if interaction_target.get("is_boss_door") and player_coins < interaction_target["cost"]:
                      text_content = f"Need {interaction_target['cost']} coins (you have {player_coins}) to unlock the Boss Arena"
                      is_cost_warning = True
                 elif player_coins >= interaction_target["cost"]:
                     text_content = f"Enter {interaction_target['type']} to Level {interaction_target['target']} (Cost: {interaction_target['cost']} coins - Press Enter)"
                 else:
                     text_content = f"Need {interaction_target['cost']} coins (you have {player_coins})"
                     is_cost_warning = True
            elif interaction_target.get("type") == "Back to Level 0":
                 text_content = "Return to Level 0 (Press Enter)"

            if text_content:
                # Calculate text size and background size
                text_surface = font.render(text_content, True, TEXT_COLOR if not is_cost_warning else (255, 100, 100))
                text_rect = text_surface.get_rect(center=(WIDTH // 2, 35)) # Center text near top

                text_bg_padding = 20
                text_bg = pygame.Rect(text_rect.left - text_bg_padding // 2, text_rect.top - text_bg_padding // 2,
                                      text_rect.width + text_bg_padding, text_rect.height + text_bg_padding)

                pygame.draw.rect(screen, (50, 50, 50, 200), text_bg, border_radius=5)
                screen.blit(text_surface, text_rect)


        # Draw UI elements on top of flashlight and interaction text
        draw_ui_elements()


    # Update the display
    pygame.display.flip()

# Game loop finishes when running is False
stop_music() # Stop any music before quitting
pygame.quit()
sys.exit()