#!/usr/bin/env python3
"""
Viewport component with OpenGL API - Display rotating square using OpenGL
"""

from imgui_bundle import imgui
import time
import numpy as np
import OpenGL.GL as gl
import OpenGL.GL.shaders as shaders
import ctypes


class ViewportManager:
    """Viewport manager with OpenGL rendering"""

    def __init__(self):
        self.rotation_angle = 0.0
        self.rotation_speed = 1.0  # Rotation speed in degrees per second
        self.square_color = [1.0, 0.5, 0.0, 1.0]  # Orange color
        self.background_color = [0.1, 0.1, 0.1, 1.0]  # Dark gray background
        self.texture_id = None
        self.framebuffer_id = None
        self.renderbuffer_id = None
        self.width = 800
        self.height = 600

        # Modern OpenGL resources
        self.vao = None
        self.vbo = None
        self.shader_program = None
        self.fallback_mode = False
        self.vertex_shader_source = """
        #version 330 core
        layout (location = 0) in vec2 aPos;
        uniform mat4 model;
        uniform mat4 projection;
        void main()
        {
            gl_Position = projection * model * vec4(aPos, 0.0, 1.0);
        }
        """

        self.fragment_shader_source = """
        #version 330 core
        out vec4 FragColor;
        uniform vec4 color;
        void main()
        {
            FragColor = color;
        }
        """

    def init_opengl_context(self):
        """Initialize OpenGL context and resources"""
        try:
            # Generate framebuffer
            self.framebuffer_id = gl.glGenFramebuffers(1)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.framebuffer_id)

            # Generate texture
            self.texture_id = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, self.width, self.height, 0,
                            gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

            # Generate renderbuffer for depth and stencil
            self.renderbuffer_id = gl.glGenRenderbuffers(1)
            gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.renderbuffer_id)
            gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH24_STENCIL8, self.width, self.height)

            # Attach texture and renderbuffer to framebuffer
            gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, self.texture_id, 0)
            gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_STENCIL_ATTACHMENT, gl.GL_RENDERBUFFER, self.renderbuffer_id)

            # Check framebuffer completeness
            if gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER) != gl.GL_FRAMEBUFFER_COMPLETE:
                print("ERROR: Framebuffer is not complete!")

            # Unbind framebuffer
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

            # Create shader program
            self._create_shader_program()

            # Create vertex data
            self._create_vertex_data()

            print("OpenGL context initialized successfully")
        except Exception as e:
            print(f"Error initializing OpenGL context: {e}")
            # Fallback to ImGui rendering if OpenGL fails
            self.fallback_mode = True

    def _create_shader_program(self):
        """Create shader program"""
        try:
            # Compile vertex shader
            vertex_shader = shaders.compileShader(self.vertex_shader_source, gl.GL_VERTEX_SHADER)
            # Compile fragment shader
            fragment_shader = shaders.compileShader(self.fragment_shader_source, gl.GL_FRAGMENT_SHADER)
            # Link shader program
            self.shader_program = shaders.compileProgram(vertex_shader, fragment_shader)
        except Exception as e:
            print(f"Shader compilation error: {e}")

    def _create_vertex_data(self):
        """Create vertex data for square"""
        # Square vertices
        vertices = np.array([
            -0.5, -0.5,  # Bottom-left
             0.5, -0.5,  # Bottom-right
             0.5,  0.5,  # Top-right
            -0.5,  0.5,  # Top-left
        ], dtype=np.float32)

        # Create VAO and VBO
        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        # Set vertex attributes
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 2 * np.dtype(np.float32).itemsize, None)
        gl.glEnableVertexAttribArray(0)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

    def update_rotation(self):
        """Update rotation angle based on time"""
        current_time = time.time()
        self.rotation_angle = (current_time * self.rotation_speed) % 360.0

    def render_to_texture(self, width: int, height: int):
        """Render OpenGL scene to texture using modern OpenGL"""
        if width != self.width or height != self.height:
            self.width = width
            self.height = height
            self.resize_texture(width, height)

        # Bind framebuffer
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.framebuffer_id)

        # Set viewport
        gl.glViewport(0, 0, width, height)

        # Clear with background color
        r, g, b, a = self.background_color
        gl.glClearColor(r, g, b, a)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Enable depth testing
        gl.glEnable(gl.GL_DEPTH_TEST)

        if self.shader_program and self.vao:
            # Use shader program
            gl.glUseProgram(self.shader_program)

            # Create projection matrix (orthographic)
            projection = np.array([
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0]
            ], dtype=np.float32)

            # Create model matrix with rotation
            angle_rad = np.radians(self.rotation_angle)
            cos_a = np.cos(angle_rad)
            sin_a = np.sin(angle_rad)
            model = np.array([
                [cos_a, -sin_a, 0.0, 0.0],
                [sin_a,  cos_a, 0.0, 0.0],
                [0.0,    0.0,   1.0, 0.0],
                [0.0,    0.0,   0.0, 1.0]
            ], dtype=np.float32)

            # Set uniforms
            projection_loc = gl.glGetUniformLocation(self.shader_program, "projection")
            model_loc = gl.glGetUniformLocation(self.shader_program, "model")
            color_loc = gl.glGetUniformLocation(self.shader_program, "color")

            gl.glUniformMatrix4fv(projection_loc, 1, gl.GL_FALSE, projection)
            gl.glUniformMatrix4fv(model_loc, 1, gl.GL_FALSE, model)

            # Draw filled square
            r, g, b, a = self.square_color
            gl.glUniform4f(color_loc, r, g, b, a)

            gl.glBindVertexArray(self.vao)
            gl.glDrawArrays(gl.GL_TRIANGLE_FAN, 0, 4)

            # Draw square outline in white
            gl.glUniform4f(color_loc, 1.0, 1.0, 1.0, 1.0)
            gl.glLineWidth(2.0)
            gl.glDrawArrays(gl.GL_LINE_LOOP, 0, 4)

            gl.glBindVertexArray(0)
            gl.glUseProgram(0)

        # Unbind framebuffer
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def resize_texture(self, width: int, height: int):
        """Resize texture and renderbuffer"""
        if self.texture_id:
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0,
                           gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)

        if self.renderbuffer_id:
            gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.renderbuffer_id)
            gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH24_STENCIL8, width, height)

    def cleanup(self):
        """Clean up OpenGL resources"""
        if self.texture_id:
            gl.glDeleteTextures([self.texture_id])
        if self.framebuffer_id:
            gl.glDeleteFramebuffers(1, [self.framebuffer_id])
        if self.renderbuffer_id:
            gl.glDeleteRenderbuffers(1, [self.renderbuffer_id])
        if self.vao:
            gl.glDeleteVertexArrays(1, [self.vao])
        if self.vbo:
            gl.glDeleteBuffers(1, [self.vbo])
        if self.shader_program:
            gl.glDeleteProgram(self.shader_program)


