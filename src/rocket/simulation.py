from rocket import Rocket
from terrain import Terrain
from physics import update_rocket_translation, update_rocket_rotation, update_rocket_fuel_mass
from collision import evaluate_rocket_status, get_terrain_contact_corner

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
        self.terrain = Terrain()
        self.active_engine_actions = { # Simulationen håller reda på om bränslet är slut eller ej och kan i sin tur kommunicera med renderer
            "main_engine": False,
            "left_engine": False,
            "right_engine": False,
        }
        self.status = "running"
        self.crash_marker_position = None
        

    def update(self, dt, actions):
        """
        Advance the simulation by one frame.
        """

        if self.status != "running": # Returnerar och sätter motorflammor av om vi har krashat eller landat
            self.active_engine_actions = {
                "main_engine": False,
                "left_engine": False,
                "right_engine": False,
            }
            return
    
        burn_fraction = update_rocket_fuel_mass(self.rocket, actions, dt)
        update_rocket_translation(self.rocket, actions, dt, burn_fraction)
        update_rocket_rotation(self.rocket, actions, dt, burn_fraction)

        self.active_engine_actions = {
            "main_engine": actions["main_engine"] and burn_fraction > 0.0,
            "left_engine": actions["left_engine"] and burn_fraction > 0.0,
            "right_engine": actions["right_engine"] and burn_fraction > 0.0,
        }

        self.status = evaluate_rocket_status(self.rocket, self.terrain)

        # Om vi landar/krashar under framen så ska motororernas tillstånd uppdateras visuellt, samt tar fram aku
        if self.status == "crashed":
            self.crash_marker_position = get_terrain_contact_corner(
                self.rocket,
                self.terrain,
            )
            self.active_engine_actions = {
                "main_engine": False,
                "left_engine": False,
                "right_engine": False,
            }

        if self.status == "landed":
            self.active_engine_actions = {
                "main_engine": False,
                "left_engine": False,
                "right_engine": False,
            }

    def reset(self):
        """
        Reset the simulation to its initial state.
        """
        self.rocket = Rocket()
        self.terrain = Terrain()
        self.active_engine_actions = {
            "main_engine": False,
            "left_engine": False,
            "right_engine": False,
        }
        self.status = "running"
        self.crash_marker_position = None