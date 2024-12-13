#AISAI: Your AI Powered Sales and Insights Assistant | v25

import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults

# Set page configuration
st.set_page_config(page_title="AISAI: Your AI Powered Sales and Insights Assistant", page_icon="\U0001F310")

# Sidebar for options
st.sidebar.markdown("### About AISIA")
st.sidebar.markdown(
    "AI Sales Insights Assistant (AISIA) is a tool to help sales representatives gain insights into prospective accounts, competitors, and company strategies.",
)
st.sidebar.divider()

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
    "product_name": "https://nzxt.com/product/player-three-prime",
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
        "**Product Name** (What product are you selling?):",
        value=demo_data["product_name"] if st.session_state.use_demo_data else ""
    )
    company_url = st.text_input(
        "**Company URL** (The URL of the company you are targeting):",
        value=demo_data["company_url"] if st.session_state.use_demo_data else ""
    )
    product_category = st.text_input(
        "**Product Category** (e.g., 'Cloud Data Platform'):",
        value=demo_data["product_category"] if st.session_state.use_demo_data else ""
    )
    competitors_url = st.text_input(
        "**Competitors URL** (e.g., www.apple.com):",
        value=demo_data["competitors_url"] if st.session_state.use_demo_data else ""
    )
    value_proposition = st.text_input(
        "**Value Proposition** (Summarize the appeal of the product):",
        value=demo_data["value_proposition"] if st.session_state.use_demo_data else ""
    )
    target_customer = st.text_input(
        "**Target Customer** (Name of the person you are trying to sell to.):",
        value=demo_data["target_customer"] if st.session_state.use_demo_data else ""
    )

    include_strategy = st.checkbox("\U0001F4BC Include Company Strategy", value=True)
    include_competitors = st.checkbox("\U0001F4CA Include Competitor Analysis", value=True)
    include_financial_metrics = st.checkbox("\U0001F4B0 Include Financial Metrics", value=True)
    include_leadership = st.checkbox("\U0001F465 Include Leadership Insights", value=True)

    if st.form_submit_button("Generate Insights"):
        with st.spinner("Processing..."):
            # Fetch company information
            company_information = search.invoke(company_url)

            # Prompt Template
            prompt_template = ChatPromptTemplate([("system", PROMPT_TEMPLATE)])

            # Create input payload
            input_payload = {
                "company_information": company_information,
                "product_name": product_name,
                "competitors_url": competitors_url,
                "product_category": product_category,
                "value_proposition": value_proposition,
                "target_customer": target_customer,
                "include_financial_metrics": include_financial_metrics,
                "additional_insights": additional_insights
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
