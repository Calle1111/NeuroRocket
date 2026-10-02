# NeuroRocket

A 2D rocket landing simulator built in Python, with a custom physics model and Pygame visualization. Control thrust and rotation to reach a landing pad while managing limited fuel, changing mass, and uneven terrain.

The simulation environment and manual controls are implemented. The next stage is to develop autonomous landing agents using NEAT and reinforcement learning, then compare their performance in the same environment. **AI agents and training results are not yet implemented.**

## Motivation

NeuroRocket is a personal project exploring physics modeling, numerical methods, software architecture, and machine learning. The environment is built from basic force and torque equations so that its behavior can be understood, tested, and extended step by step.

Development follows the sequence: physics → simulation → visualization → manual landing → NEAT → reinforcement learning.

## Current features

- Two-dimensional translation and rotation of a rigid rectangular rocket.
- Gravity, orientation-dependent main-engine thrust, and two side thrusters that produce both force and torque.
- A shared fuel tank, fuel consumption, and mass that decreases during flight.
- Powered and unpowered substeps when fuel runs out during an update.
- Five terrain layouts with a landing pad and randomized initial positions above the terrain.
- Landing checks based on contact, velocity, tilt, and angular velocity.
- `running`, `landed`, and `crashed` states, with flight frozen after landing or crashing.
- Keyboard controls, reset, fuel display, engine flames, status text, and an optional telemetry HUD.
- Automated tests for rocket state, physics, collision detection, and simulation behavior.

## Getting started

The project uses Python 3, Pygame, and pytest. The current code has been verified with Python 3.12.5 and pygame-ce 2.5.7. pygame-ce provides the `pygame` module used by the application.

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/Calle1111/NeuroRocket.git
cd NeuroRocket
python3 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Or in Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies and start the simulator from the repository root:

```bash
python -m pip install pygame-ce pytest
python src/rocket/main.py
```

The application opens a 1400 × 800 pixel window. It requires a graphical desktop to play interactively.

## Controls

| Key | Action |
| --- | --- |
| ↑ | Fire the main engine |
| ← | Fire the left side thruster |
| → | Fire the right side thruster |
| R | Restart with a randomly selected terrain layout |
| 1–5 | Restart with a specific terrain layout |
| H | Toggle the telemetry HUD |
| Close window | Exit |

The arrow keys activate engines directly. When upright, the left thruster pushes the rocket to the right and rotates it counterclockwise; the right thruster does the opposite. A short pulse changes angular velocity, so releasing a key does not stop rotation. Use the opposite thruster to counter it.

Aim for the green landing pad, reduce descent speed, and keep the rocket close to upright before contact. Press **H** to inspect position, velocity, angle, and angular velocity. Press **R** to try again after a landing or crash.

The first run uses terrain layout 1. Every restart randomizes the rocket's position, including restarts with a manually selected layout. The spawn area keeps the initially upright rocket at least 2 m from the side and top boundaries and at least 2 m above the terrain's highest point.

## Physics model

### Units and coordinates

Physics uses SI units internally: meters, seconds, kilograms, newtons, and radians. Rendering converts meters to pixels at **10 pixels per meter**, giving a world of **140 × 80 m**.

The coordinate system follows the screen: x increases to the right and y increases downward. Rocket position refers to its center. An angle of zero points straight up, and positive angles represent counterclockwise rotation. Gravity acts in the positive y direction.

### Forces and translation

Acceleration follows Newton's second law:

```text
a_x = F_x / m
a_y = F_y / m
```

Gravity contributes `F_gravity = m × g`, where `g = 9.82 m/s²`. The main engine acts along the rocket's upward local axis. For thrust T and angle θ, its world-coordinate components are:

```text
F_main,x = -T × sin(θ)
F_main,y = -T × cos(θ)
```

The side-engine forces are also rotated into world coordinates. Tilting the rocket therefore changes how engine thrust is divided between horizontal and vertical motion.

### Torque and rotation

The rocket is approximated as a uniform rigid rectangle. Its moment of inertia about its center is:

```text
I = m × (width² + height²) / 12
angular_acceleration = torque / I
```

The main engine produces no torque because its thrust acts through the center. Side-thruster torque uses a moment arm of half the rocket's height. The two side thrusters produce opposite torques; firing both cancels their force and torque while still consuming fuel.

### Numerical integration

Translation and rotation use symplectic Euler integration: update velocity first, then update position using the new velocity.

```text
v_next = v + a × dt
position_next = position + v_next × dt

ω_next = ω + angular_acceleration × dt
θ_next = θ + ω_next × dt
```

The main loop targets 60 FPS and measures the elapsed time for each update. The timestep is variable rather than fixed. Within an update, fuel is consumed first, followed by translation, rotation, and collision evaluation. Forces use the orientation at the start of the translation update, and both motion updates use the mass remaining after fuel consumption.

### Fuel and changing mass

All three engines draw from the same tank:

```text
total_mass = dry_mass + remaining_fuel_mass
required_fuel = sum(active_engine_burn_rates) × dt
```

Fuel cannot become negative. If it runs out partway through a timestep, `burn_fraction` gives the fraction of that step for which the engines can operate. Translation and rotation each split the update into a powered phase and a coasting phase. With an empty tank, engines produce neither force nor torque, while gravity and existing motion continue.

