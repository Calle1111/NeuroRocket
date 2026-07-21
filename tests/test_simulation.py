from pathlib import Path
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src" / "rocket")) # Lägger till mappen rocket i pythons sökvägar så vi kan importera från den

from config import PIXELS_PER_METER, ROCKET_HEIGHT, ROCKET_WIDTH, WINDOW_WIDTH
from rocket import Rocket
from simulation import Simulation
from terrain import TERRAIN_TEMPLATE_COUNT


def create_actions(main_engine=False, left_engine=False, right_engine=False):
    """
    Create an actions dictionary with optional engine inputs.
    """
    return {
        "main_engine": main_engine,
        "left_engine": left_engine,
        "right_engine": right_engine,
    }


def assert_rocket_spawn_is_within_allowed_area(simulation):
    """
    Verify that the rocket spawn keeps all corners within the required margins.
    """
    world_margin = 2.0
    terrain_margin = 2.0

    half_rocket_width = ROCKET_WIDTH / 2
    half_rocket_height = ROCKET_HEIGHT / 2
    world_width_meters = WINDOW_WIDTH / PIXELS_PER_METER
    highest_terrain_y = min(y for _, y in simulation.terrain.terrain_points)

    minimum_spawn_x = world_margin + half_rocket_width
    maximum_spawn_x = world_width_meters - world_margin - half_rocket_width

    minimum_spawn_y = world_margin + half_rocket_height
    maximum_spawn_y = highest_terrain_y - terrain_margin - half_rocket_height

    tolerance = 1e-9

    assert simulation.rocket.x >= minimum_spawn_x - tolerance
    assert simulation.rocket.x <= maximum_spawn_x + tolerance
    assert simulation.rocket.y >= minimum_spawn_y - tolerance
    assert simulation.rocket.y <= maximum_spawn_y + tolerance


def test_simulation_initializes_with_a_rocket():
    """
    Verify that a new simulation creates and owns a Rocket object.
    """
    simulation = Simulation()

    assert isinstance(simulation.rocket, Rocket)


def test_simulation_initializes_with_running_status():
    """
    Verify that a new simulation starts in the running state.
    """
    simulation = Simulation()

    assert simulation.status == "running"


def test_simulation_initial_spawn_is_within_allowed_area():
    """
    Verify that a new simulation spawns the rocket within the allowed margins.
    """
    simulation = Simulation()

    assert_rocket_spawn_is_within_allowed_area(simulation)


def test_simulation_update_changes_rocket_translation_state():
    """
    Verify that simulation update changes the rocket's translational state.
    """
    simulation = Simulation()
    initial_y = simulation.rocket.y
    initial_velocity_y = simulation.rocket.velocity_y

    simulation.update(dt=0.1, actions=create_actions())

    assert simulation.rocket.y != pytest.approx(initial_y)
    assert simulation.rocket.velocity_y != pytest.approx(initial_velocity_y)


def test_simulation_update_changes_rocket_rotation_state():
    """
    Verify that simulation update changes the rocket's rotational state.
    """
    simulation = Simulation()
    initial_angle = simulation.rocket.angle
    initial_angular_velocity = simulation.rocket.angular_velocity

    simulation.update(dt=0.1, actions=create_actions(left_engine=True))

    assert simulation.rocket.angle != pytest.approx(initial_angle)
    assert simulation.rocket.angular_velocity != pytest.approx(initial_angular_velocity)

def test_simulation_reset_restores_rocket_to_default_state():
    """
    Verify that reset restores the rocket's default physical state.
    """
    simulation = Simulation()

    simulation.rocket.x = 12.0
    simulation.rocket.y = 18.0
    simulation.rocket.velocity_x = 3.0
    simulation.rocket.velocity_y = -4.0
    simulation.rocket.angle = 0.7
    simulation.rocket.angular_velocity = -0.2
    simulation.rocket.fuel_mass = 5.0

    simulation.reset()

    assert simulation.rocket.velocity_x == pytest.approx(0.0)
    assert simulation.rocket.velocity_y == pytest.approx(0.0)
    assert simulation.rocket.angle == pytest.approx(0.0)
    assert simulation.rocket.angular_velocity == pytest.approx(0.0)
    assert simulation.rocket.fuel_mass == pytest.approx(simulation.rocket.max_fuel_mass)
    assert_rocket_spawn_is_within_allowed_area(simulation)


def test_simulation_reset_restores_running_status():
    """
    Verify that reset restores the simulation status to running.
    """
    simulation = Simulation()
    simulation.status = "crashed"

    simulation.reset()

    assert simulation.status == "running"


def test_simulation_reset_clears_active_engine_actions():
    """
    Verify that reset clears the renderer-facing active engine state.
    """
    simulation = Simulation()

    simulation.update(
        dt=0.1,
        actions=create_actions(main_engine=True, left_engine=True),
    )

    simulation.reset()

    assert simulation.active_engine_actions == {
        "main_engine": False,
        "left_engine": False,
        "right_engine": False,
    }

