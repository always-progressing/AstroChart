from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
from flatlib import aspects

# Names
SUN = 'Sun'
MOON = 'Moon'
MERCURY = 'Mercury'
VENUS = 'Venus'
MARS = 'Mars'
JUPITER = 'Jupiter'
SATURN = 'Saturn'
URANUS = 'Uranus'
NEPTUNE = 'Neptune'
PLUTO = 'Pluto'
CHIRON = 'Chiron'
NORTH_NODE = 'North Node'
SOUTH_NODE = 'South Node'
SYZYGY = 'Syzygy'
PARS_FORTUNA = 'Pars Fortuna'
NO_PLANET = 'None'

LIST_OBJECTS_1 = [
    SUN, MOON, MERCURY, VENUS, MARS, JUPITER, SATURN, 
    NORTH_NODE,
    SOUTH_NODE, SYZYGY, PARS_FORTUNA,
]

# 转换经纬度格式（如从39.9042 -> 39n54）
def decimal_to_dms(decimal_degrees, is_latitude):
    degrees = int(decimal_degrees)
    minutes = round((decimal_degrees - degrees) * 60)
    direction = ''
    if is_latitude:
        direction = 'n' if degrees >= 0 else 's'
    else:
        direction = 'e' if degrees >= 0 else 'w'
    return f"{abs(degrees)}{direction}{minutes:02d}"


def compute_astrology(birth_data):
    """
    计算完整的星盘数据：
    包括行星位置、宫位、相位、四大尖轴、交点
    """
    # 1. 基本设置
    date_str = f"{birth_data.birth_date.year}/{birth_data.birth_date.month}/{birth_data.birth_date.day}"
    time_str = f"{birth_data.birth_date.hour}:{birth_data.birth_date.minute}"
    utcoffset_str = f"{birth_data.utcoffset}:00"
    
    date = Datetime(date_str, time_str, utcoffset_str)

    latitude_str = decimal_to_dms(birth_data.latitude, True)
    longitude_str = decimal_to_dms(birth_data.longitude, False)

    pos = GeoPos(latitude_str, longitude_str)
    
    

    # 2. 创建星盘
    chart = Chart(date, pos)

    # 3. 获取行星位置
    planets_data ={}
    for planet_name in LIST_OBJECTS_1:
        planet = chart.getObject(planet_name)
        planets_data[planet_name] = {
            "sign": planet.sign,
            "longitude": planet.lon,
            "latitude": planet.lat,
            # "sign_name": planet.sign,
            # "house": planet.house,
            "movement": planet.movement()
        }

    # 4. 获取宫位信息
    houses_data = {}
    houses = list(chart.houses)
    for house_num in range(0, 12):
        house = houses[house_num]
        houses_data[f"house_{house_num+1}"] = {
            "longitude": house.lon,
            "sign": house.sign,
            # "sign_name": const.LIST_SIGNS[house.sign_num]
        }
    
    # 5. 计算相位
    objects = list(chart.objects)
    # houses = list(chart.houses)
    angles = list(chart.angles)
    # all_objects = objects + houses + angles
    all_objects = objects + angles

    # 定义相位类型列表（这里使用主要相位）
    aspList = const.MAJOR_ASPECTS

    aspects_data = []
    for i in range(len(all_objects)):
        for j in range(i + 1, len(all_objects)):
            obj1 = all_objects[i]
            obj2 = all_objects[j]
            # 检查是否存在相位且在容许度范围内
            if aspects.hasAspect(obj1, obj2, aspList) and aspects.isAspecting(obj1, obj2, aspList):
                aspect = aspects.getAspect(obj1, obj2, aspList)
                aspects_data.append({
                        'p1': obj1.id,
                        'p2': obj2.id,
                        'type': aspect.type,
                        'orb': f"{aspect.orb:.2f}°"
                    })
    
    # 6. 获取四大尖轴（ASC，MC，DSC，IC）
    angles_data = {
        "ASC": {
            "longitude": chart.getAngle(const.ASC).lon,
            "sign": chart.getAngle(const.ASC).sign,
        },
        "MC": {
            "longitude": chart.getAngle(const.MC).lon,
            "sign": chart.getAngle(const.MC).sign,
        },
        "DESC": {
            "longitude": chart.getAngle(const.DESC).lon,
            "sign": chart.getAngle(const.DESC).sign,
        },
        "IC": {
            "longitude": chart.getAngle(const.IC).lon,
            "sign": chart.getAngle(const.IC).sign,
        }
    }
    
    # 7. 获取北交点和南交点
    nodes_data = {
        "North Node": planets_data.get("North Node", {}),
        "South Node": planets_data.get("South Node", {})
    }

    # 8. 组合所有数据
    result = {
        "name": birth_data.name,
        "birth_time": birth_data.birth_date.isoformat(),
        "location": {
            "latitude": birth_data.latitude,
            "longitude": birth_data.longitude,
            "city": birth_data.city
        },
        "planets": planets_data,
        "houses": houses_data,
        "aspects": aspects_data,
        "angles": angles_data,
        "nodes": nodes_data
    }

    return result
