# 1.1.45

2026-10-12 文件整理 / documentation cleanup：用户确认 SV-22 连续吊放可以运行。合并当前中英文说明和原型参数说明，归档可重新生成的源码测试产物；插件、源码、模型、动画、贴图及运行配置保持原字节。完整整理前文件与逐文件 SHA-256 已保留在开发回退包中。

The user confirmed continuous SV-22 dipping tasks work on 2026-10-12. Consolidate current documentation and archive regenerable test products while retaining runtime and source bytes. Older entries below preserve their original validation scope.

- 修复低速悬停后仍被旧固定翼俯仰缓存阻挡自动下放：用实际机体姿态判定稳态，保留35英尺目标、实际20–45英尺部署高度及原生速度/水深/设备条件。
- 对照海况安全高度目标，接受小于0.25 m/s的微小垂直修正；新增有频率和条数限制的等待日志，说明实际未满足的条件。
- 收纳盒两端及两侧上部按机腹实际轮廓补围板，修复斜向亮缝，保留底部通道及全部原有机身、门、探头、挂载和动画。
- 机构1.1.45、甲板1.1.36；回归复现旧缓存阻挡并验证持续旧缓存下的三点连续任务。普通SV-22到点自动悬停仍关闭；2026-10-12用户确认连续吊放可运行，外观与探测效果未在该反馈中分别确认。

# 1.1.44

- 修复内部速度/高度刷新误取消SV-22连续吊放任务；实际玩家滑条、预设菜单、手动悬停仍可取消。专用速度需求即时进入飞行控制，近点按方向及距离减速，收回完成后继续下一点。
- 添加独立SV22_2024_SonarWell五面收纳盒，遮住开舱空白，底部留空；沿用原贴图内壁区域，保持原有舱门、探头、武器挂载和性能。
- 机构1.1.44、甲板1.1.36；保留原生45英尺部署上限、速度/水深/状态条件及全部既有爬升策略。仅执行吊放任务自动悬停，普通SV-22航路不自动悬停。
- 离线三点连续任务覆盖四个机头朝向、两种更新间隔和内部命令刷新；静态探头/门/库存间隙及开口遮挡检查通过。需要完全重启后新任务验证真实下放、监听、回收与后续路径点。

# 1.1.43

- 修复SV-22在真实20英尺也被拒绝吊放：原生高度函数对Aircraft类别一律失败。补丁仅匹配该机所属SV22_2024_ALFS声纳与固定翼宿主，恢复按真实高度及配置上限判断。
- 通过共用判定同时修复声纳启用提示和原生缆线部署阻断；45英尺上限、独立速度/水深/可操作条件保留，其他飞机、直升机与舰艇声纳规则保持。
- 确认原生Enable接受后才进入下放，拒绝时退出专用控制并记录原因；部署日志附实际高度与航速。普通SV-22到点行为和所有飞行策略保持。
- 机构1.1.43、甲板1.1.36；原生字段/分支/调用链与15571项离线任务/飞行/投放检查通过。上一版修正后的舱门网格、声纳参数、武器、运输模型与贴图原字节保留；完整游戏流程需重启、新任务验证。

# 1.1.42

- 修复尚未吊放声纳时出现的机腹宽带：原生 OBJ 读取器把舱门顶点的 -2e-05 错读为 -2。71个科学计数法顶点/法线数值改为完全等值小数；网格面、材料和动作不改。
- 修正 GoToWaypointTask.OnStop(bool) 钩子，保留声纳任务完成与取消边界；原生 Harmony 实际解析验证通过。
- 使用安装游戏的 CharWordReader 对27489条记录逐条核对；同时复现旧模型错误并检查运输模型。任务、飞行和武器离线回归通过。Unity实际显示仍需重启、新任务复测。
- 机构1.1.42；甲板1.1.36、声纳/武器数据、机体参数、全部贴图与运输模型原字节保持。

# 1.1.41

- SV-22新增独立2024 ALFS／FLASH级吊放声呐；原版探头、材料与缆线仅用作外观，传感器数据使用SV22_2024_ALFS，不覆盖原版AQS-13E。
- 只在执行原生吊放声呐航路点时降至约35英尺并悬停，入水后监听、收回并关门后结束任务。保留监听时长，0为无限任务；手动命令、任务取消及原生受油/着陆会退出专用控制。
- 新增SV-22专用机腹模型、左右舱门与3秒收放动画；声呐按后移约40厘米的位置横卧收纳，舱口后缘额外留约5厘米旋转余量。两种运输型及普通SV-22到点行为不变。
- 主被动范围上限30/25公里、4.1kHz、217dB、处理等级5、520米缆线与500米建模深度；未公开参数明确为游戏估算，并在既有850公斤任务设备预算内分配。
- 机构1.1.41针对当前游戏编译；甲板1.1.36原字节保留。配置、接口、85个开口射线、121个收放姿态及离线回归核对；实际显示、缆线与探测需重启后复测。

