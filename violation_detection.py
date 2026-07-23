# violation_detection.py
# Draws a stop line on the video frame and detects vehicles that cross
# the line while the signal is Red (traffic violation).

import cv2
from config import STOP_LINE_RATIO


def draw_stop_line(frame, signal_state):
    """
    Draw the stop line across the frame.

    Line is bright red when signal is Red; white otherwise.

    Returns:
        frame        : annotated frame
        stop_line_y  : integer y-coordinate of the line
    """
    h, w = frame.shape[:2]
    stop_line_y = int(h * STOP_LINE_RATIO)

    if signal_state == "Red":
        line_color  = (0, 0, 255)   # Red
        text_color  = (0, 0, 255)
    else:
        line_color  = (200, 200, 200)  # Light grey
        text_color  = (200, 200, 200)

    # Thick horizontal line
    cv2.line(frame, (0, stop_line_y), (w, stop_line_y), line_color, 3)

    # Label
    cv2.putText(
        frame, "── STOP LINE ──",
        (10, stop_line_y - 8),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6,
        text_color, 2, cv2.LINE_AA
    )

    return frame, stop_line_y


def check_violation(frame, bounding_boxes, stop_line_y, signal_state):
    """
    Detect whether any vehicle has crossed the stop line on a Red signal.

    A vehicle "crosses" when the bottom edge of its bounding box (y2)
    is below the stop line (y2 > stop_line_y) — i.e. it has moved past it.

    Args:
        frame          : current video frame (will be annotated in-place)
        bounding_boxes : list of (x1, y1, x2, y2) from vehicle_counter
        stop_line_y    : y-coordinate of the stop line
        signal_state   : "Red", "Yellow", or "Green"

    Returns:
        violation_found : bool
        frame           : annotated frame
    """
    # Violations only count on Red
    if signal_state != "Red":
        return False, frame

    violation_found = False

    for (x1, y1, x2, y2) in bounding_boxes:
        if y2 > stop_line_y:
            violation_found = True

            # Highlight offending vehicle with a thick red box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(
                frame, "VIOLATION",
                (x1, max(y1 - 10, 12)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                (0, 0, 255), 2, cv2.LINE_AA
            )

    # Full-frame warning overlay
    if violation_found:
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 60), (0, 0, 180), -1)
        cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)
        cv2.putText(
            frame, "⚠  TRAFFIC VIOLATION DETECTED  ⚠",
            (20, 42),
            cv2.FONT_HERSHEY_DUPLEX, 0.85,
            (255, 255, 255), 2, cv2.LINE_AA
        )

    return violation_found, frame