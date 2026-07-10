from rocket import Rocket
from physics import update_rocket_translation, update_rocket_rotation, update_rocket_fuel_mass

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
        self.active_engine_actions = { # Simulationen håller reda på om bränslet är slut eller ej och kan i sin tur kommunicera med renderer
            "main_engine": False,
            "left_engine": False,
            "right_engine": False,
        }
        

    def update(self, dt, actions):
        """
        Advance the simulation by one frame.
        """
        burn_fraction = update_rocket_fuel_mass(self.rocket, actions, dt)
        update_rocket_translation(self.rocket, actions, dt, burn_fraction)
        update_rocket_rotation(self.rocket, actions, dt, burn_fraction)

        self.active_engine_actions = {
            "main_engine": actions["main_engine"] and burn_fraction > 0.0,
            "left_engine": actions["left_engine"] and burn_fraction > 0.0,
            "right_engine": actions["right_engine"] and burn_fraction > 0.0,
        }

    def reset(self):
        """
        Reset the simulation to its initial state.
        """
        self.rocket = Rocket()
        self.active_engine_actions = {
            "main_engine": False,
            "left_engine": False,
            "right_engine": False,
        }