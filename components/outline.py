#!/usr/bin/env python3
"""
大纲面板组件 - 对象列表与操作界面
支持树状结构展示、搜索、重命名、删除等操作
"""

from imgui_bundle import imgui
import re
import json
from typing import List, Dict, Set, Optional, Any

# 对象类型枚举
OBJECT_TYPE_MESH = "mesh"
OBJECT_TYPE_CAMERA = "camera"
OBJECT_TYPE_LIGHT = "light"
OBJECT_TYPE_GROUP = "group"

# 对象图标映射
OBJECT_ICONS = {
    OBJECT_TYPE_MESH: "📦",
    OBJECT_TYPE_CAMERA: "📷",
    OBJECT_TYPE_LIGHT: "💡",
    OBJECT_TYPE_GROUP: "📁"
}

# 示例JSON数据结构（嵌套结构）
SAMPLE_OUTLINE_JSON = '''
{
    "objects": [
        {
            "name": "House_01_Structure",
            "type": "group",
            "children": [
                {
                    "name": "Foundation_01",
                    "type": "mesh"
                },
                {
                    "name": "Walls_01",
                    "type": "mesh"
                },
                {
                    "name": "Roof_01",
                    "type": "mesh"
                }
            ]
        },
        {
            "name": "LivingRoom_Furniture_00000",
            "type": "group",
            "children": [
                {
                    "name": "Sofa_01",
                    "type": "mesh"
                },
                {
                    "name": "CoffeeTable_01",
                    "type": "mesh"
                }
            ]
        },
        {
            "name": "House_01_Landscape",
            "type": "mesh"
        },
        {
            "name": "Main Camera",
            "type": "camera"
        },
        {
            "name": "Sun Light",
            "type": "light"
        }
    ]
}
'''

# 对象数据结构
class OutlineObject:
    def __init__(self, id: str, name: str, obj_type: str, parent_id: str = None, children: List[str] = None):
        self.id = id
        self.name = name
        self.type = obj_type
        self.parent_id = parent_id
        self.children = children or []
        self.visible = True
        self.selected = False
        self.renaming = False
        self.temp_name = ""
        self.expanded = True  # 树节点是否展开

# 大纲面板状态
class OutlineState:
    def __init__(self):
        self.objects: Dict[str, OutlineObject] = {}
        self.selected_ids: Set[str] = set()
        self.search_text = ""
        self.show_delete_confirm = False
        self.delete_target_ids: Set[str] = set()
        self.delete_target_name = ""
        self.hovered_id = ""
        self.dragging_id = ""

        # 初始化示例数据
        self._init_sample_data()

    def _init_sample_data(self):
        """初始化示例对象数据"""
        # 从JSON加载示例数据
        self.objects = load_outline_from_json(SAMPLE_OUTLINE_JSON)

        # 确保没有任何对象在初始化时被选中
        self.selected_ids.clear()
        for obj in self.objects.values():
            obj.selected = False


def load_outline_from_json(json_data: str) -> Dict[str, OutlineObject]:
    """从JSON字符串加载大纲数据结构"""
    try:
        data = json.loads(json_data)
        return create_outline_from_dict(data)
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return {}


def create_outline_from_dict(data: Dict[str, Any]) -> Dict[str, OutlineObject]:
    """从字典数据创建大纲数据结构"""
    objects = {}

    def process_object(obj_data: Dict[str, Any], parent_name: str = None) -> str:
        """递归处理对象数据"""
        obj_name = obj_data["name"]
        obj_type = obj_data["type"]

        # 生成唯一标识符（使用名称作为基础）
        obj_id = f"{obj_type}_{obj_name}"

        # 获取子对象ID列表
        children_ids = []
        for child_data in obj_data.get("children", []):
            child_id = process_object(child_data, obj_name)
            children_ids.append(child_id)

        # 创建OutlineObject
        obj = OutlineObject(obj_id, obj_name, obj_type, parent_name, children_ids)
        objects[obj_id] = obj

        return obj_id

    # 处理所有根对象
    for obj_data in data.get("objects", []):
        process_object(obj_data)

    return objects


