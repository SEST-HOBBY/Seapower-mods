# 1.1.11

- 按游戏截图将机翼整流罩前下段归还固定机身，保留上段随翼旋转和现有机背倾轴。
- 修正甲板停机后循环发动机音效持续播放的问题；旋翼停稳后停止发动机音效。

---

- Kept the lower forward wing fairing fixed to the fuselage while preserving the rotating upper fairing and roof-aligned stow axis.
- Stopped looping engine audio after deck shutdown and rotor spin-down.

# 1.1.10

- 将机翼前方整流罩并入旋转组件，使可见接缝移至机头侧；收纳轴按机背坡度倾斜。
- 着舰与甲板流程保持短舱垂直，消除滑行指令造成的短暂水平倾转；空中回收仍按空速倾转。

---

- Moved the forward wing fairing into the rotating assembly and aligned the stow spindle with the roof slope.
- Held nacelles vertical through landing and deck taxi while preserving airspeed-based conversion during airborne recovery.

# 1.1.9

- 将外观模型、机组、转轴、挂点与选取盒统一放大 1.45 倍；不改飞行性能。
- 回收航线按实际空速控制短舱角度，避免高速时提前转为垂直。

---

- Scaled visible geometry, crew, pivots, mounts and selection boxes by 1.45 without changing flight performance.
- Kept nacelles tied to measured airspeed during high-speed recovery.

# 1.1.8

- 将高速旋转桨盘贴图的不透明度由 6.5% 提高到 20%，增强天空与海面背景下的可见度，保留柔边及平滑启停过渡。

---

- Increased spinning rotor-disc texture opacity from 6.5% to 20% for stronger contrast against sky and sea, retaining soft edges and smooth startup/shutdown transitions.

# 1.1.7

- 将最大总航程提高至 2200 公里，固定翼航程单位明确设为公里，并同步旧物理字段的海里等价值。

---

- Increased the nominal maximum total range to 2200 km, explicitly using kilometres for fixed-wing range and matching the legacy physics field in nautical miles.

# 1.1.6

- 默认、运输及救援任务的载员容量提高至 32 人。
- 核对海平面最高速度配置为 275 节（509.3 公里／小时），航速参数未改动。

---

- Increased default, transport and rescue capacity to 32 personnel.
- Verified the configured maximum sea-level speed of 275 knots (509.3 km/h); speed parameters are unchanged.

# 1.1.5

- 升级海面／地面搜索雷达：上限 220 公里，距离分辨率 15 米，扩大搜索扇区。
- 参照 F/A-18F Block III 模组的先进光电参数，将探测倍率提高至 5.5、识别倍率提高至 3.0，支持昼夜下视搜索。
- 修正红外传感器被配置为普通目视的问题。
- 雷达告警与防御干扰覆盖五个频段，提升告警方位精度和干扰参数。

---

- Upgraded surface/ground radar: 220 km range limit, 15 m range resolution and a wider search sector.
- Matched the F/A-18F Block III mod's advanced optical parameters: 5.5 detection multiplier, 3.0 identification multiplier and day/night downward search.
- Corrected the thermal sensor's native type from Visual to Infrared.
- Expanded radar warning and defensive jamming to five bands, with improved bearing accuracy and jamming parameters.

# 1.1.4

- 修复三个碰撞箱尺寸为零的问题，按模型重建机身、机翼／短舱和尾部选取盒，恢复右键选取所需的碰撞体。
- 清理开发文件、历史备份与未引用的低可视度贴图。
- 保留 1.1.3 的旋翼轴线、平滑模糊过渡及现有无武装运输／搜救功能。

---

- Rebuilt the three zero-sized selection colliders around the fuselage, wing/nacelle envelope and tail.
- Removed development files, historical backups and unused low-visibility textures from the package.
- Preserved the 1.1.3 rotor axes, smooth blur transition and unarmed transport/SAR features.
