import pygame
import math
from config import (
    BACKGROUND_COLOR,
    ROCKET_COLOR,
    ENGINE_COLOR,
    ROCKET_WIDTH,
    ROCKET_HEIGHT,
    MAIN_ENGINE_WIDTH,
    MAIN_ENGINE_HEIGHT,
    SIDE_ENGINE_WIDTH,
    SIDE_ENGINE_HEIGHT,
    MAIN_FLAME_COLOR,
    SIDE_FLAME_COLOR,
    MAIN_FLAME_WIDTH,
    MAIN_FLAME_HEIGHT,
    SIDE_FLAME_WIDTH,
    SIDE_FLAME_HEIGHT,
    PIXELS_PER_METER,
)

class Renderer:
    """
    Handles all rendering of the simulation.

    Responsible for drawing the rocket and other visual
    elements to the screen.
    """

    def __init__(self, screen):
        """
        Initialize the renderer and create the rocket surface.

        Args:
            screen: The pygame display surface.
        """
        self.screen = screen

        self.rocket_surface = pygame.Surface(
            (
                self._meters_to_pixels(ROCKET_WIDTH),
                self._meters_to_pixels(ROCKET_HEIGHT),
            ),
            pygame.SRCALPHA,
        ) # Skapar raket rityta
        self.main_flame_surface = pygame.Surface(
            (
                self._meters_to_pixels(MAIN_FLAME_WIDTH),
                self._meters_to_pixels(MAIN_FLAME_HEIGHT),
            ),
            pygame.SRCALPHA,
        )
        self.side_flame_surface = pygame.Surface(
            (
                self._meters_to_pixels(SIDE_FLAME_WIDTH),
                self._meters_to_pixels(SIDE_FLAME_HEIGHT),
            ),
            pygame.SRCALPHA,
        )

        self._create_rocket_surface()
        self._create_main_flame_surface()
        self._create_side_flame_surface()

    def _meters_to_pixels(self, length_in_meters):
        """
        Convert a length from meters to pixels for rendering.
        """
        return int(length_in_meters * PIXELS_PER_METER)

    def _rotate_local_point(self, local_x, local_y, angle):
        """
        Rotate a point from the rocket's local coordinate system to screen-oriented coordinates.

        The local origin is the rocket's center. Positive x points to the right,
        positive y points downward, and positive angle means counterclockwise rotation.
        """
        rotated_x = local_x * math.cos(angle) + local_y * math.sin(angle)
        rotated_y = -local_x * math.sin(angle) + local_y * math.cos(angle)
        return rotated_x, rotated_y

    def _create_rocket_surface(self):
        """
        Create the rocket's visual representation.
        """
        self.rocket_surface.fill((0, 0, 0, 0)) 

        rocket_body = pygame.Rect(
            0,
            0,
            self._meters_to_pixels(ROCKET_WIDTH),
            self._meters_to_pixels(ROCKET_HEIGHT),
        )

        main_engine_shape = pygame.Rect(
            self._meters_to_pixels(ROCKET_WIDTH / 2 - MAIN_ENGINE_WIDTH / 2),
            self._meters_to_pixels(ROCKET_HEIGHT - MAIN_ENGINE_HEIGHT),
            self._meters_to_pixels(MAIN_ENGINE_WIDTH),
            self._meters_to_pixels(MAIN_ENGINE_HEIGHT),
        )

        left_engine_shape = pygame.Rect(
            0,
            self._meters_to_pixels(ROCKET_HEIGHT - SIDE_ENGINE_HEIGHT),
            self._meters_to_pixels(SIDE_ENGINE_WIDTH),
            self._meters_to_pixels(SIDE_ENGINE_HEIGHT),
        )

        right_engine_shape = pygame.Rect(
            self._meters_to_pixels(ROCKET_WIDTH - SIDE_ENGINE_WIDTH),
            self._meters_to_pixels(ROCKET_HEIGHT - SIDE_ENGINE_HEIGHT),
            self._meters_to_pixels(SIDE_ENGINE_WIDTH),
            self._meters_to_pixels(SIDE_ENGINE_HEIGHT),
        )

        pygame.draw.rect(self.rocket_surface, ROCKET_COLOR, rocket_body) # Ritar rektangel på rocket_surface med formen rocket_shape
        pygame.draw.rect(self.rocket_surface, ENGINE_COLOR, main_engine_shape)
        pygame.draw.rect(self.rocket_surface, ENGINE_COLOR, left_engine_shape)
        pygame.draw.rect(self.rocket_surface, ENGINE_COLOR, right_engine_shape)

    def _create_main_flame_surface(self):
        """
        Create flame surface for the main engine.
        """
        self.main_flame_surface.fill((0, 0, 0, 0))

        main_flame_shape = pygame.Rect(
            0,
            0,
            self._meters_to_pixels(MAIN_FLAME_WIDTH),
            self._meters_to_pixels(MAIN_FLAME_HEIGHT),
        )

        pygame.draw.rect(self.main_flame_surface, MAIN_FLAME_COLOR, main_flame_shape)

    def _create_side_flame_surface(self):
        """
        Create reusable flame surface for the side engines.
        """
        self.side_flame_surface.fill((0, 0, 0, 0))

        side_flame_shape = pygame.Rect(
            0,
            0,
            self._meters_to_pixels(SIDE_FLAME_WIDTH),
            self._meters_to_pixels(SIDE_FLAME_HEIGHT),
        )

        pygame.draw.rect(self.side_flame_surface, SIDE_FLAME_COLOR, side_flame_shape)

    def draw(self, rocket, actions):
        """
        Draw the current simulation state.
        """
        self.screen.fill(BACKGROUND_COLOR) # Fyller hela fönstret med given färg

        rocket_surface_rotated = pygame.transform.rotate( # Roterar rocket_surface kring dess centrum
            self.rocket_surface,
            math.degrees(rocket.angle),
        )

        rocket_center_x_pixels = self._meters_to_pixels(rocket.x)
        rocket_center_y_pixels = self._meters_to_pixels(rocket.y)

        rocket_draw_position = rocket_surface_rotated.get_rect(
            center=(rocket_center_x_pixels, rocket_center_y_pixels)
        ) # Skapar hjälpobjekt som håller koll på vart bilden ska placeras
        self.screen.blit(rocket_surface_rotated, rocket_draw_position) # Ta bild som finns i roterade rocket_surface och placera den vid rocket_draw_position

        if actions["main_engine"]:
            main_flame_local_x = 0.0 # Denna och under beskriver centrum för flamman i raketens lokala koordinatsystem
            main_flame_local_y = ROCKET_HEIGHT / 2 + MAIN_FLAME_HEIGHT / 2 

            main_flame_offset_x, main_flame_offset_y = self._rotate_local_point( # Ta fram centrum_flammans nya punkt m.a.p raketens vinkel
                main_flame_local_x,
                main_flame_local_y,
                rocket.angle,
            )

            main_flame_center_x = rocket_center_x_pixels + self._meters_to_pixels(main_flame_offset_x) # Denna och under beskriver centurm för flamman i det utomstående koordinatsystemet
            main_flame_center_y = rocket_center_y_pixels + self._meters_to_pixels(main_flame_offset_y)

            main_flame_rotated = pygame.transform.rotate( # Roterar main_flame kring dess centrum
                self.main_flame_surface,
                math.degrees(rocket.angle),
            )

            main_flame_draw_position = main_flame_rotated.get_rect(center=(main_flame_center_x, main_flame_center_y))
            self.screen.blit(main_flame_rotated, main_flame_draw_position)

        if actions["left_engine"]:
            left_flame_local_x = -ROCKET_WIDTH / 2 - SIDE_FLAME_WIDTH / 2
            left_flame_local_y = ROCKET_HEIGHT / 2 - SIDE_FLAME_HEIGHT / 2

            left_flame_offset_x, left_flame_offset_y = self._rotate_local_point( 
                left_flame_local_x,
                left_flame_local_y,
                rocket.angle,
            )

            left_flame_center_x = rocket_center_x_pixels + self._meters_to_pixels(left_flame_offset_x) 
            left_flame_center_y = rocket_center_y_pixels + self._meters_to_pixels(left_flame_offset_y)

            left_frame_rotated = pygame.transform.rotate( 
                self.side_flame_surface,
                math.degrees(rocket.angle),
            )

            left_flame_draw_position = left_frame_rotated.get_rect(center=(left_flame_center_x, left_flame_center_y))
            self.screen.blit(left_frame_rotated, left_flame_draw_position)

        if actions["right_engine"]:
            right_flame_local_x = ROCKET_WIDTH / 2 + SIDE_FLAME_WIDTH / 2
            right_flame_local_y = ROCKET_HEIGHT / 2 - SIDE_FLAME_HEIGHT / 2

            right_flame_offset_x, right_flame_offset_y = self._rotate_local_point(
                right_flame_local_x,
                right_flame_local_y,
                rocket.angle,
            )

            right_flame_center_x = rocket_center_x_pixels + self._meters_to_pixels(right_flame_offset_x)
            right_flame_center_y = rocket_center_y_pixels + self._meters_to_pixels(right_flame_offset_y)

            right_flame_rotated = pygame.transform.rotate(
                self.side_flame_surface,
                math.degrees(rocket.angle),
            )

            right_flame_rect = right_flame_rotated.get_rect(center=(right_flame_center_x, right_flame_center_y))
            self.screen.blit(right_flame_rotated, right_flame_rect)
            

        pygame.display.flip() # Innan vi kör flip() så ritar pygame en osynlig bakgundsbild, den tidigare bilden ersätts inte förens flip()


