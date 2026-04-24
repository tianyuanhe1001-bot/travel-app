import streamlit as st
from datetime import datetime
import requests
from urllib.parse import quote

# --- 1. 全国省级机场大数据库 (涵盖各省前3大城市) ---
# 这个数据直接写在代码里，不需要联网，点击秒关联
AIRPORTS = {
    # 直辖市
    "北京": ["北京首都国际机场 (PEK)", "北京大兴国际机场 (PKX)"],
    "上海": ["上海浦东国际机场 (PVG)", "上海虹桥国际机场 (SHA)"],
    "天津": ["天津滨海国际机场 (TSN)"],
    "重庆": ["重庆江北国际机场 (CKG)", "万州五桥机场 (WXN)", "黔江武陵山机场 (JIQ)"],
    
    # 华东地区
    "江苏": ["南京禄口国际机场", "无锡硕放国际机场", "徐州观音国际机场"],
    "浙江": ["杭州萧山国际机场", "宁波栎社国际机场", "温州龙湾国际机场"],
    "安徽": ["合肥新桥国际机场", "芜湖宣州机场", "安庆天柱山机场"],
    "福建": ["厦门高崎国际机场", "福州长乐国际机场", "泉州晋江国际机场"],
    "江西": ["南昌昌北国际机场", "赣州黄金机场", "九江庐山机场"],
    "山东": ["青岛胶东国际机场", "济南遥墙国际机场", "烟台蓬莱国际机场"],
    
    # 华南地区
    "广东": ["广州白云国际机场", "深圳宝安国际机场", "珠海金湾机场"],
    "广西": ["南宁吴圩国际机场", "桂林两江国际机场", "柳州白莲机场"],
    "海南": ["海口美兰国际机场", "三亚凤凰国际机场", "琼海博鳌机场"],
    
    # 华中地区
    "湖北": ["武汉天河国际机场", "宜昌三峡机场", "襄阳刘集机场"],
    "湖南": ["长沙黄花国际机场", "张家界荷花国际机场", "常德桃花源机场"],
    "河南": ["郑州新郑国际机场", "洛阳北郊机场", "南阳姜营机场"],
    
    # 华北地区
    "河北": ["石家庄正定国际机场", "邯郸机场", "秦皇岛北戴河机场"],
    "山西": ["太原武宿国际机场", "运城张孝机场", "大同云冈机场"],
    "内蒙古": ["呼和浩特白塔国际机场", "包头东河机场", "鄂尔多斯伊金霍洛机场"],
    
    # 西北地区
    "陕西": ["西安咸阳国际机场", "榆林榆阳机场", "延安南泥湾机场"],
    "甘肃": ["兰州中川国际机场", "敦煌莫高国际机场", "庆阳机场"],
    "青海": ["西宁曹家堡国际机场", "格尔木机场", "玉树巴塘机场"],
    "宁夏": ["银川河东国际机场", "中卫沙坡头机场", "固原六盘山机场"],
    "新疆": ["乌鲁木齐地窝堡国际机场", "喀什徕宁国际机场", "伊宁机场"],
    
    # 西南地区
    "四川": ["成都天府国际机场", "成都双流国际机场", "绵阳南郊机场"],
    "贵州": ["贵阳龙洞堡国际机场", "遵义新舟机场", "铜仁凤凰机场"],
    "云南": ["昆明长水国际机场", "丽江三义国际机场", "西双版纳嘎洒国际机场"],
    "西藏": ["拉萨贡嘎国际机场", "林芝米林机场", "日喀则和平机场"],
    
    # 东北地区
    "辽宁": ["大连周水子国际机场", "沈阳桃仙国际机场", "丹东浪头机场"],
    "吉林": ["长春龙嘉国际机场", "延吉朝阳川国际机场", "白山长白山机场"],
    "黑龙江": ["哈尔滨太平国际机场", "齐齐哈尔三家子机场", "牡丹江海浪机场"],
    
    # 港澳台及国外常用
    "香港": ["香港国际机场 (HKG)"],
    "澳门": ["澳门国际机场 (MFM)"],
    "台湾": ["台北桃园国际机场", "台北松山机场", "高雄小港机场"],
    "马来西亚": ["吉隆坡国际机场 T1", "吉隆坡国际机场 T2", "槟城国际机场"],
    "日本": ["东京成田机场", "东京羽田机场", "大阪关西机场"],
    "韩国": ["首尔仁川机场", "首尔金浦机场", "济州国际机场"],
    "纽约": ["肯尼迪国际机场 (JFK)", "拉瓜迪亚机场 (LGA)"],
    "伦敦": ["希思罗机场 (LHR)", "盖特威克机场 (LGW)"]
}

