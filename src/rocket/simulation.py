from rocket import Rocket
from physics import update_rocket_translation, update_rocket_rotation

class Simulation:
    """
    Owns and updates the simulation state.

    This class connects the main program loop with the
    objects that exist in the simulated world.
    """

    def __init__(self): # Attribut är objekt programmet behöver hålla reda på
        """
        Create the simulation objects.
        """
        self.rocket = Rocket()

    def update(self, dt, actions):
        """
        Advance the simulation by one frame.

        Later this will contain gravity, thrust,
        rotation, fuel, and collision logic.
        """
        update_rocket_translation(self.rocket, actions, dt)
        update_rocket_rotation(self.rocket, actions, dt)


