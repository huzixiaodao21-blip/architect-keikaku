import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="一級建築士 建築史クイズ", layout="centered")
st.title("一級建築士 建築史クイズ")

@st.cache_data(ttl=60) 
def load_data():
    return pd.read_excel("計画-事例集.xlsx", usecols=["ジャンル", "建築名", "場所", "時代", "特徴", "画像", "建築家", "解説"])

df = load_data()

# --- 初期化 ---
if 'wrong_list' not in st.session_state: st.session_state.wrong_list = []
if 'question' not in st.session_state: st.session_state.question = None
if 'choices' not in st.session_state: st.session_state.choices = []

# --- モード選択（サイドバー） ---
st.sidebar.subheader("設定")
mode = st.sidebar.radio("モード選択", ["通常出題", "苦手問題の復習"])
genres = ["全て"] + df["ジャンル"].unique().tolist()
selected_genre = st.sidebar.selectbox("ジャンルを選択", genres)

# --- 制御処理 ---
if st.sidebar.button("問題セットをリロード"):
    st.session_state.question = None
    if mode == "通常出題":
        df_f = df if selected_genre == "全て" else df[df["ジャンル"] == selected_genre]
        st.session_state.remaining_questions = df_f.index.tolist()
    else:
        st.session_state.remaining_questions = df[df["建築名"].isin(st.session_state.wrong_list)].index.tolist()
    random.shuffle(st.session_state.remaining_questions)
    st.rerun()

# --- 新しい問題ボタン ---
if st.button("新しい問題"):
    if st.session_state.get('remaining_questions') and len(st.session_state.remaining_questions) > 0:
        idx = st.session_state.remaining_questions.pop(0)
        st.session_state.question = df.loc[idx]
        st.session_state.answer_submitted = False
        
        # 選択肢生成（同じジャンルから抽出）
        genre_match = df[df["ジャンル"] == st.session_state.question["ジャンル"]]
        opts = genre_match["建築名"].unique().tolist()
        choices = random.sample([o for o in opts if o != st.session_state.question['建築名']], min(len(opts)-1, 3)) + [st.session_state.question['建築名']]
        random.shuffle(choices)
        st.session_state.choices = choices
    else:
        st.warning("問題がありません。「問題セットをリロード」を押してください。")

# --- 表示 ---
if st.session_state.question is not None:
    q = st.session_state.question
    st.subheader(f"【{q['ジャンル']}】 この建築物はどれ？")
    st.write(f"**場所:** {q['場所']} / **時代:** {q['時代']}")
    st.write(f"**特徴:** {q['特徴']}")

    answer = st.radio("建築名を選択", st.session_state.choices, key="ans_radio")
    if st.button("回答する"):
        st.session_state.answer_submitted = True
        if answer != q['建築名'] and q['建築名'] not in st.session_state.wrong_list:
            st.session_state.wrong_list.append(q['建築名'])

    if st.session_state.answer_submitted:
        if answer == q['建築名']: st.success("正解！")
        else: st.error(f"正解は **{q['建築名']}**")
        with st.expander("解説"):
            st.write(f"**建築家:** {q['建築家']}\n\n{q['解説']}")
