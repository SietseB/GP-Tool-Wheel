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
    ICON_PATH = path.sep + 'icons' + path.sep

    def __init__(self):
        self.keymappings = []
        self.key_button_text = ''
        self.key_button_depress = False
        self.mode_order_labels = []
        self.active_modes = []
        self.textures = {}
        self.modes = ['weight', 'draw', 'vertex', 'edit', 'sculpt', 'object']
        self.modes_in_prefs = ['draw', 'edit', 'sculpt', 'object', 'vertex', 'weight']
        self.mode_hotkeys = ['ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX']
        self.mode_of_hotkey = {}
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
        # Non-draw brush assets in Draw mode
        self.non_draw_assets = [
            '/Fill',
            '/Tint',
            '/Eraser',
        ]
        # Tool index for Draw tool
        self.draw_tool_index = 0
        self.tint_tool_index = 3

        # Available tools per mode
        self.tools_per_mode = {}
        s = self.tools_per_mode
        s['weight'] = {
            'name': 'Weight Paint',
            'name_short': 'Weight',
            'mode': 'WEIGHT_GPENCIL',
            'modev3': 'WEIGHT_GREASE_PENCIL',
            'active_tools': [],
            'tool_order': [0, 1, 2, 3, 4],
            'tools': [
                {'name': 'Paint', 'tool': 'builtin_brush.Weight', 'icon': 'weight_paint_draw', 'default': True, 'as_asset': {
                    'tool': 'builtin.brush',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Blur', 'tool': 'builtin_brush.Blur', 'icon': 'vertex_paint_blur', 'default': True, 'as_asset': {
                    'tool': 'builtin_brush.blur',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Average', 'tool': 'builtin_brush.Average', 'icon': 'vertex_paint_average', 'default': True, 'as_asset': {
                    'tool': 'builtin_brush.average',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Smear', 'tool': 'builtin_brush.Smear', 'icon': 'vertex_paint_smear', 'default': True, 'as_asset': {
                    'tool': 'builtin_brush.smear',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Gradient', 'tool': 'builtin_brush.Gradient', 'icon': 'weight_paint_gradient', 'default': False, 'as_asset': {
                    'tool': 'builtin_brush.gradient',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
            ]
        }
        s['draw'] = {
            'name': 'Draw Mode',
            'name_short': 'Draw',
            'mode': 'PAINT_GPENCIL',
            'modev3': 'PAINT_GREASE_PENCIL',
            'active_tools': [],
            'tool_order': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            'tools': [
                {'name': 'Draw', 'tool': 'builtin_brush.Draw', 'icon': 'draw_draw', 'default': True, 'as_asset': {
                    'tool': 'builtin.brush',
                    'asset_library_type': 'ESSENTIALS',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': 'brushes/essentials_brushes-gp_draw.blend/Brush/Pencil'
                }},
                {'name': 'Fill', 'tool': 'builtin_brush.Fill', 'icon': 'draw_fill', 'default': True, 'as_asset': {
                    'tool': 'builtin_brush.Fill',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Erase', 'tool': 'builtin_brush.Erase', 'icon': 'draw_erase', 'default': True, 'as_asset': {
                    'tool': 'builtin_brush.Erase',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Tint', 'tool': 'builtin_brush.Tint', 'icon': 'draw_tint', 'default': True, 'as_asset': {
                    'tool': '',
                    'asset_library_type': 'ESSENTIALS',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': 'brushes/essentials_brushes-gp_draw.blend/Brush/Tint'
                }},
                {'name': 'Cutter', 'tool': 'builtin.cutter', 'icon': 'draw_cutter', 'default': True, 'as_asset': {
                    'tool': 'builtin.trim',
                    'name': 'Trim',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Eyedropper', 'tool': 'builtin.eyedropper', 'icon': 'draw_eyedropper', 'default': True, 'as_asset': {
                    'tool': 'builtin.eyedropper',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Line', 'tool': 'builtin.line', 'icon': 'draw_line', 'default': True, 'as_asset': {
                    'tool': 'builtin.line',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Polyline', 'tool': 'builtin.polyline', 'icon': 'draw_polyline', 'default': True, 'as_asset': {
                    'tool': 'builtin.polyline',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Arc', 'tool': 'builtin.arc', 'icon': 'draw_arc', 'default': True, 'as_asset': {
                    'tool': 'builtin.arc',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Curve', 'tool': 'builtin.curve', 'icon': 'draw_curve', 'default': True, 'as_asset': {
                    'tool': 'builtin.curve',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Box', 'tool': 'builtin.box', 'icon': 'draw_box', 'default': True, 'as_asset': {
                    'tool': 'builtin.box',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Circle', 'tool': 'builtin.circle', 'icon': 'draw_circle', 'default': True, 'as_asset': {
                    'tool': 'builtin.circle',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Interpolate', 'tool': 'builtin.interpolate', 'icon': 'edit_interpolate', 'default': False, 'as_asset': {
                    'tool': 'builtin.interpolate',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
            ]
        }
        s['vertex'] = {
            'name': 'Vertex Paint',
            'name_short': 'Vertex',
            'mode': 'VERTEX_GPENCIL',
            'modev3': 'VERTEX_GREASE_PENCIL',
            'active_tools': [],
            'tool_order': [0, 1, 2, 3, 4],
            'tools': [
                {'name': 'Draw', 'tool': 'builtin_brush.Draw', 'icon': 'vertex_paint_draw', 'default': True, 'as_asset': {
                    'tool': 'builtin.brush',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Blur', 'tool': 'builtin_brush.Blur', 'icon': 'vertex_paint_blur', 'default': True, 'as_asset': {
                    'tool': 'builtin_brush.blur',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Average', 'tool': 'builtin_brush.Average', 'icon': 'vertex_paint_average', 'default': True, 'as_asset': {
                    'tool': 'builtin_brush.average',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Smear', 'tool': 'builtin_brush.Smear', 'icon': 'vertex_paint_smear', 'default': True, 'as_asset': {
                    'tool': 'builtin_brush.smear',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
                {'name': 'Replace', 'tool': 'builtin_brush.Replace', 'icon': 'vertex_paint_replace', 'default': True, 'as_asset': {
                    'tool': 'builtin_brush.replace',
                    'asset_library_type': '',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': ''
                }},
            ]
        }
        s['edit'] = {
            'name': 'Edit Mode',
            'name_short': 'Edit',
            'mode': 'EDIT_GPENCIL',
            'modev3': 'EDIT_GREASE_PENCIL',
            'active_tools': [],
            'tool_order': [11, 0, 12, 13, 14, 1, 2, 3, 15, 4, 5, 6, 7, 8, 16, 9, 10],
            'tools': [
                {'name': 'Select Box', 'tool': 'builtin.select_box', 'icon': 'object_select', 'default': True},
                {'name': 'Move', 'tool': 'builtin.move', 'icon': 'object_move', 'default': True},
                {'name': 'Rotate', 'tool': 'builtin.rotate', 'icon': 'object_rotate', 'default': True},
                {'name': 'Scale', 'tool': 'builtin.scale', 'icon': 'object_scale', 'default': True},
                {'name': 'Transform', 'tool': 'builtin.transform', 'icon': 'object_transform', 'default': True},
                {'name': 'Extrude', 'tool': 'builtin.extrude', 'icon': 'edit_extrude', 'default': False},
                {'name': 'Radius', 'tool': 'builtin.radius', 'icon': 'edit_radius', 'default': True},
                {'name': 'Bend', 'tool': 'builtin.bend', 'icon': 'edit_bend', 'default': False},
                {'name': 'Shear', 'tool': 'builtin.shear', 'icon': 'edit_shear', 'default': False},
                {'name': 'Transform Fill', 'tool': 'builtin.transform_fill',
                    'icon': 'edit_transform_fill', 'default': False, 'as_asset': {
                        'tool': 'builtin.texture_gradient',
                        'name': 'Gradient',
                        'icon': 'weight_paint_gradient',
                        'asset_library_type': '',
                        'asset_library_identifier': '',
                        'relative_asset_identifier': ''
                    }},
                {'name': 'Interpolate', 'tool': 'builtin.interpolate', 'icon': 'edit_interpolate', 'default': True},

                {'name': 'Tweak', 'tool': 'builtin.select', 'icon': 'edit_tweak', 'default': False},
                {'name': 'Select Circle', 'tool': 'builtin.select_circle', 'icon': 'edit_select_circle', 'default': False},
                {'name': 'Select Lasso', 'tool': 'builtin.select_lasso', 'icon': 'edit_select_lasso', 'default': False},
                {'name': 'Cursor', 'tool': 'builtin.cursor', 'icon': 'edit_cursor', 'default': False},
                {'name': 'Scale Cage', 'tool': 'builtin.scale_cage', 'icon': 'edit_scale_cage', 'default': False},
                {'name': 'To Sphere', 'tool': 'builtin.to_sphere', 'icon': 'edit_to_sphere', 'default': False},
            ]
        }
        s['sculpt'] = {
            'name': 'Sculpt Mode',
            'name_short': 'Sculpt',
            'mode': 'SCULPT_GPENCIL',
            'modev3': 'SCULPT_GREASE_PENCIL',
            'active_tools': [],
            'tool_order': [0, 1, 2, 3, 4, 5, 6, 7, 8],
            'tools': [
                {'name': 'Smooth', 'tool': 'builtin_brush.Smooth', 'icon': 'sculpt_smooth', 'default': True, 'as_asset': {
                    'tool': '',
                    'asset_library_type': 'ESSENTIALS',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': 'brushes/essentials_brushes-gp_sculpt.blend/Brush/Smooth'
                }},
                {'name': 'Thickness', 'tool': 'builtin_brush.Thickness', 'icon': 'sculpt_thickness', 'default': True, 'as_asset': {
                    'tool': '',
                    'asset_library_type': 'ESSENTIALS',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': 'brushes/essentials_brushes-gp_sculpt.blend/Brush/Thickness'
                }},
                {'name': 'Strength', 'tool': 'builtin_brush.Strength', 'icon': 'sculpt_strength', 'default': True, 'as_asset': {
                    'tool': '',
                    'asset_library_type': 'ESSENTIALS',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': 'brushes/essentials_brushes-gp_sculpt.blend/Brush/Strength'
                }},
                {'name': 'Randomize', 'tool': 'builtin_brush.Randomize', 'icon': 'sculpt_randomize', 'default': True, 'as_asset': {
                    'tool': '',
                    'asset_library_type': 'ESSENTIALS',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': 'brushes/essentials_brushes-gp_sculpt.blend/Brush/Randomize'
                }},
                {'name': 'Grab', 'tool': 'builtin_brush.Grab', 'icon': 'sculpt_grab', 'default': True, 'as_asset': {
                    'tool': '',
                    'asset_library_type': 'ESSENTIALS',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': 'brushes/essentials_brushes-gp_sculpt.blend/Brush/Grab'
                }},
                {'name': 'Push', 'tool': 'builtin_brush.Push', 'icon': 'sculpt_push', 'default': True, 'as_asset': {
                    'tool': '',
                    'name': 'Pull',
                    'asset_library_type': 'ESSENTIALS',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': 'brushes/essentials_brushes-gp_sculpt.blend/Brush/Pull'
                }},
                {'name': 'Twist', 'tool': 'builtin_brush.Twist', 'icon': 'sculpt_twist', 'default': False, 'as_asset': {
                    'tool': '',
                    'asset_library_type': 'ESSENTIALS',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': 'brushes/essentials_brushes-gp_sculpt.blend/Brush/Twist'
                }},
                {'name': 'Pinch', 'tool': 'builtin_brush.Pinch', 'icon': 'sculpt_pinch', 'default': False, 'as_asset': {
                    'tool': '',
                    'asset_library_type': 'ESSENTIALS',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': 'brushes/essentials_brushes-gp_sculpt.blend/Brush/Pinch'
                }},
                {'name': 'Clone', 'tool': 'builtin_brush.Clone', 'icon': 'sculpt_clone', 'default': True, 'as_asset': {
                    'tool': '',
                    'asset_library_type': 'ESSENTIALS',
                    'asset_library_identifier': '',
                    'relative_asset_identifier': 'brushes/essentials_brushes-gp_sculpt.blend/Brush/Clone'
                }},
            ]
        }
        s['object'] = {
            'name': 'Object Mode',
            'name_short': 'Object',
            'mode': 'OBJECT',
            'modev3': 'OBJECT',
            'active_tools': [],
            'tool_order': [0, 1, 2, 3, 4, 5, 6, 7, 8],
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
        self.mode_of_hotkey = {}
        active_modes = []
        box_i = 0
        for mode_i in self.mode_order:
            # Get mode
            mode = self.modes[mode_i]

            # Collect enabled tools
            mode_obj = self.tools_per_mode[mode]
            active_tools = []
            for tool_i in mode_obj['tool_order']:
                tool = mode_obj['tools'][tool_i]
                if tool['enabled']:
                    active_tools.append(tool_i)
            mode_obj['active_tools'] = active_tools

            # Add to active modes when one or more tools are enabled
            if len(active_tools) > 0:
                active_modes.append((mode, box_i))

                # Assign hotkey to mode
                self.mode_of_hotkey[self.mode_hotkeys[box_i]] = mode

                box_i += 1

        # Get corresponding box layout for number of active modes
        # and set box index belonging to mode
        self.active_modes = []
        active_box_layout = self.box_layouts[len(active_modes)]
        for mode, box_i in active_modes:
            self.active_modes.append((mode, active_box_layout[box_i], box_i + 1))

        # Convert active modes to labels for Preference panel
        box_to_label = [(1, 0), (0, 1), (1, 2), (3, 2), (4, 1), (3, 0)]
        labels = [['', '', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['', '', '']]
        for mode, box_i, _ in self.active_modes:
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
