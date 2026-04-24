import streamlit as st
from datetime import datetime
import requests
from urllib.parse import quote

# --- 1. 内置常用机场数据库 ---
AIRPORTS = {
    "北京": ["北京首都国际机场 (PEK)", "北京大兴国际机场 (PKX)"],
    "上海": ["上海浦东国际机场 (PVG)", "上海虹桥国际机场 (SHA)"],
    "广州": ["广州白云国际机场 (CAN)"],
    "深圳": ["深圳宝安国际机场 (SZX)"],
    "西安": ["西安咸阳国际机场 (XIY)"],
    "成都": ["成都双流国际机场 (CTU)", "成都天府国际机场 (TFU)"],
    "杭州": ["杭州萧山国际机场 (HGH)"],
    "重庆": ["重庆江北国际机场 (CKG)"],
    "厦门": ["厦门高崎国际机场 (XMN)"],
    "吉隆坡": ["吉隆坡国际机场 T1 (KUL)", "吉隆坡国际机场 T2 (KUL)"],
    "曼谷": ["素万那普国际机场 (BKK)", "廊曼国际机场 (DMK)"],
    "东京": ["成田国际机场 (NRT)", "东京羽田机场 (HND)"],
    "大阪": ["关西国际机场 (KIX)"],
    "首尔": ["仁川国际机场 (ICN)", "金浦国际机场 (GMP)"],
    "新加坡": ["新加坡樟宜机场 (SIN)"],
    "伦敦": ["希思罗机场 (LHR)"],
    "巴黎": ["戴高乐机场 (CDG)"]
}

def get_airports(city_name):
    if not city_name:
        return []
    for key in AIRPORTS:
        if key in city_name:
            return AIRPORTS[key]
    return []

# --- 2. 天气缓存机制 (4小时刷新一次) ---
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
    except:
        return None

# --- 3. 界面美化 (全中文大字版) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFE4E1 !important; }
    .stCheckbox label { font-size: 30px !important; color: black !important; font-weight: bold; padding: 10px 0; }
    h1 { color: #D02090 !important; font-size: 45px !important; text-align: center; font-weight: 900; }
    h3 { color: #D02090 !important; font-size: 32px !important; border-bottom: 2px solid #FFB6C1; padding-bottom: 10px; }
    p, label, div { font-size: 24px !important; color: black !important; font-weight: bold; }
    /* 让下拉菜单的字也变大 */
    .stSelectbox label, .stTextInput label { font-size: 26px !important; }
    div[data-baseweb="select"] { font-size: 24px !important; }
    .stInfo, .stSuccess, .stWarning, .stError { background-color: #FFF0F5 !important; border: 3px solid #FFB6C1; font-size: 24px !important; color: #D02090 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌸 旅行贴身管家")
st.write("✨ 亲爱的，祝您拥有一个愉快的旅程！")

# --- 4. 核心逻辑 ---
st.subheader("📍 第一步：确认行程")

travel_type = st.radio("旅行类型", ["国内旅行", "国外旅行"], horizontal=True)

col1, col2 = st.columns(2)
with col1:
    dep_city = st.text_input("出发城市", placeholder="例如：西安")
with col2:
    dep_options = get_airports(dep_city)
    if dep_options:
        dep_airport = st.selectbox("出发机场", dep_options)
    else:
        dep_airport = st.text_input("出发机场", placeholder="输入机场名 (选填)")

col3, col4 = st.columns(2)
with col3:
    arr_city = st.text_input("目的城市", placeholder="例如：吉隆坡")
with col4:
    arr_options = get_airports(arr_city)
    if arr_options:
        arr_airport = st.selectbox("到达机场", arr_options)
    else:
        arr_airport = st.text_input("到达机场", placeholder="输入机场名 (选填)")

# --- 重点修改：全中文大号下拉菜单选日期 ---
st.write("---")
st.subheader("📅 第二步：出发日期")
st.write("请选择您的出发时间：")

# 获取今天的日期作为默认值
today = datetime.now()

col_y, col_m, col_d = st.columns(3)
with col_y:
    year_val = st.selectbox("年份", ["2026年", "2027年"], index=0)
with col_m:
    month_val = st.selectbox("月份", [f"{i}月" for i in range(1, 13)], index=today.month - 1)
with col_d:
    day_val = st.selectbox("日期", [f"{i}日" for i in range(1, 32)], index=today.day - 1)

# 组合日期并计算倒计时
try:
    y = int(year_val.replace("年", ""))
    m = int(month_val.replace("月", ""))
    d = int(day_val.replace("日", ""))
    travel_date = datetime(y, m, d).date()
    
    days_left = (travel_date - today.date()).days
    if days_left > 0:
        st.success(f"🎊 距离出发还有 {days_left} 天，请做好准备！")
    elif days_left == 0:
        st.success("✈️ 就是今天！出发喽！")
    else:
        st.warning("⚠️ 您选择的日期已经过去啦，请检查一下是否选错了。")
except ValueError:
    # 防止选出 2月30日 这种不存在的日期
    st.error("❌ 您选择的日期不存在（例如2月30日），请重新选择。")

# 自动获取目的地天气 (带缓存)
if arr_city:
    st.write("---")
    st.subheader("☀️ 第三步：当地天气")
    with st.spinner("正在获取最新天气..."):
        weather_info = get_weather(arr_city)
        if weather_info:
            st.info(f"✨ **{arr_city}** 实时预报：{weather_info}。")
        else:
            st.info(f"✨ 暂时无法获取 {arr_city} 的天气，请留意气温变化。")

# --- 5. 行李清单 ---
st.write("---")
st.subheader("🎒 第四步：整理行李")
st.write("（请每收拾好一样，就在方框点一下）")

list_a = ["身份证", "充电器", "衣物", "一次性马桶垫", "洗漱用品", "药品", "眼镜/墨镜", "水杯"]
list_b = ["护照", "签证", "充电器", "衣物", "一次性马桶垫", "洗漱用品", "药品", "眼镜/墨镜", "水杯", "转化插头", "电话漫游"]

current_list = list_b if travel_type == "国外旅行" else list_a

checked_count = 0
for item in current_list:
    if st.checkbox(f"✔️ {item}", key=f"check_{item}"):
        checked_count += 1

if checked_count == len(current_list):
    st.balloons()
    st.markdown("""
        <div style="background-color: #FF69B4; padding: 20px; border-radius: 15px; border: 5px solid #FF1493; text-align: center;">
            <h2 style="color: white; margin: 0;">🎉 恭喜您！</h2>
            <p style="color: white; font-size: 28px !important; font-weight: bold; margin-top: 10px;">
                行前准备已全部完成！<br>期待一个美好的旅途！
            </p>
        </div>
        """, unsafe_allow_html=True)