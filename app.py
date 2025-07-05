import streamlit as st
import requests
import subprocess
import ollama
from bs4 import BeautifulSoup
import random
import fitz  # PyMuPDF for PDF text extraction

# ⚡ Initialize Ollama client (running locally)
ollama_client = ollama.Client(host="http://localhost:11434")

# 🧠 Function: Analyze text with LLaMA (Consultant Instructions)
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

# 📄 Function: Fetch article text using fetch_page.js (for Single URL)
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

# 📄 Function: Fetch article text using fetch_page_puppeteer.js (for Auto Fetch)
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

# 📄 Function: Extract text from uploaded PDF
def extract_text_from_pdf(pdf_file):
    try:
        text = ""
        with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        return f"❌ Error extracting text from PDF: {e}"

# 📄 Function: Fetch a random headline from Google News RSS
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

# 📄 Resolve Google redirect URLs
def resolve_google_redirect(url):
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        return response.url
    except Exception:
        return url  # fallback to original

# 🎨 Streamlit App
st.title("📈 AI Insights Dashboard")
st.write("Fetch and analyze articles, custom URLs, or upload a PDF for critical analysis.")

# 📝 Mode selection
mode = st.radio("Select Mode:", ["Auto Fetch Random Article", "Analyze a Single URL", "Upload and Analyze PDF"])

# ✅ Auto Fetch Random Article
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

# ✅ Analyze a Single URL
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

# ✅ Upload PDF and analyze
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





# import streamlit as st
# import requests
# import subprocess
# import ollama
# from bs4 import BeautifulSoup
# import random
# import fitz  # PyMuPDF for PDF text extraction

# # ⚡ Initialize Ollama client (running locally)
# ollama_client = ollama.Client(host="http://localhost:11434")

# # 🌟 Custom CSS for premium styling + fix text overflow
# st.markdown("""
#     <style>
#     body {
#         background-color: #f4f7fa;
#     }
#     .main {
#         color: #333333;
#         font-family: 'Helvetica Neue', sans-serif;
#     }
#     .headline-card {
#         background-color: #ffffff;
#         border: 1px solid #e1e4e8;
#         border-radius: 12px;
#         padding: 16px;
#         margin-top: 10px;
#         box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
#         word-wrap: break-word;
#         overflow-wrap: anywhere;
#         white-space: pre-wrap;
#         font-size: 18px;
#     }
#     .analysis-card {
#         background-color: #f0f4ff;
#         border-radius: 12px;
#         padding: 16px;
#         margin-top: 10px;
#         box-shadow: inset 0 0 8px rgba(0, 114, 255, 0.1);
#         word-wrap: break-word;
#         overflow-wrap: anywhere;
#         white-space: pre-wrap;
#         font-size: 15px;
#         line-height: 1.6;
#     }
#     .stButton>button {
#         background-color: #0072ff;
#         color: white;
#         border-radius: 8px;
#         padding: 10px 20px;
#         font-size: 16px;
#         font-weight: 600;
#     }
#     .stButton>button:hover {
#         background-color: #0056cc;
#         color: white;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # 🧠 Function: Analyze text with LLaMA (Consultant Instructions)
# def analyze_text_with_llama(title, content):
#     consultant_instructions = """
# You are a professional consultant specializing in critical reasoning and analysis. Your role is to provide insightful, data-driven assessments and recommendations on a wide range of topics, from financial strategies to political analyses. You will approach each task with a structured, objective methodology, ensuring your conclusions are well-supported and defensible.

# Your approach involves these steps:

# 1. **Information Gathering:** Review all available information. Identify explicit and implicit goals, constraints, and assumptions. State clearly if information is missing.
# 2. **Problem Definition:** Reframe ambiguous or vague problems into clear, measurable questions.
# 3. **Critical Analysis:**
#     - Identify biases in the data.
#     - Evaluate evidence for quality, reliability, and validity.
#     - Consider alternative perspectives and counterarguments.
#     - Avoid logical fallacies.
#     - Synthesize information into a comprehensive understanding.
# 4. **Recommendations:** Provide specific, actionable, and quantified recommendations supported by evidence.
# 5. **Evaluating Outcomes:** Suggest KPIs or metrics to assess the recommendations' success.
# 6. **Communication:** Present findings clearly and concisely, highlighting uncertainties or limitations.

# Remember: Provide unbiased, well-reasoned analysis with clear, actionable recommendations based on sound critical reasoning.
# """
#     prompt = f"""{consultant_instructions}

# Analyze the following content and provide a structured critical analysis:

