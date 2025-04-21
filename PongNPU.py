import pygame
import random
import sys
import numpy as np # Meow! We need numpy to make sound waves!
import math # For sine waves, purr!

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
BG_COLOR = (0, 0, 0) # Black like a night sky, purr!
PADDLE_COLOR = (255, 255, 255) # White like fluffy clouds!
BALL_COLOR = (255, 255, 255) # Also white, like a little snowball!
TEXT_COLOR = (255, 255, 255) # White text, easy to see!
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 15
PADDLE_SPEED = 7 # How fast the paddles zip!
BALL_SPEED_X = 5 # How fast the ball zooms sideways!
BALL_SPEED_Y = 5 # How fast the ball zooms up/down!
WINNING_SCORE = 5 # First to 5 points wins, nya!

# --- Game States ---
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"

# --- Initialize Pygame ---
pygame.mixer.pre_init(44100, -16, 1, 512) # Initialize mixer first with good settings! Nya!
pygame.init()
pygame.font.init() # Need this for scores and text, teehee!
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cute Pong! Beep Boop!")
clock = pygame.time.Clock()

# --- Fonts ---
title_font = pygame.font.Font(None, 100) # Big title font!
score_font = pygame.font.Font(None, 74) # Big clear numbers!
menu_font = pygame.font.Font(None, 36) # Font for menu and game over text
game_over_font = pygame.font.Font(None, 80) # Font for "GAME OVER"
copyright_font = pygame.font.Font(None, 24) # Smaller font for copyright

# --- Sound Generation (Beep Boop Time!) ---
SAMPLE_RATE = 44100
DURATION_SHORT = 0.05 # Short beep duration in seconds
DURATION_MEDIUM = 0.1 # Medium beep duration

def generate_sine_wave(frequency, duration, amplitude=4096):
    """Generates a numpy array for a sine wave sound."""
    num_samples = int(SAMPLE_RATE * duration)
    buf = np.zeros((num_samples,), dtype=np.int16) # 16-bit sound
    max_sample = 2**(16 - 1) - 1 # Max value for 16-bit audio

    for i in range(num_samples):
        t = float(i) / SAMPLE_RATE # Time in seconds
        buf[i] = int(np.clip(amplitude * np.sin(2 * np.pi * frequency * t), -max_sample, max_sample))
    return buf

# Create Sound objects from generated waves
# Frequency in Hz (Higher number = higher pitch)
beep_wall = pygame.mixer.Sound(buffer=generate_sine_wave(440.0, DURATION_SHORT)) # A note (middle C-ish)
beep_score = pygame.mixer.Sound(buffer=generate_sine_wave(880.0, DURATION_MEDIUM)) # Higher pitch for score!
beep_paddle = pygame.mixer.Sound(buffer=generate_sine_wave(220.0, DURATION_SHORT)) # Lower pitch for paddle

# --- Game Objects (Rectangles are easy!) ---
# Player 1 (Left Paddle)
player1_paddle = pygame.Rect(
    30, # X position (near left edge)
    SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, # Y position (centered)
    PADDLE_WIDTH,
    PADDLE_HEIGHT
)

# Player 2 (Right Paddle)
player2_paddle = pygame.Rect(
    SCREEN_WIDTH - 30 - PADDLE_WIDTH, # X position (near right edge)
    SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, # Y position (centered)
    PADDLE_WIDTH,
    PADDLE_HEIGHT
)

# Ball
ball = pygame.Rect(
    SCREEN_WIDTH // 2 - BALL_SIZE // 2, # X position (center)
    SCREEN_HEIGHT // 2 - BALL_SIZE // 2, # Y position (center)
    BALL_SIZE,
    BALL_SIZE
)

# --- Game Variables ---
ball_speed_x_current = BALL_SPEED_X * random.choice((1, -1)) # Start direction random!
ball_speed_y_current = BALL_SPEED_Y * random.choice((1, -1)) # Start direction random!
player1_score = 0
player2_score = 0
game_state = MENU # Start in the menu state
winner_text = ""

# --- Function to reset game state for playing ---
def start_game():
    global player1_score, player2_score, game_state, winner_text
    player1_score = 0
    player2_score = 0
    winner_text = ""
    # Center paddles vertically
    player1_paddle.centery = SCREEN_HEIGHT // 2
    player2_paddle.centery = SCREEN_HEIGHT // 2
    reset_ball(True) # Reset ball without delay
    game_state = PLAYING

# --- Function to reset ball ---
def reset_ball(immediate=False):
    global ball_speed_x_current, ball_speed_y_current
    ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    # Pause briefly before starting again, meow! unless immediate reset
    if not immediate:
        pygame.time.wait(500)
    ball_speed_y_current = BALL_SPEED_Y * random.choice((1, -1))
    ball_speed_x_current = BALL_SPEED_X * random.choice((1, -1))

# --- Drawing Functions ---
def draw_menu():
    screen.fill(BG_COLOR)
    # Title "PONG 10"
    title_surface = title_font.render("PONG", True, TEXT_COLOR)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
    screen.blit(title_surface, title_rect)

    ten_surface = score_font.render("10", True, TEXT_COLOR) # Using score font for "10"
    ten_rect = ten_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10)) # Positioned below PONG
    screen.blit(ten_surface, ten_rect)

    # Start instruction
    start_surface = menu_font.render("Press SPACE to start game", True, TEXT_COLOR)
    start_rect = start_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
    screen.blit(start_surface, start_rect)

    # Copyright
    copyright_surface = copyright_font.render("copyright [@Team Flames HDR] 1.0", True, TEXT_COLOR)
    copyright_rect = copyright_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20)) # Bottom center
    screen.blit(copyright_surface, copyright_rect)

