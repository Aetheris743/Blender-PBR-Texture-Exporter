bl_info = {
    "name": "PBR Exporter",
    "category": "Export",
    "blender": (2, 90, 0),
    "author" : "Aetheris",
    "version" : (2, 1, 0),
    "description" :
            "Bake and Export Textures and Meshes",
}


import bpy
import os
import shutil
import sys
import random
import numpy
import pathlib

## TODO
## Testing of new path system
## TODO LATER
## Update to remove try/catch statements and just check first
## Add comments to functions
## Add test-files to quickly test the plugin functionality
## Add material-only export

class BakeObjects(bpy.types.Operator):
    """Bake and export selected scene objects"""
    bl_idname = "bake.bakeobjects"
    bl_label = "Bake Textures"

    def execute(self, context):
        
        bpy.ops.wm.save_mainfile(filepath=bpy.data.filepath)       

        context.scene.render.engine = "CYCLES"
        
        bar_size = 20
        
        view_layer = bpy.context.view_layer

        obj_active = view_layer.objects.active
        selection = bpy.context.selected_objects
        
        options = bpy.context.window_manager.all_export_settings
        
        objnumber = len(selection)
        
        texture_number = 0

        blender_file_name = pathlib.Path(bpy.data.filepath).stem
        
        if options.use_normal == True:
            texture_number += 1
        if options.use_rough == True:
            texture_number += 1
        if options.use_emit == True:
            texture_number += 1
        if options.use_combined == True:
            texture_number += 1
        if options.use_metal == True:
            texture_number += 1
        if options.use_albedo == True:
            texture_number += 1
        if options.use_ao == True:
            texture_number += 1
        if options.use_curvature == True:
            texture_number += 1
            
        if texture_number > 0:     
               
            bake_number = texture_number*objnumber
            texture_percent = bar_size / bake_number
            one_percent = 100 / bake_number
            first = int(one_percent)
            one_percent = 0
            bake_progress = 0
            
            data = (bar_size, view_layer, obj_active, selection, options, objnumber, texture_number, bake_number, texture_percent, one_percent, first, one_percent, bake_progress)
            
            if (options.generate_uvs == True):
                for obj in selection:
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(True)
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.uv.smart_project()
                    bpy.ops.object.editmode_toggle() 
            
            print("Starting Texture Baking:")    
            if (options.bake_materials == True):  
                
                 #bpy.ops.mesh.primitive_plane_add(size=2)
                 bpy.context.active_object.name = "MATERIAL_BAKE_TARGET"
                 object = bpy.context.active_object
                 for material in bpy.data.materials:
                     object.name = material.name
                     try:
                        object.material_slots[0].material = material
                        data = BakeObjectMaterials(object, options, data)
                     except:
                        object.data.materials.append(material)
                        object.material_slots[0].material = material
                        data = BakeObjectMaterials(object, options, data)
            if (options.bake_materials == False):    
                for obj in selection:
                    
                    if obj.type == "MESH":
                            
                        data = BakeObjectMaterials(obj, options, data)
                        
            print("Baking Done                                                                                       ")
                    
        for obj in selection:   

            if obj.type == "MESH":
                  
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                if (options.bake_materials == False and texture_number != 0):
                    SetupMaterialExport(obj)
                    
                if options.seperate_objects == True:
                    try:
                        path = pathlib.Path(bpy.context.scene.render.filepath)
                        path = path / blender_file_name / obj.name / obj.name
                        path = path.with_suffix(".fbx" )
                        bpy.ops.export_scene.fbx(filepath=path, use_selection=True)

                    except:    
                        path = pathlib.Path(bpy.context.scene.render.filepath) / blender_file_name / obj.name
                        try:
                            os.mkdir(bpy.context.scene.render.filepath + blender_file_name)   
                        except:
                            pass
                        
                        try:
                            bpy.ops.export_scene.fbx(filepath=path / (obj.name + ".fbx"), use_selection=True)
                            
                        except:    
                            os.mkdir(path)
                            bpy.ops.export_scene.fbx(filepath=path / (obj.name + ".fbx"), use_selection=True)
                            
                
        if options.use_material_id == True:
            colors = []
            for material in bpy.data.materials:
                if material.node_tree != None:
                    color_node = material.node_tree.nodes.new("ShaderNodeEmission")
                    color = (random.randint(0,255)/255, random.randint(0,255)/255, random.randint(0,255)/255, 1)
                    while color in colors:
                        print("run")
                        color = (random.randint(0,255)/255, random.randint(0,255)/255, random.randint(0,255)/255, 1)
                    colors.append(color)
                    color_node.inputs[0].default_value = color
                    output = material.node_tree.nodes["Material Output"]
                    
                    links = material.node_tree.links
                    links.new(output.inputs[0], color_node.outputs[0]) 
            
            for obj in selection:
                print("Baking Material ID on", obj.name)
                ConfigureMaterials(obj, "ID")
                sys.stdout = open(os.devnull, "w")
                bpy.ops.object.bake(type="EMIT")
            
                SaveImage(obj, "ID")
                sys.stdout = sys.__stdout__
                
                try:
                    ReconfigureMaterials(obj)
                except:
                    print("Failed to reconfigure materials on", obj.name)
                
        if options.seperate_objects == False:
            path = pathlib.Path(bpy.context.scene.render.filepath) / blender_file_name / blender_file_name
            print(path)
            SelectObjects(selection)
            
            try:
                bpy.ops.export_scene.fbx(filepath=path+".fbx", use_selection=True)
            
            except:
                os.mkdir(bpy.context.scene.render.filepath + blender_file_name)
                
                bpy.ops.export_scene.fbx(filepath=path+".fbx", use_selection=True)
        if bpy.context.window_manager.all_export_settings.number_of_maps > 0:
            for obj in selection:
                if bpy.context.window_manager.compound_map_0.active == True:
                    maps = GetMaps(bpy.context.window_manager.compound_map_0)
                    CombineTextures(obj, maps[0], maps[1], maps[2], maps[3], bpy.context.window_manager.compound_map_0.name)
                if bpy.context.window_manager.compound_map_1.active == True:
                    maps = GetMaps(bpy.context.window_manager.compound_map_1)
                    CombineTextures(obj, maps[0], maps[1], maps[2], maps[3], bpy.context.window_manager.compound_map_1.name)
                if bpy.context.window_manager.compound_map_2.active == True:
                    maps = GetMaps(bpy.context.window_manager.compound_map_2)
                    CombineTextures(obj, maps[0], maps[1], maps[2], maps[3], bpy.context.window_manager.compound_map_2.name)
                if bpy.context.window_manager.compound_map_3.active == True:
                    maps = GetMaps(bpy.context.window_manager.compound_map_3)
                    CombineTextures(obj, maps[0], maps[1], maps[2], maps[3], bpy.context.window_manager.compound_map_3.name)
                if bpy.context.window_manager.compound_map_4.active == True:
                    maps = GetMaps(bpy.context.window_manager.compound_map_4)
                    CombineTextures(obj, maps[0], maps[1], maps[2], maps[3], bpy.context.window_manager.compound_map_4.name)
                if bpy.context.window_manager.compound_map_5.active == True:
                    maps = GetMaps(bpy.context.window_manager.compound_map_5)
                    CombineTextures(obj, maps[0], maps[1], maps[2], maps[3], bpy.context.window_manager.compound_map_5.name)
                if bpy.context.window_manager.compound_map_6.active == True:
                    maps = GetMaps(bpy.context.window_manager.compound_map_6)
                    CombineTextures(obj, maps[0], maps[1], maps[2], maps[3], bpy.context.window_manager.compound_map_6.name)
                if bpy.context.window_manager.compound_map_7.active == True:
                    maps = GetMaps(bpy.context.window_manager.compound_map_7)
                    CombineTextures(obj, maps[0], maps[1], maps[2], maps[3], bpy.context.window_manager.compound_map_7.name)
                
        bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)
                
        return {'FINISHED'} 
