from config import ROCKET_DRY_MASS, ROCKET_MAX_FUEL_MASS

class Rocket:
    """
    Stores the rocket's physical state.

    Contains position, orientation, velocity, and other
    properties required by the simulation.
    """
    def __init__(self):
        """
        Initialize the rocket's state.
        """
        self.dry_mass = ROCKET_DRY_MASS
        self.max_fuel_mass = ROCKET_MAX_FUEL_MASS
        self.fuel_mass = ROCKET_MAX_FUEL_MASS

        self.x = 20.0 # Meter
        self.y = 25.0

        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.angle = 0.0
        self.angular_velocity = 0.0

    def mass(self):
        """
        Return the rocket's current total mass.

        Total mass i dry mass plus remaining fuel mass.
        """
        total_mass = self.dry_mass + self.fuel_mass
        return total_mass