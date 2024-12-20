'''
GP Tool Wheel

Addon preferences
'''

import json

import bpy
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.props import BoolProperty, CollectionProperty, IntProperty, StringProperty, EnumProperty
from bpy.types import AddonPreferences, Operator, PropertyGroup, UIList

from .tool_data import tool_data as td


# Operator for assigning keyboard shortcut
class GPTOOLWHEEL_OT_AssignHotkey(Operator):
    '''Click to set a keyboard shortcut'''
    bl_idname = 'gp_tool_wheel.assign_hotkey'
    bl_label = 'Click to set a keyboard shortcut'

    @classmethod
    def poll(cls, _):
        return True

    # Set new key mapping
    def set_new_key(self, event):
        # Remove existing key mapping
        km, kmi = td.keymappings[0]
        km.keymap_items.remove(kmi)

        # Create new mapping
        kmi = km.keymap_items.new('gpencil.tool_wheel', type=event.type, value='PRESS',
                                  alt=event.alt, ctrl=event.ctrl, shift=event.shift, oskey=event.oskey)
        td.keymappings[0] = (km, kmi)

        # Set text in operator button
        td.key_button_text = kmi.to_string()

        # Store new key as preference
        prefs = bpy.context.preferences.addons[__package__].preferences
        prefs.kmi_is_user_set = True
        prefs.kmi_key = event.type
        prefs.kmi_alt = event.alt
        prefs.kmi_ctrl = event.ctrl
        prefs.kmi_shift = event.shift
        prefs.kmi_oskey = event.oskey
        bpy.context.preferences.is_dirty = True

    # Wait for key press
    def modal(self, context, event):
        # Abort when ESC is pressed
        if event.type == 'ESC':
            self.ended(context)
            return {'CANCELLED'}

        # Only inspect key presses
        if event.value != 'PRESS':
            return {'RUNNING_MODAL'}

        # When key is not excluded, we have a hit
        if event.type not in {
            'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE',
            'TRACKPADPAN', 'TRACKPADZOOM',
            'MOUSEROTATE', 'MOUSESMARTZOOM', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'WHEELINMOUSE', 'WHEELOUTMOUSE',
            'LEFT_CTRL', 'LEFT_ALT', 'LEFT_SHIFT', 'RIGHT_ALT', 'RIGHT_CTRL', 'RIGHT_SHIFT', 'OSKEY',
            'APP', 'WINDOW_DEACTIVATE', 'TIMER', 'TIMER0', 'TIMER1', 'TIMER2', 'TIMER_JOBS',
                'TIMER_AUTOSAVE', 'TIMER_REPORT', 'TIMERREGION'}:
            self.set_new_key(event)
            self.ended(context)
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    # Start modal operator
    def execute(self, context):
        # Set button text
        td.key_button_text = 'Press a key...'
        td.key_button_depress = True

        # Run modal operator
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    # Operator ended
    def ended(self, context):
        # Restore button text
        kmi = td.keymappings[0][1]
        td.key_button_text = kmi.to_string()
        td.key_button_depress = False

        # Redraw preferences area
        wm = context.window_manager
        windows_count = len(wm.windows)
        for wi in range(1, windows_count):
            for area in wm.windows[wi].screen.areas:
                if area.type == 'PREFERENCES':
                    area.tag_redraw()


# UIList for mode order
class GPTOOLWHEEL_UL_ModeList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        layout.enabled = len(td.tools_per_mode[item.mode]['active_tools']) > 0
        label = f'  {index + 1}   {item.name}'
        layout.label(text=label)


# Operator for moving mode in Mode order list
class GPTOOLWHEEL_OT_MoveItem(Operator):
    '''Move an item upwards/downwards'''
    bl_idname = 'gp_tool_wheel.move_item'
    bl_label = 'Move an item in the list'

    direction: StringProperty()

    @classmethod
    def poll(cls, _):
        return True

    # Move selected item index
    def move_index(self):
        prefs = bpy.context.preferences.addons[__package__].preferences
        index = prefs.mode_index
        list_len = len(prefs.mode_order) - 1
        new_index = index + (-1 if self.direction == 'up' else 1)
        prefs.mode_index = max(0, min(list_len, new_index))

    # Move item upwards/downwards
    def execute(self, _):
        prefs = bpy.context.preferences.addons[__package__].preferences
        next_index = prefs.mode_index + (-1 if self.direction == 'up' else 1)
        prefs.mode_order.move(next_index, prefs.mode_index)
        self.move_index()
        return {'FINISHED'}


