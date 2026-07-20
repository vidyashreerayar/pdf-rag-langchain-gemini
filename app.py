import os
import calendar
import re
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ----------------------------
# Environment
# ----------------------------

load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("GOOGLE_API_KEY not found")


# ----------------------------
# Gemini Model
# ----------------------------

model = init_chat_model("google_genai:gemini-2.5-flash-lite")


# ----------------------------
# Load PDFs
# ----------------------------

all_docs = []

pdf_folder = Path("docs")

for pdf_file in pdf_folder.glob("*.pdf"):
    loader = PyPDFLoader(str(pdf_file))
    all_docs.extend(loader.load())


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

documents = text_splitter.split_documents(all_docs)


# ----------------------------
# Embedding Model
# ----------------------------

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.environ["GOOGLE_API_KEY"],
    batch_size=5,
)


# ----------------------------
# Vector Store
# ----------------------------

if os.path.exists("./Vectorstore"):
    vectorstore = Chroma(
        persist_directory="./Vectorstore",
        embedding_function=embedding_model
    )
else:
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory="./Vectorstore",
    )


# ----------------------------
# Load CSVs
# ----------------------------

sales_df = pd.read_csv("data/sales_kpis.csv")
manufacturing_df = pd.read_csv("data/manufacturing_kpis.csv")
procurement_df = pd.read_csv("data/procurement_kpis.csv")
inventory_df = pd.read_csv("data/inventory_kpis.csv")


# ----------------------------
# KPI Lookup
# ----------------------------

def get_monthly_kpi(month, kpi):

    month = month.strip().title()

    month_map = {m: m[:3] for m in calendar.month_name if m}

    if month in month_map:
        month = month_map[month]

    datasets = [
        sales_df,
        manufacturing_df,
        procurement_df,
        inventory_df,
    ]

    for df in datasets:
        if kpi in df.columns:
            row = df[df["Month"] == month]

            if not row.empty:
                return row.iloc[0][kpi]

    return None


# ----------------------------
# Query Router
# ----------------------------

def classify_query(query):

    query = query.lower()

    cleaned_query = re.sub(r"[^\w\s]", "", query)
    words = cleaned_query.split()

    kpi_keywords = [
        "revenue",
        "gross margin",
        "otif",
        "forecast accuracy",
        "inventory turnover",
        "oee",
        "production yield",
        "supplier",
        "lead time",
        "purchase price variance",
    ]

    months = {
        "jan","january","feb","february","mar","march",
        "apr","april","may","jun","june",
        "jul","july","aug","august",
        "sep","september","oct","october",
        "nov","november","dec","december",
    }

    definition_words = [
        "what is",
        "what does",
        "explain",
        "meaning",
        "mean",
        "define",
    ]

    has_kpi = any(k in cleaned_query for k in kpi_keywords)
    has_month = any(word in months for word in words)
    wants_definition = any(d in cleaned_query for d in definition_words)

    if has_kpi and has_month and wants_definition:
        return "hybrid"

    elif has_kpi and has_month:
        return "csv"

    else:
        return "rag"


# ----------------------------
# CSV Query
# ----------------------------

def query_csv(question):

    question = question.lower()

    month = None

    month_map = {}

    for m in calendar.month_name[1:]:
        month_map[m.lower()] = m[:3]

    for m in calendar.month_abbr[1:]:
        month_map[m.lower()] = m

    for key in month_map:
        if key in question:
            month = month_map[key]
            break

    kpi_map = {
        "revenue": "Revenue_Million_EUR",
        "gross margin": "Gross_Margin_Percent",
        "otif": "OTIF_Percent",
        "forecast accuracy": "Forecast_Accuracy_Percent",
        "inventory turnover": "Inventory_Turnover",
        "oee": "OEE_Percent",
        "production yield": "Production_Yield_Percent",
        "supplier": "Supplier_OnTime_Delivery_Percent",
    }

    kpi_column = None

    for key in kpi_map:
        if key in question:
            kpi_column = kpi_map[key]
            break

    if month is None or kpi_column is None:
        return "I couldn't understand the KPI or month."

    value = get_monthly_kpi(month, kpi_column)

    if value is None:
        return f"No data found for {kpi_column} in {month}."

    return f"{kpi_column.replace('_', ' ')} for {month}: {value}"


# ----------------------------
# AI Assistant
# ----------------------------

def ask(question):

    route = classify_query(question)

    if route == "csv":
        return query_csv(question)

    elif route == "rag":

        docs = vectorstore.similarity_search(question, k=3)

        context = "\n\n".join(doc.page_content for doc in docs)

        prompt = f"""
You are an enterprise AI assistant.

Answer ONLY using the information provided in the context below.
If the answer is not available in the context, say that you could not find it.

Context:
{context}

Question:
{question}
"""

        response = model.invoke(prompt)
        return response.content

    elif route == "hybrid":

        csv_answer = query_csv(question)

        docs = vectorstore.similarity_search(question, k=3)

        context = "\n\n".join(doc.page_content for doc in docs)

        prompt = f"""
You are an enterprise AI assistant.

CSV Result:
{csv_answer}

Reference:
{context}

Question:
{question}

Use the structured KPI result together with the document context to answer.
If the document does not contain an explanation, only return the KPI result.
"""

        response = model.invoke(prompt)

        return response.content

    return "Could not classify the question."


# ----------------------------
# Streamlit UI
# ----------------------------

st.set_page_config(
    page_title="Enterprise AI Assistant",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Enterprise AI Assistant")

st.write(
    "Ask questions about company policies, KPI definitions, or monthly business metrics."
)

question = st.text_area(
    "Ask a question",
    placeholder="Example: What was Revenue in March and explain what Revenue means?",
    height=100,
)

st.caption("""
**Example questions**

• What is Data Governance?

• Who owns Gross Margin?

• What was Revenue in March?

• What was OTIF in April?

• What was Revenue in March and explain what Revenue means?
""")

if st.button("🔍 Ask", use_container_width=True):

    if question.strip():

        with st.spinner("Searching..."):
            answer = ask(question)

        st.markdown("## Answer")
        st.success(answer)

    else:
        st.warning("Please enter a question.")

st.divider()

st.markdown("### 💡 Supported Query Types")

st.markdown("""
**📄 Document Questions (RAG)**

- What is Data Governance?
- Who owns Gross Margin?
- Explain Forecast Accuracy.

**📊 KPI Questions (CSV)**

- What was Revenue in March?
- What was OTIF in April?
- What was OEE in June?

**🔀 Hybrid Questions**

- What was Revenue in March and explain what Revenue means?
- What was OTIF in April and explain how it is calculated?
""")