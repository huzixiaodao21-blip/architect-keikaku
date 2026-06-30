import streamlit as st
import pandas as pd
import random

# --- ページ設定 ---
st.set_page_config(page_title="一級建築士 建築史クイズ", layout="centered")
st.title("一級建築士 建築史クイズ")

# --- データ読み込み ---
@st.cache_data
def load_data():
    return pd.read_excel("建築史.xlsx")

try:
    df = load_data()
except Exception as e:
    st.error(f"ファイル読み込みエラー: {e}")
    st.stop()

# --- サイドバーでジャンル選択 ---
genres = ["全て"] + df["ジャンル"].unique().tolist()
selected_genre = st.sidebar.selectbox("ジャンルを選択", genres)

if selected_genre != "全て":
    df_filtered = df[df["ジャンル"] == selected_genre]
else:
    df_filtered = df

# --- クイズの状態管理 ---
if 'question' not in st.session_state or st.sidebar.button("新しい問題"):
    st.session_state.question = df_filtered.sample(n=1).iloc[0]
    st.session_state.answer_submitted = False

q = st.session_state.question

# --- クイズ表示 ---
st.subheader(f"【{q['ジャンル']}】 この建築物はどれ？")
st.write(f"**場所:** {q['場所']} / **時代:** {q['時代']}")
st.write(f"**特徴:** {q['特徴']}")

# 選択肢の生成
options = df_filtered["建築名"].unique().tolist()
if len(options) < 2:
    options = df["建築名"].unique().tolist()
    
choices = random.sample([o for o in options if o != q['建築名']], min(len(options)-1, 3)) + [q['建築名']]
random.shuffle(choices)

# 回答入力
answer = st.radio("建築名を選んでください", choices, key="user_answer")

if st.button("回答する", key="answer_button"):
    st.session_state.answer_submitted = True

if st.session_state.answer_submitted:
    if answer == q['建築名']:
        st.success("正解！")
    else:
        st.error(f"残念！正解は **{q['建築名']}** でした。")
    
    with st.expander("解説を見る"):
        st.write(f"**建築家:** {q['建築家']}")
        st.write(f"**解説:** {q['解説']}")

# --- 状態管理にリストを追加 ---
if 'wrong_list' not in st.session_state:
    st.session_state.wrong_list = []

# --- 回答判定部分の修正 ---
if st.button("回答する"):
    st.session_state.answer_submitted = True
    if answer != q['建築名']:
        # 間違えたらリストに追加（重複を避ける）
        if q['建築名'] not in st.session_state.wrong_list:
            st.session_state.wrong_list.append(q['建築名'])

# --- サイドバーに「間違えた問題」を表示 ---
st.sidebar.markdown("---")
st.sidebar.subheader("今回の間違いリスト")
for item in st.session_state.wrong_list:
    st.sidebar.write(f"・{item}")
