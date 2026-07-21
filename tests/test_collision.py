from pathlib import Path
import math
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src" / "rocket"))

from collision import (
    _collision_is_on_landing_pad,
    _get_rocket_corners,
    _is_rocket_out_of_bounds,
    _meets_landing_conditions,
    _point_touches_segment,
    _rocket_touches_terrain,
    evaluate_rocket_status,
    get_terrain_contact_corner,
)
from config import (
    MAX_LANDING_ANGLE,
    MAX_LANDING_ANGULAR_VELOCITY,
    MAX_LANDING_HORIZONTAL_SPEED,
    MAX_LANDING_VERTICAL_SPEED,
    ROCKET_HEIGHT,
    ROCKET_WIDTH,
)
from rocket import Rocket
from terrain import Terrain


def create_rocket_touching_horizontal_segment(center_x, segment_y):
    """
    Create a rocket whose bottom corners lie on a horizontal segment.
    """
    rocket = Rocket()
    rocket.x = center_x
    rocket.y = segment_y - ROCKET_HEIGHT / 2
    rocket.angle = 0.0
    return rocket


"""Rocket corners"""


def test_get_rocket_corners_returns_expected_corners_at_zero_angle():
    """
    Verify that the rocket corners are correct when the rocket is not rotated.
    """
    rocket = Rocket()

    corners = _get_rocket_corners(rocket)

    half_width = ROCKET_WIDTH / 2
    half_height = ROCKET_HEIGHT / 2

    assert corners == pytest.approx([
        (rocket.x - half_width, rocket.y - half_height),
        (rocket.x + half_width, rocket.y - half_height),
        (rocket.x + half_width, rocket.y + half_height),
        (rocket.x - half_width, rocket.y + half_height),
    ])


def test_get_rocket_corners_returns_expected_corners_at_half_pi_rotation():
    """
    Verify that the rocket corners rotate correctly for a 90 degree angle.
    """
    rocket = Rocket()
    rocket.angle = math.pi / 2

    corners = _get_rocket_corners(rocket)

    half_width = ROCKET_WIDTH / 2
    half_height = ROCKET_HEIGHT / 2

    assert corners == pytest.approx([
        (rocket.x - half_height, rocket.y + half_width),
        (rocket.x - half_height, rocket.y - half_width),
        (rocket.x + half_height, rocket.y - half_width),
        (rocket.x + half_height, rocket.y + half_width),
    ])


"""Bounds"""


def test_is_rocket_out_of_bounds_returns_false_for_default_rocket():
    """
    Verify that the default rocket starts within the world bounds.
    """
    rocket = Rocket()
    corners = _get_rocket_corners(rocket)

    assert _is_rocket_out_of_bounds(corners) is False


def test_is_rocket_out_of_bounds_returns_true_when_a_corner_leaves_world():
    """
    Verify that the bounds check detects when a corner moves outside the world.
    """
    rocket = Rocket()
    rocket.x = 0.5
    corners = _get_rocket_corners(rocket)

    assert _is_rocket_out_of_bounds(corners) is True


"""Point to segment contact"""


def test_point_touches_segment_detects_contact_on_horizontal_segment():
    """
    Verify that a point on a horizontal segment is detected as contact.
    """
    point = (10.0, 20.0)
    segment = ((8.0, 20.0), (12.0, 20.0))

    assert _point_touches_segment(point, segment) is True


def test_point_touches_segment_detects_contact_on_vertical_segment():
    """
    Verify that a point on a vertical segment is detected as contact.
    """
    point = (10.0, 20.0)
    segment = ((10.0, 18.0), (10.0, 22.0))

    assert _point_touches_segment(point, segment) is True


def test_point_touches_segment_detects_contact_on_sloped_segment():
    """
    Verify that a point on a 45 degree segment is detected as contact.
    """
    point = (10.0, 20.0)
    segment = ((8.0, 22.0), (12.0, 18.0))

    assert _point_touches_segment(point, segment) is True


def test_point_touches_segment_returns_false_when_point_is_far_from_segment():
    """
    Verify that a point away from the segment is not classified as contact.
    """
    point = (10.0, 20.0)
    segment = ((8.0, 23.0), (12.0, 23.0))

    assert _point_touches_segment(point, segment) is False


"""Terrain contact"""


def test_rocket_touches_terrain_returns_false_when_no_corner_touches_segment():
    """
    Verify that the rocket has no terrain contact while still above the ground.
    """
    terrain = Terrain()
    rocket = Rocket()
    corners = _get_rocket_corners(rocket)

    assert _rocket_touches_terrain(corners, terrain.get_segments()) is False


def test_rocket_touches_terrain_returns_true_when_bottom_corner_touches_segment():
    """
    Verify that terrain contact is detected when a bottom corner reaches the ground.
    """
    terrain = Terrain()
    rocket = create_rocket_touching_horizontal_segment(center_x=42.0, segment_y=54.0)
    corners = _get_rocket_corners(rocket)

    assert _rocket_touches_terrain(corners, terrain.get_segments()) is True


def test_get_terrain_contact_corner_returns_first_colliding_corner():
    """
    Verify that the terrain contact helper returns the first detected contact corner.
    """
    terrain = Terrain()
    rocket = create_rocket_touching_horizontal_segment(center_x=39.0, segment_y=54.0)

    contact_corner = get_terrain_contact_corner(rocket, terrain)

    assert contact_corner == pytest.approx((40.1, 54.0))


