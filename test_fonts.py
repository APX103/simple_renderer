#!/usr/bin/env python3
import glfw
import OpenGL.GL as gl
from imgui_bundle import imgui
import sys
import ctypes

def create_window(width=800, height=600, title="Font Test"):
    """创建GLFW窗口"""
    if not glfw.init():
        raise Exception("无法初始化GLFW")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(width, height, title, None, None)
    if not window:
        glfw.terminate()
        raise Exception("无法创建GLFW窗口")

    glfw.make_context_current(window)
    return window

def init_imgui(window):
    """初始化ImGui"""
    imgui.create_context()

    # 设置ImGui IO
    io = imgui.get_io()
    io.config_flags |= imgui.ConfigFlags_.docking_enable
    io.config_flags |= imgui.ConfigFlags_.viewports_enable

    # 设置平台绑定
    window_address = ctypes.cast(window, ctypes.c_void_p).value
    imgui.backends.glfw_init_for_opengl(window_address, True)
    imgui.backends.opengl3_init("#version 130")

def load_fonts():
    """加载字体并测试合并"""
    io = imgui.get_io()

    try:
        # 创建字体配置
        font_config = imgui.ImFontConfig()

        # 首先加载heiti字体作为主字体
        main_font = io.fonts.add_font_from_file_ttf(
            "assets/heiti.ttf",
            16.0,
            font_cfg=font_config
        )

        # 为表情字体创建新的配置，启用合并模式
        emoji_config = imgui.ImFontConfig()
        emoji_config.merge_mode = True

        # 设置表情字体的字符范围（简化版本）
        # imgui-bundle会自动处理字符范围

        # 加载NotoColorEmoji字体并合并到主字体中
        emoji_font = io.fonts.add_font_from_file_ttf(
            "assets/NotoColorEmoji.ttf",
            16.0,
            font_cfg=emoji_config
        )

        print("字体加载成功！")
        print(f"主字体: {main_font}")
        print(f"表情字体: {emoji_font}")

        return main_font

    except Exception as e:
        print(f"字体加载失败: {e}")
        return io.fonts.add_font_default()

def main():
    """主函数"""
    window = create_window()
    init_imgui(window)

    # 加载字体
    font = load_fonts()

    # 构建字体纹理（imgui-bundle会自动处理）
    print("字体加载完成")

    # 测试显示一些文本
    while not glfw.window_should_close(window):
        glfw.poll_events()

        # 开始新帧
        imgui.backends.opengl3_new_frame()
        imgui.backends.glfw_new_frame()
        imgui.new_frame()

        # 使用字体显示测试文本
        if font:
            imgui.push_font(font, 16.0)

        # 显示测试文本
        imgui.begin("字体测试")
        imgui.text("中文字体测试: 你好世界")
        imgui.text("表情符号测试: 😀😃😄😁😆😅😂🤣")
        imgui.text("混合测试: 你好😊世界🎉")
        imgui.end()

        if font:
            imgui.pop_font()

        # 渲染
        imgui.render()

        gl.glClearColor(0.1, 0.1, 0.1, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.backends.opengl3_render_draw_data(imgui.get_draw_data())

        # 处理多视口
        if imgui.get_io().config_flags & imgui.ConfigFlags_.viewports_enable:
            backup_current_context = glfw.get_current_context()
            imgui.update_platform_windows()
            imgui.render_platform_windows_default()
            glfw.make_context_current(backup_current_context)

        glfw.swap_buffers(window)

    # 清理
    imgui.backends.opengl3_shutdown()
    imgui.backends.glfw_shutdown()
    imgui.destroy_context()
    glfw.terminate()

if __name__ == "__main__":
    main()