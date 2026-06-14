from pathlib import Path
import math
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src" / "rocket")) # Lägger till mappen rocket i pythons sökvägar så vi kan importera från den

from config import (
    GRAVITY, 
    LEFT_ENGINE_FORCE, 
    MAIN_ENGINE_FORCE, 
    RIGHT_ENGINE_FORCE, 
    ROCKET_HEIGHT, 
    ROCKET_MASS, 
    ROCKET_WIDTH,
)
from physics import (
    calculate_moment_of_inertia, 
    update_rocket_rotation, 
    update_rocket_translation,
)
from rocket import Rocket


def create_actions(main_engine=False, left_engine=False, right_engine=False):
    """
    Create an actions dictionary with optional engine inputs.
    """
    return {
        "main_engine": main_engine,
        "left_engine": left_engine,
        "right_engine": right_engine,
    }


def test_calculate_moment_of_inertia_returns_expected_value_for_default_rocket():
    """
    Verify that the default rocket gets the expected moment of inertia.
    """
    rocket = Rocket()

    expected_moment_of_inertia = ROCKET_MASS * (ROCKET_WIDTH ** 2 + ROCKET_HEIGHT ** 2) / 12

    actual_moment_of_inertia = calculate_moment_of_inertia(rocket)

    assert actual_moment_of_inertia == pytest.approx(expected_moment_of_inertia) # pytest.approx innebär tillräckligt nära förväntat värde, hade fungerat utan här


def test_calculate_moment_of_inertia_scales_linearly_with_mass():
    """
    Verify that the moment of inertia increases linearly with rocket mass.
    """
    rocket = Rocket()
    rocket.mass = 2.5

    expected_moment_of_inertia = rocket.mass * (ROCKET_WIDTH ** 2 + ROCKET_HEIGHT ** 2) / 12

    actual_moment_of_inertia = calculate_moment_of_inertia(rocket)

    assert actual_moment_of_inertia == pytest.approx(expected_moment_of_inertia)


"""TRANSLATIONS TESTER"""


def test_update_rocket_translation_applies_gravity_when_no_engines_are_active():
    """
    Verify that gravity alone increases the rocket's downward velocity.
    """
    rocket = Rocket()

    update_rocket_translation(rocket, create_actions(), dt=0.1)

    assert rocket.velocity_x == pytest.approx(0.0)
    assert rocket.velocity_y == pytest.approx(GRAVITY * 0.1)


def test_update_rocket_translation_moves_rocket_downward_under_gravity():
    """
    Verify that gravity alone moves the rocket downward over one time step.
    """
    rocket = Rocket()
    initial_y = rocket.y

    update_rocket_translation(rocket, create_actions(), dt=0.1)

    expected_y = initial_y + (GRAVITY * 0.1) * 0.1

    assert rocket.y == pytest.approx(expected_y)


def test_update_rocket_translation_main_engine_accelerates_upward_at_zero_angle():
    """
    Verify that the main engine produces upward acceleration when the rocket angle is zero.
    """
    rocket = Rocket()

    update_rocket_translation(rocket, create_actions(main_engine=True), dt=0.1)

    expected_velocity_y = (GRAVITY - MAIN_ENGINE_FORCE / rocket.mass) * 0.1

    assert rocket.velocity_x == pytest.approx(0.0)
    assert rocket.velocity_y == pytest.approx(expected_velocity_y)


def test_update_rocket_translation_main_engine_splits_force_into_x_and_y_components():
    """
    Verify that the main engine force is split into x and y components at a non-zero angle.
    """
    rocket = Rocket()
    rocket.angle = math.pi / 6

    update_rocket_translation(rocket, create_actions(main_engine=True), dt=0.1)

    expected_velocity_x = (-MAIN_ENGINE_FORCE * math.sin(rocket.angle) / rocket.mass) * 0.1
    expected_velocity_y = (GRAVITY - MAIN_ENGINE_FORCE * math.cos(rocket.angle) / rocket.mass) * 0.1

    assert rocket.velocity_x == pytest.approx(expected_velocity_x)
    assert rocket.velocity_y == pytest.approx(expected_velocity_y)


