from flask import Flask, render_template, request
import pytesseract
from PIL import Image
import os
import re

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def extract_text(image_path):
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)

def evaluate_math_expression(text):
    try:
        expression = re.findall(r'[\d\+\-\*/\.\(\)\s]+', text)
        expression = ''.join(expression).strip()
        return eval(expression)
    except:
        return "Unable to evaluate expression."

def summarize_math_language(text):
    text = text.lower()
    if "more" in text or "add" in text:
        numbers = [int(s) for s in text.split() if s.isdigit()]
        return f"Answer: {sum(numbers)}"
    elif "left" in text or "remain" in text:
        numbers = [int(s) for s in text.split() if s.isdigit()]
        if len(numbers) >= 2:
            return f"Answer: {numbers[0] - numbers[1]}"
    return "Sorry, I couldn't understand the question."

@app.route("/", methods=["GET", "POST"])
def index():
    result1 = result2 = ""
    if request.method == "POST":
        if 'image1' in request.files:
            image1 = request.files['image1']
            if image1.filename != "":
                path1 = os.path.join(app.config['UPLOAD_FOLDER'], image1.filename)
                image1.save(path1)
                text1 = extract_text(path1)
                result1 = evaluate_math_expression(text1)

        if 'image2' in request.files:
            image2 = request.files['image2']
            if image2.filename != "":
                path2 = os.path.join(app.config['UPLOAD_FOLDER'], image2.filename)
                image2.save(path2)
                text2 = extract_text(path2)
                result2 = summarize_math_language(text2)

        if 'text2' in request.form:
            typed_text = request.form['text2']
            if typed_text.strip() != "":
                result2 = summarize_math_language(typed_text)

    return render_template("index.html", result1=result1, result2=result2)

if __name__ == "__main__":
    app.run(debug=True)
