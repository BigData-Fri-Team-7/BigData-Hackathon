# code_generation_agent.py
from llm_chat import get_llm_response

def generate_chart_code(chart_type: str, data_description: str) -> str:
    """
    Generate Python code for an interactive chart.
    :param chart_type: e.g., "time-series", "word cloud", "network graph"
    :param data_description: description of the data to be visualized
    :return: Python code as a string
    """
    prompt = f"""
You are a Python developer. Generate a complete Plotly code snippet to create an interactive {chart_type} chart.
The data is described as: {data_description}
Include necessary imports and ensure the chart has zoom and hover capabilities.
"""
    # Use GPT-4O mini for code generation
    response = get_llm_response({"pdf_content": prompt}, prompt, "gpt-4o")
    return response.get("answer", "# Code generation failed.")

if __name__ == "__main__":
    code_snippet = generate_chart_code("time-series", "Dates on the x-axis and number of patent filings on the y-axis.")
    print(code_snippet)
