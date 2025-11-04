#!/usr/bin/env python3
"""
Components 模块
"""

from .dock_space import setup_dock_space
from .panels import (
    show_status_panel,
    show_control_panel,
    show_info_panel,
    show_all_panels
)

__all__ = [
    'setup_dock_space',
    'show_status_panel',
    'show_control_panel',
    'show_info_panel',
    'show_all_panels'
]