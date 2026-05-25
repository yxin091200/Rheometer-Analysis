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
    # 动态判断当前是代码运行环境还是打包后的单文件环境
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))

    # 拼接外部 Excel 文件的绝对路径
    file_name = os.path.join(current_dir, "自研流变仪材料测试数据.xlsx")

    # 增加一个友好的防错和指引提示
    if not os.path.exists(file_name):
        st.error("⚠️ 找不到数据源文件！")
        st.markdown(f"请确保 **【自研流变仪材料测试数据.xlsx】** 已经放在与本程序**相同的文件夹**下。")
        st.info(f"程序当前检测的路径为：`{file_name}`")
        st.stop()  # 找不到文件时拦截后续运行，避免崩溃

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
        "🖼️ 材料耐久测试照片展示"  # <-- 新增的第三个选项
    )
)

# 4. 根据模式渲染主界面
if mode == "📊 同一材料 ➔ 对比不同转子":
    st.subheader("🔹 同一材料，对比不同转子")

    materials = df['材料名称'].unique()
    selected_material = st.selectbox("📌 步骤一：请选择基础材料名称:", materials)

    # 提取该材料下所有可用的转子类型
    available_rotors = df[df['材料名称'] == selected_material]['平行杆'].unique()

    # 新增功能一：多选勾选框（默认留空，不勾选就不画图）
    selected_rotors = st.multiselect(
        "☑️ 步骤二：请选择需要绘制曲线的转子（可多选）:",
        options=available_rotors,
        default=[]  # 默认为空列表，先不画图
    )

    if not selected_rotors:
        # 如果没有勾选任何项，给出提示并暂停向下渲染
        st.info("👆 请在上方勾选至少一个转子以生成图表和数据明细。")
    else:
        # 过滤出选中材料，且仅包含被勾选转子的数据
        filtered_df = df[(df['材料名称'] == selected_material) & (df['平行杆'].isin(selected_rotors))]

        # 绘制动态折线图（新增 symbol 和 line_dash 参数）
        fig = px.line(
            filtered_df, x='磁场（T）', y='扭矩（mNm）',
            color='平行杆',  # 颜色区分
            symbol='平行杆',  # 新增功能二：点形状区分（圆、方、三角等）
            line_dash='平行杆',  # 新增功能二：线型区分（实线、虚线、点划线等）
            markers=True,
            title=f"【{selected_material}】在不同转子下的扭矩对比",
            labels={'平行杆': '转子类型', '磁场（T）': '磁场（T）', '扭矩（mNm）': '扭矩（mNm）'}
        )
        # 放大点的大小以便更清楚地看到不同形状
        fig.update_traces(line=dict(width=3), marker=dict(size=10))
        fig.update_layout(
            hovermode="x unified", font=dict(size=14),
            xaxis=dict(title="磁场（T）", title_font=dict(size=18, family="Arial, sans-serif"), tickfont=dict(size=14)),
            yaxis=dict(title="扭矩（mNm）", title_font=dict(size=18, family="Arial, sans-serif"), tickfont=dict(size=14))
        )
        st.plotly_chart(fig, use_container_width=True)

        # 底部展示对应的数据表
        st.divider()
        st.write("📄 **当前勾选项的数据明细：**")
        st.table(filtered_df.astype(str))


elif mode == "📊 同一转子 ➔ 对比不同材料":
    st.subheader("🔸 同一转子，对比不同材料")

    rotors = df['平行杆'].unique()
    selected_rotor = st.selectbox("📌 步骤一：请选择基础转子类型:", rotors)

    # 提取该转子下所有测试过的材料
    available_materials = df[df['平行杆'] == selected_rotor]['材料名称'].unique()

    # 新增功能一：多选勾选框（默认留空）
    selected_materials = st.multiselect(
        "☑️ 步骤二：请选择需要绘制曲线的材料（可多选）:",
        options=available_materials,
        default=[]  # 默认为空，先不画图
    )

    if not selected_materials:
        # 如果没有勾选任何项，给出提示并暂停向下渲染
        st.info("👆 请在上方勾选至少一种材料以生成图表和数据明细。")
    else:
        # 过滤出选中转子，且仅包含被勾选材料的数据
        filtered_df = df[(df['平行杆'] == selected_rotor) & (df['材料名称'].isin(selected_materials))]

        # 绘制动态折线图（新增 symbol 和 line_dash 参数）
        fig = px.line(
            filtered_df, x='磁场（T）', y='扭矩（mNm）',
            color='材料名称',  # 颜色区分
            symbol='材料名称',  # 新增功能二：点形状区分（圆、方、三角、菱形等）
            line_dash='材料名称',  # 新增功能二：线型区分（实线、虚线、点划线等）
            markers=True,
            title=f"转子【{selected_rotor}】在不同材料下的扭矩对比",
            labels={'材料名称': '材料类型', '磁场（T）': '磁场（T）', '扭矩（mNm）': '扭矩（mNm）'}
        )
        # 放大点的大小以便更清楚地看到不同形状
        fig.update_traces(line=dict(width=3), marker=dict(size=10))
        fig.update_layout(
            hovermode="x unified", font=dict(size=14),
            xaxis=dict(title="磁场（T）", title_font=dict(size=18, family="Arial, sans-serif"), tickfont=dict(size=14)),
            yaxis=dict(title="扭矩（mNm）", title_font=dict(size=18, family="Arial, sans-serif"), tickfont=dict(size=14))
        )
        st.plotly_chart(fig, use_container_width=True)

        # 底部展示对应的数据表
        st.divider()
        st.write("📄 **当前勾选项的数据明细：**")
        st.table(filtered_df.astype(str))


elif mode == "🖼️ 材料耐久测试照片展示":
    st.subheader("🔍 材料耐久测试照片展示")

    # 提取所有去重后的材料名称并让用户选择
    materials = df['材料名称'].unique()
    selected_material = st.selectbox("📌 请选择要查看测试结果的材料:", materials)

    # 设定照片存放的目录路径
    img_root = os.path.join(base_dir, "耐久测试照片")
    material_img_dir = os.path.join(img_root, selected_material)

    st.markdown(f"**当前选中材料：** `{selected_material}`")

    # 检查主文件夹和子文件夹是否存在
    if os.path.exists(material_img_dir):
        # 寻找常见的图片格式
        valid_extensions = ('.png', '.jpg', '.jpeg', '.webp')
        images = [f for f in os.listdir(material_img_dir) if f.lower().endswith(valid_extensions)]

        if images:
            # 采用双列排版，让图片显示更美观
            cols = st.columns(2)
            for idx, img_name in enumerate(images):
                img_path = os.path.join(material_img_dir, img_name)
                # 交替在左右两列插入图片
                with cols[idx % 2]:
                    st.image(img_path, caption=f"测试照片: {img_name}", use_container_width=True)
        else:
            st.warning(f"⚠️ 在【{selected_material}】文件夹下找到了目录，但里面没有图片文件。")
    else:
        st.info(f"💡 暂无【{selected_material}】的耐久测试照片。")
        st.caption(f"🔧 操作指南：请在 GitHub 仓库中创建路径 `耐久测试照片/{selected_material}/` 并上传图片。")



##  python -m streamlit run data.py