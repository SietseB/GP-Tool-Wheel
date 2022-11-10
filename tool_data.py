'''
GP Tool Wheel

---- Data ----
Specification of all the available Grease Pencil tools and modes
'''

from os import path

import bpy
import gpu
import numpy as np

from . import preferences


class ToolData():
    ICON_PATH = r'\icons\\'
    
    def __init__(self):
        self.keymappings = []
        self.key_button_text = ''
        self.key_button_depress = False
        self.mode_order_labels = []
        self.active_modes = []
        self.textures = {}
        self.modes = ['weight', 'draw', 'vertex', 'edit', 'sculpt', 'object']
        self.modes_in_prefs = ['draw', 'edit', 'sculpt', 'object', 'vertex', 'weight']
        self.box_by_angle = [2, 1, 1, 0, 5, 4, 4, 3]
        self.mode_order = [0, 1, 2, 3, 4, 5]
        # Which boxes are used for 1/2/3/4/5/6 active modes?
        self.box_layouts = [
            [1],
            [1],
            [1, 4],
            [0, 1, 2],
            [0, 1, 2, 4],
            [0, 1, 2, 3, 5],
            [0, 1, 2, 3, 4, 5],
        ]
        self.tools_per_mode = {}
        s = self.tools_per_mode
        s['weight'] = {
            'name': 'Weight Paint',
            'name_short': 'Weight',
            'mode': 'WEIGHT_GPENCIL',
            'active_tools': [],
            'tools': [
                {'name': 'Weight', 'tool': 'builtin_brush.Weight', 'icon': 'weight_paint_weight', 'default': True},
            ]
        }
        s['draw'] = {
            'name': 'Draw Mode',
            'name_short': 'Draw',
            'mode': 'PAINT_GPENCIL',
            'active_tools': [],
            'tools': [
                {'name': 'Draw', 'tool': 'builtin_brush.Draw', 'icon': 'draw_draw', 'default': True},
                {'name': 'Fill', 'tool': 'builtin_brush.Fill', 'icon': 'draw_fill', 'default': True},
                {'name': 'Erase', 'tool': 'builtin_brush.Erase', 'icon': 'draw_erase', 'default': True},
                {'name': 'Tint', 'tool': 'builtin_brush.Tint', 'icon': 'draw_tint', 'default': True},
                {'name': 'Cutter', 'tool': 'builtin.cutter', 'icon': 'draw_cutter', 'default': True},
                {'name': 'Eyedropper', 'tool': 'builtin.eyedropper', 'icon': 'draw_eyedropper', 'default': True},
                {'name': 'Line', 'tool': 'builtin.line', 'icon': 'draw_line', 'default': True},
                {'name': 'Polyline', 'tool': 'builtin.polyline', 'icon': 'draw_polyline', 'default': True},
                {'name': 'Arc', 'tool': 'builtin.arc', 'icon': 'draw_arc', 'default': True},
                {'name': 'Curve', 'tool': 'builtin.curve', 'icon': 'draw_curve', 'default': True},
                {'name': 'Box', 'tool': 'builtin.box', 'icon': 'draw_box', 'default': True},
                {'name': 'Circle', 'tool': 'builtin.circle', 'icon': 'draw_circle', 'default': True},
                {'name': 'Interpolate', 'tool': 'builtin.interpolate', 'icon': 'edit_interpolate', 'default': True},
            ]
        }
        s['vertex'] = {
            'name': 'Vertex Paint',
            'name_short': 'Vertex',
            'mode': 'VERTEX_GPENCIL',
            'active_tools': [],
            'tools': [
                {'name': 'Draw', 'tool': 'builtin_brush.Draw', 'icon': 'vertex_paint_draw', 'default': True},
                {'name': 'Blur', 'tool': 'builtin_brush.Blur', 'icon': 'vertex_paint_blur', 'default': True},
                {'name': 'Average', 'tool': 'builtin_brush.Average', 'icon': 'vertex_paint_average', 'default': True},
                {'name': 'Smear', 'tool': 'builtin_brush.Smear', 'icon': 'vertex_paint_smear', 'default': True},
                {'name': 'Replace', 'tool': 'builtin_brush.Replace', 'icon': 'vertex_paint_replace', 'default': True},
            ]
        }
        s['edit'] = {
            'name': 'Edit Mode',
            'name_short': 'Edit',
            'mode': 'EDIT_GPENCIL',
            'active_tools': [],
            'tools': [
                {'name': 'Select Box', 'tool': 'builtin.select_box', 'icon': 'object_select', 'default': True},
                {'name': 'Move', 'tool': 'builtin.move', 'icon': 'object_move', 'default': True},
                {'name': 'Rotate', 'tool': 'builtin.rotate', 'icon': 'object_rotate', 'default': True},
                {'name': 'Scale', 'tool': 'builtin.scale', 'icon': 'object_scale', 'default': True},
                {'name': 'Transform', 'tool': 'builtin.transform', 'icon': 'object_transform', 'default': True},
                {'name': 'Extrude', 'tool': 'builtin.extrude', 'icon': 'edit_extrude', 'default': True},
                {'name': 'Radius', 'tool': 'builtin.radius', 'icon': 'edit_radius', 'default': True},
                {'name': 'Bend', 'tool': 'builtin.bend', 'icon': 'edit_bend', 'default': False},
                {'name': 'Shear', 'tool': 'builtin.shear', 'icon': 'edit_shear', 'default': False},
                {'name': 'Transform Fill', 'tool': 'builtin.transform_fill', 'icon': 'edit_transform_fill', 'default': False},
                {'name': 'Interpolate', 'tool': 'builtin.', 'icon': 'edit_interpolate', 'default': True},
            ]
        }
        s['sculpt'] = {
            'name': 'Sculpt Mode',
            'name_short': 'Sculpt',
            'mode': 'SCULPT_GPENCIL',
            'active_tools': [],
            'tools': [
                {'name': 'Smooth', 'tool': 'builtin_brush.Smooth', 'icon': 'sculpt_smooth', 'default': True},
                {'name': 'Thickness', 'tool': 'builtin_brush.Thickness', 'icon': 'sculpt_thickness', 'default': True},
                {'name': 'Strength', 'tool': 'builtin_brush.Strength', 'icon': 'sculpt_strength', 'default': True},
                {'name': 'Randomize', 'tool': 'builtin_brush.Randomize', 'icon': 'sculpt_randomize', 'default': True},
                {'name': 'Grab', 'tool': 'builtin_brush.Grab', 'icon': 'sculpt_grab', 'default': True},
                {'name': 'Push', 'tool': 'builtin_brush.Push', 'icon': 'sculpt_push', 'default': True},
                {'name': 'Twist', 'tool': 'builtin_brush.Twist', 'icon': 'sculpt_twist', 'default': False},
                {'name': 'Pinch', 'tool': 'builtin_brush.Pinch', 'icon': 'sculpt_pinch', 'default': False},
                {'name': 'Clone', 'tool': 'builtin_brush.Clone', 'icon': 'sculpt_clone', 'default': True},
            ]
        }
        s['object'] = {
            'name': 'Object Mode',
            'name_short': 'Object',
            'mode': 'OBJECT',
            'active_tools': [],
            'tools': [
                {'name': 'Select Box', 'tool': 'builtin.select_box', 'icon': 'object_select', 'default': True},
                {'name': 'Move', 'tool': 'builtin.move', 'icon': 'object_move', 'default': True},
                {'name': 'Rotate', 'tool': 'builtin.rotate', 'icon': 'object_rotate', 'default': True},
                {'name': 'Scale', 'tool': 'builtin.scale', 'icon': 'object_scale', 'default': True},
                {'name': 'Transform', 'tool': 'builtin.transform', 'icon': 'object_transform', 'default': True},
                {'name': 'Add GP Blank', 'tool': 'add.gp.empty', 'icon': 'add_gp_empty', 'default': True},
                {'name': 'Add GP Stroke', 'tool': 'add.gp.stroke', 'icon': 'add_gp_stroke', 'default': True},
                {'name': 'Add Empty', 'tool': 'add.empty', 'icon': 'add_empty', 'default': True},
                {'name': 'Add Single Bone', 'tool': 'add.bone', 'icon': 'add_bone', 'default': False},
            ]
        }


    # Get active modes and tools (enabled in the preferences)
    def get_active_modes_and_tools(self):
        # Sync tool settings with preferences
        preferences.get_tool_preferences()
        
        # Iterate all modes, in user preferenced order
        active_modes = []
        box_i = 0
        for mode_i in self.mode_order:
            # Collect enabled tools
            mode = self.modes[mode_i]
            mode_obj = self.tools_per_mode[mode]
            active_tools = []
            for tool_i, tool in enumerate(mode_obj['tools']):
                if tool['enabled']:
                    active_tools.append(tool_i)
            
            # Add to active modes when one or more tools are enabled
            mode_obj['active_tools'] = active_tools
            if len(active_tools) > 0:
                active_modes.append((mode, box_i))
                box_i += 1

        # Get corresponding box layout for number of active modes
        # and set box index belonging to mode
        self.active_modes = []
        active_box_layout = self.box_layouts[len(active_modes)]
        for mode, box_i in active_modes:
            self.active_modes.append((mode, active_box_layout[box_i]))

        # Convert active modes to labels for Preference panel
        box_to_label = [(1, 0), (0, 1), (1, 2), (3, 2), (4, 1), (3, 0)]
        labels = [['', '', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['', '', '']]
        for mode, box_i in self.active_modes:
            row, col = box_to_label[box_i]
            labels[row][col] = self.tools_per_mode[mode]['name_short']
        labels[2][1] = '○'
        self.mode_order_labels = labels


    # Load tool icons as gpu textures
    def get_tool_icon_textures(self):
        # Get icon folder in addon directory
        local_dir = path.dirname(path.abspath(__file__)) + self.ICON_PATH
        
        # Iterate modes and tools
        self.textures = {}
        for mode in self.modes:
            mode_obj = self.tools_per_mode[mode]
            for tool in mode_obj['tools']:
                icon = tool['icon']
                # Icon not already loaded?
                if icon not in self.textures:
                    # Get image
                    file = bpy.path.abspath(local_dir + icon + '.png')
                    img = bpy.data.images.load(file)
                    
                    # Convert to texture
                    self.textures[icon] = gpu.texture.from_image(img)
                    
                    # Remove image
                    bpy.data.images.remove(img)

        # Load wheel and dot images
        imgs = ['inner_wheel', 'active_dot']
        img_np = np.empty((96 * 96 * 4), dtype=np.float32)
        theme = bpy.context.preferences.themes.items()[0][0]
        pie_colors = bpy.context.preferences.themes[theme].user_interface.wcol_toolbar_item
        wheel_color = pie_colors.inner[0:3]
        dot_color = pie_colors.inner_sel[0:3]
        for icon in imgs:
            # Load image
            file = bpy.path.abspath(local_dir + icon + '.png')
            img = bpy.data.images.load(file)
            
            # Replace color in image
            img.pixels.foreach_get(img_np)
            new_color_img = np.empty((96, 96, 4), dtype=np.float32)
            new_color_img[:, :, 0:3] = wheel_color if icon == 'inner_wheel' else dot_color
            new_color_img[:, :, 3] = img_np.reshape((96, 96, 4))[:, :, 3]
            new_color_img[new_color_img[:, :, 3] == 0] = 0
            img.pixels.foreach_set(new_color_img.ravel())
            
            # Convert to texture
            self.textures[icon] = gpu.texture.from_image(img)
            
            # Remove image
            bpy.data.images.remove(img)


tool_data = ToolData()
