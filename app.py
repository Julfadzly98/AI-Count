from flask import Flask, render_template, request
from PIL import Image
import pytesseract
import os
from sympy import *
import re

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ✅ SET YOUR TESSERACT PATH HERE
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.route("/", methods=["GET", "POST"])
def index():
    solution = ""
    if request.method == "POST":
        file = request.files["image"]
        if file:
            path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(path)

            # ✅ OCR to extract text
            img = Image.open(path).convert('L')  # Grayscale for better OCR
            question = pytesseract.image_to_string(img)

            # ✅ Normalize common math symbols
            question = question.replace("÷", "/").replace("×", "*")
            question = question.replace("—", "-").replace("–", "-")
            question = question.replace("=", "").replace("?", "").strip()

            print("OCR RAW:", question)  # Debugging output

            try:
                # ✅ Extract math expression
                expr_match = re.findall(r"[0-9\+\-\*/\(\)\s\.\/]+", question)

                if expr_match:
                    expr_str = expr_match[0].strip()
                    expr = sympify(expr_str)
                    result = expr.evalf()
                    solution = f"AI Tools Math Extracted: {question}\nThe Answer: {expr}\nResult: {result}"
                else:
                    solution = f"OCR Extracted: {question}\nNo math expression found."
            except Exception as e:
                solution = f"OCR Extracted: {question}\nError solving expression: {str(e)}"

    return render_template("index.html", solution=solution)

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
