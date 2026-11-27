# -*- coding: utf-8 -*-
"""生成《地面三维激光扫描技术及其在工程测量中的应用综述》(docx)"""
import os
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

sys.stdout.reconfigure(encoding="utf-8")
OUT = r"C:\Users\31710\OneDrive\Desktop\测量数据\精密仪器综述"
os.makedirs(OUT, exist_ok=True)

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.6)
sec.top_margin = sec.bottom_margin = Cm(2.4)
st = doc.styles["Normal"]
st.font.name = "宋体"
st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")


def run_cn(run, size=12, bold=False):
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run.font.size = Pt(size)
    run.bold = bold


def H1(t):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    run_cn(p.add_run(t), 13.5, True)


def H2(t):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(3)
    run_cn(p.add_run(t), 12, True)


def P(t):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Pt(24)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(2)
    run_cn(p.add_run(t), 12)


def ITEM(t):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Pt(24)
    p.paragraph_format.line_spacing = 1.5
    run_cn(p.add_run(t), 12)


def table(headers, rows, widths=None, fs=9.5):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = ""
        pp = cell.paragraphs[0]
        pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_cn(pp.add_run(h), fs, True)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            pp = cells[i].paragraphs[0]
            pp.alignment = WD_ALIGN_PARAGRAPH.CENTER if i else WD_ALIGN_PARAGRAPH.LEFT
            run_cn(pp.add_run(str(v)), fs)
    if widths:
        for i, w in enumerate(widths):
            for r in t.rows:
                r.cells[i].width = Cm(w)
    doc.add_paragraph()


# ==================== 标题 ====================
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_cn(p.add_run("地面三维激光扫描技术及其在工程测量中的应用"), 17, True)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_cn(p.add_run("——工程测量精密仪器及新技术应用综述"), 12)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_cn(p.add_run("（《工程测量实习》项目 5 · 2 班 202305801025）"), 9.5)
doc.add_paragraph()

H1("一、背景与发展概况")
P("三维激光扫描技术（Three-Dimensional Laser Scanning，又称 LiDAR——"
  "Light Detection and Ranging）是 20 世纪 90 年代中期开始出现、"
  "近十余年迅速成熟的一项高新技术，被认为是继 GPS 之后测绘领域的又一次技术突破。"
  "它通过高速激光扫描测量的方法，大面积、高分辨率、快速地获取被测对象表面的"
  "三维坐标数据，把传统的“点测量”扩展为“面测量”，"
  "把以单点坐标为核心的测量方式推进到以海量点云（point cloud）为核心的数据时代。")
P("地面三维激光扫描技术克服了传统建筑测量的局限性，具有快速性、不接触性、"
  "实时性强、精度高、主动性强、全数字特征等优点，"
  "其成果可直接用于三维建模、变形分析与工程量计算。"
  "随着扫描仪测距精度、扫描速度、点云处理软件与多源数据融合技术的不断进步，"
  "该技术已从最初的逆向工程、文物保护扩展到建筑工程、地下工程、"
  "道路桥梁、电力与工厂设施、矿山与地形测量等众多工程领域，"
  "成为精密工程测量中首选的自动化数据获取手段之一。")

H1("二、基本原理")
H2("（一）基本思想")
P("地面三维激光扫描仪在测站上向目标表面发射激光束，同时测量自仪器中心到目标点的"
  "斜距 S、水平角 α 和 天顶距 θ 三个量，"
  "再由极坐标公式解算出目标点相对于测站的三维坐标（图 1）。"
  "扫描仪内部的反射镜或棱镜在水平和垂直方向上快速旋转，"
  "使激光束按一定的角增量逐行、逐列扫过被测表面，"
  "从而在短时间内获得被测表面上成千上万乃至数百万个点的三维坐标，"
  "这些点集合起来就构成了能反映物体表面形状的“点云”。")
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_picture(os.path.join(OUT, "扫描原理示意图.png"), width=Cm(14.2))
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_cn(p.add_run("图 1　地面三维激光扫描测量原理示意图"), 10)

