from config import PIXELS_PER_METER, ROCKET_HEIGHT, ROCKET_WIDTH, WINDOW_WIDTH
import random
from rocket import Rocket
from terrain import Terrain, TERRAIN_TEMPLATE_COUNT
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
        self.current_template_id = 0
        self.rocket = Rocket()
        self.terrain = Terrain(template_id=self.current_template_id)
        self.active_engine_actions = { # Simulationen håller reda på om bränslet är slut eller ej och kan i sin tur kommunicera med renderer
            "main_engine": False,
            "left_engine": False,
            "right_engine": False,
        }
        self.status = "running"
        self.crash_marker_position = None
        self._set_random_spawn_position()
        

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

    def reset(self, template_id=None):
        """
        Reset the simulation to its initial state.
        """
        if template_id is None:
            template_id = random.randrange(TERRAIN_TEMPLATE_COUNT)

        self.current_template_id = template_id
        self.rocket = Rocket()
        self.terrain = Terrain(template_id=template_id)
        self.active_engine_actions = {
            "main_engine": False,
            "left_engine": False,
            "right_engine": False,
        }
        self.status = "running"
        self.crash_marker_position = None
        self._set_random_spawn_position()
    
    def _set_random_spawn_position(self):
        """
        Randomize the rocket spawn position so that its corners stay:
        - at least 2 meters from the left and right world bounds
        - at least 2 meters from the top of the world
        - at least 2 meters above the terrain's highest point
        """
        world_margin = 2.0
        terrain_margin = 2.0

        half_rocket_width = ROCKET_WIDTH / 2
        half_rocket_height = ROCKET_HEIGHT / 2
        world_width_meters = WINDOW_WIDTH / PIXELS_PER_METER

        highest_terrain_y = min(y for _, y in self.terrain.terrain_points) # Undersöker alla terrain punkter

        minimum_spawn_x = world_margin + half_rocket_width
        maximum_spawn_x = world_width_meters - world_margin - half_rocket_width

        minimum_spawn_y = world_margin + half_rocket_height
        maximum_spawn_y = highest_terrain_y - terrain_margin - half_rocket_height

        if minimum_spawn_x > maximum_spawn_x:
            raise ValueError("Terrain leaves no valid horizontal spawn area.")

        if minimum_spawn_y > maximum_spawn_y:
            raise ValueError("Terrain leaves no valid vertical spawn area.")

        self.rocket.x = random.uniform(minimum_spawn_x, maximum_spawn_x) # Randomiserar startpunkt
        self.rocket.y = random.uniform(minimum_spawn_y, maximum_spawn_y)