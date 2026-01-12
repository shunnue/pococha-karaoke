import streamlit as st
import pandas as pd
import time

# --- 1. ページ設定 ---
st.set_page_config(page_title="Pocochaカラオケ検索", layout="wide")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {
                padding-top: 1rem;
                padding-bottom: 1rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- 2. ログイン管理システム ---
# セッション状態の初期化
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""

# ログイン画面の表示
if not st.session_state['logged_in']:
    st.subheader("🔒 会員専用ログイン")
    st.markdown("note定期購読者様専用のツールです。")
    
    # ユーザーIDとパスワードの入力欄
    input_user = st.text_input("ユーザーID", placeholder="noteのIDなど")
    input_pass = st.text_input("パスワード", type="password")
    
    login_btn = st.button("ログイン")

    if login_btn:
        # ★ここがポイント：Streamlitの「Secrets（台帳）」を見に行く
        # 台帳の中に「入力されたID」が存在し、かつ「パスワード」が合っているか？
        if "users" in st.secrets and input_user in st.secrets["users"]:
            if st.secrets["users"][input_user] == input_pass:
                # ログイン成功
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = input_user
                st.success("認証成功！")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("パスワードが間違っています。")
        else:
            st.error("IDが見つかりません、または有効期限切れです。")
    
    st.stop() # ログインしていない人はここでストップ

# ==========================================
# 🌸 ここから下が「会員」だけが見れる世界
# ==========================================

# --- 3. データの読み込み ---
@st.cache_data
def load_data():
    try:
        all_sheets = pd.read_excel("data.xlsx", sheet_name=None, header=None)
        df_list = []
        for sheet_name, sheet_df in all_sheets.items():
            sheet_df.columns = range(sheet_df.shape[1])
            df_list.append(sheet_df)
        
        df = pd.concat(df_list, ignore_index=True)
        df = df.fillna("").astype(str)
        rename_map = {0: "歌手名", 1: "楽曲名"}
        df = df.rename(columns=rename_map)
        if "歌手名" in df.columns and "楽曲名" in df.columns:
            df = df[["歌手名", "楽曲名"]]
        df["歌手名"] = df["歌手名"].str.strip()
        df = df[df["歌手名"] != "歌手名"]
        df = df[df["歌手名"] != ""]
        return df
    except Exception as e:
        return None

df = load_data()

# --- 4. 検索画面表示 ---
st.subheader(f"🎤 カラオケ検索ツール")
st.caption(f"ようこそ、{st.session_state['user_name']} さん") # ユーザー名を表示して特別感を出す

if st.button("ログアウト", type="secondary"):
    st.session_state['logged_in'] = False
    st.rerun()

st.markdown("---")

if df is not None:
    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input("", placeholder="キーワードを入力", label_visibility="collapsed")
    
    st.write("")

    if search_query:
        mask = df.apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
        results = df[mask]
        if len(results) > 0:
            st.success(f"{len(results)} 件 ヒット")
            st.dataframe(results, use_container_width=True, hide_index=True)
        else:
            st.warning("見つかりませんでした。")
    else:
        st.info("キーワードを入力してください。")
        with st.expander("データを確認"):
            st.dataframe(df.head(50), use_container_width=True, hide_index=True)
else:
    st.error("データファイルエラー")
