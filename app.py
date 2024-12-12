import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults

# Model and Agent tools
llm = ChatGroq(api_key=st.secrets.get("GROQ_API_KEY"))
search = TavilySearchResults(max_results=2)
parser = StrOutputParser()

# Page Header
st.title("Assistant Agent")
st.markdown("Assistant Agent Powered by Groq\n\n**Note: Fields are pre-populated while testing. Feel free to change them**")

# Data collection/inputs
with st.form("company_info", clear_on_submit=True):
    product_name = st.text_input(
        "**Product Name** (What product are you selling?):",
        #value="https://www.buildredux.com/collections/gaming-computers/products/ultimate-gaming-pc-intel-core-ultra-9-nvidia-rtx-4090?variant=51685702336876"
        value="Dual RTX 4090 128GB 8TB NVME M.2 PC"
    )

    company_url = st.text_input(
        "**Company URL** (The URL of the company you are targeting):",
        value="https://nzxt.com"
    )

    product_category = st.text_input(
        "**Product Category** (e.g., 'Please input the product category'):",
        value="Pre-Built Computer"
    )

    competitors_url = st.text_input(
        "**Competitors URL** (ex. www.apple.com):",
        value="https://buildredux.com"
    )

    value_proposition = st.text_input(
        "**Value Proposition** (Summarize the appeal of the product):",
        value="High end PC for advanced AI, Data Modeling and Video Rendering"
    )

    target_customer = st.text_input(
        "**Target Customer** (Name of the person you are trying to sell to.):",
        value="Nerds"
    )

    # For the llm insights result
    company_insights = ""

    # Data process
    if st.form_submit_button("Generate Insights"):
        if product_name and company_url:
            with st.spinner("Processing..."):

                # Use search tool to get Company Information
                company_information = search.invoke(company_url)
                print(company_information)

                # Read prompt from external file
                with open("D:\\AIPE Project\\prompt.txt", "r") as prompt_file:
                    prompt = prompt_file.read()

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
#yeuh
st.markdown(company_insights)
