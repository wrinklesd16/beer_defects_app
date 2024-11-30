from flask import Flask, request, render_template_string, send_file, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Comprehensive beer flavor defects dictionary
flavor_defects = {
    "Diacetyl": {
        "Chemical Makeup": "2,3-butanedione",
        "Brewing Stage": "Fermentation",
        "Origins": "Insufficient yeast activity or bacterial contamination during fermentation.",
        "Off-Flavors": ["Buttery", "Butterscotch"],
        "Solutions": [
            "Perform a diacetyl rest during fermentation by raising the temperature slightly before cold-crashing.",
            "Ensure proper sanitation to avoid bacterial contamination.",
            "Pitch a healthy amount of yeast."
        ],
        "Prevention": [
            "Monitor fermentation closely and avoid premature racking or bottling.",
            "Use high-quality yeast and ensure adequate oxygenation before pitching."
        ],
        "Learn More": "https://beerandbrewing.com/off-flavor-diacetyl/",
        "Category": "Fermentation"
    },
    "Acetaldehyde": {
        "Chemical Makeup": "Ethanal",
        "Brewing Stage": "Fermentation",
        "Origins": "Incomplete fermentation or premature bottling/kegging.",
        "Off-Flavors": ["Green Apple", "Raw Pumpkin"],
        "Solutions": [
            "Allow the beer to fully ferment and condition before packaging.",
            "Increase the fermentation temperature slightly for lagers to allow yeast to clean up residual acetaldehyde."
        ],
        "Prevention": [
            "Give the beer adequate time for fermentation and conditioning.",
            "Avoid stress on the yeast by maintaining a consistent fermentation temperature."
        ],
        "Learn More": "https://beerandbrewing.com/off-flavor-acetaldehyde/",
        "Category": "Fermentation"
    },
    "DMS (Dimethyl Sulfide)": {
        "Chemical Makeup": "Dimethyl sulfide",
        "Brewing Stage": "Boil",
        "Origins": "Improper wort boil or rapid cooling, or bacterial contamination.",
        "Off-Flavors": ["Cooked Corn", "Cabbage", "Vegetal"],
        "Solutions": [
            "Ensure a vigorous boil to drive off DMS precursors.",
            "Cool the wort quickly after the boil to prevent further DMS formation."
        ],
        "Prevention": [
            "Avoid covering the boil kettle, which traps DMS.",
            "Use high-quality malt with lower DMS precursors."
        ],
        "Learn More": "https://beerandbrewing.com/off-flavor-dms/",
        "Category": "Boil"
    },
    # Additional defects go here...
}

# HTML templates
homepage_template = """
<!DOCTYPE html>
<html>
<head><title>Beer Defects App</title></head>
<body>
    <h1>Beer Flavor Defects App</h1>
    <nav>
        <ul>
            <li><a href="/defects">View All Defects</a></li>
            <li><a href="/search">Search Defects</a></li>
            <li><a href="/analyze">Analyze Recipe</a></li>
            <li><a href="/troubleshoot">Troubleshooting Guide</a></li>
            <li><a href="/export">Export Data</a></li>
        </ul>
    </nav>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(homepage_template)

@app.route('/defects')
def list_defects():
    defects_by_category = {}
    for name, details in flavor_defects.items():
        category = details.get("Category", "Uncategorized")
        if category not in defects_by_category:
            defects_by_category[category] = []
        defects_by_category[category].append((name, details))
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>All Defects</title></head>
    <body>
        <h1>All Defects</h1>
        {% for category, defects in defects_by_category.items() %}
        <h2>{{ category }}</h2>
        <ul>
            {% for name, details in defects %}
            <li><a href="/defect/{{ name }}">{{ name }}</a>: {{ ", ".join(details['Off-Flavors']) }}</li>
            {% endfor %}
        </ul>
        {% endfor %}
        <a href="/">Back to Home</a>
    </body>
    </html>
    """, defects_by_category=defects_by_category)

@app.route('/defect/<name>')
def defect_detail(name):
    defect = flavor_defects.get(name)
    if defect:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><title>{{ defect_name }}</title></head>
        <body>
            <h1>{{ defect_name }}</h1>
            <p><strong>Chemical Makeup:</strong> {{ defect['Chemical Makeup'] }}</p>
            <p><strong>Brewing Stage:</strong> {{ defect['Brewing Stage'] }}</p>
            <p><strong>Origins:</strong> {{ defect['Origins'] }}</p>
            <h3>Solutions</h3>
            <ul>
                {% for solution in defect['Solutions'] %}
                <li>{{ solution }}</li>
                {% endfor %}
            </ul>
            <h3>Prevention</h3>
            <ul>
                {% for prevention in defect['Prevention'] %}
                <li>{{ prevention }}</li>
                {% endfor %}
            </ul>
            <a href="{{ defect['Learn More'] }}">Learn More</a>
            <br><br>
            <a href="/defects">Back to All Defects</a>
        </body>
        </html>
        """, defect_name=name, defect=defect)
    else:
        return "Defect not found", 404

@app.route('/search', methods=['GET', 'POST'])
def search_defects():
    query = ""
    matches = {}
    if request.method == 'POST':
        query = request.form.get('query', '').strip().lower()
        queries = [q.strip() for q in query.split(",")]
        matches = {name: details for name, details in flavor_defects.items() if any(q in map(str.lower, details.get("Off-Flavors", [])) for q in queries)}
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>Search Defects</title></head>
    <body>
        <h1>Search Defects</h1>
        <form method="POST">
            <label for="query">Enter Off-Flavor (comma-separated for multiple):</label>
            <input type="text" id="query" name="query" value="{{ query }}">
            <button type="submit">Search</button>
        </form>
        {% if matches %}
        <h2>Results:</h2>
        <ul>
            {% for name, details in matches.items() %}
            <li><a href="/defect/{{ name }}">{{ name }}</a>: {{ ", ".join(details['Off-Flavors']) }}</li>
            {% endfor %}
        </ul>
        {% elif query %}
        <p>No results found for "{{ query }}".</p>
        {% endif %}
        <a href="/">Back to Home</a>
    </body>
    </html>
    """, query=query, matches=matches)

@app.route('/analyze', methods=['GET', 'POST'])
def analyze_recipe():
    boil_time = ferment_temp = None
    potential_issues = []
    if request.method == 'POST':
        boil_time = int(request.form.get('boil_time', 0))
        ferment_temp = float(request.form.get('ferment_temp', 0))
        if boil_time < 60:
            potential_issues.append("DMS (Dimethyl Sulfide)")
        if ferment_temp > 70:
            potential_issues.append("Alcoholic (Hot)")
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>Recipe Analysis</title></head>
    <body>
        <h1>Analyze Recipe</h1>
        <form method="POST">
            <label for="boil_time">Boil Time (minutes):</label>
            <input type="number" id="boil_time" name="boil_time">
            <label for="ferment_temp">Fermentation Temperature (°F):</label>
            <input type="number" id="ferment_temp" name="ferment_temp">
            <button type="submit">Analyze</button>
        </form>
        {% if boil_time and ferment_temp %}
        <h2>Results:</h2>
        <ul>
            {% for issue in potential_issues %}
            <li>{{ issue }}</li>
            {% endfor %}
        </ul>
        {% endif %}
        <a href="/">Back to Home</a>
    </body>
    </html>
    """, boil_time=boil_time, ferment_temp=ferment_temp, potential_issues=potential_issues)

@app.route('/export')
def export_defects():
    df = pd.DataFrame.from_dict(flavor_defects, orient='index')
    filename = "beer_defects.xlsx"
    df.to_excel(filename)
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