# Title: "{title}"
# Content: "{content}"
# """
#     try:
#         response = ollama_client.chat(
#             model="llama3",
#             messages=[
#                 {"role": "system", "content": consultant_instructions.strip()},
#                 {"role": "user", "content": prompt.strip()}
#             ],
#             options={"num_predict": 1500}  # Allow very detailed responses
#         )
#         return response['message']['content'].strip()
#     except Exception as e:
#         return f"❌ Error analyzing content: {e}"

# # 📄 Function: Extract text from uploaded PDF
# def extract_text_from_pdf(pdf_file):
#     try:
#         text = ""
#         with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
#             for page in doc:
#                 text += page.get_text()
#         return text
#     except Exception as e:
#         return f"❌ Error extracting text from PDF: {e}"

# # 🎨 Streamlit App
# st.markdown("<h1 style='color:#0072ff;'>📈 AI Trading Insights Dashboard</h1>", unsafe_allow_html=True)
# st.write("Fetch and analyze articles, custom URLs, or even upload a PDF for critical analysis.")

# # 📝 Mode selection
# mode = st.radio("Select Mode:", ["Auto Fetch Random Article", "Analyze a Single URL", "Upload and Analyze PDF"])

# # ✅ Analyze a Single URL
# if mode == "Analyze a Single URL":
#     url_input = st.text_input("🔗 Paste the article URL:")
#     if st.button("Analyze Article"):
#         if not url_input.strip():
#             st.warning("Please paste a valid URL.")
#         else:
#             st.markdown(f"<div class='headline-card'><a href='{url_input}' target='_blank'>{url_input}</a></div>", unsafe_allow_html=True)
#             with st.spinner("📄 Fetching article..."):
#                 try:
#                     response = requests.get(url_input, timeout=15)
#                     article_text = response.text
#                 except Exception as e:
#                     article_text = f"❌ Error fetching article: {e}"

#             if article_text.startswith("❌"):
#                 st.error(article_text)
#             else:
#                 with st.spinner("🤖 Analyzing article..."):
#                     analysis = analyze_text_with_llama("Custom URL Analysis", article_text)
#                 st.markdown("**🤖 AI Critical Analysis:**")
#                 st.markdown(f"<div class='analysis-card'>{analysis}</div>", unsafe_allow_html=True)

# # ✅ Upload PDF and analyze
# elif mode == "Upload and Analyze PDF":
#     uploaded_pdf = st.file_uploader("📄 Upload a PDF file for analysis", type=["pdf"])
#     if uploaded_pdf is not None:
#         st.markdown(f"<div class='headline-card'><h4>Uploaded File:</h4>{uploaded_pdf.name}</div>", unsafe_allow_html=True)

#         # Extract text from PDF
#         with st.spinner("📄 Extracting text from PDF..."):
#             pdf_text = extract_text_from_pdf(uploaded_pdf)

#         if pdf_text.startswith("❌"):
#             st.error(pdf_text)
#         else:
#             st.markdown("**📝 Extracted PDF Text (truncated):**")
#             st.markdown(f"<div class='analysis-card'>{pdf_text[:800]}{'...' if len(pdf_text) > 800 else ''}</div>", unsafe_allow_html=True)

#             # Analyze extracted text
#             if st.button("🔍 Analyze PDF"):
#                 with st.spinner("🤖 Analyzing PDF content..."):
#                     analysis = analyze_text_with_llama(uploaded_pdf.name, pdf_text)
#                 st.markdown("**🤖 AI Critical Analysis:**")
#                 st.markdown(f"<div class='analysis-card'>{analysis}</div>", unsafe_allow_html=True)



# import streamlit as st
# import requests
# import subprocess
# import ollama
# from bs4 import BeautifulSoup
# import random
# import os
# import fitz  # PyMuPDF for PDF text extraction

# # ⚡ Initialize Ollama client (running locally)
# ollama_client = ollama.Client(host="http://localhost:11434")

# # 🌟 Custom CSS for premium styling + fix text overflow
# st.markdown("""
#     <style>
#     body {
#         background-color: #f4f7fa;
#     }
#     .main {
#         color: #333333;
#         font-family: 'Helvetica Neue', sans-serif;
#     }
#     .headline-card {
#         background-color: #ffffff;
#         border: 1px solid #e1e4e8;
#         border-radius: 12px;
#         padding: 16px;
#         margin-top: 10px;
#         box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
#         word-wrap: break-word;
#         overflow-wrap: anywhere;
#         white-space: pre-wrap;
#         font-size: 18px;
#     }
#     .analysis-card {
#         background-color: #f0f4ff;
#         border-radius: 12px;
#         padding: 16px;
#         margin-top: 10px;
#         box-shadow: inset 0 0 8px rgba(0, 114, 255, 0.1);
#         word-wrap: break-word;
#         overflow-wrap: anywhere;
#         white-space: pre-wrap;
#         font-size: 15px;
#         line-height: 1.6;
#     }
#     .stButton>button {
#         background-color: #0072ff;
#         color: white;
#         border-radius: 8px;
#         padding: 10px 20px;
#         font-size: 16px;
#         font-weight: 600;
#     }
#     .stButton>button:hover {
#         background-color: #0056cc;
#         color: white;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # 🧠 Function: Analyze text with LLaMA (Consultant Instructions)
# def analyze_text_with_llama(title, content):
#     consultant_instructions = """
# You are a professional consultant specializing in critical reasoning and analysis. Your role is to provide insightful, data-driven assessments and recommendations on a wide range of topics, from financial strategies to political analyses. You will approach each task with a structured, objective methodology, ensuring your conclusions are well-supported and defensible.

