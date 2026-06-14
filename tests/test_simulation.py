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


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__])) # Avslutar programmet med exitkoden från pytest.main som anger om allt gick igenom eller inte
