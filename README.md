# 城市相 · CityPhase

**Blender Plugin · Procedural City White Model Generator · Render Pipeline Toolkit**

[中文](#中文) | [English](#english)

---

## 中文

### 项目概述
**城市相**是一个 Blender 原生插件，接受 OSM 地理数据或程序化参数作为输入，输出可直接渲染的城市白膜（白色体量模型）。核心哲学：**几何优先**——材质与光照服务于建筑形态的表达，而非掩盖形态。

### 核心功能
- **三种生成模式**
  - **单体建筑**：参数化生成 7 种建筑形态（步退塔、锥削塔、裙房+塔楼等）
  - **程序化城市**：基于网格扰动和递归分割生成完整城市街区
  - **OSM 数据**：从 OpenStreetMap 拉取真实地理数据并生成体量
- **亚洲建筑类型学**：塔楼、裙房综合体、板楼、老居民楼、工业厂房等 6 种类型
- **四套渲染管线**：Arch White（白膜）、Golden Hour（黄昏）、Neon Rain（霓虹雨夜）、Iso Clear（等轴晴空）
- **LOD 与导出**：0-3 级细节控制，支持 FBX/OBJ/USD 分层导出

### 安装
1. 下载 `city_phase.zip`
2. 打开 Blender → Edit → Preferences → Add-ons → Install
3. 选择 `city_phase.zip` 并启用
4. 在 3D 视图侧边栏（N 面板）找到「城市相」

### 技术栈
- Python 3.10+
- Blender 3.6 / 4.x (bpy, bmesh, mathutils)
- Zero external dependencies

---

## English

### Overview
**CityPhase** is a native Blender plugin that generates procedural city white models (architectural massing) from OSM geographic data or procedural parameters. Core philosophy: **Geometry First**—materials and lighting serve the expression of architectural form, not obscure it.

### Features
- **Three Generation Modes**
  - **Single Building**: Parametric generation of 7 typologies (stepped tower, tapered tower, podium+tower, etc.)
  - **Procedural City**: Full city block generation via grid perturbation and recursive subdivision
  - **OSM Data**: Fetch real geographic data from OpenStreetMap and generate massing models
- **Asian Architectural Typology**: 6 types including towers, podium complexes, slab blocks, old residential, and industrial
- **Four Render Pipelines**: Arch White, Golden Hour, Neon Rain, Iso Clear
- **LOD & Export**: 4 levels of detail control, supports layered FBX/OBJ/USD export

### Installation
1. Download `city_phase.zip`
2. Open Blender → Edit → Preferences → Add-ons → Install
3. Select `city_phase.zip` and enable
4. Find "城市相" in the 3D Viewport N-Panel

### Tech Stack
- Python 3.10+
- Blender 3.6 / 4.x (bpy, bmesh, mathutils)
- Zero external dependencies