# Your approach involves these steps:

# 1. **Information Gathering:** Review all available information. Identify explicit and implicit goals, constraints, and assumptions. State clearly if information is missing.
# 2. **Problem Definition:** Reframe ambiguous or vague problems into clear, measurable questions.
# 3. **Critical Analysis:**
#     - Identify biases in the data.
#     - Evaluate evidence for quality, reliability, and validity.
#     - Consider alternative perspectives and counterarguments.
#     - Avoid logical fallacies.
#     - Synthesize information into a comprehensive understanding.
# 4. **Recommendations:** Provide specific, actionable, and quantified recommendations supported by evidence.
# 5. **Evaluating Outcomes:** Suggest KPIs or metrics to assess the recommendations' success.
# 6. **Communication:** Present findings clearly and concisely, highlighting uncertainties or limitations.

# Remember: Provide unbiased, well-reasoned analysis with clear, actionable recommendations based on sound critical reasoning.
# """

#     prompt = f"""{consultant_instructions}

# Analyze the following content and provide a structured critical analysis:

# Title: "{title}"
# Content: "{content}"
# """
#     try:
#         response = ollama_client.chat(
#             model="llama3",
#             messages=[
#                 {"role": "system", "content": consultant_instructions.strip()},
#                 {"role": "user", "content": prompt.strip()}
#             ],
#             options={"num_predict": 1500}  # Allow very detailed responses
#         )
#         return response['message']['content'].strip()
#     except Exception as e:
#         return f"❌ Error analyzing content: {e}"

# # 📄 Function: Extract text from uploaded PDF
# def extract_text_from_pdf(pdf_file):
#     try:
#         text = ""
#         with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
#             for page in doc:
#                 text += page.get_text()
#         return text
#     except Exception as e:
#         return f"❌ Error extracting text from PDF: {e}"

# # 🎨 Streamlit App
# st.markdown("<h1 style='color:#0072ff;'>📈 AI Trading Insights Dashboard</h1>", unsafe_allow_html=True)
# st.write("Fetch and analyze articles, custom URLs, or even upload a PDF for critical analysis.")

# # 📝 Mode selection
# mode = st.radio("Select Mode:", ["Auto Fetch Random Article", "Analyze a Single URL", "Upload and Analyze PDF"])

# if mode == "Upload and Analyze PDF":
#     uploaded_pdf = st.file_uploader("📄 Upload a PDF file for analysis", type=["pdf"])
#     if uploaded_pdf is not None:
#         st.markdown(f"<div class='headline-card'><h4>Uploaded File:</h4>{uploaded_pdf.name}</div>", unsafe_allow_html=True)

#         # Extract text from PDF
#         with st.spinner("📄 Extracting text from PDF..."):
#             pdf_text = extract_text_from_pdf(uploaded_pdf)

#         if pdf_text.startswith("❌"):
#             st.error(pdf_text)
#         else:
#             st.markdown("**📝 Extracted PDF Text (truncated):**")
#             st.markdown(f"<div class='analysis-card'>{pdf_text[:800]}{'...' if len(pdf_text) > 800 else ''}</div>", unsafe_allow_html=True)

#             # Analyze extracted text
#             if st.button("🔍 Analyze PDF"):
#                 with st.spinner("🤖 Analyzing PDF content..."):
#                     analysis = analyze_text_with_llama(uploaded_pdf.name, pdf_text)
#                 st.markdown("**🤖 AI Critical Analysis:**")
#                 st.markdown(f"<div class='analysis-card'>{analysis}</div>", unsafe_allow_html=True)





# import streamlit as st
# import requests
# import subprocess
# import ollama
# from bs4 import BeautifulSoup
# import random
# import os

# # ⚡ Initialize Ollama client (running locally)
# ollama_client = ollama.Client(host="http://localhost:11434")

# # 🗄 Local cache for articles
# if "article_cache" not in st.session_state:
#     st.session_state.article_cache = {}

