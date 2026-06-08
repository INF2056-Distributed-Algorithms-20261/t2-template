# t2-template

Template for T2 using [GrADySim](https://github.com/Project-GrADyS/gradys-sim-nextgen), including base classes for sensors and UAV drones.

## Setup

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

## Running

Always run from the **project root** using the `-m` flag so that `utils/` is on the path:

```bash
python -m src.main
```

### CLI flags

| Flag | Description |
|------|-------------|
| *(none)* | Run simulation with browser visualisation enabled |
| `--no-viz` | Disable the browser visualisation |
| `--force-regen` | Force regeneration of sensor positions and cluster waypoints |

The visualisation connects to the GrADySim web viewer at  
<https://project-gradys.github.io/gradys-sim-nextgen-visualization/>

> **Note (Windows):** The visualization handler spawns a subprocess for the WebSocket server.
> Any top-level code that should run only once must be inside `if __name__ == "__main__":`.

## Configuration

All tuneable parameters live in [`utils/common/config.py`](utils/common/config.py).

### Simulation

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SIMULATION_DURATION` | `1000` | Total simulated time (seconds) |

### UAV

| Parameter | Default | Description |
|-----------|---------|-------------|
| `NUM_UAVS` | `5` | Number of UAVs in the cluster |
| `UAV_SPEED` | `3.0` m/s | UAV cruise speed |
| `FLIGHT_ALT` | `15.0` m | Altitude at which UAVs cruise |
| `PASS_ALT_OFFSET` | `5.0` m | Extra altitude added when passing over sensors |

### Communication

| Parameter | Default | Description |
|-----------|---------|-------------|
| `COMM_RANGE` | `20.0` m | Radio transmission range (also used as sensor spacing) |
| `ANNOUNCE_WINDOW` | `3.0` s | Time window during which a UAV announces its presence to sensors |

### Sensors

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SENSOR_SEED` | `2056` | RNG seed for reproducible sensor placement |
| `SENSOR_FIELD_X` | `(-100, 100)` | X-axis bounds of the sensor field (metres) |
| `SENSOR_FIELD_Y` | `(-100, 100)` | Y-axis bounds of the sensor field (metres) |
| `SENSOR_PACKET_INTERVAL` | `4.0` s | How often each sensor generates a data packet |
| `SENSOR_MIN_SPACING` | `= COMM_RANGE` | Minimum distance between any two sensors |
| `SENSOR_JITTER` | `SENSOR_MIN_SPACING/2 - 1` | Random positional noise applied to each sensor (must be ≤ `SENSOR_MIN_SPACING / 2`) |

### Packet / Lamport TTL

| Parameter | Default | Description |
|-----------|---------|-------------|
| `PACKET_TTL_TICKS` | `100` | Lamport ticks before an undelivered packet is expired and counted as lost |

### Derived positions (auto-computed, do not edit directly)

| Name | Description |
|------|-------------|
| `BASE_GROUND` / `BASE_HOVER` | UAV start position on the ground / at cruise altitude |
| `ENDPOINT_GROUND` / `ENDPOINT_HOVER` | Far-end target on the ground / at cruise altitude |
| `CLUSTER_WAYPOINTS` | Evenly-spaced waypoints along the base→endpoint axis, one per `COMM_RANGE` |
| `SENSOR_POSITIONS` | Dict of generated sensor positions (excludes the central obstacle zone) |