As fuel decreases, the same thrust produces greater acceleration, and the same torque produces greater angular acceleration.

| Parameter | Current value |
| --- | --- |
| Rocket width × height | 2.2 × 8.8 m |
| Dry mass | 700 kg |
| Initial fuel mass | 300 kg |
| Initial total mass | 1000 kg |
| Main-engine thrust | 15,000 N |
| Thrust per side engine | 1000 N |
| Main-engine fuel consumption | 25 kg/s |
| Fuel consumption per side engine | 1.35 kg/s |

The full tank provides 12 seconds of continuous main-engine operation when the side engines are inactive. Physical parameters and landing limits are defined in [config.py](src/rocket/config.py).

## Terrain, collisions, and landing

Terrain consists of connected line segments shared by rendering and collision detection. The five layouts include horizontal sections, vertical walls, and sloped terrain. The landing pad spans x = 72–80 m in every layout; its y coordinate varies.

Collision detection rotates the rocket's four corners into world coordinates and checks them against terrain segments using a 0.25 m contact tolerance. Leaving any world boundary with a corner produces a crash. Terrain contact without pad contact also produces a crash. When pad contact is detected, all of these limits must be satisfied:

| Landing condition | Maximum magnitude |
| --- | --- |
| Vertical velocity | 3.0 m/s |
| Horizontal velocity | 1.5 m/s |
| Tilt from upright | 0.20 rad ≈ 11.5° |
| Angular velocity | 0.50 rad/s ≈ 28.6°/s |

The tilt check normalizes the angle, so complete rotations do not change which orientations count as upright. Successful contact sets the state to `landed`; unsafe contact sets it to `crashed`. Further physics updates stop until reset.

### Model scope and limitations

The model intentionally uses constant engine forces and burn rates, a rectangular body, and a fixed center of mass. It does not model aerodynamic drag, changing fuel distribution, exhaust dynamics, or a complete variable-mass propulsion model. Ground contact ends the flight without bounce, sliding, or friction.

Collision checks sample corner positions after each update. They do not sweep the body through its entire trajectory or test every edge, so large timesteps or high speeds can miss contact. Spawn randomization ensures initial clearance; it does not guarantee that every starting position has equal difficulty or is reachable with the available fuel. These are relevant considerations for future training and evaluation.

## Architecture

Physics, state, rendering, and input have separate responsibilities. Rendering reads simulation state, while keyboard input produces engine actions without performing physics calculations.

```text
src/rocket/
├── main.py          # Application setup, events, and main loop
├── simulation.py    # World ownership, update sequence, status, and reset
├── rocket.py        # Rocket state and current total mass
├── physics.py       # Fuel, forces, torque, and integration
├── terrain.py       # Terrain layouts and landing-pad geometry
├── collision.py     # Corner geometry, contact, and landing checks
├── renderer.py      # Graphics, fuel bar, status, and telemetry HUD
├── input.py         # Keyboard-to-action conversion
└── config.py        # Physical parameters and display settings

tests/
├── test_rocket.py
├── test_physics.py
├── test_collision.py
└── test_simulation.py
```

Controllers use the same three boolean engine actions:

```python
actions = {
    "main_engine": False,
    "left_engine": False,
    "right_engine": False,
}
```

This allows a future AI controller to replace keyboard input through the existing action interface. The simulation can already be updated without a Pygame window, using `Simulation.update(dt, actions)` and `Simulation.reset(template_id=...)`. A training interface with observations, rewards, and episode management remains future work.

## Tests

Run the test suite from the repository root:

```bash
python -m pytest -q
```

The current suite contains 75 passing test cases covering initial state, force projection, gravity, torque, fuel consumption, partial burn steps, corner geometry, terrain contact, landing limits, spawn margins across all five layouts, reset, and frozen state after a crash. The tests focus on physics and simulation logic; automated rendering tests are not part of the suite.

## Roadmap: autonomous landing

The next objective is to train agents that control the main engine and both side thrusters in this environment.

1. **Implement NEAT from scratch.** Build a NeuroEvolution of Augmenting Topologies controller that learns to land through evolutionary optimization of neural networks.
2. **Improve landing performance.** Refine landing precision, fuel efficiency, and robustness across terrain layouts and starting positions.
3. **Implement reinforcement learning.** Develop a controller using a method such as REINFORCE, policy gradient, or actor–critic. The specific algorithm remains to be selected.
4. **Compare NEAT and reinforcement learning.** Evaluate both approaches on shared scenarios and document their strengths, weaknesses, and computational cost.

The planned comparison will consider:

| Dimension | Planned evaluation |
| --- | --- |
| Training efficiency | Environment interactions and elapsed training time needed to reach a target success rate |
| Landing reliability | Fraction of evaluation episodes ending in a successful landing |
| Landing quality | Distance from the pad center, touchdown velocities, tilt, and angular velocity |
| Fuel efficiency | Fuel consumed during successful landings |
| Robustness | Performance across terrain layouts and starting positions, including cases withheld from training |

Both controllers will use the same physics, action format, and landing conditions. Reproducible scenarios, multiple training seeds, and separate training and evaluation runs are planned to make the comparison meaningful. These are future experiments; no comparative results are available yet.

## License

NeuroRocket is distributed under the [MIT License](LICENSE).