# 全局状态
outline_state = OutlineState()


def show_outline_panel(open: bool) -> bool:
    """显示大纲面板"""
    # 设置可停靠
    imgui.set_next_window_dock_id(imgui.get_id("DockSpace"), imgui.Cond_.first_use_ever)

    # 设置窗口默认大小
    imgui.set_next_window_size(imgui.ImVec2(350, 600), imgui.Cond_.first_use_ever)

    keep_open = True
    window_open = imgui.begin("大纲", open)[1]

    if window_open:
        # 顶部搜索栏
        _show_search_bar()

        imgui.separator()

        # 对象列表区域
        if imgui.begin_child("ObjectList", imgui.ImVec2(0, -imgui.get_frame_height_with_spacing() * 2)):
            _show_object_tree()
        imgui.end_child()

        imgui.separator()

        # 底部操作区域
        _show_bottom_actions()

        # 显示删除确认对话框
        if outline_state.show_delete_confirm:
            _show_delete_confirmation()

    imgui.end()
    return window_open and keep_open


def _show_search_bar():
    """显示搜索栏"""
    imgui.text("搜索:")
    imgui.same_line()

    # 搜索输入框
    search_changed, outline_state.search_text = imgui.input_text(
        "##search",
        outline_state.search_text,
        256
    )

    # 清空搜索按钮
    if outline_state.search_text:
        imgui.same_line()
        if imgui.button("×##clear_search"):
            outline_state.search_text = ""


def _show_object_tree():
    """显示对象树"""
    # 如果有搜索文本，过滤对象
    if outline_state.search_text:
        filtered_objects = _get_filtered_objects()
        if not filtered_objects:
            # 没有匹配结果
            imgui.text_colored(imgui.ImVec4(0.7, 0.7, 0.7, 1.0), "没有相关结果")
            return

        # 显示过滤后的对象（平铺显示）
        for obj_id in filtered_objects:
            obj = outline_state.objects[obj_id]
            _show_object_item(obj, is_filtered=True)
    else:
        # 正常显示树状结构
        root_objects = [obj for obj in outline_state.objects.values() if not obj.parent_id]
        for obj in root_objects:
            _show_tree_node_recursive(obj)


def _show_tree_node_recursive(obj: OutlineObject):
    """递归显示树节点"""
    # 检查是否有子对象
    has_children = bool(obj.children)

    # 树节点标志 - 移除 no_tree_push_on_open 标志，使用标准树节点
    flags = imgui.TreeNodeFlags_.open_on_arrow | imgui.TreeNodeFlags_.open_on_double_click
    # 注意：我们不使用 TreeNodeFlags_.selected 标志，因为它可能导致ImGui的默认选择行为
    if not has_children:
        flags |= imgui.TreeNodeFlags_.leaf
    if obj.expanded:
        flags |= imgui.TreeNodeFlags_.default_open

    # 开始树节点 - 使用空标签，实际内容在同一行显示
    node_open = imgui.tree_node_ex("##" + obj.id, flags)

    # 处理节点点击
    if imgui.is_item_clicked() and not imgui.is_item_toggled_open():
        _handle_object_selection(obj)

    # 在同一行显示对象内容
    imgui.same_line()

    # 显示对象图标
    icon = OBJECT_ICONS.get(obj.type, "❓")
    imgui.text(icon)
    imgui.same_line()

    # 显示对象名称（可选择且检测hover）
    _show_selectable_object_name(obj)

    # 显示操作按钮（仅在悬停时）
    if imgui.is_item_hovered():
        outline_state.hovered_id = obj.id
        _show_object_buttons_in_tree(obj)
        _show_hover_tooltip(obj)
    elif outline_state.hovered_id == obj.id:
        # 如果当前对象不再是悬停状态，清除悬停ID
        outline_state.hovered_id = ""

    if node_open:
        # 如果节点展开且有子对象，递归显示子对象
        if has_children:
            obj.expanded = True
            for child_id in obj.children:
                if child_id in outline_state.objects:
                    child_obj = outline_state.objects[child_id]
                    _show_tree_node_recursive(child_obj)
        else:
            obj.expanded = False

        imgui.tree_pop()
    else:
        obj.expanded = False


