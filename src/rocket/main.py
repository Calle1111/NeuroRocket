import pygame

from config import FPS, WINDOW_HEIGHT, WINDOW_WIDTH, WINDOW_CAPTION
from renderer import Renderer
from simulation import Simulation
from input import get_player_actions


def main(): 
    """
    Initialize and run the NeuroRocket application.

    Creates the simulation objects, starts the game loop,
    and handles application shutdown.
    """
    pygame.init() # Startar alla pygames delsystem

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) # Skapar skärm
    pygame.display.set_caption(WINDOW_CAPTION)

    simulation = Simulation() # Skapar simulations objektet
    renderer = Renderer(screen) 
    clock = pygame.time.Clock() # Skapar en klocka som håller koll på hastigheten

    is_running = True

    while is_running:
        for event in pygame.event.get(): # Läs alla händelser, om användaren stängde fönstret stoppa programmet.
            if event.type == pygame.QUIT:
                is_running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: # Reset av programmet hanteras av pygame istället för player_actions, 
                simulation.reset()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                simulation.reset(template_id=0)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                simulation.reset(template_id=1)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_3:
                simulation.reset(template_id=2)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_4:
                simulation.reset(template_id=3)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_5:
                simulation.reset(template_id=4)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                renderer.toggle_hud()

        actions = get_player_actions()

        dt = clock.tick(FPS) / 1000 # Dela med 1000 för att omvandla till sekunder från millisekunder (SI-enheter)
        simulation.update(dt, actions) # Updaterar simulationen
        
        renderer.draw(
            simulation.rocket, 
            simulation.terrain, 
            simulation.active_engine_actions,
            simulation.status,
            simulation.crash_marker_position
            ) # Ritar uppdaterande raketen

    pygame.quit()


if __name__ == "__main__":
    main()