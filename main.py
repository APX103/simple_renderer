#!/usr/bin/env python3
import glfw
import OpenGL.GL as gl
from imgui_bundle import imgui
import sys
import ctypes
from components import show_demo_panels, show_render_settings_panel
from themes import apply_theme


def create_window(width=1280, height=720, title="ImGui App"):
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

    # 设置ImGui样式
    style = imgui.get_style()
    style.window_rounding = 0.0

    # 设置平台绑定
    window_address = ctypes.cast(window, ctypes.c_void_p).value
    imgui.backends.glfw_init_for_opengl(window_address, True)
    imgui.backends.opengl3_init("#version 130")


def run_imgui_app(gui_function, window_title="Pulse", width=1280, height=720):
    """运行ImGui应用程序"""
    window = create_window(width, height, window_title)
    init_imgui(window)

    # 主循环
    while not glfw.window_should_close(window):
        glfw.poll_events()

        # 开始新帧
        imgui.backends.opengl3_new_frame()
        imgui.backends.glfw_new_frame()
        imgui.new_frame()

        # 调用用户GUI函数
        gui_function()
        
        apply_theme('./themes/Light_Orange.toml')
        # apply_theme('./themes/Soft_Cherry.toml')

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


class ImGuiApp:
    """迁移后的ImGui应用程序类"""

    def __init__(self):
        self.show_about = False
        self.render_preview = True

        # 状态变量
        self.file_path = ""
        self.recording = False
        self.show_render_settings = False

        # 字体相关
        self.font = None
        self.font_loaded = False

    def handle_shortcuts(self):
        """处理快捷键"""
        io = imgui.get_io()

        # 检查Control键是否按下
        ctrl_pressed = io.key_ctrl
        shift_pressed = io.key_shift

        # 文件菜单快捷键
        if ctrl_pressed and imgui.is_key_pressed(imgui.Key.s):
            self.save_file()
        elif ctrl_pressed and imgui.is_key_pressed(imgui.Key.a):
            self.save_copy()
        elif ctrl_pressed and imgui.is_key_pressed(imgui.Key.l):
            self.load_file()
        elif ctrl_pressed and imgui.is_key_pressed(imgui.Key.i):
            self.import_assets()

        # 编辑菜单快捷键
        if ctrl_pressed and imgui.is_key_pressed(imgui.Key.z):
            if shift_pressed:
                self.redo()
            else:
                self.undo()

        # 录制菜单快捷键
        if ctrl_pressed and imgui.is_key_pressed(imgui.Key.t):
            self.start_new_recording()

        # 渲染菜单快捷键
        if imgui.is_key_pressed(imgui.Key.p):
            if ctrl_pressed:
                self.export_current_frame()
            else:
                self.render_preview = not self.render_preview
        elif ctrl_pressed and imgui.is_key_pressed(imgui.Key.r):
            self.render_export()
        elif ctrl_pressed and imgui.is_key_pressed(imgui.Key.o):
            self.render_settings()

    def create_menu_bar(self):
        """创建顶部菜单栏"""
        if imgui.begin_main_menu_bar():

            # 文件菜单
            if imgui.begin_menu("文件", True):
                if imgui.menu_item("保存", "Ctrl+S", False, True)[0]:
                    self.save_file()
                if imgui.menu_item("保存副本", "Ctrl+A", False, True)[0]:
                    self.save_copy()
                if imgui.menu_item("加载", "Ctrl+L", False, True)[0]:
                    self.load_file()
                imgui.separator()
                if imgui.menu_item("导入资产", "Ctrl+I", False, True)[0]:
                    self.import_assets()
                imgui.separator()
                if imgui.menu_item("退出", "", False, True)[0]:
                    sys.exit(0)
                imgui.end_menu()

            # 编辑菜单
            if imgui.begin_menu("编辑", True):
                if imgui.menu_item("撤销", "Ctrl+Z", False, True)[0]:
                    self.undo()
                if imgui.menu_item("重做", "Ctrl+Shift+Z", False, True)[0]:
                    self.redo()
                imgui.end_menu()

            # 录制菜单
            if imgui.begin_menu("录制", True):
                if imgui.menu_item("开始新录制", "Ctrl+T", False, True)[0]:
                    self.start_new_recording()
                imgui.end_menu()

            # 渲染菜单
            if imgui.begin_menu("渲染", True):
                if imgui.menu_item("渲染预览", "P", False, True)[0]:
                    self.render_preview = not self.render_preview
                if imgui.menu_item("渲染导出", "Ctrl+R", False, True)[0]:
                    self.render_export()
                if imgui.menu_item("渲染设置", "Ctrl+O", False, True)[0]:
                    self.render_settings()
                if imgui.menu_item("导出当前帧", "Ctrl+P", False, True)[0]:
                    self.export_current_frame()
                imgui.end_menu()

            # 帮助菜单
            if imgui.begin_menu("帮助", True):
                if imgui.menu_item("关于", "", False, True)[0]:
                    self.show_about = True
                imgui.end_menu()

            imgui.end_main_menu_bar()

    def show_about_window(self):
        """显示关于窗口"""
        if self.show_about:
            imgui.set_next_window_size(imgui.ImVec2(300, 200))
            # imgui.begin() 返回一个布尔值，表示窗口是否打开
            if imgui.begin("关于", True):
                imgui.text("ImGui Bundle 应用程序")
                imgui.text("版本: 1.0.0")
                imgui.text("作者: Your Name")
                imgui.separator()
                imgui.text("一个使用imgui-bundle构建的")
                imgui.text("简单图形界面应用程序")

                if imgui.button("关闭"):
                    self.show_about = False
                imgui.end()
            else:
                # 用户点击了小叉叉关闭窗口
                self.show_about = False
                imgui.end()

    # 菜单功能实现
    def save_file(self):
        """保存文件"""
        print("执行保存文件操作")

    def save_copy(self):
        """保存副本"""
        print("执行保存副本操作")

    def load_file(self):
        """加载文件"""
        print("执行加载文件操作")

    def import_assets(self):
        """导入资产"""
        print("执行导入资产操作")

    def undo(self):
        """撤销操作"""
        print("执行撤销操作")

    def redo(self):
        """重做操作"""
        print("执行重做操作")

    def start_new_recording(self):
        """开始新录制"""
        print("开始新录制")
        self.recording = True

    def render_export(self):
        """渲染导出"""
        print("执行渲染导出操作")

    def render_settings(self):
        """渲染设置"""
        print("打开渲染设置")
        self.show_render_settings = True

    def export_current_frame(self):
        """导出当前帧"""
        print("导出当前帧")

    def load_custom_font(self):
        """加载自定义字体"""
        try:
            io = imgui.get_io()

            # 加载自定义字体
            font_path = "assets/heiti.ttf"
            self.font = io.fonts.add_font_from_file_ttf(
                font_path,
                16.0  # 字体大小
            )

            print(f"成功加载字体: {font_path}")

        except Exception as e:
            print(f"字体加载失败: {e}")
            # 如果加载失败，使用默认字体
            self.font = io.fonts.add_font_default()

    def gui(self):
        """主要的GUI函数"""
        # 处理快捷键
        self.handle_shortcuts()

        # 在第一次运行时加载字体
        if not self.font_loaded:
            self.load_custom_font()
            self.font_loaded = True

        # 应用自定义字体
        if self.font:
            imgui.push_font(self.font, 16.0)

        # 创建界面
        imgui.dock_space_over_viewport()
        self.create_menu_bar()
        self.recording = show_demo_panels(self.file_path, self.recording, self.render_preview)
        self.show_about_window()

        # 显示渲染设置面板
        if self.show_render_settings:
            self.show_render_settings = show_render_settings_panel()

        # 恢复字体
        if self.font:
            imgui.pop_font()


def main():
    """主函数"""
    app = ImGuiApp()
    run_imgui_app(app.gui, "Pulse - Migrated")


if __name__ == "__main__":
    main()