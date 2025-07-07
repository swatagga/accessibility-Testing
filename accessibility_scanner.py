import streamlit as st
from playwright.sync_api import sync_playwright
from datetime import datetime
import os
import json

BREAKPOINTS = {
    "Mobile": {"width": 375, "height": 667},
    "Tablet": {"width": 768, "height": 1024},
    "Desktop": {"width": 1440, "height": 900}
}

def load_axe_script():
    with open("axe.min.js", "r", encoding="utf-8") as f:
        return f.read()

def generate_fix_suggestion(rule_id):
    suggestions = {
        "color-contrast": "Adjust foreground and background colors to meet contrast ratio of 4.5:1.",
        "label": "Ensure every input element has a corresponding <label> or aria-label.",
        "image-alt": "Add alt text to all informative <img> elements.",
        "document-title": "Add a meaningful <title> to your HTML <head>.",
        "link-name": "Provide descriptive text for links to clarify purpose."
    }
    return suggestions.get(rule_id, "Review WCAG documentation for specific remediation guidance.")

def run_scan(url):
    axe_script = load_axe_script()
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        for label, size in BREAKPOINTS.items():
            page = context.new_page()
            page.set_viewport_size(size)
            page.goto(url, wait_until="networkidle")
            page.add_script_tag(content=axe_script)

            raw = page.evaluate("() => axe.run()")
            results[label] = raw
            page.close()

        browser.close()
    return results

def save_results(results):
    os.makedirs("reports", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"reports/axe_report_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    return path

# === Streamlit UI ===
st.set_page_config(page_title="Axe Accessibility Scanner", layout="wide")
st.title("🧪 Automated Accessibility Testing App")
st.caption("Streamlined WCAG/ADA scans across multiple device sizes using Playwright + Axe-core")

url = st.text_input("🔗 Enter the website URL to scan", placeholder="https://example.com")

if url and st.button("Run Scan"):
    with st.spinner("Running Axe-core scans on all breakpoints..."):
        results = run_scan(url)
        report_path = save_results(results)

    for label, result in results.items():
        st.subheader(f"📱 {label} Viewport")
        violations = result.get("violations", [])
        st.markdown(f"**{len(violations)} issue(s) detected**")

        if not violations:
            st.success("✅ No accessibility issues found!")
        else:
            for v in violations:
                with st.expander(f"[{v['impact'].upper()}] {v['help']} ({v['id']})"):
                    st.markdown(f"**Description:** {v['description']}")
                    st.markdown(f"**WCAG Tags:** `{', '.join(v['tags'])}`")
                    st.markdown(f"**Fix Recommendation:** {generate_fix_suggestion(v['id'])}")
                    for node in v['nodes'][:1]:
                        st.markdown(f"**Selector:** `{node['target'][0]}`")
                        st.code(node['html'].strip(), language="html")

    with open(report_path, "rb") as f:
        st.download_button("📥 Download Full JSON Report", f, file_name=os.path.basename(report_path))
