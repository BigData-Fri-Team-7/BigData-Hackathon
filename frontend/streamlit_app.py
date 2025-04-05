import streamlit as st
import requests
import re
import plotly.io as pio

# Backend API URL
BASE_URL = "http://34.30.2.49:8000"

st.set_page_config(page_title="Patent Analytics Research Assistant", layout="wide")
st.title("📈 Patent Analytics Research Dashboard")

# --- Load and Select PDF ---
st.header("🔖 Select and Process Patent PDF")

if st.button("Load PDFs from S3"):
    with st.spinner("Loading PDFs from S3..."):
        pdfs = requests.post(f"{BASE_URL}/list_s3_pdfs").json().get("pdfs", [])
        st.session_state["pdfs"] = pdfs if pdfs else []

if "pdfs" in st.session_state and st.session_state["pdfs"]:
    selected_pdf = st.selectbox("Select PDF:", st.session_state["pdfs"])
    if st.button("Process PDF"):
        with st.spinner("Processing PDF..."):
            res = requests.post(f"{BASE_URL}/process_patent",
                                json={"source": "s3", "identifier": selected_pdf})
            if res.ok:
                processed_data = res.json().get("processed_data", {})
                
                # Extract filename without extension
                filename = selected_pdf.split("/")[-1].replace(".pdf", "")
                
                # Use regex to split into patent_number and patent_title
                match = re.match(r"^(\S+)\s+(.+)$", filename)
                if match:
                    patent_number, patent_title = match.groups()
                else:
                    patent_number = filename
                    patent_title = "Unknown Title"

                # Store in session state
                st.session_state["patent_number"] = patent_number
                st.session_state["patent_title"] = patent_title
                st.session_state["processed_pdf"] = selected_pdf

                st.success("PDF processed successfully!")
                st.markdown(f"**Patent Number:** {patent_number}")
                st.markdown(f"**Patent Title:** {patent_title}")
            else:
                st.error(f"Error: {res.text}")

# --- Augmented Report Generation ---
st.header("📚 Generate Patent Research Report with Web Augmentation")

default_template = """
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


with st.expander("Customize Report Template"):
    template = st.text_area("Research Report Template:", default_template, height=300)

patent_number = st.session_state.get("patent_number", "")
patent_title = st.session_state.get("patent_title", "")

if patent_number:
    st.markdown(f"**Patent Number:** {patent_number}")
    st.markdown(f"**Patent Title:** {patent_title}")
else:
    st.warning("No patent number found. Please process a PDF first.")

if st.button("Generate Augmented Research Report"):
    if patent_number and patent_title:
        payload = {
            "patent_number": patent_number,
            "patent_title": patent_title,
            "template": template
        }
        with st.spinner("Generating augmented research report... This may take a minute..."):
            res = requests.post(f"{BASE_URL}/generate_augmented_report", json=payload)
            if res.ok:
                report_data = res.json()
                st.session_state["summary"] = report_data.get("summary", "")
                st.session_state["related_patents"] = report_data.get("related_patents", [])
            else:
                st.error(f"Error: {res.text}")
    else:
        st.warning("Patent number and title are required to generate the report.")

if "summary" in st.session_state:
    st.subheader("Patent Research Report")
    st.markdown(st.session_state["summary"])

    if st.session_state.get("related_patents"):
        st.subheader("Related Patents from Web Search")
        for idx, patent in enumerate(st.session_state["related_patents"], 1):
            st.markdown(f"**Result {idx}: {patent.get('title')}**")
            st.markdown(f"Link: {patent.get('link')}")
            st.markdown(f"Snippet: {patent.get('snippet')}")
            st.markdown("---")

st.header("📊 Domain-Based Patent Visualization")

# Ensure that processed patent details exist in session state.
if "patent_number" not in st.session_state or "patent_title" not in st.session_state:
    st.warning("No processed patent details available. Please process a PDF first.")
else:
    patent_number = st.session_state["patent_number"]
    patent_title = st.session_state["patent_title"]
    
    st.markdown(f"**Processed Patent:** {patent_number} - {patent_title}")
    
    # (Optional) Allow user to override domain if desired.
    st.markdown("The domain will be automatically determined based on the processed patent title.")
    # In this case, the backend uses the processed patent title to classify the domain.
    
    if st.button("Generate Domain Bar Chart"):
        with st.spinner("Generating domain bar chart..."):
            payload = {
                "processed_patent_id": patent_number,
                "processed_patent_title": patent_title
            }
            res = requests.post(f"{BASE_URL}/generate_domain_bar_chart", json=payload)
            if res.ok:
                data = res.json()
                chart_json = data.get("chart", "")
                if chart_json:
                    fig = pio.from_json(chart_json)
                    st.plotly_chart(fig, use_container_width=True)
                    st.success(data.get("message", "Bar chart generated successfully."))
                else:
                    st.error("No chart data returned.")
            else:
                st.error(f"Error: {res.text}")

st.header("Additional Visualizations")
tab1, tab2, tab3 = st.tabs(["Heatmap", "Box Plot", "Word Cloud"])

with tab1:
    if st.button("Generate Heatmap"):
        with st.spinner("Generating heatmap..."):
            res = requests.post(f"{BASE_URL}/generate_heatmap")
            if res.ok:
                data = res.json()
                chart_json = data.get("chart", "")
                if chart_json:
                    fig = pio.from_json(chart_json)
                    st.plotly_chart(fig, use_container_width=True)
                    st.success(data.get("message", "Heatmap generated successfully."))
                else:
                    st.error("No chart data returned.")
            else:
                st.error(f"Error: {res.text}")

with tab2:
    if st.button("Generate Box Plot"):
        with st.spinner("Generating box plot..."):
            res = requests.post(f"{BASE_URL}/generate_boxplot")
            if res.ok:
                data = res.json()
                chart_json = data.get("chart", "")
                if chart_json:
                    fig = pio.from_json(chart_json)
                    st.plotly_chart(fig, use_container_width=True)
                    st.success(data.get("message", "Box plot generated successfully."))
                else:
                    st.error("No chart data returned.")
            else:
                st.error(f"Error: {res.text}")

with tab3:
    if st.button("Generate Word Cloud"):
        with st.spinner("Generating word cloud..."):
            res = requests.post(f"{BASE_URL}/generate_wordcloud")
            if res.ok:
                data = res.json()
                chart_json = data.get("chart", "")
                if chart_json:
                    fig = pio.from_json(chart_json)
                    st.plotly_chart(fig, use_container_width=True)
                    st.success(data.get("message", "Word cloud generated successfully."))
                else:
                    st.error("No chart data returned.")
            else:
                st.error(f"Error: {res.text}")
