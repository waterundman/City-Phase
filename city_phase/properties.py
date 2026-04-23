import bpy


class CityPhaseSettings(bpy.types.PropertyGroup):
    base_w: bpy.props.FloatProperty(
        name="Base Width",
        description="Building base width (X axis) in meters",
        default=24.0,
        min=4.0,
        max=200.0,
        step=100,
    )

    base_d: bpy.props.FloatProperty(
        name="Base Depth",
        description="Building base depth (Y axis) in meters",
        default=18.0,
        min=4.0,
        max=200.0,
        step=100,
    )

    height: bpy.props.FloatProperty(
        name="Height",
        description="Total building height in meters",
        default=120.0,
        min=3.0,
        max=500.0,
        step=100,
    )

    typology: bpy.props.EnumProperty(
        name="Typology",
        description="Building typology type",
        items=[
            ("stepped_tower", "Stepped Tower", "Stepped setback tower with optional twist"),
            ("tapered", "Tapered Tower", "Linear tapered tower from base to top"),
            ("podium_tower", "Podium + Tower", "Commercial podium with residential/office tower"),
            ("slab", "Slab Block", "Long rectangular slab block, common in Asian residential"),
            ("old_res", "Old Residential", "Small-scale dense residential, pre-2000s"),
            ("complex", "Mixed-Use Complex", "Large mixed-use complex with multiple towers on podium"),
            ("industrial", "Industrial", "Low-span factory with sawtooth roof"),
        ],
        default="stepped_tower",
    )

    seed: bpy.props.IntProperty(
        name="Seed",
        description="Random seed for reproducible generation",
        default=7,
        min=0,
        max=99999,
    )

    sections: bpy.props.IntProperty(
        name="Sections",
        description="Number of setback sections (stepped tower only)",
        default=4,
        min=2,
        max=12,
    )

    setback_ratio: bpy.props.FloatProperty(
        name="Setback Ratio",
        description="XY shrink ratio per section (stepped tower only)",
        default=0.80,
        min=0.5,
        max=0.95,
        step=10,
    )

    twist_deg: bpy.props.FloatProperty(
        name="Twist (deg)",
        description="Twist angle per section in degrees (stepped tower only)",
        default=5.0,
        min=-30.0,
        max=30.0,
        step=100,
    )

    taper_ratio: bpy.props.FloatProperty(
        name="Taper Ratio",
        description="Top-to-bottom size ratio (tapered tower only)",
        default=0.30,
        min=0.05,
        max=0.8,
        step=10,
    )

    podium_height: bpy.props.FloatProperty(
        name="Podium Height",
        description="Podium section height in meters (podium+tower only)",
        default=22.0,
        min=3.0,
        max=80.0,
        step=100,
    )

    tower_ratio: bpy.props.FloatProperty(
        name="Tower Ratio",
        description="Tower width / podium width ratio (podium+tower only)",
        default=0.45,
        min=0.1,
        max=0.9,
        step=10,
    )

    gen_mode: bpy.props.EnumProperty(
        name="Mode",
        description="Generation mode",
        items=[
            ("single", "Single Building", "Generate one building at origin"),
            ("city", "Procedural City", "Generate full city from procedural parameters"),
            ("osm", "OSM Data", "Generate from OpenStreetMap real data"),
        ],
        default="single",
    )

    road_mode: bpy.props.EnumProperty(
        name="Road Mode",
        description="Road network generation pattern",
        items=[
            ("grid", "Grid / 正交网格", "Standard orthogonal grid with hierarchical roads"),
            ("radial_ring", "Radial + Ring / 放射环路", "Concentric rings with radial spokes (Paris/Moscow style)"),
            ("organic", "Organic / 有机生长", "L-system inspired branching growth"),
            ("mixed", "Mixed / 混合模式", "Radial core with outer grid transition"),
        ],
        default="grid",
    )

    city_radius: bpy.props.FloatProperty(
        name="Radius",
        description="City generation radius in meters",
        default=400.0,
        min=100.0,
        max=2000.0,
        step=1000,
    )

    main_grid_spacing: bpy.props.FloatProperty(
        name="Main Grid",
        description="Main road grid spacing in meters",
        default=300.0,
        min=100.0,
        max=800.0,
        step=100,
    )

    sub_grid_spacing: bpy.props.FloatProperty(
        name="Sub Grid",
        description="Secondary road spacing in meters",
        default=90.0,
        min=40.0,
        max=300.0,
        step=100,
    )

    perturbation_pct: bpy.props.FloatProperty(
        name="Perturbation",
        description="Grid node perturbation as percentage of grid spacing",
        default=15.0,
        min=0.0,
        max=40.0,
        step=100,
    )

    building_density: bpy.props.FloatProperty(
        name="Density",
        description="Building fill density (0-1)",
        default=0.75,
        min=0.1,
        max=1.0,
        step=10,
    )

    avg_floors: bpy.props.IntProperty(
        name="Avg Floors",
        description="Average number of floors in the city",
        default=12,
        min=1,
        max=80,
    )

    floor_variance: bpy.props.IntProperty(
        name="Floor Variance",
        description="Floor count variance",
        default=8,
        min=0,
        max=40,
    )

    setback: bpy.props.FloatProperty(
        name="Setback",
        description="Building setback from block edge in meters",
        default=2.0,
        min=0.0,
        max=20.0,
        step=100,
    )

    osm_source: bpy.props.EnumProperty(
        name="OSM Source",
        description="How to define OSM query area",
        items=[
            ("center_radius", "Center + Radius", "Define area by center point and radius"),
            ("bbox", "Bounding Box", "Define area by explicit lat/lon bounds"),
        ],
        default="center_radius",
    )

    osm_lat: bpy.props.FloatProperty(
        name="Latitude",
        description="Center latitude",
        default=31.2304,
        precision=6,
    )

    osm_lon: bpy.props.FloatProperty(
        name="Longitude",
        description="Center longitude",
        default=121.4737,
        precision=6,
    )

    osm_radius: bpy.props.IntProperty(
        name="Radius (m)",
        description="Query radius in meters",
        default=500,
        min=100,
        max=5000,
    )

    bbox_lat_min: bpy.props.FloatProperty(
        name="Lat Min",
        description="Minimum latitude",
        default=31.20,
        precision=6,
    )

    bbox_lat_max: bpy.props.FloatProperty(
        name="Lat Max",
        description="Maximum latitude",
        default=31.26,
        precision=6,
    )

    bbox_lon_min: bpy.props.FloatProperty(
        name="Lon Min",
        description="Minimum longitude",
        default=121.44,
        precision=6,
    )

    bbox_lon_max: bpy.props.FloatProperty(
        name="Lon Max",
        description="Maximum longitude",
        default=121.50,
        precision=6,
    )

    osm_use_cache: bpy.props.BoolProperty(
        name="Use Cache",
        description="Use cached OSM data if available (7 day expiry)",
        default=True,
    )

    lod_level: bpy.props.IntProperty(
        name="LOD",
        description="Level of detail (0=lowest, 3=highest)",
        default=2,
        min=0,
        max=3,
    )

    export_format: bpy.props.EnumProperty(
        name="Export Format",
        description="Export file format",
        items=[
            ("FBX", "FBX", "Filmbox format"),
            ("OBJ", "OBJ", "Wavefront OBJ format"),
            ("USD", "USD", "Universal Scene Description"),
        ],
        default="FBX",
    )

    export_layered: bpy.props.BoolProperty(
        name="Layered Export",
        description="Export by collection (buildings/roads/vegetation)",
        default=True,
    )

    add_roof_details: bpy.props.BoolProperty(
        name="Roof Details",
        description="Add rooftop equipment (cooling towers, water tanks)",
        default=False,
    )

    road_width: bpy.props.FloatProperty(
        name="Road Width",
        description="Road surface width in meters",
        default=8.0,
        min=2.0,
        max=40.0,
        step=100,
    )