# 辅助函数：根据输入的城市或省份找机场
def find_airports(text):
    if not text: return []
    res = []
    for key, val in AIRPORTS.items():
        if key in text: # 模糊匹配省份或直辖市
            res.extend(val)
    # 如果没搜到省份，尝试搜城市名（比如输入"南京"）
    if not res:
        for key, val in AIRPORTS.items():
            for airport in val:
                if text in airport: res.append(airport)
    return list(set(res)) # 去重

# --- 2. 天气缓存 (4小时刷新一次) ---
@st.cache_data(ttl=14400)
def get_weather(city):
    try:
        encoded_dest = quote(city)
        weather_url = f"https://wttr.in/{encoded_dest}?format=j1&lang=zh"
        req = requests.get(weather_url, timeout=3)
        req.encoding = 'utf-8'
        res = req.json()
        temp_c = res['current_condition'][0]['temp_C']
        weather_desc = res['current_condition'][0]['lang_zh'][0]['value'] 
        return f"{temp_c}℃，{weather_desc}"
    except: return None

# --- 3. 界面美化 (全中文大字版) ---
st.set_page_config(page_title="旅行贴身管家", layout="wide") # 为了图片排列更整齐
st.markdown("""
    <style>
    .stApp { background-color: #FFE4E1 !important; }
    .stCheckbox label { font-size: 30px !important; color: black !important; font-weight: bold; padding: 10px 0; }
    h1 { color: #D02090 !important; font-size: 45px !important; text-align: center; font-weight: 900; }
    h3 { color: #D02090 !important; font-size: 32px !important; border-bottom: 2px solid #FFB6C1; padding-bottom: 10px; }
    p, label, div { font-size: 26px !important; color: black !important; font-weight: bold; }
    /* 下拉菜单和按钮字体也变大 */
    .stSelectbox label, .stTextInput label { font-size: 26px !important; }
    div[data-baseweb="select"] { font-size: 24px !important; }
    /* 图片下方的选择按钮变大变显眼 */
    .stButton>button { height: 60px; font-size: 24px; background-color: #FF1493 !important; color: white !important; border-radius: 10px; width: 100%; border: none; margin-bottom: 20px;}
    .stInfo, .stSuccess, .stWarning { background-color: #FFF0F5 !important; border: 3px solid #FFB6C1; font-size: 24px !important; color: #D02090 !important; }
    </style>
    """, unsafe_allow_html=True)

# 开启记忆功能，记住长辈点的城市
if 'dest_city_name' not in st.session_state:
    st.session_state.dest_city_name = ""

st.title("🌸 旅行贴身管家")
st.write("✨ 祝您拥有一个愉快的旅程！")

# --- 4. 快捷选择目的地 ---
st.subheader("📍 第一步：快捷选择目的地")
travel_type = st.radio("请选择旅行类型：", ["国内旅行", "国外旅行"], horizontal=True)

