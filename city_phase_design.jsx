import { useState } from "react";

const sections = [
  { id: "overview", label: "概览" },
  { id: "arch", label: "插件架构" },
  { id: "pipeline", label: "数据管线" },
  { id: "typology", label: "亚洲建筑类型学" },
  { id: "render", label: "渲染管线预设" },
  { id: "ui", label: "UI面板设计" },
  { id: "phases", label: "开发阶段" },
];

const fileTree = [
  { name: "city_phase/", type: "dir", depth: 0 },
  { name: "__init__.py", type: "file", depth: 1, note: "Addon注册 · bl_info · 依赖检查" },
  { name: "properties.py", type: "file", depth: 1, note: "CityPhaseSettings PropertyGroup" },
  { name: "operators/", type: "dir", depth: 1 },
  { name: "op_generate.py", type: "file", depth: 2, note: "主生成Operator · 调度各Generator" },
  { name: "op_osm_fetch.py", type: "file", depth: 2, note: "Overpass API拉取 · 异步Modal" },
  { name: "op_apply_pipeline.py", type: "file", depth: 2, note: "应用渲染管线预设" },
  { name: "panels/", type: "dir", depth: 1 },
  { name: "panel_main.py", type: "file", depth: 2, note: "N-Panel主界面 · 响应式折叠" },
  { name: "generators/", type: "dir", depth: 1 },
  { name: "city_layout.py", type: "file", depth: 2, note: "路网生成 · 街区细分 · 地块分割" },
  { name: "building_gen.py", type: "file", depth: 2, note: "Footprint→Mesh · 类型学规则" },
  { name: "road_gen.py", type: "file", depth: 2, note: "道路曲面 · 高架桥 · 立交结构" },
  { name: "detail_gen.py", type: "file", depth: 2, note: "屋顶设备 · 广告牌 · LOD控制" },
  { name: "pipelines/", type: "dir", depth: 1 },
  { name: "arch_white.py", type: "file", depth: 2, note: "建筑白膜预设" },
  { name: "golden_hour.py", type: "file", depth: 2, note: "黄昏金切预设" },
  { name: "neon_rain.py", type: "file", depth: 2, note: "霓虹雨夜预设" },
  { name: "iso_clear.py", type: "file", depth: 2, note: "等轴晴空预设" },
  { name: "data/", type: "dir", depth: 1 },
  { name: "typologies.json", type: "file", depth: 2, note: "建筑类型参数表" },
  { name: "utils/", type: "dir", depth: 1 },
  { name: "osm_parser.py", type: "file", depth: 2, note: "OSM XML/JSON解析" },
  { name: "geo_projection.py", type: "file", depth: 2, note: "经纬度→平面坐标投影" },
  { name: "mesh_utils.py", type: "file", depth: 2, note: "BMesh工具函数" },
  { name: "material_utils.py", type: "file", depth: 2, note: "节点材质构建器" },
];

const typologies = [
  {
    id: "tower",
    name: "塔楼",
    en: "Tower",
    floors: "25–60F",
    coverage: "25–40%",
    desc: "细长高层，底层架空或小商业，常见于浦东、新宿副都心",
    color: "#1a3a5c",
    shape: "tall",
  },
  {
    id: "podium",
    name: "裙房+塔楼",
    en: "Podium + Tower",
    floors: "裙房3–6F / 塔楼20–50F",
    coverage: "60–80% (裙房)",
    desc: "商业裙楼托举住宅/办公塔，上海内环CBD标志形态",
    color: "#2d5a8e",
    shape: "podium",
  },
  {
    id: "slab",
    name: "板楼",
    en: "Slab Block",
    floors: "6–18F",
    coverage: "30–50%",
    desc: "长条形板式住宅，东西向排列，1980–2000年代主力建筑类型",
    color: "#3a7ca5",
    shape: "slab",
  },
  {
    id: "old_res",
    name: "老式居民楼",
    en: "Old Residential",
    floors: "4–7F",
    coverage: "70–85%",
    desc: "小尺度密集排布，旧城改造区，上海内环弄堂肌理背景体",
    color: "#4a9078",
    shape: "dense",
  },
  {
    id: "complex",
    name: "综合体",
    en: "Mixed-Use Complex",
    floors: "5–10F (基座)",
    coverage: "80–95%",
    desc: "大底盘商业综合体，不规则平面，常含中庭、天桥连接",
    color: "#7a3a8e",
    shape: "wide",
  },
  {
    id: "industrial",
    name: "工业厂房",
    en: "Industrial",
    floors: "1–3F",
    coverage: "60–75%",
    desc: "大跨度低层，锯齿屋顶，城市边缘/园区，正在大量被改造为创意园区",
    color: "#8e5a2d",
    shape: "flat",
  },
];