def test_simulation_reset_replaces_the_old_rocket_instance():
    """
    Verify that reset creates a new rocket object instead of mutating the old one in place.
    """
    simulation = Simulation()
    old_rocket = simulation.rocket

    simulation.update(dt=0.1, actions=create_actions(main_engine=True))
    simulation.reset()

    assert simulation.rocket is not old_rocket
    assert isinstance(simulation.rocket, Rocket)


def test_simulation_reset_random_spawn_is_within_allowed_area():
    """
    Verify that reset randomizes a rocket spawn that still respects all margins.
    """
    simulation = Simulation()

    simulation.reset()

    assert_rocket_spawn_is_within_allowed_area(simulation)


@pytest.mark.parametrize("template_id", range(TERRAIN_TEMPLATE_COUNT))
def test_simulation_reset_spawn_is_within_allowed_area_for_each_template(template_id):
    """
    Verify that each terrain template can spawn the rocket within the allowed area.
    """
    simulation = Simulation()

    simulation.reset(template_id=template_id)

    assert simulation.current_template_id == template_id
    assert_rocket_spawn_is_within_allowed_area(simulation)


def test_simulation_update_sets_crashed_status_after_non_pad_terrain_contact():
    """
    Verify that simulation status becomes crashed after contact with ordinary terrain.
    """
    simulation = Simulation()
    simulation.rocket.x = 42.0
    simulation.rocket.y = 54.0 - ROCKET_HEIGHT / 2
    simulation.rocket.angle = 0.0

    simulation.update(dt=0.0, actions=create_actions())

    assert simulation.status == "crashed"


def test_simulation_update_sets_landed_status_after_safe_pad_contact():
    """
    Verify that simulation status becomes landed after safe contact on the landing pad.
    """
    simulation = Simulation()
    simulation.rocket.x = (
        simulation.terrain.landing_pad_x_min + simulation.terrain.landing_pad_x_max
    ) / 2
    simulation.rocket.y = simulation.terrain.landing_pad_y - ROCKET_HEIGHT / 2
    simulation.rocket.angle = 0.0

    simulation.update(dt=0.0, actions=create_actions())

    assert simulation.status == "landed"


def test_simulation_update_freezes_rocket_state_after_crash():
    """
    Verify that the rocket state no longer changes after the simulation has crashed.
    """
    simulation = Simulation()
    simulation.rocket.x = 42.0
    simulation.rocket.y = 54.0 - ROCKET_HEIGHT / 2
    simulation.rocket.angle = 0.0

    simulation.update(dt=0.0, actions=create_actions())

    crashed_x = simulation.rocket.x
    crashed_y = simulation.rocket.y
    crashed_velocity_x = simulation.rocket.velocity_x
    crashed_velocity_y = simulation.rocket.velocity_y
    crashed_angle = simulation.rocket.angle
    crashed_angular_velocity = simulation.rocket.angular_velocity
    crashed_fuel_mass = simulation.rocket.fuel_mass

    simulation.update(dt=0.1, actions=create_actions(main_engine=True, left_engine=True))

    assert simulation.status == "crashed"
    assert simulation.rocket.x == pytest.approx(crashed_x)
    assert simulation.rocket.y == pytest.approx(crashed_y)
    assert simulation.rocket.velocity_x == pytest.approx(crashed_velocity_x)
    assert simulation.rocket.velocity_y == pytest.approx(crashed_velocity_y)
    assert simulation.rocket.angle == pytest.approx(crashed_angle)
    assert simulation.rocket.angular_velocity == pytest.approx(crashed_angular_velocity)
    assert simulation.rocket.fuel_mass == pytest.approx(crashed_fuel_mass)


def test_simulation_update_clears_active_engine_actions_after_crash():
    """
    Verify that renderer-facing engine actions are turned off immediately after a crash.
    """
    simulation = Simulation()
    simulation.rocket.x = 42.0
    simulation.rocket.y = 54.0 - ROCKET_HEIGHT / 2
    simulation.rocket.angle = 0.0

    simulation.update(dt=0.0, actions=create_actions(main_engine=True, left_engine=True))

    assert simulation.status == "crashed"
    assert simulation.active_engine_actions == {
        "main_engine": False,
        "left_engine": False,
        "right_engine": False,
    }


def test_simulation_update_clears_active_engine_actions_after_landing():
    """
    Verify that renderer-facing engine actions are turned off immediately after a landing.
    """
    simulation = Simulation()
    simulation.rocket.x = (
        simulation.terrain.landing_pad_x_min + simulation.terrain.landing_pad_x_max
    ) / 2
    simulation.rocket.y = simulation.terrain.landing_pad_y - ROCKET_HEIGHT / 2
    simulation.rocket.angle = 0.0

    simulation.update(dt=0.0, actions=create_actions(main_engine=True))

    assert simulation.status == "landed"
    assert simulation.active_engine_actions == {
        "main_engine": False,
        "left_engine": False,
        "right_engine": False,
    }

if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__])) # Avslutar programmet med exitkoden från pytest.main som anger om allt gick igenom eller inte
