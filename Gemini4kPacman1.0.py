# test.py
import pygame
import sys
import random
import math

# === Configuration ===
TILE_SIZE = 24 # Slightly smaller tiles often work well for Pac-Man layouts
MAZE_W_TILES = 28
MAZE_H_TILES = 31 # Classic Pac-Man dimensions (approx)
SCREEN_WIDTH = MAZE_W_TILES * TILE_SIZE
SCREEN_HEIGHT = (MAZE_H_TILES + 3) * TILE_SIZE # Extra space for score/lives

FPS = 60
PLAYER_SPEED = TILE_SIZE * 3.0 / FPS # Adjusted speed in pixels per frame
GHOST_SPEED = TILE_SIZE * 2.8 / FPS
GHOST_FRIGHT_SPEED = TILE_SIZE * 1.5 / FPS

# Colors
COLOR_BG       = (0,   0,  0)
COLOR_WALL     = (33,  33, 255) # Blue
COLOR_TUNNEL   = (50, 50, 50) # Dark grey for tunnel background indication
COLOR_PELLET   = (255, 255, 0) # Yellowish white
COLOR_PLAYER   = (255, 255, 0) # Yellow
COLOR_GHOSTS   = [(255, 0, 0), (255, 184, 255), (0, 255, 255), (255, 184, 82)] # Red, Pink, Cyan, Orange
COLOR_WHITE    = (255, 255, 255)

# Maze Layout (Simplified Pac-Man Style Example)
# 0: Empty Path, 1: Wall, 2: Pellet, 5: Tunnel
# More complex layout would be needed for a true clone
MAZE_LAYOUT = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,1,1,1,1,1],
    [0,0,0,0,0,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,0,0,0,0,0], # Row with potential ghost house area (simplified)
    [1,1,1,1,1,1,2,1,1,0,1,1,1,0,0,1,1,1,0,1,1,2,1,1,1,1,1,1],
    [5,0,0,0,0,0,2,0,0,0,1,0,0,0,0,0,0,1,0,0,0,2,0,0,0,0,0,5], # Tunnel Row
    [1,1,1,1,1,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,1,1,1,1,1],
    [0,0,0,0,0,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,0,0,0,0,0],
    [1,1,1,1,1,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,2,2,2,1,1,2,2,2,2,2,2,2,0,0,2,2,2,2,2,2,2,1,1,2,2,2,1],
    [1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1],
    [1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]
# Add empty rows to reach MAZE_H_TILES for display consistency if needed
while len(MAZE_LAYOUT) < MAZE_H_TILES:
    MAZE_LAYOUT.append([1]*MAZE_W_TILES) # Fill bottom with walls

