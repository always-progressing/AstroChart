import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math
from io import BytesIO
import asyncio
from concurrent.futures import ThreadPoolExecutor
from .storage import save_chart_image
import matplotlib

from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patheffects import withStroke

matplotlib.use('Agg')  # 非交互式后端
plt.rcParams.update({
    'font.family': ['DejaVu Sans', 'SimSun'],  # 同时支持符号和中文
    'axes.unicode_minus': False,
    'font.sans-serif': ['SimSun', 'DejaVu Sans', 'STIXGeneral'],  # 调整优先级
})

# 星座背景颜色 - 添加星座元素色彩
ZODIAC_COLORS = {
    "Aries": "#FFECEC",      # 火相星座 - 淡红
    "Leo": "#FFF0E0",        # 火相星座 - 淡橙
    "Sagittarius": "#FFF8E0", # 火相星座 - 淡黄
    
    "Taurus": "#E0FFE0",     # 土相星座 - 淡绿
    "Virgo": "#E8FFE8",      # 土相星座 - 淡绿
    "Capricorn": "#E0F0E0",  # 土相星座 - 淡绿灰
    
    "Gemini": "#E0E0FF",     # 风相星座 - 淡蓝
    "Libra": "#E8E8FF",      # 风相星座 - 淡蓝
    "Aquarius": "#E0E8FF",   # 风相星座 - 淡蓝
    
    "Cancer": "#E0F0FF",     # 水相星座 - 淡蓝紫
    "Scorpio": "#E8E0FF",    # 水相星座 - 淡紫
    "Pisces": "#F0E0FF",     # 水相星座 - 淡紫粉
}

# 图表颜色配置
COLORS = {
    "Sun": "#FFA500",  # 橙色
    "Moon": "#FFA500",  # 橙色
    "Mercury": "#9932CC",  # 紫色
    "Venus": "#00FF00",  # 绿色
    "Mars": "#FF0000",  # 红色
    "Jupiter": "#ADD8E6",  # 浅蓝色
    "Saturn": "#A52A2A",  # 棕色
    "Uranus": "#00FFFF",  # 青色
    "Neptune": "#0000FF",  # 蓝色
    "Pluto": "#800080",  # 紫色
    "ASC": "#FF1493",  # 粉色
    "MC": "#FF1493",  # 粉色
    "DESC": "#FF1493",  # 粉色
    "IC": "#FF1493",  # 粉色
}

ASPECT_STYLES = {
    0: {"color": "#9370DB", "style": "-", "alpha": 0.7},    # 合相 - 紫色
    180: {"color": "#FF4500", "style": "--", "alpha": 0.7}, # 对冲 - 红橙色
    120: {"color": "#4CAF50", "style": "-", "alpha": 0.7},  # 三分相 - 绿色
    90: {"color": "#FF8C00", "style": ":", "alpha": 0.7},   # 四分相 - 橙色
    60: {"color": "#6495ED", "style": "-", "alpha": 0.7},   # 六分相 - 蓝色
}

# 星座符号
ZODIAC_SYMBOLS = {
    "Aries": "♈",
    "Taurus": "♉",
    "Gemini": "♊",
    "Cancer": "♋",
    "Leo": "♌",
    "Virgo": "♍",
    "Libra": "♎",
    "Scorpio": "♏",
    "Sagittarius": "♐",
    "Capricorn": "♑",
    "Aquarius": "♒",
    "Pisces": "♓"
}

# 星座中文名称
ZODIAC_NAMES_CN = {
    "Aries": "白羊座",
    "Taurus": "金牛座",
    "Gemini": "双子座",
    "Cancer": "巨蟹座",
    "Leo": "狮子座",
    "Virgo": "处女座",
    "Libra": "天秤座",
    "Scorpio": "天蝎座",
    "Sagittarius": "射手座",
    "Capricorn": "摩羯座",
    "Aquarius": "水瓶座",
    "Pisces": "双鱼座"
}

PLANET_SYMBOLS = {
    "Sun": "☉",
    "Moon": "☽",
    "Mercury": "☿",
    "Venus": "♀",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
    "URANUS": "♅",
    "NEPTUNE": "♆",
    "PLUTO": "♇",
    "North Node": "NN",
    "South Node": "SN",
    "ASC": "ASC",
    "MC": "MC",
    "DESC": "DESC",
    "IC": "IC"
}