def _show_selectable_object_name(obj: OutlineObject):
    """显示可选择的对象名称（支持重命名和hover检测）"""
    if obj.renaming:
        # 重命名模式
        imgui.set_next_item_width(imgui.get_content_region_avail().x - 60)
        enter_pressed, obj.temp_name = imgui.input_text("##rename", obj.temp_name, 256)

        imgui.same_line()

        # 确认按钮
        if _can_rename_to(obj, obj.temp_name):
            if imgui.button("✓##confirm_rename"):
                obj.name = obj.temp_name
                obj.renaming = False
        else:
            imgui.text_colored(imgui.ImVec4(1, 0, 0, 1), "已存在重复命名")

        # 按回车确认或ESC取消
        if enter_pressed:
            if _can_rename_to(obj, obj.temp_name):
                obj.name = obj.temp_name
                obj.renaming = False
        elif imgui.is_key_pressed(imgui.Key.escape):
            obj.renaming = False
    else:
        # 正常显示模式 - 使用自定义选择状态显示
        is_selected = obj.id in outline_state.selected_ids

        # 构建显示名称（支持搜索高亮）
        display_name = obj.name

        # 高亮搜索匹配
        if outline_state.search_text and outline_state.search_text.lower() in obj.name.lower():
            # 找到匹配位置
            pattern = re.compile(re.escape(outline_state.search_text), re.IGNORECASE)
            match = pattern.search(obj.name)
            if match:
                start, end = match.span()
                # # 使用自定义选择状态显示
                # if is_selected:
                #     imgui.text_colored(imgui.ImVec4(0.26, 0.59, 0.98, 1.0), "● ")
                #     imgui.same_line()

                # 显示高亮文本
                if start > 0:
                    imgui.text(obj.name[:start])
                    imgui.same_line()

                imgui.text_colored(imgui.ImVec4(1, 0.8, 0, 1), obj.name[start:end])
                imgui.same_line()

                if end < len(obj.name):
                    imgui.text(obj.name[end:])

                # 添加可点击区域
                if imgui.is_item_clicked():
                    _handle_object_selection(obj)
            else:
                # 使用自定义选择状态显示
                if is_selected:
                    # imgui.text_colored(imgui.ImVec4(0.26, 0.59, 0.98, 1.0), "● ")
                    imgui.same_line()
                imgui.text(display_name)
                if imgui.is_item_clicked():
                    _handle_object_selection(obj)
        else:
            # 使用自定义选择状态显示
            if is_selected:
                # imgui.text_colored(imgui.ImVec4(0.26, 0.59, 0.98, 1.0), "● ")
                imgui.same_line()
            imgui.text(display_name)
            if imgui.is_item_clicked():
                _handle_object_selection(obj)


def _show_object_buttons_in_tree(obj: OutlineObject):
    """在树节点中显示操作按钮"""
    imgui.same_line()
    
    # 重命名按钮
    if imgui.button("✏️##rename"):
        obj.renaming = True
        obj.temp_name = obj.name

    imgui.same_line()

    # 删除按钮
    if imgui.button("🗑️##delete"):
        _prepare_delete_confirmation([obj.id])


