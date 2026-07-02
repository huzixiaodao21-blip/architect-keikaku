import streamlit as st
import pandas as pd
import random

# --- ページ設定 ---
st.set_page_config(page_title="一級建築士 建築史クイズ", layout="centered")
st.title("一級建築士 建築史クイズ")

# --- データ読み込み ---
@st.cache_data
def load_data():
    return pd.read_excel("計画-事例集.xlsx")

try:
    df = load_data()
except Exception as e:
    st.error(f"ファイル読み込みエラー: {e}")
    st.stop()

# --- 状態管理の初期化 ---
if 'wrong_list' not in st.session_state:
    st.session_state.wrong_list = []

# --- サイドバーでジャンル選択 ---
genres = ["全て"] + df["ジャンル"].unique().tolist()
selected_genre = st.selectbox("ジャンルを選択", genres)

if selected_genre != "全て":
    df_filtered = df[df["ジャンル"] == selected_genre]
else:
    df_filtered = df

# --- クイズの状態管理 ---
if 'question' not in st.session_state or st.button("新しい問題"):
    st.session_state.question = df_filtered.sample(n=1).iloc[0]
    st.session_state.answer_submitted = False
    
    # 選択肢をここで一度だけ生成して保存する
    options = df_filtered["建築名"].unique().tolist()
    if len(options) < 2:
        options = df["建築名"].unique().tolist()
    
    # 正解と不正解を混ぜる
    choices = random.sample([o for o in options if o != st.session_state.question['建築名']], min(len(options)-1, 3)) + [st.session_state.question['建築名']]
    random.shuffle(choices)
    st.session_state.choices = choices # ここで選択肢を固定保存

q = st.session_state.question
choices = st.session_state.choices # 保存した選択肢を読み出す

# --- クイズ表示 ---
st.subheader(f"【{q['ジャンル']}】 この建築物はどれ？")
st.write(f"**場所:** {q['場所']} / **時代:** {q['時代']}")
st.write(f"**特徴:** {q['特徴']}")

# 選択肢の生成
choices = st.session_state.choices

# 回答入力
answer = st.radio("建築名を選んでください", choices, key="user_answer")

# --- 回答ボタン（ここを一つに統合） ---
if st.button("回答する", key="answer_button"):
    st.session_state.answer_submitted = True
    if answer != q['建築名']:
        if q['建築名'] not in st.session_state.wrong_list:
            st.session_state.wrong_list.append(q['建築名'])

if st.session_state.answer_submitted:
    if answer == q['建築名']:
        st.success("正解！")
    else:
        st.error(f"残念！正解は **{q['建築名']}** でした。")

    with st.expander("解説を見る"):
        # データの中身を確認できたので、デバッグ用表示は消してOKです
        # st.write("この行のデータ:", q.to_dict()) 
        
        # 1. Excelの「画像」列からURLを取得
        img_url = q.get("画像")
        
        # 2. URLが空でなく、かつURLっぽい文字列であれば画像を表示
        if pd.notna(img_url) and str(img_url).startswith("http"):
            st.image(str(img_url), caption=q["建築名"], use_container_width=True)
        else:
            # 画像がない行のための表示（あえて何も出さない、もしくは「画像なし」と出すなど）
            st.info("この建築物には画像が設定されていません。")
            

        st.write(f"**建築家:** {q['建築家']}")
        st.write(f"**解説:** {q['解説']}")

# --- サイドバーに「間違えた問題」を表示 ---
st.sidebar.subheader("今回の間違いリスト")
for item in st.session_state.wrong_list:
    st.sidebar.write(f"・{item}")
