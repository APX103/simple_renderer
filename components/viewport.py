"""
Python Viewport implementation for USD scene visualization.
This is a Python rewrite of the C++ Viewport class for use in other projects.
"""

import numpy as np
from typing import Optional, List, Tuple
import math

# Mock classes to simulate USD/Hydra functionality
class SdfPath:
    """Mock SdfPath class"""
    def __init__(self, path: str = ""):
        self.path = path

    def IsEmpty(self) -> bool:
        return not self.path

    def GetName(self) -> str:
        return self.path.split("/")[-1] if "/" in self.path else self.path

    def GetAsString(self) -> str:
        return self.path

class GfVec3d:
    """3D vector class"""
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def YAxis():
        return GfVec3d(0, 1, 0)

    def __add__(self, other):
        return GfVec3d(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return GfVec3d(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return GfVec3d(self.x * scalar, self.y * scalar, self.z * scalar)

    def GetNormalized(self):
        length = self.GetLength()
        if length == 0:
            return GfVec3d(0, 0, 0)
        return GfVec3d(self.x/length, self.y/length, self.z/length)

    def GetLength(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

class GfMatrix4d:
    """4x4 matrix class"""
    def __init__(self, data: Optional[List[List[float]]] = None):
        if data is None:
            self.data = [[1, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1]]
        else:
            self.data = data

    def SetLookAt(self, eye: GfVec3d, at: GfVec3d, up: GfVec3d):
        """Create a look-at matrix"""
        forward = GfVec3d(at.x - eye.x, at.y - eye.y, at.z - eye.z)
        forward = forward.GetNormalized()

        right = cross(forward, up).GetNormalized()
        up = cross(right, forward).GetNormalized()

        self.data = [
            [right.x, right.y, right.z, -dot(right, eye)],
            [up.x, up.y, up.z, -dot(up, eye)],
            [-forward.x, -forward.y, -forward.z, dot(forward, eye)],
            [0, 0, 0, 1]
        ]
        return self

    def GetInverse(self):
        """Simple inverse for identity matrix - in practice use numpy"""
        # This is a simplified version - in real implementation use proper matrix inversion
        return GfMatrix4d()

class GfFrustum:
    """Camera frustum class"""
    def __init__(self):
        self.position = GfVec3d(0, 0, 0)
        self.rotation = [0, 0, 0, 1]  # quaternion

    def SetPerspective(self, fov: float, is_vertical: bool, aspect_ratio: float, near: float, far: float):
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far

    def SetPositionAndRotationFromMatrix(self, matrix: GfMatrix4d):
        """Extract position and rotation from view matrix"""
        # Simplified implementation
        pass

    def ComputeLookAtPoint(self) -> GfVec3d:
        """Compute look-at point from position and rotation"""
        return GfVec3d(0, 0, -1)  # Simplified

    def GetPosition(self) -> GfVec3d:
        return self.position

class GfCamera:
    """Camera class"""
    def __init__(self):
        self.frustum = GfFrustum()

    def GetFrustum(self) -> GfFrustum:
        return self.frustum

    def GetFieldOfView(self, direction) -> float:
        return 45.0  # Default FOV

    def GetClippingRange(self):
        return (0.1, 10000.0)  # Default clipping range

class TransformControl:
    """Transform control for manipulating objects"""
    def __init__(self):
        self.operation = "TRANSLATE"
        self.mode = "LOCAL"

    def SetOperation(self, operation: str):
        self.operation = operation

    def GetOperation(self) -> str:
        return self.operation

    def SetMode(self, mode: str):
        self.mode = mode

    def GetMode(self) -> str:
        return self.mode

    def Draw(self):
        """Draw transform control"""
        pass

class Engine:
    """Rendering engine mock"""
    def __init__(self, scene_index, plugin: str = ""):
        self.plugin = plugin
        self.render_size = (800, 600)

    def GetRendererPlugins(self):
        return ["GL", "Vulkan", "Metal"]

    def GetCurrentRendererPlugin(self) -> str:
        return self.plugin

    def GetRendererPluginName(self, plugin: str) -> str:
        return plugin

    def SetSelection(self, paths: List[SdfPath]):
        pass

    def SetRenderSize(self, width: float, height: float):
        self.render_size = (width, height)

    def SetCameraMatrices(self, view: GfMatrix4d, proj: GfMatrix4d):
        pass

    def Prepare(self):
        pass

    def Render(self):
        pass

    def GetRenderBufferData(self):
        """Return texture ID for ImGui"""
        return 0  # Mock texture ID

    def FindIntersection(self, mouse_pos) -> SdfPath:
        """Find prim under mouse cursor"""
        return SdfPath()

def cross(a: GfVec3d, b: GfVec3d) -> GfVec3d:
    """Cross product of two vectors"""
    return GfVec3d(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    )

def dot(a: GfVec3d, b: GfVec3d) -> float:
    """Dot product of two vectors"""
    return a.x * b.x + a.y * b.y + a.z * b.z

class Viewport:
    """
    Python Viewport implementation for USD scene visualization.
    This class provides viewport functionality similar to the C++ version.
    """

    VIEW_TYPE = "Viewport"

    def __init__(self, model, label: str = VIEW_TYPE):
        self.model = model
        self.label = label

        self._gizmo_window_flags = 0  # ImGuiWindowFlags_MenuBar
        self._is_ambient_light_enabled = True
        self._is_dome_light_enabled = False
        self._is_grid_enabled = True

        # Initialize transform control
        self._transform_control = TransformControl()
        self._transform_control.SetOperation("TRANSLATE")
        self._transform_control.SetMode("LOCAL")

        # Camera setup
        self._eye = GfVec3d(5, 5, 5)
        self._at = GfVec3d(0, 0, 0)
        self._up = GfVec3d.YAxis()

        self._active_cam = SdfPath()
        self._proj = GfMatrix4d()

        # Constants
        self._FREE_CAM_FOV = 45.0
        self._FREE_CAM_NEAR = 0.1
        self._FREE_CAM_FAR = 10000.0

        # Initialize engine
        plugin = "GL"  # Default renderer
        self._engine = Engine(model.get_final_scene_index() if hasattr(model, 'get_final_scene_index') else None, plugin)

        self._update_active_cam_from_viewport()

    def __del__(self):
        """Destructor"""
        pass

    def get_view_type(self) -> str:
        """Get the view type"""
        return self.VIEW_TYPE

    def _get_gizmo_window_flags(self):
        """Get gizmo window flags"""
        return self._gizmo_window_flags

    def _get_viewport_width(self) -> float:
        """Get viewport width"""
        # In practice, get from ImGui window
        return 800.0

    def _get_viewport_height(self) -> float:
        """Get viewport height"""
        # In practice, get from ImGui window
        return 600.0

    def draw(self):
        """Main draw function"""
        self._draw_menu_bar()

        if self._get_viewport_width() <= 0 or self._get_viewport_height() <= 0:
            return

        # Begin child window for rendering
        # ImGui.BeginChild("GameRender")

        self._configure_imguzmo()

        # Update from active camera if window not focused
        # if not ImGui.IsWindowFocused():
        #     self._update_viewport_from_active_cam()

        self._update_projection()
        self._update_grid()
        self._update_hydra_render()
        self._update_transform_guizmo()
        self._update_cube_guizmo()
        self._update_plugin_label()

        # Draw transform control
        self._transform_control.Draw()

        # ImGui.EndChild()

    def _draw_menu_bar(self):
        """Draw menu bar"""
        # if ImGui.BeginMenuBar():
        #     if ImGui.BeginMenu("renderer"):
        #         plugins = self._engine.GetRendererPlugins()
        #         cur_plugin = self._engine.GetCurrentRendererPlugin()
        #         for p in plugins:
        #             enabled = (p == cur_plugin)
        #             name = self._engine.GetRendererPluginName(p)
        #             if ImGui.MenuItem(name, None, enabled):
        #                 # Switch renderer
        #                 self._engine = Engine(self.model.get_final_scene_index(), p)
        #         ImGui.EndMenu()
        #
        #     if ImGui.BeginMenu("cameras"):
        #         enabled = self._active_cam.IsEmpty()
        #         if ImGui.MenuItem("free camera", None, enabled):
        #             self._set_free_cam_as_active()
        #         for path in self.model.get_cameras():
        #             enabled = (path == self._active_cam)
        #             if ImGui.MenuItem(path.GetName(), None, enabled):
        #                 self._set_active_cam(path)
        #         ImGui.EndMenu()
        #
        #     if ImGui.BeginMenu("lights"):
        #         ImGui.MenuItem("ambient light", None, self._is_ambient_light_enabled)
        #         ImGui.MenuItem("dome light", None, self._is_dome_light_enabled)
        #         ImGui.EndMenu()
        #
        #     if ImGui.BeginMenu("show"):
        #         ImGui.MenuItem("grid", None, self._is_grid_enabled)
        #         ImGui.EndMenu()
        #
        #     ImGui.EndMenuBar()
        pass

    def _configure_imguzmo(self):
        """Configure ImGuizmo"""
        # ImGuizmo.BeginFrame()
        #
        # # Convert last label char to ID
        # label = self.label
        # ImGuizmo.SetID(ord(label[-1]) if label else 0)
        #
        # ImGuizmo.SetDrawlist()
        # rect_min = (0, 0)  # Get from ImGui window
        # ImGuizmo.SetRect(rect_min[0], rect_min[1],
        #                  self._get_viewport_width(), self._get_viewport_height())
        pass

    def _update_grid(self):
        """Update grid display"""
        if not self._is_grid_enabled:
            return

        # Draw grid using ImGuizmo
        view_f = self._get_cur_view_matrix()
        proj_f = self._proj
        identity = GfMatrix4d()

        # ImGuizmo.DrawGrid(view_f.data, proj_f.data, identity.data, 10)
        pass

    def _update_hydra_render(self):
        """Update Hydra rendering"""
        view = self._get_cur_view_matrix()
        width = self._get_viewport_width()
        height = self._get_viewport_height()

        # Set selection
        paths = []
        for prim in self.model.get_selection():
            paths.append(prim.GetPrimPath() if hasattr(prim, 'GetPrimPath') else SdfPath())

        self._engine.SetSelection(paths)
        self._engine.SetRenderSize(width, height)
        self._engine.SetCameraMatrices(view, self._proj)
        self._engine.Prepare()

        # Do the render
        self._engine.Render()

        # Create ImGui image with render buffer
        texture_id = self._engine.GetRenderBufferData()
        # ImGui.Image(texture_id, (width, height), (0, 1), (1, 0))

    def _update_transform_guizmo(self):
        """Update transform gizmo"""
        prim_paths = self.model.get_selection()
        if not prim_paths or prim_paths[0].IsEmpty():
            return

        prim_path = prim_paths[0]

        # Get current transform
        transform = GfMatrix4d()  # In practice, get from scene index
        transform_f = transform

        view = self._get_cur_view_matrix()
        view_f = view
        proj_f = self._proj

        # Manipulate transform with ImGuizmo
        # ImGuizmo.Manipulate(view_f.data, proj_f.data,
        #                    self._transform_control.GetOperation(),
        #                    self._transform_control.GetMode(),
        #                    transform_f.data)

        # Update transform if changed
        # if transform_f != transform:
        #     # Update in scene index
        #     pass

    def _update_cube_guizmo(self):
        """Update cube gizmo for view manipulation"""
        view = self._get_cur_view_matrix()
        view_f = view

        # ImGuizmo.ViewManipulate(
        #     view_f.data, 8.0,
        #     (self._get_viewport_width() - 128, 18),  # Position
        #     (128, 128),  # Size
        #     0x00000020)  # Color (black transparent)

        # if view_f != view:
        #     view = GfMatrix4d(view_f)
        #     frustum = GfFrustum()
        #     frustum.SetPositionAndRotationFromMatrix(view.GetInverse())
        #     self._eye = frustum.GetPosition()
        #     self._at = frustum.ComputeLookAtPoint()
        #
        #     self._update_active_cam_from_viewport()

    def _update_plugin_label(self):
        """Update renderer plugin label"""
        cur_plugin = self._engine.GetCurrentRendererPlugin()
        plugin_text = self._engine.GetRendererPluginName(cur_plugin)
        text = plugin_text

        # Draw text in viewport
        # draw_list = ImGui.GetWindowDrawList()
        # text_size = ImGui.CalcTextSize(text)
        # margin = 6
        # x_pos = (self._get_viewport_width() - 64 - text_size[0] / 2)
        # y_pos = margin * 2
        #
        # # Draw background
        # draw_list.AddRectFilled(
        #     (x_pos - margin, y_pos - margin),
        #     (x_pos + text_size[0] + margin, y_pos + text_size[1] + margin),
        #     0x33000000, margin)  # Black transparent
        #
        # # Draw text
        # draw_list.AddText((x_pos, y_pos), 0xFFFFFFFF, text)
        pass

    def _pan_active_cam(self, mouse_delta_pos):
        """Pan active camera"""
        cam_front = self._at - self._eye
        cam_right = cross(cam_front, self._up).GetNormalized()
        cam_up = cross(cam_right, cam_front).GetNormalized()

        delta = cam_right * (-mouse_delta_pos[0] / 100.0) + cam_up * (mouse_delta_pos[1] / 100.0)

        self._eye += delta
        self._at += delta

        self._update_active_cam_from_viewport()

    def _orbit_active_cam(self, mouse_delta_pos):
        """Orbit active camera"""
        # Simplified orbit implementation
        # In practice, use proper rotation matrices

        # Horizontal rotation around up axis
        angle_x = mouse_delta_pos[0] / 2.0

        # Vertical rotation around right axis
        angle_y = mouse_delta_pos[1] / 2.0

        # Update eye position based on rotation
        # This is a simplified version - in practice use proper rotation math

        self._update_active_cam_from_viewport()

    def _zoom_active_cam(self, mouse_delta_pos):
        """Zoom active camera"""
        cam_front = (self._at - self._eye).GetNormalized()
        self._eye += cam_front * (mouse_delta_pos[0] / 100.0)
        self._update_active_cam_from_viewport()

    def _zoom_active_cam_scroll(self, scroll_wheel):
        """Zoom active camera with scroll wheel"""
        cam_front = (self._at - self._eye).GetNormalized()
        self._eye += cam_front * (scroll_wheel / 10.0)
        self._update_active_cam_from_viewport()

    def _set_free_cam_as_active(self):
        """Set free camera as active"""
        self._active_cam = SdfPath()

    def _set_active_cam(self, prim_path: SdfPath):
        """Set given camera as active"""
        self._active_cam = prim_path
        self._update_viewport_from_active_cam()

    def _update_viewport_from_active_cam(self):
        """Update viewport from active camera"""
        if self._active_cam.IsEmpty():
            return

        # In practice, get camera data from scene index
        # prim = self._scene_index.GetPrim(self._active_cam)
        # gf_cam = self._to_gf_camera(prim)
        # frustum = gf_cam.GetFrustum()
        # self._eye = frustum.GetPosition()
        # self._at = frustum.ComputeLookAtPoint()
        pass

    def _get_cur_view_matrix(self) -> GfMatrix4d:
        """Get current view matrix"""
        view_matrix = GfMatrix4d()
        view_matrix.SetLookAt(self._eye, self._at, self._up)
        return view_matrix

    def _update_active_cam_from_viewport(self):
        """Update active camera from viewport"""
        if self._active_cam.IsEmpty():
            return

        # In practice, update camera transform in scene index
        pass

    def _update_projection(self):
        """Update projection matrix"""
        fov = self._FREE_CAM_FOV
        near_plane = self._FREE_CAM_NEAR
        far_plane = self._FREE_CAM_FAR

        if not self._active_cam.IsEmpty():
            # Get camera parameters from active camera
            # prim = self._scene_index.GetPrim(self._active_cam)
            # gf_cam = self._to_gf_camera(prim)
            # fov = gf_cam.GetFieldOfView("vertical")
            # near_plane, far_plane = gf_cam.GetClippingRange()
            pass

        # Create projection matrix
        aspect_ratio = self._get_viewport_width() / self._get_viewport_height()
        frustum = GfFrustum()
        frustum.SetPerspective(fov, True, aspect_ratio, near_plane, far_plane)

        # In practice, compute projection matrix from frustum
        # self._proj = frustum.ComputeProjectionMatrix()

    def _to_gf_camera(self, prim):
        """Convert Hydra prim to GfCamera"""
        camera = GfCamera()
        # Implementation would extract camera parameters from prim
        return camera

    def _focus_on_prim(self, prim_path: SdfPath):
        """Focus camera on prim"""
        if prim_path.IsEmpty():
            return

        # In practice, get prim extent and adjust camera
        # prim = self._scene_index.GetPrim(prim_path)
        # extent_schema = HdExtentSchema.GetFromParent(prim.dataSource)
        # if not extent_schema.IsDefined():
        #     print(f"Prim at {prim_path.GetAsString()} has no extent; skipping focus.")
        #     return
        #
        # extent_min = extent_schema.GetMin().GetValue(0).Get()
        # extent_max = extent_schema.GetMax().GetValue(0).Get()
        # extent_range = (extent_min, extent_max)
        #
        # midpoint = GfVec3d((extent_min.x + extent_max.x) / 2,
        #                    (extent_min.y + extent_max.y) / 2,
        #                    (extent_min.z + extent_max.z) / 2)
        #
        # self._at = midpoint
        # self._eye = self._at + (self._eye - self._at).GetNormalized() * extent_range.GetSize().GetLength() * 2
        #
        # self._update_active_cam_from_viewport()
        pass

    def key_press_event(self, key: str):
        """Handle key press events"""
        if key == "F":
            prim_paths = self.model.get_selection()
            if prim_paths:
                self._focus_on_prim(prim_paths[0])
        elif key == "W":
            self._transform_control.SetOperation("TRANSLATE")
        elif key == "E":
            self._transform_control.SetOperation("ROTATE")
        elif key == "R":
            self._transform_control.SetOperation("SCALE")

    def mouse_move_event(self, prev_pos, cur_pos):
        """Handle mouse move events"""
        delta_mouse_pos = (cur_pos[0] - prev_pos[0], cur_pos[1] - prev_pos[1])

        # Handle scroll wheel
        # if io.MouseWheel:
        #     self._zoom_active_cam_scroll(io.MouseWheel)

        # Handle camera controls
        # if ImGui.IsMouseDown(ImGuiMouseButton_Left) and (ImGui.IsKeyDown(ImGuiKey_LeftAlt) or ImGui.IsKeyDown(ImGuiKey_RightAlt)):
        #     self._orbit_active_cam(delta_mouse_pos)
        # if ImGui.IsMouseDown(ImGuiMouseButton_Left) and (ImGui.IsKeyDown(ImGuiKey_LeftShift) or ImGui.IsKeyDown(ImGuiKey_RightShift)):
        #     self._pan_active_cam(delta_mouse_pos)
        # if ImGui.IsMouseDown(ImGuiMouseButton_Right) and (ImGui.IsKeyDown(ImGuiKey_LeftAlt) or ImGui.IsKeyDown(ImGuiKey_RightAlt)):
        #     self._zoom_active_cam(delta_mouse_pos)
        # # Direct right-click rotation
        # if ImGui.IsMouseDown(ImGuiMouseButton_Right) and not ImGui.IsKeyDown(ImGuiKey_LeftAlt) and not ImGui.IsKeyDown(ImGuiKey_RightAlt):
        #     self._orbit_active_cam(delta_mouse_pos)

    def mouse_release_event(self, button: str, mouse_pos):
        """Handle mouse release events"""
        if button == "left":
            # Handle selection
            # delta = ImGui.GetMouseDragDelta(ImGuiMouseButton_Left)
            # if abs(delta[0]) + abs(delta[1]) < 0.001:
            #     prim_path = self._engine.FindIntersection(mouse_pos)
            #     if prim_path.IsEmpty():
            #         self.model.set_selection([])
            #     else:
            #         self.model.set_selection([prim_path])
            pass

    def hover_in_event(self):
        """Handle hover in event"""
        self._gizmo_window_flags |= 0x00000002  # ImGuiWindowFlags_NoMove

    def hover_out_event(self):
        """Handle hover out event"""
        self._gizmo_window_flags &= ~0x00000002  # ImGuiWindowFlags_NoMove

    def handle_continuous_input(self):
        """Handle continuous input"""
        if self.is_hovered() and self.is_focused():
            self._handle_wsad_movement()

    def _handle_wsad_movement(self):
        """Handle WSAD camera movement"""
        # Only handle when right mouse button is held
        # if not ImGui.IsMouseDown(ImGuiMouseButton_Right):
        #     return

        move_speed = 0.1
        move_delta = GfVec3d(0, 0, 0)

        # Get camera vectors
        forward = (self._at - self._eye).GetNormalized()
        right = cross(forward, self._up).GetNormalized()

        # Handle WSAD keys
        # if ImGui.IsKeyDown(ImGuiKey_W):
        #     move_delta += forward * move_speed
        # if ImGui.IsKeyDown(ImGuiKey_S):
        #     move_delta -= forward * move_speed
        # if ImGui.IsKeyDown(ImGuiKey_A):
        #     move_delta -= right * move_speed
        # if ImGui.IsKeyDown(ImGuiKey_D):
        #     move_delta += right * move_speed

        # Apply movement
        if move_delta.GetLength() > 0:
            self._eye += move_delta
            self._at += move_delta
            self._update_active_cam_from_viewport()

    def is_hovered(self) -> bool:
        """Check if viewport is hovered"""
        # In practice, check ImGui window hover state
        return False

    def is_focused(self) -> bool:
        """Check if viewport is focused"""
        # In practice, check ImGui window focus state
        return False

# Example usage
if __name__ == "__main__":
    # Mock model class
    class MockModel:
        def get_selection(self):
            return []
        def get_cameras(self):
            return []
        def get_final_scene_index(self):
            return None

    model = MockModel()
    viewport = Viewport(model)

    print("Viewport created successfully")
    print(f"View type: {viewport.get_view_type()}")
    print(f"Camera position: ({viewport._eye.x}, {viewport._eye.y}, {viewport._eye.z})")
