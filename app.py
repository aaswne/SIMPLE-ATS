import pandas as pd
import streamlit as st
import os
import re

st.set_page_config(page_title="HIRENGINE ATS", layout="wide")
st.title("📂 HIRENGINE - CLIENT DATA")

# Create a folder to save uploaded files
upload_folder = "uploaded_files"
os.makedirs(upload_folder, exist_ok=True)

# Upload Excel files
uploaded_files = st.file_uploader("Upload one or more Excel files", type=["xlsx"], accept_multiple_files=True)

if uploaded_files:
    df_list = []
    for file in uploaded_files:
        # Save uploaded file permanently
        file_path = os.path.join(upload_folder, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        
        # Read Excel into dataframe
        df = pd.read_excel(file)
        df.columns = df.columns.str.lower()  # normalize headers
        df_list.append(df)
    
    # Combine all files including previously uploaded files
    all_files = [os.path.join(upload_folder, f) for f in os.listdir(upload_folder) if f.endswith(".xlsx")]
    df_all_list = [pd.read_excel(f).rename(columns=str.lower) for f in all_files]
    df_all = pd.concat(df_all_list, ignore_index=True)
    
    st.success(f"✅ Loaded {len(df_all)} records from {len(all_files)} file(s)")

    # Search input
    query = st.text_input("🔎 Enter search keyword:")
    exact_match = st.toggle("🔒 Exact Match Only", value=False)  # Toggle for exact/partial search

    if query:
        keyword = query.lower()

        if exact_match:
            # Exact match: look for whole words
            filtered_df = df_all[df_all.apply(
                lambda row: row.astype(str).str.lower().str.split().apply(lambda words: keyword in words).any(),
                axis=1
            )]
        else:
            # Partial match: like substring search
            filtered_df = df_all[df_all.apply(
                lambda row: row.astype(str).str.lower().str.contains(keyword).any(),
                axis=1
            )]
        
        if not filtered_df.empty:
            st.write(f"### Results found: {len(filtered_df)}")

            # 🔹 Highlight matches
            def highlight_text(val):
                if isinstance(val, str):
                    pattern = fr"\b({re.escape(query)})\b" if exact_match else f"({re.escape(query)})"
                    return re.sub(pattern, r"<mark>\1</mark>", val, flags=re.IGNORECASE)
                return val

            highlighted_df = filtered_df.applymap(highlight_text)

            # Show with highlights
            st.write(highlighted_df.to_html(escape=False, index=False), unsafe_allow_html=True)

            # Download filtered results
            csv = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Results (CSV)", data=csv, file_name="search_results.csv", mime="text/csv")
        else:
            st.warning("No results found.")