const renderPipelines = [
  {
    id: "arch_white",
    name: "建筑白膜",
    tag: "ARCH WHITE",
    engine: "EEVEE",
    palette: ["#F5F5F0", "#E8E8E2", "#C8D4DC", "#8899AA"],
    desc: "纯粹的建筑表达语言。消除所有材质噪声，让城市形态本身成为主角。",
    specs: [
      { k: "引擎", v: "EEVEE" },
      { k: "材质", v: "白色漫反射 + 微腔AO" },
      { k: "光照", v: "柔光区域灯 55° + 蓝灰天光" },
      { k: "相机", v: "45°鸟瞰 / 斜45°透视" },
      { k: "后处理", v: "轻晕影 · 去饱和 · 微锐化" },
    ],
    mood: "冷静 · 分析性 · 建筑事务所汇报",
  },
  {
    id: "golden_hour",
    name: "黄昏金切",
    tag: "GOLDEN HOUR",
    engine: "Cycles / EEVEE",
    palette: ["#F4A460", "#E87040", "#2A3A5C", "#8BA0B8"],
    desc: "东亚城市特有的黄昏时刻——阳光以15°低角切割高密度街区，形成强烈的光影层次。",
    specs: [
      { k: "引擎", v: "Cycles 256spp / EEVEE" },
      { k: "太阳", v: "仰角15–20°，色温2800K，amber调" },
      { k: "阴影", v: "超长投影，蓝紫冷调暗面" },
      { k: "体积", v: "轻度大气散射，城市霾感" },
      { k: "后处理", v: "高对比 · filmic曲线 · 暖色LUT" },
    ],
    mood: "叙事感 · 都市诗意 · 电影静帧",
  },
  {
    id: "neon_rain",
    name: "霓虹雨夜",
    tag: "NEON RAIN",
    engine: "EEVEE + Bloom",
    palette: ["#0A0A14", "#E0203C", "#2040E0", "#F0C020"],
    desc: "雨后湿润路面映射出霓虹的倒影。高密度亚洲城市特有的视觉过载，被转化为美学资产。",
    specs: [
      { k: "引擎", v: "EEVEE + Bloom + AO" },
      { k: "自发光", v: "建筑立面发光条带，红/蓝/黄" },
      { k: "地面", v: "Glossy湿面材质，倒影强度0.8" },
      { k: "体积雾", v: "街道层，密度0.03，向上衰减" },
      { k: "色彩", v: "高饱和 · 低曝光 · 深色基调" },
    ],
    mood: "赛博朋克 · 孤独感 · 视觉冲击",
  },
  {
    id: "iso_clear",
    name: "等轴晴空",
    tag: "ISO CLEAR",
    engine: "EEVEE + Freestyle",
    palette: ["#F2EBD9", "#A8BED4", "#7EC8A0", "#E8D090"],
    desc: "将三维城市还原为精密的等轴插图。Freestyle描边给予每个建筑明确的边界感。",
    specs: [
      { k: "引擎", v: "EEVEE + Freestyle描边" },
      { k: "相机", v: "正交投影，35.26°俯仰（真等轴）" },
      { k: "着色", v: "平面色调 + 单方向硬阴影" },
      { k: "色板", v: "暖米色建筑 / 蓝道路 / 绿地" },
      { k: "后处理", v: "无雾 · 高对比描边 · 无景深" },
    ],
    mood: "清爽 · 示意图感 · 游戏美术/展示板",
  },
];