def test_update_rocket_translation_side_engines_produce_sideways_motion_at_zero_angle():
    """
    Verify that the side engines produce horizontal translation when the rocket angle is zero.
    """
    left_rocket = Rocket()
    right_rocket = Rocket()

    update_rocket_translation(left_rocket, create_actions(left_engine=True), dt=0.1)
    update_rocket_translation(right_rocket, create_actions(right_engine=True), dt=0.1)

    expected_left_velocity_x = (LEFT_ENGINE_FORCE / left_rocket.mass) * 0.1
    expected_right_velocity_x = (-RIGHT_ENGINE_FORCE / right_rocket.mass) * 0.1

    assert left_rocket.velocity_x == pytest.approx(expected_left_velocity_x)
    assert right_rocket.velocity_x == pytest.approx(expected_right_velocity_x)


def test_update_rocket_translation_side_engines_split_force_into_x_and_y_components():
    """
    Verify that the side engine forces are split into x and y components at a non-zero angle.
    """
    left_rocket = Rocket()
    right_rocket = Rocket()

    left_rocket.angle = math.pi / 6
    right_rocket.angle = math.pi / 6

    update_rocket_translation(left_rocket, create_actions(left_engine=True), dt=0.1)
    update_rocket_translation(right_rocket, create_actions(right_engine=True), dt=0.1)

    expected_left_velocity_x = (LEFT_ENGINE_FORCE * math.cos(left_rocket.angle) / left_rocket.mass) * 0.1
    expected_left_velocity_y = (GRAVITY - LEFT_ENGINE_FORCE * math.sin(left_rocket.angle) / left_rocket.mass) * 0.1

    expected_right_velocity_x = (-RIGHT_ENGINE_FORCE * math.cos(right_rocket.angle) / right_rocket.mass) * 0.1
    expected_right_velocity_y = (GRAVITY + RIGHT_ENGINE_FORCE * math.sin(right_rocket.angle) / right_rocket.mass) * 0.1

    assert left_rocket.velocity_x == pytest.approx(expected_left_velocity_x)
    assert left_rocket.velocity_y == pytest.approx(expected_left_velocity_y)
    assert right_rocket.velocity_x == pytest.approx(expected_right_velocity_x)
    assert right_rocket.velocity_y == pytest.approx(expected_right_velocity_y)


def test_update_rocket_translation_main_engine_and_right_engine_at_zero_angle():
    """
    Verify that the main engine and right engine combine correctly when the rocket angle is zero.
    """
    rocket = Rocket()

    update_rocket_translation(
        rocket,
        create_actions(main_engine=True, right_engine=True),
        dt=0.1,
    )

    expected_velocity_x = (-RIGHT_ENGINE_FORCE / rocket.mass) * 0.1
    expected_velocity_y = (GRAVITY - MAIN_ENGINE_FORCE / rocket.mass) * 0.1

    assert rocket.velocity_x == pytest.approx(expected_velocity_x)
    assert rocket.velocity_y == pytest.approx(expected_velocity_y)


def test_update_rocket_translation_main_engine_and_left_engine_at_non_zero_angle():
    """
    Verify that the main engine and left engine combine correctly at a non-zero rocket angle.
    """
    rocket = Rocket()
    rocket.angle = math.pi / 6

    update_rocket_translation(
        rocket,
        create_actions(main_engine=True, left_engine=True),
        dt=0.1,
    )

    expected_force_x = (
        -MAIN_ENGINE_FORCE * math.sin(rocket.angle)
        + LEFT_ENGINE_FORCE * math.cos(rocket.angle)
    )
    expected_force_y = (
        rocket.mass * GRAVITY
        - MAIN_ENGINE_FORCE * math.cos(rocket.angle)
        - LEFT_ENGINE_FORCE * math.sin(rocket.angle)
    )

    expected_velocity_x = (expected_force_x / rocket.mass) * 0.1
    expected_velocity_y = (expected_force_y / rocket.mass) * 0.1

    assert rocket.velocity_x == pytest.approx(expected_velocity_x)
    assert rocket.velocity_y == pytest.approx(expected_velocity_y)


