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
    ROCKET_DRY_MASS,
    ROCKET_MAX_FUEL_MASS,
    ROCKET_WIDTH,
    MAIN_ENGINE_FUEL_BURN_RATE,
    SIDE_ENGINE_FUEL_BURN_RATE,
)
from physics import (
    _calculate_moment_of_inertia,
    update_rocket_rotation, 
    update_rocket_translation,
    update_rocket_fuel_mass,
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


"""Moment of inertia"""


def test_calculate_moment_of_inertia_returns_expected_value_for_default_rocket():
    """
    Verify that the default rocket gets the expected moment of inertia.
    """
    rocket = Rocket()

    expected_moment_of_inertia = (
        (ROCKET_DRY_MASS + ROCKET_MAX_FUEL_MASS)
        * (ROCKET_WIDTH ** 2 + ROCKET_HEIGHT ** 2)
        / 12
    )

    actual_moment_of_inertia = _calculate_moment_of_inertia(rocket)

    assert actual_moment_of_inertia == pytest.approx(expected_moment_of_inertia) # pytest.approx innebär tillräckligt nära förväntat värde, hade fungerat utan här


def test_calculate_moment_of_inertia_scales_linearly_with_mass():
    """
    Verify that the moment of inertia increases linearly with rocket mass.
    """
    rocket = Rocket()
    rocket.dry_mass = 2.0
    rocket.fuel_mass = 0.5

    expected_moment_of_inertia = rocket.mass() * (ROCKET_WIDTH ** 2 + ROCKET_HEIGHT ** 2) / 12

    actual_moment_of_inertia = _calculate_moment_of_inertia(rocket)

    assert actual_moment_of_inertia == pytest.approx(expected_moment_of_inertia)


"""Translation"""


def test_update_rocket_translation_applies_gravity_when_no_engines_are_active():
    """
    Verify that gravity alone increases the rocket's downward velocity.
    """
    rocket = Rocket()

    update_rocket_translation(rocket, create_actions(), dt=0.1, burn_fraction=0.0)

    assert rocket.velocity_x == pytest.approx(0.0)
    assert rocket.velocity_y == pytest.approx(GRAVITY * 0.1)


def test_update_rocket_translation_moves_rocket_downward_under_gravity():
    """
    Verify that gravity alone moves the rocket downward over one time step with no engines active.
    """
    rocket = Rocket()
    initial_y = rocket.y

    update_rocket_translation(rocket, create_actions(), dt=0.1, burn_fraction=0.0)

    expected_y = initial_y + (GRAVITY * 0.1) * 0.1

    assert rocket.y == pytest.approx(expected_y)


def test_update_rocket_translation_main_engine_accelerates_upward_at_zero_angle():
    """
    Verify that the main engine produces upward acceleration when the rocket angle is zero.
    """
    rocket = Rocket()

    update_rocket_translation(
        rocket,
        create_actions(main_engine=True),
        dt=0.1,
        burn_fraction=1.0,
    )

    expected_velocity_y = (GRAVITY - MAIN_ENGINE_FORCE / rocket.mass()) * 0.1

    assert rocket.velocity_x == pytest.approx(0.0)
    assert rocket.velocity_y == pytest.approx(expected_velocity_y)


def test_update_rocket_translation_main_engine_splits_force_into_x_and_y_components():
    """
    Verify that the main engine force is split into x and y components at a non-zero angle.
    """
    rocket = Rocket()
    rocket.angle = math.pi / 6

    update_rocket_translation(
        rocket,
        create_actions(main_engine=True),
        dt=0.1,
        burn_fraction=1.0,
    )

    expected_velocity_x = (-MAIN_ENGINE_FORCE * math.sin(rocket.angle) / rocket.mass()) * 0.1
    expected_velocity_y = (GRAVITY - MAIN_ENGINE_FORCE * math.cos(rocket.angle) / rocket.mass()) * 0.1

    assert rocket.velocity_x == pytest.approx(expected_velocity_x)
    assert rocket.velocity_y == pytest.approx(expected_velocity_y)


def test_update_rocket_translation_side_engines_produce_sideways_motion_at_zero_angle():
    """
    Verify that the side engines produce horizontal translation when the rocket angle is zero.
    """
    left_rocket = Rocket()
    right_rocket = Rocket()

    update_rocket_translation(left_rocket, create_actions(left_engine=True), dt=0.1, burn_fraction=1.0)
    update_rocket_translation(right_rocket, create_actions(right_engine=True), dt=0.1, burn_fraction=1.0)

    expected_left_velocity_x = (LEFT_ENGINE_FORCE / left_rocket.mass()) * 0.1
    expected_right_velocity_x = (-RIGHT_ENGINE_FORCE / right_rocket.mass()) * 0.1

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

    update_rocket_translation(left_rocket, create_actions(left_engine=True), dt=0.1, burn_fraction=1.0)
    update_rocket_translation(right_rocket, create_actions(right_engine=True), dt=0.1, burn_fraction=1.0)

    expected_left_velocity_x = (LEFT_ENGINE_FORCE * math.cos(left_rocket.angle) / left_rocket.mass()) * 0.1
    expected_left_velocity_y = (GRAVITY - LEFT_ENGINE_FORCE * math.sin(left_rocket.angle) / left_rocket.mass()) * 0.1

    expected_right_velocity_x = (-RIGHT_ENGINE_FORCE * math.cos(right_rocket.angle) / right_rocket.mass()) * 0.1
    expected_right_velocity_y = (GRAVITY + RIGHT_ENGINE_FORCE * math.sin(right_rocket.angle) / right_rocket.mass()) * 0.1

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
        burn_fraction=1.0,
    )

    expected_velocity_x = (-RIGHT_ENGINE_FORCE / rocket.mass()) * 0.1
    expected_velocity_y = (GRAVITY - MAIN_ENGINE_FORCE / rocket.mass()) * 0.1

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
        burn_fraction=1.0,
    )

    expected_force_x = (
        -MAIN_ENGINE_FORCE * math.sin(rocket.angle)
        + LEFT_ENGINE_FORCE * math.cos(rocket.angle)
    )
    expected_force_y = (
        rocket.mass() * GRAVITY
        - MAIN_ENGINE_FORCE * math.cos(rocket.angle)
        - LEFT_ENGINE_FORCE * math.sin(rocket.angle)
    )

    expected_velocity_x = (expected_force_x / rocket.mass()) * 0.1
    expected_velocity_y = (expected_force_y / rocket.mass()) * 0.1

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
        burn_fraction=1.0,
    )

    assert rocket.velocity_x == pytest.approx(0.0)


