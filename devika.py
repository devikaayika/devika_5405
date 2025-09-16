import streamlit as st
import pandas as pd
import re
from collections import Counter
from io import BytesIO

from PyPDF2 import PdfReader          # For reading PDF text
from wordcloud import WordCloud        # For the word cloud
import matplotlib.pyplot as plt        # Needed by WordCloud
import plotly.express as px            # For scatter & line charts

# ---------------- Streamlit Page Setup ----------------
st.set_page_config(page_title="PDF Text Visualizer", layout="wide")
st.title("📑 PDF Text Visualization")

# ---------------- File Upload ----------------
uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_pdf is not None:
    # -------- Extract Text from PDF --------
    reader = PdfReader(uploaded_pdf)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "

    if not text.strip():
        st.error("No readable text found in this PDF.")
    else:
        # -------- Tokenize & Count --------
        words = re.findall(r"\b\w+\b", text.lower())
        counter = Counter(words)
        freq_df = (
            pd.DataFrame(counter.items(), columns=["Word", "Count"])
            .sort_values(by="Count", ascending=False)
            .reset_index(drop=True)
        )
        freq_df["Rank"] = range(1, len(freq_df) + 1)

        # -------- Summary --------
        st.subheader("Summary")
        st.write(f"*Total Words:* {len(words)}")
        st.write(f"*Unique Words:* {len(counter)}")

        with st.expander("Preview Extracted Text"):
            st.text(text[:1500] + ("..." if len(text) > 1500 else ""))

        # -------- Word Cloud --------
        st.subheader("☁ Word Cloud")
        wc = WordCloud(width=800, height=400,
                       background_color="white",
                       max_words=200).generate_from_frequencies(counter)
        fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
        ax_wc.imshow(wc, interpolation="bilinear")
        ax_wc.axis("off")
        st.pyplot(fig_wc)

        # -------- Scatter Plot --------
        st.subheader("📈 Scatter Plot (Word Rank vs Frequency)")
        scatter_fig = px.scatter(
            freq_df,
            x="Rank",
            y="Count",
            hover_data=["Word"],
            title="Word Frequency Scatter Plot",
        )
        st.plotly_chart(scatter_fig, use_container_width=True)

        # -------- Line Chart --------
        st.subheader("📊 Line Chart (Frequency Distribution)")
        line_fig = px.line(
            freq_df,
            x="Rank",
            y="Count",
            title="Word Frequency Line Chart",
        )
        st.plotly_chart(line_fig, use_container_width=True)

        # -------- Full Table --------
        st.subheader("📋 Word Frequency Table")
        st.dataframe(freq_df, use_container_width=True)

else:
    st.info("Please upload a PDF file to visualize its text.")
