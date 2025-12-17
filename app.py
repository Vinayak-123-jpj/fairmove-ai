from flask import Flask, render_template, request
import re
import PyPDF2

app = Flask(__name__)

SCAM_KEYWORDS = {
    "registration fee": 30,
    "processing fee": 30,
    "agent fee": 30,
    "guaranteed visa": 40,
    "no interview": 25,
    "urgent hiring": 20,
    "limited slots": 20,
    "pay immediately": 40,
    "cash payment": 50
}

COUNTRY_RULES = {
    "canada": ["lmia guaranteed", "job bank not required"],
    "uae": ["visit visa job", "pay visa cost"],
    "uk": ["cos guaranteed"],
    "australia": ["pr guaranteed"]
}

FAKE_COMPANIES = [
    "global solutions",
    "international services",
    "worldwide consultancy",
    "overseas careers",
    "immigration experts"
]

OFFICIAL_PORTALS = {
    "canada": "https://www.canada.ca/en/immigration-refugees-citizenship.html",
    "uae": "https://u.ae/en/information-and-services/jobs",
    "uk": "https://www.gov.uk/check-job-offer",
    "australia": "https://immi.homeaffairs.gov.au"
}

def extract_pdf_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text.lower()

def analyze_text(text):
    score = 100
    found = []
    finance = visa = urgency = company = country = 0
    text_lower = text.lower()

    for word, penalty in SCAM_KEYWORDS.items():
        if word in text_lower:
            score -= penalty
            found.append(word)
            if "fee" in word or "payment" in word:
                finance += penalty
            elif "visa" in word:
                visa += penalty
            else:
                urgency += penalty

    for c, rules in COUNTRY_RULES.items():
        if c in text_lower:
            for rule in rules:
                if rule in text_lower:
                    score -= 25
                    country += 25
                    found.append(rule)

    for name in FAKE_COMPANIES:
        if name in text_lower:
            score -= 20
            company += 20
            found.append("suspicious company name")

    score = max(score, 0)

    if score < 40:
        risk = "High Risk"
        color = "high"
        advice = "❌ Do NOT proceed. Strong scam indicators detected."
        confidence = "90%"
    elif score < 70:
        risk = "Medium Risk"
        color = "medium"
        advice = "⚠️ Proceed with caution. Verify employer carefully."
        confidence = "70%"
    else:
        risk = "Low Risk"
        color = "low"
        advice = "✅ Appears safe, but official verification is recommended."
        confidence = "85%"

    highlighted = text
    for item in found:
        highlighted = re.sub(item, f"<mark>{item}</mark>", highlighted, flags=re.IGNORECASE)

    explanation = (
        f"FairMove AI analyzed this offer using rule-based fraud intelligence. "
        f"{len(found)} scam indicators were detected related to payments, visa claims, "
        f"urgency tactics, country rules, and suspicious company patterns."
    )

    links = [link for c, link in OFFICIAL_PORTALS.items() if c in text_lower]

    return {
        "risk": risk,
        "color": color,
        "score": score,
        "advice": advice,
        "confidence": confidence,
        "finance": finance,
        "visa": visa,
        "urgency": urgency,
        "country": country,
        "company": company,
        "keywords": found,
        "highlighted": highlighted,
        "explanation": explanation,
        "links": links
    }

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    history = ""

    if request.method == "POST":
        if "pdf" in request.files and request.files["pdf"].filename:
            history = extract_pdf_text(request.files["pdf"])
        else:
            history = request.form.get("job_text", "")
        result = analyze_text(history)

    return render_template("index.html", result=result, history=history)

if __name__ == "__main__":
    app.run(debug=True)