"""Rotation"""


def test_update_rocket_rotation_left_engine_produces_positive_angular_velocity():
    """
    Verify that the left engine produces positive angular velocity.
    """
    rocket = Rocket()

    update_rocket_rotation(rocket, create_actions(left_engine=True), dt=0.1, burn_fraction=1.0)

    assert rocket.angular_velocity > 0.0


def test_update_rocket_rotation_right_engine_produces_negative_angular_velocity():
    """
    Verify that the right engine produces negative angular velocity.
    """
    rocket = Rocket()

    update_rocket_rotation(rocket, create_actions(right_engine=True), dt=0.1, burn_fraction=1.0)

    assert rocket.angular_velocity < 0.0


def test_update_rocket_rotation_left_engine_matches_expected_angular_velocity():
    """
    Verify that the left engine gives the expected angular velocity after one time step.
    """
    rocket = Rocket()

    update_rocket_rotation(rocket, create_actions(left_engine=True), dt=0.1, burn_fraction=1.0)

    expected_moment_of_inertia = _calculate_moment_of_inertia(rocket)
    expected_torque = LEFT_ENGINE_FORCE * (ROCKET_HEIGHT / 2)
    expected_angular_acceleration = expected_torque / expected_moment_of_inertia
    expected_angular_velocity = expected_angular_acceleration * 0.1

    assert rocket.angular_velocity == pytest.approx(expected_angular_velocity)


