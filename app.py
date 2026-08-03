import streamlit as st
import pandas as pd
from database import init_db, get_all_articles
from pipeline import run_pipeline
from excel_export import export_to_excel

st.set_page_config(page_title="NewsPulse", page_icon="📰", layout="wide")

init_db()

st.title("📰 NewsPulse — AI-Powered News Intelligence Dashboard")
st.caption("Scrapes news, uses an LLM (Groq/Llama 3.3) to summarize and classify, and visualizes trends.")

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🔄 Run Scraper Now"):
        with st.spinner("Scraping + AI summarizing... this takes longer since each new article calls the AI."):
            run_pipeline()
        st.success("Done! Refreshing data below.")

    if st.button("📊 Generate Excel Report"):
        export_to_excel("newspulse_report.xlsx")
        st.session_state["excel_ready"] = True

    if st.session_state.get("excel_ready"):
        with open("newspulse_report.xlsx", "rb") as f:
            st.download_button(
                label="⬇️ Download Excel Report",
                data=f,
                file_name="newspulse_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

articles = get_all_articles()

if not articles:
    st.info("No articles yet — click 'Run Scraper Now' to fetch some.")
else:
    df = pd.DataFrame(articles)

    st.subheader(f"Total articles stored: {len(df)}")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Articles by Category")
        category_counts = df["category"].value_counts()
        st.bar_chart(category_counts)

    with chart_col2:
        st.subheader("Sentiment Breakdown")
        sentiment_counts = df["sentiment"].value_counts()
        st.bar_chart(sentiment_counts)

    st.subheader("Latest Articles (with AI Summary)")
    display_df = df[["source", "title", "summary", "category", "sentiment", "url", "scraped_at"]]
    st.dataframe(display_df, use_container_width=True, hide_index=True)