def GetMaps(ref):
    maps = []
    maps += GetTextures(ref.red_channel)
    maps += GetTextures(ref.green_channel)
    maps += GetTextures(ref.blue_channel)
    maps += GetTextures(ref.alpha_channel)
    return maps
def GetTextures(channel):
    maps = []
    if channel == "use_nothing":
        maps.append("null")
    elif channel == "use_rough":
        maps.append("Roughness")
    elif channel == "use_metal":
        maps.append("Metalness")
    elif channel == "use_curvature":
        maps.append("Curvature")
    elif channel == "use_ao":
        maps.append("AO")
    return maps
    
def CombineTextures(obj, tex1, tex2, tex3, tex4, name):
    bpy.context.scene.use_nodes = True
    
    tree = bpy.context.scene.node_tree
    for node in tree.nodes:
        tree.nodes.remove(node)
    
    combiner = tree.nodes.new("CompositorNodeCombRGBA") 
    
    try:  
        first_image = tree.nodes.new("CompositorNodeImage")
        first_image.image = bpy.data.images[obj.name+"_"+tex1]
    except:
        first_image = tree.nodes.new("CompositorNodeValue")
        first_image.outputs[0].default_value = 0
        
    try:  
        second_image = tree.nodes.new("CompositorNodeImage")
        second_image.image = bpy.data.images[obj.name+"_"+tex2]
    except:
        second_image = tree.nodes.new("CompositorNodeValue")
        second_image.outputs[0].default_value = 0
        
    try:  
        third_image = tree.nodes.new("CompositorNodeImage")
        third_image.image = bpy.data.images[obj.name+"_"+tex3]
    except:
        third_image = tree.nodes.new("CompositorNodeValue")
        third_image.outputs[0].default_value = 0
        
    try:  
        fourth_image = tree.nodes.new("CompositorNodeImage")
        fourth_image.image = bpy.data.images[obj.name+"_"+tex4]
    except:
        fourth_image = tree.nodes.new("CompositorNodeValue")
        fourth_image.outputs[0].default_value = 1
       
    final = tree.nodes.new("CompositorNodeComposite")   
        
    tree.links.new(combiner.outputs[0], final.inputs[0])
    tree.links.new(first_image.outputs[0], combiner.inputs[0])
    tree.links.new(second_image.outputs[0], combiner.inputs[1])
    tree.links.new(third_image.outputs[0], combiner.inputs[2])
    tree.links.new(fourth_image.outputs[0], combiner.inputs[3])
    
    tmp_path = bpy.context.scene.render.filepath
    
    bpy.context.scene.render.resolution_x = int(bpy.context.window_manager.all_export_settings.texture_resoulution)
    bpy.context.scene.render.resolution_y = int(bpy.context.window_manager.all_export_settings.texture_resoulution)
    bpy.context.scene.render.resolution_percentage = 100
    
    export_path = pathlib.Path(bpy.context.scene.render.filepath) / pathlib.Path(bpy.data.filepath).stem
    if bpy.context.window_manager.all_export_settings.seperate_objects == True:
        path /= obj.name
    bpy.context.scene.render.filepath = path / (obj.name+"_"+name)
    bpy.ops.render.render(write_still=True)
    bpy.context.scene.render.filepath = tmp_path
    