def test_update_rocket_rotation_right_engine_matches_expected_angular_velocity():
    """
    Verify that the right engine gives the expected angular velocity after one time step.
    """
    rocket = Rocket()

    update_rocket_rotation(rocket, create_actions(right_engine=True), dt=0.1, burn_fraction=1.0)

    expected_moment_of_inertia = _calculate_moment_of_inertia(rocket)
    expected_torque = -RIGHT_ENGINE_FORCE * (ROCKET_HEIGHT / 2)
    expected_angular_acceleration = expected_torque / expected_moment_of_inertia
    expected_angular_velocity = expected_angular_acceleration * 0.1

    assert rocket.angular_velocity == pytest.approx(expected_angular_velocity)


def test_update_rocket_rotation_updates_angle_from_angular_velocity():
    """
    Verify that the rocket angle is updated from the new angular velocity.
    """
    rocket = Rocket()

    update_rocket_rotation(rocket, create_actions(left_engine=True), dt=0.1, burn_fraction=1.0)

    expected_moment_of_inertia = _calculate_moment_of_inertia(rocket)
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

    update_rocket_rotation(rocket, create_actions(main_engine=True), dt=0.1, burn_fraction=1.0)

    assert rocket.angular_velocity == pytest.approx(0.0)
    assert rocket.angle == pytest.approx(0.0)


"""Fuel consumtion"""


def test_update_rocket_fuel_mass_returns_zero_and_preserves_fuel_when_no_engines_are_active():
    """
    Verify that no fuel is consumed when no engines are active.
    """
    rocket = Rocket()
    initial_fuel_mass = rocket.fuel_mass

    burn_fraction = update_rocket_fuel_mass(rocket, create_actions(), dt=0.1)

    assert burn_fraction == pytest.approx(0.0)
    assert rocket.fuel_mass == pytest.approx(initial_fuel_mass)

def test_update_rocket_fuel_mass_consumes_main_engine_fuel_when_enough_fuel_exists():
    """
    Verify that the main engine consumes fuel and returns full burn fraction.
    """
    rocket = Rocket()
    initial_fuel_mass = rocket.fuel_mass

    burn_fraction = update_rocket_fuel_mass(
        rocket,
        create_actions(main_engine=True),
        dt=0.1,
    )

    expected_fuel_mass = initial_fuel_mass - MAIN_ENGINE_FUEL_BURN_RATE * 0.1

    assert burn_fraction == pytest.approx(1.0)
    assert rocket.fuel_mass == pytest.approx(expected_fuel_mass)


def test_update_rocket_fuel_mass_combines_multiple_engine_burn_rates():
    """
    Verify that multiple active engines consume the sum of their burn rates.
    """
    rocket = Rocket()
    initial_fuel_mass = rocket.fuel_mass

    burn_fraction = update_rocket_fuel_mass(
        rocket,
        create_actions(main_engine=True, left_engine=True, right_engine=True),
        dt=0.1,
    )

    total_burn_rate = MAIN_ENGINE_FUEL_BURN_RATE + 2 * SIDE_ENGINE_FUEL_BURN_RATE
    expected_fuel_mass = initial_fuel_mass - total_burn_rate * 0.1

    assert burn_fraction == pytest.approx(1.0)
    assert rocket.fuel_mass == pytest.approx(expected_fuel_mass)

def test_update_rocket_fuel_mass_returns_partial_burn_fraction_when_fuel_runs_out_mid_step():
    """
    Verify that a partial burn fraction is returned when fuel runs out mid-step.
    """
    rocket = Rocket()
    rocket.fuel_mass = 0.2

    burn_fraction = update_rocket_fuel_mass(
        rocket,
        create_actions(main_engine=True),
        dt=0.1,
    )

    required_fuel_mass = MAIN_ENGINE_FUEL_BURN_RATE * 0.1
    expected_burn_fraction = 0.2 / required_fuel_mass

    assert burn_fraction == pytest.approx(expected_burn_fraction)
    assert rocket.fuel_mass == pytest.approx(0.0)

def test_update_rocket_fuel_mass_never_makes_fuel_negative():
    """
    Verify that fuel mass is clamped at zero when the required fuel exceeds what remains.
    """
    rocket = Rocket()
    rocket.fuel_mass = 0.01

    update_rocket_fuel_mass(
        rocket,
        create_actions(main_engine=True, left_engine=True, right_engine=True),
        dt=0.1,
    )

    assert rocket.fuel_mass == pytest.approx(0.0)


"""Fuel with translation"""


