from pathlib import Path
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src" / "rocket")) # Lägger till mappen rocket i pythons sökvägar så vi kan importera från den

from config import ROCKET_MASS
from rocket import Rocket


def test_rocket_initializes_with_expected_mass():
    """
    Verify that a new rocket gets the expected default mass.
    """
    rocket = Rocket()

    assert rocket.mass == pytest.approx(ROCKET_MASS)


def test_rocket_initializes_with_expected_position():
    """
    Verify that a new rocket gets the expected default position.
    """
    rocket = Rocket()

    assert rocket.x == pytest.approx(50)
    assert rocket.y == pytest.approx(35)


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


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__])) # Avslutar programmet med exitkoden från pytest.main som anger om allt gick igenom eller inte
