import pygame


def get_player_actions():
    """
    Read keyboard input and convert it into simulation actions.

    The simulation should not care whether the action comes from
    a keyboard, an AI agent, or something else.
    """
    keys = pygame.key.get_pressed() # Skapar key klass som håller koll på olika tangenter

    actions = {  # Gör om actions till en dictionary
        "main_engine": keys[pygame.K_UP], # nyckel main_engine pekar på True om pil upp nedtryckt
        "left_engine": keys[pygame.K_LEFT],
        "right_engine": keys[pygame.K_RIGHT],
    }

    return actions