def test_update_rocket_translation_applies_zero_thrust_when_burn_fraction_is_zero():
    """
    Verify that active engines give no force when burn_fraction is zero.
    """

    rocket = Rocket()
    rocket.angle = 0.0

    initial_x = rocket.x
    initial_y = rocket.y
    initial_velocity_x = rocket.velocity_x
    initial_velocity_y = rocket.velocity_y

    dt = 0.1

    update_rocket_translation(
        rocket,
        create_actions(
            main_engine=True,
            left_engine=True,
            right_engine=True,
        ),
        dt=dt,
        burn_fraction=0.0,
    )

    expected_velocity_y = initial_velocity_y + GRAVITY * dt
    expected_y = initial_y + expected_velocity_y * dt

    assert rocket.velocity_x == pytest.approx(initial_velocity_x)
    assert rocket.x == pytest.approx(initial_x)
    assert rocket.velocity_y == pytest.approx(expected_velocity_y)
    assert rocket.y == pytest.approx(expected_y)

def test_update_rocket_translation_matches_manual_split_step_when_burn_fraction_is_partial():
    """
    Verify that partial burn translation matches a manual powered-step plus coast-step split.
    """
    partial_burn_rocket = Rocket()
    manual_split_rocket = Rocket()

    partial_burn_rocket.angle = math.pi / 6 # Gör testet mindre grundläggande
    manual_split_rocket.angle = math.pi / 6

    actions = create_actions(main_engine=True, left_engine=True)

    dt = 0.1
    burn_fraction = 0.4
    powered_dt = burn_fraction * dt
    coast_dt = dt - powered_dt

    update_rocket_translation(
        partial_burn_rocket,
        actions,
        dt=dt,
        burn_fraction=burn_fraction,
    )

    update_rocket_translation(
        manual_split_rocket,
        actions,
        dt=powered_dt,
        burn_fraction=1.0,
    )
    update_rocket_translation(
        manual_split_rocket,
        actions,
        dt=coast_dt,
        burn_fraction=0.0,
    )

    assert partial_burn_rocket.velocity_x == pytest.approx(manual_split_rocket.velocity_x)
    assert partial_burn_rocket.velocity_y == pytest.approx(manual_split_rocket.velocity_y)
    assert partial_burn_rocket.x == pytest.approx(manual_split_rocket.x)
    assert partial_burn_rocket.y == pytest.approx(manual_split_rocket.y)


"""Fuel with rotation"""


def test_update_rocket_rotation_applies_no_torque_when_burn_fraction_is_zero():
    """
    Verify that active side engines give no rotational effect when burn_fraction is zero.
    """
    rocket = Rocket()

    initial_angle = rocket.angle
    initial_angular_velocity = rocket.angular_velocity

    update_rocket_rotation(
        rocket,
        create_actions(left_engine=True),
        dt=0.1,
        burn_fraction=0.0,
    )

    assert rocket.angular_velocity == pytest.approx(initial_angular_velocity)
    assert rocket.angle == pytest.approx(initial_angle)

def test_update_rocket_rotation_matches_manual_split_step_when_burn_fraction_is_partial():
    """
    Verify that partial burn rotation matches a manual powered-step plus coast-step split.
    """
    partial_burn_rocket = Rocket()
    manual_split_rocket = Rocket()

    actions = create_actions(right_engine=True)

    dt = 0.1
    burn_fraction = 0.4
    powered_dt = burn_fraction * dt
    coast_dt = dt - powered_dt

    update_rocket_rotation(
        partial_burn_rocket,
        actions,
        dt=dt,
        burn_fraction=burn_fraction,
    )

    update_rocket_rotation(
        manual_split_rocket,
        actions,
        dt=powered_dt,
        burn_fraction=1.0,
    )
    update_rocket_rotation(
        manual_split_rocket,
        actions,
        dt=coast_dt,
        burn_fraction=0.0,
    )

    assert partial_burn_rocket.angular_velocity == pytest.approx(manual_split_rocket.angular_velocity)
    assert partial_burn_rocket.angle == pytest.approx(manual_split_rocket.angle)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__])) # Avslutar programmet med exitkoden från pytest.main som anger om allt gick igenom eller inte
