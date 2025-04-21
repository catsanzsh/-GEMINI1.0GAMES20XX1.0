# Sonic4k.py - Meow! A cute Sonic CD starter, now with pure code graphics!
import pygame
import os
import sys
import random # Nya, let's add some random stars!
import math # For spikes, meow!

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
WHITE = (255, 255, 255)
# Player Colors - Let's make Sonic! Purrr...
SONIC_BLUE = (0, 0, 200) 
SONIC_SKIN = (255, 211, 155) # A peachy color, nya!
SONIC_RED = (200, 0, 0)
BLACK = (0, 0, 0)
# Background Colors
SKY_BLUE = (135, 206, 235) # A nice sky color!
GREEN = (0, 180, 0) # Ground color!
YELLOW = (255, 255, 0) # Star color!
TRANSPARENT_BG = (1, 1, 1) # A nearly black color for transparency key

GRAVITY = 0.5 # Gotta come down sometime! Purrrr... 
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12 # A little slippery! 
PLAYER_JUMP = -10 # Wee!
# Adjust player size for drawing
PLAYER_WIDTH = 40 
PLAYER_HEIGHT = 50 # Slightly taller to fit spikes, maybe?
GROUND_HEIGHT = 50

# --- Helper Function for Background ---
def create_background(width, height):
    """Creates a simple sky and ground background, purrr."""
    background = pygame.Surface((width, height))
    background.fill(SKY_BLUE) # Fill the sky
    # Draw the ground rectangle
    pygame.draw.rect(background, GREEN, (0, height - GROUND_HEIGHT, width, GROUND_HEIGHT)) 
    # Draw some stars, nya!
    for _ in range(50): # 50 stars!
        x = random.randint(0, width)
        y = random.randint(0, height - GROUND_HEIGHT) # Only in the sky part
        size = random.randint(1, 3)
        pygame.draw.circle(background, YELLOW, (x, y), size)
    return background