H2("（二）测距原理")
P("按测距原理，地面三维激光扫描仪主要分为三类：")
ITEM("① 脉冲飞行时间法（TOF）：由仪器发出激光脉冲，"
     "记录脉冲往返的飞行时间 t，按 S = c·t/2 计算斜距（c 为光速）。"
     "测程远（可达数百米至数千米），测距精度一般为毫米级，"
     "是目前大测程扫描仪（如 Riegl VZ 系列）采用的主要方法。")
ITEM("② 相位差法：由仪器发出经过调制的连续激光，"
     "通过测量发射波与回波之间的相位差来计算斜距。"
     "测距精度高（可达 1～2 mm）、扫描速度快（每秒上百万点），"
     "但测程较近，多用于建筑、工业与文物保护等中近距离扫描。")
ITEM("③ 三角测量法：由激光发射器、接收器与目标点构成三角形，"
     "通过已知基线与夹角计算距离，测程较短（几米至几十米），"
     "但精度极高（可达 0.02～0.1 mm），多用于手持式扫描仪与工业测量。")

H2("（三）点位坐标与点云")
P("设仪器中心为原点，X 轴指北、Y 轴指东、Z 轴指向天顶，"
  "则目标点的坐标为：")
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_cn(p.add_run("X = S·sin θ·cos α　　Y = S·sin θ·sin α　　Z = S·cos θ"), 11.5, True)
P("除三维坐标外，扫描仪还同时记录每个点的回波强度（intensity），"
  "部分仪器还配有内置数码相机，可获取目标的彩色影像，"
  "通过影像与点云的配准可为每个点赋以真彩色，"
  "便于后续的纹理映射、目标识别与成果表达。")

H1("三、系统组成与构造")
P("一套完整的地面三维激光扫描系统通常由硬件与软件两大部分组成：")
ITEM("① 扫描仪主机：包括激光发射与接收单元、高速扫描反射镜（或旋转棱镜）、"
     "测角系统（编码度盘）、控制与存储单元、内置数码相机、水平与垂直补偿器、"
     "整平基座与三脚架接口、电池与通讯接口。")
ITEM("② 控制系统：机载控制面板或外接手簿（PDA、平板电脑），"
     "用于设置扫描范围、点间距（扫描分辨率）、扫描速度等参数并控制扫描全过程。")
ITEM("③ 标靶：平面标靶、球状标靶或圆柱标靶，用于多测站点云的配准（拼接）"
     "与控制点联测。")
ITEM("④ 配套软件：包括扫描控制软件、点云配准与去噪软件、"
     "建模与成图软件（如 Cyclone、SCENE、RealWorks、CloudCompare 等）。")
ITEM("⑤ 附属设备：三脚架、电源与充电设备、运输箱、笔记本电脑等。")

H1("四、主要功能与技术特点")
P("1. 主要功能")
P("可以快速获取目标表面的三维坐标与强度/彩色信息；"
  "支持多测站点云配准，形成完整的三维模型；"
  "可进行距离、面积、体积（土方量）量测，断面提取，"
  "平整度与垂直度检测，变形分析与比对，"
  "以及三维建模、纹理映射、立面成图、BIM 建模等。")
P("2. 技术特点")
ITEM("① 快速高效：每秒可获取数万至数百万个点，几分钟即可完成一个测站的扫描，"
     "效率是传统测量的几十倍甚至上百倍；")
ITEM("② 非接触测量：无需接触目标，特别适合危险、不可触及或"
     "不宜破坏的对象（古建筑、危岩、高温设备等）；")
ITEM("③ 高精度、高密度：点间距可达 1～10 mm，点位精度可达毫米级，"
     "能够精细地表达物体表面的细节；")
ITEM("④ 全数字、真三维：成果为数字点云，可直接进入 CAD、GIS、BIM 系统，"
     "实现三维可视化与信息化管理；")