# # 🌟 Custom CSS for premium styling + fix text overflow
# st.markdown("""
#     <style>
#     body {
#         background-color: #f4f7fa;
#     }
#     .main {
#         color: #333333;
#         font-family: 'Helvetica Neue', sans-serif;
#     }
#     .headline-card {
#         background-color: #ffffff;
#         border: 1px solid #e1e4e8;
#         border-radius: 12px;
#         padding: 16px;
#         margin-top: 10px;
#         box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
#         word-wrap: break-word;
#         overflow-wrap: anywhere;
#         white-space: pre-wrap;
#         font-size: 18px;
#     }
#     .headline-card h4 {
#         color: #0072ff;
#         margin-bottom: 5px;
#     }
#     .analysis-card {
#         background-color: #f0f4ff;
#         border-radius: 12px;
#         padding: 16px;
#         margin-top: 10px;
#         box-shadow: inset 0 0 8px rgba(0, 114, 255, 0.1);
#         word-wrap: break-word;
#         overflow-wrap: anywhere;
#         white-space: pre-wrap;
#         font-size: 15px;
#         line-height: 1.6;
#     }
#     .stButton>button {
#         background-color: #0072ff;
#         color: white;
#         border-radius: 8px;
#         padding: 10px 20px;
#         font-size: 16px;
#         font-weight: 600;
#     }
#     .stButton>button:hover {
#         background-color: #0056cc;
#         color: white;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # 📄 Function: Fetch a random headline from Google News RSS
# def get_random_headline(search_query):
#     rss_url = f"https://news.google.com/rss/search?q={search_query}&hl=en-AU&gl=AU&ceid=AU:en"
#     response = requests.get(rss_url)
#     soup = BeautifulSoup(response.content, "xml")
#     headlines = []
#     for item in soup.find_all("item")[:15]:  # Fetch more articles for variety
#         title = item.title.text
#         link = item.link.text
#         headlines.append((title, link))
#     random.shuffle(headlines)  # Shuffle for randomness
#     return headlines[0] if headlines else None  # Return one random article

# # 📄 Function: Resolve Google redirect URLs to actual article URLs
# def resolve_google_redirect(url):
#     try:
#         response = requests.get(url, timeout=10, allow_redirects=True)
#         return response.url  # Return the final destination URL
#     except Exception as e:
#         return f"Error resolving redirect: {e}"

# # 📄 Function: Fetch article text (Puppeteer Stealth for random articles)
# def fetch_article_text_puppeteer(url):
#     if url in st.session_state.article_cache:
#         return st.session_state.article_cache[url]

#     try:
#         result = subprocess.run(
#             ["node", "fetch_page_puppeteer.js", url],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             timeout=180
#         )

#         if result.returncode != 0:
#             return f"❌ Puppeteer Error: {result.stderr}"

#         article_text = result.stdout.strip()
#         st.session_state.article_cache[url] = article_text
#         return article_text
#     except Exception as e:
#         return f"❌ Error fetching article: {e}"

# # 📄 Function: Fetch article text (archive.ph for Single URL)
# def fetch_article_text_archive(url):
#     if url in st.session_state.article_cache:
#         return st.session_state.article_cache[url]

#     try:
#         result = subprocess.run(
#             ["node", "fetch_page.js", url],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             timeout=240
#         )

#         if result.returncode != 0:
#             return f"❌ Archive Error: {result.stderr}"

#         article_text = result.stdout.strip()
#         st.session_state.article_cache[url] = article_text
#         return article_text
#     except Exception as e:
#         return f"❌ Error fetching article: {e}"

# # 🧠 Function: Analyze article with LLaMA (Consultant Instructions)
# def analyze_article_llama(title, article_text):
#     consultant_instructions = """
# You are a professional consultant specializing in critical reasoning and analysis. Your role is to provide insightful, data-driven assessments and recommendations on a wide range of topics, from financial strategies to political analyses. You will approach each task with a structured, objective methodology, ensuring your conclusions are well-supported and defensible.

# Your approach involves these steps:

# 1. **Information Gathering:** Review all available information. Identify explicit and implicit goals, constraints, and assumptions. State clearly if information is missing.
# 2. **Problem Definition:** Reframe ambiguous or vague problems into clear, measurable questions.
# 3. **Critical Analysis:**
#     - Identify biases in the data.
#     - Evaluate evidence for quality, reliability, and validity.
#     - Consider alternative perspectives and counterarguments.
#     - Avoid logical fallacies.
#     - Synthesize information into a comprehensive understanding.
# 4. **Recommendations:** Provide specific, actionable, and quantified recommendations supported by evidence.
# 5. **Evaluating Outcomes:** Suggest KPIs or metrics to assess the recommendations' success.
# 6. **Communication:** Present findings clearly and concisely, highlighting uncertainties or limitations.

