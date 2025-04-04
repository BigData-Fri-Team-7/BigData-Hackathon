#app.py
import os
import re
import time
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
from s3_manager import list_pdfs, download_pdf_from_s3
from pdf_processor import process_pdf
from rag_agent import build_graph, RAGState
from websearch_agent import build_patent_query, serpapi_search  # newly imported for web search
from snowflake_proto import fetch_patent_data, classify_patent

# Load environment variables from .env
load_dotenv()

app = FastAPI(title="Patent Analytics Research API")

# -----------------------------
# Pydantic Models
# -----------------------------
class SearchRequest(BaseModel):
    query: str
    num_results: int = 10

class PatentSelection(BaseModel):
    source: str  # only "s3" is supported
    identifier: str  # S3 PDF key

class ReportRequest(BaseModel):
    question: str
    top_k: int = 500

class SummaryRequest(BaseModel):
    question: str

class AggregateRequest(BaseModel):
    query: str
    num_results: int = 10
    top_k: int = 500
    chart_type: str = "bar"

# -----------------------------
# Models for Agentic Endpoint
# -----------------------------
class AgentReportRequest(BaseModel):
    patent_number: str
    patent_title: str  # Added field to capture the patent title from the frontend
    template: Optional[str] = """
ENHANCED PROMPT

Instruction to the Model:  
Act as a senior patent analyst with expertise in patent law, technical due diligence, and commercialization strategy. You have been provided with extensive chunks of text/data about patent [PATENT_NUMBER]. Using those details, produce a comprehensive research report that addresses each of the following sections in depth.

--------------------------------------------------------------------------------
1. FRONT MATTER
   - Patent Number: [PATENT_NUMBER]
   - Title: <Insert Patent Title>
   - Inventors: <List Inventor Names>
   - Assignee (if applicable): <Entity or Organization>
   - Priority Date: <Priority Date>
   - Filing Date: <Filing Date>
   - Issue/Publications Date: <Issue or Publication Date>

2. EXECUTIVE SUMMARY
   - Problem/Background: Provide a concise overview of the technical or market problem(s) the invention addresses.
   - Solution: Summarize the core inventive concept and how it solves the stated problem(s).
   - Uniqueness: Highlight the key differentiators that set this invention apart from existing solutions or prior art.

3. TECHNICAL ANALYSIS
   - Classification Codes (CPC/IPC/USPC): List and briefly explain the relevant classification codes indicating the technological domain(s).
   - Key Components & Method Steps: Provide a bullet-point breakdown of the invention’s main components, embodiments, or processes. Focus on functionality and technical effects.
   - Detailed Novelty Discussion: Identify specific novel elements or method steps that potentially distinguish this invention over prior art. Discuss how these elements improve or optimize existing solutions.

4. CLAIM ANALYSIS
   - Independent Claims: Summarize each independent claim, noting critical elements and language that define the scope of protection.
   - Dependent Claims: Provide a brief overview of the additional details or limitations introduced by dependent claims.
   - Key Claim Limitations: Point out any critical limitations that could affect infringement or patentability.

5. EMBODIMENTS & ILLUSTRATIVE EXAMPLES
   - Main Embodiments: Discuss the primary embodiments described in the patent.
   - Alternative/Additional Embodiments: Note any alternative designs or variations that broaden the application.
   - Technical Drawings & Figures: Briefly describe the essential figures and how they illustrate the invention.

6. PRIOR ART & BACKGROUND REFERENCES
   - Referenced Prior Art: Identify any prior art mentioned in the specification or cited by examiners.
   - Comparison to Prior Art: Explain how the invention differs and advances beyond prior art.
   - Potential Art Gaps: Mention any areas where the invention might be strong or vulnerable relative to known solutions.

7. LEGAL STATUS & PROSECUTION HISTORY
   - Current Legal Status: Is the patent granted, pending, or abandoned? Note any continuations or divisionals.
   - Family Members: List relevant domestic and international family members.
   - Key Prosecution Details: Summarize any notable office actions, arguments made by the applicant, or rejections.

8. COMMERCIAL VALUE & MARKET APPLICATIONS
   - Applicable Industries: Identify industries or sectors likely to benefit from or adopt this technology.
   - Market Size & Growth: Provide high-level estimates or insights on potential market size.
   - Potential Licensees/Partners: Suggest companies or organizations that might be interested in licensing or collaborating.

9. COMPETITIVE LANDSCAPE & RELATED PATENTS
   - Competitor Analysis: Identify major competitors and their related patent filings or products.
   - Related Patents: List and briefly describe similar or closely related patents that might compete or complement.
   - Freedom to Operate Considerations: Highlight any obstacles or blocking patents.

10. RISKS & LIMITATIONS
   - Validity Concerns: Discuss potential challenges to patent validity, such as prior art or indefiniteness.
   - Enforceability: Identify any ambiguities in claim language or potential design-around opportunities.
   - Commercial & Regulatory Risks: Mention business, regulatory, or adoption risks.

11. POTENTIAL MONETIZATION & LICENSING STRATEGY
   - Licensing Approaches: Outline possible licensing models (e.g., exclusive, non-exclusive, cross-licensing).
   - Royalty Structures: Suggest typical royalty ranges or lump-sum payments.
   - Litigation Strategies: If relevant, discuss infringement assertion or litigation potential.

12. STRATEGIC RECOMMENDATIONS
   - Next Steps: Provide actionable steps for further R&D, prosecution strategies, or business development.
   - Portfolio Integration: How does this patent fit into a broader IP portfolio? Any synergy with existing patents?
   - Strengthening the Patent: Suggest ways to broaden or refine claims, or build continuation applications.

13. CONCLUSION
   - Overall Assessment: Provide a concise final evaluation of the patent’s strength, market potential, and strategic value.
   - Key Takeaways: List three to five primary insights or recommendations from your analysis.

--------------------------------------------------------------------------------
ADDITIONAL GUIDELINES FOR THE MODEL
- Depth & Specificity: For each section, incorporate relevant data from the provided patent chunks. Include numerical estimates, examples, or comparisons wherever possible.
- Structured & Logical Flow: Maintain clear headings and subheadings. Use bullet points or tables for clarity when listing items.
- Technical & Legal Accuracy: Use precise terminology consistent with patent documentation. Clarify or interpret complex technical aspects in a comprehensible manner.
- Impartial Analysis: Present both strengths and weaknesses candidly. Avoid excessive marketing language.
- Citations & References: Where applicable, cross-reference relevant paragraphs, figures, or claim numbers to ensure traceability.

"""