def BakeObjectMaterials(obj, options, data):
    bar_size, view_layer, obj_active, selection, options, objnumber, texture_number, bake_number, texture_percent, one_percent, first, one_percent, bake_progress = data
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)

    if options.use_normal == True:
        print("Baking Normal on", obj.name, "", "#"*int(bake_progress), "-"*int(bar_size-bake_progress), str(one_percent)+"% Done", "               ", end="\r")
        sys.stdout = open(os.devnull, "w")

        ConfigureMaterials(obj, "Normal")
        bpy.ops.object.bake(type="NORMAL")
    
        SaveImage(obj, "Normal")
        sys.stdout = sys.__stdout__
        
        bake_progress += texture_percent
        one_percent += first
        
            
    if options.use_rough == True:
        print("Baking Roughness on", obj.name, "", "#"*int(bake_progress), "-"*int(bar_size-bake_progress), str(one_percent)+"% Done", "               ", end="\r")
        sys.stdout = open(os.devnull, "w")
        ConfigureMaterials(obj, "Roughness")
        bpy.ops.object.bake(type="ROUGHNESS")
    
        SaveImage(obj, "Roughness")
        sys.stdout = sys.__stdout__
        bake_progress += texture_percent
        one_percent += first
        
                
    if options.use_emit == True:
        print("Baking Emission on", obj.name, "", "#"*int(bake_progress), "-"*int(bar_size-bake_progress), str(one_percent)+"% Done", "               ", end="\r")
        ConfigureMaterials(obj, "Emission")
        sys.stdout = open(os.devnull, "w")
        bpy.ops.object.bake(type="EMIT")
    
        SaveImage(obj, "Emission")
        sys.stdout = sys.__stdout__
        bake_progress += texture_percent
        one_percent += first
    if options.use_combined == True:
        bpy.context.scene.render.bake.use_pass_direct = True
        bpy.context.scene.render.bake.use_pass_indirect = True
        
        
        print("Baking Combined on", obj.name, "", "#"*int(bake_progress), "-"*int(bar_size-bake_progress), str(one_percent)+"% Done", "               ", end="\r")
        sys.stdout = open(os.devnull, "w")
        ConfigureMaterials(obj, "Combined")
        bpy.ops.object.bake(type="COMBINED")
    
        SaveImage(obj, "Combined")
        
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        sys.stdout = sys.__stdout__
        bake_progress += texture_percent
        one_percent += first
    if options.use_metal == True:
        print("Baking Metalic on", obj.name, "", "#"*int(bake_progress), "-"*int(bar_size-bake_progress), str(one_percent)+"% Done", "               ", end="\r")
        sys.stdout = open(os.devnull, "w")
        if SetToEmissive(obj, principled_input="Metallic"):
            ConfigureMaterials(obj, "Metalness")
            bpy.ops.object.bake(type="EMIT")
        
            SaveImage(obj, "Metalness")
        else:
            ConfigureMaterials(obj, "Metalness")
            bpy.ops.object.bake(type="GLOSSY")
        
            SaveImage(obj, "Metalness")
        sys.stdout = sys.__stdout__
        bake_progress += texture_percent
        one_percent += first
            
    if options.use_albedo == True:
        print("Baking Albedo on", obj.name, "", "#"*int(bake_progress), "-"*int(bar_size-bake_progress), str(one_percent)+"% Done", "               ", end="\r")
        sys.stdout = open(os.devnull, "w")
        if SetToEmissive(obj):
            ConfigureMaterials(obj, "Albedo")
            bpy.ops.object.bake(type="EMIT")
        
            SaveImage(obj, "Albedo")
        else:
            ConfigureMaterials(obj, "Albedo")
            bpy.ops.object.bake(type="DIFFUSE")
        
            SaveImage(obj, "Albedo")
        sys.stdout = sys.__stdout__
        bake_progress += texture_percent
        one_percent += first
    if options.use_ao == True:
        print("Baking AO on", obj.name, "", "#"*int(bake_progress), "-"*int(bar_size-bake_progress), str(one_percent)+"% Done", "               ", end="\r")
        sys.stdout = open(os.devnull, "w")
        ConfigureMaterials(obj, "AO")
        for mat in obj.material_slots:
            ao = mat.material.node_tree.nodes.new("ShaderNodeAmbientOcclusion")
            emission = mat.material.node_tree.nodes.new("ShaderNodeEmission")
            output = mat.material.node_tree.nodes["Material Output"]
            
            links = mat.material.node_tree.links
            links.new(output.inputs[0], emission.outputs[0])
            links.new(emission.inputs[0], ao.outputs[0])
                    
        bpy.ops.object.bake(type="EMIT")
                    
        SaveImage(obj, "AO")
        
        sys.stdout = sys.__stdout__
        bake_progress += texture_percent
        one_percent += first 
            
    if options.use_curvature == True:
        print("run")
        print("Baking Curvature on", obj.name, "", "#"*int(bake_progress), "-"*int(bar_size-bake_progress), str(one_percent)+"% Done", "               ", end="\r")
        sys.stdout = open(os.devnull, "w")
        ConfigureMaterials(obj, "Curvature")
        for mat in obj.material_slots:
            geometry = mat.material.node_tree.nodes.new("ShaderNodeNewGeometry")
            
            color_ramp = mat.material.node_tree.nodes.new("ShaderNodeValToRGB")
            color_ramp.color_ramp.elements[0].position = (0.471)
            color_ramp.color_ramp.elements[0].color = (0,0,0,1)
            color_ramp.color_ramp.elements[1].position = (0.514) 
            color_ramp.color_ramp.elements[1].color = (1,1,1,1)
                    
            emission = mat.material.node_tree.nodes.new("ShaderNodeEmission")
            output = mat.material.node_tree.nodes["Material Output"]
            
            links = mat.material.node_tree.links
            links.new(output.inputs[0], emission.outputs[0])
            links.new(color_ramp.inputs[0], geometry.outputs[7])
            links.new(emission.inputs[0], color_ramp.outputs[0])
                    
        bpy.ops.object.bake(type="EMIT")
                    
        SaveImage(obj, "Curvature")
        
        sys.stdout = sys.__stdout__
        bake_progress += texture_percent
        one_percent += first
    try:
        ReconfigureMaterials(obj)
    except:
        print("Failed to reconfigure materials on", obj.name)
        
    data = (bar_size, view_layer, obj_active, selection, options, objnumber, texture_number, bake_number, texture_percent, one_percent, first, one_percent, bake_progress)
    return data
   
