import streamlit as st
import pandas as pd

# ==========================================
# ★設定エリア：ここにブログのURLを入れてください
BLOG_URL = "https://your-blog-url.com" 
# ==========================================

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

# --- ★プロテクト機能★ ---
# URLに「?embed=true」という合言葉がない場合、警告を出して停止する
query_params = st.query_params
if "embed" not in query_params:
    st.warning("⚠️ このツールはブログ記事内でのみ利用可能です。")
    st.info("以下のリンクから正規ページへ移動してください。")
    st.markdown(f"👉 **[検索ツールのページへ移動する]({BLOG_URL})**")
    st.stop()  # ここでプログラムを強制停止

# --- 2. データの読み込み ---
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

# --- 3. アプリの画面構成 ---
st.subheader("🎤 ポコチャカラオケ検索ツール")

if df is not None:
    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input("", placeholder="キーワードを入力（例：EXILE, マリーゴールド）", label_visibility="collapsed")
    
    st.markdown("---")

    if search_query:
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
    st.error("⚠️ データファイルが見つかりません。")