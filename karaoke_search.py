import streamlit as st
import pandas as pd
import time

# ==========================================
# ★設定エリア
SIGNUP_URL = "https://note.com/" 
INITIAL_LIMIT = 2   # 最初の検索回数
REWARD_LIMIT = 5    # 広告を見たときに追加される回数
# ==========================================

# --- 1. ページ設定 ---
st.set_page_config(page_title="Pocochaカラオケ検索", layout="centered")

# スタイル設定
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {
                padding-top: 1rem;
                padding-bottom: 2rem;
            }
            /* ツールバー非表示（DL防止） */
            [data-testid="stElementToolbar"] {
                display: none;
            }
            /* 残り回数の表示デザイン */
            .counter-box {
                padding: 10px;
                background-color: #f0f2f6;
                border-radius: 10px;
                text-align: center;
                font-weight: bold;
                color: #31333F;
                margin-bottom: 10px;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- 2. セッション状態の管理 ---
# ログイン状態
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = "ゲスト"

# 検索回数管理（ゲスト用）
if 'search_count' not in st.session_state:
    st.session_state.search_count = 0
if 'search_limit' not in st.session_state:
    st.session_state.search_limit = INITIAL_LIMIT
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""

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

# ==========================================
# 🟢 サイドバー（ログイン管理）
# ==========================================
with st.sidebar:
    st.title("⚙️ 設定")
    
    if st.session_state['logged_in']:
        st.success(f"ログイン中: {st.session_state['user_name']}")
        st.info("💎 プレミアム会員特典\n- 広告なし\n- 検索回数無制限")
        if st.button("ログアウト"):
            st.session_state['logged_in'] = False
            st.session_state['user_name'] = "ゲスト"
            st.rerun()
    else:
        st.info("ゲストモードで利用中")
        with st.expander("会員ログイン"):
            with st.form("login_form"):
                input_user = st.text_input("ユーザーID")
                input_pass = st.text_input("パスワード", type="password")
                submitted = st.form_submit_button("ログイン")
                
                if submitted:
                    if "users" in st.secrets and input_user in st.secrets["users"]:
                        if st.secrets["users"][input_user] == input_pass:
                            st.session_state['logged_in'] = True
                            st.session_state['user_name'] = input_user
                            st.success("成功！")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("パスワードが違います")
                    else:
                        st.error("IDがありません")
        
        st.markdown("---")
        st.markdown("🔰 **会員登録はこちら**")
        st.link_button("新規登録ページへ", SIGNUP_URL)

# ==========================================
# 📱 メイン画面ロジック
# ==========================================
st.subheader("🎤 Pococha カラオケ検索")

# 1. 残り回数の計算と表示（ゲストのみ）
is_premium = st.session_state['logged_in']
remaining = st.session_state.search_limit - st.session_state.search_count

if not is_premium:
    if remaining > 0:
        st.markdown(f"""
        <div class="counter-box">
            あと {remaining} 回 検索できます
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("🔒 無料分の検索回数が終わりました")

# 2. 検索ボックスの表示
# 制限オーバーのゲストには、入力ボックスを無効化（disabled）する
disable_input = (not is_premium) and (remaining <= 0)

query = st.text_input(
    "曲名・歌手名を入力", 
    placeholder="例：マリーゴールド", 
    value=st.session_state.last_query,
    disabled=disable_input
)

# 3. 検索実行ロジック
if query:
    # 新しい検索ワードが入力された場合のみカウントを進める
    if query != st.session_state.last_query:
        if not is_premium:
            if remaining > 0:
                st.session_state.search_count += 1
                st.session_state.last_query = query
                st.rerun() # カウント更新のためにリロード
            else:
                # 制限オーバー時は検索させない
                pass
        else:
            st.session_state.last_query = query

    # 4. 結果表示 or 制限ブロック表示
    if not is_premium and remaining <= 0:
        # ==========================
        # 🚧 制限到達時の「広告リワード」画面
        # ==========================
        st.warning("続けて検索するには、広告を見て回数をチャージしてください（無料）。")
        
        st.markdown("### ✨ チャージチャンス！")
        
        # ★広告画像とリンク
        st.markdown("""
        <div style="text-align:center; border:2px solid #ff4b4b; padding:10px; border-radius:10px;">
            <p style="font-weight:bold; color:red;">👇 この広告をチェックしてチャージ 👇</p>
            <a href="https://amzn.to/YOUR_LINK_HERE" target="_blank">
                <img src="https://m.media-amazon.com/images/I/61kL0F-o1XL._AC_SL1000_.jpg" width="80%">
            </a>
            <br><br>
            <b>YAMAHA AG03</b><br>
            配信の必需品！音質が変わればランクも変わる。<br>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        # リワードボタン
        if st.button(f"🎁 広告を見ました（+{REWARD_LIMIT}回 追加）", use_container_width=True):
            st.session_state.search_limit += REWARD_LIMIT
            st.balloons() # 風船を飛ばす演出
            st.rerun()
            
        st.markdown("---")
        st.info("💡 会員登録すると、広告なしで無制限に使えます。")

    else:
        # ==========================
        # 🔍 通常の検索結果画面
        # ==========================
        if df is not None and query:
            mask = df.apply(lambda row: row.str.contains(query, case=False).any(), axis=1)
            results = df[mask]

            if len(results) > 0:
                st.success(f"✨ {len(results)} 件 ヒット")
                st.dataframe(results, use_container_width=True, hide_index=True)
            else:
                st.warning("見つかりませんでした。")
        elif not query:
             st.info("上のボックスに入力してください。")

else: # queryが空のとき
    if is_premium:
         st.info("プレミアム会員モード：無制限に検索可能です")