# --- Helper Functions ---
def pixel_to_maze(px, py):
    """Convert pixel coords to maze cell indices."""
    col = int(px // TILE_SIZE)
    row = int(py // TILE_SIZE)
    # Clamp values to be within maze bounds
    col = max(0, min(col, MAZE_W_TILES - 1))
    row = max(0, min(row, MAZE_H_TILES - 1))
    return col, row

def maze_to_pixel_center(mx, my):
    """Gets the center pixel coordinates of a maze tile."""
    return mx * TILE_SIZE + TILE_SIZE // 2, my * TILE_SIZE + TILE_SIZE // 2

def is_wall(mx, my):
    """Checks if a maze coordinate is a wall."""
    if 0 <= my < MAZE_H_TILES and 0 <= mx < MAZE_W_TILES:
        return MAZE_LAYOUT[my][mx] == 1
    return True # Treat out-of-bounds as walls

def get_valid_moves(mx, my):
    """Returns a list of valid (non-wall) neighbor coordinates (mx, my)."""
    moves = []
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Up, Down, Left, Right
        next_mx, next_my = mx + dx, my + dy
        if 0 <= next_my < MAZE_H_TILES and 0 <= next_mx < MAZE_W_TILES:
             # Allow movement into tunnels (5) and paths (0, 2)
             if MAZE_LAYOUT[next_my][next_mx] != 1:
                moves.append((next_mx, next_my))
    return moves

# --- Pellet Management ---
pellet_positions = set() # Use a set for efficient checking and removal
def initialize_pellets():
    pellet_positions.clear()
    for r in range(MAZE_H_TILES):
        for c in range(MAZE_W_TILES):
            if MAZE_LAYOUT[r][c] == 2:
                pellet_positions.add((c, r))

# --- Base Entity Class ---
class Entity:
    def __init__(self, mx, my, radius, speed, color):
        self.start_mx, self.start_my = mx, my
        self.px, self.py = maze_to_pixel_center(mx, my)
        self.radius = radius
        self.speed = speed
        self.color = color
        self.dx = 0 # velocity in pixels per frame
        self.dy = 0
        self.current_mx, self.current_my = mx, my

    def update_maze_pos(self):
        self.current_mx, self.current_my = pixel_to_maze(self.px, self.py)

    def move_and_collide(self):
        """Handles movement, wall collision, and tunnel wrapping."""
        # --- X-Axis Movement and Collision ---
        self.px += self.dx
        sign_x = 1 if self.dx > 0 else -1 if self.dx < 0 else 0
        if sign_x != 0:
            # Check collision using corners in the direction of movement
            check_x_edge = self.px + sign_x * self.radius
            for y_offset in [-self.radius * 0.9, self.radius * 0.9]: # Check near top/bottom edges
                collided_mx, collided_my = pixel_to_maze(check_x_edge, self.py + y_offset)
                if is_wall(collided_mx, collided_my):
                    # Collision detected! Snap back to the wall edge
                    if sign_x > 0: # Moving right
                        self.px = collided_mx * TILE_SIZE - self.radius - 0.01 # Place just left of wall
                    else: # Moving left
                        self.px = (collided_mx + 1) * TILE_SIZE + self.radius + 0.01 # Place just right of wall
                    self.dx = 0 # Stop horizontal movement
                    break # Stop checking after first collision on this axis

        # --- Y-Axis Movement and Collision ---
        self.py += self.dy
        sign_y = 1 if self.dy > 0 else -1 if self.dy < 0 else 0
        if sign_y != 0:
            # Check collision using corners in the direction of movement
            check_y_edge = self.py + sign_y * self.radius
            for x_offset in [-self.radius * 0.9, self.radius * 0.9]: # Check near left/right edges
                collided_mx, collided_my = pixel_to_maze(self.px + x_offset, check_y_edge)
                if is_wall(collided_mx, collided_my):
                    # Collision detected! Snap back to the wall edge
                    if sign_y > 0: # Moving down
                        self.py = collided_my * TILE_SIZE - self.radius - 0.01 # Place just above wall
                    else: # Moving up
                        self.py = (collided_my + 1) * TILE_SIZE + self.radius + 0.01 # Place just below wall
                    self.dy = 0 # Stop vertical movement
                    break # Stop checking after first collision on this axis

        # --- Tunnel Wrapping ---
        self.update_maze_pos() # Get current tile after movement/collision checks
        if 0 <= self.current_my < MAZE_H_TILES and MAZE_LAYOUT[self.current_my][self.current_mx] == 5:
            if self.px < TILE_SIZE / 2: # Went off left edge
                self.px = (MAZE_W_TILES - 1) * TILE_SIZE - TILE_SIZE / 2 # Appear on right
            elif self.px > SCREEN_WIDTH - TILE_SIZE / 2: # Went off right edge
                self.px = TILE_SIZE / 2 # Appear on left

        self.update_maze_pos() # Update maze coords again after potential wrap

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.px), int(self.py)), int(self.radius))