class AgentReportResponse(BaseModel):
    summary: str
    extracted_title: str
    related_patents: List[dict]

# -----------------------------
# Existing Endpoints
# -----------------------------
@app.post("/list_s3_pdfs")
def list_s3_pdfs_endpoint():
    try:
        pdfs = list_pdfs()
        return {"pdfs": pdfs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_patent")
def process_patent_endpoint(selection: PatentSelection):
    try:
        if selection.source != "s3":
            raise Exception("Only 's3' source is supported.")
        pdf_path = download_pdf_from_s3(selection.identifier)
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        from embedding_manager import upsert_embeddings
        processed = process_pdf(pdf_bytes)
        metadata = {"source": selection.identifier}
        upsert_embeddings(processed.get("chunks", []), metadata)
        processed["pinecone_status"] = "Embeddings upserted successfully."
        return {"processed_data": processed}
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_summary")
async def generate_summary(request: SummaryRequest):
    try:
        rag_graph = build_graph()
        result = rag_graph.invoke({
            "question": request.question,
            "top_k": 500
        })
        return {"summary": result.get("rag_output", "No summary generated.")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

# -----------------------------
# Utility Function for Agentic Behavior
# -----------------------------
def extract_title_from_summary(summary: str) -> str:
    """
    Extracts the patent title from the report summary.
    Looks for a line starting with "- Title:" and returns the text after it.
    """
    pattern = r"(?im)^- *Title:\s*(.+)$"
    match = re.search(pattern, summary)
    if match:
        return match.group(1).strip()
    return "Title not found"

# -----------------------------
# New Augmented Agentic Endpoint
# -----------------------------
@app.post("/generate_augmented_report", response_model=AgentReportResponse)
def generate_augmented_report(request: AgentReportRequest):
    patent_number = request.patent_number.strip()
    supplied_patent_title = request.patent_title.strip()
    template = request.template
    summary = ""
    extracted_title = ""

    # Generate internal report using the RAG agent; retry up to 3 times if title extraction fails.
    for attempt in range(3):
        question = template.replace("[PATENT_NUMBER]", patent_number)
        try:
            rag_graph = build_graph()
            result = rag_graph.invoke({
                "question": question,
                "top_k": 500
            })
            summary = result.get("rag_output", "")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating report: {e}")
        
        extracted_title = extract_title_from_summary(summary)
        if extracted_title != "Title not found":
            break
        time.sleep(1)
    
    # If the internal report didn't yield a title, fallback to the supplied title.
    if extracted_title == "Title not found":
        extracted_title = supplied_patent_title

    # Augment the report with related patents obtained from the web search.
    # Use the supplied patent title for building the search query.
    web_query = build_patent_query(supplied_patent_title)
    web_results = serpapi_search(web_query, num_results=10)

    related_patents = []
    for patent in web_results.get("organic_results", []):
        related_patents.append({
            "title": patent.get("title", "No Title"),
            "link": patent.get("patent_link") or patent.get("link") or patent.get("scholar_link", ""),
            "snippet": patent.get("snippet", "No snippet available"),
            "publication_date": patent.get("publication_date", "Unknown"),
            "filing_date": patent.get("filing_date", "N/A"),
            "inventor": patent.get("inventor", "Unknown"),
            "assignee": patent.get("assignee", "Unknown")
        })

    return AgentReportResponse(
        summary=summary,
        extracted_title=extracted_title,
        related_patents=related_patents
    )


# Define request/response models for the new endpoint.
class DomainBarChartRequest(BaseModel):
    processed_patent_id: str
    processed_patent_title: str

class DomainBarChartResponse(BaseModel):
    chart: str
    message: str

# Add the new endpoint to your existing app.py:
@app.post("/generate_domain_bar_chart", response_model=DomainBarChartResponse)
def generate_domain_bar_chart(request: DomainBarChartRequest):
    processed_patent_id = request.processed_patent_id.strip()
    processed_patent_title = request.processed_patent_title.strip()
    
    # Determine the domain using your keyword-based classifier.
    processed_domain = classify_patent(processed_patent_title)
    
    # Fetch data from Snowflake.
    df = fetch_patent_data()
    
    # Normalize PATENT_ID (remove hyphens) and locate the processed patent.
    df['normalized_id'] = df['PATENT_ID'].str.replace("-", "", regex=False)
    matching = df[df['normalized_id'].str.startswith(processed_patent_id)]
    if matching.empty:
        raise HTTPException(status_code=404, detail="Processed patent not found in Snowflake data.")
    processed_record = matching.iloc[0]
    ref_date = processed_record["PUBLICATION_DATE"]
    
    # Filter for patents published in the last 5 years relative to the processed patent's publication date.
    from dateutil.relativedelta import relativedelta
    five_years_ago = ref_date - relativedelta(years=5)
    filtered_df = df[df["PUBLICATION_DATE"] >= five_years_ago].copy()
    
    # Classify each patent using its TITLE.
    filtered_df["Domain"] = filtered_df["TITLE"].apply(classify_patent)
    
    # Keep only patents that are in the same domain as the processed patent.
    domain_filtered_df = filtered_df[filtered_df["Domain"] == processed_domain].copy()
    
    # Extract the publication year.
    domain_filtered_df["year"] = domain_filtered_df["PUBLICATION_DATE"].dt.year.astype(int)
    
    # Group by publication year and count the patents.
    agg_df = domain_filtered_df.groupby("year").size().reset_index(name="patent_count")
    agg_df["year"] = agg_df["year"].astype(str)  # treat year as discrete category
    
    # Create a bar chart using Plotly.
    import plotly.express as px
    import plotly.io as pio
    fig = px.bar(
        agg_df,
        x="year",
        y="patent_count",
        text="patent_count",
        title=f"Number of '{processed_domain}' Patents Published Per Year (Last 5 Years)\nProcessed Patent: {processed_patent_id}",
        labels={"year": "Publication Year", "patent_count": "Number of Patents"}
    )
    fig.update_traces(textposition="outside")
    
    # Serialize the Plotly figure to JSON.
    fig_json = pio.to_json(fig)
    return DomainBarChartResponse(chart=fig_json, message="Domain bar chart generated successfully")


# -----------------------------
# Endpoints for Other Visualizations
# -----------------------------
from snowflake_proto import fetch_patent_data, classify_patent
from snowflake_visualizations import (
    generate_bar_chart,
    generate_heatmap,
    generate_boxplot,
    generate_wordcloud
)

class InteractiveVizResponse(BaseModel):
    chart: str
    message: str

@app.post("/generate_heatmap", response_model=InteractiveVizResponse)
def generate_heatmap_endpoint():
    try:
        chart_json = generate_heatmap()
        return InteractiveVizResponse(chart=chart_json, message="Interactive heatmap generated successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_boxplot", response_model=InteractiveVizResponse)
def generate_boxplot_endpoint():
    try:
        chart_json = generate_boxplot()
        return InteractiveVizResponse(chart=chart_json, message="Interactive box plot generated successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_wordcloud", response_model=InteractiveVizResponse)
def generate_wordcloud_endpoint():
    try:
        chart_json = generate_wordcloud()
        return InteractiveVizResponse(chart=chart_json, message="Interactive word cloud generated successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
