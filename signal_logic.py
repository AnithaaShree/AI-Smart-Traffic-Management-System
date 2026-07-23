# signal_logic.py
# Traffic signal state machine: Red → Green → Yellow → Red
# Timing is determined by vehicle density and emergency overrides.

from config import (
    DENSITY_LOW_MAX, DENSITY_MEDIUM_MAX,
    GREEN_LOW, GREEN_MEDIUM, GREEN_HIGH,
    GREEN_AMBULANCE, YELLOW_DURATION, RED_DURATION
)


def get_traffic_density(vehicle_count):
    """
    Classify vehicle count into a density category.

    Returns: "Low", "Medium", or "High"
    """
    if vehicle_count <= DENSITY_LOW_MAX:
        return "Low"
    elif vehicle_count <= DENSITY_MEDIUM_MAX:
        return "Medium"
    else:
        return "High"


def get_green_duration(density):
    """
    Map density label to green signal duration (seconds).
    """
    return {
        "Low":    GREEN_LOW,
        "Medium": GREEN_MEDIUM,
        "High":   GREEN_HIGH,
    }.get(density, GREEN_LOW)


class TrafficSignal:
    """
    Simulates a 3-state traffic signal (Red / Yellow / Green).

    Call update() once per second to advance the state machine.
    """

    def __init__(self):
        self.state        = "Red"
        self.timer        = RED_DURATION
        self._in_emergency = False   # Track if we are in ambulance override

    def update(self, vehicle_count, ambulance_detected):
        """
        Advance the signal by one second tick.

        Priority order:
          1. Ambulance override → force Green for GREEN_AMBULANCE seconds
          2. Normal state machine countdown
        """
        # ── Emergency override ───────────────────────────────────────
        if ambulance_detected and not self._in_emergency:
            self.state         = "Green"
            self.timer         = GREEN_AMBULANCE
            self._in_emergency = True
            return

        # Clear emergency flag once timer expires
        if self._in_emergency and not ambulance_detected:
            self._in_emergency = False

        # ── Normal countdown ─────────────────────────────────────────
        if self.timer > 0:
            self.timer -= 1
            return

        # ── State transition on timer expiry ─────────────────────────
        if self.state == "Green":
            self.state = "Yellow"
            self.timer = YELLOW_DURATION

        elif self.state == "Yellow":
            self.state = "Red"
            self.timer = RED_DURATION

        elif self.state == "Red":
            density    = get_traffic_density(vehicle_count)
            self.state = "Green"
            self.timer = get_green_duration(density)

    def is_red(self):
        return self.state == "Red"

    def is_green(self):
        return self.state == "Green"