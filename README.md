# Blender 2.8 Object Exporter
This plugin is designed to improve the export process from blender to any external software by automaticly baking standard PBR texture maps and other maps that are useful for texturing, configuring object materials and exporting meshes.
## How to install this plugin
To install this plugin download *PBR_Exporter.py*, install it from the blender's preferences, and enable it.
## How to use this plugin
Select the objects to export and the textures to export with them in the export panel. Then select the output directory. (*note: the objects will be exported into a subdirectory of the output path named after the blend file*) Then press *Export Objects*. Blender will momentarily freeze while it is baking textures. Progress is logged to the console window while it is baking. Blender will then configure object materials to use the textures and export all of the objects to a single *.fbx* or into individual *.fbx*'s if 'Seperate Objects' is enabled. For fastest baking switch to GPU rendering. This plugin uses blender's cycles for baking textures so cycles quality setting will affect the baking speeds and quality for some maps (*AO, Combined, etc.*).



### Export Options
- *Textures To Export:* The texture maps to export for each object. (*Combined will take a very long time*)
	- *Albedo:* Bake and export albedo maps. (*This only work with Principled BSDF materials. On other materials this will be a diffuse map*) 
	- *Normal:* Bake and export normal maps.
	- *Metalness:* Bake and export metalness maps. (*This only work with Principled BSDF materials. On other materials this will be a gloss map*) 
	- *Roughness:* Bake and export roughness maps.
	- *Emission:* Bake and export emission maps.
	- *AO:* Bake and export AO maps.
	- *Curvature:* Bake a curvature map.
	- *Material ID:* Bake a map with a different color for each material.
	- *Combined:* Bake and export combined maps. (*Settings can be changed from cycles baking options*)
- *Texture Resolution:* The size of the texture maps (1024 -> 1024 * 1024).
- *Composite Maps:* Options to create maps that have Metalic, Roughness, AO, and Concavity channels  Currently each channel can be *Empty* or a *Curvature*, *AO*, *Metalness*, or *Roughness*
- *Separate Objects:* Exports each of the selected objects to it's own file and subdirectory
- *Generate UV Maps:* Generates a UV map for each selected object.
