#!/usr/bin/env python3
"""
Viewport component - Display rotating square using ImGui drawing
"""

from imgui_bundle import imgui
import time
import math


class ViewportManager:
    """Viewport manager for managing rotating square"""

    def __init__(self):
        self.rotation_angle = 0.0
        self.rotation_speed = 1.0  # Rotation speed in degrees per second
        self.square_color = [1.0, 0.5, 0.0, 1.0]  # Orange color
        self.background_color = [0.1, 0.1, 0.1, 1.0]  # Dark gray background

    def update_rotation(self):
        """Update rotation angle based on time"""
        current_time = time.time()
        self.rotation_angle = (current_time * self.rotation_speed) % 360.0


def show_viewport_panel(viewport_manager: ViewportManager, _open: bool = True) -> bool:
    """Display viewport panel with rotating square"""
    # Set dockable
    imgui.set_next_window_dock_id(imgui.get_id("DockSpace"), imgui.Cond_.first_use_ever)

    # Set default window size
    imgui.set_next_window_size(imgui.ImVec2(800, 600), imgui.Cond_.first_use_ever)

    # Set window background color
    r, g, b, a = viewport_manager.background_color
    imgui.push_style_color(imgui.Col_.window_bg, imgui.ImVec4(r, g, b, a))

    # Start viewport window
    window_open = imgui.begin("旋转正方形视口", True)

    if window_open:
        # Control panel
        imgui.text("控制设置:")

        # Rotation speed control
        imgui.text("旋转速度:")
        _, viewport_manager.rotation_speed = imgui.slider_float("##speed",
                                                              viewport_manager.rotation_speed,
                                                              0.1, 5.0)

        # Square color control
        imgui.text("正方形颜色:")
        _, viewport_manager.square_color = imgui.color_edit4("##square_color",
                                                           viewport_manager.square_color)

        # Background color control
        imgui.text("背景颜色:")
        _, viewport_manager.background_color = imgui.color_edit4("##bg_color",
                                                                viewport_manager.background_color)

        imgui.separator()

        # Get window content region size for drawing
        content_region = imgui.get_content_region_avail()
        window_width = int(content_region.x)
        window_height = int(content_region.y)

        # Ensure minimum size
        if window_width < 100:
            window_width = 100
        if window_height < 100:
            window_height = 100

        # Create child window for drawing
        imgui.begin_child("Drawing Area", imgui.ImVec2(window_width, window_height), True)

        # Get drawing area position and size
        draw_pos = imgui.get_cursor_screen_pos()
        draw_size = imgui.get_content_region_avail()

        # Update rotation
        viewport_manager.update_rotation()

        # Calculate center of drawing area
        center_x = draw_pos.x + draw_size.x * 0.5
        center_y = draw_pos.y + draw_size.y * 0.5

        # Calculate square size (80% of smaller dimension)
        square_size = min(draw_size.x, draw_size.y) * 0.4

        # Calculate rotation in radians
        angle_rad = math.radians(viewport_manager.rotation_angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        # Square vertices (relative to center)
        half_size = square_size * 0.5
        vertices = [
            (-half_size, -half_size),  # Bottom-left
            (half_size, -half_size),   # Bottom-right
            (half_size, half_size),    # Top-right
            (-half_size, half_size)    # Top-left
        ]

        # Get draw list
        draw_list = imgui.get_window_draw_list()

        # Apply rotation and calculate screen coordinates
        screen_vertices = []
        for x, y in vertices:
            # Rotate vertex
            x_rot = x * cos_a - y * sin_a
            y_rot = x * sin_a + y * cos_a
            # Convert to screen coordinates
            screen_x = center_x + x_rot
            screen_y = center_y + y_rot
            screen_vertices.append(imgui.ImVec2(screen_x, screen_y))

        # Draw rotating square
        r, g, b, a = viewport_manager.square_color
        draw_list.add_quad_filled(
            screen_vertices[0],  # Bottom-left
            screen_vertices[1],  # Bottom-right
            screen_vertices[2],  # Top-right
            screen_vertices[3],  # Top-left
            imgui.get_color_u32(imgui.ImVec4(r, g, b, a))
        )

        # Draw square outline
        draw_list.add_quad(
            screen_vertices[0],  # Bottom-left
            screen_vertices[1],  # Bottom-right
            screen_vertices[2],  # Top-right
            screen_vertices[3],  # Top-left
            imgui.get_color_u32(imgui.ImVec4(1.0, 1.0, 1.0, 1.0)),
            2.0  # Thickness
        )

        # Display information
        imgui.text(f"旋转角度: {viewport_manager.rotation_angle:.1f}°")
        imgui.text(f"绘制区域: {int(draw_size.x)} x {int(draw_size.y)}")
        imgui.text(f"正方形大小: {int(square_size)}px")

        imgui.end_child()

    imgui.end()
    imgui.pop_style_color()

    return window_open