const phases = [
  {
    num: "01",
    name: "插件骨架",
    duration: "1–2周",
    status: "start",
    tasks: [
      "__init__.py 注册结构",
      "PropertyGroup + N-Panel基础UI",
      "程序化网格城市（无OSM）",
      "单一白色材质 + 可见输出",
    ],
    milestone: "在Blender里看到第一个生成城市",
  },
  {
    num: "02",
    name: "OSM集成",
    duration: "2–3周",
    status: "mid",
    tasks: [
      "Overpass API异步拉取（Modal Operator）",
      "OSM XML/JSON解析 → 内部数据结构",
      "建筑Footprint → 拉伸Mesh",
      "道路网络 → 曲面Mesh",
    ],
    milestone: "输入上海某街区坐标，生成真实路网+建筑体量",
  },
  {
    num: "03",
    name: "亚洲类型学规则",
    duration: "2–3周",
    status: "mid",
    tasks: [
      "建筑类型判别（OSM tags + 面积/比例启发式）",
      "裙房+塔楼二段体量生成",
      "高度梯度算法（离中心距离衰减）",
      "密度填充（程序化模式）",
    ],
    milestone: "生成的城市能看出上海/东京的密度特征",
  },
  {
    num: "04",
    name: "渲染管线",
    duration: "2–3周",
    status: "late",
    tasks: [
      "4个预设Pipeline类完成",
      "节点材质程序化构建",
      "灯光Rig自动配置",
      "EEVEE/Cycles参数一键应用",
    ],
    milestone: "一键切换四种渲染风格，可直接出图",
  },
  {
    num: "05",
    name: "细节与导出",
    duration: "1–2周",
    status: "polish",
    tasks: [
      "LOD系统（0–3级精度）",
      "屋顶细节生成（选配）",
      "FBX/OBJ/USD分层导出",
      "Collection组织（建筑/道路/水体/植被）",
    ],
    milestone: "可交付给其他DCC工具使用的城市资产",
  },
];

const PhaseColors = {
  start: { bg: "#0d2a1a", border: "#1a6640", text: "#4ade80", dot: "#22c55e" },
  mid: { bg: "#0d1f2a", border: "#1a4060", text: "#60a5fa", dot: "#3b82f6" },
  late: { bg: "#1a0d2a", border: "#3a1a60", text: "#a78bfa", dot: "#8b5cf6" },
  polish: { bg: "#2a1a0d", border: "#604010", text: "#fb923c", dot: "#f97316" },
};

function BuildingShape({ shape, color }) {
  const shapes = {
    tall: (
      <svg width="48" height="80" viewBox="0 0 48 80">
        <rect x="14" y="5" width="20" height="75" fill={color} opacity="0.9" rx="1"/>
        <rect x="16" y="5" width="16" height="10" fill={color} opacity="1" rx="1"/>
      </svg>
    ),
    podium: (
      <svg width="56" height="80" viewBox="0 0 56 80">
        <rect x="4" y="45" width="48" height="35" fill={color} opacity="0.7" rx="1"/>
        <rect x="16" y="8" width="24" height="40" fill={color} opacity="1" rx="1"/>
      </svg>
    ),
    slab: (
      <svg width="72" height="60" viewBox="0 0 72 60">
        <rect x="4" y="15" width="64" height="45" fill={color} opacity="0.9" rx="1"/>
      </svg>
    ),
    dense: (
      <svg width="64" height="56" viewBox="0 0 64 56">
        <rect x="2" y="20" width="18" height="36" fill={color} opacity="0.8" rx="1"/>
        <rect x="23" y="14" width="18" height="42" fill={color} opacity="0.9" rx="1"/>
        <rect x="44" y="18" width="18" height="38" fill={color} opacity="0.85" rx="1"/>
      </svg>
    ),
    wide: (
      <svg width="72" height="56" viewBox="0 0 72 56">
        <rect x="4" y="24" width="64" height="32" fill={color} opacity="0.7" rx="1"/>
        <rect x="16" y="10" width="20" height="18" fill={color} opacity="0.9" rx="1"/>
        <rect x="38" y="14" width="18" height="14" fill={color} opacity="0.85" rx="1"/>
      </svg>
    ),
    flat: (
      <svg width="72" height="40" viewBox="0 0 72 40">
        <rect x="4" y="18" width="64" height="22" fill={color} opacity="0.8" rx="1"/>
        <polygon points="4,18 20,6 36,18" fill={color} opacity="0.7"/>
        <polygon points="36,18 52,6 68,18" fill={color} opacity="0.7"/>
      </svg>
    ),
  };
  return shapes[shape] || shapes.tall;
}