# Operator for saving preference definition
class GPTOOLWHEEL_OT_SavePrefDefinition(Operator, ExportHelper):
    '''Save preference definition to file'''
    bl_idname = 'gp_tool_wheel.save_pref_definition'
    bl_label = 'Save Preferences'

    filename_ext = ".json"
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,
    )

    @classmethod
    def poll(cls, _):
        return True

    def execute(self, context):
        # Get prefs
        prefs = context.preferences.addons[__package__].preferences
        tools = []
        for tool in prefs.tools:
            tools.append((tool.mode, tool.tool_index, tool.enabled,
                         tool.asset_lib_type, tool.asset_lib_id, tool.asset_id))
        mode_order = []
        for mode in prefs.mode_order:
            mode_order.append((mode.name, mode.order, mode.mode))

        # Compose data object for json
        data = {
            'tools': tools,
            'mode_order': mode_order,
            'show_hints': prefs.show_hints,
            'kmi_wheel': (True,
                          prefs.kmi_key,
                          prefs.kmi_alt,
                          prefs.kmi_ctrl,
                          prefs.kmi_shift,
                          prefs.kmi_oskey),
        }

        # Write json
        with open(self.filepath, 'w') as outfile:
            json.dump(data, outfile, indent=4)

        self.report({'INFO'}, f'Preference Definition saved to {self.filepath}')

        return {'FINISHED'}


# Operator for loading preference definition
class GPTOOLWHEEL_OT_LoadPrefDefinition(Operator, ImportHelper):
    '''Load preference definition from file'''
    bl_idname = 'gp_tool_wheel.load_pref_definition'
    bl_label = 'Load Preferences'

    filename_ext = ".json"
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,
    )

    @classmethod
    def poll(cls, _):
        return True

    def execute(self, context):
        # Get prefs
        prefs = context.preferences.addons[__package__].preferences

        # Read json
        with open(self.filepath, 'r') as infile:
            data = json.load(infile)

        # Convert data to preference settings
        prefs.tools.clear()
        for tool in data['tools']:
            pref = prefs.tools.add()
            if len(tool) == 3:
                # Before version 4.3
                pref.mode, pref.tool_index, pref.enabled = tool
            else:
                # From version 4.3 on
                pref.mode, pref.tool_index, pref.enabled, pref.asset_lib_type, pref.asset_lib_id, pref.asset_id = tool

        prefs.mode_order.clear()
        for mode in data['mode_order']:
            pref = prefs.mode_order.add()
            pref.name, pref.order, pref.mode = mode
        prefs.show_hints = data['show_hints']
        (prefs.kmi_is_user_set,
         prefs.kmi_key, prefs.kmi_alt,
         prefs.kmi_ctrl, prefs.kmi_shift, prefs.kmi_oskey) = data['kmi_wheel']

        # Remove existing key mapping
        km, kmi = td.keymappings[0]
        km.keymap_items.remove(kmi)

        # Create new mapping
        kmi = km.keymap_items.new('gpencil.tool_wheel', type=prefs.kmi_key, value='PRESS',
                                  alt=prefs.kmi_alt, ctrl=prefs.kmi_ctrl, shift=prefs.kmi_shift, oskey=prefs.kmi_oskey)
        td.keymappings[0] = (km, kmi)

        # Set text in operator button
        td.key_button_text = kmi.to_string()

        # Fill empty preferences with default values
        set_default_preferences()

        context.preferences.is_dirty = True

        self.report({'INFO'}, f'Preference Definition loaded from {self.filepath}')

        return {'FINISHED'}


