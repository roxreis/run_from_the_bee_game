import pgzero
import pgzrun
import random
import math

from pgzero.actor import Actor
from pygame import Rect

from constants import WIDTH, HEIGHT


class Player:
    def __init__(self):
        self.pos = [WIDTH // 2, HEIGHT // 2]
        self.speed = 4
        self.health = 100
        self.max_health = 100
        self.sprite = Actor('player_stopped')
        self.animation_state = 'stopped'
        self.animation_frame = 0
        self.direction = 'right'
        self.inventory = []

    def move(self, dx, dy):
        self.pos[0] += dx * self.speed
        self.pos[1] += dy * self.speed

        if dx != 0 or dy != 0:
            self.animation_state = 'walk'
            self.animation_frame = (self.animation_frame + 1) % 4
        else:
            self.animation_state = 'stopped'

        if dx > 0:
            self.direction = 'right'
        elif dx < 0:
            self.direction = 'left'

    def update_sprite(self):
        sprite_name = f'player_{self.animation_state}_{self.direction}_{self.animation_frame}'
        self.sprite.image = sprite_name

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            game_over()


class Enemy:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.speed = 3
        self.sprite = Actor('enemy_stopped')
        self.animation_state = 'stopped'
        self.animation_frame = 0
        self.time_waited = 0
        self.wait_time = 3000

    def start_moving_after_delay(self, delta_time):
        self.time_waited += delta_time
        if self.time_waited >= self.wait_time:
            self.move_towards_player(game_state.player)
        else:
            self.animation_state = 'stopped'
            self.animation_frame = 0

    def move_towards_player(self, player):
        dx = player.pos[0] - self.pos[0]
        dy = player.pos[1] - self.pos[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            self.pos[0] += (dx / distance) * self.speed
            self.pos[1] += (dy / distance) * self.speed

            self.check_collision_with_other_enemies()

            self.animation_state = 'walk'
            self.animation_frame = (self.animation_frame + 1) % 4

    def check_collision_with_other_enemies(self):
        for other_enemy in game_state.enemies:
            if other_enemy != self:
                dist_x = self.pos[0] - other_enemy.pos[0]
                dist_y = self.pos[1] - other_enemy.pos[1]
                distance = math.sqrt(dist_x ** 2 + dist_y ** 2)
                if distance < 40:
                    self.pos[0] += dist_x * 0.5
                    self.pos[1] += dist_y * 0.5

    def update_sprite(self):
        sprite_name = f'enemy_{self.animation_state}_{self.animation_frame}'
        self.sprite.image = sprite_name


class GameState:
    def __init__(self):
        self.player = Player()
        self.enemies = []
        self.current_screen = 'menu'
        self.music_on = True
        self.occupied_positions = []

    def spawn_enemies(self, num_enemies, min_distance=50):
        for _ in range(num_enemies):
            while True:
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
                too_close = False
                for (occupied_x, occupied_y) in self.occupied_positions:
                    if math.sqrt((x - occupied_x) ** 2 + (y - occupied_y) ** 2) < min_distance:
                        too_close = True
                        break
                if not too_close:
                    self.enemies.append(Enemy(x, y))
                    self.occupied_positions.append((x, y))
                    break


game_state = GameState()


def draw():
    screen.clear()
    Actor('background_game').draw()
    if game_state.current_screen == 'menu':
        draw_menu()
    elif game_state.current_screen == 'game':
        draw_game()
    elif game_state.current_screen == 'game_over':
        draw_game_over()


def draw_menu():
    screen.draw.text("RUN FROM THE BEE", (WIDTH // 2 - 170, 100), color='black', fontsize=80)
    draw_button("Start Game", WIDTH // 2 - 50, 250)
    draw_button("Music: ON" if game_state.music_on else "Music: OFF", WIDTH // 2 - 50, 350)
    draw_button("Exit", WIDTH // 2 - 50, 450)


def draw_game():
    game_state.player.sprite.pos = game_state.player.pos
    game_state.player.sprite.draw()

    for enemy in game_state.enemies:
        enemy.sprite.pos = enemy.pos
        enemy.sprite.draw()


def draw_game_over():
    screen.draw.text("GAME OVER", (WIDTH // 2 - 50, 200), color='red', fontsize=50)
    draw_button("Restart", WIDTH // 2 - 50, 300)


def draw_button(text, x, y):
    screen.draw.filled_rect(Rect(x, y, 200, 50), 'yellow')
    screen.draw.text(text, (x + 50, y + 10), color='black')


def update():
    if game_state.current_screen == 'game':
        update_game()


def update_game():
    delta_time = 33
    player_rect = Rect(game_state.player.pos[0], game_state.player.pos[1], 32, 32)
    if keyboard.left and player_rect.left > 0:
        game_state.player.move(-1, 0)
    if keyboard.right and player_rect.right < WIDTH:
        game_state.player.move(1, 0)
    if keyboard.up and player_rect.top > 0:
        game_state.player.move(0, -1)
    if keyboard.down and player_rect.bottom < HEIGHT:
        game_state.player.move(0, 1)

    game_state.player.update_sprite()

    for enemy in game_state.enemies:
        enemy.start_moving_after_delay(delta_time)  # Passa o tempo decorrido
        enemy.update_sprite()

    check_collisions()


def check_collisions():
    player_rect = Rect(game_state.player.pos[0], game_state.player.pos[1], 32, 32)
    for enemy in game_state.enemies:
        enemy_rect = Rect(enemy.pos[0], enemy.pos[1], 32, 32)
        if player_rect.colliderect(enemy_rect):
            game_state.player.take_damage(10)


def on_mouse_down(pos):
    if game_state.current_screen == 'menu':
        handle_menu_click(pos)
    elif game_state.current_screen == 'game_over':
        restart_game()


def handle_menu_click(pos):
    if 250 <= pos[1] <= 300:
        game_state.current_screen = 'game'
        game_state.spawn_enemies(15)
        play_music()
    elif 350 <= pos[1] <= 400:
        game_state.music_on = not game_state.music_on
        toggle_music()
    elif 450 <= pos[1] <= 500:
        exit()

# 
# def handle_game_over_click(pos):
#     if 350 <= pos[1] <= 400:
#         


def game_over():
    game_state.current_screen = 'game_over'
    stop_music()


def restart_game():
    global game_state
    game_state = GameState()
    game_state.current_screen = 'menu'


def play_music():
    if game_state.music_on:
        music.play('run_bee_theme')


def stop_music():
    music.stop()


def toggle_music():
    if game_state.music_on:
        play_music()
    else:
        stop_music()


pgzrun.go()