def draw_game():
    screen.fill(BG_COLOR) # Fill the background first!
    # Draw Paddles
    pygame.draw.rect(screen, PADDLE_COLOR, player1_paddle)
    pygame.draw.rect(screen, PADDLE_COLOR, player2_paddle)
    # Draw Ball
    pygame.draw.ellipse(screen, BALL_COLOR, ball) # Ellipse looks more ball-like!
    # Draw Center Line (optional aesthetic)
    pygame.draw.aaline(screen, PADDLE_COLOR, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))
    # Draw Scores
    player1_text = score_font.render(str(player1_score), True, PADDLE_COLOR)
    screen.blit(player1_text, (SCREEN_WIDTH // 4, 20))
    player2_text = score_font.render(str(player2_score), True, PADDLE_COLOR)
    screen.blit(player2_text, (SCREEN_WIDTH * 3 // 4 - player2_text.get_width() // 2 , 20)) # Adjust position slightly

def draw_game_over():
    screen.fill(BG_COLOR)
    # Display "GAME OVER"
    game_over_surface = game_over_font.render("GAME OVER", True, TEXT_COLOR)
    game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(game_over_surface, game_over_rect)

    # Display winner text
    win_surface = menu_font.render(winner_text, True, PADDLE_COLOR) # Using menu font now
    win_rect = win_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(win_surface, win_rect)

    # Display instruction text
    restart_surface = menu_font.render("Restart? (Y/N)", True, PADDLE_COLOR)
    restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(restart_surface, restart_rect)

    # Copyright (optional, keep it consistent?)
    copyright_surface = copyright_font.render("copyright [@Team Flames HDR] 1.0", True, TEXT_COLOR)
    copyright_rect = copyright_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20)) # Bottom center
    screen.blit(copyright_surface, copyright_rect)


# --- Game Loop ---
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == MENU:
                if event.key == pygame.K_SPACE:
                    start_game() # Start the game from menu
            elif game_state == GAME_OVER:
                if event.key == pygame.K_y: # Yes to restart
                    start_game() # Restart the game
                elif event.key == pygame.K_n: # No to restart
                    running = False # Quit the program

    # --- Game Logic based on State ---
    if game_state == PLAYING:
        # --- Player Input ---
        keys = pygame.key.get_pressed()
        # Player 1 (W and S)
        if keys[pygame.K_w] and player1_paddle.top > 0:
            player1_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_s] and player1_paddle.bottom < SCREEN_HEIGHT:
            player1_paddle.y += PADDLE_SPEED
        # Player 2 (Up and Down Arrows)
        if keys[pygame.K_UP] and player2_paddle.top > 0:
            player2_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] and player2_paddle.bottom < SCREEN_HEIGHT:
            player2_paddle.y += PADDLE_SPEED

        # --- Ball Movement ---
        ball.x += ball_speed_x_current
        ball.y += ball_speed_y_current

        # --- Ball Collision ---
        # Top/Bottom Walls
        if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
            ball_speed_y_current *= -1 # Bounce! Boing!
            # Keep ball in bounds slightly to prevent sticking
            if ball.top < 0:
                ball.top = 0
            if ball.bottom > SCREEN_HEIGHT:
                ball.bottom = SCREEN_HEIGHT
            beep_wall.play() # Play wall bounce beep!

        # Left/Right Walls (Scoring)
        if ball.left <= 0:
            player2_score += 1
            beep_score.play() # Play score beep!
            if player2_score >= WINNING_SCORE:
                winner_text = "Player 2 Wins! Purrrrfect!"
                game_state = GAME_OVER # Change state to game over
            else:
                reset_ball()
        if ball.right >= SCREEN_WIDTH:
            player1_score += 1
            beep_score.play() # Play score beep!
            if player1_score >= WINNING_SCORE:
                winner_text = "Player 1 Wins! Meow-tastic!"
                game_state = GAME_OVER # Change state to game over
            else:
                reset_ball()

        # Paddles
        if ball.colliderect(player1_paddle) or ball.colliderect(player2_paddle):
            # Prevent ball getting stuck inside paddle slightly
            if ball.colliderect(player1_paddle):
                 # Check if ball center is within paddle bounds vertically
                if player1_paddle.top < ball.centery < player1_paddle.bottom:
                    ball.left = player1_paddle.right # Move ball outside
                    ball_speed_x_current *= -1 # Bounce off paddle!
                    beep_paddle.play() # Play paddle hit beep!
                # Handle edge case where ball hits corner slightly outside vertical bounds
                elif ball.left < player1_paddle.right and ball_speed_x_current < 0:
                    ball.left = player1_paddle.right # Push out
                    ball_speed_x_current *= -1
                    beep_paddle.play()

            elif ball.colliderect(player2_paddle):
                 # Check if ball center is within paddle bounds vertically
                if player2_paddle.top < ball.centery < player2_paddle.bottom:
                    ball.right = player2_paddle.left # Move ball outside
                    ball_speed_x_current *= -1 # Bounce off paddle!
                    beep_paddle.play() # Play paddle hit beep!
                # Handle edge case
                elif ball.right > player2_paddle.left and ball_speed_x_current > 0:
                     ball.right = player2_paddle.left # Push out
                     ball_speed_x_current *= -1
                     beep_paddle.play()

    # --- Drawing based on State ---
    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        draw_game()
    elif game_state == GAME_OVER:
        draw_game_over()

    # --- Update Display ---
    pygame.display.flip() # Show the new frame! Nya!

    # --- Frame Rate ---
    clock.tick(60) # Keep it running smoothly at 60 FPS, like a graceful kitty!

# --- Quit Pygame ---
pygame.quit()
sys.exit() # Clean exit! Bye-bye!