def ReconfigureMaterials(obj):
    for mat in obj.material_slots:
        output = mat.material.node_tree.nodes["Material Output"]        
        principled = mat.material.node_tree.nodes["Principled BSDF"]
        
        mat.material.node_tree.links.new(output.inputs[0], principled.outputs[0])

def SetToEmissive(obj, principled_input="Base Color"):   
    try: 
        for mat in obj.material_slots:
            emission = mat.material.node_tree.nodes.new("ShaderNodeEmission")
            output = mat.material.node_tree.nodes["Material Output"]
            
            principled = mat.material.node_tree.nodes["Principled BSDF"]
               
            test = False     
            for link in mat.material.node_tree.links:
                if link.to_socket == principled.inputs[principled_input]:
                    node = link.from_socket
                    test=True
            if test == False:
                input = principled.inputs[principled_input]
                type = input.type
                if type == "VALUE":
                    emission.inputs[0].default_value = (input.default_value, input.default_value, input.default_value, 1)
                if type == "RGBA":
                    emission.inputs[0].default_value = input.default_value
            
            mat.material.node_tree.links.new(output.inputs[0], emission.outputs[0])
            if test == True:
                mat.material.node_tree.links.new(emission.inputs[0], node)
        return True
    except:
        print("Node Transfer Error Occured: using fallback bake type")
        return False