# Remember: Provide unbiased, well-reasoned analysis with clear, actionable recommendations based on sound critical reasoning.
# """

#     prompt = f"""{consultant_instructions}

# Analyze the following article and provide a structured critical analysis:

# Title: "{title}"
# Article Content: "{article_text}"
# """
#     try:
#         response = ollama_client.chat(
#             model="llama3",
#             messages=[
#                 {"role": "system", "content": consultant_instructions.strip()},
#                 {"role": "user", "content": prompt.strip()}
#             ],
#             options={"num_predict": 1000}  # Allow very detailed responses
#         )
#         return response['message']['content'].strip()
#     except Exception as e:
#         return f"❌ Error analyzing article: {e}"

# # 🎨 Streamlit App
# st.markdown("<h1 style='color:#0072ff;'>📈 AI News Insights Dashboard</h1>", unsafe_allow_html=True)
# st.write("Fetch and analyze **1 random article** or analyze a custom URL with a local AI model.")

# # 📝 Mode selection
# mode = st.radio("Select Mode:", ["Auto Fetch Random Article", "Analyze a Single URL"])

# if mode == "Auto Fetch Random Article":
#     search_query = st.text_input("🔍 Enter a topic to search for:", "Australia finance")
#     if st.button("Fetch & Analyze Random Article"):
#         if not search_query.strip():
#             st.warning("Please enter a topic to search for.")
#         else:
#             random_article = get_random_headline(search_query.strip())

#             if random_article:
#                 title, url = random_article
#                 st.markdown(f"<div class='headline-card'><h4>{title}</h4><a href='{url}' target='_blank'>{url}</a></div>", unsafe_allow_html=True)

#                 # ✅ Resolve Google redirect
#                 real_url = resolve_google_redirect(url)
#                 if real_url.startswith("Error"):
#                     st.error(real_url)
#                 else:
#                     # Fetch full article text
#                     with st.spinner("📄 Fetching article..."):
#                         article_text = fetch_article_text_puppeteer(real_url)

#                     if article_text.startswith("❌"):
#                         st.error(article_text)
#                     else:
#                         # Analyze article with Consultant instructions
#                         with st.spinner("🤖 Analyzing article..."):
#                             analysis = analyze_article_llama(title, article_text)

#                         # Display results in styled cards
#                         st.markdown("**📝 Full Article Text (truncated):**")
#                         st.markdown(f"<div class='analysis-card'>{article_text[:800]}{'...' if len(article_text) > 800 else ''}</div>", unsafe_allow_html=True)
#                         st.markdown("**🤖 AI Critical Analysis:**")
#                         st.markdown(f"<div class='analysis-card'>{analysis}</div>", unsafe_allow_html=True)
#             else:
#                 st.warning("No articles found. Try a different search term.")

# elif mode == "Analyze a Single URL":
#     url_input = st.text_input("🔗 Paste the article URL:")
#     if st.button("Analyze Article"):
#         if not url_input.strip():
#             st.warning("Please paste a valid URL.")
#         else:
#             st.markdown(f"<div class='headline-card'><a href='{url_input}' target='_blank'>{url_input}</a></div>", unsafe_allow_html=True)
#             with st.spinner("📄 Fetching article..."):
#                 article_text = fetch_article_text_archive(url_input.strip())
#             if article_text.startswith("❌"):
#                 st.error(article_text)
#             else:
#                 with st.spinner("🤖 Analyzing article..."):
#                     analysis = analyze_article_llama("Custom URL Analysis", article_text)
#                 st.markdown("**📝 Full Article Text (truncated):**")
#                 st.markdown(f"<div class='analysis-card'>{article_text[:800]}{'...' if len(article_text) > 800 else ''}</div>", unsafe_allow_html=True)
#                 st.markdown("**🤖 AI Critical Analysis:**")
#                 st.markdown(f"<div class='analysis-card'>{analysis}</div>", unsafe_allow_html=True)





# import streamlit as st
# import requests
# import subprocess
# import ollama
# from bs4 import BeautifulSoup
# import random
# import os

# # ⚡ Initialize Ollama client (running locally)
# ollama_client = ollama.Client(host="http://localhost:11434")

# # 🗄 Local cache for articles
# if "article_cache" not in st.session_state:
#     st.session_state.article_cache = {}

# # 📄 Function: Fetch a random headline from Google News RSS
# def get_random_headline(search_query):
#     rss_url = f"https://news.google.com/rss/search?q={search_query}&hl=en-AU&gl=AU&ceid=AU:en"
#     response = requests.get(rss_url)
#     soup = BeautifulSoup(response.content, "xml")
#     headlines = []
#     for item in soup.find_all("item")[:15]:  # Fetch more articles for variety
#         title = item.title.text
#         link = item.link.text
#         headlines.append((title, link))
#     random.shuffle(headlines)  # Shuffle for randomness
#     return headlines[0] if headlines else None  # Return one random article