export default function CityPhaseDoc() {
  const [active, setActive] = useState("overview");

  return (
    <div style={{
      fontFamily: "'Courier New', 'Consolas', monospace",
      background: "#080c10",
      color: "#c8d4e0",
      minHeight: "100vh",
      fontSize: "13px",
      lineHeight: "1.6",
    }}>
      {/* Header */}
      <div style={{
        borderBottom: "1px solid #1a2a3a",
        padding: "28px 32px 20px",
        background: "linear-gradient(180deg, #0a1018 0%, #080c10 100%)",
      }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: "16px", marginBottom: "6px" }}>
          <span style={{ fontSize: "11px", color: "#3a6080", letterSpacing: "0.2em" }}>PROJECT DESIGN DOC</span>
          <span style={{ fontSize: "11px", color: "#1a3040" }}>v0.1</span>
        </div>
        <h1 style={{
          fontSize: "32px",
          fontWeight: "700",
          color: "#e8f0f8",
          margin: "0 0 4px",
          letterSpacing: "-0.5px",
          fontFamily: "'Courier New', monospace",
        }}>城市相 · CityPhase</h1>
        <p style={{ color: "#4a6a80", margin: 0, fontSize: "12px" }}>
          Blender Plugin · Procedural City White Model Generator · Render Pipeline Toolkit
        </p>
      </div>

      {/* Nav */}
      <div style={{
        display: "flex",
        gap: "2px",
        padding: "0 32px",
        borderBottom: "1px solid #1a2a3a",
        background: "#080c10",
        overflowX: "auto",
      }}>
        {sections.map(s => (
          <button key={s.id} onClick={() => setActive(s.id)} style={{
            background: "none",
            border: "none",
            padding: "10px 14px",
            cursor: "pointer",
            color: active === s.id ? "#60b0e0" : "#3a5060",
            borderBottom: active === s.id ? "2px solid #3080b0" : "2px solid transparent",
            fontSize: "11px",
            letterSpacing: "0.1em",
            whiteSpace: "nowrap",
            transition: "color 0.15s",
          }}>{s.label}</button>
        ))}
      </div>

      <div style={{ padding: "28px 32px", maxWidth: "900px" }}>

        {/* OVERVIEW */}
        {active === "overview" && (
          <div>
            <Label>项目定义</Label>
            <p style={{ color: "#8ab0c8", marginBottom: "24px", lineHeight: "1.8" }}>
              城市相是一个Blender原生插件，接受OSM地理数据或程序化参数作为输入，
              输出可直接渲染的城市白膜（白色体量模型），并预制数个针对现代亚洲高密度城市美学优化的渲染管线。
              核心哲学：<em style={{color:"#60b0e0"}}>几何优先，材质服务于形态的表达而非掩盖形态。</em>
            </p>

            <Label>核心功能矩阵</Label>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginBottom: "24px" }}>
              {[
                ["OSM数据导入", "Overpass API拉取 + 解析建筑/道路/地块"],
                ["程序化生成", "参数化城市布局，种子可控，风格可选"],
                ["亚洲类型学", "裙房塔楼、板楼、老居民楼等六种体量规则"],
                ["四套渲染管线", "白膜 / 黄昏 / 霓虹 / 等轴，一键切换"],
                ["LOD系统", "0–3级精度，适配不同视距渲染需求"],
                ["分层导出", "Collection分组，支持FBX/OBJ/USD"],
              ].map(([k, v]) => (
                <div key={k} style={{
                  background: "#0a1018",
                  border: "1px solid #1a2a3a",
                  padding: "12px 14px",
                  borderRadius: "4px",
                }}>
                  <div style={{ color: "#60b0e0", fontSize: "11px", marginBottom: "4px" }}>{k}</div>
                  <div style={{ color: "#6a8090", fontSize: "12px" }}>{v}</div>
                </div>
              ))}
            </div>

            <Label>技术栈</Label>
            <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
              {["Python 3.10+", "bpy (Blender 3.6 / 4.x)", "bmesh", "requests", "xml.etree", "mathutils", "EEVEE + Cycles"].map(t => (
                <span key={t} style={{
                  background: "#0d1a20",
                  border: "1px solid #1a3040",
                  color: "#4a8090",
                  padding: "4px 10px",
                  borderRadius: "2px",
                  fontSize: "11px",
                }}>{t}</span>
              ))}
            </div>
          </div>
        )}

        {/* ARCHITECTURE */}
        {active === "arch" && (
          <div>
            <Label>目录结构</Label>
            <div style={{
              background: "#060a0e",
              border: "1px solid #1a2a3a",
              borderRadius: "4px",
              padding: "16px",
              marginBottom: "24px",
            }}>
              {fileTree.map((f, i) => (
                <div key={i} style={{
                  display: "flex",
                  alignItems: "baseline",
                  gap: "8px",
                  padding: "2px 0",
                  paddingLeft: `${f.depth * 20}px`,
                }}>
                  <span style={{ color: f.type === "dir" ? "#6a90a0" : "#4a6070", minWidth: "180px", fontSize: "12px" }}>
                    {f.type === "dir" ? "📁 " : "   "}{f.name}
                  </span>
                  {f.note && <span style={{ color: "#2a4050", fontSize: "11px" }}>// {f.note}</span>}
                </div>
              ))}
            </div>

            <Label>关键模块说明</Label>
            {[
              {
                name: "op_generate.py — 主Operator",
                code: `class CITYP_OT_Generate(bpy.types.Operator):
    bl_idname = "cityp.generate"
    bl_label = "生成城市白膜"
    
    def execute(self, context):
        props = context.scene.cityp_settings
        # 1. 获取数据（OSM or 程序化）
        city_data = fetch_osm(props) if props.mode == 'OSM' 
                    else procedural_gen(props)
        # 2. 构建几何
        build_city_mesh(city_data, props)
        # 3. 组织Collections
        organize_collections()
        return {'FINISHED'}`,
              },
              {
                name: "geo_projection.py — 坐标投影",
                code: `def latlon_to_local(lat, lon, origin_lat, origin_lon):
    """墨卡托投影，以城市中心为原点"""
    R = 6371000  # 地球半径(m)
    x = R * math.radians(lon - origin_lon) * math.cos(math.radians(origin_lat))
    y = R * math.radians(lat - origin_lat)
    return x, y`,
              },
            ].map(item => (
              <div key={item.name} style={{ marginBottom: "20px" }}>
                <div style={{ color: "#4a7890", fontSize: "11px", marginBottom: "8px" }}>{item.name}</div>
                <pre style={{
                  background: "#050810",
                  border: "1px solid #141e2a",
                  padding: "14px",
                  borderRadius: "3px",
                  fontSize: "11px",
                  color: "#7aaa88",
                  overflowX: "auto",
                  margin: 0,
                  lineHeight: "1.7",
                }}>{item.code}</pre>
              </div>
            ))}
          </div>
        )}

        {/* DATA PIPELINE */}
        {active === "pipeline" && (
          <div>
            <Label>双模式数据管线</Label>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "28px" }}>
              <div style={{ background: "#0a1018", border: "1px solid #1a3040", borderRadius: "4px", padding: "16px" }}>
                <div style={{ color: "#60b0e0", fontSize: "12px", marginBottom: "12px", letterSpacing: "0.1em" }}>OSM 模式</div>
                {["① 用户输入城市名 / 经纬度BBox", "② Overpass API 查询 (buildings + highways + landuse)", "③ XML解析 → Way/Node数据结构", "④ 经纬度 → 平面坐标（墨卡托投影）", "⑤ Way多边形 → BMesh Footprint", "⑥ 按OSM tags推断建筑类型", "⑦ 执行类型学体量规则"].map((s, i) => (
                  <div key={i} style={{ display: "flex", gap: "8px", marginBottom: "6px" }}>
                    <span style={{ color: "#1a4060", width: "14px", flexShrink: 0 }}>›</span>
                    <span style={{ color: "#5a8090", fontSize: "12px" }}>{s}</span>
                  </div>
                ))}
              </div>
              <div style={{ background: "#0a1018", border: "1px solid #1a3040", borderRadius: "4px", padding: "16px" }}>
                <div style={{ color: "#80c060", fontSize: "12px", marginBottom: "12px", letterSpacing: "0.1em" }}>程序化 模式</div>
                {["① 用户设定网格密度 / 随机种子 / 范围", "② 生成骨干路网（网格+有机扰动）", "③ 细分街区 → 地块Polygon", "④ 按离中心距离分配建筑类型权重", "⑤ 地块内生成建筑Footprint", "⑥ 应用高度梯度模型", "⑦ 填充空隙绿地/广场"].map((s, i) => (
                  <div key={i} style={{ display: "flex", gap: "8px", marginBottom: "6px" }}>
                    <span style={{ color: "#1a4020", width: "14px", flexShrink: 0 }}>›</span>
                    <span style={{ color: "#5a8090", fontSize: "12px" }}>{s}</span>
                  </div>
                ))}
              </div>
            </div>

            <Label>高度梯度模型</Label>
            <div style={{ background: "#060a0e", border: "1px solid #141e28", padding: "16px", borderRadius: "4px", marginBottom: "20px" }}>
              <pre style={{ color: "#7aaa88", fontSize: "11px", margin: 0, lineHeight: "1.8" }}>{`def assign_height(distance_ratio, typology, rng):
    """
    distance_ratio: 0=市中心 → 1=城市边缘
    
    高度模型：双峰分布（CBD + 副中心）+ 随机扰动
    """
    base_heights = {
        'tower':    lerp(120, 40, distance_ratio),
        'podium':   lerp(80,  25, distance_ratio),
        'slab':     lerp(50,  18, distance_ratio),
        'old_res':  lerp(20,  12, distance_ratio),
    }
    base = base_heights.get(typology, 30)
    # 添加±30%随机扰动，避免机械均匀感
    variance = base * 0.3 * (rng.random() * 2 - 1)
    return max(base + variance, 6.0)`}
            </pre>
            </div>
          </div>
        )}

        {/* TYPOLOGY */}
        {active === "typology" && (
          <div>
            <Label>六种建筑类型学</Label>
            <p style={{ color: "#4a6070", marginBottom: "20px", fontSize: "12px" }}>
              基于对上海/东京城市形态的归纳，覆盖现代亚洲高密度城市90%以上的建筑体量类型
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              {typologies.map(t => (
                <div key={t.id} style={{
                  background: "#080d12",
                  border: `1px solid ${t.color}33`,
                  borderLeft: `3px solid ${t.color}`,
                  borderRadius: "4px",
                  padding: "14px 16px",
                  display: "flex",
                  gap: "14px",
                  alignItems: "flex-start",
                }}>
                  <div style={{ flexShrink: 0, display: "flex", alignItems: "flex-end", height: "80px" }}>
                    <BuildingShape shape={t.shape} color={t.color} />
                  </div>
                  <div>
                    <div style={{ display: "flex", alignItems: "baseline", gap: "8px", marginBottom: "4px" }}>
                      <span style={{ color: "#d0dce8", fontSize: "14px", fontWeight: "600" }}>{t.name}</span>
                      <span style={{ color: "#3a5060", fontSize: "10px" }}>{t.en}</span>
                    </div>
                    <div style={{ display: "flex", gap: "12px", marginBottom: "6px" }}>
                      <span style={{ color: t.color, fontSize: "10px" }}>层数 {t.floors}</span>
                      <span style={{ color: "#2a4050", fontSize: "10px" }}>覆盖率 {t.coverage}</span>
                    </div>
                    <p style={{ color: "#4a6070", fontSize: "11px", margin: 0, lineHeight: "1.6" }}>{t.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* RENDER PIPELINES */}
        {active === "render" && (
          <div>
            <Label>四套渲染管线预设</Label>
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {renderPipelines.map(p => (
                <div key={p.id} style={{
                  background: "#080d12",
                  border: "1px solid #1a2a3a",
                  borderRadius: "4px",
                  overflow: "hidden",
                }}>
                  <div style={{
                    padding: "14px 18px",
                    borderBottom: "1px solid #1a2a3a",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}>
                    <div>
                      <span style={{ color: "#d0dce8", fontSize: "15px", fontWeight: "600", marginRight: "10px" }}>{p.name}</span>
                      <span style={{
                        background: "#0a1820",
                        border: "1px solid #1a3040",
                        color: "#3a7090",
                        padding: "2px 8px",
                        fontSize: "10px",
                        letterSpacing: "0.1em",
                        borderRadius: "2px",
                      }}>{p.tag}</span>
                    </div>
                    <span style={{ color: "#2a4050", fontSize: "11px" }}>ENGINE: {p.engine}</span>
                  </div>
                  <div style={{ padding: "14px 18px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                    <div>
                      <p style={{ color: "#5a7888", fontSize: "12px", margin: "0 0 12px", lineHeight: "1.7" }}>{p.desc}</p>
                      <div style={{ display: "flex", gap: "6px", marginBottom: "10px" }}>
                        {p.palette.map((c, i) => (
                          <div key={i} style={{
                            width: "28px", height: "28px",
                            background: c,
                            borderRadius: "2px",
                            border: "1px solid #ffffff11",
                          }} title={c} />
                        ))}
                      </div>
                      <div style={{ color: "#2a4050", fontSize: "11px", fontStyle: "italic" }}>氛围：{p.mood}</div>
                    </div>
                    <div>
                      {p.specs.map(s => (
                        <div key={s.k} style={{ display: "flex", gap: "8px", marginBottom: "5px" }}>
                          <span style={{ color: "#2a5060", fontSize: "11px", width: "50px", flexShrink: 0 }}>{s.k}</span>
                          <span style={{ color: "#5a8090", fontSize: "11px" }}>{s.v}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* UI PANEL */}
        {active === "ui" && (
          <div>
            <Label>N-Panel 面板结构</Label>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
              {/* Mock panel */}
              <div style={{
                background: "#1a1e24",
                border: "1px solid #2a3040",
                borderRadius: "6px",
                overflow: "hidden",
                maxWidth: "220px",
              }}>
                <div style={{ background: "#2a3040", padding: "6px 10px", fontSize: "11px", color: "#8a9ab0", letterSpacing: "0.1em" }}>
                  城市相
                </div>
                {[
                  { section: "数据源", items: ["模式: [OSM ▼]", "城市/坐标: ___", "范围: 2.0 km"] },
                  { section: "生成参数", items: ["建筑密度: ████░ 0.75", "平均层数: 12F ±8", "LOD: [2 ▼]"] },
                  { section: "", items: ["[█ 生成城市白膜]"] },
                  { section: "渲染管线", items: ["预设: [黄昏金切 ▼]", "[✓ 应用管线]"] },
                  { section: "导出", items: ["格式: [FBX ▼]", "分层导出 ☑", "[导出]"] },
                ].map((g, i) => (
                  <div key={i} style={{ borderTop: "1px solid #2a3040" }}>
                    {g.section && (
                      <div style={{ padding: "5px 10px 2px", fontSize: "10px", color: "#4a6070", letterSpacing: "0.1em" }}>
                        {g.section}
                      </div>
                    )}
                    {g.items.map((item, j) => (
                      <div key={j} style={{
                        padding: "4px 14px",
                        fontSize: "11px",
                        color: item.startsWith("[█") ? "#c8e0f0" : "#6a8090",
                        background: item.startsWith("[█") ? "#1a3a50" : "transparent",
                        margin: item.startsWith("[█") ? "4px 8px" : "0",
                        borderRadius: item.startsWith("[█") ? "3px" : "0",
                        textAlign: item.startsWith("[█") ? "center" : "left",
                      }}>{item}</div>
                    ))}
                  </div>
                ))}
              </div>

              {/* Descriptions */}
              <div style={{ paddingTop: "4px" }}>
                {[
                  ["数据源", "OSM/程序化模式切换。OSM模式下显示城市输入和范围滑块，程序化模式显示种子和网格参数。"],
                  ["生成参数", "城市风格预设（现代亚洲/欧洲历史等）、密度、层数、LOD精度。"],
                  ["生成按钮", "主Operator入口，执行完整的数据→几何流程，完成后自动跳转到Scene Collection。"],
                  ["渲染管线", "下拉选择四种预设，「应用管线」按钮重新配置灯光、材质、EEVEE/Cycles参数。"],
                  ["导出", "格式下拉、分层导出选项，按Collection分别导出建筑/道路/水体。"],
                ].map(([k, v]) => (
                  <div key={k} style={{ marginBottom: "14px" }}>
                    <div style={{ color: "#60a0b8", fontSize: "11px", marginBottom: "4px" }}>{k}</div>
                    <div style={{ color: "#4a6070", fontSize: "12px", lineHeight: "1.6" }}>{v}</div>
                  </div>
                ))}
              </div>
            </div>

            <Label style={{ marginTop: "24px" }}>Blender插件注册模式</Label>
            <pre style={{
              background: "#050810",
              border: "1px solid #141e2a",
              padding: "14px",
              borderRadius: "3px",
              fontSize: "11px",
              color: "#7aaa88",
              lineHeight: "1.7",
            }}>{`bl_info = {
    "name": "城市相 CityPhase",
    "author": "...",
    "version": (0, 1, 0),
    "blender": (3, 6, 0),
    "category": "Add Mesh",
    "description": "Procedural city white model generator with render pipeline presets",
}

classes = [
    CityPhaseSettings,   # PropertyGroup
    CITYP_OT_Generate,   # 主生成Operator
    CITYP_OT_FetchOSM,   # OSM拉取
    CITYP_OT_ApplyPipeline,
    CITYP_PT_MainPanel,  # N-Panel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cityp_settings = PointerProperty(type=CityPhaseSettings)`}</pre>
          </div>
        )}

        {/* PHASES */}
        {active === "phases" && (
          <div>
            <Label>开发阶段规划</Label>
            <div style={{ position: "relative" }}>
              {phases.map((phase, i) => {
                const c = PhaseColors[phase.status];
                return (
                  <div key={phase.num} style={{
                    display: "flex",
                    gap: "16px",
                    marginBottom: "16px",
                  }}>
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: "14px", flexShrink: 0 }}>
                      <div style={{
                        width: "10px", height: "10px", borderRadius: "50%",
                        background: c.dot, flexShrink: 0, marginTop: "16px",
                      }} />
                      {i < phases.length - 1 && (
                        <div style={{ width: "1px", flex: 1, background: "#1a2a3a", marginTop: "4px" }} />
                      )}
                    </div>
                    <div style={{
                      flex: 1,
                      background: c.bg,
                      border: `1px solid ${c.border}`,
                      borderRadius: "4px",
                      padding: "14px 16px",
                    }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                        <div style={{ display: "flex", alignItems: "baseline", gap: "10px" }}>
                          <span style={{ color: c.dot, fontSize: "11px", fontWeight: "700" }}>PHASE {phase.num}</span>
                          <span style={{ color: "#d0dce8", fontSize: "14px", fontWeight: "600" }}>{phase.name}</span>
                        </div>
                        <span style={{ color: "#2a4050", fontSize: "11px" }}>{phase.duration}</span>
                      </div>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4px", marginBottom: "10px" }}>
                        {phase.tasks.map((t, j) => (
                          <div key={j} style={{ display: "flex", gap: "6px", alignItems: "flex-start" }}>
                            <span style={{ color: c.border, fontSize: "10px", marginTop: "2px" }}>□</span>
                            <span style={{ color: "#4a6070", fontSize: "11px" }}>{t}</span>
                          </div>
                        ))}
                      </div>
                      <div style={{
                        borderTop: `1px solid ${c.border}`,
                        paddingTop: "8px",
                        fontSize: "11px",
                        color: c.text,
                      }}>
                        <span style={{ color: "#2a4050" }}>里程碑 › </span>{phase.milestone}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div style={{
              background: "#0a1018",
              border: "1px solid #1a3040",
              borderRadius: "4px",
              padding: "14px 16px",
              marginTop: "8px",
            }}>
              <div style={{ color: "#3a7090", fontSize: "11px", marginBottom: "6px" }}>⚠ 开发注意事项</div>
              {[
                "Overpass API有频率限制，OSM获取应加缓存层（本地JSON缓存）",
                "bpy不支持真正的异步，网络请求要用 modal() + 计时器模式",
                "大城市OSM数据可能包含十万级节点，geometry construction要用BMesh而非直接操作mesh",
                "Blender addon打包时需检查第三方依赖（requests等），或引导用户pip安装",
              ].map((note, i) => (
                <div key={i} style={{ display: "flex", gap: "8px", marginBottom: "5px" }}>
                  <span style={{ color: "#1a4060" }}>—</span>
                  <span style={{ color: "#4a6070", fontSize: "11px" }}>{note}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function Label({ children }) {
  return (
    <div style={{
      fontSize: "10px",
      color: "#2a5060",
      letterSpacing: "0.2em",
      textTransform: "uppercase",
      marginBottom: "12px",
      paddingBottom: "6px",
      borderBottom: "1px solid #0d1a22",
    }}>{children}</div>
  );
}
