import streamlit as st
import pandas as pd

# --- 1. ページ設定 ---
st.set_page_config(page_title="ポコチャカラオケ検索", layout="wide")

# 見た目をスッキリさせる設定
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                padding-left: 2rem;
                padding-right: 2rem;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- 2. データの読み込み（最強モード） ---
@st.cache_data
def load_data():
    try:
        # フォルダ内の 'data.xlsx' を読み込みます
        all_sheets = pd.read_excel("data.xlsx", sheet_name=None, header=None)
        
        df_list = []
        for sheet_name, sheet_df in all_sheets.items():
            # 列番号を強制的にリセット
            sheet_df.columns = range(sheet_df.shape[1])
            df_list.append(sheet_df)
        
        # 合体
        df = pd.concat(df_list, ignore_index=True)
        df = df.fillna("").astype(str)
        
        # 列名を変更
        rename_map = {0: "歌手名", 1: "楽曲名"}
        df = df.rename(columns=rename_map)

        # 必要な列だけ残す
        if "歌手名" in df.columns and "楽曲名" in df.columns:
            df = df[["歌手名", "楽曲名"]]

        # ゴミ掃除
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

# --- 3. 画面表示 ---
st.title("🎤 ポコチャカラオケ検索")

if df is not None:
    # 検索ボックス
    search_query = st.text_input("曲名・歌手名を入力", placeholder="例: マリーゴールド")
    
    if search_query:
        # 検索実行
        mask = df.apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
        results = df[mask]

        st.success(f"{len(results)} 件 ヒットしました")
        
        if len(results) > 0:
            st.dataframe(results, use_container_width=True, hide_index=True)
        else:
            st.warning("見つかりませんでした。")
    else:
        # 何も入力していない時は全リストを少し表示
        st.info("👇 全リスト")
        st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.error("⚠️ データファイルが見つかりません。")
    st.info("同じフォルダに『data.xlsx』を入れてください。")
