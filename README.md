# Blender 2.8 Object Exporter
This plugin is designed to improve the export process from blender to external software by baking PBR texture maps, configuring object materials and exporting meshes so that they can be used in almost any external software.
## How to install
To install this plugin download *PBR_Exporter.py*, install it from the blender's plugin preferences, and enable it.
## How to use
Select the objects to export and the textures to export with them in the export panel. Then select the output directory. (*note: the objects will be exported into a subdirectory of the output path named after the blend file*) Then press *Export Objects*. Blender will freeze while it is baking textures. (*bake progress is logged to the console.*) Blender will then configure materials and export all of the objects to a .fbx. (*Or into individual .fbx's if Seperate Objects is enabled.*)
*GPU baking will sometimes sometimes cause baking errors. Switching to CPU rendering will fix this problem.*

### Options
- *Textures To Export:* The texture maps to export for each object. (*Combined will take a very long time*)
	- *Albedo:* Bake and export albedo maps. (*This only work with Principled BSDF materials. On other materials this will be a diffuse map*) 
	- *Normal:* Bake and export normal maps.
	- *Metalness:* Bake and export metalness maps. (*This only work with Principled BSDF materials. On other materials this will be a gloss map*) 
	- *Roughness:* Bake and export roughness maps.
	- *Emission:* Bake and export emission maps.
	- *Combined:* Bake and export combined maps. (*Settings can be changed from cycles baking options*)
- *Texture Resolution:* The size of the texture maps (1024 -> 1024 * 1024).
- *Separate Objects:* Exports each of the selected objects to it's own file and subdirectory
- *Only Bake Materials:* Only bakes and exports materials. *If a material ralies on any mesh data this should be disabled.*