def test_update_rocket_translation_left_and_right_engines_cancel_horizontal_motion_at_zero_angle():
    """
    Verify that the left and right engines cancel horizontal motion when the rocket angle is zero.
    """
    rocket = Rocket()

    update_rocket_translation(
        rocket,
        create_actions(left_engine=True, right_engine=True),
        dt=0.1,
    )

    assert rocket.velocity_x == pytest.approx(0.0)


"""ROTATION TESTER"""


def test_update_rocket_rotation_left_engine_produces_positive_angular_velocity():
    """
    Verify that the left engine produces positive angular velocity.
    """
    rocket = Rocket()

    update_rocket_rotation(rocket, create_actions(left_engine=True), dt=0.1)

    assert rocket.angular_velocity > 0.0


def test_update_rocket_rotation_right_engine_produces_negative_angular_velocity():
    """
    Verify that the right engine produces negative angular velocity.
    """
    rocket = Rocket()

    update_rocket_rotation(rocket, create_actions(right_engine=True), dt=0.1)

    assert rocket.angular_velocity < 0.0


def test_update_rocket_rotation_left_engine_matches_expected_angular_velocity():
    """
    Verify that the left engine gives the expected angular velocity after one time step.
    """
    rocket = Rocket()

    update_rocket_rotation(rocket, create_actions(left_engine=True), dt=0.1)

    expected_moment_of_inertia = calculate_moment_of_inertia(rocket)
    expected_torque = LEFT_ENGINE_FORCE * (ROCKET_HEIGHT / 2)
    expected_angular_acceleration = expected_torque / expected_moment_of_inertia
    expected_angular_velocity = expected_angular_acceleration * 0.1

    assert rocket.angular_velocity == pytest.approx(expected_angular_velocity)


def test_update_rocket_rotation_right_engine_matches_expected_angular_velocity():
    """
    Verify that the right engine gives the expected angular velocity after one time step.
    """
    rocket = Rocket()

    update_rocket_rotation(rocket, create_actions(right_engine=True), dt=0.1)

    expected_moment_of_inertia = calculate_moment_of_inertia(rocket)
    expected_torque = -RIGHT_ENGINE_FORCE * (ROCKET_HEIGHT / 2)
    expected_angular_acceleration = expected_torque / expected_moment_of_inertia
    expected_angular_velocity = expected_angular_acceleration * 0.1

    assert rocket.angular_velocity == pytest.approx(expected_angular_velocity)


def test_update_rocket_rotation_updates_angle_from_angular_velocity():
    """
    Verify that the rocket angle is updated from the new angular velocity.
    """
    rocket = Rocket()

    update_rocket_rotation(rocket, create_actions(left_engine=True), dt=0.1)

    expected_moment_of_inertia = calculate_moment_of_inertia(rocket)
    expected_torque = LEFT_ENGINE_FORCE * (ROCKET_HEIGHT / 2)
    expected_angular_acceleration = expected_torque / expected_moment_of_inertia
    expected_angular_velocity = expected_angular_acceleration * 0.1
    expected_angle = expected_angular_velocity * 0.1

    assert rocket.angle == pytest.approx(expected_angle)


def test_update_rocket_rotation_main_engine_does_not_affect_angular_motion():
    """
    Verify that the main engine does not change the rocket's angular motion.
    """
    rocket = Rocket()

    update_rocket_rotation(rocket, create_actions(main_engine=True), dt=0.1)

    assert rocket.angular_velocity == pytest.approx(0.0)
    assert rocket.angle == pytest.approx(0.0)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__])) # Avslutar programmet med exitkoden från pytest.main som anger om allt gick igenom eller inte
