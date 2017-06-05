import arcade
import random
import time
import math

KEY_FORWARD = arcade.key.W
KEY_LEFT = arcade.key.A
KEY_RIGHT = arcade.key.D
KEY_SHOOT = arcade.key.SPACE


class Window(arcade.Window):

    def __init__(self, width, height):

        super().__init__(width, height, title="Asteroids!")
        self.level = 1

        self.player = Player(self.width / 2, self.height / 2, 0)
        self.bullets = []

        self.asteroids = []
        self.spawn_asteroids()

        self.bullets_shot = 0
        self.last_frame_time = time.time()
        self.time_accumulator = 0
        self.lives = 10
        self.last_death = time.time()
        self.last_asteroid_hit = time.time()
        self.shown_screen_time = 0
        self.game_screen = "asteroids"

        arcade.load_sound_library()
        # LICENSED UNDER CC BY 3.0
        # https://www.freesound.org/people/ani_music/sounds/219619/
        # https://creativecommons.org/licenses/by/3.0/legalcode
        self.shoot_sound = arcade.load_sound("pew.wav")

        # LICENSED UNDER CC 0
        # https://www.freesound.org/people/Xenonn/sounds/128302/
        self.asteroid_hit_sound = arcade.load_sound("asteroid_hit.wav")

        # LICENSED UNDER CC BY 3.0
        # https://www.freesound.org/people/bone666138/sounds/198876/
        # Converted from aiff to wav
        # https://creativecommons.org/licenses/by/3.0/legalcode
        self.death_sound = arcade.load_sound("death.wav")

    def spawn_asteroids(self):

        self.asteroids = [
            Asteroid(
                random.randint(100, self.width - 100), random.randint(100, self.height - 100),
                random.randint(-200, 200) / 100, random.randint(-200, 200) / 100
            )
            for _ in range(5 * self.level)
        ]

    def on_key_press(self, key, modifiers):

        if key == KEY_FORWARD:
            self.player.velocity *= 5
            self.player.turning *= 2

        elif key == KEY_LEFT:
            self.player.turning = -2

        elif key == KEY_RIGHT:
            self.player.turning = 2

        elif key == KEY_SHOOT and self.bullets_shot != 1:
            self.bullets.append(Bullet(self.player.x, self.player.y, self.player.velocity + 2, self.player.angle))
            self.bullets_shot += 1
            arcade.play_sound(self.shoot_sound)

    def on_key_release(self, key: int, modifiers: int):

        if key in (KEY_LEFT, KEY_RIGHT):
            self.player.turning = 0

        elif key == KEY_FORWARD:
            self.player.velocity /= 5
            self.player.turning /= 2

    def on_draw(self):

        self.time_accumulator += time.time() - self.last_frame_time
        self.last_frame_time = time.time()

        if self.game_screen == "asteroids":
            self.player.update()

            for asteroid in self.asteroids:
                asteroid.update()

                if (asteroid.x > w + asteroid.radius * 2) or (asteroid.x < -asteroid.radius * 2) or \
                        (asteroid.y > h + asteroid.radius * 2) or (asteroid.y < -asteroid.radius * 2):

                    self.asteroids.remove(asteroid)

                if asteroid.radius > 9 and \
                        arcade.geometry.are_polygons_intersecting(asteroid.transformed_polygon,
                                                                  self.player.bounding_box):

                    if time.time() - self.last_death > 5:
                        self.lives -= 1
                        self.last_death = time.time()
                        arcade.play_sound(self.death_sound)

            for bullet in self.bullets:
                bullet.update()

                if bullet.x > w or bullet.x < 0 or bullet.y > h or bullet.y < 0:
                    self.bullets.remove(bullet)

                for asteroid in self.asteroids:
                    if arcade.geometry.are_polygons_intersecting(asteroid.transformed_polygon,
                                                                 bullet.transformed_polygon):

                        # Bullet has hit asteroid, split asteroid up into two of the next prime asteroid

                        sides = asteroid.side_ordinal - 1 if asteroid.side_ordinal - 1 != -1 else 0

                        asteroid_a = Asteroid(
                            random.randint(
                                min(int(asteroid.x), int(asteroid.x + asteroid.radius)),
                                max(int(asteroid.x), int(asteroid.x + asteroid.radius))
                            ),
                            random.randint(
                                min(int(asteroid.y,), int(asteroid.y + asteroid.radius)),
                                max(int(asteroid.y, ), int(asteroid.y + asteroid.radius)),
                            ),
                            random.randint(-200, 200) / 100, random.randint(-200, 200) / 100,
                            side_ordinal=sides,
                            size=asteroid.size / 2
                        )

                        asteroid_b = Asteroid(
                            random.randint(
                                min(int(asteroid.x), int(asteroid.x + asteroid.radius)),
                                max(int(asteroid.x), int(asteroid.x + asteroid.radius))
                            ),
                            random.randint(
                                min(int(asteroid.y,), int(asteroid.y + asteroid.radius)),
                                max(int(asteroid.y, ), int(asteroid.y + asteroid.radius)),
                            ),
                            random.randint(-200, 200) / 100, random.randint(-200, 200) / 100,
                            side_ordinal=sides,
                            size=asteroid.size / 2
                        )

                        if len(self.asteroids) < 200 or asteroid_a.size > 3:
                            self.asteroids.append(asteroid_a)
                            self.asteroids.append(asteroid_b)

                        self.asteroids.remove(asteroid)

                        if time.time() - self.last_asteroid_hit > 0.5:
                            arcade.play_sound(self.asteroid_hit_sound)
                            self.last_asteroid_hit = time.time()

                        print("Boom!")

            if self.time_accumulator > 1:
                self.bullets_shot = 0
                self.time_accumulator = 0

            if len(self.asteroids) == 0:
                self.game_screen = "next_level"

            if self.lives <= 0:
                self.game_screen = "death"

        arcade.start_render()

        if self.game_screen == "death":

            arcade.draw_text("GAME OVER", self.width / 2 - 100, self.height / 2, arcade.color.WHITE, font_size=24,
                             font_name="courier new")
            return

        elif self.game_screen == "next_level":

            if self.shown_screen_time == 0:
                self.level += 1
                self.shown_screen_time = time.time()
                arcade.draw_text(f"LEVEL {self.level}",
                                 self.width / 2 - 100, self.height / 2, arcade.color.WHITE,
                                 font_size=24, font_name="courier new")

                self.shown_screen_time = time.time()

            elif time.time() - self.shown_screen_time > 3:

                self.game_screen = "asteroids"
                self.spawn_asteroids()
                self.shown_screen_time = 0

            else:
                arcade.draw_text(f"LEVEL {self.level}",
                                 self.width / 2 - 100, self.height / 2, arcade.color.WHITE,
                                 font_size=24, font_name="courier new")
                self.shown_screen_time += time.time() - self.last_frame_time

            return

        for asteroid in self.asteroids:
            asteroid.render()

        for bullet in self.bullets:
            bullet.render()

        self.player.render()

        arcade.draw_text(f"LIVES: {self.lives}", 0, 10, arcade.color.WHITE, font_size=24, font_name="courier new")


