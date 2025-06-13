"""
Reader plugin for teeth landmarks JSON files.
"""

import json
import numpy as np
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

def napari_get_reader(path: Union[str, List[str]]) -> Optional[Callable]:
    """
    Returns a reader function if the path is a JSON file with landmarks data.
    
    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.
        
    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # if multiple files, we don't handle that
        return None
        
    if isinstance(path, str):
        path = Path(path)
        
    # Check if it's a JSON file
    if not path.suffix.lower() == '.json':
        return None
        
    # Try to validate if it's a landmarks JSON by checking structure
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if it has the expected structure
        if not isinstance(data, dict) or 'objects' not in data:
            return None
            
        objects = data.get('objects', [])
        if not objects:
            return None
            
        # Check if first object has expected keys
        first_obj = objects[0]
        if not isinstance(first_obj, dict) or 'coord' not in first_obj:
            return None
            
    except (json.JSONDecodeError, FileNotFoundError, KeyError, IndexError):
        return None
    
    # If we get here, it looks like a valid landmarks file
    return reader_function


def reader_function(path: Union[str, Path]) -> List[Tuple[Any, Dict[str, Any], str]]:
    """
    Read teeth landmarks from JSON file and return napari layer data.
    
    Parameters
    ----------
    path : str or Path
        Path to the JSON file.
        
    Returns
    -------
    layer_data : list of tuples
        List of layer data tuples. Each tuple contains:
        (data, metadata, layer_type)
    """
    if isinstance(path, str):
        path = Path(path)
        
    # Load the landmarks data
    landmarks_data = load_landmarks_json(str(path))
    
    # Extract points and metadata
    points, metadata = extract_points_data(landmarks_data)
    
    # Create color map and colors
    _, point_colors = create_color_map(metadata['classes'])
    
    # Create labels for tooltips
    labels = create_point_labels(metadata)
    
    # Prepare layer metadata
    layer_meta = {
        'name': f"Landmarks [{path.name}]",
        'size': 1.0,
        'face_color': point_colors,
        'border_color': 'white',
        'border_width': 0.1,
        'properties': {
            'key': metadata['keys'],
            'class': metadata['classes'],
            'score': metadata['scores'],  
            'instance_id': metadata['instance_ids'],
            'label': labels
        }
    }
    
    # Return layer data as expected by napari
    return [(points, layer_meta, 'points')]


def load_landmarks_json(filepath: str) -> Dict[str, Any]:
    """Load landmarks data from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def extract_points_data(landmarks_data: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, List]]:
    """Extract points coordinates and metadata from landmarks data."""
    objects = landmarks_data.get('objects', [])
    
    if not objects:
        raise ValueError("Invalid JSON: no objects found")
    
    # Extract coordinates
    coordinates = []
    metadata = {
        'keys': [],
        'scores': [],
        'classes': [],
        'instance_ids': []
    }
    
    for obj in objects:
        coord = obj.get('coord', [0, 0, 0])
        coordinates.append(coord)
        
        metadata['keys'].append(obj.get('key', 'unknown'))
        metadata['scores'].append(obj.get('score', 0.0))
        metadata['classes'].append(obj.get('class', 'unknown'))
        metadata['instance_ids'].append(obj.get('instance_id', 0))
    
    points = np.array(coordinates)
    
    return points, metadata


def create_color_map(classes: List[str]) -> Tuple[Dict[str, str], List[str]]:
    """Create color mapping for different classes."""
    unique_classes = list(set(classes))
    
    # Default colors
    colors = ['red', 'blue', 'green', 'yellow', 'magenta', 'cyan', 'orange', 'purple']
    
    # Create color map
    color_map = {}
    for i, cls in enumerate(unique_classes):
        color_map[cls] = colors[i % len(colors)]
    
    # Assign color to each point
    point_colors = [color_map[cls] for cls in classes]
    
    return color_map, point_colors


def create_point_labels(metadata: Dict[str, List]) -> List[str]:
    """Create human-readable labels for points."""
    labels = []
    for i in range(len(metadata['keys'])):
        label = (f"Key: {metadata['keys'][i]}\n"
                f"Class: {metadata['classes'][i]}\n"
                f"Score: {metadata['scores'][i]:.4f}\n"
                f"Instance ID: {metadata['instance_ids'][i]}")
        labels.append(label)
    
    return labels