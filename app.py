import streamlit as st
import pandas as pd
import random

# --- ページ設定 ---
st.set_page_config(page_title="一級建築士 建築史クイズ", layout="centered")
st.title("一級建築士 建築史クイズ")

# --- データ読み込み ---
@st.cache_data(ttl=600) 
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
if 'remaining_questions' not in st.session_state:
    st.session_state.remaining_questions = []
if 'current_genre' not in st.session_state:
    st.session_state.current_genre = None

# --- ジャンル選択 ---
genres = ["全て"] + df["ジャンル"].unique().tolist()
selected_genre = st.selectbox("ジャンルを選択", genres)

# ジャンルが切り替わった時の初期化
if selected_genre != st.session_state.current_genre:
    st.session_state.current_genre = selected_genre
    df_filtered = df if selected_genre == "全て" else df[df["ジャンル"] == selected_genre]
    st.session_state.remaining_questions = df_filtered.index.tolist()
    random.shuffle(st.session_state.remaining_questions)
    st.session_state.question = None
    st.session_state.answer_submitted = False

# --- 新しい問題ボタン ---
if st.button("新しい問題"):
    if st.session_state.remaining_questions:
        next_idx = st.session_state.remaining_questions.pop(0)
        st.session_state.question = df.loc[next_idx]
        st.session_state.answer_submitted = False
        
        # 選択肢生成
        df_filtered = df if st.session_state.current_genre == "全て" else df[df["ジャンル"] == st.session_state.current_genre]
        options = df_filtered["建築名"].unique().tolist()
        if len(options) < 2: options = df["建築名"].unique().tolist()
        
        choices = random.sample([o for o in options if o != st.session_state.question['建築名']], min(len(options)-1, 3)) + [st.session_state.question['建築名']]
        random.shuffle(choices)
        st.session_state.choices = choices
    else:
        st.warning("このジャンルは全問終了しました！")

# --- クイズ表示 ---
if st.session_state.get('question') is not None:
    q = st.session_state.question
    st.subheader(f"【{q['ジャンル']}】 この建築物はどれ？（残り:{len(st.session_state.remaining_questions)}問）")
    st.write(f"**場所:** {q['場所']} / **時代:** {q['時代']}")
    st.write(f"**特徴:** {q['特徴']}")

    # 選択肢と回答
    answer = st.radio("建築名を選んでください", st.session_state.choices, key="user_answer")

    if st.button("回答する"):
        st.session_state.answer_submitted = True
        if answer != q['建築名'] and q['建築名'] not in st.session_state.wrong_list:
            st.session_state.wrong_list.append(q['建築名'])

    if st.session_state.answer_submitted:
        if answer == q['建築名']:
            st.success("正解！")
        else:
            st.error(f"残念！正解は **{q['建築名']}** でした。")

        with st.expander("解説を見る"):
            img_url = q.get("画像")
            if pd.notna(img_url) and str(img_url).startswith("http"):
                st.image(str(img_url), caption=q["建築名"], use_container_width=True)
            st.write(f"**建築家:** {q['建築家']}")
            st.write(f"**解説:** {q['解説']}")
else:
    st.info("「新しい問題」ボタンを押してクイズを開始してください！")

# --- 間違いリスト ---
st.markdown("---")
st.sidebar.subheader("今回の間違いリスト")
for item in st.session_state.wrong_list:
    st.sidebar.write(f"・{item}")


# --- サイドバーにジャンル選択を追加（"復習モード"を増やしました） ---
genres = ["全て", "復習モード"] + df["ジャンル"].unique().tolist()
selected_genre = st.selectbox("ジャンルを選択", genres)


if st.button("新しい問題", key="new_q_btn"):
    
    if selected_genre == "復習モード":
        # 間違えた問題リスト(建築名)に該当する行だけ抽出
        target_df = df[df["建築名"].isin(st.session_state.wrong_list)]
    else:
        target_df = df if selected_genre == "全て" else df[df["ジャンル"] == selected_genre]

    # リスト作成とシャッフル
    st.session_state.remaining_questions = target_df.index.tolist()
    random.shuffle(st.session_state.remaining_questions)
    
    if st.session_state.remaining_questions:
        next_idx = st.session_state.remaining_questions.pop(0)
        st.session_state.question = df.loc[next_idx]
        st.session_state.answer_submitted = False
        
        # --- ここで「同じジャンル」から選択肢を作る ---
        current_q = st.session_state.question
        # 同じジャンルの建築名だけを抽出
        genre_options = df[df["ジャンル"] == current_q["ジャンル"]]["建築名"].unique().tolist()
        
        # 選択肢を作る（正解を含めて4つ）
        choices = random.sample([o for o in genre_options if o != current_q['建築名']], min(len(genre_options)-1, 3)) + [current_q['建築名']]
        random.shuffle(choices)
        st.session_state.choices = choices
    else:
        st.warning("対象となる問題がありません！")
        st.session_state.question = None
