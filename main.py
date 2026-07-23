# main.py
# Entry point — wires all modules together and runs the Tkinter event loop.

import tkinter as tk
import cv2
import time
import threading

from config import VIDEOS, DEFAULT_VIDEO, FRAME_SKIP
from vehicle_counter import detect_vehicles
from signal_logic import TrafficSignal, get_traffic_density
from ambulance_detection import is_ambulance_present
from violation_detection import draw_stop_line, check_violation
from gui import TrafficGUI


class SmartTrafficSystem:
    """
    Orchestrates video reading, AI detection, signal logic, and GUI updates.
    """

    def __init__(self, root):
        self.root         = root
        self.running      = True

        # Current scenario
        self._current_scenario = DEFAULT_VIDEO
        self._pending_scenario = None          # Set by GUI callback
        self._scenario_lock    = threading.Lock()

        # Build GUI — pass our scenario-change callback
        self.gui = TrafficGUI(root, scenario_change_callback=self._request_scenario_change)

        # Signal state machine
        self.signal = TrafficSignal()

        # Per-frame state
        self.vehicle_count     = 0
        self.density           = "Low"
        self.ambulance         = False
        self.violation         = False
        self.frame_number      = 0

        # Open the default video
        self.cap = self._open_video(VIDEOS[DEFAULT_VIDEO])
        if self.cap is None:
            return

        # Background thread: updates signal once per second
        self._sig_thread = threading.Thread(
            target=self._signal_loop, daemon=True
        )
        self._sig_thread.start()

        self.gui.log_message(f"System started — {DEFAULT_VIDEO}")
        self._process_frame()

    # ──────────────────────────────────────────────────────────────────────
    # Video helpers
    # ──────────────────────────────────────────────────────────────────────

    def _open_video(self, path):
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            print(f"❌  Cannot open video: {path}")
            print("    Make sure the file exists inside the videos/ folder.")
            self.gui.log_message(f"ERROR: file not found — {path}")
            return None
        print(f"✅  Loaded: {path}")
        return cap

    def _switch_video(self, scenario_name):
        """Hot-swap the video source without restarting the app."""
        path = VIDEOS.get(scenario_name)
        if path is None:
            return

        new_cap = self._open_video(path)
        if new_cap is None:
            return

        # Release old capture and swap
        if self.cap:
            self.cap.release()

        self.cap                   = new_cap
        self.frame_number          = 0
        self._current_scenario     = scenario_name

        # Reset signal when switching scenarios
        self.signal = TrafficSignal()
        self.gui.log_message(f"Loaded: {scenario_name}")

    # ──────────────────────────────────────────────────────────────────────
    # Scenario change (triggered from GUI dropdown)
    # ──────────────────────────────────────────────────────────────────────

    def _request_scenario_change(self, name):
        """Called from the GUI thread; deferred to main loop for safety."""
        with self._scenario_lock:
            self._pending_scenario = name

    def _apply_pending_scenario(self):
        with self._scenario_lock:
            if self._pending_scenario:
                self._switch_video(self._pending_scenario)
                self._pending_scenario = None

    # ──────────────────────────────────────────────────────────────────────
    # Signal background thread
    # ──────────────────────────────────────────────────────────────────────

    def _signal_loop(self):
        """Tick the signal state machine every second."""
        while self.running:
            self.signal.update(self.vehicle_count, self.ambulance)
            time.sleep(1.0)

    # ──────────────────────────────────────────────────────────────────────
    # Main frame processing loop
    # ──────────────────────────────────────────────────────────────────────

    def _process_frame(self):
        if not self.running:
            return

        # Apply any pending scenario switch first
        self._apply_pending_scenario()

        if self.cap is None:
            self.root.after(100, self._process_frame)
            return

        ret, frame = self.cap.read()

        # Loop video when it ends
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.frame_number = 0
            self.root.after(30, self._process_frame)
            return

        self.frame_number += 1

        # ── Skip frames to reduce CPU load ────────────────────────
        if self.frame_number % FRAME_SKIP != 0:
            self.root.after(15, self._process_frame)
            return

        # ── 1. Vehicle detection ───────────────────────────────────
        annotated, count, classes, boxes = detect_vehicles(frame)
        self.vehicle_count = count
        self.density       = get_traffic_density(count)

        # ── 2. Ambulance detection ─────────────────────────────────
        self.ambulance = is_ambulance_present(
            classes, self.frame_number, self._current_scenario
        )
        if self.ambulance:
            self.gui.log_message("🚑 Ambulance! Green override active.")

        # ── 3. Stop line + violation ───────────────────────────────
        annotated, stop_y = draw_stop_line(annotated, self.signal.state)
        self.violation, annotated = check_violation(
            annotated, boxes, stop_y, self.signal.state
        )
        if self.violation:
            self.gui.log_message("⚠  Violation detected!")

        # ── 4. Overlay: scenario name, density badge ───────────────
        self._draw_overlays(annotated)

        # ── 5. GUI updates ─────────────────────────────────────────
        self.gui.update_video(annotated, self.frame_number)
        self.gui.update_signal(self.signal.state, self.signal.timer)
        self.gui.update_dashboard(
            self.vehicle_count,
            self.density,
            self.ambulance,
            self.violation,
            self._current_scenario
        )

        # Schedule next frame (~30 FPS)
        self.root.after(30, self._process_frame)

    # ──────────────────────────────────────────────────────────────────────
    # Frame overlay helpers
    # ──────────────────────────────────────────────────────────────────────

    def _draw_overlays(self, frame):
        """
        Draw minimal HUD overlays directly on the video frame:
        - Top-left: scenario name
        - Top-right: density badge
        These give the prototype a 'live system' feel.
        """
        h, w = frame.shape[:2]

        # ── Scenario tag (top-left) ────────────────────────────────
        tag = self._current_scenario
        cv2.rectangle(frame, (0, 0), (len(tag) * 9 + 16, 26), (13, 17, 23), -1)
        cv2.putText(frame, tag, (8, 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, (88, 166, 255), 1, cv2.LINE_AA)

        # ── Density badge (top-right) ──────────────────────────────
        density_colors = {
            "Low":    (63, 185, 80),
            "Medium": (210, 153, 34),
            "High":   (248, 81, 73),
        }
        d_color = density_colors.get(self.density, (200, 200, 200))
        badge_text = f"Density: {self.density}"
        bw = len(badge_text) * 9 + 16
        cv2.rectangle(frame, (w - bw, 0), (w, 26), (13, 17, 23), -1)
        cv2.putText(frame, badge_text, (w - bw + 8, 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, d_color, 1, cv2.LINE_AA)

        # ── Vehicle count bottom-left ──────────────────────────────
        cv2.rectangle(frame, (0, h - 28), (180, h), (13, 17, 23), -1)
        cv2.putText(frame, f"Vehicles: {self.vehicle_count}", (8, h - 9),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (201, 209, 217), 1, cv2.LINE_AA)

    # ──────────────────────────────────────────────────────────────────────
    # Cleanup
    # ──────────────────────────────────────────────────────────────────────

    def cleanup(self):
        self.running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        print("✅  System stopped cleanly.")


# ── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    system = SmartTrafficSystem(root)
    root.protocol("WM_DELETE_WINDOW",
                  lambda: (system.cleanup(), root.destroy()))
    print("🖥️   GUI running. Close the window to stop.")
    root.mainloop()