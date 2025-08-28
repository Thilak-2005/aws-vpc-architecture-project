# save as create_recipe_project.py
import os, zipfile, shutil, textwrap

project_name = "recipe_generator"

# Remove existing project folder if present
if os.path.exists(project_name):
    shutil.rmtree(project_name)

os.makedirs(os.path.join(project_name, "templates"))
os.makedirs(os.path.join(project_name, "static"))

app_py = r'''from flask import Flask, render_template, request, redirect, url_for
import random, textwrap

app = Flask(__name__)

def generate_title(ingredients):
    main = ingredients[0].title()
    styles = ["Savory", "Crispy", "Hearty", "Zesty", "Creamy", "Spiced", "Quick & Easy", "One-Pan", "Comfort"]
    dishes = ["Stir-Fry", "Pasta", "Casserole", "Skillet", "Salad", "Soup", "Bake", "Curry", "Wrap"]
    return f"{random.choice(styles)} {main} {random.choice(dishes)}"

def estimate_time(n_ingredients):
    t = 10 + 5 * n_ingredients
    if t > 60:
        t = 60 + (n_ingredients - 10) * 2
    return f"{t} minutes"

def generate_steps(ingredients):
    steps = []
    steps.append("Prepare the ingredients: wash, peel and chop as needed. Gather tools (pan, knife, cutting board).")
    if any(i.lower() in ['onion','garlic','shallot'] for i in ingredients):
        steps.append("Sauté aromatics: heat oil in a pan, add chopped onion and garlic and cook until translucent.")
    if any(i.lower() in ['chicken','beef','pork','tofu'] for i in ingredients):
        steps.append("Cook the protein: increase heat and add protein pieces. Brown on all sides.")
    vegs = [i for i in ingredients if i.lower() not in ['chicken','beef','pork','tofu','salt','pepper','oil','butter']]
    if vegs:
        steps.append("Add vegetables and other ingredients to the pan and cook until tender-crisp.")
    steps.append("Season: add salt, pepper and spices to taste. Stir to combine.")
    steps.append("Simmer: add a splash of liquid (stock, water, or cream) if needed and simmer to combine flavors.")
    steps.append("Finish and serve: garnish with fresh herbs, a squeeze of lemon, or grated cheese as desired.")
    numbered = [textwrap.fill(s, width=80) for s in steps]
    return numbered

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        raw = request.form.get('ingredients','').strip()
        if not raw:
            return render_template('index.html', error="Please enter one or more ingredients (comma separated).")
        parts = [p.strip() for p in raw.replace('\\n',',').split(',') if p.strip()]
        ingredients = []
        for p in parts:
            words = p.split()
            if words and words[0].isdigit():
                words = words[1:]
            ingredients.append(' '.join(words))
        title = generate_title(ingredients)
        time = estimate_time(len(ingredients))
        steps = generate_steps(ingredients)
        servings = max(1, len(ingredients)//2)
        return render_template('recipe.html',
                               title=title,
                               ingredients=ingredients,
                               steps=steps,
                               time=time,
                               servings=servings)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
'''

index_html = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Smart Recipe Generator</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <main class="container">
    <header class="hero">
      <h1>Smart Recipe Generator</h1>
      <p>Enter ingredients you have, and get a clean, ready-to-cook recipe.</p>
    </header>

    <section class="card">
      <form method="POST" action="/">
        <label for="ingredients">Ingredients (comma separated):</label>
        <textarea id="ingredients" name="ingredients" rows="5" placeholder="e.g. chicken, onion, garlic, tomato, basil"></textarea>
        <div class="row">
          <button class="btn-primary" type="submit">Generate Recipe</button>
          <button class="btn-secondary" type="button" id="sample">Use sample ingredients</button>
        </div>
        {% if error %}
          <p class="error">{{ error }}</p>
        {% endif %}
      </form>
    </section>

    <footer class="foot">Made with ♥ — Simple generator (no external APIs)</footer>
  </main>
  <script>
    document.getElementById('sample').addEventListener('click', function(){
      document.getElementById('ingredients').value = "chicken, onion, garlic, tomato, basil, olive oil";
    });
  </script>
