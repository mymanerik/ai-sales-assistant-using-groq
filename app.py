import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults

# Visualization function
def create_comparison_chart(data):
    """Create a bar chart comparing company and competitor metrics."""
    try:
        # Check if numeric data exists
        if not any(data.select_dtypes(include="number").columns):
            raise ValueError("No numeric data available to plot.")

        fig, ax = plt.subplots(figsize=(10, 6))
        data.set_index("Metric").plot(kind="bar", ax=ax, legend=True)
        plt.title("Company vs. Competitor Metrics")
        plt.ylabel("Values")
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig
    except Exception as e:
        return f"Please note: {e}"

# Function to scrape data from a URL
def scrape_website(url, target="paragraphs"):
    """Scrapes data from the specified URL."""
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        if target == "meta":
            meta_description = soup.find("meta", attrs={"name": "description"})
            meta_content = meta_description["content"] if meta_description else "No meta description available"
            return {"type": "meta", "content": meta_content}

        elif target == "headings":
            headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])[:5]]
            return {"type": "headings", "content": headings}

        elif target == "paragraphs":
            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")[:5]]
            return {"type": "paragraphs", "content": paragraphs}

        else:
            return {"error": "Invalid scraping target selected."}

    except Exception as e:
        return {"error": f"Failed to scrape data: {e}"}

# File upload handling
def extract_text_from_uploaded_file(uploaded_file):
    """Extracts text from uploaded PDF or Word files."""
    try:
        if uploaded_file.name.endswith(".pdf"):
            from PyPDF2 import PdfReader
            pdf_reader = PdfReader(uploaded_file)
            text = "\n".join([page.extract_text() for page in pdf_reader.pages])
            return text
        elif uploaded_file.name.endswith(".docx"):
            from docx import Document
            doc = Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        else:
            return "Unsupported file format. Please upload a PDF or Word document."
    except Exception as e:
        return f"Error processing file: {e}"

# Sidebar for options
with st.sidebar:
    st.markdown("### About AISIA")
    st.markdown(
        "**AI Sales Insights Assistant (AISIA)** helps sales representatives gain insights into prospective accounts, competitors, and strategies."
    )
    st.divider()

    # Model selection
    st.markdown("### Model Selection")
    selected_model = st.selectbox(
        "Select a Language Model",
        options=[
            "Groq-Sales-v1.2.3",
            "Groq-Finance-v2.0.1",
            "Groq-Insights-v3.1.0",
            "Gemini – EXP – 1206 (coming soon)",
            "ChatGPT – 40 – latest (2024 – 11– 20) (coming soon)",
            "Ye – lightning (coming soon)",
            "Claude 3.5 sonnet (coming soon)",
            "Antheme – V2 – chat – 72B (coming soon)"
        ]
    )

    # Temperature slider
    st.markdown("### Model Temperature")
    selected_temperature = st.slider(
        "Adjust Model Temperature", 0.0, 1.0, 0.7, 0.1
    )

    st.divider()
    st.markdown("### Erik Malson: Contact Information")
    st.markdown(
        "[GitHub](https://github.com/mymanerik) | "
        "[LinkedIn](https://www.linkedin.com/in/erikmalson) | "
        "[Resume](https://docs.google.com/document/d/1GxGBTHxJAxRu9_t98PeaH9Jk-ogLInSCU85Ub9gnjiY/edit?usp=sharing) | "
        "[YouTube](https://www.youtube.com/@AIInTheAM)"
    )

# Determine model and set title
placeholder_models = [
    "Gemini – EXP – 1206 (coming soon)",
    "ChatGPT – 40 – latest (2024 – 11– 20) (coming soon)",
    "Ye – lightning (coming soon)",
    "Claude 3.5 sonnet (coming soon)",
    "Antheme – V2 – chat – 72B (coming soon)"
]
if selected_model in placeholder_models:
    display_model = "Groq-Insights-v3.1.0"
    st.title(f"AI Sales Insights Assistant: {display_model}")
    st.markdown(
        f"<p style='font-size:14px;'>Selected model <b>{selected_model}</b> is unavailable at this time. Defaulting to <b>{display_model}</b>.</p>",
        unsafe_allow_html=True,
    )
