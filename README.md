# Blender 2.8+ Object Exporter
This plugin is designed to improve the export process from blender to any external software by automaticly baking standard PBR texture maps, meshes, and other maps that are useful for texturing.

## How to install this plugin
To install this plugin download *PBR_Exporter.py*, install it from the *Add-ons* panel in blender's preferences, and enable it.

## How to use this plugin
First, Select the objects you want to export the textures of.

Select the options you want in the export panel. *(In render properties)*


<img width="197" alt="image" src="https://user-images.githubusercontent.com/45411688/175611326-212c3c53-a92c-491d-ad30-9b3ee6bb8d4a.png">

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


	<img width="193" alt="image" src="https://user-images.githubusercontent.com/45411688/175611965-2db996d7-9501-4ff7-854d-9be3ce659a4c.png">
- *Separate Objects:* Exports each of the selected objects to it's own file and subdirectory
- *Generate UV Maps:* Generates a UV map for each selected object.


### Exporting
Then, if you want to see the progress open the console *(Window > Toggle Console)*, and click the *Export Maps* button. This will take a while. Blender will momentarily freeze while it is baking textures.

After it finishes you will have an your objects export somthing like this
```
Blend-file Name
├───Object_1
│       Object_1.fbx
│       Object_1_Albedo.png
│       Object_1_AO.png
│       Object_1_Custom.png
│       Object_1_Emission.png
│		...
├───Object_2
│       Object_2.fbx
│       Object_2_Albedo.png
│       Object_2_AO.png
│       Object_2_Custom.png
│       Object_2_Emission.png
│	    ...
├─ etc...
```
or this depending on your settings.
```
Blend-file Name
	Object_1_Albedo.png
	Object_1_AO.png
	Object_1_Custom.png
	Object_1_Metalness.png
	Object_1_Normal.png
	Object_1_Roughness.png
	Object_2_Albedo.png
	Object_2_AO.png
	Object_2_Custom.png
	...
	Blend-file Name.fbx
```
