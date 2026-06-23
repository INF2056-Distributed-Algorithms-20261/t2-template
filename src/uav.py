import logging
from typing import List, Set, Tuple

from gradysim.protocol.messages.telemetry import Telemetry

from utils.actor_templates.uav_template import make_uav_protocol
from utils.viz_templates.uav_viz_template import UAVVizMixin
from utils.common.config import CLUSTER_WAYPOINTS, NUM_UAVS

from src.election_mixin import ElectionMixin


# ── Shared state for coordinated shutdown (non-loop mode) ──────────────────
# When loop=False, each UAV registers itself here upon reaching the endpoint.
# Once all UAVs have arrived, they stop scheduling timers so the event loop
# drains and the simulation ends naturally.

_total_uavs: int = 0                # set by main.py before simulation starts
_arrived_uavs: Set[int] = set()     # UAV IDs that reached the endpoint


def set_total_uavs(n: int) -> None:
    """Call before starting the simulation to tell UAVs how many must arrive."""
    global _total_uavs
    _total_uavs = n


def _all_uavs_arrived() -> bool:
    return _total_uavs > 0 and len(_arrived_uavs) >= _total_uavs


def make_uav(
    cluster_index: int,
    waypoints: List[Tuple[float, float, float]] = None,
    group_size: int = None,
    loop: bool = False,
) -> type:
    """
    Factory that returns a UAV protocol class for the given cluster slot.

    Args:
        cluster_index: This UAV's slot within its sub-group (0-based).
        waypoints:     Ordered waypoint path for this UAV's group.
                       Defaults to CLUSTER_WAYPOINTS.
        group_size:    Number of UAVs sharing this path (used for
                       formation spacing).  Defaults to NUM_UAVS.
        loop:          If True the UAV bounces back and forth along the
                       path.  If False (default) the UAV stops once it
                       reaches the last waypoint.

    If you want to add behaviours to every UAV (e.g. battery drain, swap
    logic), do it here: add a mixin before make_uav_protocol, or subclass
    the returned class.

    Example — adding battery drain to every UAV:

        class BatteryMixin:
            def handle_telemetry(self, telemetry):
                super().handle_telemetry(telemetry)
                # compute distance moved, subtract from self.battery …

        class _UAV(BatteryMixin, ElectionMixin, make_uav_protocol(
            waypoints     = CLUSTER_WAYPOINTS,
            cluster_index = cluster_index,
            num_uavs      = NUM_UAVS,
        )):
            pass
        return _UAV
    """
    if waypoints is None:
        waypoints = CLUSTER_WAYPOINTS
    if group_size is None:
        group_size = NUM_UAVS

    _loop = loop  # capture in closure

    class _UAV(ElectionMixin, make_uav_protocol(
        waypoints     = waypoints,
        cluster_index = cluster_index,
        num_uavs      = group_size,
    )):
        def initialize(self) -> None:
            super().initialize()
            self._loop = _loop
            self._reached_end = False

        def _advance_waypoint(self) -> None:
            if not self._loop and not self._going_to_base:
                if self._wp_index >= len(self._waypoints) - 1:
                    self._reached_end = True
                    _arrived_uavs.add(self.provider.get_id())
                    logging.info(
                        f"UAV {self.provider.get_id()} (slot {self._cluster_index}) "
                        f"reached endpoint — stopping (loop=False) "
                        f"[{len(_arrived_uavs)}/{_total_uavs} arrived]"
                    )
                    return
            super()._advance_waypoint()

        def handle_timer(self, timer: str) -> None:
            # Once all UAVs have arrived, stop rescheduling timers
            # so the event loop drains and the simulation ends.
            if self._reached_end and _all_uavs_arrived():
                return
            super().handle_timer(timer)

        def handle_telemetry(self, telemetry: Telemetry) -> None:
            if self._reached_end:
                return
            super().handle_telemetry(telemetry)

    _UAV.__name__ = f"UAV_slot{cluster_index}"
    return _UAV


def make_uav_viz(
    cluster_index: int,
    waypoints: List[Tuple[float, float, float]] = None,
    group_size: int = None,
    loop: bool = False,
) -> type:
    """
    Same as make_uav() but with GrADySim visualisation support mixed in.
    Use this class with VisualizationHandler enabled.

    Args:
        cluster_index: This UAV's slot within its sub-group (0-based).
        waypoints:     Ordered waypoint path for this UAV's group.
                       Defaults to CLUSTER_WAYPOINTS.
        group_size:    Number of UAVs sharing this path (used for
                       formation spacing).  Defaults to NUM_UAVS.
        loop:          If True the UAV bounces back and forth along the
                       path.  If False (default) the UAV stops once it
                       reaches the last waypoint.
    """
    if waypoints is None:
        waypoints = CLUSTER_WAYPOINTS
    if group_size is None:
        group_size = NUM_UAVS

    _loop = loop  # capture in closure

    class _UAVViz(UAVVizMixin, ElectionMixin, make_uav_protocol(
        waypoints     = waypoints,
        cluster_index = cluster_index,
        num_uavs      = group_size,
    )):
        """
        Example UAV Protocol with added Visualization support and
        leader election.  ElectionMixin sits between UAVVizMixin and the
        base protocol so it can intercept handle_packet and handle_timer
        before the base class processes them.
        """
        def initialize(self) -> None:
            super().initialize()
            self._loop = _loop
            self._reached_end = False

        def _advance_waypoint(self) -> None:
            if not self._loop and not self._going_to_base:
                if self._wp_index >= len(self._waypoints) - 1:
                    self._reached_end = True
                    _arrived_uavs.add(self.provider.get_id())
                    logging.info(
                        f"UAV {self.provider.get_id()} (slot {self._cluster_index}) "
                        f"reached endpoint — stopping (loop=False) "
                        f"[{len(_arrived_uavs)}/{_total_uavs} arrived]"
                    )
                    return
            super()._advance_waypoint()

        def handle_timer(self, timer: str) -> None:
            if self._reached_end and _all_uavs_arrived():
                return
            super().handle_timer(timer)

        def handle_telemetry(self, telemetry: Telemetry) -> None:
            if self._reached_end:
                return
            super().handle_telemetry(telemetry)

    _UAVViz.__name__ = f"UAV_slot{cluster_index}"
    return _UAVViz