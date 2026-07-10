from pathlib import Path
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src" / "rocket")) # Lägger till mappen rocket i pythons sökvägar så vi kan importera från den

from rocket import Rocket
from simulation import Simulation


def create_actions(main_engine=False, left_engine=False, right_engine=False):
    """
    Create an actions dictionary with optional engine inputs.
    """
    return {
        "main_engine": main_engine,
        "left_engine": left_engine,
        "right_engine": right_engine,
    }


def test_simulation_initializes_with_a_rocket():
    """
    Verify that a new simulation creates and owns a Rocket object.
    """
    simulation = Simulation()

    assert isinstance(simulation.rocket, Rocket)


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

    assert simulation.rocket.x == pytest.approx(50.0)
    assert simulation.rocket.y == pytest.approx(35.0)
    assert simulation.rocket.velocity_x == pytest.approx(0.0)
    assert simulation.rocket.velocity_y == pytest.approx(0.0)
    assert simulation.rocket.angle == pytest.approx(0.0)
    assert simulation.rocket.angular_velocity == pytest.approx(0.0)
    assert simulation.rocket.fuel_mass == pytest.approx(simulation.rocket.max_fuel_mass)

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

if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__])) # Avslutar programmet med exitkoden från pytest.main som anger om allt gick igenom eller inte
