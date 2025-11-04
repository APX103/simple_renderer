#!/usr/bin/env python3
"""
Dock Space 组件
"""

from imgui_bundle import imgui


def setup_dock_space():
    """设置dock space"""
    # 获取视口大小
    viewport = imgui.get_main_viewport()
    imgui.set_next_window_pos(viewport.work_pos)
    imgui.set_next_window_size(viewport.work_size)

    # 创建dock space窗口
    window_flags = (imgui.WindowFlags_.no_title_bar |
                    imgui.WindowFlags_.no_collapse |
                    imgui.WindowFlags_.no_resize |
                    imgui.WindowFlags_.no_move |
                    imgui.WindowFlags_.no_bring_to_front_on_focus |
                    imgui.WindowFlags_.no_nav_focus)

    imgui.push_style_var(imgui.StyleVar_.window_padding, imgui.ImVec2(0.0, 0.0))
    imgui.begin("DockSpace", True, window_flags)
    imgui.pop_style_var()

    # 提交dock space
    dockspace_id = imgui.get_id("DockSpace")
    imgui.dock_space(dockspace_id, imgui.ImVec2(0.0, 0.0))

    imgui.end()