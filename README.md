# ImGui Bundle 应用程序

一个使用imgui-bundle构建的图形界面应用程序，具有完整的菜单栏和快捷键支持。

## 功能特性

### 菜单栏
- **文件菜单**
  - 保存 (Ctrl+S)
  - 保存副本 (Ctrl+A)
  - 加载 (Ctrl+L)
  - 导入资产 (Ctrl+I)
  - 退出

- **编辑菜单**
  - 撤销 (Ctrl+Z)
  - 重做 (Ctrl+Shift+Z)

- **录制菜单**
  - 开始新录制 (Ctrl+T)

- **渲染菜单**
  - 渲染预览 (P) - 可切换状态
  - 渲染导出 (Ctrl+R)
  - 渲染设置 (Ctrl+O)
  - 导出当前帧 (Ctrl+P)

- **帮助菜单**
  - 关于

### 快捷键支持
所有菜单项都支持对应的快捷键操作，快捷键会在菜单项旁边显示。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行应用程序

```bash
python run.py
```

或者直接运行：

```bash
python main.py
```

## 项目结构

- `main.py` - 主应用程序文件
- `run.py` - 启动脚本
- `requirements.txt` - Python依赖
- `README.md` - 项目说明

## 技术栈

- **imgui-bundle**: 完整的ImGui Python绑定套件
- **ImGui**: 即时模式图形用户界面
- **Hello ImGui**: 应用程序框架和窗口管理

## 开发说明

应用程序使用面向对象设计，主要类为 `ImGuiApp`，包含：
- 菜单栏和快捷键处理
- 状态管理
- GUI布局和控件

应用程序使用imgui-bundle的Hello ImGui框架，自动处理窗口创建、事件循环和渲染。

## 扩展功能

您可以在相应的方法中添加实际的功能实现：
- `save_file()` - 文件保存逻辑
- `load_file()` - 文件加载逻辑
- `start_new_recording()` - 录制功能
- `render_export()` - 渲染导出功能
- 等等...

## 许可证

MIT License