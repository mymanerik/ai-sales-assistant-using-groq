import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults


# Model and Agent tools
llm = ChatGroq(api_key=st.secrets.get("GROQ_API_KEY"))
search = TavilySearchResults(max_results=2)
parser = StrOutputParser()
# tools = [search] # add tools to the list

# Page Header
st.title("Assistant Agent")
st.markdown("Assistant Agent Powered by Groq")


# Data collection/inputs
with st.form("company_info", clear_on_submit=True):

    product_name = st.text_input("**Product Name** (What product are you selling?):")
    
    company_url = st.text_input(
        "**Company URL** (The URL of the company you are targeting):"
    )
    
    product_category = st.text_input(
        "**Product Category** (e.g., 'Data Warehousing' or 'Cloud Data Platform')"
    )
    
    competitors_url = st.text_input("**Competitors URL** (ex. www.apple.com):")
    
    value_proposition = st.text_input(
        "**Value Proposition** (A sentence summarizing the product’s value):"
    )
    
    target_customer = st.text_input(
        "**Target Customer** (Name of the person you are trying to sell to.) :"
    )

    # For the llm insights result
    company_insights = ""

    # Data process
    if st.form_submit_button("Generate Insights"):
        if product_name and company_url:
            st.spinner("Processing...")

            # Use search tool to get Company Information
            company_information = search.invoke(company_url)
            print(company_information)

            # TODO: Create prompt <=================
            #prompt = """
            prompt = "Analyze the following company information and summarize its strategy, key leadership, and mentions of competitors."

            # Prompt Template
            prompt_template = ChatPromptTemplate([("system", prompt)])

            # Chain
            chain = prompt_template | llm | parser

            # Result/Insights
            company_insights = chain.invoke(
                {
                    "company_information": company_information,
                    "product_name": product_name,
                    "competitors_url": competitors_url,
                    "product_category": product_category,
                    "value_proposition": value_proposition,
                    "target_customer": target_customer
                }
            )

st.markdown(company_insights)