def SelectObjects(objs):
    for obj in objs:
        obj.select_set(True)

def SaveImage(obj, texture_type):
    image = bpy.data.images[obj.name+"_"+texture_type]
    try:
        image.save()
    except:
        base_path = pathlib.Path(bpy.context.scene.render.filepath) / pathlib.Path(bpy.data.filepath).stem
        try:
            if bpy.context.window_manager.all_export_settings.seperate_objects == True:
                os.mkdir(base_path / obj.name)
            else:
                os.mkdir(base_path)
        except:
            os.mkdir(base_path)
            os.mkdir(base_path / obj.name)
        image.save()

def SetupMaterialExport(obj):
    
    options = bpy.context.window_manager.all_export_settings
    
    for mat in obj.material_slots:
        
        bpy.data.materials.new(name=obj.name+"_"+mat.material.name)
        
        material = bpy.data.materials[obj.name+"_"+mat.material.name]
        material.use_nodes = True
        
        mat.material = material
        
        nodetree = material.node_tree
        
        principled = nodetree.nodes.new("ShaderNodeBsdfPrincipled")
        
        output = nodetree.nodes['Material Output'].inputs[0]
        
        nodetree.links.new(output, principled.outputs[0])
        
        try:
            if options.use_albedo == True:
                diffuse = nodetree.nodes.new("ShaderNodeTexImage")
                diffuse.image = bpy.data.images[obj.name+"_Albedo"]
                
                nodetree.links.new(principled.inputs["Base Color"], diffuse.outputs[0])
                    
            if options.use_normal == True:
                normal = nodetree.nodes.new("ShaderNodeTexImage")
                normal.image = bpy.data.images[obj.name+"_Normal"]
                normal.image.colorspace_settings.name = 'Non-Color'
                
                map = nodetree.nodes.new("ShaderNodeNormalMap")
                
                nodetree.links.new(map.inputs["Color"], normal.outputs[0])            
                
                nodetree.links.new(principled.inputs["Normal"], map.outputs[0])
                        
            if options.use_metal == True:
                gloss = nodetree.nodes.new("ShaderNodeTexImage")
                gloss.image = bpy.data.images[obj.name+"_Metalness"]
                gloss.image.colorspace_settings.name = 'Non-Color'
                
                nodetree.links.new(principled.inputs["Metallic"], gloss.outputs[0])
                        
            if options.use_rough == True:
                rough = nodetree.nodes.new("ShaderNodeTexImage")
                rough.image = bpy.data.images[obj.name+"_Roughness"]
                rough.image.colorspace_settings.name = 'Non-Color'
                
                nodetree.links.new(principled.inputs["Roughness"], rough.outputs[0])
                
        except:
            print("Failed to convert colorspaces")


