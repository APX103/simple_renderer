#!/usr/bin/env python3
"""
TOML 主题应用模块
用于从 TOML 文件加载和应用 ImGui 主题
"""

import tomllib
import re
from imgui_bundle import imgui


def parse_color(color_str: str):
    """
    解析颜色字符串，支持 rgba 格式
    格式: "rgba(r, g, b, a)" 或 "rgb(r, g, b)"
    """
    # 匹配 rgba 格式
    rgba_match = re.match(r'rgba\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)', color_str)
    if rgba_match:
        r, g, b, a = map(float, rgba_match.groups())
        return (r / 255.0, g / 255.0, b / 255.0, a)

    # 匹配 rgb 格式
    rgb_match = re.match(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_str)
    if rgb_match:
        r, g, b = map(float, rgb_match.groups())
        return (r / 255.0, g / 255.0, b / 255.0, 1.0)

    # 如果无法解析，返回默认颜色
    print(f"警告: 无法解析颜色 '{color_str}'，使用默认颜色")
    return (1.0, 1.0, 1.0, 1.0)


def apply_toml_theme(theme_file_path: str):
    """
    从 TOML 文件加载并应用 ImGui 主题

    Args:
        theme_file_path (str): TOML 主题文件路径
    """
    try:
        # 加载 TOML 文件
        with open(theme_file_path, 'rb') as f:
            theme_data = tomllib.load(f)

        # 获取 ImGui 样式对象
        style = imgui.get_style()

        # 应用样式属性
        if 'alpha' in theme_data:
            style.alpha = theme_data['alpha']

        if 'disabledAlpha' in theme_data:
            style.disabled_alpha = theme_data['disabledAlpha']

        if 'windowPadding' in theme_data:
            style.window_padding = imgui.ImVec2(*theme_data['windowPadding'])

        if 'windowRounding' in theme_data:
            style.window_rounding = theme_data['windowRounding']

        if 'windowBorderSize' in theme_data:
            style.window_border_size = theme_data['windowBorderSize']

        if 'windowMinSize' in theme_data:
            style.window_min_size = imgui.ImVec2(*theme_data['windowMinSize'])

        if 'windowTitleAlign' in theme_data:
            style.window_title_align = imgui.ImVec2(*theme_data['windowTitleAlign'])

        if 'windowMenuButtonPosition' in theme_data:
            position_map = {
                "None": imgui.Dir_.none,
                "Left": imgui.Dir_.left,
                "Right": imgui.Dir_.right
            }
            if theme_data['windowMenuButtonPosition'] in position_map:
                style.window_menu_button_position = position_map[theme_data['windowMenuButtonPosition']]

        if 'childRounding' in theme_data:
            style.child_rounding = theme_data['childRounding']

        if 'childBorderSize' in theme_data:
            style.child_border_size = theme_data['childBorderSize']

        if 'popupRounding' in theme_data:
            style.popup_rounding = theme_data['popupRounding']

        if 'popupBorderSize' in theme_data:
            style.popup_border_size = theme_data['popupBorderSize']

        if 'framePadding' in theme_data:
            style.frame_padding = imgui.ImVec2(*theme_data['framePadding'])

        if 'frameRounding' in theme_data:
            style.frame_rounding = theme_data['frameRounding']

        if 'frameBorderSize' in theme_data:
            style.frame_border_size = theme_data['frameBorderSize']

        if 'itemSpacing' in theme_data:
            style.item_spacing = imgui.ImVec2(*theme_data['itemSpacing'])

        if 'itemInnerSpacing' in theme_data:
            style.item_inner_spacing = imgui.ImVec2(*theme_data['itemInnerSpacing'])

        if 'cellPadding' in theme_data:
            style.cell_padding = imgui.ImVec2(*theme_data['cellPadding'])

        if 'indentSpacing' in theme_data:
            style.indent_spacing = theme_data['indentSpacing']

        if 'columnsMinSpacing' in theme_data:
            style.columns_min_spacing = theme_data['columnsMinSpacing']

        if 'scrollbarSize' in theme_data:
            style.scrollbar_size = theme_data['scrollbarSize']

        if 'scrollbarRounding' in theme_data:
            style.scrollbar_rounding = theme_data['scrollbarRounding']

        if 'grabMinSize' in theme_data:
            style.grab_min_size = theme_data['grabMinSize']

        if 'grabRounding' in theme_data:
            style.grab_rounding = theme_data['grabRounding']

        if 'tabRounding' in theme_data:
            style.tab_rounding = theme_data['tabRounding']

        if 'tabBorderSize' in theme_data:
            style.tab_border_size = theme_data['tabBorderSize']

        # 注意: tab_min_width_for_close_button 属性在较新版本的 ImGui 中可用
        # 如果您的 imgui-bundle 版本不支持，请注释掉以下代码
        # if 'tabMinWidthForCloseButton' in theme_data:
        #     style.tab_min_width_for_close_button = theme_data['tabMinWidthForCloseButton']

        if 'colorButtonPosition' in theme_data:
            position_map = {
                "Left": imgui.Dir_.left,
                "Right": imgui.Dir_.right
            }
            if theme_data['colorButtonPosition'] in position_map:
                style.color_button_position = position_map[theme_data['colorButtonPosition']]

        if 'buttonTextAlign' in theme_data:
            style.button_text_align = imgui.ImVec2(*theme_data['buttonTextAlign'])

        if 'selectableTextAlign' in theme_data:
            style.selectable_text_align = imgui.ImVec2(*theme_data['selectableTextAlign'])

        # 应用颜色
        if 'colors' in theme_data:
            colors = theme_data['colors']
            color_enum_map = {
                'Text': imgui.Col_.text,
                'TextDisabled': imgui.Col_.text_disabled,
                'WindowBg': imgui.Col_.window_bg,
                'ChildBg': imgui.Col_.child_bg,
                'PopupBg': imgui.Col_.popup_bg,
                'Border': imgui.Col_.border,
                'BorderShadow': imgui.Col_.border_shadow,
                'FrameBg': imgui.Col_.frame_bg,
                'FrameBgHovered': imgui.Col_.frame_bg_hovered,
                'FrameBgActive': imgui.Col_.frame_bg_active,
                'TitleBg': imgui.Col_.title_bg,
                'TitleBgActive': imgui.Col_.title_bg_active,
                'TitleBgCollapsed': imgui.Col_.title_bg_collapsed,
                'MenuBarBg': imgui.Col_.menu_bar_bg,
                'ScrollbarBg': imgui.Col_.scrollbar_bg,
                'ScrollbarGrab': imgui.Col_.scrollbar_grab,
                'ScrollbarGrabHovered': imgui.Col_.scrollbar_grab_hovered,
                'ScrollbarGrabActive': imgui.Col_.scrollbar_grab_active,
                'CheckMark': imgui.Col_.check_mark,
                'SliderGrab': imgui.Col_.slider_grab,
                'SliderGrabActive': imgui.Col_.slider_grab_active,
                'Button': imgui.Col_.button,
                'ButtonHovered': imgui.Col_.button_hovered,
                'ButtonActive': imgui.Col_.button_active,
                'Header': imgui.Col_.header,
                'HeaderHovered': imgui.Col_.header_hovered,
                'HeaderActive': imgui.Col_.header_active,
                'Separator': imgui.Col_.separator,
                'SeparatorHovered': imgui.Col_.separator_hovered,
                'SeparatorActive': imgui.Col_.separator_active,
                'ResizeGrip': imgui.Col_.resize_grip,
                'ResizeGripHovered': imgui.Col_.resize_grip_hovered,
                'ResizeGripActive': imgui.Col_.resize_grip_active,
                'Tab': imgui.Col_.tab,
                'TabHovered': imgui.Col_.tab_hovered,
                'TabActive': imgui.Col_.tab_selected,  # 注意: imgui-bundle 中使用 tab_selected 而不是 tab_active
                'TabUnfocused': imgui.Col_.tab_dimmed,  # 注意: imgui-bundle 中使用 tab_dimmed 而不是 tab_unfocused
                'TabUnfocusedActive': imgui.Col_.tab_dimmed_selected,  # 注意: imgui-bundle 中使用 tab_dimmed_selected
                'PlotLines': imgui.Col_.plot_lines,
                'PlotLinesHovered': imgui.Col_.plot_lines_hovered,
                'PlotHistogram': imgui.Col_.plot_histogram,
                'PlotHistogramHovered': imgui.Col_.plot_histogram_hovered,
                'TableHeaderBg': imgui.Col_.table_header_bg,
                'TableBorderStrong': imgui.Col_.table_border_strong,
                'TableBorderLight': imgui.Col_.table_border_light,
                'TableRowBg': imgui.Col_.table_row_bg,
                'TableRowBgAlt': imgui.Col_.table_row_bg_alt,
                'TextSelectedBg': imgui.Col_.text_selected_bg,
                'DragDropTarget': imgui.Col_.drag_drop_target,
                'NavHighlight': imgui.Col_.nav_cursor,  # 注意: imgui-bundle 中使用 nav_cursor 而不是 nav_highlight
                'NavWindowingHighlight': imgui.Col_.nav_windowing_highlight,
                'NavWindowingDimBg': imgui.Col_.nav_windowing_dim_bg,
                'ModalWindowDimBg': imgui.Col_.modal_window_dim_bg
            }

            for color_name, color_value in colors.items():
                if color_name in color_enum_map:
                    parsed_color = parse_color(color_value)
                    # 使用 set_color_ 方法设置颜色
                    style.set_color_(color_enum_map[color_name], imgui.ImVec4(*parsed_color))
    except FileNotFoundError:
        print(f"错误: 主题文件未找到: {theme_file_path}")
    except tomllib.TOMLDecodeError as e:
        print(f"错误: TOML 文件格式错误: {e}")
    except Exception as e:
        print(f"错误: 应用主题时发生错误: {e}")
