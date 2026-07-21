import math

from config import (
    ROCKET_WIDTH,
    ROCKET_HEIGHT,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    PIXELS_PER_METER,
    MAX_LANDING_VERTICAL_SPEED,
    MAX_LANDING_HORIZONTAL_SPEED,
    MAX_LANDING_ANGLE,
    MAX_LANDING_ANGULAR_VELOCITY,
)

"""
Collision and landing-condition utilities for the rocket simulation.
"""

def _get_rocket_corners(rocket):
    """
    Return the rocket's four corners in world coordinates.

    The rocket position (rocket.x, rocket.y) is the center of the rectangle.
    Corner coordinates are first defined in the rocket's local coordinate system,
    then rotated by the rocket angle, and finally translated into world coordinates.
    """
    half_width = ROCKET_WIDTH / 2
    half_height = ROCKET_HEIGHT / 2

    local_corners = [
        (-half_width, -half_height),  # top left
        (half_width, -half_height),   # top right
        (half_width, half_height),    # bottom right
        (-half_width, half_height),   # bottom left
    ]

    world_corners = []

    for local_x, local_y in local_corners:
        rotated_x = local_x * math.cos(rocket.angle) + local_y * math.sin(rocket.angle)
        rotated_y = -local_x * math.sin(rocket.angle) + local_y * math.cos(rocket.angle)

        world_x = rocket.x + rotated_x
        world_y = rocket.y + rotated_y

        world_corners.append((world_x, world_y))

    return world_corners

def _is_rocket_out_of_bounds(corners):
    """
    Return True if any rocket corner is outside the world bounds otherwise False.
    """
    world_width_meters = WINDOW_WIDTH / PIXELS_PER_METER
    world_height_meters = WINDOW_HEIGHT / PIXELS_PER_METER

    for corner_x, corner_y in corners:
        if corner_x < 0.0:
            return True
        if corner_x > world_width_meters:
            return True
        if corner_y < 0.0:
            return True
        if corner_y > world_height_meters:
            return True

    return False

def _point_touches_segment(point, segment, epsilon=0.25):
    """
    Return True if a point lies on or very close (margin with epsilon) 
    to a terrain segment or False if not.
    """
    point_x, point_y = point
    (x1, y1), (x2, y2) = segment

    min_x = min(x1, x2)
    max_x = max(x1, x2)
    min_y = min(y1, y2)
    max_y = max(y1, y2)

    if point_x < min_x - epsilon or point_x > max_x + epsilon:
        return False
    if point_y < min_y - epsilon or point_y > max_y + epsilon:
        return False

    if x1 == x2:
        point_is_on_vertical_segment = abs(point_x - x1) <= epsilon
        return point_is_on_vertical_segment

    slope = (y2 - y1) / (x2 - x1) # Lutning för linjesekmentet
    expected_y = y1 + slope * (point_x - x1)  # Räta linjens ekvation för linjesegmentet

    point_is_on_segment_line = abs(point_y - expected_y) <= epsilon
    return point_is_on_segment_line

def _rocket_touches_terrain(corners, terrain_segments):
    """Return True if any rocket corner touches any terrain_segment.
    I.e return True if the rocket has crashed."""
    for corner in corners:
        for segment in terrain_segments:
            if _point_touches_segment(corner, segment):
                return True

    return False

def _collision_is_on_landing_pad(corners, terrain, epsilon=0.25):
    """
    Return True if any rocket corner touches the landing pad segment.
    """
    landing_pad_segment = (
        (terrain.landing_pad_x_min, terrain.landing_pad_y),
        (terrain.landing_pad_x_max, terrain.landing_pad_y),
    )

    for corner in corners:
        if _point_touches_segment(corner, landing_pad_segment, epsilon):
            return True

    return False

def _meets_landing_conditions(rocket):
    """
    Return True if the rocket state satisfies all landing limits.
    """
    vertical_speed_is_safe = abs(rocket.velocity_y) <= MAX_LANDING_VERTICAL_SPEED
    horizontal_speed_is_safe = abs(rocket.velocity_x) <= MAX_LANDING_HORIZONTAL_SPEED

    normalized_angle = math.atan2(math.sin(rocket.angle), math.cos(rocket.angle)) # Skriver om aktuell vinkel till standardintervall utifrån x,y koordinater
    angle_is_safe = abs(normalized_angle) <= MAX_LANDING_ANGLE 

    angular_velocity_is_safe = (
        abs(rocket.angular_velocity) <= MAX_LANDING_ANGULAR_VELOCITY
    )

    rocket_meets_landing_conditions = (
        vertical_speed_is_safe
        and horizontal_speed_is_safe
        and angle_is_safe
        and angular_velocity_is_safe
    )

    return rocket_meets_landing_conditions

def evaluate_rocket_status(rocket, terrain):
    """
    Determine the rocket's current simulation status from terrain contact
    and landing conditions.

    The rocket is classified as crashed if it is out of bounds or touches
    terrain outside the landing pad. A landing pad collision is classified
    as landed only if all landing conditions are satisfied. Otherwise the
    rocket is crashed.

    Returns:
        str: "running", "landed", or "crashed".
    """
    corners = _get_rocket_corners(rocket)

    rocket_is_out_of_bounds = _is_rocket_out_of_bounds(corners)
    if rocket_is_out_of_bounds:
        return "crashed"

    terrain_segments = terrain.get_segments()
    rocket_has_terrain_contact = _rocket_touches_terrain(corners, terrain_segments)
    if not rocket_has_terrain_contact:
        return "running"

    collision_happened_on_landing_pad = _collision_is_on_landing_pad(corners, terrain)
    rocket_has_safe_landing_state = _meets_landing_conditions(rocket)

    if collision_happened_on_landing_pad and rocket_has_safe_landing_state:
        return "landed"

    return "crashed"

def get_terrain_contact_corner(rocket, terrain):
    """
    Return the first rocket corner that touches any terrain segment
    Return None if no corners touches any terrain segmants
    """
    corners = _get_rocket_corners(rocket)
    terrain_segments = terrain.get_segments()

    for corner in corners:
        for segment in terrain_segments:
            if _point_touches_segment(corner, segment):
                return corner

    return None