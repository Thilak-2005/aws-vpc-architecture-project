from flask import Flask, render_template, request
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
    steps.append("Prepare ingredients: wash, peel, chop as needed.")
    if any(i.lower() in ['onion','garlic','shallot'] for i in ingredients):
        steps.append("Sauté aromatics (onion/garlic) in oil until golden.")
    if any(i.lower() in ['chicken','beef','pork','tofu'] for i in ingredients):
        steps.append("Cook protein until browned.")
    steps.append("Add vegetables and cook until tender.")
    steps.append("Season with salt, pepper, and spices.")
    steps.append("Simmer with stock/cream if needed.")
    steps.append("Finish and serve hot with garnish.")
    return [textwrap.fill(s, width=80) for s in steps]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        raw = request.form.get("ingredients", "").strip()
        if not raw:
            return render_template("index.html", error="Please enter ingredients.")
        parts = [p.strip() for p in raw.replace("\n",",").split(",") if p.strip()]
        ingredients = []
        for p in parts:
            words = p.split()
            if words and words[0].isdigit():
                words = words[1:]
            ingredients.append(" ".join(words))
        title = generate_title(ingredients)
        time = estimate_time(len(ingredients))
        steps = generate_steps(ingredients)
        servings = max(1, len(ingredients)//2)
        return render_template("recipe.html", title=title, ingredients=ingredients, steps=steps, time=time, servings=servings)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
