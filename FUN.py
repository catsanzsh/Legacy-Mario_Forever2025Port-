import os
import sys
import random
import inspect
from datetime import datetime
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

class Mario3DEngine(Ursina):
    def __init__(self):
        super().__init__()  # Initialize the Ursina engine first
        
        # Initialize game components
        self.setup_window()
        self.create_player()
        self.create_ui()
        self.setup_environment()

        # Define levels and load the first level
        self.levels = self.define_levels()
        self.current_level = 0
        
        if self.levels:  # Check if levels are defined
            self.load_level(self.current_level)
        else:
            print("Error: No levels defined. Exiting game.")
            application.quit()  # Exit the application if levels are missing


    def setup_window(self):
        window.title = 'Super Mario 3D'
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        window.fps_counter.enabled = True

    def create_player(self):
        self.player = FirstPersonController(
            model='cube', color=color.red, scale=(1, 2, 1), position=(0, 2, 0),
            speed=10, jump_height=4
        )
        self.player.health = 3
        self.score = 0

    def create_ui(self):
        self.health_text = Text(text=f'Lives: {self.player.health}', position=(-0.85, 0.45))
        self.score_text = Text(text=f'Score: {self.score}', position=(-0.85, 0.4))
        self.status_message = Text(text='', position=(0, 0.3), visible=False)
        self.flash_effect = Entity(model='quad', scale=(2, 1), color=color.rgba(1, 1, 1, 0), z=-0.1)

    def setup_environment(self):
        self.sky = Sky()  # Ensuring `sky` is created before accessing it
        self.directional_light = DirectionalLight(y=-1, z=-1)

    def define_levels(self):
        return [
            {'theme': 'grass', 'color': color.green, 'enemies': 5, 'coins': 10, 'ground_scale': (100, 1, 100),
             'platforms': 8},
            {'theme': 'desert', 'color': color.yellow, 'enemies': 7, 'coins': 15, 'ground_scale': (120, 1, 120),
             'platforms': 10},
            {'theme': 'snow', 'color': color.white, 'enemies': 10, 'coins': 20, 'ground_scale': (150, 1, 150),
             'platforms': 12}
        ]

    def load_level(self, level_idx):
        level = self.levels[level_idx]
        self.clear_scene()
        self.show_message(f'Level {level_idx + 1}: {level["theme"].title()}', 2)
        self.create_level_elements(level)

    def clear_scene(self):
        for entity in scene.entities:
            if entity not in [self.player, self.sky, self.directional_light, self.flash_effect, self.status_message]:
                destroy(entity)

    def create_level_elements(self, level):
        self.ground = Entity(
            model='plane', scale=level['ground_scale'], color=level['color'],
            texture=self.get_texture(level['theme']), texture_scale=(50, 50), collider='box'
        )
        self.create_platforms(level['platforms'])
        self.create_coins(level['coins'])
        self.create_enemies(level['enemies'])

    @staticmethod
    def get_texture(theme):
        return {
            'grass': 'grass',
            'desert': 'sand',
            'snow': 'snow'
        }.get(theme, 'grass')

    def create_platforms(self, count):
        self.platforms = [
            Entity(
                model='cube', color=color.light_gray,
                position=(random.uniform(-40, 40), random.uniform(3, 15), random.uniform(-40, 40)),
                scale=(4, 0.5, 4), texture='brick', collider='box'
            )
            for _ in range(count)
        ]

    def create_coins(self, count):
        self.coins = [
            Entity(
                model='sphere', scale=0.5, color=color.gold,
                position=(random.uniform(-45, 45), random.uniform(1, 10), random.uniform(-45, 45)),
                collider='sphere'
            )
            for _ in range(count)
        ]
        for coin in self.coins:
            coin.animate_rotation_y(360, duration=1, loop=True)

    def create_enemies(self, count):
        self.enemies = [
            Entity(
                model='cube', scale=(1, 1, 1), color=color.red,
                position=(random.uniform(-45, 45), 1, random.uniform(-45, 45)),
                collider='box'
            )
            for _ in range(count)
        ]
        for enemy in self.enemies:
            enemy.speed = random.uniform(2, 4)
            enemy.direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()

    def show_message(self, text, duration=1):
        self.status_message.text = text
        self.status_message.visible = True
        invoke(self.hide_message, delay=duration)

    def hide_message(self):
        self.status_message.visible = False

    def update(self):
        self.update_ui()

    def update_ui(self):
        if self.health_text.text != f'Lives: {self.player.health}':
            self.health_text.text = f'Lives: {self.player.health}'
        if self.score_text.text != f'Score: {self.score}':
            self.score_text.text = f'Score: {self.score}'

    def patch_program(self):
        """
        Saves a patched version of the entire program with a timestamp.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_file_path = f"SM3D_patched_{timestamp}.py"
        try:
            # Determine the current script's file path
            if hasattr(sys, 'frozen'):
                # If the script is bundled (e.g., with PyInstaller)
                current_file = sys.executable
            else:
                current_file = __file__

            # Read the entire content of the current script
            with open(current_file, "r") as file:
                content = file.read()

            # Write the content to the new patched file
            with open(new_file_path, "w") as new_file:
                new_file.write(content)

            print(f"New build saved at: {new_file_path}")
        except Exception as e:
            print(f"Failed to create a patched build: {e}")


if __name__ == '__main__':
    try:
        game = Mario3DEngine()
        game.run()
    except Exception as e:
        print(f"Exception occurred: {e}")
        print("Attempting to create a patched build...")
        Mario3DEngine().patch_program()
