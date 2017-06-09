import arcade
import random
import time
import math
import pyglet
import itertools


# Tuples of keys for controls
KEY_FORWARD = (arcade.key.W, arcade.key.UP)
KEY_LEFT = (arcade.key.A, arcade.key.LEFT)
KEY_RIGHT = (arcade.key.D, arcade.key.RIGHT)
KEY_SHOOT = (arcade.key.SPACE,)


class Window(arcade.Window):
    """Window. Manages main game class"""

    def __init__(self, width, height):

        super().__init__(width, height, "Asteroids!")
        self.level = 0

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
        self.has_sound = True
        self.score = 0
        self.last_blink = 0

        arcade.load_sound_library()

        try:
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

        except pyglet.media.MediaFormatException:
            self.has_sound = False

    def spawn_asteroids(self):
        """Populate self.asteroids with random asteroids"""

        self.asteroids = [
            Asteroid(
                random.randint(100, self.width - 100), random.randint(100, self.height - 100),
                random.randint(-200, 200) / 100, random.randint(-200, 200) / 100
            )
            for _ in range(5 * self.level)
        ]

    def on_key_press(self, key, modifiers):
        """Handle controls"""

        if self.game_screen == "asteroids":
            if key in KEY_FORWARD:
                self.player.velocity = 5

            elif key in KEY_LEFT:
                self.player.turning = -2

            elif key in KEY_RIGHT:
                self.player.turning = 2

            elif key in KEY_SHOOT and self.bullets_shot != 1:
                self.bullets.append(Bullet(self.player.x, self.player.y, self.player.velocity + 2, self.player.angle))
                self.bullets_shot = 1

                if self.has_sound:
                    arcade.play_sound(self.shoot_sound)

        # If dead and key is pressed restart
        elif self.game_screen == "death" and time.time() - self.shown_screen_time > 3:

            self.lives = 10
            self.score = 0
            self.level = 0
            self.player.x = 0
            self.player.y = 0
            self.bullets = []
            self.spawn_asteroids()
            self.game_screen = "asteroids"
            self.last_death = time.time()

    def on_key_release(self, key, modifiers):
        """Handle controls"""

        if key in itertools.chain(KEY_LEFT, KEY_RIGHT):
            self.player.turning = 0

        elif key in KEY_FORWARD:
            self.player.velocity = 1

    def on_draw(self):
        """Update and draw the game"""

        # Add to the counter which is used to limit bullets and time screen cahnges
        self.time_accumulator += time.time() - self.last_frame_time
        self.last_frame_time = time.time()

        # Game screen is asteroids - update main game logic
        if self.game_screen == "asteroids":

            # Update player
            self.player.update()

            # Update asteroids
            for asteroid in self.asteroids:
                asteroid.update()

                """
                Remove the asteroid if it is out of bounds

                This will only happen if the asteroid has not bounced automatically in Asteroid#update
                which will only occur if it is too small

                1) Check if asteroid is out of x upper bound
                2) Check if asteroid is out of x lower bound
                3) Check if asteroid is out of y upper bound
                4) Check if asteroid is out of y lower bound

                """
                if (asteroid.x > w + asteroid.radius * 2) or (asteroid.x < -asteroid.radius * 2) or \
                        (asteroid.y > h + asteroid.radius * 2) or (asteroid.y < -asteroid.radius * 2):

                    self.asteroids.remove(asteroid)

                # Check if asteroid is colliding with player
                # Only do so if the asteroid is not space debris, i.e has size > 9
                if asteroid.size > 9 and \
                        arcade.geometry.are_polygons_intersecting(asteroid.transformed_polygon,
                                                                  self.player.bounding_box):

                    # Give player immunity for 5 seconds after death
                    if time.time() - self.last_death > 5:
                        self.lives -= 1
                        self.score -= 10
                        self.last_death = time.time()
                        self.last_blink = time.time()

                        if self.has_sound:
                            arcade.play_sound(self.death_sound)

            # Update bullets
            for bullet in self.bullets:
                bullet.update()

                # Make sure bullets aren't out of bounds; destroy if they are
                if bullet.x > w or bullet.x < 0 or bullet.y > h or bullet.y < 0:
                    self.bullets.remove(bullet)

                # Check for collisions between bullets and asteroids
                for asteroid in self.asteroids:
                    if arcade.geometry.are_polygons_intersecting(asteroid.transformed_polygon,
                                                                 bullet.transformed_polygon) and asteroid.size > 3:

                        # Only add to score if they are not debris, i.e size > 9
                        if asteroid.size > 9:
                            self.score += 5

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

                        if len(self.asteroids) < 100 or asteroid_a.size > 3:
                            self.asteroids.append(asteroid_a)
                            self.asteroids.append(asteroid_b)

                        self.asteroids.remove(asteroid)

                        if time.time() - self.last_asteroid_hit > 0.5:

                            if self.has_sound:
                                arcade.play_sound(self.asteroid_hit_sound)

                            self.last_asteroid_hit = time.time()

                        print("Boom!")

            # Reset bullet count
            # This prevents spamming bullets
            if self.time_accumulator > 1:
                self.bullets_shot = 0
                self.time_accumulator = 0

            # Go to next level if big asteroids are destroyed
            if len([1 for a in self.asteroids if a.size > 9]) == 0:
                self.game_screen = "next_level"

            if self.lives <= 0:
                self.game_screen = "death"

        # Render game
        arcade.start_render()

        # Show death screen
        if self.game_screen == "death":

            if self.shown_screen_time == 0:
                self.shown_screen_time = time.time()

            self.shown_screen_time += time.time() - self.last_frame_time

            arcade.draw_text("GAME OVER", self.width / 2 - 100, self.height / 2, arcade.color.WHITE,
                             font_size=24, font_name="courier new")
            arcade.draw_text("SCORE: {0}".format(self.score), self.width / 2 - 100, self.height / 2 - 75, arcade.color.WHITE,
                             font_size=24, font_name="courier new")

            if time.time() - self.shown_screen_time > 3:

                arcade.draw_text("PRESS ANY KEY TO PLAY AGAIN", self.width / 2 - 275, self.height / 2 - 150, arcade.color.WHITE,
                                 font_size=24, font_name="courier new")

        # Show next level screen
        elif self.game_screen == "next_level":

            if self.shown_screen_time == 0:
                self.level += 1
                self.shown_screen_time = time.time()
                arcade.draw_text("LEVEL {0}".format(self.level),
                                 self.width / 2 - 75, self.height / 2, arcade.color.WHITE,
                                 font_size=24, font_name="courier new")

            # Actually go to next level
            elif time.time() - self.shown_screen_time > 3:

                self.score += 20
                self.game_screen = "asteroids"
                self.bullets = []
                self.spawn_asteroids()
                self.shown_screen_time = 0
                self.last_death = time.time()

            else:
                arcade.draw_text("LEVEL {0}".format(self.level),
                                 self.width / 2 - 75, self.height / 2, arcade.color.WHITE,
                                 font_size=24, font_name="courier new")
                self.shown_screen_time += time.time() - self.last_frame_time

        # Show main game screen
        elif self.game_screen == "asteroids":
            for asteroid in self.asteroids:
                asteroid.render()

            for bullet in self.bullets:
                bullet.render()

            # Set last blink cycle time
            if time.time() - self.last_death < 5 and time.time() - self.last_blink > 0.35:
                self.last_blink = time.time()

            # Draw if blink is in "draw half"
            elif time.time() - self.last_blink < 0.2:
                self.player.render()

            # Draw if time - last death time > 5
            elif time.time() - self.last_death > 5:
                self.player.render()

            arcade.draw_text("LIVES: {0}".format(self.lives), 0, 15, arcade.color.WHITE, font_size=24, font_name="courier new")
            arcade.draw_text("SCORE: {0}".format(self.score), 0, self.height - 25, arcade.color.WHITE, font_size=24, font_name="courier new")


