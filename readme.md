# GP Tool Wheel
*a Grease Pencil addon for [Blender](https://www.blender.org/) 3.0+ –– switch quickly between tools*

![GP Tool Wheel in action](docs/images/gp_tool_wheel_in_action.gif)

Using Grease Pencil and switching a lot between modes and tools? Then GP Tool Wheel can speed up your workflow: it combines mode and tool selection in one delicious wheel.


## How to use the wheel – press <kbd>F8</kbd>
By default you can invoke the tool wheel with the shortcut <kbd>F8</kbd>. You can change this shortcut easily by [customizing your wheel](#customize-your-wheel).

The wheel only appears when there is an active Grease Pencil object.

Selecting a tool needs no explanation: click on an icon and you are good to go.

> **Switching mode only:** Tap 1...6 on your keyboard. Or click near the colored dot in the center space of the wheel.
> 
> ![Selecting mode only](docs/images/gp_tool_wheel_selecting_mode.png)


## Customize your wheel
You can customize your wheel in the add-on preferences.

Up to Blender 4.1, go to `Edit` > `Preferences...` > `Add-ons` and look for `3D View: GP Tool Wheel`.

For Blender 4.2 and higher, go to `Edit` > `Preferences...` > `Add-ons` and look for `GP Tool Wheel`. 

Click on the arrow on the left.

Here you can compose your ideal, tailor made wheel. Perhaps you want to change it in a kind of 'Quick favorites' menu, with only the modes and tools you often use. 
Or assign <kbd>Tab</kbd> as shortcut, replacing the default pie menu.


> **Circle of GP life:** defining the order of modes
>
> ![GP Tool Wheel Preferences](docs/images/gp_tool_wheel_preferences_1.png)

> **Don't show what you don't need:** selecting your favorite tools
> 
> ![GP Tool Wheel Preferences select you tools](docs/images/gp_tool_wheel_preferences_2.png)

> **Transfer preferences to other computer or Blender installation:**
> you can save the preferences to a `.json` file and distribute that file to other computers or Blender installations.
> 
> ![Save and load preferences to/from definition file](docs/images/gp_tool_wheel_preferences_3.png)


## Link brush assets (new in Blender 4.3)

Blender 4.3 ships with the new Brush Asset Shelf, with default brushes and the option to define custom brushes yourself.
For Grease Pencil, the Brush Shelf is active in Draw and Sculpt Mode.
By default, GP Tool Wheel uses the _Essential_ brush assets that ship with Blender. 

But you can assign a custom brush to a tool in the wheel. Right-click on the brush and choose _Set as Tool in GP Tool Wheel..._

![Brush asset context menu with link brush to GP Tool Wheel](docs/images/link_brush_to_tool_1.jpg)

In the dialog that follows, select the tool in the GP Tool Wheel and click OK.

![Link brush to a tool in the GP Tool Wheel](docs/images/link_brush_to_tool_2.jpg)

Now this brush will be activated when you click on it in the wheel.


## Installation
GP Tool Wheel is suited for Blender 3.0 and higher.

For Blender 4.2 and higher, the add-on is [available as an extension](https://extensions.blender.org/add-ons/grease-pencil-tool-wheel/) at the Blender Extension platform. 
Click on the big blue 'Get Add-on' button and follow the instructions.


Up to Blender 4.1 (or when you don't want to use the Extension platform), installation of the add-on is done in the usual Blender 'legacy' way:
- Download [the latest release](https://github.com/SietseB/GP-Tool-Wheel/releases). (Make sure it is a zip file, not automatically unzipped.)
- In Blender, go to `Edit` > `Preferences...` > `Add-ons`. Click on `Install...` and select the zip file.
- When the stars are in your favour, the add-on appears. Activate it.
- And since you are here: click on the add-on arrow and take a look at the preferences straight away.


## Having issues? Or wishes?
[Create a ticket](https://github.com/SietseB/GP-Tool-Wheel/issues) and I'll see what I can do.


## Changelog
- v1.0.11 – 2025-06-09
  - Small compatibility update for Blender 5.0, `gpencil_paint.brush.gpencil_tool` property was removed
- v1.0.10 – 2025-05-22
  - When Blender was started by opening a .blend file in the file explorer, the add-on wouldn't initialize correctly. This is fixed now.
- v1.0.9 – 2025-05-18
  - Fix for separator lines not showing in some Blender versions
- v1.0.8 – 2025-05-18
  - Switching from Tint tool to Brush tool is handled better
  - Fix for draw artefacts
- v1.0.7 – 2024-12-23
  - Fix for unintended change of brush size when using the wheel
  - Tools in Edit mode completed: Tweak, Select Circle, Select Lasso, Cursor, Scale Cage and To Sphere added
- v1.0.6 – 2024-11-01
  - Adapted for Blender 4.3, with the new Brush Asset Shelf
  - New feature: Assign a custom brush in the Asset Shelf to a tool in the GP Tool Wheel
- v1.0.5 – 2024-05-23
  - Now uses UI scale: bigger wheel when UI scale is higher
  - Support for Grease Pencil v3
  - Save and load preferences to a custom file path
  - Made ready as extension for extensions.blender.org
- v1.0.4 – 2023-05-26
  - Support for Blender 4.0
  - Support for gradient weight paint tool (yet to come in Blender)
- v1.0.3 – 2023-04-07
  - Support for new weight paint tools (Blur, Average, Smear)
  - Fix: brush size error when opening tool wheel in older GP files
- v1.0.2 – 2023-02-07
  - Default keyboard shortcut changed to F8
- v1.0.1 – 2023-01-02
  - Code cleanup
- v1.0.0 – 2022-11-16
  - Initial release