# Mode order properties
class GPToolWheel_PG_mode_order(PropertyGroup):
    name: StringProperty(name='Mode')
    order: IntProperty()
    mode: StringProperty()


# Tool properties
class GPToolWheel_PG_tool(PropertyGroup):
    # Make sure Blender sees changes in preferences
    # (it doesn't autodetect that for properties in a collection)
    def on_pref_change(self, context):
        context.preferences.is_dirty = True

    mode: StringProperty()
    tool_index: IntProperty()
    enabled: BoolProperty(update=on_pref_change)
    asset_lib_type: StringProperty(update=on_pref_change)
    asset_lib_id: StringProperty(update=on_pref_change)
    asset_id: StringProperty(update=on_pref_change)


# GP Tool Wheel preferences
class GPToolWheelPreferences(AddonPreferences):
    bl_idname = __package__

    prefs_version: IntProperty(default=1)
    tools: CollectionProperty(name='Wheel Tools', type=GPToolWheel_PG_tool)
    show_hints: BoolProperty(name='Show Hints', default=True,
                             description='Show tool name when hovering over the tools in the wheel')
    mode_order: CollectionProperty(name='Mode Order', type=GPToolWheel_PG_mode_order)
    mode_index: IntProperty(name='Mode', default=0, description='Mode')

    kmi_is_user_set: BoolProperty(default=False)
    kmi_key: StringProperty()
    kmi_alt: BoolProperty()
    kmi_ctrl: BoolProperty()
    kmi_shift: BoolProperty()
    kmi_oskey: BoolProperty()

    # Draw preferences
    def draw(self, _):
        layout = self.layout
        td.get_active_modes_and_tools()
        use_brush_assets = (bpy.app.version >= (4, 3, 0))

        # Save preference definition
        box = layout.box()
        col = box.column(align=True)
        row = col.row()
        row.operator('gp_tool_wheel.save_pref_definition')
        row.operator('gp_tool_wheel.load_pref_definition')
        col.separator(factor=1.5)
        col.label(text='You can save and load the GP Tool Wheel preferences for backup purposes or', icon='FILE_TICK')
        col.label(text='for distribution to other Blender installations.')

        # Keyboard shortcut
        layout.separator(factor=0)
        box = layout.box()
        row = box.row()
        row.label(text='Keyboard shortcut for GP Tool Wheel:')
        row.operator('gp_tool_wheel.assign_hotkey', text=td.key_button_text, depress=td.key_button_depress)

        # Hints
        box = layout.box()
        col = box.column()
        col.prop(self, 'show_hints')

        # Mode order
        box = layout.box()
        row = box.column()
        row.label(text='Mode order in the wheel:')
        row = box.row().split(factor=0.35)
        row.template_list('GPTOOLWHEEL_UL_ModeList', '', self, 'mode_order', self, 'mode_index', rows=7)

        # Order buttons (operators)
        row = row.column()
        sub = row.split(factor=0.07)
        op = sub.operator('gp_tool_wheel.move_item', icon='TRIA_UP', text='')
        op.direction = 'up'
        sub = row.split(factor=0.07)
        op = sub.operator('gp_tool_wheel.move_item', icon='TRIA_DOWN', text='')
        op.direction = 'down'

        # Visual sketch of mode order in the wheel
        row.separator(factor=4)
        box = row.column().split(factor=0.6).box()
        col = box.column(align=True)
        col.enabled = False
        col.scale_y = 0.8
        for row_labels in td.mode_order_labels:
            row = col.row()
            row.alignment = 'CENTER'
            for i, label in enumerate(row_labels):
                row.label(text=label)
                if i < 2:
                    row.separator()

        # Tools per mode
        box = layout.box()
        col = box.column(align=True)
        col.label(text='Select the tools you want to appear in the tool wheel.')
        col.label(text='Tip: you can click-and-drag to change multiple values in one sweep.')
        for mode_i, mode in enumerate(td.modes_in_prefs):
            if mode_i % 3 == 0:
                box.separator(factor=0.2)
                grid = box.grid_flow(row_major=True, columns=3, even_columns=True)
            col = grid.column()
            col.label(text=td.tools_per_mode[mode]['name'])
            for index in td.tools_per_mode[mode]['tool_order']:
                tool = td.tools_per_mode[mode]['tools'][index]
                pref = get_tool_preference(mode, index)
                name = tool['as_asset']['name'] if use_brush_assets and 'as_asset' in tool and 'name' in tool['as_asset'] \
                    else tool['name']
                col.prop(pref, 'enabled', text=name)

        # Brush assets
        if bpy.app.version < (4, 3, 0):
            return

        box = layout.box()
        box.label(text='Brush Assets')
        col = box.column(align=True)
        col.separator(factor=1)
        col.label(text='Tip: instead of making manual changes here, you can right-click on a brush in', icon='BRUSHES_ALL')
        col.label(text="the brush asset shelf and choose 'Set as Tool in GP Tool Wheel...'.")

        col = box.column()
        col.separator(factor=1.0)
        col.label(text='Draw Mode')
        sub = col.column()

        tool = td.tools_per_mode['draw']['tools'][td.tint_tool_index]
        row = sub.row().split(factor=0.25)
        row.label(text='')
        row.column().label(text=tool['name'])
        pref = get_tool_preference('draw', td.tint_tool_index)
        sub.prop(pref, 'asset_lib_type', text='Library Type')
        sub.prop(pref, 'asset_lib_id', text='Library')
        sub.prop(pref, 'asset_id', text='Asset')

        col = box.column()
        col.separator(factor=4)
        col.label(text='Sculpt Mode')
        sub = col.column()

        for index, tool in enumerate(td.tools_per_mode['sculpt']['tools']):
            pref = get_tool_preference('sculpt', index)
            row = sub.row().split(factor=0.25)
            row.label(text='')
            row.column().label(text=tool['name'])
            sub.prop(pref, 'asset_lib_type', text='Library Type')
            sub.prop(pref, 'asset_lib_id', text='Library')
            sub.prop(pref, 'asset_id', text='Asset')
            sub.separator(factor=1.0)


