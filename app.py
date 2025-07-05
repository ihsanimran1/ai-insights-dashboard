import streamlit as st
import requests
import subprocess
import ollama
from bs4 import BeautifulSoup
import random
import fitz  
import pymupdf  # PyMuPDF for PDF text extraction

# ⚡ Initialize Ollama client (running locally)
ollama_client = ollama.Client(host="http://localhost:11434")

# Function: Analyze text with LLaMA (Consultant Instructions)
def analyze_text_with_llama(title, content):
    consultant_instructions = """
You are a professional consultant specializing in critical reasoning and analysis across diverse fields. Your expertise encompasses financial strategies, political analysis, scientific research evaluation, and more. You approach each task with a structured, methodical approach, ensuring a thorough and unbiased assessment.

Your process for handling any input:

First summarise the article/text/essay in detail at least 150 words.

Identify the Input Type: Determine the nature of the input. Is it a financial proposal, a political commentary, a research article, a problem statement, or something else? This step is crucial for selecting the appropriate analytical framework.

Define the Scope and Objectives: Clearly define the scope of your analysis. What specific aspects of the input require scrutiny? What are the ultimate objectives of the analysis? For example, are you aiming to identify potential flaws, evaluate the feasibility of a plan, assess the validity of research findings, or offer recommendations?

Establish Evaluation Criteria: Based on the input type and objectives, establish clear and specific criteria for evaluation. These criteria should be objective, measurable, and relevant to the task at hand. For instance, when analyzing a financial proposal, you might consider factors such as profitability, risk, market demand, and scalability. When evaluating a research article, you would assess the methodology, data analysis, statistical significance, and the validity of the conclusions.

Gather and Analyze Information: Thoroughly review and analyze the input, paying close attention to detail and identifying any inconsistencies, biases, or potential weaknesses. For quantitative data, perform calculations and statistical analysis as needed. For qualitative data, employ techniques such as thematic analysis or content analysis to identify recurring patterns and themes.

Critical Reasoning and Evaluation: Apply critical reasoning skills to evaluate the information gathered. This includes questioning assumptions, identifying potential biases, considering alternative explanations, and assessing the credibility of sources. Utilize logical reasoning, deductive and inductive arguments, and other analytical techniques to draw valid conclusions.

Formulate Conclusions and Recommendations: Based on your analysis, formulate clear and concise conclusions. For research articles, determine whether the findings are valid, reliable, and significant. For financial proposals, assess their feasibility and potential return on investment. Offer specific, actionable recommendations based on your findings.

Document Your Analysis: Maintain a detailed record of your analysis process, including your methodology, data sources, assumptions, and reasoning. This documentation ensures transparency, replicability, and enables others to understand your conclusions. This should be presented in a clear, concise, and professional manner, using appropriate terminology and avoiding jargon where possible.

Examples of how you would approach different input types:

Financial Proposal: You would analyze the financial projections, market research, and competitive landscape. You would identify potential risks, assess the financial viability, and make recommendations for improvement.

Political Commentary: You would evaluate the arguments presented, identify underlying biases, and assess the validity of the claims made. You would consider the context, the sources of information, and the potential implications of the commentary.

Research Article: You would critically evaluate the methodology, the data analysis, and the conclusions reached. You would assess the validity of the research design, the statistical significance of the findings, and the potential limitations of the study.

Remember to maintain objectivity, avoid personal biases, and clearly articulate your reasoning and conclusions in all your analyses.
"""
    prompt = f"""{consultant_instructions}

Analyze the following content and provide a structured critical analysis:

Title: "{title}"
Content: "{content}"
"""
    try:
        response = ollama_client.chat(
            model="llama3",
            messages=[
                {"role": "system", "content": consultant_instructions.strip()},
                {"role": "user", "content": prompt.strip()}
            ],
            options={"num_predict": 1500}  # Allow very detailed responses
        )
        return response['message']['content'].strip()
    except Exception as e:
        return f"❌ Error analyzing content: {e}"

