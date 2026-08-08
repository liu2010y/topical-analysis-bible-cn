# 《圣经主题分析》中译工程说明

**原书**：*Topical Analysis of the Bible: A Re-statement of Its Moral and Spiritual Truths, Drawn Directly from the Inspired Text*
**作者**：J. Glentworth Butler, D.D.
**出版**：Butler Bible Work Company, New York, 1897（公有领域）
**来源文件**：`topicalanalysiso00butl.epub`（Internet Archive OCR 扫描本）

## 原书结构

本书不是章节体书籍，而是一部**按字母顺序排列的圣经主题工具书**：

- 全书约 590 页、24 万英文单词，约 300 个主题词条（Accountability、Adoption、Affliction、…、Youth）
- 每个词条 = 作者的论述 + 分类整理的经文清单
- 正文中的罗马数字引用（如 XI. 268）指向作者另一部著作 *The Bible Work*（共 11 卷注释书）的卷号与页码

本工程采用**每个主题词条一个 HTML 页面**的划分方式，按原书字母顺序编号。

## 目录结构

```
译文/
├── index.html                 # 目录页（从这里开始阅读）
├── NNN-主题-中文名.html        # 每词条一个页面（build.py 生成，勿手改）
├── assets/
│   ├── style.css              # 护眼淡绿主题
│   ├── app.js                 # 页面交互
│   └── grammar-registry.js    # 全局语法点登记表（build.py 生成，勿手改）
├── data/
│   ├── grammar-points.json    # 语法点主表（唯一可编辑的语法数据源）
│   └── NNN-主题.json           # 每词条的源数据（唯一可编辑的内容源）
├── build.py                   # 生成器：python3 build.py 一键重建全部页面
└── md-archive/                # 早期 Markdown 版本存档（已停止维护）
```

> ⚠️ 整个 `译文/` 文件夹需作为整体移动/分享（HTML 依赖 `assets/` 目录）。

## 页面功能

1. **中英逐段对照**：英文原文（已修正明显 OCR 错误）+ 中文译文；经文中文采用**和合本**通行译法，与原书英文有出入处加括注
1b. **现代英译对照（BSB 行）**：原书经文为 KJV/RV（1611/1885）古体英语；每条经文下并列一行 **BSB**（Berean Standard Bible，已释入公有领域的现代英语译本），古今对照。BSB 全文在 `../bsb/bsb.txt`，`build.py` 构建时按经文块开头的引用（如 "Rom. 14:10, 12."）**自动取经**；不匹配时在块中用 `"bsb": "Romans 2:6"` 覆盖，`"bsb": false` 表示该块不加。顶部有独立的「现代英译」开关（默认开）
2. **英文显示开关**：每节标题右侧 `EN` 按钮控制本节英文；顶部按钮全局控制
3. **悬停查词（两级词典）**：任意英文单词悬停 1.5 秒或点击均可查询——带虚线下划线的是**本词条精编词汇**（语境释义＋级别标注＋古英语说明）；其余单词自动查 **ECDICT 兜底词典**（开源英汉词典裁剪版：单词 2.6 万＋短语 1.6 万＋变形别名 2.8 万，共 7 万键、3.6MB，按首字母分 26 片存于 `assets/dict/`，按需加载，完全离线）。弹窗中标注「通用词典」以区分，并附「网页查词」外链
3b. **划选查词**：用鼠标划选任意单词或**短语**（如 according to、in spite of），弹窗查询＋朗读；短语条目来自兜底词典。兜底词典由 `tools/build_dict_shards.py` 从 `../dict-source/stardict.db`（ECDICT sqlite 发行包）裁剪生成，调整收录规则后重跑该脚本即可
4. **语法说明**：顶部按钮开关，默认隐藏。全局去重——每个语法点只在首次出现的词条里完整讲解，其余位置显示引用 chip（如「参：倒装 → 001」），点击 chip 可就地展开完整讲解
5. **词汇表**：每页底部列出 CET-4 及以上词汇（音标＋释义）

## 维护流程（新增/修改词条）

1. 在 `data/` 新增 `NNN-主题.json`（结构参照现有文件：sections → blocks → en/zh/grammar，另有 hover_vocab、vocab_table）
2. 新语法点先登记到 `data/grammar-points.json`（`first` 字段 = 首次出现的词条编号）
3. 运行 `python3 build.py`——自动重建所有页面、目录页和语法登记表；构建时会警告未登记的语法点和未命中的词典键

