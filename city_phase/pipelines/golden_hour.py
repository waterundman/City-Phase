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

    sky = tree.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "PREETHAM2"
    sky.sun_direction = (0.966, 0.0, 0.259)
    sky.turbidity = 4.5
    sky.ground_albedo = 0.2
    sky.location = (-300, 0)

    output = tree.nodes.new("ShaderNodeOutputWorld")
    output.location = (200, 0)

    tree.links.new(sky.outputs["Color"], output.inputs["Surface"])

    scene.render.engine = "CYCLES"
    scene.cycles.samples = 256
    scene.cycles.use_denoising = True

    for light in list(bpy.data.lights):
        if light.name.startswith("CityP_"):
            bpy.data.lights.remove(light)

    sun_data = bpy.data.lights.new("CityP_GoldenSun", "SUN")
    sun_data.energy = 8.0
    sun_data.angle = 0.02
    sun_data.color = (0.96, 0.65, 0.35)
    sun = bpy.data.objects.new("CityP_GoldenSun", sun_data)
    sun.rotation_euler = (math.radians(15), 0, math.radians(45))
    context.collection.objects.link(sun)

    fill_data = bpy.data.lights.new("CityP_CoolFill", "AREA")
    fill_data.energy = 50
    fill_data.color = (0.35, 0.4, 0.65)
    fill_data.size = 30
    fill = bpy.data.objects.new("CityP_CoolFill", fill_data)
    fill.location = (-15, 10, 5)
    fill.rotation_euler = (math.radians(30), 0, math.radians(-60))
    context.collection.objects.link(fill)

    rim_data = bpy.data.lights.new("CityP_Rim", "AREA")
    rim_data.energy = 30
    rim_data.color = (0.8, 0.5, 0.3)
    rim_data.size = 15
    rim = bpy.data.objects.new("CityP_Rim", rim_data)
    rim.location = (10, -10, 3)
    rim.rotation_euler = (math.radians(60), 0, math.radians(135))
    context.collection.objects.link(rim)

    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    scene.sequencer_colorspace_settings.name = "sRGB"
