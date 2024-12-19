import pygame
import random
import math

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BRICK_COLOR = (200, 100, 100)

# Player properties
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 32
PLAYER_SPEED = 5
JUMP_FORCE = -15
GRAVITY = 0.8

# Mode 7 Constants
BACKGROUND_ROTATION_SPEED = 0.05
BACKGROUND_MIN_SCALE = 0.5
BACKGROUND_MAX_SCALE = 1.2

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False

    def update(self):
        self.velocity_y += GRAVITY
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        if self.rect.bottom > SCREEN_HEIGHT - TILE_SIZE:
            self.rect.bottom = SCREEN_HEIGHT - TILE_SIZE
            self.velocity_y = 0
            self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_FORCE
            self.on_ground = False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = random.choice([-2, 2])

    def update(self):
        self.rect.x += self.velocity_x

        if self.rect.right > SCREEN_WIDTH:
            self.velocity_x = -2
        elif self.rect.left < 0:
            self.velocity_x = 2

def draw_castle(screen):
    castle_width = 200
    castle_height = 300
    castle_x = (SCREEN_WIDTH - castle_width) // 2
    castle_y = SCREEN_HEIGHT - TILE_SIZE - castle_height

    # Draw castle body
    pygame.draw.rect(screen, BRICK_COLOR, (castle_x, castle_y, castle_width, castle_height))

    # Draw castle windows
    window_width = 30
    window_height = 40
    window_y = castle_y + 50
    for i in range(3):
        window_x = castle_x + (castle_width - window_width) // 2
        pygame.draw.rect(screen, BLACK, (window_x, window_y + i * 80, window_width, window_height))

    # Draw castle door
    door_width = 60
    door_height = 100
    door_x = castle_x + (castle_width - door_width) // 2
    door_y = castle_y + castle_height - door_height
    pygame.draw.rect(screen, BLACK, (door_x, door_y, door_width, door_height))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario FX")
        self.clock = pygame.time.Clock()
        self.running = True

        self.mario = Player(100, SCREEN_HEIGHT - TILE_SIZE * 2, RED)
        self.luigi = Player(200, SCREEN_HEIGHT - TILE_SIZE * 2, GREEN)

        self.enemies = pygame.sprite.Group()
        self.enemies.add(Enemy(400, SCREEN_HEIGHT - TILE_SIZE, BLUE))
        self.enemies.add(Enemy(600, SCREEN_HEIGHT - TILE_SIZE, BLUE))

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.mario)
        self.all_sprites.add(self.luigi)
        self.all_sprites.add(self.enemies)

        self.background_angle = 0
        self.background_scale = 1.0
        self.background_scale_speed = 0.01  # Initialize instance variable

    def show_menu(self):
        menu_font = pygame.font.Font(None, 50)
        instructions_font = pygame.font.Font(None, 30)

        title_text = menu_font.render("Super Mario FX", True, WHITE)
        play_text = menu_font.render("Press ENTER to Play", True, WHITE)
        exit_text = menu_font.render("Press ESC to Quit", True, WHITE)
        controls_text = instructions_font.render("Controls: WASD for Luigi, Arrow Keys for Mario, Space to Jump", True, WHITE)

        while True:
            self.screen.fill(BLACK)
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
            self.screen.blit(play_text, (SCREEN_WIDTH // 2 - play_text.get_width() // 2, 200))
            self.screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, 300))
            self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, 400))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()

    def handle_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.mario.velocity_x = -PLAYER_SPEED
        elif keys[pygame.K_RIGHT]:
            self.mario.velocity_x = PLAYER_SPEED
        else:
            self.mario.velocity_x = 0

        if keys[pygame.K_a]:
            self.luigi.velocity_x = -PLAYER_SPEED
        elif keys[pygame.K_d]:
            self.luigi.velocity_x = PLAYER_SPEED
        else:
            self.luigi.velocity_x = 0

        if keys[pygame.K_SPACE]:
            self.mario.jump()
        if keys[pygame.K_w]:
            self.luigi.jump()

    def update(self):
        self.all_sprites.update()

    def draw(self):
        # Apply Mode 7-like background effect (rotation + scaling)
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill(WHITE)

        # Rotate and scale the background
        self.background_angle += BACKGROUND_ROTATION_SPEED
        self.background_scale += self.background_scale_speed
        if self.background_scale > BACKGROUND_MAX_SCALE or self.background_scale < BACKGROUND_MIN_SCALE:
            self.background_scale_speed *= -1  # Reverse the scaling direction

        # Rotate and scale the background
        rotated_background = pygame.transform.rotate(background, self.background_angle)
        scaled_width = int(SCREEN_WIDTH * self.background_scale)
        scaled_height = int(SCREEN_HEIGHT * self.background_scale)
        scaled_background = pygame.transform.scale(rotated_background, (scaled_width, scaled_height))

        # Center the scaled background
        bg_x = (SCREEN_WIDTH - scaled_width) // 2
        bg_y = (SCREEN_HEIGHT - scaled_height) // 2

        # Draw background and castle
        self.screen.fill(BLACK)
        self.screen.blit(scaled_background, (bg_x, bg_y))

        # Draw ground (bottom green area)
        pygame.draw.rect(self.screen, GREEN, (0, SCREEN_HEIGHT - TILE_SIZE, SCREEN_WIDTH, TILE_SIZE))

        # Draw castle
        draw_castle(self.screen)

        # Draw all sprites
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def run(self):
        self.show_menu()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
