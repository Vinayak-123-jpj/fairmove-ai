from flask import Flask, render_template, request

app = Flask(__name__)

def analyze_text(text):
    text_lower = text.lower()

    financial = 0
    visa = 0
    urgency = 0
    countries = []

    if "registration fee" in text_lower or "pay upfront" in text_lower:
        financial += 30
    if "guaranteed visa" in text_lower or "no interview" in text_lower:
        visa += 40
    if "urgent hiring" in text_lower or "limited slots" in text_lower:
        urgency += 20

    country_list = ["canada", "uae", "uk", "poland", "romania"]
    for country in country_list:
        if country in text_lower:
            countries.append(country.title())

    total_risk = min(financial + visa + urgency, 100)
    trust_score = 100 - total_risk

    if total_risk >= 60:
        risk = "High Risk"
    elif total_risk >= 30:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"

    checklist = [
        "Verify employer on official government portals",
        "Do not pay any registration or processing fees",
        "Confirm interview process",
        "Check embassy or labor ministry advisories",
        "Avoid offers promising guaranteed visas"
    ]

    recommendation = (
        "This offer should be carefully verified before proceeding. "
        "FairMove AI recommends independent verification."
    )

    explanation = (
        "FairMove AI uses pattern-based risk assessment across financial, visa, "
        "urgency, and regional scam indicators. The system is designed for decision "
        "support and public safety."
    )

    return {
        "risk": risk,
        "trust_score": trust_score,
        "financial": financial,
        "visa": visa,
        "urgency": urgency,
        "countries": countries,
        "checklist": checklist,
        "recommendation": recommendation,
        "explanation": explanation
    }

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        text = request.form.get("text")
        result = analyze_text(text)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)

