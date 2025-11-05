#!/usr/bin/env python3
"""
Components 模块
"""

from .panels import (
    show_status_panel,
    show_control_panel,
    show_info_panel,
    show_demo_panels
)
from .render import show_render_settings_panel
from .properties import show_property_panel
from .outline import show_outline_panel

__all__ = [
    'setup_dock_space',
    'show_status_panel',
    'show_control_panel',
    'show_info_panel',
    'show_demo_panels',
    'show_render_settings_panel',
    'show_property_panel',
    'show_outline_panel'
]