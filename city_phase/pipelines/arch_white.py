import bpy


def apply(context):
    scene = context.scene
    world = scene.world

    if not world:
        world = bpy.data.worlds.new("CityP_World")
        scene.world = world

    world.use_nodes = True
    tree = world.node_tree
    tree.nodes.clear()

    bg = tree.nodes.new("ShaderNodeTexEnvironment")
    bg.location = (-300, 200)

    sky = tree.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "PREETHAM2"
    sky.sun_direction = (0.5, 0.3, 0.8)
    sky.turbidity = 2.0
    sky.ground_albedo = 0.3
    sky.location = (-300, 0)

    output = tree.nodes.new("ShaderNodeOutputWorld")
    output.location = (200, 0)

    mix = tree.nodes.new("ShaderNodeMixRGB")
    mix.inputs["Fac"].default_value = 0.0
    mix.location = (-50, 0)

    tree.links.new(sky.outputs["Color"], mix.inputs[1])
    tree.links.new(bg.outputs["Color"], mix.inputs[2])
    tree.links.new(mix.outputs["Shader"], output.inputs["Surface"])

    scene.render.engine = "BLENDER_EEVEE_NEXT" if bpy.app.version >= (4, 2, 0) else "BLENDER_EEVEE"

    eevee = scene.eevee
    eevee.use_bloom = False
    eevee.use_ssr = False
    eevee.use_gtao = True
    eevee.gtao_quality = 0.5

    for light in list(bpy.data.lights):
        if light.name.startswith("CityP_"):
            bpy.data.lights.remove(light)

    sun_data = bpy.data.lights.new("CityP_SoftLight", "SUN")
    sun_data.energy = 3.0
    sun_data.angle = 0.1
    sun_data.color = (0.85, 0.88, 0.95)
    sun = bpy.data.objects.new("CityP_SoftLight", sun_data)
    sun.rotation_euler = (0.96, 0, 0.96)
    context.collection.objects.link(sun)

    fill_data = bpy.data.lights.new("CityP_Fill", "AREA")
    fill_data.energy = 100
    fill_data.color = (0.5, 0.55, 0.7)
    fill_data.size = 20
    fill = bpy.data.objects.new("CityP_Fill", fill_data)
    fill.location = (0, 0, 10)
    context.collection.objects.link(fill)

    for mat in bpy.data.materials:
        if mat.name == "CityP_WhiteClay":
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            bsdf = nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Base Color"].default_value = (0.94, 0.93, 0.92, 1.0)
                bsdf.inputs["Roughness"].default_value = 0.85
                bsdf.inputs["Specular IOR Level"].default_value = 0.05
        elif mat.name == "CityP_RoadMat":
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            bsdf = nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Base Color"].default_value = (0.75, 0.75, 0.78, 1.0)
                bsdf.inputs["Roughness"].default_value = 0.9

    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
