import bpy
from bpy.types import Operator

from . import tool_wheel_draw
from .tool_data import tool_data as td


class GPENCIL_OT_tool_wheel(Operator):
    '''Grease Pencil tool wheel for quickly selecting tools in another mode'''
    bl_idname = "gpencil.tool_wheel"
    bl_label = "Grease Pencil Tool Wheel"
    bl_options = {'REGISTER', 'UNDO'}

    _draw_handle = None
    _brush_sizes = [0, 0, 0, 0, 0]
    _unprojected_radius = [0.0, 0.0, 0.0, 0.0, 0.0]
    tool_wheel = tool_wheel_draw.ToolWheel()

    @classmethod
    def poll(cls, context):
        ob = context.object
        return (ob and (ob.type == 'GPENCIL' or ob.type == 'GREASEPENCIL')
                and context.area and context.area.type == 'VIEW_3D')

    # Switch to new mode and tool
    def switch_mode_and_tool(self, context, new_mode, new_tool):
        # Clean up wheel
        self.ended(context)

        # No active mode selected?
        if new_mode == '':
            return {'CANCELLED'}

        # Get Grease Pencil version
        is_gp_legacy = context.object.type == 'GPENCIL'

        # From 4.3 on, use brush assets
        use_brush_assets = (bpy.app.version >= (4, 3, 0))
        brush_asset = None

        # Get selected mode.
        mode = td.tools_per_mode[new_mode]

        # Remember last used draw brush
        if use_brush_assets and context.mode == 'PAINT_GREASE_PENCIL':
            brush_asset = context.tool_settings.gpencil_paint.brush_asset_reference
            if brush_asset is not None:
                # When the brush asset is a fill, tint or eraser, we don't store it.
                # We only want to remember real draw brushes.
                is_draw_brush = True
                for non_draw_brush in td.non_draw_assets:
                    if brush_asset.relative_asset_identifier.find(non_draw_brush) != -1:
                        is_draw_brush = False
                        break

                if is_draw_brush:
                    # Store the draw brush asset
                    td.tools_per_mode['draw']['tools'][td.draw_tool_index]['as_asset']['asset_library_type'] = brush_asset.asset_library_type
                    td.tools_per_mode['draw']['tools'][td.draw_tool_index]['as_asset']['asset_library_identifier'] = brush_asset.asset_library_identifier
                    td.tools_per_mode['draw']['tools'][td.draw_tool_index]['as_asset']['relative_asset_identifier'] = brush_asset.relative_asset_identifier

        # Switch to mode.
        if is_gp_legacy and mode['mode'] != context.mode:
            match(new_mode):
                case 'object':
                    bpy.ops.object.mode_set(mode='OBJECT')
                case 'edit':
                    bpy.ops.gpencil.editmode_toggle()
                case 'sculpt':
                    bpy.ops.gpencil.sculptmode_toggle()
                case 'draw':
                    bpy.ops.gpencil.paintmode_toggle()
                case 'weight':
                    bpy.ops.gpencil.weightmode_toggle()
                case 'vertex':
                    bpy.ops.gpencil.vertexmode_toggle()
        elif not is_gp_legacy and mode['modev3'] != context.mode:
            match(new_mode):
                case 'object':
                    bpy.ops.object.mode_set(mode='OBJECT')
                case 'edit':
                    bpy.ops.object.mode_set(mode='EDIT')
                case 'sculpt':
                    bpy.ops.object.mode_set(mode='SCULPT_GREASE_PENCIL')
                case 'draw':
                    bpy.ops.object.mode_set(mode='PAINT_GREASE_PENCIL')
                case 'weight':
                    bpy.ops.object.mode_set(mode='WEIGHT_GREASE_PENCIL')
                case 'vertex':
                    bpy.ops.object.mode_set(mode='VERTEX_GREASE_PENCIL')
        elif new_tool == -1:
            return {'CANCELLED'}

        # Get selected tool
        if new_tool == -1:
            return {'FINISHED'}

        tool = mode['tools'][new_tool]['tool']
        tool_as_asset = None
        if use_brush_assets and 'as_asset' in mode['tools'][new_tool]:
            tool_as_asset = mode['tools'][new_tool]['as_asset']

        # Handle 'add' tools
        if tool.startswith('add.'):
            match tool:
                case 'add.empty':
                    bpy.ops.object.empty_add(radius=0.1)
                case 'add.bone':
                    bpy.ops.object.armature_add(radius=0.4)
                case 'add.gp.stroke':
                    if is_gp_legacy:
                        bpy.ops.object.gpencil_add(type='STROKE')
                    else:
                        bpy.ops.object.grease_pencil_add(type='STROKE')
                case 'add.gp.empty':
                    if is_gp_legacy:
                        bpy.ops.object.gpencil_add(type='EMPTY')
                    else:
                        bpy.ops.object.grease_pencil_add(type='EMPTY')
        else:
            # Switch to tool
            if tool_as_asset is None:
                bpy.ops.wm.tool_set_by_id(name=tool)
            else:
                # From 4.3 on, use brush assets for drawing and sculpting and tools for all the others
                use_asset = False if tool_as_asset['tool'] else True

                # Edge case: when switching from from a non-draw brush to the Draw tool,
                # use the previously stored draw brush asset.
                if new_mode == 'draw' and mode['tools'][new_tool]['name'] == 'Draw':
                    brush_asset = context.tool_settings.gpencil_paint.brush_asset_reference
                    if brush_asset is not None:
                        for non_draw_brush in td.non_draw_assets:
                            if brush_asset.relative_asset_identifier.find(non_draw_brush) != -1:
                                use_asset = True
                                break

                # Switch to the new tool or brush asset
                if use_asset:
                    # Set brush asset
                    bpy.ops.brush.asset_activate(asset_library_type=tool_as_asset['asset_library_type'],
                                                 asset_library_identifier=tool_as_asset['asset_library_identifier'],
                                                 relative_asset_identifier=tool_as_asset['relative_asset_identifier'])
                else:
                    # Set tool
                    bpy.ops.wm.tool_set_by_id(name=tool_as_asset['tool'])

        return {'FINISHED'}

    # Check modal events
    def modal(self, context, event):
        # Abort?
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.ended(context)
            return {'CANCELLED'}

        # Handle mode hotkeys
        if event.type in td.mode_of_hotkey:
            return self.switch_mode_and_tool(context, td.mode_of_hotkey[event.type], -1)

        # Handle left mouse click
        if event.type == 'LEFTMOUSE':
            return self.switch_mode_and_tool(context, self.tool_wheel.active_mode, self.tool_wheel.active_tool)

        # Redraw area on mouse move
        if event.type == 'MOUSEMOVE':
            self.tool_wheel.mouse_x = event.mouse_region_x
            self.tool_wheel.mouse_y = event.mouse_region_y
            context.area.tag_redraw()

        return {'RUNNING_MODAL'}

    # Invoke operator
    def invoke(self, context, event):
        # Mouse cursor outside viewport?
        area = context.area
        if (event.mouse_x < area.x or
            event.mouse_x > area.x + area.width or
            event.mouse_y < area.y or
                area.y + area.height - event.mouse_y < 54):
            return {'CANCELLED'}

        # Prepare draw
        if not self.tool_wheel.prepare(event, area, context):
            return {'CANCELLED'}

        # Set cursor to default
        context.window.cursor_modal_set('DEFAULT')

        # Hide brush cursor (the potentially big circle)
        ts = context.tool_settings
        ts.gpencil_paint.show_brush = False
        ts.gpencil_sculpt_paint.show_brush = False
        ts.gpencil_vertex_paint.show_brush = False
        ts.gpencil_weight_paint.show_brush = False

        # Add draw handler to 3D viewport
        args = (context,)
        self._draw_handle = area.spaces[0].draw_handler_add(
            self.tool_wheel.draw, args, 'WINDOW', 'POST_PIXEL')
        area.tag_redraw()

        # Run modal operator
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    # Operator ended, clean up
    def ended(self, context):
        # Restore cursor
        context.window.cursor_modal_restore()

        # Show brush cursor
        ts = context.tool_settings
        ts.gpencil_paint.show_brush = True
        ts.gpencil_sculpt_paint.show_brush = True
        ts.gpencil_vertex_paint.show_brush = True
        ts.gpencil_weight_paint.show_brush = True

        # Remove draw handler
        context.area.spaces[0].draw_handler_remove(self._draw_handle, 'WINDOW')
        context.area.tag_redraw()

        # Clean up draw
        self.tool_wheel.end()
