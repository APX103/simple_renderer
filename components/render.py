#!/usr/bin/env python3
"""
渲染设置面板组件
"""

from imgui_bundle import imgui

# 渲染设置状态变量
render_settings = {
    # 基本信息
    "resolution_width": 1280,
    "resolution_height": 720,
    "renderer_type": "rasterizer",

    # 光栅化渲染设置
    "antialiasing": "OFF",
    "color_type": "texture",
    "antialiasing2": "OFF",
    "ray_tracing_enabled": False,
    "ambient_occlusion_enabled": False,

    # 路径追踪渲染设置
    "samples": 64,
    "max_depth": 8,
    "russian_roulette": True,

    # 光线追踪渲染设置
    "reflection_depth": 4,
    "shadow_quality": "High"
}


def show_render_settings_panel(open: bool) -> bool:
    """显示渲染设置面板"""
    # 设置可停靠
    imgui.set_next_window_dock_id(imgui.get_id("DockSpace"), imgui.Cond_.first_use_ever)

    # 设置窗口默认大小
    imgui.set_next_window_size(imgui.ImVec2(500, 540), imgui.Cond_.first_use_ever)

    keep_open = True

    # 使用imgui.begin返回的布尔值来判断窗口是否应该关闭
    window_open = imgui.begin("渲染设置", True)
    if window_open:
        # 基本信息部分
        imgui.text("基本信息")
        imgui.separator()

        # 分辨率设置
        imgui.text("分辨率:")
        imgui.same_line()
        imgui.text(f"{render_settings['resolution_width']} × {render_settings['resolution_height']}")

        # 渲染器类型 - 使用combo替代begin_combo
        imgui.text("渲染器类型:")
        imgui.same_line()
        renderer_types = ["rasterizer", "path_tracer", "ray_tracer"]

        # 获取当前选择的索引
        current_index = renderer_types.index(render_settings['renderer_type'])

        # 使用imgui.combo替代begin_combo
        clicked, new_index = imgui.combo("##renderer_type", current_index, renderer_types)
        if clicked:
            render_settings['renderer_type'] = renderer_types[new_index]

        imgui.spacing()

        # 光栅化渲染部分
        if render_settings['renderer_type'] == "rasterizer":
            imgui.text("光栅化渲染设置")
            imgui.separator()

            # 抗锯齿设置 - 使用combo替代begin_combo
            imgui.text("抗锯齿:")
            imgui.same_line()
            aa_options = ["OFF", "FXAA", "MSAA 2x", "MSAA 4x", "MSAA 8x"]

            # 获取当前选择的索引
            current_index = aa_options.index(render_settings['antialiasing'])

            # 使用imgui.combo替代begin_combo
            clicked, new_index = imgui.combo("##antialiasing", current_index, aa_options)
            if clicked:
                render_settings['antialiasing'] = aa_options[new_index]

            # 颜色类型 - 使用combo替代begin_combo
            imgui.text("颜色类型:")
            imgui.same_line()
            color_types = ["texture", "normal", "depth", "albedo"]

            # 获取当前选择的索引
            current_index = color_types.index(render_settings['color_type'])

            # 使用imgui.combo替代begin_combo
            clicked, new_index = imgui.combo("##color_type", current_index, color_types)
            if clicked:
                render_settings['color_type'] = color_types[new_index]

            imgui.spacing()

            # 另一处光栅化渲染相关设置
            imgui.text("高级光栅化设置")
            imgui.separator()

            # 抗锯齿设置
            imgui.text("抗锯齿:")
            imgui.same_line()
            aa_options2 = ["OFF", "FXAA", "MSAA 2x", "MSAA 4x", "MSAA 8x"]

            if imgui.begin_combo("##antialiasing2", render_settings['antialiasing2']):
                for option in aa_options2:
                    is_selected = (option == render_settings['antialiasing2'])
                    if imgui.selectable(option, is_selected):
                        render_settings['antialiasing2'] = option
                    if is_selected:
                        imgui.set_item_default_focus()
                imgui.end_combo()

            # 光线追踪开关
            imgui.text("光线追踪:")
            imgui.same_line()
            _, render_settings['ray_tracing_enabled'] = imgui.checkbox("##ray_tracing", render_settings['ray_tracing_enabled'])

            # 环境光遮蔽开关
            imgui.text("环境光遮蔽:")
            imgui.same_line()
            _, render_settings['ambient_occlusion_enabled'] = imgui.checkbox("##ambient_occlusion", render_settings['ambient_occlusion_enabled'])

        # 路径追踪渲染部分
        elif render_settings['renderer_type'] == "path_tracer":
            imgui.text("路径追踪渲染设置")
            imgui.separator()

            # 采样数设置
            imgui.text("采样数:")
            imgui.same_line()
            imgui.text(f"{render_settings['samples']}")

            # 其他路径追踪相关设置可以在这里添加
            imgui.text("最大深度:")
            imgui.same_line()
            imgui.text(f"{render_settings['max_depth']}")

            imgui.text("俄罗斯轮盘:")
            imgui.same_line()
            _, render_settings['russian_roulette'] = imgui.checkbox("##russian_roulette", render_settings['russian_roulette'])

        # 光线追踪渲染部分
        elif render_settings['renderer_type'] == "ray_tracer":
            imgui.text("光线追踪渲染设置")
            imgui.separator()

            imgui.text("反射次数:")
            imgui.same_line()
            imgui.text(f"{render_settings['reflection_depth']}")

            imgui.text("阴影质量:")
            imgui.same_line()
            shadow_qualities = ["Low", "Medium", "High", "Ultra"]

            if imgui.begin_combo("##shadow_quality", render_settings['shadow_quality']):
                for quality in shadow_qualities:
                    is_selected = (quality == render_settings['shadow_quality'])
                    if imgui.selectable(quality, is_selected):
                        render_settings['shadow_quality'] = quality
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
            print("渲染设置已保存:")
            print(f"  分辨率: {render_settings['resolution_width']} × {render_settings['resolution_height']}")
            print(f"  渲染器类型: {render_settings['renderer_type']}")

            if render_settings['renderer_type'] == "rasterizer":
                print(f"  抗锯齿: {render_settings['antialiasing']}")
                print(f"  颜色类型: {render_settings['color_type']}")
                print(f"  高级抗锯齿: {render_settings['antialiasing2']}")
                print(f"  光线追踪: {'开启' if render_settings['ray_tracing_enabled'] else '关闭'}")
                print(f"  环境光遮蔽: {'开启' if render_settings['ambient_occlusion_enabled'] else '关闭'}")
            elif render_settings['renderer_type'] == "path_tracer":
                print(f"  采样数: {render_settings['samples']}")
                print(f"  最大深度: {render_settings['max_depth']}")
                print(f"  俄罗斯轮盘: {'开启' if render_settings['russian_roulette'] else '关闭'}")
            elif render_settings['renderer_type'] == "ray_tracer":
                print(f"  反射次数: {render_settings['reflection_depth']}")
                print(f"  阴影质量: {render_settings['shadow_quality']}")

            keep_open = False  # 保存后关闭窗口

        imgui.same_line()

        if imgui.button("取消", imgui.ImVec2(button_width, button_height)):
            # 取消设置的逻辑
            print("渲染设置已取消")
            keep_open = False

    imgui.end()

    # 如果窗口被关闭（通过关闭按钮或ESC键），或者用户点击了保存/取消按钮，则返回False
    # 否则返回True保持窗口打开
    return window_open and keep_open