# When not set already, set default tool preferences
def set_default_preferences():
    # Get tool preferences
    addon_prefs = bpy.context.preferences.addons[__package__].preferences
    tool_prefs = addon_prefs.tools

    # When there are no tool preferences, add them
    if len(tool_prefs) == 0:
        for mode in td.modes:
            for i, tool in enumerate(td.tools_per_mode[mode]['tools']):
                pref = tool_prefs.add()
                pref.mode = mode
                pref.tool_index = i
                pref.enabled = tool['default']

    # When brush asset data is not set, add it
    for mode in td.modes:
        for i, tool in enumerate(td.tools_per_mode[mode]['tools']):
            if 'as_asset' in tool and tool['as_asset']['tool'] == '':
                pref = get_tool_preference(mode, i)
                asset = tool['as_asset']
                if pref.asset_lib_type == '':
                    pref.asset_lib_type = asset['asset_library_type']
                    pref.asset_lib_id = asset['asset_library_identifier']
                    pref.asset_id = asset['relative_asset_identifier']

    # When there is no mode order, add it
    mode_order = addon_prefs.mode_order
    if not mode_order:
        for i in range(len(td.modes)):
            pref = mode_order.add()
            pref.name = td.tools_per_mode[td.modes[i]]['name']
            pref.order = i
            pref.mode = td.modes[i]

    # When there is no user defined keyboard shortcut,
    # assign F8
    if not addon_prefs.kmi_is_user_set:
        addon_prefs.kmi_key = 'F8'
        addon_prefs.kmi_ctrl = False
        addon_prefs.kmi_shift = False
        addon_prefs.kmi_alt = False
        addon_prefs.kmi_oskey = False


# Get tool preference (by mode and tool index)
def get_tool_preference(mode, index):
    prefs = bpy.context.preferences.addons[__package__].preferences
    for pref in prefs.tools:
        if pref.mode == mode and pref.tool_index == index:
            return pref
    return None


