"""
Hydroponics Platform — Edge Camera Module
Exposes high-level image acquisition and AI integration hooks.
"""

from .camera_service import get_latest_frame, capture_snapshot, get_camera_status

__all__ = ["get_latest_frame", "capture_snapshot", "get_camera_status"]
