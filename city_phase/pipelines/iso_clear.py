import bpy
import math
from ._common import setup_world_nodes, cleanup_cityp_lights, add_light_to_scene, update_material


def apply(context):
    scene = context.scene
    world = scene.world

    if not world:
        world = bpy.data.worlds.new("CityP_World")
        scene.world = world

    tree = setup_world_nodes(world)

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

    cleanup_cityp_lights()

    add_light_to_scene(
        context, "CityP_IsoSun", "SUN",
        energy=5.0, angle=0.0, color=(1.0, 0.98, 0.92),
    ).rotation_euler = (math.radians(35.264), 0, math.radians(45))

    camera = context.scene.camera
    if camera and camera.data:
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = 120
        camera.rotation_euler = (math.radians(35.264), 0, math.radians(45))
        camera.location = (50, 50, 50)

    scene.render.use_freestyle = True

    for lineset in scene.freestyle_settings.linesets:
        scene.freestyle_settings.linesets.remove(lineset)

    lineset = scene.freestyle_settings.linesets.new("CityP_Outline")
    lineset.select_silhouette = True
    lineset.select_contour = True

    for module in scene.freestyle_settings.modules:
        scene.freestyle_settings.modules.remove(module)

    parameter_editor = scene.freestyle_settings.modules.new("ParameterEditor")
    parameter_editor.active = True

    line_style = bpy.data.linestyles.get("CityP_IsoLine")
    if not line_style:
        line_style = bpy.data.linestyles.new("CityP_IsoLine")
    line_style.thickness = 1.5
    line_style.color = (0.15, 0.15, 0.18)
    lineset.linestyle = line_style

    update_material("CityP_WhiteClay", {
        "Base Color": (0.95, 0.92, 0.85, 1.0),
        "Roughness": 1.0,
        "Specular IOR Level": 0.0,
    })
    update_material("CityP_RoadMat", {
        "Base Color": (0.65, 0.74, 0.83, 1.0),
        "Roughness": 1.0,
    })

    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
