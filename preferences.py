'''
GP Tool Wheel

Addon preferences
'''
import bpy
from bpy.props import BoolProperty, CollectionProperty, IntProperty, StringProperty
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
            'APP', 'WINDOW_DEACTIVATE',
            'TIMER', 'TIMER0', 'TIMER1', 'TIMER2', 'TIMER_JOBS',
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


# Mode order properties
class GPToolWheel_PG_mode_order(PropertyGroup):
    name: StringProperty(name='Mode')
    order: IntProperty()
    mode: StringProperty()


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


# Tool properties
class GPToolWheel_PG_tool(PropertyGroup):
    # Make sure Blender sees changes in preferences
    # (it doesn't autodetect that for properties in a collection)
    def on_pref_change(self, context):
        context.preferences.is_dirty = True
    
    mode: StringProperty()
    tool_index: IntProperty()
    enabled: BoolProperty(update=on_pref_change)


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
        
        # Keyboard shortcut
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
            for tool in td.tools_per_mode[mode]['tools']:
                col.prop(tool['pref'], 'enabled', text=tool['name'])
            

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

    # When there is no mode order, add it
    mode_order = addon_prefs.mode_order
    if not mode_order:
        for i in range(len(td.modes)):
            pref = mode_order.add()
            pref.name = td.tools_per_mode[td.modes[i]]['name']
            pref.order = i
            pref.mode = td.modes[i]

    # When there is no user defined keyboard shortcut,
    # assign Ctrl Tab / Tab
    if not addon_prefs.kmi_is_user_set:
        addon_prefs.kmi_key = 'TAB'
        addon_prefs.kmi_alt = False
        addon_prefs.kmi_shift = False
        addon_prefs.kmi_oskey = False
        # Use Tab for pie menu or Ctrl Tab?
        addon_prefs.kmi_ctrl = not bpy.context.window_manager.keyconfigs.active.preferences.use_v3d_tab_menu


# Get the tool preferences
def get_tool_preferences():
    # Get tool preferences
    prefs = bpy.context.preferences.addons[__package__].preferences

    # Update tool list
    for pref in prefs.tools:
        tool = td.tools_per_mode[pref.mode]['tools'][pref.tool_index]
        tool['enabled'] = pref.enabled
        tool['pref'] = pref

    # Get mode order
    td.mode_order = []
    for pref in prefs.mode_order:
        td.mode_order.append(pref.order)


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
