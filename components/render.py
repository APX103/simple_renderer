#!/usr/bin/env python3
"""
渲染设置面板组件
"""

from imgui_bundle import imgui


def show_render_settings_panel():
    """显示渲染设置面板"""
    # 设置可停靠
    imgui.set_next_window_dock_id(imgui.get_id("DockSpace"), imgui.Cond_.first_use_ever)

    # 设置窗口默认大小
    imgui.set_next_window_size(imgui.ImVec2(500, 540), imgui.Cond_.first_use_ever)

    keep_open = True

    if imgui.begin("渲染设置", True):
        # 基本信息部分
        imgui.text("基本信息")
        imgui.separator()

        # 分辨率设置
        imgui.text("分辨率:")
        imgui.same_line()
        resolution_width = 1280
        resolution_height = 720
        imgui.text(f"{resolution_width} × {resolution_height}")

        # 渲染器类型
        imgui.text("渲染器类型:")
        imgui.same_line()
        renderer_types = ["rasterizer", "path_tracer", "ray_tracer"]
        current_renderer = "rasterizer"

        if imgui.begin_combo("##renderer_type", current_renderer):
            for renderer in renderer_types:
                is_selected = (renderer == current_renderer)
                if imgui.selectable(renderer, is_selected):
                    current_renderer = renderer
                if is_selected:
                    imgui.set_item_default_focus()
            imgui.end_combo()

        imgui.spacing()

        # 光栅化渲染部分
        if current_renderer == "rasterizer":
            imgui.text("光栅化渲染设置")
            imgui.separator()

            # 抗锯齿设置
            imgui.text("抗锯齿:")
            imgui.same_line()
            aa_options = ["OFF", "FXAA", "MSAA 2x", "MSAA 4x", "MSAA 8x"]
            current_aa = "OFF"

            if imgui.begin_combo("##antialiasing", current_aa):
                for option in aa_options:
                    is_selected = (option == current_aa)
                    if imgui.selectable(option, is_selected):
                        current_aa = option
                    if is_selected:
                        imgui.set_item_default_focus()
                imgui.end_combo()

            # 颜色类型
            imgui.text("颜色类型:")
            imgui.same_line()
            color_types = ["texture", "normal", "depth", "albedo"]
            current_color_type = "texture"

            if imgui.begin_combo("##color_type", current_color_type):
                for color_type in color_types:
                    is_selected = (color_type == current_color_type)
                    if imgui.selectable(color_type, is_selected):
                        current_color_type = color_type
                    if is_selected:
                        imgui.set_item_default_focus()
                imgui.end_combo()

            imgui.spacing()

            # 另一处光栅化渲染相关设置
            imgui.text("高级光栅化设置")
            imgui.separator()

            # 抗锯齿设置
            imgui.text("抗锯齿:")
            imgui.same_line()
            aa_options2 = ["OFF", "FXAA", "MSAA 2x", "MSAA 4x", "MSAA 8x"]
            current_aa2 = "OFF"

            if imgui.begin_combo("##antialiasing2", current_aa2):
                for option in aa_options2:
                    is_selected = (option == current_aa2)
                    if imgui.selectable(option, is_selected):
                        current_aa2 = option
                    if is_selected:
                        imgui.set_item_default_focus()
                imgui.end_combo()

            # 光线追踪开关
            imgui.text("光线追踪:")
            imgui.same_line()
            ray_tracing_enabled = False
            _, ray_tracing_enabled = imgui.checkbox("##ray_tracing", ray_tracing_enabled)

            # 环境光遮蔽开关
            imgui.text("环境光遮蔽:")
            imgui.same_line()
            ambient_occlusion_enabled = False
            _, ambient_occlusion_enabled = imgui.checkbox("##ambient_occlusion", ambient_occlusion_enabled)

        # 路径追踪渲染部分
        elif current_renderer == "path_tracer":
            imgui.text("路径追踪渲染设置")
            imgui.separator()

            # 采样数设置
            imgui.text("采样数:")
            imgui.same_line()
            samples = 64
            imgui.text(f"{samples}")

            # 其他路径追踪相关设置可以在这里添加
            imgui.text("最大深度:")
            imgui.same_line()
            max_depth = 8
            imgui.text(f"{max_depth}")

            imgui.text("俄罗斯轮盘:")
            imgui.same_line()
            russian_roulette = True
            _, russian_roulette = imgui.checkbox("##russian_roulette", russian_roulette)

        # 光线追踪渲染部分
        elif current_renderer == "ray_tracer":
            imgui.text("光线追踪渲染设置")
            imgui.separator()

            imgui.text("反射次数:")
            imgui.same_line()
            reflection_depth = 4
            imgui.text(f"{reflection_depth}")

            imgui.text("阴影质量:")
            imgui.same_line()
            shadow_quality = "High"
            shadow_qualities = ["Low", "Medium", "High", "Ultra"]

            if imgui.begin_combo("##shadow_quality", shadow_quality):
                for quality in shadow_qualities:
                    is_selected = (quality == shadow_quality)
                    if imgui.selectable(quality, is_selected):
                        shadow_quality = quality
                    if is_selected:
                        imgui.set_item_default_focus()
                imgui.end_combo()

        imgui.spacing()
        imgui.separator()

        # 保存和取消按钮
        imgui.dummy((0, 20))  # 添加一些垂直间距

        # 按钮居中显示
        button_width = 80
        button_height = 0
        total_width = button_width * 2 + 10  # 两个按钮宽度 + 间距
        available_width = imgui.get_content_region_avail().x
        offset = (available_width - total_width) * 0.5

        imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + offset)

        if imgui.button("保存", imgui.ImVec2(button_width, button_height)):
            # 保存设置的逻辑
            print("渲染设置已保存")

        imgui.same_line()

        if imgui.button("取消", imgui.ImVec2(button_width, button_height)):
            # 取消设置的逻辑
            print("渲染设置已取消")
            keep_open = False

    # 检查窗口是否被关闭
    if not imgui.is_window_appearing() and not imgui.is_window_collapsed():
        if not imgui.is_window_focused() and imgui.is_key_pressed(imgui.Key.escape):
            keep_open = False

    imgui.end()

    return keep_open