# Function: Fetch article text using fetch_page.js (for Single URL)
def fetch_article_text_archive(url):
    try:
        result = subprocess.run(
            ["node", "fetch_page.js", url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300  # Allow extra time for archive.ph fallback
        )
        if result.returncode != 0:
            return f"❌ fetch_page.js Error: {result.stderr}"
        return result.stdout.strip()
    except Exception as e:
        return f"❌ Error fetching article with fetch_page.js: {e}"

# Function: Fetch article text using fetch_page_puppeteer.js (for Auto Fetch)
def fetch_article_text_puppeteer(url):
    try:
        result = subprocess.run(
            ["node", "fetch_page_puppeteer.js", url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=180
        )
        if result.returncode != 0:
            return f"❌ fetch_page_puppeteer.js Error: {result.stderr}"
        return result.stdout.strip()
    except Exception as e:
        return f"❌ Error fetching article with Puppeteer: {e}"

# Function: Extract text from uploaded PDF
def extract_text_from_pdf(pdf_file):
    try:
        text = ""
        with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        return f"❌ Error extracting text from PDF: {e}"

# Function: Fetch a random headline from Google News RSS
def get_random_headline(search_query):
    try:
        rss_url = f"https://news.google.com/rss/search?q={search_query}&hl=en-AU&gl=AU&ceid=AU:en"
        response = requests.get(rss_url)
        soup = BeautifulSoup(response.content, "xml")
        headlines = []
        for item in soup.find_all("item")[:15]:  # Get more articles for variety
            title = item.title.text
            link = item.link.text
            headlines.append((title, link))
        random.shuffle(headlines)
        return headlines[0] if headlines else None
    except Exception as e:
        return None

# Resolve Google redirect URLs
def resolve_google_redirect(url):
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        return response.url
    except Exception:
        return url  # fallback to original

# Streamlit App
st.title("📈 AI Insights Dashboard")
st.write("Fetch and analyze articles, custom URLs, or upload a PDF for critical analysis.")

# Mode selection
mode = st.radio("Select Mode:", ["Auto Fetch Random Article", "Analyze a Single URL", "Upload and Analyze PDF"])

# Auto Fetch Random Article
if mode == "Auto Fetch Random Article":
    search_query = st.text_input("🔍 Enter a topic to search for:", "Australia finance")
    if st.button("Fetch & Analyze Random Article"):
        random_article = get_random_headline(search_query.strip())
        if random_article:
            title, url = random_article
            st.markdown(f"### [{title}]({url})")
            resolved_url = resolve_google_redirect(url)
            with st.spinner("📄 Fetching article..."):
                article_text = fetch_article_text_puppeteer(resolved_url)
            if article_text.startswith("❌"):
                st.error(article_text)
            else:
                with st.spinner("🤖 Analyzing article..."):
                    analysis = analyze_text_with_llama(title, article_text)
                st.markdown("**🤖 AI Critical Analysis:**")
                st.write(analysis)
        else:
            st.warning("No articles found. Try a different search term.")

# Analyze a Single URL
elif mode == "Analyze a Single URL":
    url_input = st.text_input("🔗 Paste the article URL:")
    if st.button("Analyze Article"):
        if not url_input.strip():
            st.warning("Please paste a valid URL.")
        else:
            st.markdown(f"### [{url_input}]({url_input})")
            with st.spinner("📄 Fetching article..."):
                article_text = fetch_article_text_archive(url_input.strip())
            if article_text.startswith("❌"):
                st.error(article_text)
            else:
                with st.spinner("🤖 Analyzing article..."):
                    analysis = analyze_text_with_llama("Custom URL Analysis", article_text)
                st.markdown("**🤖 AI Critical Analysis:**")
                st.write(analysis)

# Upload PDF and analyze
elif mode == "Upload and Analyze PDF":
    uploaded_pdf = st.file_uploader("📄 Upload a PDF file for analysis", type=["pdf"])
    if uploaded_pdf is not None:
        st.markdown(f"### Uploaded File: {uploaded_pdf.name}")
        with st.spinner("📄 Extracting text from PDF..."):
            pdf_text = extract_text_from_pdf(uploaded_pdf)
        if pdf_text.startswith("❌"):
            st.error(pdf_text)
        else:
            st.markdown("**📝 Extracted PDF Text (truncated):**")
            st.write(pdf_text[:800] + "..." if len(pdf_text) > 800 else pdf_text)
            if st.button("🔍 Analyze PDF"):
                with st.spinner("🤖 Analyzing PDF content..."):
                    analysis = analyze_text_with_llama(uploaded_pdf.name, pdf_text)
                st.markdown("**🤖 AI Critical Analysis:**")
                st.write(analysis)

