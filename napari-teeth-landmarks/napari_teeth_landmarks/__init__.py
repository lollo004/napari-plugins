"""
A napari plugin for visualizing teeth landmarks from JSON files.
"""

__version__ = "0.1.0"

from ._reader import napari_get_reader

__all__ = (
    "napari_get_reader",
)