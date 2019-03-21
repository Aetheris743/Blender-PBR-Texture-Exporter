bl_info = {
    "name": "PBR Exporter",
    "category": "Export",
    "blender": (2, 80, 0),
    "author" : "Aetheris",
    "version" : (1, 0, 2),
    "description" :
            "Export Blender Scenes",
}




import bpy
import os
import shutil

class BakeObjects(bpy.types.Operator):
    """Bake Textures for all scene objects"""
    bl_idname = "bake.bakeobjects"
    bl_label = "Bake Textures"

    def execute(self, context):
        
        bpy.ops.wm.save_mainfile(filepath=bpy.data.filepath)       

        context.scene.render.engine = "CYCLES"
        
        view_layer = bpy.context.view_layer

        obj_active = view_layer.objects.active
        selection = bpy.context.selected_objects
        
        options = bpy.context.window_manager.all_export_settings        
        
        if (options.use_lighting == False):
            bpy.context.scene.render.bake.use_pass_direct = False
            bpy.context.scene.render.bake.use_pass_indirect = False
        
        if (options.use_lighting == True):
            bpy.context.scene.render.bake.use_pass_direct = True
            bpy.context.scene.render.bake.use_pass_indirect = True
        
        for obj in selection:
            
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)            
                
            if (options.use_diffuse == True):
                
                ConfigureMaterials(obj, "Diffuse")
                print("starting diffuse bake: " + obj.name)
                bpy.ops.object.bake(type="DIFFUSE")
            
                SaveImage(obj, "Diffuse")
                
            if (options.use_normal == True):
                ConfigureMaterials(obj, "Normal")
                print("starting normal bake: " + obj.name)
                bpy.ops.object.bake(type="NORMAL")
            
                SaveImage(obj, "Normal")
                    
            if (options.use_gloss == True):
                ConfigureMaterials(obj, "Glossiness")
                print("starting gloss bake: " + obj.name)
                bpy.ops.object.bake(type="GLOSSY")
            
                SaveImage(obj, "Glossiness")
                    
            if (options.use_rough == True):
                ConfigureMaterials(obj, "Roughness")
                print("starting roughness bake: " + obj.name)
                bpy.ops.object.bake(type="ROUGHNESS")
            
                SaveImage(obj, "Roughness")
                
                        
            if (options.use_emit == True):
                ConfigureMaterials(obj, "Emission")
                print("starting emission bake: " + obj.name)
                bpy.ops.object.bake(type="EMIT")
            
                SaveImage(obj, "Emission")
                
                    
            if (options.use_combined == True):
                ConfigureMaterials(obj, "Combined")
                print("starting combined bake: " + obj.name)
                bpy.ops.object.bake(type="COMBINED")
            
                SaveImage(obj, "Combined")
              
                
            SetupMaterialExport(obj)
            
            if (options.seperate_objects == True):
                path = bpy.context.scene.render.filepath + bpy.data.filepath.split("\\")[-1].split(".")[0] + "\\" + obj.name+ "\\" + obj.name
                
                bpy.ops.export_scene.fbx(filepath=path+".fbx", use_selection=True)
            
        if (options.seperate_objects == False):
            path = bpy.context.scene.render.filepath + bpy.data.filepath.split("\\")[-1].split(".")[0]+ "\\" + bpy.data.filepath.split("\\")[-1].split(".")[0]
            print(path)
            SelectObjects(selection)
            bpy.ops.export_scene.fbx(filepath=path+".fbx", use_selection=True)
            
        bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)
                
        return {'FINISHED'} 

def SelectObjects(objs):
    for obj in objs:
        obj.select_set(True)

def SaveImage(obj, texture_type):
    image = bpy.data.images[obj.name+"_"+texture_type]
    try:
        image.save()
    except:
        try:
            if (bpy.context.window_manager.all_export_settings.seperate_objects == True):
                os.mkdir(bpy.context.scene.render.filepath + bpy.data.filepath.split("\\")[-1].split(".")[0] + "\\" + obj.name)
            else:
                os.mkdir(bpy.context.scene.render.filepath + bpy.data.filepath.split("\\")[-1].split(".")[0])
        except:
            os.mkdir(bpy.context.scene.render.filepath + bpy.data.filepath.split("\\")[-1].split(".")[0])
            os.mkdir(bpy.context.scene.render.filepath + bpy.data.filepath.split("\\")[-1].split(".")[0] + "\\" + obj.name)
        image.save()

