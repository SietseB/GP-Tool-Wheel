'''
GP Tool Wheel

Tool wheel drawing
'''

import math
import numpy as np
import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from gpu_extras.presets import draw_texture_2d

from .preferences import get_show_hints
from .tool_data import tool_data as td


class ToolButton():
    BUTTON_IMG_SIZE = 32
    BUTTON_IMG_PADDING = 2
    BUTTON_SIZE = BUTTON_IMG_SIZE + 2 * BUTTON_IMG_PADDING + 1
    
    def __init__(self, index):
        self.x = 0
        self.y = 0
        self.w = self.BUTTON_IMG_SIZE
        self.h = self.BUTTON_IMG_SIZE
        self.tool_index = index
        self.separator_right = False
        self.separator_top = False


class ModeBox():
    BOX_PADDING = 4
    BUTTONS_PER_ROW = 4
    TITLE_HEIGHT = 18
    
    def __init__(self, mode, box_index, tool_count, hotkey):
        self.x = 0
        self.y = 0
        self.row_count = math.ceil(tool_count / self.BUTTONS_PER_ROW)
        self.w = 2 * self.BOX_PADDING + self.BUTTONS_PER_ROW * ToolButton.BUTTON_SIZE
        self.h = (2 * self.BOX_PADDING + 
                  self.row_count * ToolButton.BUTTON_SIZE +
                  self.TITLE_HEIGHT)
        self.upwards = box_index in {0, 1, 2}
        self.mode = mode
        self.index = box_index
        self.hotkey = str(hotkey)
        self.tool_buttons = []
        self.title_x = 0
        self.title_y = 0
        self.sep_offset = 1 if box_index in {2, 3} else 0
        self.texture = None
        self.texture_sel = None


