import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

# 1. 设置页面布局
st.set_page_config(page_title="流变仪测试数据对比工具", layout="wide")
st.title("流变仪材料测试数据对比分析")


# 2. 加载数据与获取基础路径
def load_data():
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))

    file_name = os.path.join(current_dir, "自研流变仪材料测试数据.xlsx")

    if not os.path.exists(file_name):
        st.error("⚠️ 找不到数据源文件！")
        st.markdown(f"请确保 **【自研流变仪材料测试数据.xlsx】** 已经放在与本程序**相同的文件夹**下。")
        st.info(f"程序当前检测的路径为：`{file_name}`")
        st.stop()

    df = pd.read_excel(file_name)
    return df, current_dir


# 获取数据和当前文件夹路径
df, base_dir = load_data()

# 3. 侧边栏：选择功能模式
st.sidebar.header("🛠️ 控制面板")
mode = st.sidebar.radio(
    "请选择您的功能模式：",
    (
        "📊 同一材料 ➔ 对比不同转子",
        "📊 同一转子 ➔ 对比不同材料",
        "🖼️ 材料耐久测试照片展示"
    )
)

# 4. 根据模式渲染主界面
if mode == "📊 同一材料 ➔ 对比不同转子":
    st.subheader("🔹 同一材料，对比不同转子")

    materials = df['材料名称'].unique()
    selected_material = st.selectbox("📌 步骤一：请选择基础材料名称:", materials)

    available_rotors = df[df['材料名称'] == selected_material]['平行杆'].unique()


    select_all = st.checkbox("🟩 全选所有可对比的转子", value=False)


    default_selection = available_rotors if select_all else []


    selected_rotors = st.multiselect(
        "☑️ 步骤二：请选择需要绘制曲线的转子（可多选）:",
        options=available_rotors,
        default=default_selection
    )

    if not selected_rotors:
        st.info("👆 请在上方勾选或选择“全选”以生成图表和数据明细。")
    else:
        filtered_df = df[(df['材料名称'] == selected_material) & (df['平行杆'].isin(selected_rotors))]


        fig = px.line(
            filtered_df, x='磁场（T）', y='扭矩（mNm）',
            color='平行杆',
            symbol='平行杆',
            line_dash='平行杆',
            markers=True,
            title=f"【{selected_material}】在不同转子下的扭矩对比",
            labels={'平行杆': '转子类型', '磁场（T）': '磁场（T）', '扭矩（mNm）': '扭矩（mNm）'}
        )
        fig.update_traces(line=dict(width=5), marker=dict(size=10))
        fig.update_layout(
            hovermode="x unified", font=dict(size=14),
            xaxis=dict(title="磁场（T）", title_font=dict(size=18, family="Arial, sans-serif"), tickfont=dict(size=14)),
            yaxis=dict(title="扭矩（mNm）", title_font=dict(size=18, family="Arial, sans-serif"), tickfont=dict(size=14))
        )
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.write("📄 **当前勾选项的数据明细：**")
        st.table(filtered_df.astype(str))


elif mode == "📊 同一转子 ➔ 对比不同材料":
    st.subheader("🔸 同一转子，对比不同材料")

    rotors = df['平行杆'].unique()
    selected_rotor = st.selectbox("📌 步骤一：请选择基础转子类型:", rotors)

    available_materials = df[df['平行杆'] == selected_rotor]['材料名称'].unique()

    select_all = st.checkbox("🟩 全选所有可对比的材料", value=False)

    default_selection = available_materials if select_all else []

    # 多选勾选框
    selected_materials = st.multiselect(
        "☑️ 步骤二：请选择需要绘制曲线的材料（可多选）:",
        options=available_materials,
        default=default_selection
    )

    if not selected_materials:
        st.info("👆 请在上方勾选或选择“全选”以生成图表和数据明细。")
    else:
        filtered_df = df[(df['平行杆'] == selected_rotor) & (df['材料名称'].isin(selected_materials))]

        fig = px.line(
            filtered_df, x='磁场（T）', y='扭矩（mNm）',
            color='材料名称',
            symbol='材料名称',
            line_dash='材料名称',
            markers=True,
            title=f"转子【{selected_rotor}】在不同材料下的扭矩对比",
            labels={'材料名称': '材料类型', '磁场（T）': '磁场（T）', '扭矩（mNm）': '扭矩（mNm）'}
        )
        fig.update_traces(line=dict(width=5), marker=dict(size=10))
        fig.update_layout(
            hovermode="x unified", font=dict(size=14),
            xaxis=dict(title="磁场（T）", title_font=dict(size=18, family="Arial, sans-serif"), tickfont=dict(size=14)),
            yaxis=dict(title="扭矩（mNm）", title_font=dict(size=18, family="Arial, sans-serif"), tickfont=dict(size=14))
        )
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.write("📄 **当前勾选项的数据明细：**")
        st.table(filtered_df.astype(str))


elif mode == "🖼️ 材料耐久测试照片展示":
    st.subheader("🔍 材料耐久测试照片展示")

    materials = df['材料名称'].unique()
    selected_material = st.selectbox("📌 请选择要查看测试结果的材料:", materials)

    img_root = os.path.join(base_dir, "耐久测试照片")
    material_img_dir = os.path.join(img_root, selected_material)

    st.markdown(f"**当前选中材料：** `{selected_material}`")

    if os.path.exists(material_img_dir):
        valid_extensions = ('.png', '.jpg', '.jpeg', '.webp')
        images = [f for f in os.listdir(material_img_dir) if f.lower().endswith(valid_extensions)]

        if images:
            cols = st.columns(2)
            for idx, img_name in enumerate(images):
                img_path = os.path.join(material_img_dir, img_name)
                with cols[idx % 2]:
                    st.image(img_path, caption=f"测试照片: {img_name}", use_container_width=True)
        else:
            st.warning(f"⚠️ 在【{selected_material}】文件夹下找到了目录，但里面没有图片文件。")
    else:
        st.info(f"💡 暂无【{selected_material}】的耐久测试照片。")
        st.caption(f"🔧 操作指南：请在 GitHub 仓库中创建路径 `耐久测试照片/{selected_material}/` 并上传图片。")



##  python -m streamlit run data.py