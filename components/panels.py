#!/usr/bin/env python3
"""
面板组件
"""

from imgui_bundle import imgui


def show_status_panel(file_path: str, recording: bool, render_preview: bool):
    """显示状态面板"""
    # 设置可停靠
    imgui.set_next_window_dock_id(imgui.get_id("DockSpace"), imgui.Cond_.first_use_ever)
    imgui.begin("状态面板")
    imgui.text(f"当前文件: {file_path if file_path else '未加载'}")
    imgui.text(f"录制状态: {'正在录制' if recording else '未录制'}")
    imgui.text(f"渲染预览: {'开启' if render_preview else '关闭'}")
    imgui.end()


def show_control_panel(recording: bool) -> bool:
    """显示控制面板"""
    # 设置可停靠
    imgui.set_next_window_dock_id(imgui.get_id("DockSpace"), imgui.Cond_.first_use_ever)
    imgui.begin("控制面板")
    imgui.text("欢迎使用ImGui Bundle应用程序！")
    imgui.text("您可以使用顶部菜单栏来访问各种功能。")

    imgui.separator()
    imgui.text("示例控件:")

    # 示例按钮
    if imgui.button("测试按钮"):
        print("测试按钮被点击!")

    imgui.same_line()

    # 示例复选框
    clicked, new_recording = imgui.checkbox("录制", recording)
    imgui.end()

    return new_recording if clicked else recording


def show_info_panel():
    """显示信息面板"""
    # 设置可停靠
    imgui.set_next_window_dock_id(imgui.get_id("DockSpace"), imgui.Cond_.first_use_ever)
    imgui.begin("信息面板")
    imgui.text("应用程序信息:")
    imgui.text("- 基于imgui-bundle")
    imgui.text("- 支持dock space")
    imgui.text("- 可停靠面板")
    imgui.end()


def show_demo_panels(file_path: str, recording: bool, render_preview: bool) -> bool:
    """显示所有面板"""
    show_status_panel(file_path, recording, render_preview)
    new_recording = show_control_panel(recording)
    show_info_panel()

    return new_recording