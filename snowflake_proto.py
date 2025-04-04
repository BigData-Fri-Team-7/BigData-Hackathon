import os
import snowflake.connector as connector
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
import plotly.io as pio
from dotenv import load_dotenv

load_dotenv()


def fetch_patent_data():
    """
    Connects to Snowflake and retrieves patent data from the 'patents_data' table.
    Expects columns: PATENT_ID, TITLE, PUBLICATION_DATE, RESULT_LINK.
    """
    conn = connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )
    cur = conn.cursor()
    query = "SELECT PATENT_ID, TITLE, PUBLICATION_DATE, RESULT_LINK FROM patents_data"
    cur.execute(query)
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=["PATENT_ID", "TITLE", "PUBLICATION_DATE", "RESULT_LINK"])
    df["PUBLICATION_DATE"] = pd.to_datetime(df["PUBLICATION_DATE"])
    cur.close()
    conn.close()
    return df

def classify_patent(title: str) -> str:
    """
    Classify a patent title into one of the domains using keyword mapping.
    
    Domains:
      - "Healthcare": if "medical", "health", "hospital", or "diagnosis" appear in the title.
      - "Machine Learning": if "machine learning", "neural", "ai", "artificial intelligence",
         "deep learning", "natural language processing", "nlp", "text", "language model", "bert", or "gpt" appear.
      - "Computer Vision": if "vision", "image", "detection", or "camera" appear.
      - Otherwise: "Other"
    """
    title_lower = title.lower()
    if any(kw in title_lower for kw in ["medical", "health", "hospital", "diagnosis"]):
        return "Healthcare"
    elif any(kw in title_lower for kw in [
        "machine learning", "neural", "ai", "artificial intelligence",
        "deep learning", "natural language processing", "nlp", "text", "language model", "bert", "gpt"
    ]):
        return "Machine Learning"
    elif any(kw in title_lower for kw in ["vision", "image", "detection", "camera"]):
        return "Computer Vision"
    else:
        return "Other"


def fetch_patent_data():
    """
    Connects to Snowflake and retrieves patent data from the 'patents_data' table.
    Expects columns: PATENT_ID, TITLE, PUBLICATION_DATE, RESULT_LINK.
    """
    conn = connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )
    cur = conn.cursor()
    query = "SELECT PATENT_ID, TITLE, PUBLICATION_DATE, RESULT_LINK FROM patents_data"
    cur.execute(query)
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=["PATENT_ID", "TITLE", "PUBLICATION_DATE", "RESULT_LINK"])
    df["PUBLICATION_DATE"] = pd.to_datetime(df["PUBLICATION_DATE"])
    cur.close()
    conn.close()
    return df

def classify_patent(title: str) -> str:
    """
    Classify a patent title into one of the domains using keyword mapping.
    
    Domains:
      - "Robotics": if "robot" is in the title.
      - "Medical Imaging": if both "medical" and "image" are in the title.
      - "Healthcare": if the title contains "medical", "allergy", "diagnosis", or "health".
      - "General Machine Learning": if it contains "machine learning", "deep learning", or "classifier".
      - Otherwise: "Other"
    """
    title_lower = title.lower()
    if "robot" in title_lower:
        return "Robotics"
    elif "medical" in title_lower and "image" in title_lower:
        return "Medical Imaging"
    elif "medical" in title_lower or "allergy" in title_lower or "diagnosis" in title_lower or "health" in title_lower:
        return "Healthcare"
    elif "machine learning" in title_lower or "deep learning" in title_lower or "classifier" in title_lower:
        return "General Machine Learning"
    else:
        return "Other"

def main():
    # Example processed patent details.
    processed_patent_id = "US10810491"  # Processed patent ID (without hyphens)
    processed_patent_title = "REAL TIME VISUALIZATION OF MACHINE LEARNING MODELS"

    # Determine the processed patent's domain.
    processed_domain = classify_patent(processed_patent_title)
    print("Processed Patent Domain:", processed_domain)
    
    # 1. Fetch data from Snowflake.
    df = fetch_patent_data()
    
    # 2. Normalize PATENT_ID (remove hyphens) and locate the processed patent.
    df['normalized_id'] = df['PATENT_ID'].str.replace("-", "", regex=False)
    matching = df[df['normalized_id'].str.startswith(processed_patent_id)]
    if matching.empty:
        raise ValueError("Processed patent not found in Snowflake data.")
    processed_record = matching.iloc[0]
    ref_date = processed_record["PUBLICATION_DATE"]
    print("Processed Patent Record:")
    print(processed_record)
    print("Reference Publication Date:", ref_date)
    
    # 3. Filter for patents published in the last 5 years relative to the processed patent's publication date.
    five_years_ago = ref_date - relativedelta(years=5)
    filtered_df = df[df["PUBLICATION_DATE"] >= five_years_ago].copy()
    
    # 4. Classify each patent using its TITLE.
    filtered_df["Domain"] = filtered_df["TITLE"].apply(classify_patent)
    
    # 5. Keep only patents that are in the same domain as the processed patent.
    domain_filtered_df = filtered_df[filtered_df["Domain"] == processed_domain].copy()
    
    # 6. Extract the publication year.
    domain_filtered_df["year"] = domain_filtered_df["PUBLICATION_DATE"].dt.year.astype(int)
    
    # 7. Group by publication year and count the number of patents.
    agg_df = domain_filtered_df.groupby("year").size().reset_index(name="patent_count")
    agg_df["year"] = agg_df["year"].astype(str)  # Ensure year is a discrete category.
    
    print("\nPatents in Domain '{}' by Year (Last 5 Years):".format(processed_domain))
    print(agg_df)
    
    # 8. Create a bar chart using Plotly.
    fig = px.bar(
        agg_df,
        x="year",
        y="patent_count",
        text="patent_count",
        title=f"Number of '{processed_domain}' Patents Published Per Year (Last 5 Years)\nProcessed Patent: {processed_patent_id}",
        labels={"year": "Publication Year", "patent_count": "Number of Patents"}
    )
    fig.update_traces(textposition="outside")
    
    # 9. Display the bar chart and save it as an HTML file.
    fig.show()
    pio.write_html(fig, file="patents_by_domain_filtered.html", auto_open=True, encoding="utf-8")

if __name__ == "__main__":
    main()
