#!/usr/bin/env python3
"""
对象属性面板组件
支持不同对象类型的属性展示与设置
"""

from imgui_bundle import imgui
import os

# 全局状态变量 - 存储当前选中的对象和属性
selected_object = {
    "type": "none",  # "mesh", "material", "camera", "light", "none"
    "name": "",
    "properties": {}
}

# 对象属性默认值
object_properties = {
    # 网格对象属性
    "mesh": {
        "name": "未命名网格",
        "visible": True,
        "position": [0.0, 0.0, 0.0],
        "rotation": [0.0, 0.0, 0.0],
        "scale": [1.0, 1.0, 1.0],
        "material": "default"
    },

    # 材质对象属性
    "material": {
        "name": "未命名材质",
        "albedo_texture": "",
        "normal_texture": "",
        "metallic_texture": "",
        "roughness_texture": "",
        "metallic_value": 0.0,
        "roughness_value": 0.5
    },

    # 摄像机对象属性
    "camera": {
        "name": "未命名摄像机",
        "position": [0.0, 0.0, 5.0],
        "rotation": [0.0, 0.0, 0.0],
        "fov_x": 60.0,
        "fov_y": 45.0,
        "near_clip": 0.1,
        "far_clip": 100.0
    },

    # HDRI光照对象属性
    "light": {
        "name": "未命名HDRI",
        "hdri_file": "",
        "intensity": 1.0,
        "rotation": 0.0
    }
}


def select_object(obj_type, obj_name):
    """选择对象并加载其属性"""
    global selected_object

    if obj_type in object_properties:
        selected_object["type"] = obj_type
        selected_object["name"] = obj_name
        selected_object["properties"] = object_properties[obj_type].copy()
    else:
        selected_object["type"] = "none"
        selected_object["name"] = ""
        selected_object["properties"] = {}


def show_property_panel(open: bool) -> bool:
    """显示属性面板 """
    # 设置可停靠
    imgui.set_next_window_dock_id(imgui.get_id("DockSpace"), imgui.Cond_.first_use_ever)

    # 设置窗口默认大小
    imgui.set_next_window_size(imgui.ImVec2(400, 600), imgui.Cond_.first_use_ever)

    keep_open = True
    window_open = imgui.begin("属性面板", open)[1]

    if window_open:
        # 根据选中的对象类型显示不同的属性面板
        if selected_object["type"] == "none":
            show_no_selection()
        elif selected_object["type"] == "mesh":
            show_mesh_properties()
        elif selected_object["type"] == "material":
            show_material_properties()
        elif selected_object["type"] == "camera":
            show_camera_properties()
        elif selected_object["type"] == "light":
            show_light_properties()

    imgui.end()
    return window_open and keep_open


def show_no_selection():
    """未选中对象时的显示"""
    imgui.text("未选中对象")
    imgui.separator()
    imgui.text("请选择一个对象以查看其属性")

    # 测试按钮 - 用于演示不同对象类型
    imgui.spacing()
    imgui.text("测试选择:")

    if imgui.button("选择网格"):
        select_object("mesh", "测试网格")
    imgui.same_line()
    if imgui.button("选择材质"):
        select_object("material", "测试材质")
    imgui.same_line()
    if imgui.button("选择摄像机"):
        select_object("camera", "测试摄像机")
    imgui.same_line()
    if imgui.button("选择HDRI"):
        select_object("light", "测试HDRI")


def show_mesh_properties():
    """显示网格对象属性"""
    props = selected_object["properties"]

    # 显示对象名称和类型
    imgui.text(f"对象: {selected_object['name']}")
    imgui.text(f"类型: 网格")
    imgui.separator()

    # 标签页
    if imgui.begin_tab_bar("MeshTabs"):
        # 基本属性标签页
        if imgui.begin_tab_item("基本属性")[0]:
            show_basic_properties(props)
            imgui.end_tab_item()

        # 材质属性标签页
        if imgui.begin_tab_item("材质属性")[0]:
            show_material_tab_for_mesh(props)
            imgui.end_tab_item()

        # 物理属性标签页
        if imgui.begin_tab_item("物理属性")[0]:
            show_physics_properties(props)
            imgui.end_tab_item()

        imgui.end_tab_bar()