class ToolWheel():
    BOX_SPACING = -65
    BOX_ANGLE = math.radians(3.5)
    HINT_WIDTH = 100
    HINT_HEIGHT = 20
    
    def __init__(self):
        self.center_x = 0
        self.center_y = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.area = None
        self.boxes = []
        self.rect_indices = ((0, 1, 2), (2, 1, 3))
        self.show_hints = True
        self.active_mode = ''
        self.active_tool = -1
    
    
    def get_adjusted_color(self, color, perc):
        new_color = [0, 0, 0, color[3]]
        for i in range(3):
            new_color[i] = max(0, min(1, color[i] + (1 - color[i]) * perc))
        return new_color
    
    
    def get_box_rounded_corners(self, img_np, w, h):
        # Round corners with alpha 0.92, 0.8, 0.25 and 0.0
        alpha_list = [(0, 0.0), (1, 0.25), (2, 0.8), (3, 0.92)]
        for d, alpha in alpha_list:
            for cy in [0, h - 1]:
                dy = d if cy == 0 else -d
                for cx in [0, w - 1]:
                    dx = d if cx == 0 else -d
                    if alpha == 0:
                        img_np[cy, cx] = 0
                    else:
                        img_np[cy + dy, cx, 3] = alpha
                        img_np[cy, cx + dx, 3] = alpha
    
    
    def prepare(self, event, area, context):
        box: ModeBox
        
        # Init
        self.active_mode = ''
        self.active_tool = -1
        
        # Store area and wheel center
        self.area = area
        self.center_x = event.mouse_region_x
        self.center_y = event.mouse_region_y
        self.mouse_x = event.mouse_region_x
        self.mouse_y = event.mouse_region_y
        
        # Get show hints preference
        self.show_hints = get_show_hints()
        
        # Get active modes and tools
        td.get_active_modes_and_tools()
        
        # Create draw boxes for active modes
        self.boxes = []
        for mode, box_index, hotkey in td.active_modes:
            tool_count = len(td.tools_per_mode[mode]['active_tools'])
            box = ModeBox(mode, box_index, tool_count, hotkey)
            self.boxes.append(box)
        
        # No active modes (unlikely, but we have to check)
        if len(self.boxes) == 0:
            return False
        
        # Position boxes
        box_w = self.boxes[0].w
        box_w_half = int(box_w * 0.5)
        wheel_radius = box_w + self.BOX_SPACING
        dx = math.cos(self.BOX_ANGLE) * wheel_radius
        dy = math.sin(self.BOX_ANGLE) * wheel_radius
        wheel_radius = int(wheel_radius * 0.5)
        min_x = math.inf
        min_y = math.inf
        max_x = -math.inf
        max_y = -math.inf
        for box in self.boxes:
            # Position box in wheel
            match box.index:
                case 0:
                    box.x = -dx - box_w
                    box.y = dy + box.h
                case 1:
                    box.x = -box_w_half
                    box.y = wheel_radius + box.h
                case 2:
                    box.x = dx
                    box.y = dy + box.h
                case 3:
                    box.x = dx
                    box.y = -dy
                case 4:
                    box.x = -box_w_half
                    box.y = -wheel_radius
                case 5:
                    box.x = -dx - box_w
                    box.y = -dy
            
            # Apply cursor coordinates
            box.x += event.mouse_region_x
            box.y += event.mouse_region_y
            
            # Get bounding box
            min_x = min(min_x, box.x)
            min_y = min(min_y, box.y - box.h)
            max_x = max(max_x, box.x + box.w)
            max_y = max(max_y, box.y)
        
        # Get width of toolbar and n-panel
        left_padding = 3
        right_padding = 3
        for region in area.regions:
            if region.alignment == 'LEFT' and region.width > left_padding:
                left_padding = region.width
            if region.alignment == 'RIGHT' and region.width > right_padding:
                right_padding = region.width
        
        # Make sure bounding box is within area bounds
        dx = 0
        dy = 0
        if min_x < left_padding:
            dx = left_padding - min_x
            max_x += dx
        if max_x > area.width - right_padding:
            dx = area.width - right_padding - max_x
        if min_y < 3:
            dy = 3 - min_y
            max_y += dy
        if max_y > area.height - 54:
            dy = area.height - 54 - max_y
        
        # Adjust xy of boxes if not within area bounds
        if dx != 0 or dy != 0:
            self.center_x += dx
            self.center_y += dy
            for box in self.boxes:
                box.x += dx
                box.y += dy
        
        # Create buttons within boxes
        padding = ModeBox.BOX_PADDING
        bsize = ToolButton.BUTTON_SIZE
        for box in self.boxes:
            box.tool_buttons = []
            right_to_left = box.index in {0, 5}
            row = 0
            column = ModeBox.BUTTONS_PER_ROW - 1 if right_to_left else 0
            dir = -1 if right_to_left else 1
            for tool_i in td.tools_per_mode[box.mode]['active_tools']:
                # Create button
                button = ToolButton(tool_i)
                
                # Calculate position
                button.x = box.x + padding + bsize * column
                if box.upwards:
                    button.y = box.y - box.h + padding + bsize * (row + 1)
                else:
                    button.y = box.y - padding - bsize * row
                
                # Line separator on the right and top?
                button.separator_right = column != ModeBox.BUTTONS_PER_ROW - 1
                button.separator_top = column == 0 and ((box.upwards and row < box.row_count - 1) 
                                                        or (not box.upwards and row > 0))
                
                # Append button to mode box
                box.tool_buttons.append(button)
                
                # Increase column (and row)
                column += dir
                if column >= ModeBox.BUTTONS_PER_ROW or column < 0:
                    column = ModeBox.BUTTONS_PER_ROW - 1 if right_to_left else 0
                    row += 1

            # Set position of box title
            box.title_x = box.x + box.BOX_PADDING
            if box.upwards:
                box.title_y = box.y - box.BOX_PADDING - ModeBox.TITLE_HEIGHT + 7
            else:
                box.title_y = box.y - box.h + box.BOX_PADDING + 3

        # Get pie menu colors from active theme
        theme = context.preferences.themes.items()[0][0]
        wheel_colors = context.preferences.themes[theme].user_interface.wcol_toolbar_item
        base_color = list(wheel_colors.inner)[0:3] + [1]
        hint_color = self.get_adjusted_color(base_color, 0.25)
        hint_color[3] = 0.98
        box_color = self.get_adjusted_color(base_color, -0.03)
        box_color_sel = self.get_adjusted_color(base_color, -0.10)
        box_title_bg = self.get_adjusted_color(base_color, -0.10)
        box_title_bg_sel = self.get_adjusted_color(base_color, -0.20)
        self.sep_color = self.get_adjusted_color(list(wheel_colors.outline)[0:3] + [1], -0.03)
        self.sep_color_sel = self.get_adjusted_color(self.sep_color, -0.07)
        self.text_color = wheel_colors.text
        self.highlight_color = self.get_adjusted_color(base_color, 0.05)
        
        # Init shaders
        self.shader_icon_bg = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        self.shader_icon_bg.bind()

        # Create icon background batch
        bsize = ToolButton.BUTTON_IMG_SIZE
        verts = ((0, 0), (bsize, 0), (0, -bsize), (bsize, -bsize))
        self.batch_icon_bg = batch_for_shader(self.shader_icon_bg, 'TRIS', {'pos': verts}, indices=self.rect_indices)
        
        # Create textures with rounded corners for mode boxes
        for box in self.boxes:
            # Create image
            img = bpy.data.images.new('temp_gp_tool_wheel', box.w, box.h, alpha=True)
            img_np = np.empty((box.h, box.w, 4), dtype=np.float32)
            
            for sel in range(2):
                # Fill with box color
                img_np[:, :] = box_color if sel == 0 else box_color_sel
                
                # Darken title area
                color = box_title_bg if sel == 0 else box_title_bg_sel
                if box.upwards:
                    img_np[-20:] = color
                else:
                    img_np[0:20] = color
                
                # Get rounded corners
                self.get_box_rounded_corners(img_np, box.w, box.h)
                img.pixels.foreach_set(img_np.ravel())
                
                # Convert to texture
                if sel == 0:
                    box.texture = gpu.texture.from_image(img)
                else:
                    box.texture_sel = gpu.texture.from_image(img)
            
            # Remove image
            bpy.data.images.remove(img)

        # Create texture for hint box
        if self.show_hints:
            # Create image
            img = bpy.data.images.new('temp_gp_tool_wheel', self.HINT_WIDTH, self.HINT_HEIGHT, alpha=True)
            img_np = np.empty((self.HINT_HEIGHT, self.HINT_WIDTH, 4), dtype=np.float32)
            
            # Fill with box color
            img_np[:, :] = hint_color
            
            # Get rounded corners
            self.get_box_rounded_corners(img_np, self.HINT_WIDTH, self.HINT_HEIGHT)
            img.pixels.foreach_set(img_np.ravel())
            
            # Convert to texture
            self.hint_texture = gpu.texture.from_image(img)
            
            # Remove image
            bpy.data.images.remove(img)
        
        return True

    
    def end(self):
        # Delete shaders and textures
        self.shader_icon_bg = None
        self.batch_icon_bg = None
        for box in self.boxes:
            del box.texture
            del box.texture_sel
    
    
    def draw(self, context):
        box: ModeBox
        button: ToolButton
        
        # Drawing in the area the tool wheel was invoked?
        if context.area != self.area:
            return
        
        # Inits
        ipad = ToolButton.BUTTON_IMG_PADDING
        gpu.state.blend_set('ALPHA')
        self.active_mode = ''
        
        # Get active mode, based on angle of mouse in the wheel
        dx = self.mouse_x - self.center_x
        dy = self.mouse_y - self.center_y
        significant_angle = abs(dx) > 3 or abs(dy) > 3
        angle = math.degrees(math.atan2(dy, dx))
        if angle < 0:
            angle += 360
        active_box_index = td.box_by_angle[int(angle // 45)] if significant_angle else -1
        for box in self.boxes:
            if box.index == active_box_index:
                self.active_mode = box.mode
        
        # Override: box is active when mouse is pointing at it
        active_box = None
        for box in self.boxes:
            if (box.x <= self.mouse_x <= box.x + box.w and
                box.y - box.h <= self.mouse_y <= box.y):
                self.active_mode = box.mode
            if self.active_mode == box.mode:
                active_box = box
        
        # Draw center wheel
        draw_texture_2d(td.textures['inner_wheel'], (self.center_x - 24, self.center_y - 24), 48, 48)
        
        # Iterate boxes (modes)
        active_tool = -1
        for box in self.boxes:
            # Draw box (in selected state or not)
            box_is_selected = box.mode == self.active_mode
            texture = box.texture_sel if box_is_selected else box.texture
            draw_texture_2d(texture, (box.x, box.y - box.h), box.w, box.h)
            
            # Draw tool buttons
            for button in box.tool_buttons:
                # Get tool
                tool = td.tools_per_mode[box.mode]['tools'][button.tool_index]
                
                # Is the icon active (mouse pointing at it)?
                is_active = (button.x <= self.mouse_x <= button.x + button.BUTTON_SIZE and 
                             button.y - button.BUTTON_SIZE <= self.mouse_y <= button.y)
                if is_active:
                    active_tool = button.tool_index
                
                # Draw tool icon background
                if is_active:
                    gpu.matrix.push()
                    gpu.matrix.translate((button.x + button.BUTTON_IMG_PADDING, button.y - button.BUTTON_IMG_PADDING))
                    color = self.highlight_color
                    self.shader_icon_bg.uniform_float('color', color)
                    self.batch_icon_bg.draw(self.shader_icon_bg)
                    gpu.matrix.pop()
                
                # Draw tool icon
                texture = td.textures[tool['icon']]
                x = button.x + ipad
                y = button.y - button.h - ipad
                draw_texture_2d(texture, (x, y), button.w, button.h)
                
                # Draw separator lines
                if button.separator_right or button.separator_top:
                    coords = []
                    if button.separator_right:
                        x0 = button.x + button.w + ModeBox.BOX_PADDING + box.sep_offset
                        y0 = button.y - ModeBox.BOX_PADDING
                        y1 = button.y - button.h
                        coords.append((x0, y0))
                        coords.append((x0, y1))
                    if button.separator_top:
                        x0 = box.x + ModeBox.BOX_PADDING + box.sep_offset
                        x1 = box.x + box.w - ModeBox.BOX_PADDING + box.sep_offset
                        y0 = button.y + box.sep_offset
                        coords.append((x0, y0))
                        coords.append( (x1, y0))
                    batch = batch_for_shader(self.shader_icon_bg, 'LINES', {'pos': coords})
                    color = self.sep_color_sel if box_is_selected else self.sep_color
                    self.shader_icon_bg.uniform_float('color', color)
                    batch.draw(self.shader_icon_bg)
        
        self.active_tool = active_tool
        
        # Draw dot on inner wheel
        if significant_angle:
            angle = math.radians(angle)
            dx = self.center_x + math.cos(angle) * 19 - 4
            dy = self.center_y + math.sin(angle) * 19 - 4
            draw_texture_2d(td.textures['active_dot'], (dx, dy), 8, 8)
        
        # Draw dot on active box
        if active_box is not None:
            box = active_box
            match box.index:
                case 0:
                    dx = box.x + box.w + 2
                    dy = box.y - box.h + 14
                case 1:
                    dx = box.x + box.w * 0.5 - 5
                    dy = box.y - box.h - 12
                case 2:
                    dx = box.x - 12
                    dy = box.y - box.h + 14
                case 3:
                    dx = box.x - 12
                    dy = box.y - 24
                case 4:
                    dx = box.x + box.w * 0.5 - 5
                    dy = box.y + 2
                case 5:
                    dx = box.x + box.w + 2
                    dy = box.y - 24
            
            draw_texture_2d(td.textures['active_dot'], (dx, dy), 10, 10)
        
        # Draw active mode or tool name as hint
        # Note: this must be done last, because blf messes with the alpha state
        blf.size(0, 11)
        if self.show_hints and active_box is not None:
            # Draw rectangle in center of wheel
            dx = self.center_x - self.HINT_WIDTH * 0.5
            dy = self.center_y - self.HINT_HEIGHT * 0.5
            draw_texture_2d(self.hint_texture, (dx, dy), self.HINT_WIDTH, self.HINT_HEIGHT)            
            
            # Draw hint text
            if self.active_tool == -1:
                hint = td.tools_per_mode[self.active_mode]['name']
            else:
                hint = td.tools_per_mode[self.active_mode]['tools'][self.active_tool]['name']
            tw, _ = blf.dimensions(0, hint)
            tx = self.center_x - tw * 0.5
            blf.color(0, self.text_color[0], self.text_color[1], self.text_color[2], 0.8)
            blf.position(0, tx, dy + 6, 0)
            blf.draw(0, hint)
        
        # Draw centered box title and hotkey on the right
        for box in self.boxes:
            # Title
            text = td.tools_per_mode[box.mode]['name']
            tw, _ = blf.dimensions(0, text)
            dx = int((box.w - tw) * 0.5) - ModeBox.BOX_PADDING
            alpha = 0.9 if box.mode == self.active_mode else 0.25
            blf.color(0, self.text_color[0], self.text_color[1], self.text_color[2], alpha)
            blf.position(0, box.title_x + dx, box.title_y, 0)
            blf.draw(0, text)
            
            # Hotkey
            text = box.hotkey
            tw, _ = blf.dimensions(0, text)
            dx = box.x + box.w - ModeBox.BOX_PADDING * 2 - tw
            alpha = 0.4 if box.mode == self.active_mode else 0.15
            blf.color(0, self.text_color[0], self.text_color[1], self.text_color[2], alpha)
            blf.position(0, dx, box.title_y, 0)
            blf.draw(0, text)
        
        # Reset gpu state
        gpu.state.blend_set('NONE')
