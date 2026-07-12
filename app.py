import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="一級建築士 建築史クイズ", layout="centered")
st.title("一級建築士 建築史クイズ")

@st.cache_data(ttl=3600) 
def get_df_minimal():
    return pd.read_excel("計画-事例集.xlsx", engine='openpyxl', usecols=["ジャンル", "建築名", "場所", "時代", "特徴", "画像", "建築家", "解説"])

df = get_df_minimal()


def get_optimized_url(url):
    # images.weserv.nl を通すと、勝手に画像を圧縮・軽量化して配信してくれます
    # w=500 は「幅を500pxにする」という指示です。これで1.4MBが数十KBになります！
    return f"https://images.weserv.nl/?url={url}&w=500&output=webp"


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

# --- 新しい問題ボタン ---
if st.button("新しい問題"):
    if st.session_state.remaining_questions:
        idx = st.session_state.remaining_questions.pop(0)
        # 必要な行だけを抽出
        q = df.loc[idx]
        st.session_state.question = q
        st.session_state.answer_submitted = False
        
        # 選択肢の計算を最小限に
        genre_match = df[df["ジャンル"] == q["ジャンル"]]
        opts = genre_match["建築名"].unique().tolist()
        # 選択肢の生成
        choices = random.sample([o for o in opts if o != q['建築名']], min(len(opts)-1, 3)) + [q['建築名']]
        random.shuffle(choices)
        st.session_state.choices = choices
        st.rerun() # 即座に反映
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
            img_url = str(q.get("画像")).strip() # 余分な空白を削除！
            if img_url and img_url.startswith("http"):
                optimized_url = get_optimized_url(img_url)
                try:
                    st.image(optimized_url, caption=q["建築名"], use_container_width=True)
                except Exception as e:
                    st.error("画像の読み込みに失敗しました")
                
        st.write(f"**建築家:** {q['建築家']}")
        st.write(f"**解説:** {q['解説']}")
