import streamlit as st
import pandas as pd
import time

# ==========================================
# ★設定エリア（後でここを書き換えてください）
# 会員登録ボタンを押したときの飛び先URL
SIGNUP_URL = "https://note.com/" 
# ==========================================

# --- 1. ページ設定 ---
st.set_page_config(page_title="Pocochaカラオケ検索", layout="wide")

# スタイル設定
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
            /* リンクボタンを目立たせる */
            .stLinkButton > a {
                background-color: #ff4b4b;
                color: white !important;
                font-weight: bold;
                border-radius: 5px;
                text-align: center;
                border: none;
            }
            .stLinkButton > a:hover {
                background-color: #ff3333;
                color: white !important;
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

# -------------------------------------------
# 🔒 ログイン画面の処理
# -------------------------------------------
if not st.session_state['logged_in']:
    
    # 画面中央に配置するためにカラムを使う
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("🔒 会員専用ログイン")
        st.info("Note定期購読者様専用のツールです。")
        
        # ログインフォーム
        with st.form("login_form"):
            input_user = st.text_input("ユーザーID", placeholder="発行されたIDを入力")
            input_pass = st.text_input("パスワード", type="password")
            
            # ログインボタン
            submitted = st.form_submit_button("ログイン", use_container_width=True)

            if submitted:
                # 顧客台帳チェック
                if "users" not in st.secrets:
                    st.error("システムエラー：顧客台帳(Secrets)が設定されていません。")
                else:
                    if input_user in st.secrets["users"]:
                        if st.secrets["users"][input_user] == input_pass:
                            # ★ログイン成功
                            st.session_state['logged_in'] = True
                            st.session_state['user_name'] = input_user
                            st.success("認証成功！")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("パスワードが間違っています。")
                    else:
                        st.error("IDが見つかりません。")

        # -------------------------------------------
        # ✨ 新規会員登録への誘導エリア
        # -------------------------------------------
        st.markdown("---") # 区切り線
        st.markdown("##### 🔰 IDをお持ちでない方")
        st.write("このツールを利用するには会員登録が必要です。")
        
        # 会員登録ボタン（設定したURLに飛びます）
        st.link_button("👉 新規会員登録はこちら", SIGNUP_URL, use_container_width=True)
    
    # ログインしていない人はここでプログラム終了
    st.stop() 

# ==========================================
# 🌸 ログイン成功者エリア
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
    except Exception:
        return None

df = load_data()

# --- 4. 検索ツール画面 ---
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("🎤 Pococha カラオケ検索")
with col2:
    st.write(f"User: **{st.session_state['user_name']}**")
    if st.button("ログアウト", type="secondary", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['user_name'] = ""
        st.rerun()

st.markdown("---")

if df is not None:
    search_query = st.text_input("キーワード検索", placeholder="曲名・歌手名（例：マリーゴールド）")
    
    if search_query:
        mask = df.apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
        results = df[mask]

        if len(results) > 0:
            st.success(f"{len(results)} 件 ヒット")
            st.dataframe(results, use_container_width=True, hide_index=True)
        else:
            st.warning("見つかりませんでした。")
    else:
        st.info("👆 上のボックスに入力してください。")
        with st.expander("データ一覧（最初の50件）"):
            st.dataframe(df.head(50), use_container_width=True, hide_index=True)

else:
    st.error("⚠️ データファイル(data.xlsx)が見つかりません。")
