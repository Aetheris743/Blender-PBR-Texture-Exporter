# Blender 2.8 Object Exporter
This plugin is designed to improve the export process from blender to external software (Unity, Unreal, etc..). 
## How to install
To install this plugin download *PBR_Exporter.py*, install it from the blender's plugin preferences, and enable it.
## How to use
Select the objects to export and the textures to export with them in the export panel. Then select the output directory. (*note: the objects will be exported into a subdirectory of the output path named after the blend file*) Then press *Export Objects*. Blender will freeze up while it is baking textures. (*bake progress is logged to the console.*)
*GPU baking will sometimes sometimes cause baking errors. Switching to CPU rendering will fix this problem*

### Options
- *Textures To Export:* The texture maps to export for each object. (*Combined will take a very long time*)
- *Texture Resolution:* The size of the texture maps (1024 -> 1024 * 1024).
- *Separate Objects:* Exports each of the selected objects to it's own file and subdirectory
