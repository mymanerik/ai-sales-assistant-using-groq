#v32
import requests
from bs4 import BeautifulSoup
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults

# Set page configuration
st.set_page_config(
    page_title="AISAI: Your AI Powered Sales and Insights Assistant",
    page_icon="🌐",
    layout="wide"
)

# Function to scrape data from a URL
def scrape_website(url, target="meta"):
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
    st.markdown("#### Contact Information")
    st.markdown(
        "[GitHub](https://github.com/mymanerik) | "
        "[LinkedIn](https://www.linkedin.com/in/erikmalson) | "
        "[Resume](https://docs.google.com/document/d/1GxGBTHxJAxRu9_t98PeaH9Jk-ogLInSCU85Ub9gnjiY/edit?usp=sharing) | "
        "[YouTube](https://www.youtube.com/@AIInTheAM)"
    )

# Demo Data
demo_data = {
    "product_name": "Player Three Prime",
    "company_url": "https://nzxt.com",
    "product_category": "Pre-Built Computer",
    "competitors_url": "https://buildredux.com",
    "value_proposition": "High-end PC for AI, Data Modeling, and Video Rendering",
    "target_customer": "High-end gamers, AI, and ML Developers"
}

# Main Form
st.title("AI Sales Insights Assistant")
st.markdown("### Please fill out the form below to generate insights.")

# Toggle for demo data
use_demo_data = st.checkbox("Use Demo Data")

# Data collection form
with st.form("company_info"):
    product_name = st.text_input(
        "Product Name (What product are you selling?):",
        value=demo_data["product_name"] if use_demo_data else ""
    )
    company_url = st.text_input(
        "Company URL (The URL of the company you are targeting):",
        value=demo_data["company_url"] if use_demo_data else ""
    )
    product_category = st.text_input(
        "Product Category (e.g., 'Cloud Data Platform'):",
        value=demo_data["product_category"] if use_demo_data else ""
    )
    competitors_url = st.text_input(
        "Competitors URL (e.g., www.apple.com):",
        value=demo_data["competitors_url"] if use_demo_data else ""
    )
    value_proposition = st.text_input(
        "Value Proposition (Summarize the appeal of the product):",
        value=demo_data["value_proposition"] if use_demo_data else ""
    )
    target_customer = st.text_input(
        "Target Customer (Name of the person you are trying to sell to.):",
        value=demo_data["target_customer"] if use_demo_data else ""
    )

    include_strategy = st.checkbox("Include Company Strategy", value=True)
    include_competitors = st.checkbox("Include Competitor Analysis", value=True)
    include_financial_metrics = st.checkbox("Include Financial Metrics", value=True)
    include_leadership = st.checkbox("Include Leadership Insights", value=True)

    submitted = st.form_submit_button("Generate Insights")

if submitted:
    with st.spinner("Scraping and generating insights..."):
        # Scrape company data
        scraped_content = scrape_website(company_url, target="paragraphs")
        if "error" in scraped_content:
            st.error(scraped_content["error"])
        else:
            # Use scraped content as additional insights
            scraped_text = " ".join(scraped_content["content"]) if isinstance(scraped_content["content"], list) else scraped_content["content"]

            # Prepare input for prompt
            PROMPT_TEMPLATE = """
            You are an assistant providing account insights for a sales representative. The insights include:
            1. Analysis of the company's product offerings in terms of pricing, performance, and value.
            2. A summary of the company's strategy, including any press releases or leadership statements.
            3. Identification of competitors and their strategies.
            4. Leadership details of the company, including relevant individuals and their roles.
            5. Financial metrics, such as annual revenue, growth rates, and profit margins (if selected).
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

            input_payload = {
                "company_information": scraped_text,
                "product_name": product_name,
                "competitors_url": competitors_url,
                "product_category": product_category,
                "value_proposition": value_proposition,
                "target_customer": target_customer,
                "include_financial_metrics": include_financial_metrics,
                "additional_insights": scraped_text,
            }

            # Generate insights
            llm = ChatGroq(api_key=st.secrets.get("GROQ_API_KEY"))
            prompt_template = ChatPromptTemplate([("system", PROMPT_TEMPLATE)])
            parser = StrOutputParser()
            chain = prompt_template | llm | parser
            company_insights = chain.invoke(input_payload)

            # Display insights
            st.markdown("## Sales Insights Report")
            if isinstance(company_insights, str):
                st.markdown(company_insights)
            elif isinstance(company_insights, dict):
                st.json(company_insights)
            else:
                st.warning("Unexpected output format.")
