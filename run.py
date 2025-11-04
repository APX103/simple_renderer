#!/usr/bin/env python3
"""
启动脚本 - ImGui Bundle 应用程序
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import main

    print("启动 ImGui Bundle 应用程序...")
    print("功能特性:")
    print("- 完整的顶部菜单栏")
    print("- 文件、编辑、录制、渲染、帮助菜单")
    print("- 完整的快捷键支持")
    print("- 响应式界面")
    print()

    main()

except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所有依赖:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"运行时错误: {e}")
    sys.exit(1)