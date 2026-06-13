from config import ROCKET_MASS

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
        self.mass = ROCKET_MASS

        self.x = 500
        self.y = 350

        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.angle = 0.0
        self.angular_velocity = 0.0


