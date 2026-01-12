import streamlit as st
import pandas as pd

# --- 1. ページ設定 ---
st.set_page_config(page_title="Pocochaカラオケ検索", layout="wide")

# スタイル設定（見た目を整える）
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

# ==========================================
# ★パスワード設定エリア
# 好きなパスワードに変更してください（現在は '2026'）
SECRET_PASSWORD = "2026"
# ==========================================

# --- 2. パスワード認証機能 ---
st.subheader("🔒 カラオケ検索ツール")

# パスワード入力ボックス（type="password"で文字が伏せ字になります）
input_password = st.text_input("パスワードを入力してください", type="password")

# パスワードが合っているかチェック
if input_password != SECRET_PASSWORD:
    st.info("管理者が設定したパスワードを入力すると利用できます。")
    st.stop()  # ここでプログラムを停止させ、以下の画面を見せない

# --- 3. データの読み込み（認証通過後に実行） ---
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
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"読み込みエラー: {e}")
        return None

df = load_data()

# --- 4. 検索画面（パスワード正解時のみ表示） ---
st.markdown("---") # 区切り線

if df is not None:
    # 検索ボックス
    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input("", placeholder="キーワードを入力（例：EXILE, マリーゴールド）", label_visibility="collapsed")
    
    # 少し隙間を開ける
    st.write("")

    if search_query:
        # 検索実行
        mask = df.apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
        results = df[mask]

        if len(results) > 0:
            st.success(f"{len(results)} 件 ヒット")
            st.dataframe(results, use_container_width=True, hide_index=True)
        else:
            st.warning("見つかりませんでした。")
    else:
        st.info("👆 上のボックスに探したい曲名や歌手名を入力してください。")
        with st.expander("データを確認（最初の50件）"):
            st.dataframe(df.head(50), use_container_width=True, hide_index=True)

else:
    st.error("⚠️ データファイル(data.xlsx)が見つかりません。")
