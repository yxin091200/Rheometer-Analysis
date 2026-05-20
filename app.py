import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 设置页面布局
st.set_page_config(page_title="流变仪测试数据对比工具", layout="wide")
st.title("流变仪材料测试数据对比分析")


# 2. 加载数据 (修改为：动态读取外部同级目录下的 Excel 文件)
@st.cache_data
def load_data():
    import os
    import sys

    # 1. 核心逻辑：动态判断当前是代码运行环境还是打包后的单文件环境
    if getattr(sys, 'frozen', False):
        # 如果是打包后的 EXE 环境，sys.executable 获取的是 exe 的绝对路径
        current_dir = os.path.dirname(sys.executable)
    else:
        # 如果是平时本地直接运行代码的环境
        current_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. 拼接外部 Excel 文件的绝对路径
    file_name = os.path.join(current_dir, "自研流变仪材料测试数据.xlsx")

    # 3. 增加一个友好的防错和指引提示
    if not os.path.exists(file_name):
        st.error("⚠️ 找不到数据源文件！")
        st.markdown(f"请确保 **【自研流变仪材料测试数据.xlsx】** 已经放在与本程序**相同的文件夹**下。")
        st.info(f"程序当前检测的路径为：`{file_name}`")
        st.stop()  # 找不到文件时拦截后续运行，避免崩溃

    df = pd.read_excel(file_name)
    return df

df = load_data()

# 3. 侧边栏：选择对比模式
st.sidebar.header("🛠️ 控制面板")
mode = st.sidebar.radio(
    "请选择您的对比模式：",
    ("同一材料 ➔ 对比不同转子", "同一转子 ➔ 对比不同材料")
)

# 4. 根据模式渲染主界面
if mode == "同一材料 ➔ 对比不同转子":
    st.subheader("🔹 同一材料，对比不同转子")

    # 提取所有去重后的材料名称并让用户选择
    materials = df['材料名称'].unique()
    selected_material = st.selectbox("📌 请选择要分析的材料名称:", materials)

    # 过滤出选中材料的数据
    filtered_df = df[df['材料名称'] == selected_material]

    # 绘制动态折线图
    fig = px.line(
        filtered_df,
        x='磁场（T）',
        y='扭矩（mNm）',
        color='平行杆',
        markers=True,
        title=f"【{selected_material}】在不同转子下的扭矩对比",
        labels={'平行杆': '转子类型 (平行杆)', '磁场（T）': '磁场（T）', '扭矩（mNm）': '扭矩（mNm）'},
    )

    # 调整线条粗细与数据点大小
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )

    # 调整坐标轴与字体大小
    fig.update_layout(
        hovermode="x unified",
        font=dict(size=14),
        xaxis=dict(
            title="磁场（T）",
            title_font=dict(size=18, family="Arial, sans-serif"),
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            title="扭矩（mNm）",
            title_font=dict(size=18, family="Arial, sans-serif"),
            tickfont=dict(size=14)
        )
    )

    # 只保留这一次渲染
    st.plotly_chart(fig, width='stretch')


elif mode == "同一转子 ➔ 对比不同材料":
    st.subheader("🔸 同一转子，对比不同材料")

    # 提取所有去重后的转子名称并让用户选择
    rotors = df['平行杆'].unique()
    selected_rotor = st.selectbox("📌 请选择要分析的转子类型:", rotors)

    # 过滤出选中转子的数据
    filtered_df = df[df['平行杆'] == selected_rotor]

    # 绘制动态折线图
    fig = px.line(
        filtered_df,
        x='磁场（T）',
        y='扭矩（mNm）',
        color='材料名称',
        markers=True,
        title=f"转子【{selected_rotor}】在不同材料下的扭矩对比",
        labels={'材料名称': '材料类型', '磁场（T）': '磁场（T）', '扭矩（mNm）': '扭矩（mNm）'}
    )

    # 调整线条粗细与数据点大小
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )

    # 调整坐标轴与字体大小
    fig.update_layout(
        hovermode="x unified",
        font=dict(size=14),
        xaxis=dict(
            title="磁场（T）",
            title_font=dict(size=18, family="Arial, sans-serif"),
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            title="扭矩（mNm）",
            title_font=dict(size=18, family="Arial, sans-serif"),
            tickfont=dict(size=14)
        )
    )

    # 只保留这一次渲染
    st.plotly_chart(fig, width='stretch')

# # 5. 在底部展示对应的数据表，方便核对原始数据
# st.divider()
# st.write("📄 **当前图表对应的数据明细：**")

# 方法 A：使用 st.table（最稳定，但如果数据上千行页面会变很长）
# 为了防止数据为空导致报错，加一个简单的判断
if not filtered_df.empty:
    st.table(filtered_df.astype(str))
else:
    st.info("当前选择的条件下没有数据。")

# --- 如果您觉得 st.table 太长不好看，可以把上面的代码删掉，换成下面的方法 B ---

# # 方法 B（推荐）：使用 Pandas 自带的 HTML 渲染功能，稳定且排版整齐
# if not filtered_df.empty:
#     # 将 DataFrame 转换为 HTML 表格字符串，并去掉索引
#     html_table = filtered_df.to_html(index=False, classes='table table-striped')
#     # 使用 st.markdown 直接渲染 HTML
#     st.markdown(html_table, unsafe_allow_html=True)
# else:
#     st.info("当前选择的条件下没有数据。")

##  python -m streamlit run data.py