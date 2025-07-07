import streamlit as st
import json
import groq
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from axe_selenium_python import Axe

# ========== CONFIGURATION ==========
GROQ_API_KEY = "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"
GROQ_MODEL = "llama3-8b-8192"
                
# ========== SETUP STREAMLIT UI ==========
st.set_page_config(page_title="AI-Powered Accessibility Scanner", layout="wide")
st.title("🔍 AI-Powered Accessibility Scanner")
st.markdown("Analyze any webpage for accessibility issues and get **LLM-suggested WCAG-compliant fixes.**")

url = st.text_input("Enter URL to scan", value="https://w3.ibm.com/", placeholder="https://example.com")
run_scan = st.button("🚀 Run Accessibility Scan")

# ========== MAIN LOGIC ==========
def run_accessibility_scan(target_url):
    st.info("Launching headless browser and analyzing page...", icon="🕵️‍♂️")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(target_url)
        axe = Axe(driver)
        axe.inject()
        results = axe.run()

        issues = results.get("violations", [])
        ai_remediations = {}

        client = groq.Client(api_key=GROQ_API_KEY)

        progress = st.progress(0)
        total = len(issues)

        for i, issue in enumerate(issues):
            html_element = issue["nodes"][0]["html"]

            prompt = f"""
            You are an expert web accessibility reviewer and front-end engineer. You are given raw HTML content from a real webpage. Analyze the HTML code and identify all accessibility issues based on the latest WCAG 2.1/2.2 standards.

            Your goal is to:
            1. Detect and explain any accessibility problems.
            2. Provide WCAG-compliant or ADA-compliant code-level fixes.
            3. Return:
               a. A brief summary of issues found
               b. A list of recommended fixes
               c. The updated and fixed HTML

            Input HTML: {html_element}
            """

            try:
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": f"Fix accessibility issue for element: {html_element}"}
                    ]
                )
                suggested_fix = response.choices[0].message.content
            except Exception as e:
                print(e)
                suggested_fix = f"⚠️ Error calling LLM: {e}"

            ai_remediations[issue["id"]] = {
                "Issue": issue["description"],
                "Element": html_element,
                "LLM-Suggested Fix": suggested_fix
            }

            progress.progress((i + 1) / total)

        driver.quit()
        return ai_remediations

    except Exception as e:
        driver.quit()
        st.error(f"🚨 Error during scan: {e}")
        return None

# ========== RUN BUTTON ==========
if run_scan and url:
    with st.spinner("Running accessibility analysis..."):
        results = run_accessibility_scan(url)

    if results:
        st.success("✅ Scan complete! Review issues and suggested fixes below.")

        # Display results
        for rule_id, fix in results.items():
            with st.expander(f"🚨 Issue: {fix['Issue']}"):
                st.markdown(f"**❌ Affected Element:** `{fix['Element']}`", unsafe_allow_html=True)
                st.markdown(f"**💡 LLM-Suggested Fix:**")
                st.code(fix["LLM-Suggested Fix"], language="html")

        # Save downloadable report
        st.download_button(
            label="💾 Download JSON Report",
            data=json.dumps(results, indent=2),
            file_name="accessibility_fixes.json",
            mime="application/json"
        )