def ConfigureMaterials(obj, texture_type):

    resoulution = int(bpy.context.window_manager.all_export_settings.texture_resoulution)

    bpy.ops.image.new(name=obj.name+"_"+texture_type, width=resoulution, height=resoulution)

    image = bpy.data.images[obj.name+"_"+texture_type]

    image_path = pathlib.Path(bpy.context.scene.render.filepath) / pathlib.Path(bpy.data.filepath).stem
    if bpy.context.window_manager.all_export_settings.seperate_objects == True:
        image_path /= obj.name
    
    image.filepath = image_path / (obj.name+"_"+texture_type+".png")
    image.file_format = 'PNG'
    
    for mat in obj.material_slots:
        node = mat.material.node_tree.nodes.new("ShaderNodeTexImage")
        node.image = bpy.data.images[obj.name+"_"+texture_type]
        node.select = True
        mat.material.node_tree.nodes.active = node

    
  
class ExportPanel(bpy.types.Panel):
    """Export Menu"""
    bl_label = "Export Panel"
    bl_idname = "RENDER_PT_Exportpanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    
    def draw_map_panel(self, layout, mask_ref):
        box = layout.box()
        row = box.row()
        row.prop(mask_ref, "active", icon="TRIA_DOWN" if mask_ref.active else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text=mask_ref.name)
        maps = []
        if mask_ref.active:
            row = box.row()
            row.prop(mask_ref, "name")
            row = box.row()
            row.label(text="Channel Maps")
            
            row = box.row()
            row.prop(mask_ref, "red_channel")
            if mask_ref.red_channel != "use_nothing":
                maps.append(mask_ref.red_channel)
            row = box.row()
            row.prop(mask_ref, "green_channel")
            if mask_ref.green_channel != "use_nothing":
                maps.append(mask_ref.green_channel)
            row = box.row()
            row.prop(mask_ref, "blue_channel")
            if mask_ref.blue_channel != "use_nothing":
                maps.append(mask_ref.blue_channel)
            row = box.row()
            row.prop(mask_ref, "alpha_channel")
            if mask_ref.alpha_channel != "use_nothing":
                maps.append(mask_ref.alpha_channel)
        return maps
            
    def draw(self, context):
        layout = self.layout
        
        options = context.window_manager
        
        
        
        row = layout.row()
        row.label(text= "Textures to Export")

        row = layout.row(align=True)
        row.prop(options.all_export_settings, "use_albedo")
        row.prop(options.all_export_settings, "use_normal")

        row = layout.row(align=True)
        row.prop(options.all_export_settings, "use_metal")
        row.prop(options.all_export_settings, "use_rough")

        row = layout.row(align=True)
        row.prop(options.all_export_settings, "use_emit")
        row.prop(options.all_export_settings, "use_ao")
        
        row = layout.row(align=True)
        #row.enabled = not options.all_export_settings.bake_materials
        #if (options.all_export_settings.bake_materials):
        #    options.all_export_settings.use_combined = False
        #    options.all_export_settings.use_curvature = False
        #    options.all_export_settings.use_colorid = False
        row.prop(options.all_export_settings, "use_material_id")
        row.prop(options.all_export_settings, "use_curvature")
        
        row = layout.row()
        row = layout.row()
        row.enabled = not options.all_export_settings.bake_materials
        row.prop(options.all_export_settings, "use_combined")
        
        #if options.all_export_settings.use_colorid:  //to be added in later version
        #    row = layout.row()
        #    row.label(text="Export .FBX with combined materials")
        #    row.prop(options.all_export_settings, "combine_materials")
                
        row = layout.row()
        row.label(text= "Map Texture Resoulution")
        row = layout.row()
        row.prop(options.all_export_settings, "texture_resoulution", expand=True)
        
        row = layout.row()
        row.label(text="Composite Maps")
        maps_used = []
        if options.all_export_settings.number_of_maps > 0:
            maps_used += self.draw_map_panel(layout, options.compound_map_0)
        if options.all_export_settings.number_of_maps > 1:
            maps_used += self.draw_map_panel(layout, options.compound_map_1)
        if options.all_export_settings.number_of_maps > 2:
            maps_used += self.draw_map_panel(layout, options.compound_map_2)
        if options.all_export_settings.number_of_maps > 3:
            maps_used += self.draw_map_panel(layout, options.compound_map_3)
        if options.all_export_settings.number_of_maps > 4:
            maps_used += self.draw_map_panel(layout, options.compound_map_4)
        if options.all_export_settings.number_of_maps > 5:
            maps_used += self.draw_map_panel(layout, options.compound_map_5)
        if options.all_export_settings.number_of_maps > 6:
            maps_used += self.draw_map_panel(layout, options.compound_map_6)
        if options.all_export_settings.number_of_maps > 7:
            maps_used += self.draw_map_panel(layout, options.compound_map_7)
        maps_used = list(dict.fromkeys(maps_used))
        
        for map in maps_used:
            exec("options.all_export_settings."+map+" = True")
        
        row = layout.row()
        if options.all_export_settings.number_of_maps < 7:
            row.operator("bake.add_compound_map", text="Add Composite Map")
        if options.all_export_settings.number_of_maps > 0:
            row.operator("bake.remove_compound_map", text="Remove Composite Map")

        row = layout.row()
        
        row = layout.row()
        row.prop(options.all_export_settings, "seperate_objects")
        
        #row = layout.row() //to be added later
        #row.prop(options.all_export_settings, "bake_materials")        
        
        row = layout.row()
        row.prop(options.all_export_settings, "generate_uvs")
        
        row = layout.row()
        
        row = layout.row()
        row.prop(bpy.context.scene.render, "filepath")

        row = layout.row()
        row.operator("bake.bakeobjects", text='Export Maps')


