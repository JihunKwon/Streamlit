"""Simulation

    _summary_
    This script is a simulation of long-term investment in a specific asset with a certain return and risk.
    """
# ライブラリ読み込み

from datetime import datetime, time as datetime_time
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go


st.title("長期収益シミュレーション")
st.markdown("""
## 概要
お客様の検査運用状況をもとに、ソフトウェアを活用した場合の長期収益推移をシミュレーションします。

## 使い方
お客様の状況を入力し「Run」ボタンをクリック
## 実行例
 """)

increase_per_day = st.number_input("検査数増加分（件）", min_value=0, max_value=None,
                           value=3, step=1, help="導入時の検査数増加分（件）")
exam_time_new = st.number_input("検査時間（分）", min_value=0,
                                max_value=None, value=25, step=1, help="導入時の検査時間（分）")
wait = st.number_input("検査待ち日数（日）", min_value=0,
                       max_value=None, value=20, step=1, help="検査待ち日数（日）")

field = st.selectbox(
    "静磁場強度（T）",
    ("1.5", "3.0"),
)
field = float(field)
exam_time_old = st.number_input("検査枠(従来)（分）", min_value=0,
                                max_value=None, value=30, step=1, help="現在の検査時間（分）")
MR_people = st.number_input("MR担当者数（人）", min_value=1,
                            max_value=None, value=2, step=1)

exam_per_day = st.number_input("1日あたりの検査枠数（件）", min_value=1,
                               max_value=None, value=18, step=1)


time_start = st.time_input("検査開始時間", datetime_time(9, 00))
time_end = st.time_input("検査終了時間", datetime_time(18, 00))

# Create datetime objects for today with the input times
dt_start = datetime.combine(datetime.today(), time_start)
dt_end = datetime.combine(datetime.today(), time_end)

# Calculate the difference
time_diff = dt_end - dt_start

# Convert to hours and minutes
total_hours = time_diff.total_seconds() / 3600  # Convert to decimal hours

# Display the result
st.write(f"稼働時間: {total_hours:.1f} 時間")

# Display the waiting time
st.write(f"待ち検査数: {wait * exam_per_day} （件）")

# Depending on the field strength selected above, chose which to pre-selected
if field == 1.5:
    check_3T = st.checkbox(
        '撮像点数(3T)(1600点)', value=False, label_visibility="visible")
    check_15T = st.checkbox(
        '撮像点数(1.5T)(1330点)', value=True, label_visibility="visible")
elif field == 3.0:
    check_3T = st.checkbox(
        '撮像点数(3T)(1600点)', value=True, label_visibility="visible")
    check_15T = st.checkbox(
        '撮像点数(1.5T)(1330点)', value=False, label_visibility="visible")

check_computer_diagnosis = st.checkbox(
    'コンピューター断層診断料(450点)', value=False, label_visibility="visible")
check_kasan1 = st.checkbox(
    '画像診断管理加算１(70点)', value=False, label_visibility="visible")
check_kasan2 = st.checkbox(
    '画像診断管理加算２(180点)', value=False, label_visibility="visible")
check_kasan3 = st.checkbox(
    '画像診断管理加算３(300点)', value=False, label_visibility="visible")
check_densi = st.checkbox(
    '電子画像管理加算 (120点)', value=False, label_visibility="visible")


# First define the points for each item
points_dict = {
    'check_3T': 1600 if check_3T else 0,
    'check_15T': 1330 if check_15T else 0,
    'check_computer_diagnosis': 450 if check_computer_diagnosis else 0,
    'check_kasan1': 70 if check_kasan1 else 0,
    'check_kasan2': 180 if check_kasan2 else 0,
    'check_kasan3': 300 if check_kasan3 else 0,
    'check_densi': 120 if check_densi else 0
}

# Calculate total points
total_points = sum(points_dict.values())


# Add some validation rules
if check_3T and check_15T:
    st.error('3Tと1.5Tは同時に選択できません')
    total_points = 0
elif not (check_3T or check_15T):
    st.warning('撮像点数を選択してください')
    total_points = 0

if sum([check_kasan1, check_kasan2, check_kasan3]) > 1:
    st.error('画像診断管理加算は1つのみ選択可能です')
    total_points = 0


# Display the total
if total_points > 0:
    st.success(f'合計点数: {total_points} 点')
    st.write(f'診療報酬: ¥{total_points * 10:,}')


weekday = st.number_input("2025年の平日日数（日）", min_value=1,
                          max_value=365, value=246, step=1)
salary = st.number_input("診療放射線技師の時給（円）", min_value=1000,
                         max_value=10000, value=2500, step=100)

if st.button("Run"):
    # 年間増収
    Zoshu = increase_per_day * total_points * 10 * weekday
    st.write(f'年間増収は{Zoshu:,}円です')

    # 検査終了時間はXX時間短くなります
    Delta_time_per_exam = exam_time_old - exam_time_new
    Delta_time_per_day = Delta_time_per_exam * exam_per_day
    #st.write(df.style.format("{:.2}"))
    st.write(f'検査終了時間は{Delta_time_per_day}分短くなります')

    # 検査待ちはXX日でなくなります
    Day_till_zero = wait_exam / increase_per_day
    st.write(f'検査待ちは{Day_till_zero}日でなくなります')

    # 残業代(年あたり)XX円削減できます
    Reduce = salary * MR_people * weekday * Delta_time_per_day / 60
    st.write(f'残業代(年あたり){Reduce:,}円削減できます')

    year = np.arange(5)+1
    Zoshu_year = np.zeros([5])
    for i in range(5):
        Zoshu_year[i] = Zoshu * (i+1)

    # 計算結果をDataFrameに格納
    df_result = pd.DataFrame(np.transpose([year, Zoshu_year]), columns=[
        "Year", "Zoshu"])

    # グラフ出力
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_result["Year"], y=df_result["Zoshu"], name="増収",
        # Format numbers with commas
        text=df_result["Zoshu"].map('{:,.0f}'.format),
        textposition='top center',  # Position the text above the points
        mode='lines+markers+text'  # Show lines, markers, and text
    ))
    fig.update_layout(hovermode="x")
    fig.update_layout(title="収益シミュレーション（増収分）",
                      xaxis_title="年目", yaxis_title="増収益（円）")

    # Adjust layout to prevent text overlap
    fig.update_traces(texttemplate='¥%{text}')  # Add yen symbol
    fig.update_layout(
        showlegend=True,
        # Add 10% padding at the top for labels
        yaxis_range=[0, max(df_result["Zoshu"]) * 1.1]
    )

    st.plotly_chart(fig, use_container_width=True)
