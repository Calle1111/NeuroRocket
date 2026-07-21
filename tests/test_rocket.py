from pathlib import Path
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src" / "rocket")) # Lägger till mappen rocket i pythons sökvägar så vi kan importera från den

from config import ROCKET_DRY_MASS, ROCKET_MAX_FUEL_MASS
from rocket import Rocket


def test_rocket_initializes_with_expected_fuel_and_mass_state():
    """
    Verify that a new rocket gets the expected default dry mass, fuel mass, and total mass.
    """
    rocket = Rocket()

    assert rocket.dry_mass == pytest.approx(ROCKET_DRY_MASS)
    assert rocket.max_fuel_mass == pytest.approx(ROCKET_MAX_FUEL_MASS)
    assert rocket.fuel_mass == pytest.approx(ROCKET_MAX_FUEL_MASS)
    assert rocket.mass() == pytest.approx(ROCKET_DRY_MASS + ROCKET_MAX_FUEL_MASS)


def test_rocket_initializes_with_expected_position():
    """
    Verify that a new rocket gets the expected default position.
    """
    rocket = Rocket()

    assert rocket.x == pytest.approx(20.0)
    assert rocket.y == pytest.approx(25.0)


def test_rocket_initializes_with_zero_translational_velocity():
    """
    Verify that a new rocket starts with zero translational velocity.
    """
    rocket = Rocket()

    assert rocket.velocity_x == pytest.approx(0.0)
    assert rocket.velocity_y == pytest.approx(0.0)


def test_rocket_initializes_with_zero_rotation_state():
    """
    Verify that a new rocket starts with zero angle and zero angular velocity.
    """
    rocket = Rocket()

    assert rocket.angle == pytest.approx(0.0)
    assert rocket.angular_velocity == pytest.approx(0.0)

def test_rocket_mass_returns_sum_of_dry_mass_and_fuel_mass():
    rocket = Rocket()
    rocket.dry_mass = 900.0
    rocket.fuel_mass = 25.0

    assert rocket.mass() == pytest.approx(925.0)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__])) # Avslutar programmet med exitkoden från pytest.main som anger om allt gick igenom eller inte