def show_basic_properties(props):
    """显示基本属性（位置、旋转、缩放）"""
    imgui.text("变换")
    imgui.separator()

    # 位置
    imgui.text("位置:")
    imgui.same_line()
    _, props["position"][0] = imgui.input_float("##pos_x", props["position"][0], format="%.3f")
    imgui.same_line()
    _, props["position"][1] = imgui.input_float("##pos_y", props["position"][1], format="%.3f")
    imgui.same_line()
    _, props["position"][2] = imgui.input_float("##pos_z", props["position"][2], format="%.3f")

    # 旋转
    imgui.text("旋转:")
    imgui.same_line()
    _, props["rotation"][0] = imgui.input_float("##rot_x", props["rotation"][0], format="%.1f")
    imgui.same_line()
    _, props["rotation"][1] = imgui.input_float("##rot_y", props["rotation"][1], format="%.1f")
    imgui.same_line()
    _, props["rotation"][2] = imgui.input_float("##rot_z", props["rotation"][2], format="%.1f")

    # 缩放
    imgui.text("缩放:")
    imgui.same_line()
    _, props["scale"][0] = imgui.input_float("##scale_x", props["scale"][0], format="%.3f")
    imgui.same_line()
    _, props["scale"][1] = imgui.input_float("##scale_y", props["scale"][1], format="%.3f")
    imgui.same_line()
    _, props["scale"][2] = imgui.input_float("##scale_z", props["scale"][2], format="%.3f")

    imgui.spacing()

    # 可见性
    imgui.text("可见性:")
    imgui.same_line()
    _, props["visible"] = imgui.checkbox("##visible", props["visible"])


def show_material_tab_for_mesh(props):
    """为网格显示材质属性标签页"""
    imgui.text("材质设置")
    imgui.separator()

    # 材质选择
    imgui.text("材质:")
    imgui.same_line()
    materials = ["default", "metal", "plastic", "glass", "custom"]
    current_mat = props.get("material", "default")

    if current_mat not in materials:
        materials.append(current_mat)

    current_index = materials.index(current_mat)
    clicked, new_index = imgui.combo("##material", current_index, materials)
    if clicked:
        props["material"] = materials[new_index]


def show_physics_properties(props):
    """显示物理属性"""
    imgui.text("物理属性")
    imgui.separator()
    imgui.text("物理属性功能待实现")


def show_material_properties():
    """显示材质对象属性"""
    props = selected_object["properties"]

    # 显示对象名称和类型
    imgui.text(f"对象: {selected_object['name']}")
    imgui.text(f"类型: 材质")
    imgui.separator()

    # 材质属性标签页
    if imgui.begin_tab_bar("MaterialTabs"):
        if imgui.begin_tab_item("材质属性")[0]:
            show_material_textures(props)
            imgui.end_tab_item()
        imgui.end_tab_bar()


def show_material_textures(props):
    """显示材质纹理设置"""
    imgui.text("纹理设置")
    imgui.separator()

    # 纹理图
    show_file_input("纹理图:", "albedo_texture", props)

    # 法线图
    show_file_input("法线图:", "normal_texture", props)

    # 金属度
    show_file_input("金属度:", "metallic_texture", props)

    # 粗糙度
    show_file_input("粗糙度:", "roughness_texture", props)

    imgui.spacing()
    imgui.separator()

    # 数值设置
    imgui.text("数值设置")
    imgui.separator()

    # 金属度数值
    imgui.text("金属度:")
    imgui.same_line()
    _, props["metallic_value"] = imgui.slider_float("##metallic_value", props["metallic_value"], 0.0, 1.0)

    # 粗糙度数值
    imgui.text("粗糙度:")
    imgui.same_line()
    _, props["roughness_value"] = imgui.slider_float("##roughness_value", props["roughness_value"], 0.0, 1.0)


