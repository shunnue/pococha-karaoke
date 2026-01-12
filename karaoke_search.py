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
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = "ゲスト"
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

# 2. 検索ボックスの制御
disable_input = (not is_premium) and (remaining <= 0)

query = st.text_input(
    "曲名・歌手名を入力", 
    placeholder="例：マリーゴールド", 
    value=st.session_state.last_query,
    disabled=disable_input
)

# 3. 検索実行ロジック
if query:
    if query != st.session_state.last_query:
        if not is_premium:
            if remaining > 0:
                st.session_state.search_count += 1
                st.session_state.last_query = query
                st.rerun()
            else:
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
        
        # ★★★ 楽天アフィリエイトHTML（インデント対策済み） ★★★
        # HTMLを変数に入れて、左詰めで定義することでバグを防ぎます
        rakuten_ad_html = """
<div style="text-align:center; border:2px solid #bf0000; padding:15px; border-radius:10px; background-color:#fff;">
<p style="font-weight:bold; color:#bf0000; margin-bottom:10px;">👇 スポンサーサイトをチェックしてチャージ 👇</p>
<a href="https://hb.afl.rakuten.co.jp/hsc/4ffa876e.80dc9404.4ffa8711.4e90cb43/_RTLink123938?link_type=pict&ut=eyJwYWdlIjoic2hvcCIsInR5cGUiOiJwaWN0IiwiY29sIjoxLCJjYXQiOiI1OCIsImJhbiI6MzIzMDk1MSwiYW1wIjpmYWxzZX0%3D" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;"><img src="https://hbb.afl.rakuten.co.jp/hsb/4ffa876e.80dc9404.4ffa8711.4e90cb43/?me_id=1&me_adv_id=3230951&t=pict" border="0" style="margin:2px" alt="" title=""></a>
<br><br>
<div style="font-size:0.9rem; color:#333;">
<b>楽天市場でお得な商品をチェック！</b><br>
人気の配信機材やアイテムが勢揃い。
</div>
</div>
"""
        st.markdown(rakuten_ad_html, unsafe_allow_html=True)
        # ★★★★★★★★★★★★★★★★★★★★★★★★★
        
        st.write("")
        # リワードボタン
        if st.button(f"🎁 広告を見ました（+{REWARD_LIMIT}回 追加）", use_container_width=True):
            st.session_state.search_limit += REWARD_LIMIT
            st.balloons()
            st.rerun()
            
        st.markdown("---")
        st.info("💡 会員登録すると、広告なしで無制限に使えます。")

    else:
        # 🔍 通常の検索結果画面
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

else:
    if is_premium:
         st.info("プレミアム会員モード：無制限に検索可能です")
