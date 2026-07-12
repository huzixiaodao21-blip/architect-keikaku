import streamlit as st
import pandas as pd
import random

# --- ページ設定 ---
st.set_page_config(page_title="一級建築士 建築史クイズ", layout="centered")
st.title("一級建築士 建築史クイズ")

# --- データ読み込み ---
@st.cache_data(ttl=60) 
def load_data():
    return pd.read_excel("計画-事例集.xlsx", usecols=["ジャンル", "建築名", "場所", "時代", "特徴", "画像", "建築家", "解説"])
    
try:
    df = load_data()
except Exception as e:
    st.error(f"ファイル読み込みエラー: {e}")
    st.stop()

# --- 状態管理の初期化 ---
if 'wrong_list' not in st.session_state: st.session_state.wrong_list = []
if 'remaining_questions' not in st.session_state: st.session_state.remaining_questions = []
if 'current_genre' not in st.session_state: st.session_state.current_genre = None
if 'previous_mode' not in st.session_state: st.session_state.previous_mode = "通常出題"

# --- サイドバー：モード切替 ---
st.sidebar.markdown("---")
mode = st.sidebar.radio("モード選択", ["通常出題", "苦手問題の復習"], key="mode_radio")

# モードが変わった時の処理
if mode != st.session_state.previous_mode:
    st.session_state.previous_mode = mode
    st.session_state.question = None
    st.session_state.answer_submitted = False
    
    if mode == "通常出題":
        df_filtered = df if st.session_state.current_genre == "全て" else df[df["ジャンル"] == st.session_state.current_genre]
        st.session_state.remaining_questions = df_filtered.index.tolist()
        random.shuffle(st.session_state.remaining_questions)
    st.rerun() # ここでリセットを確定させる

# --- ジャンル選択 ---
genres = ["全て"] + df["ジャンル"].unique().tolist()
selected_genre = st.selectbox("ジャンルを選択", genres)

if selected_genre != st.session_state.current_genre:
    st.session_state.current_genre = selected_genre
    df_filtered = df if selected_genre == "全て" else df[df["ジャンル"] == selected_genre]
    st.session_state.remaining_questions = df_filtered.index.tolist()
    random.shuffle(st.session_state.remaining_questions)
    st.session_state.question = None
    st.rerun()

# --- 新しい問題ボタン ---
if st.button("新しい問題"):
    if mode == "苦手問題の復習":
        st.session_state.remaining_questions = df[df["建築名"].isin(st.session_state.wrong_list)].index.tolist()
        random.shuffle(st.session_state.remaining_questions)
        
    if st.session_state.remaining_questions:
        next_idx = st.session_state.remaining_questions.pop(0)
        st.session_state.question = df.loc[next_idx]
        st.session_state.answer_submitted = False
        
        source_df = df if st.session_state.current_genre == "全て" else df[df["ジャンル"] == st.session_state.current_genre]
        options = source_df["建築名"].unique().tolist()
        choices = random.sample([o for o in options if o != st.session_state.question['建築名']], min(len(options)-1, 3)) + [st.session_state.question['建築名']]
        random.shuffle(choices)
        st.session_state.choices = choices
    else:
        st.warning("出題できる問題がありません！")

# --- クイズ表示 ---
if st.session_state.get('question') is not None:
    q = st.session_state.question
    st.subheader(f"【{q['ジャンル']}】 この建築物はどれ？（残り:{len(st.session_state.remaining_questions)}問）")
    st.write(f"**場所:** {q['場所']} / **時代:** {q['時代']}")
    st.write(f"**特徴:** {q['特徴']}")

    # 回答入力 (keyをリセットするためにquestionのindexを埋め込む)
    answer = st.radio("建築名を選んでください", st.session_state.choices, key=f"ans_{st.session_state.question.name}")

    if st.button("回答する"):
        st.session_state.answer_submitted = True
        if answer != q['建築名'] and q['建築名'] not in st.session_state.wrong_list:
            st.session_state.wrong_list.append(q['建築名'])
            st.rerun()

    if st.session_state.answer_submitted:
        if answer == q['建築名']: st.success("正解！")
        else: st.error(f"残念！正解は **{q['建築名']}** でした。")

        with st.expander("解説を見る"):
            img_url = q.get("画像")
            if pd.notna(img_url) and str(img_url).startswith("http"):
                st.image(str(img_url), caption=q["建築名"], use_container_width=True)
            st.write(f"**建築家:** {q['建築家']}")
            st.write(f"**解説:** {q['解説']}")
