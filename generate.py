#!/usr/bin/env python3
"""
TTM Proposal Generator
Usage: python3 generate.py <proposal_data.json>

Or run from fishtail directly — reads a Google Doc and outputs a live proposal URL.
"""
import json, sys, os, subprocess, urllib.request, time

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_USER = "bigfish777-dog"
TEMPLATE_PATH = os.path.dirname(os.path.abspath(__file__))

def create_repo(name):
    """Create a new GitHub repo for the proposal."""
    payload = json.dumps({"name": name, "description": f"TTM Proposal — {name}", "private": False, "auto_init": False}).encode()
    req = urllib.request.Request("https://api.github.com/user/repos", data=payload)
    req.add_header("Authorization", f"token {GITHUB_TOKEN}")
    req.add_header("Content-Type", "application/json")
    try:
        resp = json.load(urllib.request.urlopen(req, timeout=15))
        return resp.get("clone_url", "").replace("https://", f"https://{GITHUB_TOKEN}@")
    except Exception as e:
        return None

def enable_pages(repo_name):
    """Enable GitHub Pages on the repo."""
    payload = json.dumps({"source": {"branch": "main", "path": "/"}}).encode()
    req = urllib.request.Request(f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/pages", data=payload)
    req.add_header("Authorization", f"token {GITHUB_TOKEN}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/vnd.github+json")
    try:
        urllib.request.urlopen(req, timeout=15)
        return True
    except:
        return False

def build_proposal(data):
    """Fill the template with proposal data and return HTML."""
    with open(os.path.join(TEMPLATE_PATH, "index.html")) as f:
        html = f.read()

    # Build phases HTML
    phases_html = ""
    for phase in data.get("phases", []):
        phases_html += f'<div class="phase"><p class="phase-title">{phase["title"]}</p>'
        if phase.get("subtitle"):
            phases_html += f'<p class="phase-subtitle">{phase["subtitle"]}</p>'
        phases_html += f'<div class="body-text"><p>{phase["description"]}</p></div>'
        for activity in phase.get("activities", []):
            phases_html += f'<p class="activity-title">{activity["title"]}</p><div class="body-text"><p>{activity["description"]}</p></div>'
        phases_html += "</div>"

    # Build deliverables
    deliverables_html = ""
    for d in data.get("deliverables", []):
        deliverables_html += f'<li><strong>{d["title"]}</strong> — {d["description"]}</li>'

    # Build pricing lines
    pricing_html = ""
    for p in data.get("pricing", {}).get("lines", []):
        pricing_html += f'<div class="pricing-line"><span class="label">{p["label"]}</span><span class="value">{p["value"]}</span></div>'

    # Build next steps
    steps_html = ""
    for s in data.get("next_steps", []):
        steps_html += f'<li><div class="step-num">{s["num"]}</div><span>{s["text"]}</span></li>'

    # Comparison table
    table_html = ""
    if data.get("comparison_table"):
        t = data["comparison_table"]
        table_html = '<table class="compare-table"><thead><tr>'
        for h in t["headers"]:
            table_html += f"<th>{h}</th>"
        table_html += "</tr></thead><tbody>"
        for row in t["rows"]:
            table_html += "<tr>"
            for cell in row:
                table_html += f"<td>{cell}</td>"
            table_html += "</tr>"
        table_html += "</tbody></table>"

    # Build opening copy
    opening_html = "".join(f"<p>{p}</p>" for p in data.get("opening_paragraphs", []))
    plan_intro_html = "".join(f"<p>{p}</p>" for p in data.get("plan_intro", []))

    replacements = {
        "{{CLIENT_NAME}}": data["client_name"],
        "{{DATE}}": data.get("date", ""),
        "{{COVER_SUBTITLE}}": data.get("cover_subtitle", ""),
        "{{OPENING_HEADING}}": data.get("opening_heading", "My take."),
        "{{OPENING_COPY}}": opening_html,
        "{{PLAN_INTRO}}": plan_intro_html,
        "{{PHASES}}": phases_html,
        "{{DELIVERABLES}}": deliverables_html,
        "{{INVESTMENT_INTRO}}": "".join(f"<p>{p}</p>" for p in data.get("investment_intro", [])),
        "{{PRICING_TITLE}}": data.get("pricing", {}).get("title", ""),
        "{{PRICING_LINES}}": pricing_html,
        "{{PRICING_NOTE}}": data.get("pricing", {}).get("note", ""),
        "{{COMPARISON_TABLE}}": table_html,
        "{{NEXT_STEPS}}": steps_html,
        "{{SIGN_OFF}}": data.get("sign_off", "Looking forward to working with you."),
        "{{SIGNOFF_NAME}}": data.get("signoff_name", "Nick 'Fish' Fisher"),
        "{{PROPOSAL_URL}}": data.get("proposal_url", ""),
    }

    for key, val in replacements.items():
        html = html.replace(key, val)

    return html

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            data = json.load(f)
        print(build_proposal(data))