# # 📄 Function: Resolve Google redirect URLs to actual article URLs
# def resolve_google_redirect(url):
#     try:
#         response = requests.get(url, timeout=10, allow_redirects=True)
#         return response.url  # Return the final destination URL
#     except Exception as e:
#         return f"Error resolving redirect: {e}"

# # 📄 Function: Fetch article text (Auto Fetch -> Puppeteer Stealth)
# def fetch_article_text_puppeteer(url):
#     if url in st.session_state.article_cache:
#         return st.session_state.article_cache[url]

#     try:
#         result = subprocess.run(
#             ["node", "fetch_page_puppeteer.js", url],  # 👈 Use Puppeteer Stealth only
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             timeout=180  # Faster than archive.ph
#         )

#         if result.returncode != 0:
#             return f"❌ Puppeteer Error: {result.stderr}"

#         article_text = result.stdout.strip()
#         st.session_state.article_cache[url] = article_text
#         return article_text
#     except Exception as e:
#         return f"❌ Error fetching article: {e}"

# # 📄 Function: Fetch article text (Single URL -> Archive.ph for paywalls)
# def fetch_article_text_archive(url):
#     if url in st.session_state.article_cache:
#         return st.session_state.article_cache[url]

#     try:
#         result = subprocess.run(
#             ["node", "fetch_page.js", url],  # 👈 Your current archive.ph logic
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             timeout=240  # Allow more time for archive.ph
#         )

#         if result.returncode != 0:
#             return f"❌ Archive Error: {result.stderr}"

#         article_text = result.stdout.strip()
#         st.session_state.article_cache[url] = article_text
#         return article_text
#     except Exception as e:
#         return f"❌ Error fetching article: {e}"

# # 🧠 Function: Analyze article with LLaMA
# def analyze_article_llama(title, article_text):
#     prompt = f"""You are a financial analyst. Analyze the following news article in depth. Your response should include:\n
# 1. A detailed summary of the article.\n
# 2. The potential impact on the company, sector, and overall market.\n
# 3. Short-term and long-term implications for investors.\n
# Title: \"{title}\"\n
# Article Content: \"{article_text}\"
# Provide a detailed, professional analysis.
# """
#     try:
#         response = ollama_client.chat(
#             model="llama3",
#             messages=[
#                 {"role": "system", "content": "You are a professional financial analyst."},
#                 {"role": "user", "content": prompt}
#             ],
#             options={"num_predict": 800}  # Allow longer responses
#         )
#         return response['message']['content'].strip()
#     except Exception as e:
#         return f"❌ Error analyzing article: {e}"

# # 🎨 Streamlit App
# st.title("📈 AI Trading Insights Dashboard")
# st.write("Fetch and analyze **1 random article** or analyze a custom URL with a local AI model.")

# # 📝 Mode selection
# mode = st.radio("Select Mode:", ["Auto Fetch Random Article", "Analyze a Single URL"])

# if mode == "Auto Fetch Random Article":
#     search_query = st.text_input("🔍 Enter a topic to search for:", "Australia finance")
#     if st.button("Fetch & Analyze Random Article"):
#         if not search_query.strip():
#             st.warning("Please enter a topic to search for.")
#         else:
#             random_article = get_random_headline(search_query.strip())

#             if random_article:
#                 title, url = random_article
#                 st.markdown(f"### [{title}]({url})")

#                 # ✅ Resolve Google redirect before sending to Puppeteer
#                 real_url = resolve_google_redirect(url)
#                 if real_url.startswith("Error"):
#                     st.error(real_url)
#                 else:
#                     # Fetch full article text (Puppeteer Stealth)
#                     with st.spinner("📄 Fetching article..."):
#                         article_text = fetch_article_text_puppeteer(real_url)

#                     if article_text.startswith("❌"):
#                         st.error(article_text)
#                     else:
#                         # Analyze article with LLaMA
#                         with st.spinner("🤖 Analyzing article..."):
#                             analysis = analyze_article_llama(title, article_text)

#                         # Display results
#                         st.markdown("**📝 Full Article Text (truncated):**")
#                         st.write(article_text[:800] + "..." if len(article_text) > 800 else article_text)
#                         st.markdown("**🤖 AI Analysis:**")
#                         st.write(analysis)
#             else:
#                 st.warning("No articles found. Try a different search term.")