# Get the tool preferences
def get_tool_preferences():
    # Get tool preferences
    prefs = bpy.context.preferences.addons[__package__].preferences

    # Reset list
    for mode in td.modes:
        for tool in td.tools_per_mode[mode]['tools']:
            tool.pop('pref', None)

    # Update tool list
    for pref in prefs.tools:
        tool = td.tools_per_mode[pref.mode]['tools'][pref.tool_index]
        tool['enabled'] = pref.enabled
        tool['pref'] = pref

        if 'as_asset' in tool and tool['as_asset']['tool'] == '' and pref.asset_id:
            asset = tool['as_asset']
            asset['asset_library_type'] = pref.asset_lib_type
            asset['asset_library_identifier'] = pref.asset_lib_id
            asset['relative_asset_identifier'] = pref.asset_id

    # Check for new tools, not yet set in list
    for mode in td.modes:
        for i, tool in enumerate(td.tools_per_mode[mode]['tools']):
            if 'pref' not in tool:
                pref = prefs.tools.add()
                pref.mode = mode
                pref.tool_index = i
                pref.enabled = tool['default']
                tool['enabled'] = pref.enabled
                tool['pref'] = pref

                if 'as_asset' in tool and tool['as_asset']['tool'] == '' and pref.asset_id:
                    asset = tool['as_asset']
                    asset['asset_library_type'] = pref.asset_lib_type
                    asset['asset_library_identifier'] = pref.asset_lib_id
                    asset['relative_asset_identifier'] = pref.asset_id

    # Get mode order
    td.mode_order = []
    for pref in prefs.mode_order:
        td.mode_order.append(pref.order)


class GPENCIL_OT_link_brush_to_gp_tool_wheel(Operator):
    '''Link current brush asset to a tool in the GP Tool Wheel'''
    bl_idname = "gpencil.link_brush_to_gp_tool_wheel"
    bl_label = "Set Brush in GP Tool Wheel"
    bl_options = {'REGISTER', 'UNDO'}

    brush_items_draw: EnumProperty(items=[('0', 'Tint', '')], name='Tool')
    brush_items_sculpt: EnumProperty(items=[
        ('0', 'Smooth', ''),
        ('1', 'Thickness', ''),
        ('2', 'Strength', ''),
        ('3', 'Randomize', ''),
        ('4', 'Grab', ''),
        ('5', 'Pull', ''),
        ('6', 'Twist', ''),
        ('7', 'Pinch', ''),
        ('8', 'Clone', ''),
    ], name='Tool')

    sculpt_tools = ['smooth', 'thickness', 'strength', 'randomize', 'grab', 'pull', 'twist', 'pinch', 'clone']
    brush_name = ''

    @classmethod
    def poll(cls, context):
        if context.mode not in ['PAINT_GREASE_PENCIL', 'SCULPT_GREASE_PENCIL']:
            return False

        brush_asset = None
        if context.mode == 'PAINT_GREASE_PENCIL':
            brush_asset = context.tool_settings.gpencil_paint.brush_asset_reference
        elif context.mode == 'SCULPT_GREASE_PENCIL':
            brush_asset = context.tool_settings.gpencil_sculpt_paint.brush_asset_reference
        return brush_asset is not None

    def invoke(self, context, _):
        # Get brush asset name (part after last / in relative_asset_identifier)
        brush_asset = None
        if context.mode == 'PAINT_GREASE_PENCIL':
            brush_asset = context.tool_settings.gpencil_paint.brush_asset_reference
        elif context.mode == 'SCULPT_GREASE_PENCIL':
            brush_asset = context.tool_settings.gpencil_sculpt_paint.brush_asset_reference
        brush_name = brush_asset.relative_asset_identifier
        brush_name = brush_name[brush_name.rfind('/') + 1:]
        self.brush_name = brush_name

        # And make a tool guess, based on the brush name
        if context.mode == 'SCULPT_GREASE_PENCIL':
            brush_name_parts = brush_name.lower().split()
            for part in brush_name_parts:
                if part and part in self.sculpt_tools:
                    tool_index = self.sculpt_tools.index(part)
                    self.brush_items_sculpt = str(tool_index)
                    break

        # Invoke dialog
        return context.window_manager.invoke_props_dialog(self, width=240)

    def draw(self, context):
        layout = self.layout
        layout.label(text=f"Use brush '{self.brush_name}' for tool:")
        if context.mode == 'PAINT_GREASE_PENCIL':
            layout.props_enum(self, 'brush_items_draw')
        if context.mode == 'SCULPT_GREASE_PENCIL':
            layout.props_enum(self, 'brush_items_sculpt')
        layout.label(text="in the GP Tool Wheel.")

    def execute(self, context):
        wheel_tool_asset = None
        mode = ''
        index = 0
        if context.mode == 'PAINT_GREASE_PENCIL':
            brush_asset = context.tool_settings.gpencil_paint.brush_asset_reference
            wheel_tool_asset = td.tools_per_mode['draw']['tools'][td.tint_tool_index]['as_asset']
            mode = 'draw'
            index = td.tint_tool_index
        if context.mode == 'SCULPT_GREASE_PENCIL':
            brush_asset = context.tool_settings.gpencil_sculpt_paint.brush_asset_reference
            wheel_tool_asset = td.tools_per_mode['sculpt']['tools'][int(self.brush_items_sculpt)]['as_asset']
            mode = 'sculpt'
            index = int(self.brush_items_sculpt)

        if wheel_tool_asset is not None:
            wheel_tool_asset['asset_library_type'] = brush_asset.asset_library_type
            wheel_tool_asset['asset_library_identifier'] = brush_asset.asset_library_identifier
            wheel_tool_asset['relative_asset_identifier'] = brush_asset.relative_asset_identifier

            # Update tool in addon preferences
            pref = get_tool_preference(mode, index)
            pref.asset_lib_type = brush_asset.asset_library_type
            pref.asset_lib_id = brush_asset.asset_library_identifier
            pref.asset_id = brush_asset.relative_asset_identifier
            context.preferences.is_dirty = True

        return {'FINISHED'}


