import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="一級建築士 建築史クイズ", layout="centered")
st.title("一級建築士 建築史クイズ")

@st.cache_data(ttl=3600) 
def load_data():
    return pd.read_excel("計画-事例集.xlsx", engine='openpyxl', usecols=["ジャンル", "建築名", "場所", "時代", "特徴", "画像", "建築家", "解説"])

df = load_data()

# --- 初期化 ---
if 'wrong_list' not in st.session_state: st.session_state.wrong_list = []
if 'question' not in st.session_state: st.session_state.question = None
if 'choices' not in st.session_state: st.session_state.choices = []

# --- サイドバー ---
mode = st.sidebar.radio("モード選択", ["通常出題", "苦手問題の復習"])
selected_genre = st.sidebar.selectbox("ジャンルを選択", ["全て"] + df["ジャンル"].unique().tolist())

# 画像表示の切り替えスイッチ（追加！）
show_image = st.sidebar.checkbox("画像を表示する", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("今回間違えた問題")
for item in st.session_state.wrong_list:
    st.sidebar.write(f"・{item}")

# --- ロジック ---
current_config = f"{mode}-{selected_genre}"
if st.session_state.get('last_config') != current_config:
    st.session_state.last_config = current_config
    st.session_state.question = None
    if mode == "通常出題":
        df_f = df if selected_genre == "全て" else df[df["ジャンル"] == selected_genre]
        st.session_state.remaining_questions = df_f.index.tolist()
    else:
        st.session_state.remaining_questions = df[df["建築名"].isin(st.session_state.wrong_list)].index.tolist()
    random.shuffle(st.session_state.remaining_questions)

if st.button("新しい問題"):
    if st.session_state.remaining_questions:
        idx = st.session_state.remaining_questions.pop(0)
        st.session_state.question = df.loc[idx]
        st.session_state.answer_submitted = False
        
        genre_match = df[df["ジャンル"] == st.session_state.question["ジャンル"]]
        opts = genre_match["建築名"].unique().tolist()
        choices = random.sample([o for o in opts if o != st.session_state.question['建築名']], min(len(opts)-1, 3)) + [st.session_state.question['建築名']]
        random.shuffle(choices)
        st.session_state.choices = choices
    else:
        st.warning("問題がありません。")

if st.session_state.question is not None:
    q = st.session_state.question
    st.subheader(f"【{q['ジャンル']}】 この建築物はどれ？")
    st.write(f"**特徴:** {q['特徴']}")

    answer = st.radio("建築名を選択", st.session_state.choices, key="ans_radio")
    
    if st.button("回答する"):
        st.session_state.answer_submitted = True
        if answer != q['建築名'] and q['建築名'] not in st.session_state.wrong_list:
            st.session_state.wrong_list.append(q['建築名'])
        st.rerun()

    if st.session_state.get('answer_submitted'):
        if answer == q['建築名']: st.success("正解！")
        else: st.error(f"正解は **{q['建築名']}**")
        
        # 画像表示を「チェックボックスがONの時だけ」にする
        if show_image:
            img_url = q.get("画像")
            if pd.notna(img_url) and isinstance(img_url, str) and img_url.startswith("http"):
                st.image(img_url, caption=q["建築名"], use_container_width=True)
                
        st.write(f"**建築家:** {q['建築家']}")
        st.write(f"**解説:** {q['解説']}")