# elif mode == "Analyze a Single URL":
#     url_input = st.text_input("🔗 Paste the article URL:")
#     if st.button("Analyze Article"):
#         if not url_input.strip():
#             st.warning("Please paste a valid URL.")
#         else:
#             st.markdown(f"### [{url_input}]({url_input})")
#             with st.spinner("📄 Fetching article..."):
#                 article_text = fetch_article_text_archive(url_input.strip())  # 👈 Use archive.ph logic here
#             if article_text.startswith("❌"):
#                 st.error(article_text)
#             else:
#                 with st.spinner("🤖 Analyzing article..."):
#                     analysis = analyze_article_llama("Custom URL Analysis", article_text)
#                 st.markdown("**📝 Full Article Text (truncated):**")
#                 st.write(article_text[:800] + "..." if len(article_text) > 800 else article_text)
#                 st.markdown("**🤖 AI Analysis:**")
#                 st.write(analysis)







# import streamlit as st
# import requests
# import subprocess
# import json
# import ollama
# from bs4 import BeautifulSoup

# # ⚡ Initialize Ollama client (running locally)
# ollama_client = ollama.Client(host="http://localhost:11434")

# # 📄 Function: Fetch headlines from Google News RSS
# def get_headlines(search_query):
#     rss_url = f"https://news.google.com/rss/search?q={search_query}&hl=en-AU&gl=AU&ceid=AU:en"
#     response = requests.get(rss_url)
#     soup = BeautifulSoup(response.content, "xml")
#     headlines = []
#     for item in soup.find_all("item")[:5]:  # Limit to 5 articles for speed
#         title = item.title.text
#         link = item.link.text
#         headlines.append((title, link))
#     return headlines

# # 📄 Function: Resolve Google redirect URLs to actual article URLs
# def resolve_google_redirect(url):
#     try:
#         response = requests.get(url, timeout=10, allow_redirects=True)
#         return response.url  # Return the final destination URL
#     except Exception as e:
#         return f"Error resolving redirect: {e}"

# # 📄 Function: Fetch full article text using Playwright
# def fetch_article_text(url, min_length=300):
#     try:
#         # Step 1: Use Playwright to fetch clean article text
#         result = subprocess.run(
#             ["node", "fetch_page.js", url],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             timeout=90
#         )

#         if result.returncode != 0:
#             return f"Playwright Error: {result.stderr}"

#         article_text = result.stdout.strip()

#         # Sanity check: ensure the text isn’t empty or too short
#         if len(article_text) < min_length:
#             return "Error: Article content is too short or missing."

#         # Return clean text to be analyzed by LLaMA
#         return article_text
#     except Exception as e:
#         return f"Error fetching article: {e}"

# # 🧠 Function: Analyze article with LLaMA
# def analyze_article_llama(title, article_text):
#     prompt = f"""You are a financial analyst. Analyze the following news article in depth. Your response should include:

# 1. A detailed summary of the article.
# 2. The potential impact on the company, sector, and overall market.
# 3. Short-term and long-term implications for investors.

# Title: "{title}"
# Article Content: "{article_text}"

# Provide a detailed, professional analysis.
# """
#     try:
#         response = ollama_client.chat(
#             model="llama3",
#             messages=[
#                 {"role": "system", "content": "You are a professional financial analyst."},
#                 {"role": "user", "content": prompt}
#             ],
#             options={"num_predict": 800}  # Allow longer responses
#         )
#         return response['message']['content'].strip()
#     except Exception as e:
#         return f"Error analyzing article: {e}"

# # 🎨 Streamlit App
# st.title("📈 AI Trading Insights Dashboard (Full Article Analysis)")
# st.write("Fetch and analyze full articles online or analyze a custom URL with a local AI model.")

# # 📝 Mode selection
# mode = st.radio("Select Mode:", ["Auto Fetch Articles", "Analyze a Single URL"])

# if mode == "Auto Fetch Articles":
#     search_query = st.text_input("🔍 Enter a topic to search for:", "Australia finance")
#     if st.button("Get Insights"):
#         if not search_query.strip():
#             st.warning("Please enter a topic to search for.")
#         else:
#             st.session_state.insights = []  # Clear old results
#             headlines = get_headlines(search_query.strip())

#             if headlines:
#                 st.success(f"Found {len(headlines)} articles for: **{search_query}**")
#                 for i, (title, url) in enumerate(headlines):
#                     st.markdown(f"### [{title}]({url})")

#                     # Resolve Google redirect
#                     real_url = resolve_google_redirect(url)
#                     if real_url.startswith("Error"):
#                         st.error(real_url)
#                         continue

#                     # Fetch full article text with relaxed min length for auto fetch
#                     article_text = fetch_article_text(real_url, min_length=200)
#                     if article_text.startswith("Error"):
#                         st.error(article_text)
#                         continue

#                     # Analyze article with LLaMA
#                     analysis = analyze_article_llama(title, article_text)