else:
    display_model = selected_model
    st.title(f"AI Sales Insights Assistant: {display_model}")

# Demo data
demo_data = {
    "product_name": "Player Three Prime",
    "company_url": "https://nzxt.com",
    "product_category": "Pre-Built Computer",
    "competitors_url": "https://buildredux.com",
    "value_proposition": "High-end PC for AI, Data Modeling, and Video Rendering",
    "target_customer": "High-end gamers, AI, and ML Developers"
}

# Data collection form
st.markdown("### Please fill out the form below to generate insights.")
use_demo_data = st.checkbox("Use Demo Data")

with st.form("company_info"):
    product_name = st.text_input(
        "Product Name (What product are you selling?)",
        value=demo_data["product_name"] if use_demo_data else ""
    )
    company_url = st.text_input(
        "Company URL (The URL of the company you are targeting)",
        value=demo_data["company_url"] if use_demo_data else ""
    )
    product_category = st.text_input(
        "Product Category (e.g., 'Cloud Data Platform')",
        value=demo_data["product_category"] if use_demo_data else ""
    )
    competitors_url = st.text_input(
        "Competitors URL (e.g., www.apple.com)",
        value=demo_data["competitors_url"] if use_demo_data else ""
    )
    value_proposition = st.text_input(
        "Value Proposition (Summarize the appeal of the product)",
        value=demo_data["value_proposition"] if use_demo_data else ""
    )
    target_customer = st.text_input(
        "Target Customer (Who are you selling to?)",
        value=demo_data["target_customer"] if use_demo_data else ""
    )
    uploaded_file = st.file_uploader("Optional: Upload a product overview document (PDF or Word)", type=["pdf", "docx"])
    include_strategy = st.checkbox("Include Company Strategy", value=True)
    include_competitors = st.checkbox("Include Competitor Analysis", value=True)
    include_financial_metrics = st.checkbox("Include Financial Metrics", value=True)
    include_leadership = st.checkbox("Include Leadership Insights", value=True)
    submitted = st.form_submit_button("Generate Insights")

# Prepare input for prompt from external file
# ADD PROMPT HERE
try:
    with open("theprompt.txt", "r") as prompt_file:
        PROMPT_TEMPLATE = prompt_file.read()
except FileNotFoundError:
    PROMPT_TEMPLATE = """Error: Prompt file not found. Please ensure 'theprompt.extension' is available in the working directory."""

if submitted:
    with st.spinner("Preparing Report..."):
        # Scraping logic
        company_data = scrape_website(company_url)
        competitor_data = scrape_website(competitors_url)

        # Handle uploaded file
        uploaded_text = None
        if uploaded_file:
            uploaded_text = extract_text_from_uploaded_file(uploaded_file)

        # Prepare input payload
        input_payload = {
            "company_information": company_data.get("content", ""),
            "competitor_information": competitor_data.get("content", ""),
            "product_name": product_name,
            "product_category": product_category,
            "value_proposition": value_proposition,
            "target_customer": target_customer,
            "include_financial_metrics": include_financial_metrics,
            "uploaded_file": uploaded_text,
            "additional_insights": "N/A",  # Default value if not available
            "competitors_url": competitors_url,
            "data_source_url": company_url,
            "ecommerce site name": "N/A"  # Default value
        }

        # Generate insights
        st.markdown("## Sales Insights Report")
        llm = ChatGroq(api_key=st.secrets.get("GROQ_API_KEY"))
        parser = StrOutputParser()
        chain = ChatPromptTemplate([("system", PROMPT_TEMPLATE)]) | llm | parser
        insights = chain.invoke(input_payload)
        st.markdown(insights)

        # Generate comparison data
        comparison_data = pd.DataFrame({
            "Metric": ["Price", "Customer Focus"],
            "Company": [59, None],
            "Competitor": [79, None]
        })

        st.markdown("### Comparison Chart")
        chart = create_comparison_chart(comparison_data)
        if isinstance(chart, str):
            st.warning(chart)
        else:
            st.pyplot(chart)

        st.markdown("### Sources")
        sources = ["https://example.com", "https://news.example.com"]
        for source in sources:
            st.markdown(f"- [Link]({source})")
