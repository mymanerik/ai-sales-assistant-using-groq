#AISAI: Your AI Powered Sales and Insights Assistant | v25

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
st.sidebar.markdown("### Model Comparison")
selected_model = st.sidebar.selectbox(
    "Select a Language Model",
    options=["Groq Model A", "Groq Model B", "Groq Model C"]
)

# Temperature slider for selected Groq model
st.sidebar.markdown("### Model Temperature")
selected_temperature = st.sidebar.slider(
    "Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1
)

# Top K slider
st.sidebar.markdown("### Top K")
top_k = st.sidebar.slider(
    "Top K", min_value=1, max_value=100, value=10, step=1
)

# Divider and Lets Connect section
st.sidebar.divider()
st.sidebar.markdown("<h4>Erik Malson</h4>", unsafe_allow_html=True)
st.sidebar.markdown("<span style='font-size:12px;'>[GitHub](https://github.com/mymanerik) | [LinkedIn](https://www.linkedin.com/in/erikmalson) | [Resume](https://docs.google.com/document/d/1GxGBTHxJAxRu9_t98PeaH9Jk-ogLInSCU85Ub9gnjiY/edit?usp=sharing) | [YouTube](https://www.youtube.com/@AIInTheAM)</span>", unsafe_allow_html=True)

# Title and description for the main panel
st.title(f"AI Sales Insights Assistant: {selected_model}")
st.markdown(
    """
    Please fill out the form below, use our demo data or upload a document for insights
    """
)

# Model and Agent tools
llm = ChatGroq(api_key=st.secrets.get("GROQ_API_KEY"))
search = TavilySearchResults(max_results=2)
parser = StrOutputParser()

# Prompt Template
PROMPT_TEMPLATE = """
You are an assistant providing account insights for a sales representative. The insights include:
1. Analysis of the company's product offerings in terms of pricing, performance, and value.
2. A summary of the company's strategy, including any press releases or leadership statements.
3. Leadership details of the company, including relevant individuals and their roles.
4. Analysis of the company's financial metrics, such as annual revenue, growth rates, and profit margins (if selected).
5. Identification of competitors and a similar comparisons.
6. Links to supporting articles or references.

Inputs provided are:
- Company Information: {company_information}
- Product Name: {product_name}
- Competitors URL: {competitors_url}
- Product Category: {product_category}
- Value Proposition: {value_proposition}
- Target Customer: {target_customer}
- Include Financial Metrics: {include_financial_metrics}
- Additional Insights: {additional_insights}

Please generate a concise one-page summary with actionable insights for the sales representative.
"""

# Demo data for pre-filling (optional)
demo_data = {
    "product_name": "Player Three Prime",
    "company_url": "https://nzxt.com",
    "product_category": "Pre-Built Computer",
    "competitors_url": "https://buildredux.com",
    "value_proposition": "High-end PC for advanced AI, Data Modeling and Video Rendering",
    "target_customer": "Nerds"
}

# Toggle for demo data
if "use_demo_data" not in st.session_state:
    st.session_state.use_demo_data = False

if st.button("Click here to use demo data"):
    st.session_state.use_demo_data = True

# File upload for additional insights
uploaded_file = st.file_uploader("Optional: Upload a product overview document (PDF or Word).", type=["pdf", "docx"])
additional_insights = None
if uploaded_file:
    # Placeholder: Add logic to extract insights from the uploaded document
    additional_insights = "Insights from uploaded document."

# Data collection/inputs
with st.form("company_info", clear_on_submit=True):
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
            chain = prompt_template | llm | parser
            company_insights = chain.invoke(input_payload)

            # Debugging output type
            #st.write(f"Type of company_insights: {type(company_insights)}")
            
            # Output formatting based on type
            st.markdown("## Sales Insights Report", unsafe_allow_html=True)

            if isinstance(company_insights, str):
                import html
                #st.markdown("### Insights Report")
                safe_content = html.escape(company_insights).replace('\n', '  \n')
                st.markdown(safe_content, unsafe_allow_html=True)
            elif isinstance(company_insights, dict):
                st.json(company_insights)  # Display as JSON
            else:
                st.write("Unexpected output format for company_insights:")
                st.write(company_insights)
