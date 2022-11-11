import bpy
from bpy.types import Operator

from .tool_data import tool_data as td
from .tool_wheel_draw import tool_wheel


class GPENCIL_OT_tool_wheel(Operator):
    '''Grease Pencil tool wheel for quickly selecting tools in another mode'''
    bl_idname = "gpencil.tool_wheel"
    bl_label = "Grease Pencil Tool Wheel"
    bl_options = {'REGISTER', 'UNDO'}

    _draw_handle = None
    _brush_sizes = [0, 0, 0, 0]
    
    
    @classmethod
    def poll(cls, context):
        ob = context.object
        return (ob and ob.type == 'GPENCIL' 
                and context.area and context.area.type == 'VIEW_3D')


    # Switch to new mode and tool
    def switch_mode_and_tool(self, context, new_mode, new_tool):
        # Clean up wheel
        self.ended(context)
        
        # No active mode selected?
        if new_mode == '':
            return {'CANCELLED'}
        
        # Get selected mode
        mode = td.tools_per_mode[new_mode]
        
        # Switch to mode
        if mode['mode'] != context.mode:
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
        elif new_tool == -1:
            return {'CANCELLED'}
        
        # Switch to tool
        if new_tool != -1:
            tool = td.tools_per_mode[new_mode]['tools'][new_tool]['tool']
            # Handle 'add' tools
            if tool.startswith('add.'):
                match tool:
                    case 'add.empty':
                        bpy.ops.object.empty_add(radius=0.1)
                    case 'add.bone':
                        bpy.ops.object.armature_add(radius=0.4)
                    case 'add.gp.stroke':
                        bpy.ops.object.gpencil_add(type='STROKE')
                    case 'add.gp.empty':
                        bpy.ops.object.gpencil_add(type='EMPTY')
            else:
                # Switch to tool
                bpy.ops.wm.tool_set_by_id(name=tool)
        
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
            return self.switch_mode_and_tool(context, tool_wheel.active_mode, tool_wheel.active_tool)
        
        # Redraw area on mouse move
        if event.type == 'MOUSEMOVE':
            tool_wheel.mouse_x = event.mouse_region_x
            tool_wheel.mouse_y = event.mouse_region_y
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
        if not tool_wheel.prepare(event, area, context):
            return {'CANCELLED'}
        
        # Set cursor to default
        context.window.cursor_modal_set('DEFAULT')
        
        # An active brush cursor (red circle) can visually interfere with tool wheel,
        # so set brush size temporarily to 0.
        ts = context.tool_settings
        for i, brush in enumerate([ts.gpencil_paint.brush,
                                   ts.gpencil_sculpt_paint.brush,
                                   ts.gpencil_vertex_paint.brush,
                                   ts.gpencil_weight_paint.brush]):
            self._brush_sizes[i] = brush.size
            brush.size = 0
        
        # Add draw handler to 3D viewport
        args = (context,)
        self._draw_handle = area.spaces[0].draw_handler_add(tool_wheel.draw, args, 'WINDOW', 'POST_PIXEL')
        area.tag_redraw()
        
        # Run modal operator
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    # Operator ended, clean up
    def ended(self, context):
        # Restore cursor
        context.window.cursor_modal_restore()
        
        # Restore brush size
        ts = context.tool_settings
        for i, brush in enumerate([ts.gpencil_paint.brush,
                                   ts.gpencil_sculpt_paint.brush,
                                   ts.gpencil_vertex_paint.brush,
                                   ts.gpencil_weight_paint.brush]):
            brush.size = self._brush_sizes[i]
        
        # Remove draw handler
        context.area.spaces[0].draw_handler_remove(self._draw_handle, 'WINDOW')
        context.area.tag_redraw()
        
        # Clean up draw
        tool_wheel.end()