def show_viewport_panel(viewport_manager: ViewportManager, window_open: bool = True) -> bool:
    """Display viewport panel with OpenGL rendering"""
    # Set dockable
    imgui.set_next_window_dock_id(imgui.get_id("DockSpace"), imgui.Cond_.first_use_ever)

    # Set default window size
    imgui.set_next_window_size(imgui.ImVec2(800, 600), imgui.Cond_.first_use_ever)

    # Start viewport window
    window_open = imgui.begin("OpenGL 视口", True)

    if window_open:
        # # Control panel
        # imgui.text("控制设置:")

        # # Rotation speed control
        # imgui.text("旋转速度:")
        # _, viewport_manager.rotation_speed = imgui.slider_float("##speed",
        #                                                       viewport_manager.rotation_speed,
        #                                                       0.1, 5.0)

        # # Square color control
        # imgui.text("正方形颜色:")
        # _, viewport_manager.square_color = imgui.color_edit4("##square_color",
        #                                                    viewport_manager.square_color)

        # # Background color control
        # imgui.text("背景颜色:")
        # _, viewport_manager.background_color = imgui.color_edit4("##bg_color",
        #                                                         viewport_manager.background_color)

        # imgui.separator()

        # Get window content region size for drawing
        content_region = imgui.get_content_region_avail()
        window_width = int(content_region.x)
        window_height = int(content_region.y)

        # Ensure minimum size
        if window_width < 100:
            window_width = 100
        if window_height < 100:
            window_height = 100

        # Create child window for drawing
        imgui.begin_child("OpenGL Drawing Area", imgui.ImVec2(window_width, window_height), True)

        # Get drawing area size
        draw_size = imgui.get_content_region_avail()

        # Update rotation
        viewport_manager.update_rotation()

        # Render OpenGL scene to texture
        viewport_manager.render_to_texture(int(draw_size.x), int(draw_size.y))

        # Display OpenGL texture in ImGui
        if viewport_manager.texture_id:
            # Convert OpenGL texture ID to ImGui texture reference
            texture_ref = imgui.ImTextureRef(viewport_manager.texture_id)
            imgui.image(texture_ref, draw_size)

        # # Display information
        # imgui.text(f"旋转角度: {viewport_manager.rotation_angle:.1f}°")
        # imgui.text(f"绘制区域: {int(draw_size.x)} x {int(draw_size.y)}")
        # imgui.text(f"使用 OpenGL API 渲染")

        imgui.end_child()

    imgui.end()

    return window_open