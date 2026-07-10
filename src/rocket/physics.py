import math
from config import (
    GRAVITY, 
    MAIN_ENGINE_FORCE, 
    LEFT_ENGINE_FORCE, 
    RIGHT_ENGINE_FORCE,
    ROCKET_WIDTH,
    ROCKET_HEIGHT,
    MAIN_ENGINE_FUEL_BURN_RATE,
    SIDE_ENGINE_FUEL_BURN_RATE
)

def update_rocket_fuel_mass(rocket, actions, dt):
    """
    Update the rocket's fuel mass for one time step.

    Returns the fraction of the time step during which the engines can burn.

    Assumes that the current engine actions are constant during the whole time step.
    If the remaining fuel is not enough for the full step, compute the fraction of
    the step during which the active engines can burn together.
    """
    total_burn_rate = 0.0

    if actions["main_engine"]:
        total_burn_rate += MAIN_ENGINE_FUEL_BURN_RATE
    if actions["left_engine"]:
        total_burn_rate += SIDE_ENGINE_FUEL_BURN_RATE
    if actions["right_engine"]:
        total_burn_rate += SIDE_ENGINE_FUEL_BURN_RATE

    if total_burn_rate == 0.0:
        return 0.0
    
    required_fuel_mass = total_burn_rate * dt

    if rocket.fuel_mass >= required_fuel_mass:
        rocket.fuel_mass -= required_fuel_mass
        return 1.0

    burn_fraction = rocket.fuel_mass / required_fuel_mass
    rocket.fuel_mass = 0.0
    return burn_fraction

def _calculate_engine_forces(rocket, actions):
    """
    Calculate the total current engine force in world coordinates.
    """
    force_x = 0.0
    force_y = 0.0

    if actions["main_engine"]:
        force_x += -MAIN_ENGINE_FORCE * math.sin(rocket.angle)
        force_y += -MAIN_ENGINE_FORCE * math.cos(rocket.angle)

    if actions["left_engine"]:
        force_x += LEFT_ENGINE_FORCE * math.cos(rocket.angle)
        force_y += -LEFT_ENGINE_FORCE * math.sin(rocket.angle)

    if actions["right_engine"]:
        force_x += -RIGHT_ENGINE_FORCE * math.cos(rocket.angle)
        force_y += RIGHT_ENGINE_FORCE * math.sin(rocket.angle)

    return force_x, force_y

def _apply_translation_step(rocket, force_x, force_y, dt):
    """
    Apply one symplectic Euler translation step with given forces.
    """
    acceleration_x = force_x / rocket.mass()
    acceleration_y = force_y / rocket.mass()

    rocket.velocity_x += acceleration_x * dt
    rocket.velocity_y += acceleration_y * dt

    rocket.x += rocket.velocity_x * dt
    rocket.y += rocket.velocity_y * dt

def update_rocket_translation(rocket, actions, dt, burn_fraction):
    """
    Update the rocket's position and velocity from external forces for one time step.

    Gravity, main-engine thrust, and side-engine thrust are summed in x- and
    y-directions. The engine forces are rotated according to the rocket's angle,
    then converted to acceleration using F = m * a.

    If fuel runs out mid-timestep, the translation update is split 
    into a powered phase (engines active) and a coast phase (engines inactive). 

    Velocity and position are updated with symplectic Euler integration.
    """
    gravity_force_y = rocket.mass() * GRAVITY
    engine_force_x, engine_force_y = _calculate_engine_forces(rocket, actions)

    coast_force_x = 0.0
    coast_force_y = gravity_force_y

    powered_force_x = engine_force_x
    powered_force_y = gravity_force_y + engine_force_y

    if burn_fraction <= 0.0:
        _apply_translation_step(rocket, coast_force_x, coast_force_y, dt) # No engine active during entire dt
        return

    if burn_fraction >= 1.0:
        _apply_translation_step(rocket, powered_force_x, powered_force_y, dt) # All engines active during entire dt
        return

    powered_dt = burn_fraction * dt
    coast_dt = dt - powered_dt

    _apply_translation_step(rocket, powered_force_x, powered_force_y, powered_dt)
    _apply_translation_step(rocket, coast_force_x, coast_force_y, coast_dt)

def _calculate_moment_of_inertia(rocket):
    """
    Calculate the rocket's moment of inertia around its center of mass.

    The rocket is approximated as a uniform rectangle rotating around
    the z-axis.
    """
    width = ROCKET_WIDTH
    height = ROCKET_HEIGHT

    moment_of_inertia = rocket.mass() * (width ** 2 + height ** 2) / 12

    return moment_of_inertia

def _calculate_torque(actions):
    """
    Calculate the total current torque from the side engines.
    """
    torque = 0.0
    moment_arm = ROCKET_HEIGHT / 2

    if actions["left_engine"]:
        torque += LEFT_ENGINE_FORCE * moment_arm

    if actions["right_engine"]:
        torque += -RIGHT_ENGINE_FORCE * moment_arm

    return torque

def _apply_rotation_step(rocket, torque, dt):
    """
    Apply one symplectic Euler rotation step with given torque.
    """
    moment_of_inertia = _calculate_moment_of_inertia(rocket)
    angular_acceleration = torque / moment_of_inertia

    rocket.angular_velocity += angular_acceleration * dt
    rocket.angle += rocket.angular_velocity * dt

def update_rocket_rotation(rocket, actions, dt, burn_fraction):
    """
    Update the rocket's rotational motion from side-engine torque.

    The rocket is treated as a rigid rectangular body rotating around its
    center of mass. The side engines create torque, which gives angular
    acceleration through torque = I * angular_acceleration.

    If fuel runs out mid-timestep, the rotation update is split into a
    powered phase (side engines active) and a coast phase (side engines
    inactive).

    Angular velocity and angle are updated with symplectic Euler integration.

    Positive angle corresponds to rotation to the left.
    """
    powered_torque = _calculate_torque(actions)
    coast_torque = 0.0

    if burn_fraction <= 0.0:
        _apply_rotation_step(rocket, coast_torque, dt)
        return

    if burn_fraction >= 1.0:
        _apply_rotation_step(rocket, powered_torque, dt)
        return

    powered_dt = burn_fraction * dt
    coast_dt = dt - powered_dt

    _apply_rotation_step(rocket, powered_torque, powered_dt)
    _apply_rotation_step(rocket, coast_torque, coast_dt)