# 行星中文名称
PLANET_NAMES_CN = {
    "Sun": "太阳",
    "Moon": "月亮",
    "Mercury": "水星",
    "Venus": "金星",
    "Mars": "火星",
    "Jupiter": "木星",
    "Saturn": "土星",
    "URANUS": "天王星",
    "NEPTUNE": "海王星",
    "PLUTO": "冥王星",
    "North Node": "北交点",
    "South Node": "南交点",
    "ASC": "上升",
    "MC": "天顶",
    "DESC": "下降",
    "IC": "天底"
}

ASPECT_TYPES = {
    0: "合相 (0°)",
    180: "对冲 (180°)",
    120: "三分相 (120°)",
    90: "四分相 (90°)",
    60: "六分相 (60°)"
}

async def generate_chart_image(chart_data):
    """异步生成星盘图片并保存到本地"""
    # 为图表创建唯一ID
    chart_id = f"{chart_data['name']}_{chart_data.get('birth_time', '').replace(':', '-')}"
    filename = f"{chart_id}.png"

    # 使用线程池执行CPU密集型图片生成
    with ThreadPoolExecutor() as executor:
        image_data = await asyncio.get_event_loop().run_in_executor(
            executor,
            _create_chart_image,
            chart_data,
            1200, 1200
        )

    # 保存到本地存储
    image_url = await save_chart_image(image_data, filename)

    return image_url

