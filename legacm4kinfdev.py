import pygame
import json

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40

# Animation states
IDLE = 'idle'
WALKING = 'walking'
JUMPING = 'jumping'

class SpriteSheet:
    def __init__(self, filename):
        self.sprite_sheet = pygame.image.load(filename).convert_alpha()
        
        # Sprite dimensions from the sheet
        self.SPRITE_WIDTH = 16
        self.SPRITE_HEIGHT = 32
        
        # Define sprite locations in the sheet
        self.sprite_locations = {
            'mario': {
                IDLE: [(0, 0, 16, 32)],
                WALKING: [(x * 16, 0, 16, 32) for x in range(3)],
                JUMPING: [(48, 0, 16, 32)]
            },
            'luigi': {
                IDLE: [(0, 32, 16, 32)],
                WALKING: [(x * 16, 32, 16, 32) for x in range(3)],
                JUMPING: [(48, 32, 16, 32)]
            },
            'goomba': {
                WALKING: [(x * 16, 64, 16, 16) for x in range(2)]
            },
            'koopa': {
                WALKING: [(x * 16, 80, 16, 24) for x in range(2)]
            }
        }

    def get_sprite(self, x, y, width, height):
        """Extract a single sprite from the sheet."""
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return sprite

    def get_animation_frames(self, character, state):
        """Get all frames for a character's animation state."""
        frames = []
        if character in self.sprite_locations and state in self.sprite_locations[character]:
            for rect in self.sprite_locations[character][state]:
                frames.append(self.get_sprite(*rect))
        return frames

class AnimatedSprite:
    def __init__(self, sprite_sheet, character, x, y, scale=2):
        self.x = x
        self.y = y
        self.scale = scale
        self.velocity_x = 0
        self.velocity_y = 0
        self.facing_right = True
        self.character = character
        self.current_state = IDLE
        
        # Load animations
        self.animations = {
            IDLE: sprite_sheet.get_animation_frames(character, IDLE),
            WALKING: sprite_sheet.get_animation_frames(character, WALKING),
            JUMPING: sprite_sheet.get_animation_frames(character, JUMPING)
        }
        
        # Animation properties
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 100  # milliseconds per frame
        
        # Set initial sprite dimensions based on first frame
        first_frame = self.animations[IDLE][0]
        self.width = first_frame.get_width() * scale
        self.height = first_frame.get_height() * scale

    def update(self, dt):
        """Update sprite animation and position."""
        # Update animation frame
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_state])
        
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y

    def draw(self, surface):
        """Draw the sprite with current animation frame."""
        current_sprite = self.animations[self.current_state][self.current_frame]
        
        # Scale sprite
        scaled_sprite = pygame.transform.scale(current_sprite, 
                                            (self.width, self.height))
        
        # Flip sprite if facing left
        if not self.facing_right:
            scaled_sprite = pygame.transform.flip(scaled_sprite, True, False)
        
        surface.blit(scaled_sprite, (self.x, self.y))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario World with Sprites")
        self.clock = pygame.time.Clock()
        
        # Load sprite sheet
        self.sprite_sheet = SpriteSheet("sprites.png")
        
        # Create characters
        self.mario = AnimatedSprite(self.sprite_sheet, 'mario', 100, 500)
        self.luigi = AnimatedSprite(self.sprite_sheet, 'luigi', 200, 500)
        
        # Create enemies
        self.enemies = [
            AnimatedSprite(self.sprite_sheet, 'goomba', 400, 500),
            AnimatedSprite(self.sprite_sheet, 'koopa', 600, 500)
        ]
        
        # Physics
        self.gravity = 0.8
        self.jump_force = -15
        self.move_speed = 5

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Mario controls
        if keys[pygame.K_LEFT]:
            self.mario.velocity_x = -self.move_speed
            self.mario.facing_right = False
            self.mario.current_state = WALKING
        elif keys[pygame.K_RIGHT]:
            self.mario.velocity_x = self.move_speed
            self.mario.facing_right = True
            self.mario.current_state = WALKING
        else:
            self.mario.velocity_x = 0
            self.mario.current_state = IDLE
            
        if keys[pygame.K_SPACE] and self.mario.velocity_y == 0:
            self.mario.velocity_y = self.jump_force
            self.mario.current_state = JUMPING
            
        # Luigi controls (for multiplayer)
        if keys[pygame.K_a]:
            self.luigi.velocity_x = -self.move_speed
            self.luigi.facing_right = False
            self.luigi.current_state = WALKING
        elif keys[pygame.K_d]:
            self.luigi.velocity_x = self.move_speed
            self.luigi.facing_right = True
            self.luigi.current_state = WALKING
        else:
            self.luigi.velocity_x = 0
            self.luigi.current_state = IDLE
            
        if keys[pygame.K_w] and self.luigi.velocity_y == 0:
            self.luigi.velocity_y = self.jump_force
            self.luigi.current_state = JUMPING

    def update(self):
        dt = self.clock.get_time()
        
        # Update characters
        for character in [self.mario, self.luigi] + self.enemies:
            # Apply gravity
            character.velocity_y += self.gravity
            
            # Update position and animation
            character.update(dt)
            
            # Ground collision
            if character.y > SCREEN_HEIGHT - character.height:
                character.y = SCREEN_HEIGHT - character.height
                character.velocity_y = 0
                if character.current_state == JUMPING:
                    character.current_state = IDLE
                    
        # Update enemy animations
        for enemy in self.enemies:
            enemy.current_state = WALKING  # Enemies always walking
            enemy.velocity_x = -2  # Simple left movement

    def draw(self):
        self.screen.fill((135, 206, 235))  # Sky blue background
        
        # Draw characters
        self.mario.draw(self.screen)
        self.luigi.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