---

- Add independent SV-22 dipping-sonar data and a dedicated belly hatch using native AQS-13 visuals.
- Hover is scoped to an executing sonar waypoint through listening and retrieval. Ordinary SV-22 terminal hover and SAR remain disabled.
- Preserve weapon loads, aircraft performance, transport geometry and deck1.1.36 binary. Unpublished contemporary parameters are gameplay estimates; Unity/cable/detection checks remain pending.

# 1.1.40

- 2026-10-11 游戏日志确认 1.1.39 的 SV-22 大幅巡航爬升已产生约14–16°抬头、约31 m/s航迹爬升；此前型号条件排除了美方和日方运输型。
- 共享原生30秒巡航爬升策略，三种确切鱼鹰型号均生效；诊断前缀统一为 V-22 cruise climb。保留原生性能上限、用户速度命令和受油/着陆/低速边界。
- 美方与日方运输配置各增加两项500英尺高度响应参数，与 SV-22 一致。运输型搜救/到点自动悬停，以及 SV-22 手动悬停范围沿用。
- 独立声呐布置草案向后移约40厘米，更靠近机身中心；重新核对静态空间和储架/起落架间隙。运行包未新增声呐，鱼雷、浮标、储架、模型、贴图与甲板1.1.36二进制保持。
- 机构1.1.40针对当前游戏编译，完成离线回归和文件哈希核对；美方/日方新修正需完全重启后实机复测。

---

- Extend the previously SV-22-only native cruise-climb fix to both transport variants, retaining native dynamics and command boundaries.
- Add the same two 500 ft response thresholds to both transport configurations and use unit-specific bounded V-22 diagnostics.
- Move the separate sonar-layout proposal aft by approximately 0.40 m. Mechanics 1.1.40; deck 1.1.36 binary and existing assets/stores retained. New transport gameplay checks remain pending.

# 1.1.39

- 排查 SV-22 最大航速下 20→1500 英尺爬升缓慢：原生非战斗爬升按 180 秒交换超额航速能量，高速余推力不足时爬升角很小；本机原生方法离线样本复现约 2.17° / 5.35 米/秒。
- 正常巡航的 SV-22 上升改用原生已有的 30 秒策略，保留原生最大爬升率、动力、阻力、俯仰边界及选定航速。实际爬升期间允许航速下降，不改写速度命令。
- 增加每个高度目标最多四条巡航爬升诊断。运输机、低速/悬停、下降、着陆及受油边界保持。
- 机构插件为 1.1.39，甲板仍为 1.1.36 原字节；运行 INI 的键值、武器/传感器数据、储架、动画和模型全部保持。吊放声呐仅完成位置考察与图示，尚未安装。
- 对安装游戏的原生算术、补丁分派和既有离线回归进行了核对；实际飞行动作需完全重启后复测。

---

- Use the existing native 30-second energy trade for eligible SV-22 non-combat cruise climbs instead of 180 seconds, keeping native dynamics/rate limits and the selected speed command.
- Add bounded diagnostic samples. Native arithmetic and dispatch checks cover the reported maximum-speed altitude change; Unity/gameplay retest remains pending.
- Mechanics 1.1.39; deck 1.1.36 binary and all running configuration values/assets remain unchanged. Dipping-sonar layout is a separate proposal only.

# 1.1.38

- 增加海面实际位置保护，覆盖低速及原生巡航，最低为 20 英尺加原生波浪间距；保持原生着陆/甲板/坠毁/受油边界。
- 低速爬升上限从 5 提高到 12 米/秒、下降 6 米/秒；按制动距离收平，增加有界前飞俯仰，零速悬停保持水平，并记录垂直运动供模式交接使用。
- SV-22 明确填写非战斗/战斗高度响应参数 500/500 英尺，改善原生 2500/10000 英尺默认值造成的小幅爬升过缓。
- 机构插件为 1.1.38，甲板保持 1.1.36 原字节。鱼雷卧放、储架、释放点、武器性能、载弹量、运输机配置与机型功能保持。
- 编译及离线高度/交接检查通过；实际下降与爬升仍需完全重启后复测。

---