"""Landing pad and landing conditions"""


def test_collision_is_on_landing_pad_returns_true_for_pad_contact():
    """
    Verify that pad contact is detected when the rocket touches the landing pad.
    """
    terrain = Terrain()
    rocket = create_rocket_touching_horizontal_segment(
        center_x=(terrain.landing_pad_x_min + terrain.landing_pad_x_max) / 2,
        segment_y=terrain.landing_pad_y,
    )
    corners = _get_rocket_corners(rocket)

    assert _collision_is_on_landing_pad(corners, terrain) is True


def test_collision_is_on_landing_pad_returns_false_for_non_pad_contact():
    """
    Verify that ordinary terrain contact is not misclassified as landing-pad contact.
    """
    terrain = Terrain()
    rocket = create_rocket_touching_horizontal_segment(center_x=42.0, segment_y=54.0)
    corners = _get_rocket_corners(rocket)

    assert _collision_is_on_landing_pad(corners, terrain) is False


def test_meets_landing_conditions_returns_true_for_safe_landing_state():
    """
    Verify that a stable, upright rocket satisfies the landing limits.
    """
    rocket = Rocket()
    rocket.velocity_x = MAX_LANDING_HORIZONTAL_SPEED
    rocket.velocity_y = MAX_LANDING_VERTICAL_SPEED
    rocket.angle = MAX_LANDING_ANGLE
    rocket.angular_velocity = MAX_LANDING_ANGULAR_VELOCITY

    assert _meets_landing_conditions(rocket) is True


def test_meets_landing_conditions_allows_full_rotations_before_touchdown():
    """
    Verify that the landing angle check accepts upright orientations after full loops.
    """
    rocket = Rocket()
    rocket.angle = 2 * math.pi + 0.1

    assert _meets_landing_conditions(rocket) is True


def test_meets_landing_conditions_returns_false_for_excessive_vertical_speed():
    """
    Verify that too high vertical speed makes the landing unsafe.
    """
    rocket = Rocket()
    rocket.velocity_y = MAX_LANDING_VERTICAL_SPEED + 0.1

    assert _meets_landing_conditions(rocket) is False


def test_meets_landing_conditions_returns_false_for_excessive_horizontal_speed():
    """
    Verify that too high horizontal speed makes the landing unsafe.
    """
    rocket = Rocket()
    rocket.velocity_x = MAX_LANDING_HORIZONTAL_SPEED + 0.1

    assert _meets_landing_conditions(rocket) is False


def test_meets_landing_conditions_returns_false_for_excessive_angle():
    """
    Verify that too large tilt angle makes the landing unsafe.
    """
    rocket = Rocket()
    rocket.angle = MAX_LANDING_ANGLE + 0.1

    assert _meets_landing_conditions(rocket) is False


def test_meets_landing_conditions_returns_false_for_excessive_angular_velocity():
    """
    Verify that too high angular velocity makes the landing unsafe.
    """
    rocket = Rocket()
    rocket.angular_velocity = MAX_LANDING_ANGULAR_VELOCITY + 0.1

    assert _meets_landing_conditions(rocket) is False


"""Status evaluation"""


def test_evaluate_rocket_status_returns_running_when_no_contact_exists():
    """
    Verify that the rocket remains running while flying above the terrain.
    """
    terrain = Terrain()
    rocket = Rocket()

    assert evaluate_rocket_status(rocket, terrain) == "running"


def test_evaluate_rocket_status_returns_crashed_when_rocket_is_out_of_bounds():
    """
    Verify that leaving the world bounds gives crashed status.
    """
    terrain = Terrain()
    rocket = Rocket()
    rocket.x = 0.5

    assert evaluate_rocket_status(rocket, terrain) == "crashed"


def test_evaluate_rocket_status_returns_crashed_for_non_pad_terrain_contact():
    """
    Verify that terrain contact outside the landing pad gives crashed status.
    """
    terrain = Terrain()
    rocket = create_rocket_touching_horizontal_segment(center_x=42.0, segment_y=54.0)

    assert evaluate_rocket_status(rocket, terrain) == "crashed"


def test_evaluate_rocket_status_returns_landed_for_safe_pad_contact():
    """
    Verify that safe contact on the landing pad gives landed status.
    """
    terrain = Terrain()
    rocket = create_rocket_touching_horizontal_segment(
        center_x=(terrain.landing_pad_x_min + terrain.landing_pad_x_max) / 2,
        segment_y=terrain.landing_pad_y,
    )

    assert evaluate_rocket_status(rocket, terrain) == "landed"


def test_evaluate_rocket_status_returns_crashed_for_unsafe_pad_contact():
    """
    Verify that unsafe contact on the landing pad still gives crashed status.
    """
    terrain = Terrain()
    rocket = create_rocket_touching_horizontal_segment(
        center_x=(terrain.landing_pad_x_min + terrain.landing_pad_x_max) / 2,
        segment_y=terrain.landing_pad_y,
    )
    rocket.velocity_y = MAX_LANDING_VERTICAL_SPEED + 0.1

    assert evaluate_rocket_status(rocket, terrain) == "crashed"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