def _show_object_item(obj: OutlineObject, depth: int = 0, is_filtered: bool = False):
    """显示单个对象项"""
    # 缩进
    imgui.indent(depth * 20)

    # 对象选择状态
    is_selected = obj.id in outline_state.selected_ids

    # 开始对象行
    imgui.push_id(obj.id)

    # 选择框
    if imgui.selectable("##selectable", is_selected, imgui.SelectableFlags_.span_all_columns):
        _handle_object_selection(obj)

    # 处理悬停
    if imgui.is_item_hovered():
        outline_state.hovered_id = obj.id
        _show_hover_tooltip(obj)
    elif outline_state.hovered_id == obj.id:
        # 如果当前对象不再是悬停状态，清除悬停ID
        outline_state.hovered_id = ""

    # 在同一行显示对象内容
    imgui.same_line()

    # 对象图标
    icon = OBJECT_ICONS.get(obj.type, "❓")
    imgui.text(icon)
    imgui.same_line()

    # 对象名称
    if obj.renaming:
        # 重命名模式
        imgui.set_next_item_width(imgui.get_content_region_avail().x - 60)
        enter_pressed, obj.temp_name = imgui.input_text("##rename", obj.temp_name, 256)

        imgui.same_line()

        # 确认按钮
        if _can_rename_to(obj, obj.temp_name):
            if imgui.button("✓##confirm_rename"):
                obj.name = obj.temp_name
                obj.renaming = False
        else:
            imgui.text_colored(imgui.ImVec4(1, 0, 0, 1), "已存在重复命名")

        # 按回车确认或ESC取消
        if enter_pressed:
            if _can_rename_to(obj, obj.temp_name):
                obj.name = obj.temp_name
                obj.renaming = False
        elif imgui.is_key_pressed(imgui.Key.escape):
            obj.renaming = False
    else:
        # 正常显示模式
        display_name = obj.name

        # 高亮搜索匹配
        if outline_state.search_text and outline_state.search_text.lower() in obj.name.lower():
            # 找到匹配位置
            pattern = re.compile(re.escape(outline_state.search_text), re.IGNORECASE)
            match = pattern.search(obj.name)
            if match:
                start, end = match.span()
                # 显示高亮文本
                if start > 0:
                    imgui.text(obj.name[:start])
                    imgui.same_line()

                imgui.text_colored(imgui.ImVec4(1, 0.8, 0, 1), obj.name[start:end])
                imgui.same_line()

                if end < len(obj.name):
                    imgui.text(obj.name[end:])
            else:
                imgui.text(display_name)
        else:
            imgui.text(display_name)

        # 操作按钮（仅在悬停或选中时显示）
        if obj.id == outline_state.hovered_id or is_selected:
            imgui.same_line()

            # 重命名按钮
            if imgui.button("✏️##rename"):
                obj.renaming = True
                obj.temp_name = obj.name

            imgui.same_line()

            # 删除按钮
            if imgui.button("🗑️##delete"):
                _prepare_delete_confirmation([obj.id])

    imgui.pop_id()

    # 取消缩进
    imgui.unindent(depth * 20)


def _show_hover_tooltip(obj: OutlineObject):
    """显示悬停提示"""
    if imgui.begin_tooltip():
        imgui.text(f"类型: {obj.type}")

        # 操作提示
        imgui.separator()
        imgui.text("操作:")
        imgui.text("- 点击: 选择对象")
        imgui.text("- 悬停按钮: 重命名/删除")
        imgui.text("- 拖拽: 重新排序")

        # 添加到场景按钮
        if imgui.button("添加到场景"):
            print(f"将对象 {obj.name} 添加到场景")

        imgui.end_tooltip()


def _handle_object_selection(obj: OutlineObject):
    """处理对象选择"""
    # 如果对象已经选中，则取消选择
    if obj.id in outline_state.selected_ids:
        # 获取所有需要取消选择的对象（包括子对象）
        all_deselected_ids = _get_all_children_ids(obj.id)
        all_deselected_ids.add(obj.id)

        # 更新全局选择状态
        outline_state.selected_ids.difference_update(all_deselected_ids)

        # 更新对象级别的选择状态
        for obj_id in all_deselected_ids:
            if obj_id in outline_state.objects:
                outline_state.objects[obj_id].selected = False

        # 清除属性面板选择
        _clear_properties_selection()
    else:
        # 清除当前选择，选择新对象（不自动选择子对象）
        # 先清除所有对象的选择状态
        for selected_id in outline_state.selected_ids:
            if selected_id in outline_state.objects:
                outline_state.objects[selected_id].selected = False

        # 更新全局选择状态
        outline_state.selected_ids.clear()
        outline_state.selected_ids.add(obj.id)

        # 更新对象级别的选择状态
        obj.selected = True

        # 更新属性面板选择
        _update_properties_selection(obj)


