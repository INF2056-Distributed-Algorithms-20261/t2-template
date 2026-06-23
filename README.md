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
| *(none)* | Run simulation with browser visualisation enabled; UAVs do a single start→end run |
| `--no-viz` | Disable the browser visualisation |
| `--force-regen` | Force regeneration of sensor positions and cluster waypoints |
| `--loop` | UAVs bounce back and forth along their path instead of stopping at the endpoint |

By default (`--loop` not set) the simulation **ends automatically** once every UAV has reached its final waypoint. With `--loop`, UAVs patrol continuously until `SIMULATION_DURATION` is reached.

The visualisation connects to the GrADySim web viewer at  
<https://project-gradys.github.io/gradys-sim-nextgen-visualization/>

> **Note (Windows):** The visualization handler spawns a subprocess for the WebSocket server.
> Any top-level code that should run only once must be inside `if __name__ == "__main__":`.

## Leader Election

The simulation includes a **Bully-style leader election protocol** ([`src/election_mixin.py`](src/election_mixin.py)).

### How it works

1. **Pre-split**: Before UAV groups diverge around the obstacle, the leader is **predefined** as the UAV with the highest node ID — no election overhead.
2. **Split detection**: A periodic check (every 1 s) monitors heartbeat timestamps. If a known peer hasn't been heard from in 5 s (`PEER_TIMEOUT`), it's considered out of range. If the lost peer was the leader, a new election is triggered.
3. **Merge detection**: When a heartbeat arrives from a previously-unknown peer, a merge event is detected and a new election is triggered.
4. **During election**: Sensor data is still collected but buffered separately (`_election_buffer`). Normal data gossip continues for already-collected packets.
5. **After election**: The winner is announced. Non-leaders **transfer all their data** (packets + election buffer) to the leader, then clear their local buffers.

### Election messages

| `msg_type` | Purpose |
|------------|---------|
| `"election"` | "I'm starting an election" — broadcast by any UAV detecting a split or merge |
| `"alive"` | "I have a higher ID, stand down" — sent by higher-ID UAVs |
| `"leader"` | "I am the leader" — broadcast by the winner after the election timeout |
| `"data_transfer"` | Non-leader sends its buffered data to the new leader |

### Metrics

After the simulation finishes, an **Election Summary** is printed to stdout with:

- Total elections triggered (split vs merge)
- Per-election details: trigger, winner, duration, time window
- Per-UAV buffer sizes at transfer time
- **Time lost to merges**: total and average merge election duration

Election events are also available programmatically via `utils.metrics.election_stats.ELECTION_LOG`.

## Configuration

All tuneable parameters live in [`utils/common/config.py`](utils/common/config.py).

### Simulation

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SIMULATION_DURATION` | `120` | Total simulated time in seconds (acts as upper bound; simulation ends earlier if all UAVs reach the endpoint in non-loop mode) |

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
| `LEFT_WAYPOINTS` / `RIGHT_WAYPOINTS` | Split paths that diverge around the obstacle zone and converge afterward |
| `SENSOR_POSITIONS` | Dict of generated sensor positions (excludes the central obstacle zone) |
