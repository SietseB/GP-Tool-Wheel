bl_info = {
    "name": "GP Tool Wheel",
    "author": "Sietse Brouwer",
    "version": (1, 0, 6),
    "blender": (3, 0, 0),
    "description": "Extended pie menu for selecting Grease Pencil tools quickly.",
    "doc_url": "https://github.com/SietseB/GP-Tool-Wheel",
    "tracker_url": "https://github.com/SietseB/GP-Tool-Wheel/issues",
    "category": "3D View"
}


if 'bpy' in locals():
    import importlib
    importlib.reload(preferences)
    importlib.reload(tool_wheel_operator)
    importlib.reload(tool_data)
else:
    from . import preferences
    from . import tool_wheel_operator
    from . import tool_data

import bpy


# Inits
def addon_init():
    # Blender ready to assign hotkey?
    if bpy.context.window_manager.keyconfigs.active is None:
        # Keep interval timer alive
        return 0.2

    # Set default preferences (when needed)
    preferences.set_default_preferences()

    # Assign hotkey to tool wheel operator
    preferences.assign_hotkey_to_tool_wheel()

    # Add brush asset context menu item
    preferences.add_brush_asset_context_menu_item()

    # Load tool icons
    tool_data.tool_data.get_tool_icon_textures()


# Addon registration
def register():
    bpy.utils.register_class(preferences.GPToolWheel_PG_tool)
    bpy.utils.register_class(preferences.GPToolWheel_PG_mode_order)
    bpy.utils.register_class(preferences.GPToolWheelPreferences)
    bpy.utils.register_class(preferences.GPTOOLWHEEL_UL_ModeList)
    bpy.utils.register_class(preferences.GPTOOLWHEEL_OT_MoveItem)
    bpy.utils.register_class(preferences.GPTOOLWHEEL_OT_AssignHotkey)
    bpy.utils.register_class(preferences.GPTOOLWHEEL_OT_SavePrefDefinition)
    bpy.utils.register_class(preferences.GPTOOLWHEEL_OT_LoadPrefDefinition)
    bpy.utils.register_class(preferences.GPENCIL_OT_link_brush_to_gp_tool_wheel)
    bpy.utils.register_class(tool_wheel_operator.GPENCIL_OT_tool_wheel)

    # Delayed inits
    bpy.app.timers.register(addon_init, first_interval=0.2)


def unregister():
    bpy.utils.unregister_class(preferences.GPToolWheel_PG_tool)
    bpy.utils.unregister_class(preferences.GPToolWheel_PG_mode_order)
    bpy.utils.unregister_class(preferences.GPToolWheelPreferences)
    bpy.utils.unregister_class(preferences.GPTOOLWHEEL_UL_ModeList)
    bpy.utils.unregister_class(preferences.GPTOOLWHEEL_OT_MoveItem)
    bpy.utils.unregister_class(preferences.GPTOOLWHEEL_OT_AssignHotkey)
    bpy.utils.unregister_class(preferences.GPTOOLWHEEL_OT_SavePrefDefinition)
    bpy.utils.unregister_class(preferences.GPTOOLWHEEL_OT_LoadPrefDefinition)
    bpy.utils.unregister_class(preferences.GPENCIL_OT_link_brush_to_gp_tool_wheel)
    bpy.utils.unregister_class(tool_wheel_operator.GPENCIL_OT_tool_wheel)

    # Remove hotkey
    preferences.remove_hotkey_of_tool_wheel()

    # Remove brush asset context menu item
    preferences.remove_brush_asset_context_menu_item()


if __name__ == "__main__":
    register()