class Asteroid:
    """Class representing an asteroid"""

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
        """
        Polygon which represents where the asteroid actually is, not just the shape
        Relative to 0, 0
        """
        return [(x + self.x, y + self.y) for x, y in self.polygon]

    def update(self):
        """Update asteroid"""

        self.x += self.v_y
        self.y += self.v_x

        bounce = False

        for x, y in self.transformed_polygon:

            # Bounce if point is out of bounds
            if x > w or x < 0 or y > h or y < 0:
                bounce = True
                break

        # Only bounce if not space debris, i.e size > 9
        if bounce and self.size > 9:
            self.v_x *= -1
            self.v_y *= -1

    def render(self):
        """Render asteroid"""

        polygon = [(x + self.x, y + self.y) for x, y in self.polygon]

        arcade.draw_polygon_outline(polygon, arcade.color.WHITE)


class Bullet:
    """Class representing a bullet"""

    def __init__(self, x, y, velocity, direction):

        self.x = x
        self.y = y

        self.velocity = velocity
        self.angle = direction

    @property
    def transformed_polygon(self):
        """
        Polygon which represents where the bullet actually is, not just its shape
        Relative to 0, 0
        """

        return (
            (self.x, self.y),
            (self.x + 5, self.y),
            (self.x + 2.5, self.y + 5)
        )

    def update(self):
        """Update bullet"""

        self.angle %= 360

        self.x += self.velocity * math.sin(math.radians(self.angle))
        self.y += self.velocity * math.cos(math.radians(self.angle))

    def render(self):
        """Render bullet"""

        arcade.draw_triangle_outline(
            self.x, self.y,
            self.x + 5, self.y,
            self.x + 2.5, self.y + 5,
            arcade.color.WHITE
        )


class Player:
    """Class representing player"""

    def __init__(self, x, y, direction):

        self.x = x
        self.y = y
        self.texture = arcade.load_texture("ship.png", 0, 0, 200, 200, False, False, 0.01)

        self.velocity = 0
        self.angle = direction
        self.turning = 0

    @property
    def bounding_box(self):
        """Bounding box of player, relative to 0,0"""

        return [(self.x + 10, self.y + 10),
                (self.x - 10, self.y + 10),
                (self.x - 10, self.y - 10),
                (self.x + 10, self.y - 10)]

    def update(self):
        """Update player"""

        self.angle += self.turning
        self.angle %= 360

        self.x += self.velocity * math.sin(math.radians(self.angle))
        self.y += self.velocity * math.cos(math.radians(self.angle))

        self.x %= w + 10
        self.y %= h + 10

    def render(self):
        """Render player"""

        arcade.draw_texture_rectangle(self.x, self.y, 20, 20, self.texture, -self.angle, alpha=5, transparent=True)

# Set up game
w, h = 640, 500
window = Window(w, h)
time.sleep(1)  # Sleep to wait for window to open

arcade.set_window(window)
window.player.velocity = 1

# Run game
arcade.run()
