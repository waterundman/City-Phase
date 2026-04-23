# 城市相 · CityPhase

**Blender Plugin · Procedural City White Model Generator · Render Pipeline Toolkit**

**Version 2.0.5**  
[中文](#中文) | [English](#english)

---

## 中文

### 项目概述
**城市相 (CityPhase)** 是一个 Blender 原生插件，接受 OSM 地理数据或程序化参数作为输入，输出可直接渲染的城市白膜（建筑体量模型）。核心哲学：**几何优先**——材质与光照服务于建筑形态的表达，而非掩盖形态。

从 v0.7.0 到 v1.0.0，CityPhase 已完成从「规划示意图级别」到「建筑可视化级别」的跨越。  
从 v1.0.0 到 v2.0.0，CityPhase 引入**构成语法引擎**，开始探索从「参数化体量」到「风格化构成」的进化。

### 核心功能

#### 三种生成模式
- **单体建筑 (Single)**：参数化生成 7 种亚洲建筑形态
- **程序化城市 (Procedural City)**：基于多层次路网和地块分割生成完整城市街区
- **OSM 数据 (OSM Data)**：从 OpenStreetMap 拉取真实地理数据并生成体量

#### 路网系统 · 4 种模式
| 模式 | 描述 |
|------|------|
| **Grid / 正交网格** | 主干路 + 次级路网双层结构，适合棋盘格城市 |
| **Radial+Ring / 放射环路** | 同心圆环路 + 放射辐条，巴黎/莫斯科风格 |
| **Organic / 有机生长** | L-System 分支生长，产生不规则路网 |
| **Mixed / 混合模式** | 中心放射环路 + 外围正交网格过渡 |

- 支持分层道路宽度：主干 (14m) > 次级 (8m) > 小巷 (5-6m)

#### 地块分割 · 智能朝向
- **正确多边形偏移**：平行边向内偏移 + miter join，避免质心收缩导致的自相交
- **沿街面朝向分割**：自动识别地块最长边作为街道，建筑 footprint 长轴平行于街道
- 建筑放置时自动旋转，自然朝向街道

#### 建筑生成 · 12 种类型学

**亚洲类型学（7 种）**：`stepped_tower` `tapered` `podium_tower` `slab` `old_res` `complex` `industrial`

**西方风格构成（5 种）** — v2.0 新增：
| 风格 | 核心法则 |
|------|---------|
| **Bauhaus / 包豪斯** | 正交网格、自由平面、流动空间、模数化设计 |
| **Constructivist / 构成主义** | 体块交叉、对角线动力、不对称平衡、悬挑 |
| **Minimalist / 极简主义** | 纯粹几何、片墙、光的切割、极致减法 |
| **Postmodern / 后现代** | 历史符号引用、矛盾并置、色彩、规模游戏 |
| **Brutalist / 粗野主义** | 巨型体量、雕塑立面、粗粝材质、纪念性 |

- 基于 **CompositionBuilder** 构成语法引擎：PLACE / EXTRUDE / INSET / BOOLEAN / SUBDIVIDE / CONNECT / ALIGN / OFFSET / MATERIAL
- 每种风格定义独立的 **PRS（参数化规则集）**，控制不变量与变量

#### 屋顶系统 · 6 种类型
`flat` `hip` `gable` `dome` `terrace` `parapet`
- 在 BMesh 阶段直接对顶面变形，零额外几何体

#### 立面语法 (Facade Grammar)
- **窗格**：`inset_individual` 向内凹陷，形成窗洞感
- **阳台**：extrude 向外推出并缩放，形成阳台板
- 在 LOD 2-3 下可自由组合

#### 城市形态 · 高度分布模型
- **Radial / 同心圆**：中心高、外围低，带双峰次中心
- **Corridor / 走廊轴**：用户定义发展轴线，产生上海世纪大道式天际线
- **Metro Peak / 地铁峰值**：沿走廊随机生成虚拟地铁站，150m 半径内高度加成
- **Waterfront Premium / 临水溢价**：虚拟水岸 300m 内建筑高度提升

#### 视觉增强 · 渲染质感
| 功能 | 技术实现 | 性能开销 |
|------|---------|---------|
| **Grime 污渍纹理** | Musgrave 噪声 + ColorRamp + MixRGB | 材质节点，零几何开销 |
| **Edge Bevel 边缘倒角** | `bmesh.ops.bevel` 硬边倒角 | 轻度几何增加 |
| **Window Emission 窗格发光** | Brick Texture + Emission Shader | 材质节点，零几何开销 |
| **Atmospheric Fog 大气雾效** | World Volume Scatter | 全局一次设置 |

#### 四套渲染管线
- **Arch White**：白膜 + 三灯布光，建筑形态纯粹表达
- **Golden Hour**：低角度暖光 + 体积雾，黄昏氛围
- **Neon Rain**：青品对比 + 湿润路面 + 霓虹点缀，赛博朋克雨夜
- **Iso Clear**：等轴测 + 定向阴影 + 天光漫射，晴空技术图解

#### LOD 与导出
- **4 级细节控制** (0-3)：从极简 box 到完整立面细节
- **分层导出**：FBX / OBJ / USD，按 Buildings / Roads / Vegetation 分集合
- **预设系统**：保存/加载/删除生成参数预设

### 安装
1. 下载 `city_phase.zip`（GitHub Releases 或本仓库根目录）
2. 打开 Blender → Edit → Preferences → Add-ons → Install
3. 选择 `city_phase.zip` 并启用「城市相 CityPhase」
4. 在 3D 视图侧边栏（N 面板）找到「城市相」标签页

### 快速开始
1. 切换 **Mode** 为「Procedural City」
2. 调整 **City Layout** 参数（推荐尝试 `Mixed` 路网模式）
3. 设置 **Urban Morphology**（如开启 Corridor + Metro Peak）
4. 选择 **Roof & Facade** 样式（如 `hip` + `full`）
5. 点击「Generate」生成城市
6. （可选）开启 **Visual Enhancement** 的 Window Emission + Atmospheric Fog
7. 选择 **Render Pipeline** 预设并点击「Apply Pipeline」

### 技术栈
- Python 3.10+
- Blender 3.6 / 4.x (`bpy`, `bmesh`, `mathutils`)
- **Zero external dependencies** — 不依赖 shapely、requests 等第三方库
- 所有几何算法（多边形偏移、布尔运算）自行实现

### 迭代路线
| 版本 | 里程碑 |
|------|--------|
| v0.7.0 | 基础功能：路网、地块、建筑、OSM、渲染管线 |
| v0.8.0 | 多模式路网：Grid / Radial+Ring / Organic / Mixed |
| v0.8.5 | 正确多边形偏移 + 沿街面朝向分割 |
| v0.9.0 | 6 种屋顶 + Facade Grammar（窗格/阳台） |
| v0.9.5 | 城市形态：走廊高度 + 地铁峰值 + 临水溢价 |
| **v1.0.0** | **视觉增强：Grime + Bevel + 窗格发光 + 大气雾** |
| v2.0.0 | 构成语法引擎：CompositionBuilder + 9 种谓词语法 |
| **v2.0.5** | **5 种风格化单体生成器：包豪斯/构成主义/极简/后现代/粗野** |
| v2.1.0 | 混合风格插值：任意两种风格可按比例融合 (interpolate_prs) |
| **v2.2.0** | **自然语言设计意图：输入"轻盈透明"自动匹配风格并生成** |

---

## English

### Overview
**CityPhase** is a native Blender plugin that generates procedural city white models (architectural massing) from OSM geographic data or procedural parameters. Core philosophy: **Geometry First**—materials and lighting serve the expression of architectural form, not obscure it.

From v0.7.0 to v1.0.0, CityPhase evolved from "planning sketch level" to "architectural visualization level".  
From v1.0.0 to v2.0.0, CityPhase introduced the **Composition Engine**, exploring the evolution from "parametric massing" to "stylistic composition".

### Features

#### Three Generation Modes
- **Single Building**: Parametric generation of 7 Asian architectural typologies
- **Procedural City**: Full city block generation via multi-layer road networks and intelligent plot splitting
- **OSM Data**: Fetch real geographic data from OpenStreetMap and generate massing models

#### Road Network System · 4 Modes
| Mode | Description |
|------|-------------|
| **Grid** | Arterial + secondary hierarchical grid, chessboard city style |
| **Radial+Ring** | Concentric rings + radial spokes, Paris/Moscow style |
| **Organic** | L-System branching growth, irregular road networks |
| **Mixed** | Radial-ring core with outer grid transition |

- Hierarchical road widths: arterial (14m) > secondary (8m) > alley (5-6m)

#### Plot Splitting · Street-Aware Orientation
- **Correct polygon offset**: Parallel-edge inward offset with miter join, avoids self-intersection from centroid shrink
- **Street-frontage splitting**: Automatically identifies the longest edge as street frontage; building footprints align parallel to streets
- Buildings auto-rotate to face the street naturally

#### Building Generation · 12 Typologies

**Asian Typologies (7)**: `stepped_tower` `tapered` `podium_tower` `slab` `old_res` `complex` `industrial`

**Western Style Composition (5)** — v2.0 new:
| Style | Core Principles |
|-------|-----------------|
| **Bauhaus** | Orthogonal grid, free plan, flowing space, modular design |
| **Constructivist** | Volume intersection, diagonal dynamics, asymmetry, cantilever |
| **Minimalist** | Pure geometry, wall protagonist, light cutting, extreme subtraction |
| **Postmodern** | Historical motif citation, juxtaposition, color, scale play |
| **Brutalist** | Monumental scale, sculptural facade, raw material, hero volume |

- Powered by **CompositionBuilder** predicate grammar: PLACE / EXTRUDE / INSET / BOOLEAN / SUBDIVIDE / CONNECT / ALIGN / OFFSET / MATERIAL
- Each style defines an independent **PRS (Parametric Rule Set)** controlling invariants and variables

#### Roof System · 6 Types
`flat` `hip` `gable` `dome` `terrace` `parapet`
- Deforms top faces directly in BMesh stage, zero extra geometry

#### Facade Grammar
- **Windows**: `inset_individual` recess for window panel feel
- **Balconies**: Extrude outward and scale to create balcony slabs
- Combinable at LOD 2-3

#### Urban Morphology · Height Distribution
- **Radial**: Concentric height decay with bimodal sub-center
- **Corridor**: User-defined development axis, Shanghai Century Avenue-style skyline
- **Metro Peak**: Virtual metro stations along corridor, height bonus within 150m radius
- **Waterfront Premium**: Height boost within 300m of virtual waterfront

#### Visual Enhancement · Render Quality
| Feature | Technique | Performance Cost |
|---------|-----------|------------------|
| **Grime Texture** | Musgrave noise + ColorRamp + MixRGB | Material nodes, zero geo cost |
| **Edge Bevel** | `bmesh.ops.bevel` on hard edges | Light geometry increase |
| **Window Emission** | Brick Texture + Emission Shader | Material nodes, zero geo cost |
| **Atmospheric Fog** | World Volume Scatter | Global one-time setup |

#### Four Render Pipelines
- **Arch White**: White clay + 3-point lighting, pure form expression
- **Golden Hour**: Low-angle warm light + volumetric fog, dusk atmosphere
- **Neon Rain**: Cyan-magenta contrast + wet roads + neon accents, cyberpunk rain
- **Iso Clear**: Isometric + directional shadows + sky diffusion, clear-day technical drawing

#### LOD & Export
- **4 detail levels** (0-3): From minimal box to full facade detail
- **Layered export**: FBX / OBJ / USD by collection (Buildings / Roads / Vegetation)
- **Preset system**: Save / load / delete generation parameter presets

### Installation
1. Download `city_phase.zip` (GitHub Releases or repo root)
2. Open Blender → Edit → Preferences → Add-ons → Install
3. Select `city_phase.zip` and enable "城市相 CityPhase"
4. Find "城市相" in the 3D Viewport N-Panel sidebar

### Quick Start
1. Switch **Mode** to "Procedural City"
2. Adjust **City Layout** parameters (try `Mixed` road mode)
3. Set **Urban Morphology** (e.g. enable Corridor + Metro Peak)
4. Choose **Roof & Facade** style (e.g. `hip` + `full`)
5. Click "Generate" to build the city
6. (Optional) Enable **Visual Enhancement**: Window Emission + Atmospheric Fog
7. Select a **Render Pipeline** preset and click "Apply Pipeline"

### Tech Stack
- Python 3.10+
- Blender 3.6 / 4.x (`bpy`, `bmesh`, `mathutils`)
- **Zero external dependencies** — no shapely, requests, etc.
- All geometry algorithms (polygon offset, boolean ops) implemented internally

### Version History
| Version | Milestone |
|---------|-----------|
| v0.7.0 | Baseline: roads, blocks, buildings, OSM, render pipelines |
| v0.8.0 | Multi-mode roads: Grid / Radial+Ring / Organic / Mixed |
| v0.8.5 | Correct polygon offset + street-frontage plot splitting |
| v0.9.0 | 6 roof types + Facade Grammar (windows / balconies) |
| v0.9.5 | Urban morphology: corridor height + metro peak + waterfront premium |
| **v1.0.0** | **Visual enhancement: grime, bevel, window emission, atmospheric fog** |
| v2.0.0 | Composition Engine: CompositionBuilder + 9 predicate grammar |
| **v2.0.5** | **5 style generators: Bauhaus / Constructivist / Minimalist / Postmodern / Brutalist** |
| v2.1.0 | Mixed style interpolation: blend any two styles with adjustable ratio |
| **v2.2.0** | **Natural language design intent: type "light and airy" to auto-match styles** |