# --- Player Class ---
# Using Pygame Sprites makes things easier, purrrr! 
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        # Create the player surface with code, meow! Make it transparent!
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT)).convert()
        self.image.fill(TRANSPARENT_BG) # Fill with transparent background color
        self.image.set_colorkey(TRANSPARENT_BG) # Make this color transparent

        # --- Draw Sonic with Shapes! Nya! ---
        center_x = PLAYER_WIDTH // 2
        body_bottom = PLAYER_HEIGHT - 10 # Leave space for feet

        # Body (Blue ellipse)
        body_rect = pygame.Rect(center_x - 12, 5, 24, 30)
        pygame.draw.ellipse(self.image, SONIC_BLUE, body_rect)

        # Belly (Skin ellipse)
        belly_rect = pygame.Rect(center_x - 7, 15, 14, 18)
        pygame.draw.ellipse(self.image, SONIC_SKIN, belly_rect)
        
        # Muzzle (Skin circle/ellipse) - drawn slightly lower and forward
        muzzle_rect = pygame.Rect(center_x - 2, body_bottom - 20, 14, 10) 
        pygame.draw.ellipse(self.image, SONIC_SKIN, muzzle_rect)
        
        # Nose (Small black circle)
        nose_pos = (muzzle_rect.centerx + 5 , muzzle_rect.centery)
        pygame.draw.circle(self.image, BLACK, nose_pos, 2)

        # Eyes (White ovals with black dots) - Basic version
        eye_y = body_rect.centery - 5
        pygame.draw.ellipse(self.image, WHITE, (center_x - 7, eye_y -3 , 6, 8))
        pygame.draw.ellipse(self.image, WHITE, (center_x + 1, eye_y - 3, 6, 8))
        pygame.draw.circle(self.image, BLACK, (center_x - 4, eye_y + 1), 1) # Pupils
        pygame.draw.circle(self.image, BLACK, (center_x + 4, eye_y + 1), 1)

        # Spikes (Blue triangles) - Simplified! Nya!
        spike_base_y = body_rect.centery
        # Spike 1 (Top)
        pygame.draw.polygon(self.image, SONIC_BLUE, [(center_x - 12, spike_base_y - 5), (center_x - 20, spike_base_y - 15), (center_x - 10, spike_base_y)])
        # Spike 2 (Middle)
        pygame.draw.polygon(self.image, SONIC_BLUE, [(center_x - 14, spike_base_y + 5), (center_x - 25, spike_base_y + 5), (center_x - 12, spike_base_y + 12)])
        # Spike 3 (Lower)
        pygame.draw.polygon(self.image, SONIC_BLUE, [(center_x - 12, spike_base_y + 15), (center_x - 20, spike_base_y + 25), (center_x - 10, spike_base_y + 18)])

        # Feet/Shoes (Red ovals with white stripe) - Simple!
        shoe_y = body_bottom + 2
        # Left Shoe
        pygame.draw.ellipse(self.image, SONIC_RED, (center_x - 13, shoe_y, 12, 8))
        pygame.draw.rect(self.image, WHITE, (center_x - 12, shoe_y + 1, 10, 3)) # Stripe
        # Right Shoe
        pygame.draw.ellipse(self.image, SONIC_RED, (center_x + 1, shoe_y, 12, 8))
        pygame.draw.rect(self.image, WHITE, (center_x + 2, shoe_y + 1, 10, 3)) # Stripe
        # --- End Drawing Sonic ---

        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH / 2
        self.rect.bottom = SCREEN_HEIGHT - GROUND_HEIGHT # Start on the ground
        self.pos = pygame.math.Vector2(self.rect.centerx, self.rect.bottom)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)

    def jump(self):
        # Only jump if standing on the ground, nya!
        if self.rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT:
             self.vel.y = PLAYER_JUMP 

    def update(self):
        # Reset acceleration each frame
        self.acc = pygame.math.Vector2(0, GRAVITY) # Gravity always pulls down! 
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pygame.K_RIGHT]:
            self.acc.x = PLAYER_ACC
            
        # Apply friction, meow! 
        self.acc.x += self.vel.x * PLAYER_FRICTION
        
        # Equations of motion, purrrfect physics! 
        self.vel += self.acc
        # Limit max fall speed, nya!
        if self.vel.y > 15:
            self.vel.y = 15
        self.pos += self.vel + 0.5 * self.acc
        
        # Keep Player on screen (simple boundary check)
        # Adjust bounds for the new player width
        if self.pos.x > SCREEN_WIDTH - self.rect.width / 2:
            self.pos.x = SCREEN_WIDTH - self.rect.width / 2
            self.vel.x = 0 # Stop at edge
        if self.pos.x < self.rect.width / 2:
            self.pos.x = self.rect.width / 2
            self.vel.x = 0 # Stop at edge
            
        # Simple ground check - stop exactly at ground level
        if self.pos.y > SCREEN_HEIGHT - GROUND_HEIGHT:
             self.pos.y = SCREEN_HEIGHT - GROUND_HEIGHT
             self.vel.y = 0 # Stop falling at the bottom
             
        # Update rect position using midbottom for better ground alignment
        self.rect.midbottom = (round(self.pos.x), round(self.pos.y)) 

# --- Game Initialization ---
pygame.init()
# pygame.mixer.init() # Still commented out, meow! 
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Meow! Sonic CD Code Shapes!")
clock = pygame.time.Clock()

# --- Create Assets with Code ---
background_surface = create_background(SCREEN_WIDTH, SCREEN_HEIGHT)

# --- Sprites ---
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

# --- Game Loop ---
running = True
while running:
    # Keep loop running at the right speed, purrrr!
    clock.tick(60) # Aim for 60 FPS
    
    # Process Input (Events)
    for event in pygame.event.get():
        # Check for closing window
        if event.type == pygame.QUIT:
            running = False
        # Check for key presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP: # Jump keys!
                player.jump()

    # Update
    all_sprites.update() # Calls the update() method of all sprites (our player!)

    # Draw / Render
    screen.blit(background_surface, (0,0)) # Draw the background surface first! 
        
    all_sprites.draw(screen) # Pygame draws all sprites in the group, nya!
    
    # *after* drawing everything, flip the display
    pygame.display.flip() # Shows the new frame! 

# --- Done ---
pygame.quit()
sys.exit() # Ensures the program closes cleanly, purr!