- Enforce a sea-state-dependent 20-ft position floor after low-speed and native cruise updates; preserve native landing, deck, crash and active refueling.
- Improve low-speed vertical response, braking, forward-flight pitch and native handoff. Set SV-22 altitude response thresholds to 500/500 ft.
- Mechanics is 1.1.38; the 1.1.36 deck binary and torpedo storage/release data are preserved. Offline checks pass; gameplay retest remains pending.

# 1.1.37

- 修正库存鱼雷竖放并穿过舱顶/舱底：原版 usn_mk46_mod2 长轴沿 Z，去掉额外 90° 俯仰，使用 0,180,0 纵向卧放。
- 鱼雷储架原点 Y 从 0.027 降为 0.023，层间距从 0.005 改为 0.0053；两列及 4/6 枚数量保持。直接读取完整原版预制体子网格包围盒，并与当前机体内舱底/顶三角面核查。
- 仅修改五个鱼雷库存配置值与说明。两枚插件沿用 1.1.36 原字节，浮标储架、武器数据、后舱门实际释放位置、释放姿态、悬停和甲板行为保持。
- 旧竖放布局可被几何检查检出；新布局的完整弹体边界及弹体间距检查通过。修正后画面需完全重启并重新放置 SV-22 复测。

---

- Remove the incorrect 90-degree torpedo storage pitch. The native long axis is Z; use longitudinal storage at 0,180,0.
- Lower the torpedo rack and increase row spacing using complete native mesh bounds and actual inner cabin surfaces. Four/six torpedo counts and all release behavior are preserved.
- Data-only fix; both 1.1.36 plugin binaries remain byte-identical. Geometry checks pass; in-game appearance awaits recheck.

# 1.1.36

- 梳理三型机、原生资源引用、独立武器/声呐名称和两个插件的加载边界。保留按名称加载的资料图和材质文件，运行目录只保留资源及用户说明。
- 高频读取缓存反射成员元数据及未找到的成员；不缓存对象或字段值。统一机型识别，避免同一标识反复做路径解析，并移除重复判断。
- 源码目录中的旧/重复 DLL 归档；正式构建输出统一到 out。发布校验的 --clean 模式更新为包含反潜文件的当前结构。
- 中英文说明按当前功能重写，移除互相矛盾的旧分类与版本段落；完整旧发布历史和源码笔记保留在开发归档。兼容版本提示对齐本机 0.8.5。
- 两枚插件升级为 1.1.36。机体几何、贴图、动画、各装载数量、武器/声呐性能、舱内储架、后舱门释放点与飞行参数保持。
- 当前游戏程序集编译、资源/配置检查及七组离线回归通过。读取基准属于离线代码比较，不代表游戏内帧率；更新后需完全重启复测。

---

- Cache reflection metadata and share identity normalization while reading live values on every call.
- Consolidate build outputs and current documentation; archive old source artifacts and history. Update the clean-release audit and compatibility hint for 0.8.5.
- Both plugins are 1.1.36. All model/texture bytes, weapon data, loadouts, storage/release layout and flight behavior are preserved. Compilation and offline audits pass; in-game recheck remains pending.

# 1.1.35

- 库存弹药改用机舱内不同储架槽位，鱼雷卧放；挂载位置与后舱门释放点分开。只在 SV-22 独立投放系统发射三种独立弹药时移动被选中的一枚，随后沿用原生发射、降落伞、入水及制导流程。
- 三种鱼鹰统一归类为舰载倾转旋翼机（Naval tiltrotor），保留国别与型号名称。
- SV-22 移除低速搜救菜单及全部航路终点自动悬停处理，保留手动悬停。原两种运输型的搜救、终点自动悬停、空中受油及甲板功能保持。
- 两枚插件升级至 1.1.35；装载数量、装备性能、释放点、舱门动画、航程、燃油及机体几何保持。编译与离线核查通过；新增画面与飞行行为仍需完全重启后实测。

---

- Use distinct internal storage slots and independent rear-ramp release points. A scoped prefix moves only the selected SV-22 weapon before native launch.
- Unify all aircraft under Naval tiltrotor. Keep manual SV-22 hover while removing terminal auto-hover and the slow SAR shortcut; preserve transport functionality.
- Both plugins are 1.1.35. Payload counts, weapon/sensor performance, release geometry and aircraft assets are preserved. In-game recheck remains pending.

完整 1.1.35 及以前历史已归档到源码 docs/history_before_1.1.36.md，并包含在 1.1.35 回退包中。
Full earlier history is retained in the development archive and 1.1.35 rollback package.