class Asteroid:

    def __init__(self, x, y, v_x, v_y, side_ordinal=None, size=random.randint(20, 25)):

        self.x = x
        self.y = y
        self.v_x = v_x
        self.v_y = v_y

        self.polygon = []
        self.side_ordinal = side_ordinal if side_ordinal is not None else random.randint(0, 3)
        self.size = size
        self.sides = (3, 5, 7, 11)[self.side_ordinal]  # Prime numbered polygons
        self.radius = abs(self.size / (2 * math.sin(180 / self.sides)))

        exterior_angle = math.radians(360 / self.sides)
        cur_angle = 0
        cur_pos = [0, 0]

        for i in range(self.sides):

            cur_angle += exterior_angle
            cur_pos = [math.sin(cur_angle) * self.size + cur_pos[0], cur_pos[1] + math.cos(cur_angle) * self.size]
            self.polygon.append(cur_pos)

    @property
    def transformed_polygon(self):
        return [(x + self.x, y + self.y) for x, y in self.polygon]

    def update(self):

        self.x += self.v_y
        self.y += self.v_x

        bounce = False

        for x, y in self.transformed_polygon:

            if x > w or x < 0 or y > h or y < 0:
                bounce = True
                break

        if bounce and self.size > 9:
            self.v_x *= -1
            self.v_y *= -1

    def render(self):

        polygon = [(x + self.x, y + self.y) for x, y in self.polygon]

        arcade.draw_polygon_outline(polygon, arcade.color.WHITE)


class Bullet:

    def __init__(self, x, y, velocity, direction):

        self.x = x
        self.y = y

        self.velocity = velocity
        self.angle = direction

    @property
    def transformed_polygon(self):

        return (
            (self.x, self.y),
            (self.x + 5, self.y),
            (self.x + 2.5, self.y + 5)
        )

    def update(self):

        self.angle %= 360

        self.x += self.velocity * math.sin(math.radians(self.angle))
        self.y += self.velocity * math.cos(math.radians(self.angle))

    def render(self):

        arcade.draw_triangle_outline(
            self.x, self.y,
            self.x + 5, self.y,
            self.x + 2.5, self.y + 5,
            arcade.color.WHITE
        )


class Player:

    def __init__(self, x, y, direction):

        self.x = x
        self.y = y
        self.texture = arcade.load_texture("ship.png", 0, 0, 200, 200, False, False, 0.01)

        self.velocity = 0
        self.angle = direction
        self.turning = 0

    @property
    def bounding_box(self):
        return [(self.x + 10, self.y + 10),
                (self.x - 10, self.y + 10),
                (self.x - 10, self.y - 10),
                (self.x + 10, self.y - 10)]

    def update(self):

        self.angle += self.turning
        self.angle %= 360

        self.x += self.velocity * math.sin(math.radians(self.angle))
        self.y += self.velocity * math.cos(math.radians(self.angle))

        self.x %= w + 10
        self.y %= h + 10

    def render(self):

        arcade.draw_texture_rectangle(self.x, self.y, 20, 20, self.texture, -self.angle, alpha=5, transparent=True)


def choose_keyscheme():

    while True:
        c = input("WASD or arrow keys? (1/2) ")

        if c != "1" and c != "2":
            print("Please input 1 or 2!")

        else:
            break

    return c

choice = choose_keyscheme()

if choice == "1":
    KEY_FORWARD = arcade.key.W
    KEY_LEFT = arcade.key.A
    KEY_RIGHT = arcade.key.D

else:
    KEY_FORWARD = arcade.key.UP
    KEY_LEFT = arcade.key.LEFT
    KEY_RIGHT = arcade.key.RIGHT

w, h = 640, 500
window = Window(w, h)
time.sleep(1)  # Sleep to wait for window to open

arcade.set_window(window)
window.player.velocity = 1

arcade.run()