ITEM("⑤ 全天候主动式：采用主动发射激光，不依赖自然光照，可在夜间作业。")

H1("五、作业流程")
P("地面三维激光扫描的作业流程如图 2 所示，可概括为外业与内业两大部分：")
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_picture(os.path.join(OUT, "作业流程图.png"), width=Cm(15.5))
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_cn(p.add_run("图 2　地面三维激光扫描作业流程图"), 10)
ITEM("① 踏勘与方案设计：了解测区范围、对象特点与精度要求，"
     "确定测站位置、数量与扫描分辨率；")
ITEM("② 控制点布设与靶标设置：在测区布设控制点并测量其坐标，"
     "在扫描范围内合理布设标靶，作为多测站点云配准的公共依据；")
ITEM("③ 仪器安置与参数设置：整平仪器，设置扫描范围、点间距、"
     "扫描速度、相机参数等；")
ITEM("④ 分站扫描：按预定方案逐站扫描，"
     "相邻测站之间应有一定重叠（一般不小于 30%），保证配准精度；")
ITEM("⑤ 点云配准（拼接）：以标靶或同名特征为依据，"
     "把各测站点云统一到同一坐标系中，并检查配准误差；")
ITEM("⑥ 去噪、滤波与简化：剔除噪声点与冗余点，抽稀点云，"
     "提高后续处理的效率；")
ITEM("⑦ 特征提取、建模与成图：提取点、线、面等特征，"
     "进行三维建模、立面图绘制、断面提取或工程量计算；")
ITEM("⑧ 成果输出与精度评定：输出点云、模型、图纸与量测成果，"
     "并对点位精度、配准精度和成果精度进行评定。")

H1("六、典型产品与主要技术指标")
P("目前国内外主流的地面三维激光扫描仪产品及其典型指标见表 1"
  "（数据为各厂商公开资料的概略值，仅作比较参考）。")
table(["产品（厂商）", "测距原理", "测程", "测距精度", "扫描速度", "主要应用"],
      [["Leica RTC360 / P 系列", "相位/脉冲", "0.5～130 m", "1～3 mm", "200 万点/s", "建筑、工厂、BIM"],
       ["Faro Focus S 系列", "相位", "0.6～350 m", "±1 mm", "200 万点/s", "建筑、考古、工业"],
       ["Trimble TX8/TX10", "脉冲", "0.6～340 m", "1～2 mm", "100 万点/s", "地形、工程、建模"],
       ["Riegl VZ-2000i", "脉冲", "最远 2500 m", "5～8 mm", "60 万点/s", "大范围地形、矿山"],
       ["Z+F IMAGER 5016", "相位", "0.3～360 m", "0.5～1 mm", "100 万点/s", "精密工业、文物"],
       ["国产手持扫描仪", "三角", "0.1～5 m", "0.02～0.1 mm", "数十万点/s", "逆向工程、工业检测"]],
      widths=[3.6, 1.8, 2.2, 2.0, 2.0, 3.0], fs=8.5)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_cn(p.add_run("表 1　典型地面三维激光扫描仪主要技术指标"), 9.5)

H1("七、在工程测量中的应用")
P("1. 建筑工程与钢结构测量：用于建筑立面测绘、竣工测量、"
  "钢结构安装偏差检测、幕墙与桥架安装定位，可快速获取建筑的完整三维模型，"
  "为改造与运维提供基础数据。")
P("2. 古建筑与文物保护：以非接触方式精细记录古建筑的形制、尺寸与病害，"
  "建立数字档案，为修复设计、变形监测与虚拟展示提供高精度三维数据。")
P("3. 地下工程与隧道：用于隧道断面测量、超欠挖检测、衬砌厚度与形变分析、"
  "地铁车站与管廊的三维建模，可在狭窄、昏暗的洞内快速作业。")
