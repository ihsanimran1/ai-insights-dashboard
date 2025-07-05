# 📈 AI Insights Dashboard

## 📅 Initial Concept
**Date:** 2025-05-07  
**Time:** 10:00 AM  
**Concept:** Build a local AI-powered tool that fetches and analyzes financial news articles, PDFs, and URLs to provide critical reasoning insights for trading and consulting purposes.  
**Goal:** Help users make informed financial and strategic decisions by delivering high-quality, structured AI analysis, while keeping all AI computation for privacy.  

---

## 🔍 Market Research
- **Competitor Analysis:** Researched existing tools like MarketMuse, Bloomberg Terminal, and Seeking Alpha. Found that they often require subscriptions.  
- **Target Audience:** Financial analysts, traders, consultants, and business decision-makers.  
- **Estimated Market Size:** $13+ billion globally for financial analytics platforms (2025).  

---

## 🛠 Technical Requirements
| Component            | Requirement                                             |
|----------------------|---------------------------------------------------------|
| Programming Language | Python 3.9+                                             |
| Frontend Framework   | Streamlit                                               |
| Backend              | Node.js with Puppeteer and archive.ph fallback          |
| AI Model             | Ollama with LLaMA 3                                     |
| PDF Parsing          | PyMuPDF (fitz)                                          |
| APIs                 | BeautifulSoup for RSS; Puppeteer for dynamic websites   |
| Deployment Target    | Docker container or local machine                       |

---

## 🗺 Project Roadmap

| Task                      | Start Date | End Date   | Status       |
|---------------------------|------------|------------|--------------|
| Requirement Gathering     | 2025-07-01 | 2025-07-02 | ✅ Complete   |
| Backend Scraper (Puppeteer)| 2025-07-02 | 2025-07-04 | ✅ Complete   |
| Streamlit UI              | 2025-07-04 | 2025-07-06 | ✅ Complete   |
| Ollama AI Integration     | 2025-07-06 | 2025-07-07 | ✅ Complete   |
| Testing & Debugging       | 2025-07-07 | 2025-07-08 | ✅ Complete   |
| Packaging (Docker)        | 2025-07-08 | 2025-07-10 | ⏳ In Progress|

---

## 🛠 Technology Stack
- **Backend:** Node.js (Puppeteer with archive.ph support)  
- **Frontend:** Python (Streamlit framework)  
- **AI Model:** LLaMA 3 running on Ollama locally  
- **PDF Parsing:** PyMuPDF  
- **Web Scraping:** BeautifulSoup  
- **Version Control:** GitHub  

---

## 🪵 Challenges & Solutions

| **Challenge**                                                                                      | **Solution**                                                                                                                       |
|-----------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| **Paywalled Articles (e.g., Bloomberg, WSJ)**                                                      | Integrated `archive.ph` fallback to snapshot paywalled pages and extract content safely.                                            |
| **Anti-bot Protections (Cloudflare, dynamic JS rendering)**                                        | Used `puppeteer-extra-plugin-stealth` to bypass anti-bot measures and mimic real browser behavior.                                  |
| **Streamlit UI looked plain and unpolished**                                                       | Designed a custom CSS style with modern buttons and clean layout for better UX.                                                     |
| **Local AI (Ollama) not working in Streamlit Community Cloud**                                     | Shifted to a fully local architecture and documented the setup so users can run the app offline.                                    |
| **Long articles exceeding LLaMA token limits**                                                     | Added automatic truncation and summarization pipelines to preprocess large inputs for AI analysis.                                  |
| **PDF text extraction from scanned documents failed**                                              | Switched to PyMuPDF for better text parsing; flagged unsupported scanned PDFs with a user warning.                                  |
| **Sharing with non-technical users**                                                               | Built a Dockerfile to package all dependencies so the app can run with one command on any machine.                                  |

---

## 🧠 Key Highlights for Portfolio
✅ Full-stack architecture (Python, Node.js, AI).  
✅ Private local AI (LLaMA via Ollama).  
✅ Handles paywalls ethically by analyzing only (not showing articles).  
Dockerized for cross-platform sharing.  (in progress)

---

## ⚠️ Disclaimer
*This project is for educational and portfolio purposes only. It demonstrates technical skills in web scraping, AI integration, and full-stack development. Users are responsible for complying with the terms of service of any websites they access with this tool. The developer does not condone or encourage bypassing paywalls or violating copyright policies.*

---

## 🖥️ How to Run the App Locally

Follow these steps to set up and run the AI Insight Dashboard on your machine:  

**Step 1: Clone the Repository**

git clone https://github.com/<your-username>/ai-insight-dashboard.git
cd ai-insight-dashboard

**Step 2: Set Up Python Virtual Environment**

python3 -m venv venv
source venv/bin/activate

**Step 3: Install Python Dependencies**

pip install -r requirements.txt

**Step 4: Install Node.js Dependencies**

npm install

**Step 5: Install Ollama**

This project uses LLaMA 3 via Ollama, visit their website to download

Start Ollama in the background:
ollama serve

Pull the LLaMA 3 model:
ollama run llama3

**Step 6: Start the App**

streamlit run app.py

**To stop running**

Ctrl + C