def _create_chart_image(chart_data, width, height):
    """创建星盘图像 - 旋转180度，天顶在上方，神秘风格"""
    # 创建图像，使用深色背景增强神秘感
    fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
    
    # 创建深蓝色到紫色的渐变背景
    background = np.array([[0, 0], [0, 1]])
    cmap = LinearSegmentedColormap.from_list('mystical_bg', ['#0A0A2A', '#191970', '#483D8B'])
    ax.imshow(background, cmap=cmap, interpolation='bicubic', extent=[-1.3, 1.3, -1.3, 1.3], alpha=0.9)
    
    # 设置圆形图表
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect("equal")
    ax.axis('off')
    
    # 添加随机星星点缀背景
    np.random.seed(42)  # 固定随机种子确保一致的结果
    num_stars = 100
    star_positions = np.random.uniform(-1.2, 1.2, (num_stars, 2))
    star_sizes = np.random.uniform(0.2, 2.0, num_stars)
    star_alphas = np.random.uniform(0.3, 0.8, num_stars)
    
    for (x, y), size, alpha in zip(star_positions, star_sizes, star_alphas):
        # 避免与主星盘重叠
        dist_from_center = np.sqrt(x**2 + y**2)
        if dist_from_center > 1.05:
            ax.plot(x, y, 'o', color='white', markersize=size, alpha=alpha)
    
    # 绘制外圆 - 金色
    outer_circle = plt.Circle((0, 0), 1, fill=False, linewidth=2.5, color='#FFD700', alpha=0.8)
    ax.add_patch(outer_circle)
    
    # 装饰性外环
    decorative_circle = plt.Circle((0, 0), 1.05, fill=False, linewidth=1, color='#FFD700', alpha=0.5)
    ax.add_patch(decorative_circle)

    # 绘制内圆（宫位圈）- 淡金色
    house_circle = plt.Circle((0, 0), 0.7, fill=False, linewidth=1.5, color='#FFD700', alpha=0.6)
    ax.add_patch(house_circle)

    # 绘制中心圈 - 明亮的金色
    inner_circle = plt.Circle((0, 0), 0.1, fill=True, linewidth=1.5, color='#FFD700', alpha=0.2)
    ax.add_patch(inner_circle)
    inner_circle_border = plt.Circle((0, 0), 0.1, fill=False, linewidth=1, color='#FFD700', alpha=0.8)
    ax.add_patch(inner_circle_border)

    # 获取上升点位置（如果有）
    asc_lon = 0  # 默认值
    if 'angles' in chart_data and 'ASC' in chart_data['angles']:
        asc_lon = chart_data['angles']['ASC']['longitude']
    
    # 获取MC位置 - 用于定位天顶
    mc_lon = 0
    if 'angles' in chart_data and 'MC' in chart_data['angles']:
        mc_lon = chart_data['angles']['MC']['longitude']
    
    # 调整角度，使MC位于顶部（旋转180度）
    angle_adjustment = 270 - (mc_lon - asc_lon)

    # 绘制黄道带（十二星座）- 从上升点开始，逆时针方向，并考虑旋转
    zodiac_positions = {}
    for i, sign in enumerate(ZODIAC_SYMBOLS.keys()):
        # 计算星座起始位置（考虑上升点和旋转）
        start_angle = (i * 30 - asc_lon + angle_adjustment + 360) % 360
        end_angle = (start_angle + 30) % 360
        
        # 确保起始角度小于结束角度（用于绘制扇形）
        if end_angle < start_angle:
            end_angle += 360
            
        # 用星座元素色彩填充扇区背景
        sign_color = ZODIAC_COLORS.get(sign, "#F8F8FF")  # 默认为雪白色
        wedge_bg = patches.Wedge((0, 0), 1, start_angle, end_angle, width=0.3,
                              fc=sign_color, alpha=0.2, linewidth=0)
        ax.add_patch(wedge_bg)
        
        # 绘制扇形边界
        wedge = patches.Wedge((0, 0), 1, start_angle, end_angle, width=0.3,
                              fill=False, linewidth=1, edgecolor='#FFD700', alpha=0.8)
        ax.add_patch(wedge)

        # 添加星座符号
        angle_rad = math.radians(start_angle + 15)
        x = 0.85 * math.cos(angle_rad)
        y = 0.85 * math.sin(angle_rad)
        symbol_text = ax.text(x, y, ZODIAC_SYMBOLS[sign], fontsize=16, ha='center', va='center', 
                             color='white', weight='bold')
        symbol_text.set_path_effects([withStroke(linewidth=2, foreground='#FFD700')])
        
        # 添加星座中文名称
        angle_rad = math.radians(start_angle + 15)
        x = 0.95 * math.cos(angle_rad)
        y = 0.95 * math.sin(angle_rad)
        cn_text = ax.text(x, y, ZODIAC_NAMES_CN[sign], fontsize=8, ha='center', va='center',
                         color='white', alpha=0.9)
        cn_text.set_path_effects([withStroke(linewidth=1, foreground='#000000', alpha=0.5)])
        
        # 记录星座位置
        zodiac_positions[sign] = (start_angle, end_angle)

    # 绘制宫位线和标签
    houses = chart_data['houses']
    for i in range(1, 13):
        house_key = f"house_{i}"
        if house_key in houses:
            house_lon = houses[house_key]['longitude']
            # 调整角度（考虑上升点和旋转）
            adjusted_angle = (house_lon - asc_lon + angle_adjustment + 360) % 360
            angle_rad = math.radians(adjusted_angle)
            
            # 绘制宫位线 - 使用金色半透明
            ax.plot([0, math.cos(angle_rad)], [0, math.sin(angle_rad)], '-', color='#FFD700', 
                   linewidth=1, alpha=0.6)
            
            # 添加宫位标签 - 带发光效果
            label_radius = 0.6
            x = label_radius * math.cos(angle_rad)
            y = label_radius * math.sin(angle_rad)
            house_text = ax.text(x, y, str(i), fontsize=10, ha='center', va='center', color='white',
                   bbox=dict(facecolor='#191970', alpha=0.7, edgecolor='#FFD700', boxstyle='circle,pad=0.2'))
            house_text.set_path_effects([withStroke(linewidth=1, foreground='#FFD700', alpha=0.6)])
    
    # 绘制行星
    planets = chart_data['planets']
    angles = chart_data.get('angles', {})
    
    # 合并行星和角度点
    all_points = {}
    for planet_name, planet_data in planets.items():
        all_points[planet_name] = planet_data
    
    for angle_name, angle_data in angles.items():
        all_points[angle_name] = angle_data
    
    # 计算行星位置 - 考虑旋转
    planet_positions = {}
    for point_name, point_data in all_points.items():
        if point_name in PLANET_SYMBOLS:
            lon = point_data['longitude']
            # 调整角度（考虑上升点和旋转）
            adjusted_angle = (lon - asc_lon + angle_adjustment + 360) % 360
            angle_rad = math.radians(adjusted_angle)
            radius = 0.4  # 行星放置在中间圆圈
            x = radius * math.cos(angle_rad)
            y = radius * math.sin(angle_rad)

            # 存储位置以检测重叠
            planet_positions[point_name] = (x, y, adjusted_angle, lon, point_data.get('sign_name', ''))
    
    # 解决行星重叠问题
    resolved_positions = _resolve_overlapping_planets(planet_positions)

    # 绘制相位线 - 先绘制相位线再绘制行星，避免行星被线覆盖
    aspects = chart_data['aspects']
    for aspect in aspects:
        p1 = aspect['p1']
        p2 = aspect['p2']

        if p1 in resolved_positions and p2 in resolved_positions:
            x1, y1, _, _, _ = resolved_positions[p1]
            x2, y2, _, _, _ = resolved_positions[p2]

            # 根据相位类型设置线型和颜色
            aspect_type = aspect['type']
            aspect_style = ASPECT_STYLES.get(aspect_type, {"color": "#B0C4DE", "style": ":", "alpha": 0.5})
            
            # 绘制相位线
            ax.plot([x1, x2], [y1, y2], 
                   aspect_style["style"], 
                   color=aspect_style["color"], 
                   alpha=aspect_style["alpha"], 
                   linewidth=1.5)

    # 绘制行星符号和信息
    for planet_name, (x, y, _, lon, sign) in resolved_positions.items():
        if planet_name in PLANET_SYMBOLS:
            color = COLORS.get(planet_name, 'white')
            
            # 绘制行星符号背景圆 - 添加发光效果
            bg_circle = plt.Circle((x, y), 0.035, fill=True, color='#191970', alpha=0.7)
            ax.add_patch(bg_circle)
            edge_circle = plt.Circle((x, y), 0.035, fill=False, color=color, alpha=0.8, linewidth=1)
            ax.add_patch(edge_circle)
            
            # 绘制行星符号 - 带发光效果
            planet_symbol = ax.text(x, y, PLANET_SYMBOLS[planet_name], fontsize=16,
                    ha='center', va='center', color=color, weight='bold')
            planet_symbol.set_path_effects([withStroke(linewidth=1.5, foreground='black', alpha=0.5)])
            
            # 计算行星信息文本位置（稍微偏离行星符号）
            info_angle = math.atan2(y, x)
            info_radius = math.sqrt(x**2 + y**2) + 0.1
            info_x = info_radius * math.cos(info_angle)
            info_y = info_radius * math.sin(info_angle)
            
            # 格式化度数
            deg = int(lon)
            min_val = int((lon - deg) * 60)
            deg_formatted = f"{deg}°{min_val}'"
            
            # 添加行星信息（中文名称、度数、星座）
            planet_info = f"{PLANET_NAMES_CN.get(planet_name, planet_name)}\n{deg_formatted}\n{ZODIAC_NAMES_CN.get(sign, sign)}"
            info_text = ax.text(info_x, info_y, planet_info, fontsize=8, ha='center', va='center', color='white',
                   bbox=dict(facecolor='#191970', alpha=0.8, edgecolor=color, boxstyle='round,pad=0.2'))
            info_text.set_path_effects([withStroke(linewidth=0.5, foreground='black', alpha=0.5)])

    # 添加图表标题
    name = chart_data.get('name', '未命名')
    birth_time = chart_data.get('birth_time', '')
    city = chart_data.get('location', {}).get('city', '')
    title = f"{name} - {birth_time}"
    if city:
        title += f" - {city}"

    title_text = ax.text(0, -1.1, title, fontsize=16, ha='center', weight='bold', color='white')
    title_text.set_path_effects([withStroke(linewidth=2, foreground='#000000', alpha=0.7)])

    # 添加图表说明
    footer_text = ax.text(0, -1.2, "神秘星盘 - 生成时间: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), 
            fontsize=10, ha='center', color='#E6E6FA', alpha=0.8)
    footer_text.set_path_effects([withStroke(linewidth=1, foreground='#000000', alpha=0.5)])

    # 保存图像到内存
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150, facecolor='#0A0A2A')
    buf.seek(0)
    plt.close(fig)

    return buf

def _resolve_overlapping_planets(planet_positions, threshold=0.08):
    """解决行星重叠问题"""
    resolved = {}

    # 按照黄经排序，确保处理顺序一致
    sorted_planets = sorted(planet_positions.items(), key=lambda x: x[1][2])

    for planet_name, (x, y, angle, lon, sign) in sorted_planets:
        # 检查是否与已处理的行星重叠
        overlapping = False
        new_x = x
        new_y = y

        for _, (rx, ry, _, _, _) in resolved.items():
            distance = math.sqrt((x - rx) ** 2 + (y - ry) ** 2)
            if distance < threshold:
                overlapping = True
                break

        if overlapping:
            # 向外移动一点
            angle_rad = math.atan2(y, x)
            radius = math.sqrt(x ** 2 + y ** 2) + 0.08
            new_x = radius * math.cos(angle_rad)
            new_y = radius * math.sin(angle_rad)
        
        resolved[planet_name] = (new_x, new_y, angle, lon, sign)

    return resolved