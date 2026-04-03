import os
from flask import Flask, render_template_string, request
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to generate recipe
def generate_tutorial(components):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {
                "role": "user",
                "content": f"""
Suggest a recipe using the items listed as available.

Requirements:
- Add a creative recipe name
- Add a funny version of the name
- Provide step-by-step instructions
- End with a fun fact

Available ingredients:
{components}, Haldi, Chilly Powder, Tomato Ketchup, Water, Garam Masala, Oil
"""
            }
        ],
        temperature=0.7
    )

    return response.choices[0].message.content


# Initialize Flask app
app = Flask(__name__)


# Home route
@app.route('/', methods=['GET', 'POST'])
def home():
    output = ""
    if request.method == 'POST':
        components = request.form['components']
        output = generate_tutorial(components)

    return render_template_string(HTML_TEMPLATE, output=output)


# API route for AJAX
@app.route('/generate', methods=['POST'])
def generate():
    components = request.form['components']
    return generate_tutorial(components)


# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Recipe Generator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">

    <script>
    async function generateTutorial() {
        const output = document.querySelector('#output');
        output.textContent = 'Cooking a recipe for you... 🍳';

        const response = await fetch('/generate', {
            method: 'POST',
            body: new FormData(document.querySelector('#tutorial-form'))
        });

        const result = await response.text();
        output.textContent = result;
    }

    function copyToClipboard() {
        const output = document.querySelector('#output');
        const textarea = document.createElement('textarea');
        textarea.value = output.textContent;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        alert('Copied to clipboard!');
    }
    </script>
</head>

<body>
<div class="container">
    <h1 class="my-4 text-center">🍲 Custom Recipe Generator</h1>

    <form id="tutorial-form" onsubmit="event.preventDefault(); generateTutorial();" class="mb-3">
        <div class="mb-3">
            <label for="components" class="form-label">Ingredients / Items:</label>
            <input type="text" class="form-control" id="components" name="components"
                   placeholder="e.g. Bread, Egg, Potato" required>
        </div>
        <button type="submit" class="btn btn-primary">Generate Recipe</button>
    </form>

    <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
            Output:
            <button class="btn btn-secondary btn-sm" onclick="copyToClipboard()">Copy</button>
        </div>
        <div class="card-body">
            <pre id="output" style="white-space: pre-wrap;">{{ output }}</pre>
        </div>
    </div>
</div>
</body>
</html>
'''


# Run the app
if __name__ == '__main__':
    app.run(debug=True)