#                     # Display results
#                     st.markdown("**📝 Full Article Text (truncated):**")
#                     st.write(article_text[:800] + "..." if len(article_text) > 800 else article_text)
#                     st.markdown("**🤖 AI Analysis:**")
#                     st.write(analysis)
#             else:
#                 st.warning("No articles found. Try a different search term.")

# elif mode == "Analyze a Single URL":
#     url_input = st.text_input("🔗 Paste the article URL:")
#     if st.button("Analyze Article"):
#         if not url_input.strip():
#             st.warning("Please paste a valid URL.")
#         else:
#             st.markdown(f"### [{url_input}]({url_input})")
#             article_text = fetch_article_text(url_input.strip(), min_length=300)
#             if article_text.startswith("Error"):
#                 st.error(article_text)
#             else:
#                 analysis = analyze_article_llama("Custom URL Analysis", article_text)
#                 st.markdown("**📝 Full Article Text (truncated):**")
#                 st.write(article_text[:800] + "..." if len(article_text) > 800 else article_text)
#                 st.markdown("**🤖 AI Analysis:**")
#                 st.write(analysis)








# This code is a Streamlit app that fetches financial news headlines from Google News RSS,
# fetches full article text using Playwright and Mercury Parser, and analyzes the articles
# using a local LLaMA model. It allows users to either automatically fetch articles based on
# a search query or analyze a single URL provided by the user. The app displays the article
# text and the AI-generated analysis in a user-friendly interface.


# import streamlit as st
# import requests
# from bs4 import BeautifulSoup
# import ollama

# # ⚡ Initialize Ollama client (running locally)
# ollama_client = ollama.Client(host="http://localhost:11434")

# # 📄 Function: Fetch news headlines from Google News RSS
# def get_headlines(search_query):
#     # Build Google News RSS URL with the search term
#     rss_url = f"https://news.google.com/rss/search?q={search_query}&hl=en-AU&gl=AU&ceid=AU:en"
#     response = requests.get(rss_url)
#     soup = BeautifulSoup(response.content, "xml")
#     headlines = []

#     # Parse top 10 items
#     for item in soup.find_all("item")[:10]:
#         title = item.title.text
#         link = item.link.text
#         headlines.append((title, link))

#     return headlines

# # 🧠 Function: Use LLaMA (local model) to analyze headline
# def analyze_headline_llama(headline):
#     prompt = f"""Analyze the following financial news headline and provide an extensive, analytical summary. Your response should include:

# 1. The potential impact on the company, sector, and overall market.
# 2. Possible reasons behind this news and its context in the current financial climate.
# 3. Short-term and long-term implications for investors.

# Headline: "{headline}"

# Respond in a detailed, professional tone.
# """
    
#     try:
#         response = ollama_client.chat(
#             model="llama3",
#             messages=[
#                 {"role": "system", "content": "You are a professional financial analyst."},
#                 {"role": "user", "content": prompt}
#         ],
#         options={"num_predict": 500}  # 🔥 Allow longer responses (500 tokens)
#     )

#         # response = ollama_client.chat(
#         #     model="llama3",  # Or "mistral" for a faster/smaller model
#         #     messages=[
#         #         {"role": "system", "content": "You are a financial news sentiment analyzer."},
#         #         {"role": "user", "content": prompt}
#         #     ]
#         # )
#         return response['message']['content'].strip()
#     except Exception as e:
#         return f"Error analyzing headline: {e}"

# # 🎨 Streamlit App
# st.title("📈 AI Trading Insights Dashboard (Google News + LLaMA)")
# st.write("Search for any topic and analyze headlines with a local AI model.")

# # 📝 Search bar
# search_query = st.text_input("🔍 Enter a topic to search for:", "Australia finance")

# # Button to fetch and analyze
# if st.button("Get Insights", key="get_insights_btn") and search_query.strip():
#     st.session_state.insights = []  # Clear old results
#     headlines = get_headlines(search_query.strip())

#     if headlines:
#         st.success(f"Found {len(headlines)} headlines for: **{search_query}**")
#         for i, (headline, url) in enumerate(headlines):
#             st.markdown(f"### [{headline}]({url})")

#             # Analyze headline with LLaMA
#             analysis = analyze_headline_llama(headline)

#             # Store and display
#             st.session_state.insights.append((headline, analysis))
#             st.write(analysis)
#     else:
#         st.warning("No headlines found. Try a different search term.")

# # Redisplay results after rerun
# if "insights" in st.session_state and st.session_state.insights:
#     st.markdown("---")
#     st.markdown("### 🔁 Previously Fetched Insights")
#     for headline, analysis in st.session_state.insights:
#         st.markdown(f"**{headline}**")
#         st.write(analysis)