P("4. 土方与地形测量：通过点云生成数字高程模型（DEM），"
  "计算挖填方量与堆体体积，比传统断面法更全面、更准确。")
P("5. 道路与桥梁：用于道路改扩建的现状测绘、桥梁结构的三维扫描与变形检测、"
  "净空与限界测量。")
P("6. 变形监测与工程检测：通过多期点云的配准与比对，"
  "可检测建筑物、边坡、大坝等对象的整体变形与局部损伤，"
  "并提取平整度、垂直度、圆度等几何指标。")
P("7. 工厂与电力设施：对设备、管道、厂房进行三维扫描与逆向建模，"
  "为改扩建、管线碰撞检查与数字化交付提供依据。")

H1("八、技术优越性与局限性")
P("1. 技术优越性")
P("与传统全站仪、水准仪等单点测量相比，三维激光扫描能够在极短时间内"
  "获取整个对象表面的海量三维数据，成果信息完整、细节丰富；"
  "与摄影测量相比，它不依赖目标纹理和自然光照，主动测距、精度稳定，"
  "在弱光、无纹理表面（如混凝土、岩壁）上同样适用；"
  "与常规变形监测相比，它能实现“面状”而非“点状”的变形分析，"
  "更容易发现局部异常。此外，其成果为全数字点云，"
  "可无缝接入 CAD/GIS/BIM 平台，便于信息化管理与多专业协同。")
P("2. 局限性")
P("一是仪器价格昂贵，数据处理软件与人员技术要求较高；"
  "二是点云数据量巨大，对存储、计算与处理能力要求高；"
  "三是激光无法穿透物体，存在遮挡与盲区，需多测站、多角度扫描；"
  "四是对透明（玻璃）、镜面反射及黑色表面测距效果较差；"
  "五是受大气条件（雨、雾、强光）影响，精度与测程会下降；"
  "六是单点精度虽然较高，但点云配准误差会随测站数量累积，"
  "必须布设足够的控制点与标靶加以控制。")

H1("九、发展趋势")
P("(1) 扫描速度与精度持续提高，测程不断增大，仪器向轻量化、便携化、"
  "低成本方向发展；")
P("(2) 与摄影测量、无人机、GNSS、惯性导航（SLAM）等融合，"
  "形成空地一体化的多源数据获取体系，尤其是手持/背包式 SLAM 扫描仪"
  "使室内与地下无控制扫描成为可能；")
P("(3) 点云处理智能化，基于深度学习的自动分类、自动建模与自动变形识别"
  "将大幅降低人工干预；")
P("(4) 与 BIM、数字孪生、智慧城市结合，点云成果直接服务于"
  "工程全生命周期的数字化管理；")
P("(5) 实时化与在线化，扫描—处理—分析一体化，"
  "实现施工过程的实时监测与质量反馈。")

H1("十、实习体会")
P("通过收集资料和对三维激光扫描技术的学习，我对这项技术从“背景—原理—"
  "构造—功能—流程—产品—应用—优越性”有了系统的认识。"
  "最深的体会是：三维激光扫描把测量从“测几个点”变成了“测一个面”，"
  "数据获取方式的变化带来了成果形式和应用模式的根本改变——"
  "测量成果不再只是坐标表，而是可以反复利用的三维数字模型。")
P("同时我也认识到，新技术并不能取代基本的测量原理："
  "无论仪器多么先进，控制点的布设、坐标系的选择、"
  "配准误差的控制、成果精度的评定，仍然离不开控制测量、"
  "误差理论与平差计算的基础知识。这也正是本次《工程测量实习》"
  "安排道路曲线测设、沉降监测、控制网优化设计等基础训练的意义所在——"
  "只有掌握了基本理论与方法，才能真正用好精密仪器和新技术。")

path = os.path.join(OUT, "地面三维激光扫描技术综述.docx")
doc.save(path)
print("saved", path)
print("段落数", len(doc.paragraphs), "表格", len(doc.tables), "图片",
      len(doc.inline_shapes))
