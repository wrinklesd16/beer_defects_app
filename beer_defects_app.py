from flask import Flask, request, render_template_string, send_file
import pandas as pd

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
    "Phenolic": {
        "Chemical Makeup": "Phenols",
        "Brewing Stage": "Fermentation",
        "Origins": "Wild yeast contamination, improper yeast strain selection, or chlorine in water.",
        "Off-Flavors": ["Medicinal", "Band-Aid", "Clove"],
        "Solutions": [
            "Sanitize all equipment thoroughly to avoid wild yeast contamination.",
            "Filter or treat brewing water to remove chlorine or chloramines."
        ],
        "Prevention": [
            "Use appropriate yeast strains for the desired beer style.",
            "Perform proper cleaning and sanitation."
        ],
        "Learn More": "https://beerandbrewing.com/off-flavor-phenolic/",
        "Category": "Fermentation"
    },
    "Oxidation": {
        "Chemical Makeup": "Various oxidative compounds",
        "Brewing Stage": "Packaging and Storage",
        "Origins": "Exposure to oxygen during or after fermentation.",
        "Off-Flavors": ["Papery", "Cardboard", "Stale"],
        "Solutions": [
            "Minimize oxygen exposure during packaging and storage.",
            "Purge oxygen from containers with CO2 before filling."
        ],
	"Learn More": "https://beerandbrewing.com/off-flavor-oxidation/",
        "Category": "Packaging"
    },
      "Metallic": {
        "Chemical Makeup": "Iron, copper, or other metal ions",
        "Brewing Stage": "Water and Equipment",
        "Origins": "Exposure to metal equipment, poor water quality, or contaminated ingredients.",
        "Off-Flavors": ["Metallic", "Blood-like", "Tinny"],
        "Solutions": [
            "Check brewing equipment for corrosion or metal exposure.",
            "Use a water filter to remove metallic ions."
        ],
        "Prevention": [
            "Avoid using old or corroded metal equipment.",
            "Monitor water quality and filter as needed."
        ],
        "Learn More": "https://beerandbrewing.com/off-flavor-metallic/",
        "Category": "Water"
    },
    "Astringency": {
        "Chemical Makeup": "Polyphenols, tannins",
        "Brewing Stage": "Mashing/Sparging",
        "Origins": "Over-sparging, over-crushing grains, or excessive steeping of specialty grains.",
        "Off-Flavors": ["Tart", "Dry", "Puckering"],
        "Solutions": [
            "Avoid over-sparging or using excessively hot water during sparging.",
            "Use proper grain-crushing techniques."
        ],
        "Prevention": [
            "Monitor sparge water temperature and pH.",
            "Steep specialty grains at appropriate temperatures."
        ],
        "Learn More": "https://beerandbrewing.com/off-flavor-astringency/",
        "Category": "Mashing"
    },
    "Alcoholic": {
        "Chemical Makeup": "Ethanol and fusel alcohols",
        "Brewing Stage": "Fermentation",
        "Origins": "High fermentation temperatures or excessive fermentation stress.",
        "Off-Flavors": ["Hot", "Solvent-like"],
        "Solutions": [
            "Control fermentation temperatures within the yeast's recommended range.",
            "Pitch an adequate amount of yeast to avoid stress."
        ],
        "Prevention": [
            "Ferment at the proper temperature for the yeast strain.",
            "Avoid under-pitching yeast."
        ],
        "Learn More": "https://beerandbrewing.com/off-flavor-alcoholic/",
        "Category": "Fermentation"
    },
    "Chlorophenolic": {
        "Chemical Makeup": "Chlorophenols",
        "Brewing Stage": "Water and Equipment",
        "Origins": "Chlorine or chloramine in brewing water or sanitizers.",
        "Off-Flavors": ["Plastic", "Medicinal", "Band-Aid"],
        "Solutions": [
            "Use filtered or treated water to remove chlorine or chloramine.",
            "Rinse equipment thoroughly after sanitizing."
        ],
        "Prevention": [
            "Use brewing water free of chlorine or chloramines.",
            "Sanitize carefully and rinse thoroughly."
        ],
        "Learn More": "https://beerandbrewing.com/off-flavor-chlorophenolic/",
        "Category": "Water"
    },
    "Sourness": {
        "Chemical Makeup": "Lactic acid, acetic acid",
        "Brewing Stage": "Fermentation/Contamination",
        "Origins": "Bacterial contamination or intentional souring processes.",
        "Off-Flavors": ["Tart", "Sour"],
        "Solutions": [
            "Ensure thorough sanitation to prevent unwanted bacterial contamination.",
            "Control the souring process in intentionally soured beers."
        ],
        "Prevention": [
            "Use a controlled souring process with known lactic acid bacteria.",
            "Sanitize all equipment thoroughly."
        ],
        "Learn More": "https://beerandbrewing.com/off-flavor-sourness/",
        "Category": "Fermentation"
   }
}