class ExportableMap(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="New Map")
    active: bpy.props.BoolProperty(name="Active", default=False)
    red_channel: bpy.props.EnumProperty(
        name = "Red",
        description = "Choose Texture",
        items = [
            ("use_nothing", "Empty", "Leave this Texture Channel Empty"),
            ("use_rough", "Roughness", "Use Roughness for this Texture Channel"),
            ("use_metal", "Metalness", "Use Metalness for this Texture Channel"),
            ("use_ao", "AO", "Use Ambient Occlusion for this Texture Channel"),
            ("use_curvature", "Curvature", "Use Curvature for this Texture Channel"),
        ],
        default = 'use_nothing'
    ) 
    green_channel: bpy.props.EnumProperty(
        name = "Green",
        description = "Choose Texture",
        items = [
            ("use_nothing", "Empty", "Leave this Texture Channel Empty"),
            ("use_rough", "Roughness", "Use Roughness for this Texture Channel"),
            ("use_metal", "Metalness", "Use Metalness for this Texture Channel"),
            ("use_ao", "AO", "Use Ambient Occlusion for this Texture Channel"),
            ("use_curvature", "Curvature", "Use Curvature for this Texture Channel"),
        ],
        default = 'use_nothing'
    ) 
    blue_channel: bpy.props.EnumProperty(
        name = "Blue",
        description = "Choose Texture",
        items = [
            ("use_nothing", "Empty", "Leave this Texture Channel Empty"),
            ("use_rough", "Roughness", "Use Roughness for this Texture Channel"),
            ("use_metal", "Metalness", "Use Metalness for this Texture Channel"),
            ("use_ao", "AO", "Use Ambient Occlusion for this Texture Channel"),
            ("use_curvature", "Curvature", "Use Curvature for this Texture Channel"),
        ],
        default = 'use_nothing'
    ) 
    alpha_channel: bpy.props.EnumProperty(
        name = "Alpha",
        description = "Choose Texture",
        items = [
            ("use_nothing", "Fulll", "Create this Channel at full Values"),
            ("use_rough", "Roughness", "Use Roughness for this Texture Channel"),
            ("use_metal", "Metalness", "Use Metalness for this Texture Channel"),
            ("use_ao", "AO", "Use Ambient Occlusion for this Texture Channel"),
            ("use_curvature", "Curvature", "Use Curvature for this Texture Channel"),
        ],
        default = 'use_nothing'
    ) 

