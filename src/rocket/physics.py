import math
from config import (
    GRAVITY, 
    MAIN_ENGINE_FORCE, 
    LEFT_ENGINE_FORCE, 
    RIGHT_ENGINE_FORCE,
    ROCKET_WIDTH,
    ROCKET_HEIGHT
)

def calculate_moment_of_inertia(rocket):
    """
    Calculate the rocket's moment of inertia around its center of mass.

    The rocket is approximated as a uniform rectangle rotating around
    the z-axis.
    """
    width = ROCKET_WIDTH
    height = ROCKET_HEIGHT

    moment_of_inertia = rocket.mass * (width ** 2 + height ** 2) / 12

    return moment_of_inertia

def update_rocket_translation(rocket, actions, dt):
    """
    Update the rocket's position and velocity from external forces.

    Gravity, main-engine thrust, and side-engine thrust are summed in x- and
    y-directions. The engine forces are rotated according to the rocket's angle,
    then converted to acceleration using F = m * a.

    Velocity and position are updated with symplectic Euler integration.
    """
    force_x = 0.0
    force_y = rocket.mass * GRAVITY

    if actions["main_engine"]:
        force_x += -MAIN_ENGINE_FORCE * math.sin(rocket.angle)
        force_y += -MAIN_ENGINE_FORCE * math.cos(rocket.angle)

    if actions["left_engine"]:
        force_x += LEFT_ENGINE_FORCE * math.cos(rocket.angle)
        force_y += -LEFT_ENGINE_FORCE * math.sin(rocket.angle)

    if actions["right_engine"]:
        force_x += -RIGHT_ENGINE_FORCE * math.cos(rocket.angle)
        force_y += RIGHT_ENGINE_FORCE * math.sin(rocket.angle)

    acceleration_x = force_x / rocket.mass
    acceleration_y = force_y / rocket.mass
        
    rocket.velocity_x += acceleration_x * dt # Denna och 3 under är symplektisk euler som löser ut nästa hastighet och i sin tur nästa position, både i y och x
    rocket.velocity_y += acceleration_y * dt

    rocket.x += rocket.velocity_x * dt
    rocket.y += rocket.velocity_y * dt


def update_rocket_rotation(rocket, actions, dt):
    """
    Update the rocket's rotational motion from side-engine torque.

    The rocket is treated as a rigid rectangular body rotating around its
    center of mass. The side engines create torque, which gives angular
    acceleration through torque = I * angular_acceleration.

    Positive angle corresponds to rotation to the left.
    """
    moment_of_inertia = calculate_moment_of_inertia(rocket)
    moment_arm = ROCKET_HEIGHT / 2

    torque = 0.0

    if actions["left_engine"]:
        torque += LEFT_ENGINE_FORCE * moment_arm

    if actions["right_engine"]:
        torque += -RIGHT_ENGINE_FORCE * moment_arm

    angular_acceleration = torque / moment_of_inertia

    rocket.angular_velocity += angular_acceleration * dt
    rocket.angle += rocket.angular_velocity * dt