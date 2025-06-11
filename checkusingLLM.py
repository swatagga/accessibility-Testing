import json
import groq
from selenium import webdriver
from axe_selenium_python import Axe

GROQ_API_KEY = "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"

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
driver.get("https://w3.ibm.com/")  # Replace with your target URL

axe = Axe(driver)
axe.inject()
results = axe.run()

issues = results["violations"]
ai_remediations = {}

for issue in issues:
    html_element = issue["nodes"][0]["html"]

    prompt = "You are an expert web accessibility reviewer and front-end engineer. You are given raw HTML content from a real webpage. Analyze the HTML code and identify all accessibility issues based on the latest WCAG (Web Content Accessibility Guidelines) 2.1/2.2 standards. Your goal is to: 1. Detect and explain any accessibility problems or missing features such as: - Missing or unclear <alt> attributes on <img> tags - Improper ARIA roles - Lack of keyboard navigability - Missing form labels - Insufficient color contrast - Improper use of semantic HTML - Lack of focus indicators or screen-reader compatibility 2. Provide WCAG-compliant code-level fixes for each issue you detect. 3. Return: a. A brief summary of all accessibility issues found b. A list of recommended or applied fixes, with explanations c. The updated and fully fixed HTML, ready for re-deployment Only fix the accessibility issues—do not change any visual layout, styling, or business logic. Input HTML: {html_element}"
    client = groq.Client(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="Llama-3.3-70B-Versatile",  
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Fix accessibility issue for element: {html_element}"}
        ]
    )
    
    suggested_fix = response.choices[0].message.content
    
    ai_remediations[issue["id"]] = {
        "Issue": issue["description"],
        "Element": html_element,
        "LLM-Suggested Fix": suggested_fix
    }

with open("llm_accessibility_fixes.json", "w") as f:
    json.dump(ai_remediations, f, indent=4)

print("\n LLM-Powered Accessibility Fixes:\n")
for rule, fix in ai_remediations.items():
    print(f"Issue: {fix['Issue']}")
    print(f"Element: {fix['Element']}")
    print(f"Suggested Fix: {fix['LLM-Suggested Fix']}\n")

driver.quit()