def show_camera_properties():
    """显示摄像机对象属性"""
    props = selected_object["properties"]

    # 显示对象名称和类型
    imgui.text(f"对象: {selected_object['name']}")
    imgui.text(f"类型: 摄像机")
    imgui.separator()

    # 标签页
    if imgui.begin_tab_bar("CameraTabs"):
        # 基本属性标签页
        if imgui.begin_tab_item("基本属性")[0]:
            show_camera_basic_properties(props)
            imgui.end_tab_item()

        # 摄像机属性标签页
        if imgui.begin_tab_item("摄像机属性")[0]:
            show_camera_settings(props)
            imgui.end_tab_item()

        imgui.end_tab_bar()


def show_camera_basic_properties(props):
    """显示摄像机基本属性"""
    imgui.text("变换")
    imgui.separator()

    # 位置
    imgui.text("位置:")
    imgui.same_line()
    _, props["position"][0] = imgui.input_float("##cam_pos_x", props["position"][0], format="%.3f")
    imgui.same_line()
    _, props["position"][1] = imgui.input_float("##cam_pos_y", props["position"][1], format="%.3f")
    imgui.same_line()
    _, props["position"][2] = imgui.input_float("##cam_pos_z", props["position"][2], format="%.3f")

    # 旋转
    imgui.text("旋转:")
    imgui.same_line()
    _, props["rotation"][0] = imgui.input_float("##cam_rot_x", props["rotation"][0], format="%.1f")
    imgui.same_line()
    _, props["rotation"][1] = imgui.input_float("##cam_rot_y", props["rotation"][1], format="%.1f")
    imgui.same_line()
    _, props["rotation"][2] = imgui.input_float("##cam_rot_z", props["rotation"][2], format="%.1f")


def show_camera_settings(props):
    """显示摄像机设置"""
    imgui.text("摄像机参数")
    imgui.separator()

    # 视场角
    imgui.text("视场角 X:")
    imgui.same_line()
    _, props["fov_x"] = imgui.input_float("##fov_x", props["fov_x"], format="%.1f")

    imgui.text("视场角 Y:")
    imgui.same_line()
    _, props["fov_y"] = imgui.input_float("##fov_y", props["fov_y"], format="%.1f")

    # 裁剪距离
    imgui.text("近裁剪距离:")
    imgui.same_line()
    _, props["near_clip"] = imgui.input_float("##near_clip", props["near_clip"], format="%.3f")

    imgui.text("远裁剪距离:")
    imgui.same_line()
    _, props["far_clip"] = imgui.input_float("##far_clip", props["far_clip"], format="%.1f")


def show_light_properties():
    """显示HDRI光照对象属性"""
    props = selected_object["properties"]

    # 显示对象名称和类型
    imgui.text(f"对象: {selected_object['name']}")
    imgui.text(f"类型: HDRI光照")
    imgui.separator()

    # HDRI文件输入
    show_file_input("HDRI文件:", "hdri_file", props)

    imgui.spacing()

    # 强度设置
    imgui.text("强度:")
    imgui.same_line()
    _, props["intensity"] = imgui.slider_float("##intensity", props["intensity"], 0.0, 5.0)

    # 旋转设置
    imgui.text("旋转:")
    imgui.same_line()
    _, props["rotation"] = imgui.slider_float("##light_rotation", props["rotation"], 0.0, 360.0, format="%.1f°")


def show_file_input(label, prop_key, props):
    """显示文件输入控件"""
    imgui.text(f"{label}")
    imgui.same_line()

    # 文件路径显示
    file_path = props.get(prop_key, "")
    if file_path:
        # 只显示文件名
        file_name = os.path.basename(file_path)
        imgui.text(file_name)
    else:
        imgui.text("未选择文件")

    imgui.same_line()

    # 文件夹图标按钮
    if file_path:
        # 如果已选择文件，显示删除按钮
        if imgui.button(f"×##{prop_key}"):
            props[prop_key] = ""
    else:
        # 如果未选择文件，显示文件夹按钮
        if imgui.button(f"📁##{prop_key}"):
            # 这里应该打开文件选择对话框
            # 暂时模拟选择文件
            props[prop_key] = "/path/to/selected/file.png"


def get_selected_object():
    """获取当前选中的对象信息"""
    return selected_object


def set_selected_object(obj_type, obj_name, properties=None):
    """设置选中的对象"""
    select_object(obj_type, obj_name)
    if properties:
        selected_object["properties"].update(properties)