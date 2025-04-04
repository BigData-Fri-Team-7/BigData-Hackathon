#snowflake_visualization.py
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from wordcloud import WordCloud
from snowflake_proto import fetch_patent_data, classify_patent

def generate_bar_chart(category: str) -> tuple[str, str]:
    """
    Generates an interactive Plotly bar chart of the number of patents per year
    for the given category. Returns the figure as JSON and a text summary.
    """
    df = fetch_patent_data()
    df["Category"] = df["TITLE"].apply(classify_patent)
    df["Year"] = pd.to_datetime(df["PUBLICATION_DATE"]).dt.year
    filtered = df[df["Category"] == category]
    if filtered.empty:
        raise ValueError(f"No patents found for category '{category}'.")
    counts = filtered.groupby("Year").size().reset_index(name="patent_count")
    
    fig = px.bar(
        counts,
        x="Year",
        y="patent_count",
        text="patent_count",
        title=f"{category} Patents Per Year",
        labels={"Year": "Year", "patent_count": "Number of Patents"}
    )
    fig.update_traces(textposition="outside")
    
    fig_json = pio.to_json(fig)
    summary = "\n".join([f"{row['Year']}: {row['patent_count']}" for _, row in counts.iterrows()])
    return fig_json, summary

def generate_heatmap() -> str:
    """
    Generates an interactive Plotly heatmap of patent counts by category and year.
    Returns the figure as a JSON string.
    """
    df = fetch_patent_data()
    df["Category"] = df["TITLE"].apply(classify_patent)
    df["Year"] = pd.to_datetime(df["PUBLICATION_DATE"]).dt.year
    pivot_df = df.groupby(["Category", "Year"]).size().unstack(fill_value=0)
    
    fig = px.imshow(
        pivot_df,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="YlGnBu",
        labels={"x": "Year", "y": "Category", "color": "Patent Count"},
        title="Patent Heatmap by Category and Year"
    )
    return pio.to_json(fig)

def generate_boxplot() -> str:
    """
    Generates an interactive Plotly box plot showing the distribution of
    publication years by patent category. Returns the figure as JSON.
    """
    df = fetch_patent_data()
    df["Category"] = df["TITLE"].apply(classify_patent)
    df["Year"] = pd.to_datetime(df["PUBLICATION_DATE"]).dt.year
    fig = px.box(
        df,
        x="Category",
        y="Year",
        title="Box Plot of Patent Years by Category",
        labels={"Category": "Patent Category", "Year": "Publication Year"}
    )
    return pio.to_json(fig)

def generate_wordcloud() -> str:
    """
    Generates an interactive Plotly-based word cloud of all patent titles.
    Returns the figure as a JSON string.
    """
    df = fetch_patent_data()
    all_titles = " ".join(df["TITLE"].dropna())
    wc = WordCloud(width=1000, height=500, background_color='white', colormap='viridis').generate(all_titles)
    
    words = []
    x_vals = []
    y_vals = []
    sizes = []
    for (word, font_size, position, orientation, color) in wc.layout_:
        words.append(word)
        x_vals.append(position[0])
        y_vals.append(position[1])
        sizes.append(font_size)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='text',
        text=words,
        textfont=dict(size=sizes, color='black')
    ))
    fig.update_layout(
        title="Word Cloud of Patent Titles",
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False)
    )
    return pio.to_json(fig)

if __name__ == "__main__":
    # For testing purposes:
    print("Generating Bar Chart for Healthcare...")
    bar_json, bar_summary = generate_bar_chart("Healthcare")
    print("Bar Chart JSON generated.")
    print(bar_summary)
    
    print("Generating Heatmap...")
    heatmap_json = generate_heatmap()
    print("Heatmap JSON generated.")
    
    print("Generating Box Plot...")
    boxplot_json = generate_boxplot()
    print("Box Plot JSON generated.")
    
    print("Generating Word Cloud...")
    wordcloud_json = generate_wordcloud()
    print("Word Cloud JSON generated.")
