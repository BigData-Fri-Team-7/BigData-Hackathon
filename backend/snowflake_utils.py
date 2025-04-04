from dotenv import load_dotenv
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool

# Load .env credentials
load_dotenv()

# 🧠 Patent category classifier
def classify_patent(title: str) -> str:
    title = title.lower()
    if any(kw in title for kw in ["medical", "health", "hospital", "diagnosis"]):
        return "Healthcare"
    elif any(kw in title for kw in [
        "machine learning", "neural", "ai", "artificial intelligence",
        "deep learning", "natural language processing", "nlp", "text", "language model", "bert", "gpt"
    ]):
        return "Machine Learning"
    elif any(kw in title for kw in ["vision", "image", "detection", "camera"]):
        return "Computer Vision"
    else:
        return "Other"

# 🔍 LangChain Tool
@tool
def get_patents_by_category(prompt: str) -> str:
    """
    Filters and visualizes patents by category and generates bar chart, heatmap, and box plot.
    Input: Natural language prompt like 'Show machine learning patents over time'
    """
    try:
        df = pd.read_csv("top_1000_us_patents.csv")
        df["Category"] = df["Title"].apply(classify_patent)
        df["Publication Date"] = pd.to_datetime(df["Publication Date"])
        df["Year"] = df["Publication Date"].dt.year

        # Extract category from prompt
        categories = ["Healthcare", "Machine Learning", "Computer Vision", "Other"]
        match = next((cat for cat in categories if cat.lower() in prompt.lower()), None)

        if not match:
            return f"No matching category found in prompt. Available: {', '.join(categories)}"

        filtered = df[df["Category"] == match]
        if filtered.empty:
            return f"No patents found for category '{match}'."

        counts = filtered.groupby("Year").size()

        # 📊 Bar Chart: Patents per year for selected category
        plt.figure(figsize=(10, 5))
        counts.plot(kind="bar", color="teal")
        plt.title(f"{match} Patents Per Year")
        plt.xlabel("Year")
        plt.ylabel("Number of Patents")
        plt.xticks(rotation=45)
        plt.tight_layout()
        file_name = f"{match.lower().replace(' ', '_')}_patents.png"
        plt.savefig(file_name)
        plt.close()

        # 🔥 Heatmap: All categories vs. years
        pivot_df = df.groupby(["Category", "Year"]).size().unstack(fill_value=0)
        plt.figure(figsize=(10, 6))
        sns.heatmap(pivot_df, annot=True, fmt="d", cmap="YlGnBu", linewidths=0.5)
        plt.title("Patent Heatmap by Category and Year")
        plt.xlabel("Year")
        plt.ylabel("Category")
        plt.tight_layout()
        heatmap_file = "patent_heatmap.png"
        plt.savefig(heatmap_file)
        plt.close()

        # 📦 Box Plot: Distribution of patent years by category
        plt.figure(figsize=(10, 6))
        sns.boxplot(x="Category", y="Year", data=df)
        plt.title("Box Plot of Patent Years by Category")
        plt.ylabel("Publication Year")
        plt.xlabel("Patent Category")
        plt.tight_layout()
        boxplot_file = "patent_boxplot.png"
        plt.savefig(boxplot_file)
        plt.close()

                # 🧠 Word Cloud: Common terms in patent titles
        from wordcloud import WordCloud

        all_titles = " ".join(df["Title"].dropna())
        wordcloud = WordCloud(width=1000, height=500, background_color='white', colormap='viridis').generate(all_titles)

        plt.figure(figsize=(12, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.title("Word Cloud of Patent Titles", fontsize=16)
        plt.tight_layout()
        wordcloud_file = "patent_title_wordcloud.png"
        plt.savefig(wordcloud_file)
        plt.close()

        # 📊 Title Length Histogram
        df["Title Length"] = df["Title"].str.len()
        plt.figure(figsize=(10, 5))
        plt.hist(df["Title Length"].dropna(), bins=30, color='skyblue', edgecolor='black')
        plt.title("Distribution of Patent Title Lengths", fontsize=14)
        plt.xlabel("Title Length (Characters)")
        plt.ylabel("Number of Patents")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        histogram_file = "patent_title_length_histogram.png"
        plt.savefig(histogram_file)
        plt.close()

        # 📈 Year-wise summary for the selected category
        summary = "\n".join([f"{year}: {count}" for year, count in counts.items()])

        return (
            f"📊 Charts saved:\n"
            f"- Bar chart: `{file_name}`\n"
            f"- Heatmap: `{heatmap_file}`\n"
            f"- Box plot: `{boxplot_file}`\n\n"
            f"📈 Patent Counts Per Year for {match}:\n{summary}"
        )

    except Exception as e:
        return f"❌ Error processing request: {e}"

# 🔮 LLM + Agent
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

agent = initialize_agent(
    tools=[get_patents_by_category],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)