# 寻找更加稳定的图片链接，并使用 try...except 防错加载
cities_cn = [
    {"name": "西安", "icon": "🏯", "img": "https://images.unsplash.com/photo-1599525232704-58e11a14a1f6?w=400"},
    {"name": "北京", "icon": "⛩️", "img": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=400"},
    {"name": "重庆", "icon": "🌉", "img": "https://images.unsplash.com/photo-1579737951590-482a52df4973?w=400"},
    {"name": "厦门", "icon": "🏝️", "img": "https://images.unsplash.com/photo-1596700816912-70b5513d6a2f?w=400"},
    {"name": "河南", "icon": "🗿", "img": "https://images.unsplash.com/photo-1627962650058-292109559c55?w=400"}
]
cities_intl = [
    {"name": "吉隆坡", "icon": "🗼", "img": "https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=400"},
    {"name": "东京", "icon": "🌸", "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=400"},
    {"name": "首尔", "icon": "🏯", "img": "https://images.unsplash.com/photo-1538485399081-3646ffce5ec4?w=400"},
    {"name": "纽约", "icon": "🗽", "img": "https://images.unsplash.com/photo-1485872299829-c673f5194813?w=400"},
    {"name": "伦敦", "icon": "🎡", "img": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=400"}
]

st.write("点击下方图片快捷选择目的地。若图片加载慢，请直接点击按钮或在下方输入城市名。")
current_cities = cities_cn if travel_type == "国内旅行" else cities_intl

# 展示快捷图片和按钮
cols = st.columns(5)
for i, city in enumerate(current_cities):
    with cols[i]:
        # 重要调整：添加 Try...Except 并设置统一高度（200px）
        try:
            # 尝试加载图片，并设置固定高度200px
            st.image(city["img"], use_container_width=True, height=200)
        except:
            # 如果加载失败，显示一个大的备用图标，大小也大致统一
            st.write(f"<h1 style='text-align:center; font-size:80px;'>{city['icon']}</h1>", unsafe_allow_html=True)
            st.write(f"<p style='text-align:center;'>图片加载稍慢，已显示图标备选</p>", unsafe_allow_html=True)
        
        # 按钮样式保持不变
        if st.button(f"选【{city['name']}】", key=city['name']):
            st.session_state.dest_city_name = city['name']
            st.rerun() # 强制立刻刷新，让下方输入框马上填入名字

st.write("---")

# --- 5. 行程具体确认 (出发地/目的地输入) ---
st.write("💡 输入城市名后，请按键盘【回车键 (Enter)】或点击空白处，程序才会加载关联信息。")

# 出发地输入栏
col1, col2 = st.columns(2)
with col1:
    dep_city = st.text_input("🛫 出发城市", placeholder="例如：天津")
with col2:
    dep_options = find_airports(dep_city)
    if dep_options:
        dep_airport = st.selectbox("出发机场", dep_options)
    else:
        dep_airport = st.text_input("出发机场", placeholder="输入机场名 (选填)")

# 目的地输入栏 (预填点击选择的城市)
col3, col4 = st.columns(2)
with col3:
    arr_city = st.text_input("🛬 目的城市", value=st.session_state.dest_city_name, placeholder="例如：吉隆坡")
with col4:
    arr_options = get_airports(arr_city)
    if arr_options:
        arr_airport = st.selectbox("到达机场", arr_options)
    else:
        arr_airport = st.text_input("到达机场", placeholder="输入机场名 (选填)")

# --- 6. 出发日期 (全中文下拉菜单) ---
st.write("---")
st.subheader("📅 第二步：出发日期")
today = datetime.now()
col_y, col_m, col_d = st.columns(3)
with col_y:
    year_val = st.selectbox("年份", ["2026年", "2027年"], index=0)
with col_m:
    month_val = st.selectbox("月份", [f"{i}月" for i in range(1, 13)], index=today.month - 1)
with col_d:
    day_val = st.selectbox("日期", [f"{i}日" for i in range(1, 32)], index=today.day - 1)

# 计算倒计时
try:
    y = int(year_val.replace("年", ""))
    m = int(month_val.replace("月", ""))
    d = int(day_val.replace("日", ""))
    travel_date = datetime(y, m, d).date()
    
    days_left = (travel_date - today.date()).days
    if days_left > 0:
        st.success(f"🎊 距离出发还有 {days_left} 天，请做好准备！")
    elif days_left == 0:
        st.success("✈️ 就是今天！祝您一路顺风！")
    else:
        st.warning("⚠️ 您选择的日期已经过去啦，请核对。")
except ValueError:
    # 防止选出 2月30日 这种不存在的日期
    st.error("❌ 您选择的日期不存在（例如2月30日），请重新选择。")

# --- 7. 当地天气 (带缓存，4小时刷新一次) ---
if arr_city:
    st.write("---")
    st.subheader("☀️ 第三步：目的地天气")
    with st.spinner("正在获取当地最新天气..."):
        weather_info = get_weather(arr_city)
        if weather_info:
            st.info(f"✨ **{arr_city}** 实时预报：{weather_info}。")
        else:
            st.info(f"✨ 暂时无法显示 {arr_city} 的具体天气预报，建议您留意当地气温。")

# --- 8. 行李清单 ---
st.write("---")
st.subheader("🎒 第四步：整理行李清单")
st.write("（请把收拾好的一项一项点击打勾）")

list_a = ["身份证", "充电器", "衣物", "常用药", "洗漱用品", "墨镜", "水杯", "拖鞋", "护肤品"]
list_b = ["护照", "签证", "充电器", "衣物", "常用药", "洗漱用品", "墨镜", "水杯", "拖鞋", "护肤品", "转化插头", "开通漫游"]

current_list = list_b if travel_type == "国外旅行" else list_a

checked_count = 0
for item in current_list:
    if st.checkbox(f"✔️ {item}", key=f"check_{item}"):
        checked_count += 1

# 检查是否全部勾选
if checked_count == len(current_list):
    st.balloons() # 燃放气球烟花
    st.markdown('<div style="background-color:#FF69B4;padding:20px;border-radius:15px;text-align:center;color:white;font-size:30px;font-weight:900;">🎉 恭喜您已完成行前准备，祝您拥有一个美好的旅途！</div>', unsafe_allow_html=True)