</body>
</html>
'''

recipe_html = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{{ title }}</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <main class="container recipe-page">
    <a class="back" href="/">← Back</a>
    <header class="recipe-header card">
      <h1 class="title">{{ title }}</h1>
      <div class="meta">
        <span>⏱️ {{ time }}</span>
        <span>🍽️ Serves: {{ servings }}</span>
      </div>
    </header>

    <section class="card split">
      <div class="left">
        <h2>Ingredients</h2>
        <ul>
          {% for ing in ingredients %}
            <li>{{ ing }}</li>
          {% endfor %}
        </ul>
      </div>
      <div class="right">
        <h2>Directions</h2>
        <ol>
          {% for step in steps %}
            <li style="margin-bottom:10px;">{{ step }}</li>
          {% endfor %}
        </ol>
      </div>
    </section>

    <section class="card tips">
      <h3>Quick Tips</h3>
      <ul>
        <li>Adjust seasoning to taste.</li>
        <li>Swap ingredients freely — the method is flexible.</li>
        <li>For a richer taste, finish with butter or lemon.</li>
      </ul>
    </section>

    <footer class="foot">Generated locally — no external services used.</footer>
  </main>
</body>
</html>
'''

style_css = r'''
:root{
  --bg:#f6f8fa;
  --card:#ffffff;
  --accent:#ff6b6b;
  --muted:#6b7280;
  --shadow: 0 6px 18px rgba(20,20,30,0.08);
  --radius:12px;
}
*{box-sizing:border-box;font-family:Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;}
body{margin:0;background:var(--bg);color:#111;}
.container{max-width:880px;margin:32px auto;padding:16px;}
.hero{text-align:center;margin-bottom:18px;}
.hero h1{margin:0;font-size:28px;}
.hero p{color:var(--muted);margin-top:6px;}
.card{background:var(--card);padding:18px;border-radius:var(--radius);box-shadow:var(--shadow);margin-bottom:16px;}
label{display:block;margin-bottom:8px;font-weight:600;}
textarea{width:100%;padding:10px;border-radius:8px;border:1px solid #e6e9ee;resize:vertical;}
.row{display:flex;gap:12px;margin-top:12px;}
.btn-primary{background:var(--accent);border:none;color:white;padding:10px 14px;border-radius:10px;cursor:pointer;font-weight:700;}
.btn-secondary{background:transparent;border:1px solid #ddd;color:#333;padding:10px 14px;border-radius:10px;cursor:pointer;}
.error{color:#b00020;margin-top:10px;}
.recipe-page .back{display:inline-block;margin-bottom:12px;color:#333;text-decoration:none;}
.recipe-header .title{margin:0;font-size:24px;}
.recipe-header .meta{color:var(--muted);margin-top:8px;display:flex;gap:12px;}
.split{display:grid;grid-template-columns:1fr 1fr;gap:18px;align-items:start;}
.split ul{margin:0;padding-left:18px;}
.tips ul{margin:0;padding-left:18px;color:var(--muted);}
.foot{text-align:center;color:var(--muted);font-size:13px;margin-top:6px;}
@media(max-width:720px){
  .split{grid-template-columns:1fr;}
}
'''

requirements_txt = "flask\n"

readme = "# Smart Recipe Generator\n\nEnter ingredients (comma separated) and get a generated recipe. Run with `python app.py`.\n"

files = {
    "app.py": app_py,
    "templates/index.html": index_html,
    "templates/recipe.html": recipe_html,
    "static/style.css": style_css,
    "requirements.txt": requirements_txt,
    "README.md": readme
}

# write files
for path, content in files.items():
    full = os.path.join(project_name, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

# create zip file
zip_filename = f"{project_name}.zip"
with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, fnames in os.walk(project_name):
        for fname in fnames:
            fullpath = os.path.join(root, fname)
            arcname = os.path.relpath(fullpath, project_name)
            zf.write(fullpath, arcname)

print(f"Project created in folder: ./{project_name}/")
print(f"ZIP file created: ./{zip_filename}")
a