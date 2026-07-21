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
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FUEL_BAR_WIDTH,
    FUEL_BAR_HEIGHT,
    FUEL_BAR_TOP_MARGIN,
    FUEL_BAR_RIGHT_MARGIN,
    FUEL_BAR_BORDER_WIDTH,
    FUEL_BAR_FULL_COLOR,
    FUEL_BAR_EMPTY_COLOR,
    FUEL_BAR_BORDER_COLOR,
    FUEL_TEXT_COLOR,
    FUEL_TEXT_FONT_SIZE,
    FUEL_TEXT_BOTTOM_MARGIN,
    TERRAIN_FILL_COLOR,
    LANDING_PAD_COLOR,
    LANDING_PAD_HEIGHT,
    STATUS_TEXT_FONT_SIZE,
    STATUS_TEXT_TOP_MARGIN,
    RUNNING_STATUS_COLOR,
    CRASHED_STATUS_COLOR,
    LANDED_STATUS_COLOR,
    CRASH_MARKER_SIZE,
    CRASH_MARKER_BLINK_INTERVAL_MS,
    CRASH_MARKER_RED_COLOR,
    CRASH_MARKER_ORANGE_COLOR,
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

        self.fuel_font = pygame.font.SysFont(None, FUEL_TEXT_FONT_SIZE) # Skapar font-objekt fr att sedan rita procenttexten
        self.status_font = pygame.font.SysFont(None, STATUS_TEXT_FONT_SIZE)

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

    def _draw_fuel_bar(self, rocket):
        """
        Draw a fuel bar and remaining fuel percentage as a screen-space overlay.
        """
        fuel_fraction = rocket.fuel_mass / rocket.max_fuel_mass
        fuel_percentage = round(fuel_fraction * 100)

        # Nedan anges tom bar helt i vitt
        fuel_bar_x = WINDOW_WIDTH - FUEL_BAR_RIGHT_MARGIN - FUEL_BAR_WIDTH
        fuel_bar_y = FUEL_BAR_TOP_MARGIN

        fuel_bar_rect = pygame.Rect(
            fuel_bar_x,
            fuel_bar_y,
            FUEL_BAR_WIDTH,
            FUEL_BAR_HEIGHT,
        )

        pygame.draw.rect(self.screen, FUEL_BAR_EMPTY_COLOR, fuel_bar_rect) # Ritar först tom tank i vitt

        # Över vita ritas den gråa som motsvarar ifylld, övre vänster hörn beror på fuel_fraction
        filled_height = int(fuel_fraction * FUEL_BAR_HEIGHT)
        filled_y = fuel_bar_y + (FUEL_BAR_HEIGHT - filled_height)

        filled_rect = pygame.Rect(
            fuel_bar_x,
            filled_y,
            FUEL_BAR_WIDTH,
            filled_height,
        )

        pygame.draw.rect(self.screen, FUEL_BAR_FULL_COLOR, filled_rect)
        pygame.draw.rect(self.screen, FUEL_BAR_BORDER_COLOR, fuel_bar_rect, FUEL_BAR_BORDER_WIDTH) # Ritar kant runt stapeln

        # Nedan skapas procent-texten
        fuel_text_surface = self.fuel_font.render(
            f"{fuel_percentage}%",
            True,
            FUEL_TEXT_COLOR,
        )

        
        fuel_text_rect = fuel_text_surface.get_rect( # Skapar rektangel som bestämmer var procent-texten ska sitta
            center=(
                fuel_bar_rect.centerx,
                fuel_bar_rect.top - FUEL_TEXT_BOTTOM_MARGIN,
            )
        )

        self.screen.blit(fuel_text_surface, fuel_text_rect)

    def _get_status_text_color(self, status):
        """
        Return the display color for the current simulation status.
        """
        if status == "running":
            return RUNNING_STATUS_COLOR
        if status == "crashed":
            return CRASHED_STATUS_COLOR
        if status == "landed":
            return LANDED_STATUS_COLOR

        return (0, 0, 0)

    def _draw_status_text(self, status):
        """
        Draw the current simulation status at the top center of the screen.
        """
        status_color = self._get_status_text_color(status)

        status_text_surface = self.status_font.render(
            status.upper(),
            True,
            status_color,
        )

        status_text_rect = status_text_surface.get_rect(
            center=(WINDOW_WIDTH // 2, STATUS_TEXT_TOP_MARGIN)
        )

        self.screen.blit(status_text_surface, status_text_rect)

    def _draw_terrain(self, terrain):
        """
        Draw the terrain as a filled ground polygon and a raised landing pad.
        """
        terrain_polygon_points = []

        for x_meter, y_meter in terrain.terrain_points:
            x_pixel = self._meters_to_pixels(x_meter)
            y_pixel = self._meters_to_pixels(y_meter)
            terrain_polygon_points.append((x_pixel, y_pixel))

        # Stänger hela polygonen genom att gå längs fönstrets kanter
        terrain_polygon_points.append((self._meters_to_pixels(terrain.terrain_points[-1][0]), WINDOW_HEIGHT))
        terrain_polygon_points.append((self._meters_to_pixels(terrain.terrain_points[0][0]), WINDOW_HEIGHT))

        pygame.draw.polygon(
            self.screen,
            TERRAIN_FILL_COLOR,
            terrain_polygon_points,
        )

        landing_pad_x = self._meters_to_pixels(terrain.landing_pad_x_min)
        landing_pad_y = self._meters_to_pixels(terrain.landing_pad_y - LANDING_PAD_HEIGHT)
        landing_pad_width = self._meters_to_pixels(terrain.landing_pad_x_max - terrain.landing_pad_x_min)
        landing_pad_height = self._meters_to_pixels(LANDING_PAD_HEIGHT)

        landing_pad_rect = pygame.Rect(
            landing_pad_x,
            landing_pad_y,
            landing_pad_width,
            landing_pad_height,
        )

        pygame.draw.rect(
            self.screen,
            LANDING_PAD_COLOR,
            landing_pad_rect,
        )

    def _draw_crash_marker(self, crash_marker_position):
        """
        Draw a blinking 1x1 meter marker centered on the crash corner.
        """
        if crash_marker_position is None:
            return

        blink_phase = (
            pygame.time.get_ticks() // CRASH_MARKER_BLINK_INTERVAL_MS
        ) % 2

        if blink_phase == 0:
            marker_color = CRASH_MARKER_RED_COLOR
        else:
            marker_color = CRASH_MARKER_ORANGE_COLOR

        marker_size_pixels = self._meters_to_pixels(CRASH_MARKER_SIZE)

        marker_center_x = self._meters_to_pixels(crash_marker_position[0])
        marker_center_y = self._meters_to_pixels(crash_marker_position[1])

        marker_rect = pygame.Rect(
            marker_center_x - marker_size_pixels // 2,
            marker_center_y - marker_size_pixels // 2,
            marker_size_pixels,
            marker_size_pixels,
        )

        pygame.draw.rect(self.screen, marker_color, marker_rect)

    def draw(self, rocket, terrain, actions, status, crash_marker_position):
        """
        Draw the current simulation state.
        """
        self.screen.fill(BACKGROUND_COLOR) # Fyller hela fönstret med given färg
        self._draw_terrain(terrain)

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

        self._draw_fuel_bar(rocket)
        self._draw_status_text(status)

        if status == "crashed":
            self._draw_crash_marker(crash_marker_position)

        pygame.display.flip() # Innan vi kör flip() så ritar pygame en osynlig bakgundsbild, den tidigare bilden ersätts inte förens flip()