# --- Player Class ---
class Player(Entity):
    def __init__(self, mx, my):
        super().__init__(mx, my, TILE_SIZE // 2 - 2, PLAYER_SPEED, COLOR_PLAYER)
        self.queued_dx = 0
        self.queued_dy = 0
        self.score = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        move_x = 0
        move_y = 0

        if keys[pygame.K_LEFT]: move_x = -1
        elif keys[pygame.K_RIGHT]: move_x = 1
        elif keys[pygame.K_UP]: move_y = -1
        elif keys[pygame.K_DOWN]: move_y = 1

        if move_x != 0 or move_y != 0:
            self.queued_dx = move_x * self.speed
            self.queued_dy = move_y * self.speed

    def update(self):
        # --- Try to apply queued direction if at center ---
        is_centered_x = abs(self.px - maze_to_pixel_center(self.current_mx, self.current_my)[0]) < self.speed * 0.5
        is_centered_y = abs(self.py - maze_to_pixel_center(self.current_mx, self.current_my)[1]) < self.speed * 0.5

        if self.queued_dx != 0 or self.queued_dy != 0:
            # Check if the turn is valid from the current tile center
            next_turn_mx = self.current_mx + (1 if self.queued_dx > 0 else -1 if self.queued_dx < 0 else 0)
            next_turn_my = self.current_my + (1 if self.queued_dy > 0 else -1 if self.queued_dy < 0 else 0)

            # Conditions to accept turn:
            # 1. Turning onto a different axis (e.g., was moving horizontally, turning vertically) AND centered on that axis.
            # 2. Or, reversing direction on the same axis.
            # 3. And the target tile is not a wall.
            can_turn = False
            if self.queued_dx != 0 and self.dx == 0 and is_centered_y: # Turning horizontal, currently vertical/stopped, centered Y
                 can_turn = True
            elif self.queued_dy != 0 and self.dy == 0 and is_centered_x: # Turning vertical, currently horizontal/stopped, centered X
                 can_turn = True
            elif (self.queued_dx != 0 and self.dx != 0 and self.queued_dx * self.dx < 0) or \
                 (self.queued_dy != 0 and self.dy != 0 and self.queued_dy * self.dy < 0): # Reversing direction
                 can_turn = True # Allow reversal anytime (classic behavior)


            if can_turn and not is_wall(next_turn_mx, next_turn_my):
                 # Snap to center and apply new direction
                 if self.dx == 0: # If was moving vertically or stopped, snap X
                     self.px = maze_to_pixel_center(self.current_mx, self.current_my)[0]
                 if self.dy == 0: # If was moving horizontally or stopped, snap Y
                     self.py = maze_to_pixel_center(self.current_mx, self.current_my)[1]

                 self.dx = self.queued_dx
                 self.dy = self.queued_dy
                 self.queued_dx = 0 # Clear queue
                 self.queued_dy = 0

        # --- Movement and Collision ---
        self.move_and_collide()

        # --- Pellet Collection ---
        if (self.current_mx, self.current_my) in pellet_positions:
            pellet_positions.remove((self.current_mx, self.current_my))
            self.score += 10
            # print(f"Score: {self.score}, Pellets left: {len(pellet_positions)}") # Debug


# --- Ghost Class ---
class Ghost(Entity):
    def __init__(self, mx, my, color):
        super().__init__(mx, my, TILE_SIZE // 2 - 2, GHOST_SPEED, color)
        self.direction_timer = 0 # Timer to decide new direction
        self.choose_new_direction() # Set initial direction

    def choose_new_direction(self):
        """Chooses a random valid direction, attempting not to reverse."""
        valid_tiles = get_valid_moves(self.current_mx, self.current_my)
        possible_moves = [] # (dx, dy) pairs

        current_dir_x = 1 if self.dx > 0 else -1 if self.dx < 0 else 0
        current_dir_y = 1 if self.dy > 0 else -1 if self.dy < 0 else 0

        for next_mx, next_my in valid_tiles:
            move_dir_x = next_mx - self.current_mx
            move_dir_y = next_my - self.current_my

            # Avoid reversing if possible (more than 1 option available)
            is_reverse = (move_dir_x == -current_dir_x and move_dir_y == -current_dir_y)
            if len(valid_tiles) > 1 and is_reverse:
                 continue

            possible_moves.append((move_dir_x * self.speed, move_dir_y * self.speed))

        if possible_moves:
            self.dx, self.dy = random.choice(possible_moves)
        else: # Dead end, must reverse or stop
            # Find the reversing move if it exists
            reversed_move = None
            for next_mx, next_my in valid_tiles:
                 move_dir_x = next_mx - self.current_mx
                 move_dir_y = next_my - self.current_my
                 if move_dir_x == -current_dir_x and move_dir_y == -current_dir_y:
                     reversed_move = (move_dir_x * self.speed, move_dir_y * self.speed)
                     break
            if reversed_move:
                 self.dx, self.dy = reversed_move
            else: # Completely stuck? Should not happen in standard maze
                self.dx, self.dy = 0, 0


        self.direction_timer = random.randint(15, 45) # Frames until next decision

    def update(self):
        # --- Decision Making at Center ---
        is_centered_x = abs(self.px - maze_to_pixel_center(self.current_mx, self.current_my)[0]) < self.speed * 0.5
        is_centered_y = abs(self.py - maze_to_pixel_center(self.current_mx, self.current_my)[1]) < self.speed * 0.5

        if is_centered_x and is_centered_y:
            # Snap to center
            self.px, self.py = maze_to_pixel_center(self.current_mx, self.current_my)
            # Decide new direction
            self.choose_new_direction()

        # --- Movement and Collision ---
        self.move_and_collide()


# --- Game Class ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man Zero Asset (Bandai Namco Style Test)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28) # Basic font
        self.game_over = False
        self.win = False
        self.start_game()

    def start_game(self):
        """Initializes or restarts the game state."""
        initialize_pellets()
        self.game_over = False
        self.win = False
        # Find a valid starting position for the player (first non-wall tile)
        player_start_mx, player_start_my = 1, 1 # Default
        for r in range(MAZE_H_TILES):
            for c in range(MAZE_W_TILES):
                 if MAZE_LAYOUT[r][c] != 1:
                     player_start_mx, player_start_my = c, r
                     break
            else: continue
            break
        self.player = Player(player_start_mx, player_start_my)

        # Find valid starting positions for ghosts (e.g., near center, non-wall)
        ghost_starts = [(13, 10), (14, 10), (13, 11), (14, 11)] # Example positions near center
        self.ghosts = []
        valid_ghost_starts_found = 0
        current_ghost_index = 0
        for r in range(MAZE_H_TILES):
            for c in range(MAZE_W_TILES):
                 if MAZE_LAYOUT[r][c] != 1 and (c,r) != (player_start_mx, player_start_my) and valid_ghost_starts_found < len(COLOR_GHOSTS):
                      # Use distinct starting points if possible
                      start_pos = (c,r)
                      # Quick check if too close to player start
                      if abs(c - player_start_mx) + abs(r - player_start_my) < 3: continue

                      self.ghosts.append(Ghost(start_pos[0], start_pos[1], COLOR_GHOSTS[current_ghost_index]))
                      valid_ghost_starts_found += 1
                      current_ghost_index += 1
                      if valid_ghost_starts_found == len(COLOR_GHOSTS): break # Stop once all ghosts are placed
            if valid_ghost_starts_found == len(COLOR_GHOSTS): break


    def draw_maze(self):
        # Draw Walls and Tunnels first
        for r in range(MAZE_H_TILES):
            for c in range(MAZE_W_TILES):
                cell = MAZE_LAYOUT[r][c]
                rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if cell == 1:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                elif cell == 5:
                    pygame.draw.rect(self.screen, COLOR_TUNNEL, rect) # Optional tunnel background

        # Draw Pellets
        pellet_radius = TILE_SIZE // 8
        for mx, my in pellet_positions:
            cx, cy = maze_to_pixel_center(mx, my)
            pygame.draw.circle(self.screen, COLOR_PELLET, (cx, cy), pellet_radius)

    def draw_ui(self):
        score_text = self.font.render(f"Score: {self.player.score}", True, COLOR_WHITE)
        text_rect = score_text.get_rect(topleft=(10, MAZE_H_TILES * TILE_SIZE + 10))
        self.screen.blit(score_text, text_rect)

        if self.game_over:
             end_text = self.font.render("GAME OVER! Press R to Restart", True, COLOR_GHOSTS[0])
             end_rect = end_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
             # Draw a semi-transparent background for better readability
             s = pygame.Surface((end_rect.width + 20, end_rect.height + 20), pygame.SRCALPHA)
             s.fill((0,0,0,180))
             self.screen.blit(s, (end_rect.left - 10, end_rect.top - 10))
             self.screen.blit(end_text, end_rect)

        if self.win:
             win_text = self.font.render("YOU WIN! Press R to Restart", True, COLOR_PLAYER)
             win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
             s = pygame.Surface((win_rect.width + 20, win_rect.height + 20), pygame.SRCALPHA)
             s.fill((0,0,0,180))
             self.screen.blit(s, (win_rect.left - 10, win_rect.top - 10))
             self.screen.blit(win_text, win_rect)

    def run(self):
        while True:
            # --- Event Handling ---
            for evt in pygame.event.get():
                if evt.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evt.type == pygame.KEYDOWN:
                    if (self.game_over or self.win) and evt.key == pygame.K_r:
                        self.start_game() # Restart the game

            # --- Input ---
            if not self.game_over and not self.win:
                self.player.handle_input()

            # --- Update ---
            if not self.game_over and not self.win:
                self.player.update()
                for g in self.ghosts:
                    g.update()

                # --- Check Collisions ---
                player_rect = pygame.Rect(self.player.px - self.player.radius, self.player.py - self.player.radius,
                                          self.player.radius * 2, self.player.radius * 2)
                for g in self.ghosts:
                    ghost_rect = pygame.Rect(g.px - g.radius, g.py - g.radius, g.radius * 2, g.radius * 2)
                    if player_rect.colliderect(ghost_rect):
                        self.game_over = True
                        # print("Game Over! Player collided with ghost.") # Debug
                        break # No need to check other ghosts

                # --- Check Win Condition ---
                if not pellet_positions:
                    self.win = True
                    # print("You win! All pellets collected.") # Debug

            # --- Render ---
            self.screen.fill(COLOR_BG)
            self.draw_maze()
            self.player.draw(self.screen)
            for g in self.ghosts:
                g.draw(self.screen)
            self.draw_ui() # Draw score and game over/win messages

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()
