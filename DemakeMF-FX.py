import pygame
import sys
from enum import Enum
import math

# Placeholder for FTRender class definition
class FTRender:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def render(self):
        pass

class MenuState(Enum):
    MAIN = "main"
    CREDITS = "credits"
    PLAYING = "playing"

class MenuItem:
    def __init__(self, text, position, action, font_size=36):
        self.text = text
        self.position = position
        self.action = action
        self.font = pygame.font.Font(None, font_size)
        self.is_selected = False
        self.original_y = position[1]
        self.hover_offset = 0
        
    def draw(self, surface):
        color = (255, 255, 0) if self.is_selected else (255, 255, 255)
        text_surface = self.font.render(self.text, True, color)
        pos = (self.position[0], self.position[1] + self.hover_offset)
        surface.blit(text_surface, pos)
        
    def update(self):
        if self.is_selected:
            self.hover_offset = -5 * abs(math.sin(pygame.time.get_ticks() * 0.003))
        else:
            self.hover_offset = 0

class MenuSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = MenuState.MAIN
        self.selected_index = 0
        self.button_spacing = 60
        
        # Create menu items
        self.main_menu_items = [
            MenuItem("Start Game", (screen_width//2 - 80, screen_height//2 - 60), 
                     lambda: setattr(self, 'state', MenuState.PLAYING)),
            MenuItem("Credits", (screen_width//2 - 60, screen_height//2), 
                     lambda: setattr(self, 'state', MenuState.CREDITS)),
            MenuItem("Exit", (screen_width//2 - 40, screen_height//2 + 60), 
                     lambda: sys.exit())
        ]
        
        # Title font
        self.title_font = pygame.font.Font(None, 72)
        
        # Credits text
        self.credits_text = [
            "Super Mario FX Beta",
            "A Fan Recreation",
            "",
            "Programming:",
            "FTRender Engine Team",
            "",
            "Original Concept:",
            "Nintendo & Silicon Graphics",
            "",
            "Press ESC to return"
        ]
        self.credits_font = pygame.font.Font(None, 36)
        
        # Background effect
        self.bg_angle = 0
        self.bg_tiles = self.create_background_tiles()

        # State tracking for key presses
        self.prev_up = False
        self.prev_down = False
        self.prev_enter = False
        
    def create_background_tiles(self):
        tile_size = 40
        tiles = []
        for x in range(-tile_size, self.screen_width + tile_size, tile_size):
            for y in range(-tile_size, self.screen_height + tile_size, tile_size):
                tiles.append((x, y))
        return tiles
        
    def update(self):
        self.bg_angle += 0.5
        
        if self.state == MenuState.MAIN:
            keys = pygame.key.get_pressed()
            
            # Update selected item
            for item in self.main_menu_items:
                item.is_selected = False
            self.main_menu_items[self.selected_index].is_selected = True
            
            # Update menu item animations
            for item in self.main_menu_items:
                item.update()
            
            if keys[pygame.K_UP] and not self.prev_up:
                self.selected_index = (self.selected_index - 1) % len(self.main_menu_items)
            elif keys[pygame.K_DOWN] and not self.prev_down:
                self.selected_index = (self.selected_index + 1) % len(self.main_menu_items)
            elif keys[pygame.K_RETURN] and not self.prev_enter:
                self.main_menu_items[self.selected_index].action()
                
            self.prev_up = keys[pygame.K_UP]
            self.prev_down = keys[pygame.K_DOWN]
            self.prev_enter = keys[pygame.K_RETURN]
            
        elif self.state == MenuState.CREDITS:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                self.state = MenuState.MAIN
                
    def draw_background(self, screen):
        # Create rotating grid effect
        angle_rad = math.radians(self.bg_angle)
        for x, y in self.bg_tiles:
            cx, cy = self.screen_width/2, self.screen_height/2
            px = x - cx
            py = y - cy
            rot_x = px * math.cos(angle_rad) - py * math.sin(angle_rad) + cx
            rot_y = px * math.sin(angle_rad) + py * math.cos(angle_rad) + cy
            
            pygame.draw.rect(screen, (0, 0, 100), (rot_x, rot_y, 2, 2))
    
    def draw(self, screen):
        screen.fill((0, 0, 40))
        self.draw_background(screen)
        
        if self.state == MenuState.MAIN:
            # Draw title
            title_text = self.title_font.render("Super Mario FX Beta", True, (255, 255, 255))
            screen.blit(title_text, (self.screen_width//2 - title_text.get_width()//2, 100))
            
            # Draw menu items
            for item in self.main_menu_items:
                item.draw(screen)
                
        elif self.state == MenuState.CREDITS:
            for i, line in enumerate(self.credits_text):
                text_surface = self.credits_font.render(line, True, (255, 255, 255))
                y_pos = 100 + i * 40
                screen.blit(text_surface, 
                           (self.screen_width//2 - text_surface.get_width()//2, y_pos))

class GameObject:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.width, self.height))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Super Mario FX Beta")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize menu system
        self.menu = MenuSystem(800, 600)
        
        # Initialize game components
        self.renderer = FTRender(800, 600)
        self.camera = pygame.math.Vector2(0, 0)
        self.camera_angle = 0
        
        # Initialize game objects
        self.mario = GameObject(100, 100, 24, 24)
        self.luigi = GameObject(160, 100, 24, 24)
        self.game_objects = [self.mario, self.luigi]
        
        # Load textures and create render objects
        self.init_textures()

    def init_textures(self):
        # Placeholder for texture loading logic
        pass
        
    def handle_input(self):
        keys = pygame.key.get_pressed()
        # Move Mario around using arrow keys
        if keys[pygame.K_LEFT]:
            self.mario.x -= 5
        if keys[pygame.K_RIGHT]:
            self.mario.x += 5
        if keys[pygame.K_UP]:
            self.mario.y -= 5
        if keys[pygame.K_DOWN]:
            self.mario.y += 5

    def update(self):
        # Update game logic here (if any)
        pass

    def render(self):
        # Render the gameplay screen
        self.screen.fill((0, 0, 0))
        for obj in self.game_objects:
            obj.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    # If in game (PLAYING) and ESC is pressed, return to main menu
                    if event.key == pygame.K_ESCAPE and self.menu.state == MenuState.PLAYING:
                        self.menu.state = MenuState.MAIN

            # Update and render based on current state
            if self.menu.state == MenuState.PLAYING:
                self.handle_input()
                self.update()
                self.render()
            else:
                self.menu.update()
                self.menu.draw(self.screen)
                pygame.display.flip()
                
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