# Troubleshooting HTML template
troubleshooting_template = """
<!DOCTYPE html>
<html>
<head><title>Troubleshooting Guide</title></head>
<body>
    <h1>Troubleshooting Guide</h1>
    <form method="POST">
        <label for="stage">Brewing Stage (e.g., Fermentation, Boil, Packaging):</label>
        <input type="text" id="stage" name="stage" value="{{ stage }}">
        <br>
        <label for="off_flavors">Off-Flavors (comma-separated):</label>
        <input type="text" id="off_flavors" name="off_flavors" value="{{ off_flavors }}">
        <br>
        <button type="submit">Troubleshoot</button>
    </form>
    {% if matches %}
    <h2>Matching Defects:</h2>
    <ul>
        {% for name, details in matches.items() %}
        <li><a href="/defect/{{ name }}">{{ name }}</a>: {{ ", ".join(details['Off-Flavors']) }}</li>
        {% endfor %}
    </ul>
    {% elif stage or off_flavors %}
    <p>No matching defects found for your inputs.</p>
    {% endif %}
    <a href="/">Back to Home</a>
</body>
</html>
"""

# Home page
@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>Beer Flavor Defects App</title></head>
    <body>
        <h1>Beer Flavor Defects App</h1>
        <nav>
            <ul>
                <li><a href="/defects">View All Defects</a></li>
                <li><a href="/search">Search Defects</a></li>
                <li><a href="/troubleshoot">Troubleshooting Guide</a></li>
 		<li><a href="/analyze">Analyze Recipe</a></li>
                <li><a href="/export">Export Data to Excel</a></li>
            </ul>
        </nav>
    </body>
    </html>
    """)
# View All Defects
@app.route('/defects')
def list_defects():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>All Defects</title></head>
    <body>
        <h1>All Defects</h1>
        <ul>
            {% for name in defects.keys() %}
            <li><a href="/defect/{{ name }}">{{ name }}</a></li>
            {% endfor %}
        </ul>
        <a href="/">Back to Home</a>
    </body>
    </html>
    """, defects=flavor_defects)

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

# Troubleshooting guide
@app.route('/troubleshoot', methods=['GET', 'POST'])
def troubleshoot():
    stage = ""
    off_flavors = ""
    matches = {}
    if request.method == 'POST':
        stage = request.form.get('stage', '').strip().lower()
        off_flavors = request.form.get('off_flavors', '').strip().lower()
        off_flavor_list = [flavor.strip() for flavor in off_flavors.split(",")] if off_flavors else []

        for name, details in flavor_defects.items():
            matches_stage = not stage or stage in details.get("Brewing Stage", "").lower()
            matches_flavor = not off_flavor_list or any(flavor in map(str.lower, details.get("Off-Flavors", [])) for flavor in off_flavor_list)

            if matches_stage and matches_flavor:
                matches[name] = details

    return render_template_string(troubleshooting_template, stage=stage, off_flavors=off_flavors, matches=matches)

# Analyze Recipe
@app.route('/analyze', methods=['GET', 'POST'])
def analyze_recipe():
    boil_time = ferment_temp = None
    potential_issues = []
    if request.method == 'POST':
        boil_time = int(request.form.get('boil_time', 0))
        ferment_temp = float(request.form.get('ferment_temp', 0))
        
        # Analyze the boil time and fermentation temperature
        if boil_time < 60:
            potential_issues.append("DMS (Dimethyl Sulfide)")
        if ferment_temp > 70:
            potential_issues.append("Alcoholic (Hot)")
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>Analyze Recipe</title></head>
    <body>
        <h1>Analyze Recipe</h1>
        <form method="POST">
            <label for="boil_time">Boil Time (minutes):</label>
            <input type="number" id="boil_time" name="boil_time">
            <br>
            <label for="ferment_temp">Fermentation Temperature (°F):</label>
            <input type="number" id="ferment_temp" name="ferment_temp">
            <br>
            <button type="submit">Analyze</button>
        </form>
        {% if boil_time and ferment_temp %}
        <h2>Analysis Results:</h2>
        <ul>
            <li><strong>Boil Time:</strong> {{ boil_time }} minutes</li>
            <li><strong>Fermentation Temperature:</strong> {{ ferment_temp }}°F</li>
            {% if potential_issues %}
                <h3>Potential Issues:</h3>
                <ul>
                    {% for issue in potential_issues %}
                    <li>{{ issue }}</li>
                    {% endfor %}
                </ul>
            {% else %}
                <p>No significant issues detected.</p>
            {% endif %}
        </ul>
        {% endif %}
        <a href="/">Back to Home</a>
    </body>
    </html>
    """, boil_time=boil_time, ferment_temp=ferment_temp, potential_issues=potential_issues)

# Export defects to Excel
@app.route('/export')
def export_defects():
    # Convert the defects dictionary to a pandas DataFrame
    df = pd.DataFrame.from_dict(flavor_defects, orient='index')
    filename = "beer_defects.xlsx"
    df.to_excel(filename)

    # Return the file for download
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
