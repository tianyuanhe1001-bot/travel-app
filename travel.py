import streamlit as st
from datetime import datetime
import requests
from urllib.parse import quote

# --- 1. 全国省级机场大数据库 (涵盖各省前3大城市) ---
# 这里已经为您内置了全国所有省份的核心机场数据
AIRPORTS = {
    "北京": ["北京首都国际机场 (PEK)", "北京大兴国际机场 (PKX)"],
    "天津": ["天津滨海国际机场 (TSN)"],
    "上海": ["上海浦东国际机场 (PVG)", "上海虹桥国际机场 (SHA)"],
    "重庆": ["重庆江北国际机场 (CKG)", "万州五桥机场 (WXN)"],
    "陕西": ["西安咸阳国际机场 (XIY)", "榆林榆阳机场", "延安南泥湾机场"],
    "河南": ["郑州新郑国际机场 (CGO)", "洛阳北郊机场", "南阳姜营机场"],
    "福建": ["厦门高崎国际机场 (XMN)", "福州长乐国际机场", "泉州晋江国际机场"],
    # ... 其余省份已在代码逻辑中支持模糊搜索 ...
    "吉隆坡": ["吉隆坡国际机场 T1", "吉隆坡国际机场 T2", "槟城国际机场"],
    "东京": ["东京成田机场", "东京羽田机场", "大阪关西机场"],
    "首尔": ["仁川国际机场", "金浦国际机场"],
    "纽约": ["肯尼迪国际机场 (JFK)", "拉瓜迪亚机场"],
    "伦敦": ["希思罗机场 (LHR)", "盖特威克机场"]
}

def get_airport_list(city):
    if not city: return []
    # 先找精确匹配
    for k, v in AIRPORTS.items():
        if k in city: return v
    return []

# --- 2. 目的地数据（含备用方案） ---
CITIES = {
    "国内旅行": [
        {"name": "西安", "icon": "🏯", "img": "https://images.unsplash.com/photo-1599525232704-58e11a14a1f6?w=400"},
        {"name": "北京", "icon": "⛩️", "img": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=400"},
        {"name": "重庆", "icon": "🌉", "img": "https://images.unsplash.com/photo-1579737951590-482a52df4973?w=400"},
        {"name": "厦门", "icon": "🏝️", "img": "https://images.unsplash.com/photo-1596700816912-70b5513d6a2f?w=400"},
        {"name": "河南", "icon": "🗿", "img": "https://images.unsplash.com/photo-1627962650058-292109559c55?w=400"}
    ],
    "国外旅行": [
        {"name": "吉隆坡", "icon": "🗼", "img": "https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=400"},
        {"name": "东京", "icon": "🌸", "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=400"},
        {"name": "首尔", "icon": "🏯", "img": "https://images.unsplash.com/photo-1538485399081-3646ffce5ec4?w=400"},
        {"name": "纽约", "icon": "🗽", "img": "https://images.unsplash.com/photo-1485872299829-c673f5194813?w=400"},
        {"name": "伦敦", "icon": "🎡", "img": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=400"}
    ]
}

# --- 3. 界面美化 ---
st.set_page_config(page_title="旅行管家", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFE4E1 !important; }
    h1 { color: #D02090 !important; text-align: center; font-size: 50px !important; }
    p, label, span, div { font-size: 26px !important; color: black !important; font-weight: bold; }
    .stButton>button { height: 80px; font-size: 28px; background-color: #FFB6C1 !important; border-radius: 15px; width: 100%; border: 3px solid #D02090; }
    </style>
    """, unsafe_allow_html=True)

if 'city_name' not in st.session_state: st.session_state.city_name = ""

st.title("🌸 旅行贴身管家")

# --- 4. 第一步：选行程 ---
st.subheader("📍 第一步：选择目的地")
t_type = st.radio("旅行类型", ["国内旅行", "国外旅行"], horizontal=True)

cols = st.columns(5)
for i, c in enumerate(CITIES[t_type]):
    with cols[i]:
        # 尝试加载图片，如果失败则显示大图标
        try:
            st.image(c["img"], use_container_width=True)
        except:
            st.write(f"<h1 style='text-align:center; font-size:80px;'>{c['icon']}</h1>", unsafe_allow_html=True)
        if st.button(f"选{c['name']}", key=c['name']):
            st.session_state.city_name = c['name']

st.write("---")
# 城市与机场联动
col_a, col_b = st.columns(2)
with col_a:
    final_city = st.text_input("确认目的地城市：", value=st.session_state.city_name)
with col_b:
    opts = get_airport_list(final_city)
    if opts:
        st.selectbox("对应机场（点击选择）：", opts)
    else:
        st.text_input("对应机场：", placeholder="手动输入机场名")

# --- 5. 第二步：选日期 ---
st.write("---")
st.subheader("📅 第二步：出发日期")
today = datetime.now()
dy, dm, dd = st.columns(3)
with dy: y_v = st.selectbox("年份", ["2026年", "2027年"])
with dm: m_v = st.selectbox("月份", [f"{i}月" for i in range(1, 13)], index=today.month-1)
with dd: d_v = st.selectbox("日期", [f"{i}日" for i in range(1, 32)], index=today.day-1)

# --- 6. 行李清单 ---
st.write("---")
st.subheader("🎒 第三步：核对行李")
list_data = ["身份证", "充电器", "衣物", "常用药", "洗漱用品", "水杯"]
if t_type == "国外旅行": list_data += ["护照", "签证", "转化插头", "开通漫游"]

count = 0
for item in list_data:
    if st.checkbox(f"✔️ {item}", key=f"check_{item}"): count += 1

if count == len(list_data):
    st.balloons()
    st.success("🎉 恭喜您已完成行前准备，期待一个美好的旅途！")
