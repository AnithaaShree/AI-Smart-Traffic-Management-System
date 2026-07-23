# ambulance_detection.py
# Ambulance detection logic.
#
# Standard YOLOv8n (COCO) does not include an "ambulance" class.
# Strategy used in this prototype:
#   1. Real keyword match  — works if you use a custom-trained model later.
#   2. Frame-range simulation — triggers when the ambulance video is loaded
#      and the frame counter enters the configured window.
#
# For a live demo, the simulation is clearly labelled so examiners understand
# the design intent and where a custom model would plug in.

from config import AMBULANCE_SIM_START, AMBULANCE_SIM_END


def detect_ambulance_real(detected_classes):
    """
    Check if the word 'ambulance' appears in any detected class name.
    Returns True only when a custom-trained model is used.

    Args:
        detected_classes: list of strings from vehicle_counter

    Returns:
        bool
    """
    return any("ambulance" in cls.lower() for cls in detected_classes)


def detect_ambulance_simulation(frame_number, scenario_name):
    """
    Simulate ambulance detection for the 'Ambulance Detect' scenario.
    Active only when that video is selected and within the frame window.

    Args:
        frame_number  : current frame index
        scenario_name : name of the active video scenario

    Returns:
        bool
    """
    if scenario_name != "Ambulance Detect":
        return False
    return AMBULANCE_SIM_START <= frame_number <= AMBULANCE_SIM_END


def is_ambulance_present(detected_classes, frame_number, scenario_name):
    """
    Combined check: real detection OR simulation.
    main.py calls only this function.
    """
    return (
        detect_ambulance_real(detected_classes) or
        detect_ambulance_simulation(frame_number, scenario_name)
    )