def _get_all_children_ids(obj_id: str) -> Set[str]:
    """获取对象的所有子对象ID（递归）"""
    children_ids = set()
    obj = outline_state.objects.get(obj_id)

    if obj and obj.children:
        for child_id in obj.children:
            children_ids.add(child_id)
            children_ids.update(_get_all_children_ids(child_id))

    return children_ids


def _get_filtered_objects() -> List[str]:
    """获取过滤后的对象ID列表"""
    filtered_ids = []
    search_lower = outline_state.search_text.lower()

    for obj_id, obj in outline_state.objects.items():
        if search_lower in obj.name.lower():
            filtered_ids.append(obj_id)

    return filtered_ids


def _can_rename_to(obj: OutlineObject, new_name: str) -> bool:
    """检查是否可以重命名到新名称"""
    if not new_name.strip():
        return False

    # 检查同级对象中是否有重名
    parent_id = obj.parent_id
    siblings = []

    if parent_id:
        parent_obj = outline_state.objects.get(parent_id)
        if parent_obj:
            siblings = [outline_state.objects[child_id] for child_id in parent_obj.children if child_id != obj.id]
    else:
        # 根对象
        siblings = [sibling for sibling in outline_state.objects.values() if not sibling.parent_id and sibling.id != obj.id]

    # 检查是否有重名
    for sibling in siblings:
        if sibling.name == new_name:
            return False

    return True


def _prepare_delete_confirmation(target_ids: List[str]):
    """准备删除确认"""
    outline_state.delete_target_ids = set(target_ids)

    # 获取所有要删除的对象名称
    target_names = []
    for obj_id in target_ids:
        if obj_id in outline_state.objects:
            target_names.append(outline_state.objects[obj_id].name)

    # 设置确认消息
    if len(target_ids) == 1:
        obj_name = target_names[0]
        if outline_state.objects[target_ids[0]].type == OBJECT_TYPE_GROUP:
            outline_state.delete_target_name = f"组合 {obj_name}"
        else:
            outline_state.delete_target_name = f"对象 {obj_name}"
    else:
        # 统计不同类型对象的数量
        group_count = sum(1 for obj_id in target_ids if outline_state.objects[obj_id].type == OBJECT_TYPE_GROUP)
        other_count = len(target_ids) - group_count

        if group_count > 0 and other_count > 0:
            outline_state.delete_target_name = f"所有选中项和 {group_count} 个组合"
        elif group_count > 0:
            outline_state.delete_target_name = f"{group_count} 个组合"
        else:
            outline_state.delete_target_name = f"{other_count} 个对象"

    outline_state.show_delete_confirm = True


def _show_delete_confirmation():
    """显示删除确认对话框"""
    imgui.open_popup("确认删除")

    if imgui.begin_popup_modal("确认删除", None, imgui.WindowFlags_.always_auto_resize)[0]:
        imgui.text(f"确认删除 {outline_state.delete_target_name}？")
        imgui.text("此操作不可撤销。")

        imgui.spacing()
        imgui.separator()
        imgui.spacing()

        # 删除和取消按钮
        button_width = 80

        if imgui.button("删除", imgui.ImVec2(button_width, 0)):
            _perform_delete()
            outline_state.show_delete_confirm = False
            imgui.close_current_popup()

        imgui.same_line()

        if imgui.button("取消", imgui.ImVec2(button_width, 0)):
            outline_state.show_delete_confirm = False
            imgui.close_current_popup()

        imgui.end_popup()


