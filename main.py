#!/usr/bin/env python3
"""
使用imgui-bundle但不用hello_imgui的简化版本
"""

from imgui_bundle import imgui, immapp
import sys

class ImGuiApp:
    def __init__(self):
        self.show_about = False
        self.render_preview = True

        # 状态变量
        self.file_path = ""
        self.recording = False

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
                if imgui.menu_item("保存", "Ctrl+S", False)[0]:
                    self.save_file()
                if imgui.menu_item("保存副本", "Ctrl+A", False)[0]:
                    self.save_copy()
                if imgui.menu_item("加载", "Ctrl+L", False)[0]:
                    self.load_file()
                imgui.separator()
                if imgui.menu_item("导入资产", "Ctrl+I", False)[0]:
                    self.import_assets()
                imgui.separator()
                if imgui.menu_item("退出", "", False)[0]:
                    sys.exit(0)
                imgui.end_menu()

            # 编辑菜单
            if imgui.begin_menu("编辑", True):
                if imgui.menu_item("撤销", "Ctrl+Z", False)[0]:
                    self.undo()
                if imgui.menu_item("重做", "Ctrl+Shift+Z", False)[0]:
                    self.redo()
                imgui.end_menu()

            # 录制菜单
            if imgui.begin_menu("录制", True):
                if imgui.menu_item("开始新录制", "Ctrl+T", False)[0]:
                    self.start_new_recording()
                imgui.end_menu()

            # 渲染菜单
            if imgui.begin_menu("渲染", True):
                if imgui.menu_item("渲染预览", "P", False)[0]:
                    self.render_preview = not self.render_preview
                if imgui.menu_item("渲染导出", "Ctrl+R", False)[0]:
                    self.render_export()
                if imgui.menu_item("渲染设置", "Ctrl+O", False)[0]:
                    self.render_settings()
                if imgui.menu_item("导出当前帧", "Ctrl+P", False)[0]:
                    self.export_current_frame()
                imgui.end_menu()

            # 帮助菜单
            if imgui.begin_menu("帮助", True):
                if imgui.menu_item("关于", "", False)[0]:
                    self.show_about = True
                imgui.end_menu()

            imgui.end_main_menu_bar()

    def show_about_window(self):
        """显示关于窗口"""
        if self.show_about:
            imgui.set_next_window_size(imgui.ImVec2(300, 200))
            imgui.begin("关于", True)
            imgui.text("ImGui Bundle 应用程序")
            imgui.text("版本: 1.0.0")
            imgui.text("作者: Your Name")
            imgui.separator()
            imgui.text("一个使用imgui-bundle构建的")
            imgui.text("简单图形界面应用程序")

            if imgui.button("关闭"):
                self.show_about = False
            imgui.end()

    def setup_dock_space(self):
        """设置dock space"""
        # 获取视口大小
        viewport = imgui.get_main_viewport()
        imgui.set_next_window_pos(viewport.work_pos)
        imgui.set_next_window_size(viewport.work_size)
        
        # 创建dock space窗口 - 移除no_docking标志
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

    def show_panels(self):
        """显示各种面板"""
        # 状态面板 - 设置可停靠
        imgui.set_next_window_dock_id(imgui.get_id("MyDockSpace"), imgui.Cond_.first_use_ever)
        imgui.begin("状态面板")
        imgui.text(f"当前文件: {self.file_path if self.file_path else '未加载'}")
        imgui.text(f"录制状态: {'正在录制' if self.recording else '未录制'}")
        imgui.text(f"渲染预览: {'开启' if self.render_preview else '关闭'}")
        imgui.end()

        # 控制面板 - 设置可停靠
        imgui.set_next_window_dock_id(imgui.get_id("MyDockSpace"), imgui.Cond_.first_use_ever)
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
        _, self.recording = imgui.checkbox("录制", self.recording)
        imgui.end()

        # 信息面板 - 设置可停靠
        imgui.set_next_window_dock_id(imgui.get_id("MyDockSpace"), imgui.Cond_.first_use_ever)
        imgui.begin("信息面板")
        imgui.text("应用程序信息:")
        imgui.text("- 基于imgui-bundle")
        imgui.text("- 支持dock space")
        imgui.text("- 可停靠面板")
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
        self.create_menu_bar()
        self.setup_dock_space()
        self.show_panels()
        self.show_about_window()

        # 恢复字体
        if self.font:
            imgui.pop_font()

def main():
    """主函数"""
    app = ImGuiApp()

    # 使用immapp运行应用程序
    runner_params = immapp.RunnerParams()
    runner_params.app_window_params.window_title = "Pulse"
    runner_params.app_window_params.window_geometry.size = (1280, 720)
    runner_params.ini_filename = ""  # 禁用INI文件
    runner_params.callbacks.show_gui = app.gui

    immapp.run(runner_params)

if __name__ == "__main__":
    main()