def SetupMaterialExport(obj):
    
    options = bpy.context.window_manager.all_export_settings
    
    for mat in obj.material_slots:
        nodetree = mat.material.node_tree
        
        principled = nodetree.nodes.new("ShaderNodeBsdfPrincipled")
        
        output = nodetree.nodes['Material Output'].inputs[0]
        
        nodetree.links.new(output, principled.outputs[0])
        
        if (options.use_diffuse == True):
            diffuse = nodetree.nodes.new("ShaderNodeTexImage")
            diffuse.image = bpy.data.images[obj.name+"_Diffuse"]
            
            nodetree.links.new(principled.inputs["Base Color"], diffuse.outputs[0])
                
        if (options.use_normal == True):
            normal = nodetree.nodes.new("ShaderNodeTexImage")
            normal.image = bpy.data.images[obj.name+"_Normal"]
            normal.color_space = "NONE"
            
            map = nodetree.nodes.new("ShaderNodeNormalMap")
            
            nodetree.links.new(map.inputs["Strength"], normal.outputs[0])            
            
            nodetree.links.new(principled.inputs["Normal"], map.outputs[0])
                    
        if (options.use_gloss == True):
            gloss = nodetree.nodes.new("ShaderNodeTexImage")
            gloss.image = bpy.data.images[obj.name+"_Glossiness"]
            normal.color_space = "NONE"
            
            nodetree.links.new(principled.inputs["Metallic"], gloss.outputs[0])
                    
        if (options.use_rough == True):
            rough = nodetree.nodes.new("ShaderNodeTexImage")
            rough.image = bpy.data.images[obj.name+"_Roughness"]
            rough.color_space = "NONE"
            
            nodetree.links.new(principled.inputs["Roughness"], rough.outputs[0])


def ConfigureMaterials(obj, texture_type):

    resoulution = int(bpy.context.window_manager.all_export_settings.texture_resoulution)

    bpy.ops.image.new(name=obj.name+"_"+texture_type, width=resoulution, height=resoulution)

    image = bpy.data.images[obj.name+"_"+texture_type]
    
    if (bpy.context.window_manager.all_export_settings.seperate_objects == True):
        subdir = bpy.data.filepath.split("\\")[-1].split(".")[0] + "\\" + obj.name
    else:
        subdir = bpy.data.filepath.split("\\")[-1].split(".")[0]
    
    image.filepath = bpy.context.scene.render.filepath + subdir + "\\" + obj.name+"_"+texture_type+".png"
    image.file_format = 'PNG'
    #get all materials on object
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

    def draw(self, context):
        layout = self.layout
        
        options = context.window_manager

        row = layout.row()
        row.label(text= "Select Textures to Export")

        row = layout.row(align=True)
        row.prop(options.all_export_settings, "use_diffuse")
        row.prop(options.all_export_settings, "use_normal")

        row = layout.row(align=True)
        row.prop(options.all_export_settings, "use_gloss")
        row.prop(options.all_export_settings, "use_rough")

        row = layout.row(align=True)
        row.prop(options.all_export_settings, "use_emit")
        row.prop(options.all_export_settings, "use_combined")

        row = layout.row()
        row.label(text= "Select the Texture Resoulution")

        row = layout.row()
        row.prop(options.all_export_settings, "texture_resoulution", expand=True)
        
        row = layout.row()
        
        row = layout.row()
        row.prop(options.all_export_settings, "seperate_objects")

        row = layout.row()
        row.prop(options.all_export_settings, "use_lighting")
        
        row = layout.row()
        row.label(text= "Export Selected Object")

        row = layout.row()
        row.operator("bake.bakeobjects", text='Export Objects')


class BakeObjectsSettings(bpy.types.PropertyGroup):    
    use_diffuse: bpy.props.BoolProperty(name="Diffuse", default=True)    
    use_normal: bpy.props.BoolProperty(name="Normal", default=True)    
    use_gloss: bpy.props.BoolProperty(name="Glossiness", default=True)    
    use_rough: bpy.props.BoolProperty(name="Roughness", default=True)    
    use_emit: bpy.props.BoolProperty(name="Emission", default=True)    
    use_combined: bpy.props.BoolProperty(name="Combined", default=False)

    seperate_objects: bpy.props.BoolProperty(name="Seperate Objects", default=False)

    use_lighting: bpy.props.BoolProperty(name="Use Lighting", default=False)
    
    texture_resoulution: bpy.props.EnumProperty(
        name = "Resoulution",
        description = "Choose Texture Resoulution",
        items = [
            ("1024", "1024", "Render a 1024 x 1024 texture"),
            ("2048", "2048", "Render a 2048 x 2048 texture"),
            ("4096", "4096", "Render a 4096 x 4096 texture"),
            ("8192", "8192", "Render a 8192 x 8192 texture"),
        ],
        default = '1024'
    )  

def register():
    bpy.utils.register_class(ExportPanel)    
    bpy.utils.register_class(BakeObjects)
    bpy.utils.register_class(BakeObjectsSettings)
        
    bpy.types.WindowManager.all_export_settings = bpy.props.PointerProperty(type=BakeObjectsSettings)


def unregister():
    bpy.utils.unregister_class(ExportPanel)
    bpy.utils.unregister_class(BakeObjects)
    bpy.utils.unregister_class(BakeObjectsSettings)


if __name__ == "__main__":
    register()