def _perform_delete():
    """执行删除操作"""
    # 获取所有要删除的对象ID（包括子对象）
    all_delete_ids = set()
    for obj_id in outline_state.delete_target_ids:
        all_delete_ids.add(obj_id)
        all_delete_ids.update(_get_all_children_ids(obj_id))

    # 从父对象的children列表中移除
    for obj_id in all_delete_ids:
        obj = outline_state.objects.get(obj_id)
        if obj and obj.parent_id:
            parent_obj = outline_state.objects.get(obj.parent_id)
            if parent_obj and obj_id in parent_obj.children:
                parent_obj.children.remove(obj_id)

    # 删除对象
    for obj_id in all_delete_ids:
        if obj_id in outline_state.objects:
            del outline_state.objects[obj_id]

    # 清除选择
    outline_state.selected_ids.difference_update(all_delete_ids)


def _show_bottom_actions():
    """显示底部操作区域"""
    # 添加对象按钮
    if imgui.button("添加对象"):
        _show_add_object_menu()

    imgui.same_line()

    # 删除选中按钮
    if outline_state.selected_ids:
        if imgui.button("删除选中"):
            _prepare_delete_confirmation(list(outline_state.selected_ids))
    else:
        imgui.begin_disabled()
        imgui.button("删除选中")
        imgui.end_disabled()


def _show_add_object_menu():
    """显示添加对象菜单"""
    if imgui.begin_popup_context_item("AddObjectMenu"):
        if imgui.menu_item("添加网格")[0]:
            _add_new_object("新网格", OBJECT_TYPE_MESH)
        if imgui.menu_item("添加摄像机")[0]:
            _add_new_object("新摄像机", OBJECT_TYPE_CAMERA)
        if imgui.menu_item("添加光源")[0]:
            _add_new_object("新光源", OBJECT_TYPE_LIGHT)
        if imgui.menu_item("添加组合")[0]:
            _add_new_object("新组合", OBJECT_TYPE_GROUP)
        imgui.end_popup()
    else:
        # 如果没有打开弹出菜单，则打开它
        imgui.open_popup("AddObjectMenu")


def _add_new_object(name: str, obj_type: str):
    """添加新对象"""
    # 生成唯一ID
    obj_id = f"{obj_type}_{len(outline_state.objects)}"

    # 确保名称唯一
    base_name = name
    counter = 1
    while any(obj.name == name for obj in outline_state.objects.values()):
        name = f"{base_name}_{counter:02d}"
        counter += 1

    # 创建新对象
    new_obj = OutlineObject(obj_id, name, obj_type)
    outline_state.objects[obj_id] = new_obj

    # 选择新对象
    outline_state.selected_ids.clear()
    outline_state.selected_ids.add(obj_id)


def get_selected_object_ids() -> List[str]:
    """获取选中的对象ID列表"""
    return list(outline_state.selected_ids)


def get_object_name(obj_id: str) -> Optional[str]:
    """获取对象名称"""
    obj = outline_state.objects.get(obj_id)
    return obj.name if obj else None


def get_object_type(obj_id: str) -> Optional[str]:
    """获取对象类型"""
    obj = outline_state.objects.get(obj_id)
    return obj.type if obj else None


def _update_properties_selection(obj: OutlineObject):
    """更新属性面板选择"""
    try:
        # 导入properties模块
        from . import properties

        # 根据对象类型映射到properties中的类型
        type_mapping = {
            OBJECT_TYPE_MESH: "mesh",
            OBJECT_TYPE_CAMERA: "camera",
            OBJECT_TYPE_LIGHT: "light",
            OBJECT_TYPE_GROUP: "mesh"  # 组合对象也显示为网格属性
        }

        properties_type = type_mapping.get(obj.type, "mesh")

        # 更新属性面板选择
        properties.select_object(properties_type, obj.name)

    except ImportError:
        print("警告: 无法导入properties模块")


def _clear_properties_selection():
    """清除属性面板选择"""
    try:
        from . import properties
        properties.select_object("none", "")
    except ImportError:
        print("警告: 无法导入properties模块")