class AddCompoundMap(bpy.types.Operator):
    """Internal"""
    bl_idname = "bake.add_compound_map"
    bl_label = "Add Compund Map"

    def execute(self, context):
        context.window_manager.all_export_settings.number_of_maps += 1
        return {'FINISHED'}
    
class RemoveCompoundMap(bpy.types.Operator):
    """Internal"""
    bl_idname = "bake.remove_compound_map"
    bl_label = "Remove Compund Map"

    def execute(self, context):
        context.window_manager.all_export_settings.number_of_maps -= 1
        return {'FINISHED'}
  
class BakeObjectsSettings(bpy.types.PropertyGroup):    
    use_albedo: bpy.props.BoolProperty(name="Albedo", default=False)    
    use_normal: bpy.props.BoolProperty(name="Normal", default=False)    
    use_metal: bpy.props.BoolProperty(name="Metalness", default=False)    
    use_rough: bpy.props.BoolProperty(name="Roughness", default=False)    
    use_emit: bpy.props.BoolProperty(name="Emission", default=False)    
    use_ao: bpy.props.BoolProperty(name="AO", default=False)
    use_combined: bpy.props.BoolProperty(name="Combined", default=False)
    use_curvature: bpy.props.BoolProperty(name="Curvature", default=False)
    
    use_material_id: bpy.props.BoolProperty(name="Material ID", default=False)
        
    combine_materials: bpy.props.BoolProperty(name="", default=False)
    
    number_of_maps: bpy.props.IntProperty(name="Number of Maps", default=0, min=0, max=7)
    
    generate_uvs: bpy.props.BoolProperty(name="Generate UV Maps", default=False)

    seperate_objects: bpy.props.BoolProperty(name="Separate Objects", default=False)
    bake_materials: bpy.props.BoolProperty(name="Only Bake Materials", default=False)
    
    texture_resoulution: bpy.props.EnumProperty(
        name = "Resoulution",
        description = "Choose Texture Resolution",
        items = [
            ("1024", "1024", "Render a 1024 x 1024 texture"),
            ("2048", "2048", "Render a 2048 x 2048 texture"),
            ("4096", "4096", "Render a 4096 x 4096 texture"),
            ("8192", "8192", "Render a 8192 x 8192 texture"),
        ],
        default = '1024'
    )  

def register():
    bpy.utils.register_class(BakeObjectsSettings)
    bpy.utils.register_class(ExportableMap)
    
    bpy.types.WindowManager.compound_map_0 = bpy.props.PointerProperty(type=ExportableMap) 
    bpy.types.WindowManager.compound_map_1 = bpy.props.PointerProperty(type=ExportableMap)
    bpy.types.WindowManager.compound_map_2 = bpy.props.PointerProperty(type=ExportableMap)
    bpy.types.WindowManager.compound_map_3 = bpy.props.PointerProperty(type=ExportableMap)
    bpy.types.WindowManager.compound_map_4 = bpy.props.PointerProperty(type=ExportableMap)
    bpy.types.WindowManager.compound_map_5 = bpy.props.PointerProperty(type=ExportableMap)
    bpy.types.WindowManager.compound_map_6 = bpy.props.PointerProperty(type=ExportableMap)
    bpy.types.WindowManager.compound_map_7 = bpy.props.PointerProperty(type=ExportableMap) 
    
    bpy.types.WindowManager.all_export_settings = bpy.props.PointerProperty(type=BakeObjectsSettings)
    
    bpy.utils.register_class(AddCompoundMap)
    bpy.utils.register_class(RemoveCompoundMap)
    bpy.utils.register_class(ExportPanel)    
    bpy.utils.register_class(BakeObjects)
      
    


def unregister():
    bpy.utils.unregister_class(BakeObjectsSettings)
    bpy.utils.unregister_class(ExportableMap)
    bpy.utils.unregister_class(AddCompoundMap)
    bpy.utils.unregister_class(RemoveCompoundMap)
    bpy.utils.unregister_class(ExportPanel)
    bpy.utils.unregister_class(BakeObjects)


if __name__ == "__main__":
    register()
