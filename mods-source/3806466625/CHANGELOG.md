# 1.1.18

- 修正起飞时尚在转运、机翼和桨叶未展开就出现循环发动机声音的问题：仅对两版鱼鹰拦截提前播放，待展开完成且旋翼开始转动后恢复。
- 保留原生发动机启动标志和甲板移动流程；兼容暂停、切换观察对象、取消启动、再次出库及落舰停转。
- 1.6 倍视觉尺寸、两版分类和已修复的黄蜂出库逻辑保持原值。
- 编译与离线回归检查通过，实际声音时机仍需完全重启游戏后验证。

---

- Gate premature looping engine audio for both Ospreys during deck transfer and wing/blade unfolding. Resume after the rig is fully unfolded and the rotor starts turning.
- Retain native engine state and deck motion, with handling for pause, unit selection, cancelled starts, repeated launches and recovery spin-down.
- Keep 1.6x visuals, the shared category and the previous Wasp relaunch fixes.
- Compilation and offline regressions passed. Actual audio timing still requires a full game restart and in-game verification.

# 1.1.17

- 两版鱼鹰的视觉尺寸从原模型的 1.45 倍调整至 1.6 倍（本次增量为 32/29，约 10.34%），同步机组、日方标识、转轴、连杆、舱门位移、旋翼桨盘和选取盒；飞行性能与动画控制值保持原值。
- 中英文分类统一沿用美方：舰载倾转旋翼运输机 / Naval transport tiltrotor。
- 无损精简 OBJ 数值与 PNG 压缩；原始日方参考照片移至工程参考目录，保留游戏资料图。整理当前构建源码、发布校验与历史文件。
- 用户已确认 1.1.16 出库恢复正常；保留空排烟资源修复及黄蜂甲板补丁。本次 1.6 倍尺寸的游戏内贴合与动画仍需复测。

---

- Increased both variants from 1.45x to 1.6x original visual size (an incremental 32/29, about 10.34%). Scaled crew, markings, pivots, links, door travel, rotor discs and picking boxes. Flight performance and animation control values are retained.
- Unified both localized categories as Naval transport tiltrotor / 舰载倾转旋翼运输机.
- Compacted OBJ numbers and PNG compression without changing intended game-read values or pixels. Moved the original JGSDF reference photo to the project reference folder, retaining its in-game profile. Consolidated build sources, release validation and historical files.
- The user confirmed normal spawning with 1.1.16. Retained its empty-exhaust-resource fix and the Wasp deck patches. In-game clearance and animation at 1.6x still need verification.

# 1.1.16

- 移除美海军陆战队与陆上自卫队鱼鹰 [Particles] 中的空 ExhaustSmoke 配置。游戏异步加载器只检查键是否存在，会把空值传给 Resources.LoadAsync；飞机在该资源批次完成前保持隐藏。
- 此空路径可触发大量资源加载，与首次再次出库时模型延迟、严重掉帧、内存占用激增，后续因缓存恢复顺畅的现象吻合。
- 保留 1.1.15 的黄蜂回收路线修正、可达性缓存和诊断日志；两个插件 DLL 未改动。
- 已核对两版配置仅移除此资源键，其他运行文件保持一致。完全退出并重启游戏后，首次降落再起飞的显示、帧率和内存改善仍需游戏内验证。

---

- Removed the empty ExhaustSmoke entry from [Particles] in both the USMC and JGSDF aircraft. The native asynchronous loader checks only for the key's presence and passes its empty value to Resources.LoadAsync, keeping the aircraft hidden until that resource batch completes.
- This empty path can trigger bulk resource loading, consistent with delayed visibility, frame drops and a memory spike on the first relaunch, followed by smooth cached launches.
- Retained the 1.1.15 Wasp recovery-route fix, reachability cache and diagnostics. Both plugin DLLs are unchanged.
- Verified that the only aircraft setting change is removal of this resource key, with all other runtime files unchanged. Visibility, frame rate and memory improvement on the first landing/relaunch after a full game restart still require in-game verification.

# 1.1.15

- 针对黄蜂模组的回收配置矛盾：回收点 3 指定 1 号升降机，但配置路线通向 2 号。仅在鱼鹰缺少有效回收路线时，复用同位置回收点 2 至 1 号升降机的既有倒车路线，保留升降机预约，不修改舰船文件。
- 起飞选点的可达性检查改为按甲板缓存，避免反复枚举全部滑行路线；实际滑行仍使用游戏原有选路。
- 增加鱼鹰模型创建、甲板阶段和慢速甲板更新的限量计时日志，便于区分出库延迟与帧率问题。
- 已通过本地编译与离线路线检查；黄蜂回收后再次起飞的显示延迟和掉帧改善尚未经过游戏内验证。

---

- Handle the Wasp mod's mismatched recovery definition for Ospreys: RecoveryPoint3 reserves Elevator1, while its configured route leads to Elevator2. If no valid recovery route exists, reuse the co-located RecoveryPoint2's existing backwards route to the reserved elevator. Ship files and reservations are preserved.
- Cache launch-point reachability per deck instead of repeatedly enumerating every taxi route. Actual taxi routing remains native.
- Add limited Osprey construction, deck-phase and slow deck-update timings to diagnose launch delays and frame drops.
- Compilation and offline route checks passed. The reported Wasp relaunch visibility delay and frame-rate improvement still require in-game verification.

# 1.1.14

- 鱼鹰单位收敛为美国海军陆战队 MV-22B 与日本陆上自卫队 V-22B 两种机型，每种各保留两支航空队。
- 美方保留 VMM-263、VMM-162；日方新增输送航空队第107、第108飞行队。同步更新中英文名称。

---

- Kept two Osprey units: USMC MV-22B and JGSDF V-22B, with two squadron choices each.
- Kept VMM-263 and VMM-162 for the USMC and added the JGSDF Transport Aviation Group's 107th and 108th Squadrons. Updated Chinese and English names.

# 1.1.13

- 新增独立的陆上自卫队 V-22B（91707）机型、灰蓝色双贴图、日之丸、机身文字与资料图；原美军机型保留。
- 旋翼、悬停、运输方案、20 分钟整备和直升机起飞点补丁同时识别日方机型。
- 日方资料图注明海上自卫队原图及 CC BY 4.0 许可。

---

- Added a separate JGSDF V-22B (91707) with two grey-blue texture atlases, roundels, service markings and profile image; the USMC unit remains available.
- Extended rig, hover, logistics, 20-minute ready-up and helicopter launch-point handling to the JGSDF unit.
- Credited the JMSDF reference photo and its CC BY 4.0 license.

# 1.1.12

- 舰船有可达直升机起飞点时，鱼鹰改从该点按 VTOL 流程垂直起飞；陆上基地和没有可达直升机点的舰船保留原有选点。
- 空载、运输和转场方案的基础整备时间设为 20 分钟，修正无武器系统造成的立即整备；游戏甲板计时模式仍会影响实际进度。
- 展翼动画等待由 90 秒缩至 60 秒，与可见展翼过程匹配。
- 无损精简机体与机组 OBJ 数值，并压缩飞机资料图；模型网格、游戏读取的数值和图片像素保持一致。

---

- Launch the Osprey vertically from a reachable helicopter spot on ships, while retaining its VTOL flight model and existing selection elsewhere.
- Set a base 20-minute ready-up time for Empty, Transport and Ferry; the game's flight-deck timing mode still affects progress.
- Match the wing-extension animation wait to the visible motion by reducing it from 90 to 60 seconds.
- Reduce the aircraft and crew OBJ files without changing game-read geometry, and losslessly compress the aircraft profile image.

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
