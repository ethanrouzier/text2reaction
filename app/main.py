import os
import json
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for, send_file
from .readers import read_from_url, read_local_upload
from .section_finder import find_sections
from .extractor import LLMExtractor

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

HOME_HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>🧪 Text→Reaction (Mistral)</title>
    <style>
      * { box-sizing: border-box; }
      body { 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
      }
      .container { max-width: 1200px; margin: 0 auto; }
      header { 
        text-align: center; margin-bottom: 40px; 
        background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
      }
      h1 { color: #333; margin: 0; font-size: 2.5em; }
      .subtitle { color: #666; margin: 10px 0 0; }
      .card { 
        background: white; border-radius: 20px; padding: 30px; margin: 20px 0; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: none;
      }
      .form-group { margin: 20px 0; }
      label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
      input[type=url], input[type=file], input[type=number] { 
        width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 10px; 
        font-size: 16px; transition: border-color 0.3s;
      }
      input:focus { outline: none; border-color: #667eea; }
      .divider { text-align: center; margin: 20px 0; color: #666; font-weight: 600; }
      button { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; padding: 15px 30px; border-radius: 10px;
        font-size: 16px; font-weight: 600; cursor: pointer; transition: transform 0.2s;
        width: 100%; margin-top: 20px;
      }
      button:hover { transform: translateY(-2px); }
      .quick-test { 
        background: #f8f9fa; border-left: 4px solid #667eea; padding: 20px;
        margin: 20px 0; border-radius: 0 10px 10px 0;
      }
      .loading { display: none; text-align: center; padding: 40px; }
      .spinner { 
        border: 4px solid #f3f3f3; border-top: 4px solid #667eea; 
        border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite;
        margin: 0 auto 20px;
      }
      @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
      .error { background: #fee; color: #c33; padding: 15px; border-radius: 10px; margin: 20px 0; }
      .success { background: #efe; color: #363; padding: 15px; border-radius: 10px; margin: 20px 0; }
    </style>
  </head>
  <body>
    <div class="container">
      <header>
        <h1>🧪 Text→Reaction</h1>
        <p class="subtitle">Intelligent extraction of experimental procedures with Mistral AI</p>
      </header>

      <div class="card">
        <form id="extractForm" action="/extract" method="post" enctype="multipart/form-data">
          <div class="form-group">
            <label for="url">📄 Scientific article URL:</label>
            <input type="url" id="url" name="url" placeholder="https://pubs.acs.org/doi/10.1021/..." />
          </div>
          
          <div class="divider">— or —</div>
          
          <div class="form-group">
            <label for="file">📁 Upload a file:</label>
            <input type="file" id="file" name="file" accept=".pdf,.html,.htm,.txt" />
          </div>
          
          <div class="form-group">
            <label for="max_sections">🔢 Maximum number of sections to analyze:</label>
            <input type="number" id="max_sections" name="max_sections" value="2" min="1" max="5" />
          </div>
          
          <button type="submit">🚀 Extract reactions</button>
        </form>
        
        <div id="loading" class="loading">
          <div class="spinner"></div>
          <p>Analysis in progress... Extracting chemical data with Mistral AI</p>
        </div>
      </div>

      <div class="quick-test">
        <h3>🧪 Quick test</h3>
        <p>Use the included sample file: <code>tests/samples/sample_procedure.txt</code></p>
        <p>This file contains an amide synthesis procedure to test the extraction.</p>
      </div>
    </div>

    <script>
      document.getElementById('extractForm').addEventListener('submit', function(e) {
        document.getElementById('loading').style.display = 'block';
        document.querySelector('button[type="submit"]').style.display = 'none';
      });
    </script>
  </body>
</html>
"""

RESULTS_HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>🧪 Extraction Results - Text→Reaction</title>
    <style>
      * { box-sizing: border-box; }
      body { 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
      }
      .container { max-width: 1200px; margin: 0 auto; }
      .header { 
        text-align: center; margin-bottom: 40px; 
        background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
      }
      h1 { color: #333; margin: 0; font-size: 2.5em; }
      .subtitle { color: #666; margin: 10px 0 0; }
      .actions { 
        display: flex; gap: 15px; justify-content: center; margin: 20px 0;
        flex-wrap: wrap;
      }
      .btn { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; padding: 12px 24px; border-radius: 10px;
        font-size: 14px; font-weight: 600; cursor: pointer; transition: transform 0.2s;
        text-decoration: none; display: inline-block;
      }
      .btn:hover { transform: translateY(-2px); }
      .btn-secondary { background: #6c757d; }
      .card { 
        background: white; border-radius: 20px; padding: 30px; margin: 20px 0; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
      }
      .reaction-card {
        border: 2px solid #e9ecef; border-radius: 15px; padding: 25px; margin: 20px 0;
        background: #f8f9fa;
      }
      .reaction-title { 
        font-size: 1.3em; font-weight: bold; color: #495057; margin-bottom: 20px;
        border-bottom: 2px solid #667eea; padding-bottom: 10px;
      }
      .section { margin: 20px 0; }
      .section-title { 
        font-weight: bold; color: #495057; margin-bottom: 10px; 
        display: flex; align-items: center; gap: 8px;
      }
      .chemical-list { 
        display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
        gap: 15px; margin: 15px 0;
      }
      .chemical-item { 
        background: white; padding: 15px; border-radius: 10px; border-left: 4px solid #667eea;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
      }
      .chemical-name { font-weight: bold; color: #333; }
      .chemical-role { 
        background: #667eea; color: white; padding: 4px 8px; border-radius: 15px; 
        font-size: 0.8em; margin: 5px 0;
        display: inline-block;
      }
      .chemical-amount { color: #666; font-size: 0.9em; }
      .conditions-grid { 
        display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
        gap: 15px; margin: 15px 0;
      }
      .condition-item { 
        background: white; padding: 15px; border-radius: 10px; 
        border: 1px solid #e9ecef;
      }
      .condition-label { font-weight: bold; color: #495057; }
      .condition-value { color: #666; }
      .workup-steps { 
        background: white; padding: 15px; border-radius: 10px; 
        border-left: 4px solid #28a745;
      }
      .workup-step { 
        margin: 8px 0; padding-left: 20px; position: relative;
      }
      .workup-step::before { 
        content: "✓"; position: absolute; left: 0; color: #28a745; font-weight: bold;
      }
      .outcome { 
        background: white; padding: 15px; border-radius: 10px; 
        border-left: 4px solid #ffc107;
      }
      .yield { 
        background: #fff3cd; color: #856404; padding: 10px; border-radius: 8px;
        font-weight: bold; display: inline-block; margin: 10px 0;
      }
      .notes { 
        background: #e7f3ff; padding: 15px; border-radius: 10px; 
        border-left: 4px solid #007bff;
      }
      .note { margin: 5px 0; color: #004085; }
      .summary { 
        background: #d4edda; color: #155724; padding: 20px; border-radius: 10px; 
        margin: 20px 0; border-left: 4px solid #28a745;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>🧪 Extraction Results</h1>
        <p class="subtitle">Chemical data extracted successfully</p>
        <div class="actions">
          <a href="/" class="btn btn-secondary">🔄 New extraction</a>
          <a href="/download-json" class="btn">📥 Download JSON</a>
        </div>
      </div>

      <div class="summary">
        <h3>📊 Summary</h3>
        <p><strong>Document:</strong> {{ data.document }}</p>
        <p><strong>Sections analyzed:</strong> {{ data.n_sections }}</p>
        <p><strong>Reactions extracted:</strong> {{ data.results | map(attribute='reactions') | map('length') | sum }}</p>
      </div>

      {% for result in data.results %}
        {% for reaction in result.reactions %}
          <div class="reaction-card">
            <div class="reaction-title">
              {% if reaction.title %}
                {{ reaction.title }}
              {% else %}
                Reaction {{ loop.index }}
              {% endif %}
            </div>

            <div class="section">
              <div class="section-title">🧪 Reactants and reagents</div>
              <div class="chemical-list">
                {% for input in reaction.inputs %}
                  <div class="chemical-item">
                    <div class="chemical-name">{{ input.name }}</div>
                    <div class="chemical-role">{{ input.role }}</div>
                    {% if input.amount %}
                      <div class="chemical-amount">{{ input.amount.value }} {{ input.amount.unit }}</div>
                    {% endif %}
                    {% if input.equivalents %}
                      <div class="chemical-amount">{{ input.equivalents }} equiv</div>
                    {% endif %}
                  </div>
                {% endfor %}
              </div>
            </div>

            <div class="section">
              <div class="section-title">🌡️ Reaction conditions</div>
              <div class="conditions-grid">
                {% if reaction.conditions.temperature %}
                  <div class="condition-item">
                    <div class="condition-label">Temperature</div>
                    <div class="condition-value">{{ reaction.conditions.temperature.value }} {{ reaction.conditions.temperature.unit }}</div>
                  </div>
                {% endif %}
                {% if reaction.conditions.time %}
                  <div class="condition-item">
                    <div class="condition-label">Time</div>
                    <div class="condition-value">{{ reaction.conditions.time.value }} {{ reaction.conditions.time.unit }}</div>
                  </div>
                {% endif %}
                {% if reaction.conditions.atmosphere %}
                  <div class="condition-item">
                    <div class="condition-label">Atmosphere</div>
                    <div class="condition-value">{{ reaction.conditions.atmosphere }}</div>
                  </div>
                {% endif %}
                {% if reaction.conditions.solvents %}
                  <div class="condition-item">
                    <div class="condition-label">Solvents</div>
                    <div class="condition-value">{{ reaction.conditions.solvents | join(', ') }}</div>
                  </div>
                {% endif %}
              </div>
            </div>

            {% if reaction.workup.steps %}
              <div class="section">
                <div class="section-title">⚗️ Workup</div>
                <div class="workup-steps">
                  {% for step in reaction.workup.steps %}
                    <div class="workup-step">{{ step }}</div>
                  {% endfor %}
                </div>
              </div>
            {% endif %}

            {% if reaction.outcome %}
              <div class="section">
                <div class="section-title">📈 Results</div>
                <div class="outcome">
                  {% if reaction.outcome.yield_ %}
                    <div class="yield">Yield: {{ reaction.outcome.yield_.value }} {{ reaction.outcome.yield_.unit }}</div>
                  {% endif %}
                  {% if reaction.outcome.product_name %}
                    <p><strong>Product:</strong> {{ reaction.outcome.product_name }}</p>
                  {% endif %}
                </div>
              </div>
            {% endif %}

            {% if reaction.notes %}
              <div class="section">
                <div class="section-title">📝 Notes</div>
                <div class="notes">
                  {% for note in reaction.notes %}
                    <div class="note">{{ note }}</div>
                  {% endfor %}
                </div>
              </div>
            {% endif %}
          </div>
        {% endfor %}
      {% endfor %}
    </div>
  </body>
</html>
"""

@app.get("/")
def home():
    return render_template_string(HOME_HTML)

@app.post("/extract")
def extract():
    url = request.form.get("url")
    max_sections = int(request.form.get("max_sections", 2))

    if url:
        text, kind = read_from_url(url)
        title = url
        source_url = url
    elif "file" in request.files:
        f = request.files["file"]
        text, kind = read_local_upload(f)
        title = f.filename or "upload"
        source_url = None
    else:
        return jsonify({"error": "Provide a URL or upload a file"}), 400

    sections = find_sections(text, max_sections=max_sections)
    if not sections:
        return jsonify({"message": "No Experimental-like sections found."})

    extractor = LLMExtractor()
    outputs = []
    for (sec_title, sec_text) in sections:
        rs = extractor.extract(doc_title=title, section_title=sec_title, section_text=sec_text, source_url=source_url)
        outputs.append(rs.model_dump())

    result_data = {
        "document": title,
        "n_sections": len(sections),
        "results": outputs,
    }
    
    # Store result in session for display
    session['extraction_result'] = json.dumps(result_data)
    
    # Redirect to visual display instead of returning JSON
    return redirect(url_for('display_results'))

@app.get("/results")
def display_results():
    if 'extraction_result' not in session:
        return redirect(url_for('home'))
    
    result_data = json.loads(session['extraction_result'])
    return render_template_string(RESULTS_HTML, data=result_data)

@app.get("/download-json")
def download_json():
    if 'extraction_result' not in session:
        return redirect(url_for('home'))
    
    result_data = json.loads(session['extraction_result'])
    
    # Create a temporary file
    import tempfile
    import io
    
    json_str = json.dumps(result_data, indent=2, ensure_ascii=False)
    output = io.BytesIO()
    output.write(json_str.encode('utf-8'))
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/json',
        as_attachment=True,
        download_name=f"extraction_results_{result_data['document'].replace('.', '_')}.json"
    )

if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", 5000)))