def brush_asset_context_menu_draw(self, _):
    layout = self.layout
    layout.separator()
    layout.operator("gpencil.link_brush_to_gp_tool_wheel", text="Set as Tool in GP Tool Wheel...")


# Add operator to brush asset context menu for linking a brush asset to a tool in the tool wheel
def add_brush_asset_context_menu_item():
    if bpy.app.version >= (4, 3, 0):
        if hasattr(bpy.types.VIEW3D_MT_brush_context_menu.draw, '_draw_funcs'):
            if brush_asset_context_menu_draw in bpy.types.VIEW3D_MT_brush_context_menu.draw._draw_funcs:
                return
        bpy.types.VIEW3D_MT_brush_context_menu.append(brush_asset_context_menu_draw)


# Remove operator from brush asset context menu
def remove_brush_asset_context_menu_item():
    if bpy.app.version >= (4, 3, 0):
        bpy.types.VIEW3D_MT_brush_context_menu.remove(brush_asset_context_menu_draw)


# Get show hints preference settings
def get_show_hints():
    return bpy.context.preferences.addons[__package__].preferences.show_hints


# Assign keyboard shortcut to tool wheel
def assign_hotkey_to_tool_wheel():
    # Get preferences
    prefs = bpy.context.preferences.addons[__package__].preferences

    # Get key config
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        # Set keymap item
        km = kc.keymaps.new(name='Object Non-modal', space_type='EMPTY', region_type='WINDOW')
        kmi = km.keymap_items.new('gpencil.tool_wheel', type=prefs.kmi_key, value='PRESS',
                                  alt=prefs.kmi_alt, ctrl=prefs.kmi_ctrl, shift=prefs.kmi_shift, oskey=prefs.kmi_oskey)
        td.keymappings.append((km, kmi))

        # Set text in preferences operator
        GPTOOLWHEEL_OT_AssignHotkey.bl_label = kmi.to_string()
        td.key_button_text = kmi.to_string()


# Remove keyboard shortcut
def remove_hotkey_of_tool_wheel():
    for km, kmi in td.keymappings:
        km.keymap_items.remove(kmi)
    td.keymappings.clear()
