import streamlit as st
import pandas as pd
from database import init_db, get_all_articles
from pipeline import run_pipeline

st.set_page_config(page_title="NewsPulse", page_icon="📰", layout="wide")

init_db()

st.title("📰 NewsPulse — News Intelligence Dashboard")
st.caption("Scrapes news sources, stores articles, and tracks trends.")

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🔄 Run Scraper Now"):
        with st.spinner("Scraping sources..."):
            run_pipeline()
        st.success("Done! Refreshing data below.")

articles = get_all_articles()

if not articles:
    st.info("No articles yet — click 'Run Scraper Now' to fetch some.")
else:
    df = pd.DataFrame(articles)

    st.subheader(f"Total articles stored: {len(df)}")

    st.subheader("Articles by Source")
    source_counts = df["source"].value_counts()
    st.bar_chart(source_counts)

    st.subheader("Latest Articles")
    display_df = df[["source", "title", "url", "scraped_at"]]
    st.dataframe(display_df, use_container_width=True, hide_index=True)