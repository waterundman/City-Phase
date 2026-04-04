import bpy
import math


def apply(context):
    scene = context.scene
    world = scene.world

    if not world:
        world = bpy.data.worlds.new("CityP_World")
        scene.world = world

    world.use_nodes = True
    tree = world.node_tree
    tree.nodes.clear()

    bg = tree.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.95, 0.92, 0.85, 1.0)
    bg.inputs["Strength"].default_value = 1.0
    bg.location = (-300, 0)

    output = tree.nodes.new("ShaderNodeOutputWorld")
    output.location = (200, 0)

    tree.links.new(bg.outputs["Background"], output.inputs["Surface"])

    scene.render.engine = "BLENDER_EEVEE_NEXT" if bpy.app.version >= (4, 2, 0) else "BLENDER_EEVEE"

    eevee = scene.eevee
    eevee.use_bloom = False
    eevee.use_gtao = False

    for light in list(bpy.data.lights):
        if light.name.startswith("CityP_"):
            bpy.data.lights.remove(light)

    sun_data = bpy.data.lights.new("CityP_IsoSun", "SUN")
    sun_data.energy = 5.0
    sun_data.angle = 0.0
    sun_data.color = (1.0, 0.98, 0.92)
    sun = bpy.data.objects.new("CityP_IsoSun", sun_data)
    sun.rotation_euler = (math.radians(35.264), 0, math.radians(45))
    context.collection.objects.link(sun)

    camera = context.scene.camera
    if camera:
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = 120
        camera.rotation_euler = (math.radians(35.264), 0, math.radians(45))
        camera.location = (50, 50, 50)

    scene.render.use_freestyle = True

    for lineset in scene.freestyle_settings.linesets:
        scene.freestyle_settings.linesets.remove(lineset)

    lineset = scene.freestyle_settings.linesets.new("CityP_Outline")
    lineset.select_silhouette = True
    lineset.select_border = False
    lineset.select_contour = True
    lineset.select_suggestive_contour = False
    lineset.select_ridge_valley = False
    lineset.select_crease = False
    lineset.select_edge_mark = False
    lineset.select_external_contour = False
    lineset.select_material_boundary = False

    for module in scene.freestyle_settings.modules:
        scene.freestyle_settings.modules.remove(module)

    parameter_editor = scene.freestyle_settings.modules.new("ParameterEditor")
    parameter_editor.active = True

    line_style = bpy.data.linestyles.new("CityP_IsoLine")
    line_style.thickness = 1.5
    line_style.color = (0.15, 0.15, 0.18)
    lineset.linestyle = line_style

    for mat in bpy.data.materials:
        if mat.name == "CityP_WhiteClay":
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            bsdf = nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Base Color"].default_value = (0.95, 0.92, 0.85, 1.0)
                bsdf.inputs["Roughness"].default_value = 1.0
                bsdf.inputs["Specular IOR Level"].default_value = 0.0

        elif mat.name == "CityP_RoadMat":
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            bsdf = nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Base Color"].default_value = (0.65, 0.74, 0.83, 1.0)
                bsdf.inputs["Roughness"].default_value = 1.0

    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
