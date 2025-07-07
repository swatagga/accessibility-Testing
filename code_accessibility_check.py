import os
import json
import subprocess
import groq
from selenium import webdriver
from axe_selenium_python import Axe

# 🔍 Groq API Configuration
GROQ_API_KEY = "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"

# 🛠️ Step 1: Clone GitHub Repository
GITHUB_REPO_URL = "https://github.com/harismuneer/Flight-Booking-System-JavaServlets_App.git"  # Replace with the actual repo URL
LOCAL_REPO_PATH = "./repo_clone"

if not os.path.exists(LOCAL_REPO_PATH):
    subprocess.run(["git", "clone", GITHUB_REPO_URL, LOCAL_REPO_PATH], check=True)

# 🏗️ Step 2: Scan HTML, CSS, and JavaScript for Accessibility Issues
html_files = []
excluded_folders = {"build/web"}

for root, dirs, files in os.walk(LOCAL_REPO_PATH):
    dirs[:] = [d for d in dirs if d not in excluded_folders]  # Exclude specified folders
    for file in files:
        if file.endswith(".html") or file.endswith(".css") or file.endswith(".js"):
            html_files.append(os.path.join(root, file))

accessibility_issues = {}

# 🔎 Step 3: Analyze Each File Using Selenium & Axe-Core
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

for file in html_files:
    driver.get(f"file://{file}")
    axe = Axe(driver)
    axe.inject()
    results = axe.run()

    for issue in results["violations"]:
        html_element = issue["nodes"][0]["html"]
        
        prompt = f"""
            You are an expert web accessibility reviewer and front-end engineer. You are given raw HTML content from a real webpage. Analyze the HTML code and identify all accessibility issues based on the latest WCAG 2.1/2.2 standards.

            Your goal is to:
            1. Detect and explain any accessibility problems.
            2. Provide WCAG-compliant code-level fixes.
            3. Return:
               a. A brief summary of issues found
               b. A list of recommended fixes
               c. The updated and fixed HTML

            Input HTML: {html_element}
            """
            
        # 🤖 AI-Powered Fix Suggestion (Groq)
        client = groq.Client(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Fix accessibility issue for code element: {html_element}"}
            ]
        )

        suggested_fix = response.choices[0].message.content
        
        accessibility_issues[file] = {
            "Issue": issue["description"],
            "Element": html_element,
            "AI-Suggested Fix": suggested_fix
        }

driver.quit()

# 📝 Step 4: Save AI-Suggested Fixes to JSON
with open("github_accessibility_fixes.json", "w") as f:
    json.dump(accessibility_issues, f, indent=4)

# ✅ Step 5: Print AI-Generated Fix Suggestions
print("\n🔹 AI-Powered Accessibility Fixes for GitHub Repository:\n")
for file, fix in accessibility_issues.items():
    print(f"📄 File: {file}")
    print(f"🚨 Issue: {fix['Issue']}")
    print(f"🔹 Affected Code: {fix['Element']}")
    print(f"✅ Suggested Fix: {fix['AI-Suggested Fix']}\n")