## 进度

| 页面 | 主题 | 原书页码 | 状态 |
|------|------|----------|------|
| 001 | Accountability to God（向神交账的责任） | p. 11 | ✅ |
| 002 | Adoption（得儿子的名分） | p. 12 | ✅ |
| 003 | Affliction（苦难） | p. 12–16 | ✅ |
| 004 | Agency, Divine and Human（神人协作） | p. 16–18 | ✅（原书双栏排版按主题重组） |
| 005 | Altar, for Sacrifice（祭坛） | p. 18 | ✅ |
| 006 | Angels, Unfallen and Fallen（天使） | p. 18–19 | ✅ |
| 007 | Anger of Man（人的怒气） | p. 19–20 | ✅ |
| 008 | Anthropopathy（神格拟人） | p. 20 | ✅ |
| 009 | Anxiety（忧虑） | p. 20–21 | ✅ |
| 010 | Apostleship（使徒职分） | p. 21 | ✅ |
| 011 | Archeology and Exploration（考古学与考察） | p. 21–24 | ✅（长篇论述） |
| 012 | Atheist and Atheism（无神论者与无神论） | p. 24 | ✅ |
| 013 | Atonement（赎罪） | p. 24–33 | ✅（全书核心大词条；A 字部完结） |
| 014 | Backsliders（退后背道的人） | p. 33 | ✅（索引式短词条） |
| 015 | Beatitudes（八福与诸福） | p. 34 | ✅ |
| 016 | Beauty（荣美） | p. 35 | ✅ |
| 017 | Benedictions（祝福） | p. 35 | ✅ |
| 018 | Bible（圣经） | p. 35–42 | ✅（B 字部大词条，12 个分节） |
| 019 | Bible Lands and Places（圣经的地域与地名） | p. 42–44 | ✅（地名索引；p.44 城镇列表部分缺失已注明） |
| 020 | Bishop（监督） | p. 44 | ✅（短词条） |
| 021 | Blasphemy（亵渎） | p. 44 | ✅（双栏交错已重建） |
| 022 | Blessings and Curses（祝福与咒诅） | p. 44 | ✅（短词条） |
| 023 | Books and Reading（书籍与阅读） | p. 44–45 | ✅（论述型词条） |
| 024 | Call of God to Man（神对人的呼召） | p. 46–48 | ✅ |
| 025 | Calling, Life Occupation（蒙召的职业） | p. 48 | ✅（短词条） |
| 026 | Captivity（被掳） | p. 48 | ✅（短词条） |
| 027 | Character, Moral（道德品格） | p. 48–49 | ✅ |
| 028 | Characters of Old Testament（旧约人物） | p. 49–50 | ✅（人物索引） |
| 029 | Cherubim（基路伯） | p. 50 | ✅（短词条） |
| 030 | Childlikeness（赤子之心） | p. 50–51 | ✅ |
| 031 | Choices Offered to Men（摆在人面前的抉择） | p. 51–52 | ✅ |
| 032 | Christ on Earth（基督在世） | p. 53–62 | ✅（大词条：品格/比喻/讲论/神迹/大事年表/综述） |
| 033 | Christ and the Believer（基督与信徒） | p. 62–69 | ✅（大词条：四比方/葡萄树/在基督里系列） |
| 034 | Christian Life（基督徒生活，七部连环词条） | p. 69–85 | ✅（全书最大词条，七部分全部完成） |
| 035 | Christianity（基督教） | p. 86–88 | ✅（六段论述摘录） |
| 036 | Chronology（圣经年代学） | p. 88 | ✅（短词条） |
| 037 | Church; Churches（教会） | p. 89–90 | ✅ |
| 038 | Circumcision（割礼） | p. 90 | ✅（短词条） |
| 039 | City, First（最早的城） | p. 90 | ✅（短词条） |
| 040 | Cities of Refuge（逃城） | p. 91 | ✅（短词条） |
| 041 | Civil Government（世上的政权） | p. 91 | ✅（短词条） |
| 042 | Comfort（安慰） | p. 91 | ✅ |
| 043 | Commandments, The Ten（十诫） | p. 92–93 | ✅（含三段摘录） |
| 044 | Condemnation（定罪） | p. 93–95 | ✅（含 J. Orr 摘录） |
| 045 | Confession of Christ（认基督） | p. 96 | ✅（短词条） |
| 046 | Conscience（良心） | p. 96 | ✅（短词条） |
| 047 | Consideration（思想） | p. 96–97 | ✅ |
| 048 | Conversion（归正） | p. 97–98 | ✅ |
| 049 | Covenants（神的诸约） | p. 98–100 | ✅ |
| 050 | Covetousness（贪婪） | p. 100 | ✅ |
| 051 | Creed（信经与教义） | p. 100–103 | ✅（p.101 扫描大面积缺失已标注） |
| 052 | Criticism（圣经批评学） | p. 103–109 | ✅（大词条，八家论辩摘录） |
| 053 | Day of the Lord（主的日子） | p. 109–110 | ✅ |
| 054 | Deacon（执事） | p. 110 | ✅（短词条） |
| 055 | Death（死） | p. 110–113 | ✅（大词条：四段论述含 J. Orr 论死与罪） |
| 056 | Demoniac（被鬼附者） | p. 113 | ✅（极短词条，仅一行索引） |
| 057 | Despondency（灰心丧胆） | p. 113 | ✅ |
| 058 | Diligence（殷勤） | p. 113–114 | ✅（箴言双主题：殷勤与懒惰） |
| 059 | Divorce（离婚） | p. 114 | ✅（短词条） |
| 060 | Doubts（疑惑） | p. 114–115 | ✅（含编者论述"邀请亲自验证"） |
| 061 | Drunkenness（醉酒） | p. 115–116 | ✅ |
| 062 | Elder（长老） | p. 116 | ✅（短词条） |
| 063 | Eternity（永恒） | p. 116–117 | ✅ |
| 064 | Failures of Good Men（义人的失败与教训） | p. 117 | ✅（名录式短词条） |
| 065 | Faith（信心） | p. 117–126 | ✅（核心大词条：定义／对象／称义／十六重关系） |
| 066 | Family（家庭） | p. 126–129 | ✅（婚姻/家/夫妻/亲子/儿女五目） |
| 067 | Fatherless（孤儿） | p. 129 | ✅（短词条） |
| 068 | Fear of God（敬畏神） | p. 129–130 | ✅ |
| 069 | Flesh and Spirit（肉体与灵） | p. 130–134 | ✅（四部结构，含 Babb 嫁接喻、编者论治死、Meyer 论事工中的肉体） |
| 070 | Flood（洪水） | p. 134 | ✅（极短词条） |
| 071 | Foreknowledge; Foreordination; Calling; Election（预知；预定；呼召；拣选） | p. 134–146 | ✅（12 页巨型教义词条，九分节） |
| 072 | Friendship and Fellowship（友谊与相交） | p. 146–147 | ✅ |
| 073 | Giving（奉献） | p. 147–150 | ✅（原则/动机/分量＋三家论施予） |
| 074 | God（神） | p. 150–184 | ✅（全书最大词条：存有—属性—品格—作为—三一—父—子—圣灵—神与人；p.165/180/182 扫描缺损已标注） |
| 075 | Gospel（福音） | p. 184–186 | ✅ |
| 076 | Grace（恩典） | p. 186–189 | ✅（恩典与属灵经历的全环节清单） |
| 077 | Grave; Sheol; Hades（阴间） | p. 189 | ✅（短词条：两约阴间观） |
| 078 | Hearers and Hearing（听道） | p. 190–191 | ✅ |
| 079 | Heart（心） | p. 191–193 | ✅（本性之心/新心/神与心/人与心） |
| 080 | Heaven（天堂） | p. 193–198 | ✅（5 页大词条：两重含义/天上之城/积极福乐） |
| 081 | Holiness（圣洁） | p. 198–200 | ✅ |
| 082 | Hope（盼望） | p. 200–201 | ✅ |
| 083 | House of God（神的殿） | p. 201 | ✅（短词条） |
| 084 | Humility（谦卑） | p. 201–203 | ✅（含拉斯金论伟人的谦卑） |
| 085 | Hypocrisy（假冒为善） | p. 203 | ✅（短词条） |
| 086 | Immortality; Eternal Life（不朽与永生） | p. 203–207 | ✅（含 Orr 论旧约的不朽观与理性佐证） |
| 087 | Incarnation（道成肉身） | p. 207–217 | ✅（10 页教义大词条，Orr／Westcott／Schaff 等九家） |
| 088 | Infirmity（软弱） | p. 217–218 | ✅（短词条） |
| 089 | Inspiration of the Scriptures（圣经的默示） | p. 218–224 | ✅（theopneustos 释义／性质／五重凭据） |
| 090 | Israel（以色列） | p. 225–244 | ✅（20 页巨型词条：McCurdy 亚述学史纲四篇＋论犹太人前途） |
| 091 | Joy（喜乐） | p. 245–247 | ✅ |
| 092 | Judges, Civil（民事审判官） | p. 247 | ✅（短词条） |
| 093 | Judgment of God（神的审判） | p. 248–249 | ✅ |
| 094 | Justification（称义） | p. 249–256 | ✅（法庭用语辨析／恩典根据／信心条件／行为凭据） |
| 095 | Kingdom of God（神的国） | p. 256–263 | ✅（含 Orr、Van Dyke、Liddon 三家长论） |
| 096 | Kingdoms of Israelitish History（以色列诸国） | p. 263 | ✅（索引式短词条） |
| 097 | Labor, Work（劳动） | p. 263–265 | ✅（含佚名长论"劳动的律法与赏赐"） |
| 098 | Law of God（神的律法） | p. 266–276 | ✅（编者亲撰 10 页系统论述，九分节） |
| 099 | Laws of Sinai（西奈诸律法） | p. 276–279 | ✅（道德律/礼仪律/民事律三分） |
| 100 | Liberty, Christian（基督徒的自由） | p. 280–281 | ✅（权宜原则的双重应用） |
| 101 | Life, as Mortal（人生的短暂） | p. 281–282 | ✅ |
| 102 | Life's Periods（人生的各时期） | p. 282–283 | ✅（婴孩/少年/老年） |
| 103 | Light and Darkness（光与暗） | p. 283–286 | ✅ |
| 104 | Longing after God（渴慕神） | p. 286–288 | ✅（含 Miller"除神自己别无足够"） |
| 105 | Lord's Day; Supper; Prayer（主日/主餐/主祷文） | p. 288–289 | ✅（含"debts vs trespasses"语文学辨析） |
| 106 | Love（爱） | p. 289–297 | ✅（五分节：爱的特性/神爱人/人爱神/人爱人/爱为诸德之首） |
| 107 | Man（人） | p. 297–312 | ✅（16 页人论大文：受造/魂灵之辨/神的形像/良心/堕落/两种生命） |
| 108 | Mercy（怜悯） | p. 313–314 | ✅（pardon 与 forgiveness 之辨） |
| 109 | Messianic References（弥赛亚预言） | p. 314 | ✅（交叉索引式短词条） |
| 110 | Miracle（神迹） | p. 315–316 | ✅（旧约神迹清单＋Orr 论超自然） |
| 111 | Missions（宣教） | p. 316–325 | ✅（10 页大词条：Lawrence 三自原则、Venn"差会的善终"、Behrends 六论） |
| 112 | Morality（道德） | p. 326–328 | ✅（道德须扎根于敬虔；selfial/selfish 之辨） |
| 113 | Mystery（奥秘） | p. 328–329 | ✅（mysterion＝向入门者揭晓之事） |
| 114 | Names of God（神的名） | p. 329–332 | ✅（Elohim/Jehovah 诸名＋Green 驳底本说） |
| 115 | Nation（国家） | p. 332–334 | ✅（耶 18 章兴亡律＋列国互为鞭责） |
| 116 | Nature and Natural Phenomena（自然与自然现象） | p. 335–342 | ✅（含 Young 论星空、Behrends 论自然律、Strong 论基督与自然） |
| 117 | New Testament（新约） | p. 343–347 | ✅（Gregory 论四福音成因、Storrs 论新约自证） |
| 118 | Obedience（顺服） | p. 348–350 | ✅ |
| 119 | Old Testament（旧约） | p. 350–362 | ✅（Gregory 旧约结构总纲＋三家论旧约批评） |
| 120 | Paraclete（保惠师） | p. 363 | ✅（短词条：译名辨析） |
| 121– | Patience（忍耐）起 | p. 363– | ⏳ |

完整主题索引见原书 Index of Topics（epub 第 13–18 页）。
