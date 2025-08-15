from flask import Flask, render_template, request
import pytesseract
import cv2
import os
import re
import operator
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ----------- Math Question Processor -----------
def process_math_question(question):
    try:
        text = question.lower().replace(",", "").replace("  ", " ")
        
        # Replace BM scale words with actual numbers
        text = text.replace(" juta", "000000")
        text = text.replace(" ribu", "000")
        
        # Fix numbers stuck to words: "375bekas" → "375"
        text = re.sub(r'(\d+)([a-zA-Z])', r'\1', text)
        
        # Map keywords to operations (EN + BM)
        keywords = {
            "add": operator.add, "plus": operator.add, "more": operator.add, "increase": operator.add, "sum": operator.add, "total": operator.add, "tambah": operator.add,
            "subtract": operator.sub, "minus": operator.sub, "less": operator.sub, "decrease": operator.sub, "kurang": operator.sub, "beza": operator.sub, "difference": operator.sub,
            "multiply": operator.mul, "times": operator.mul, "product": operator.mul, "kali": operator.mul,
            "divide": operator.truediv, "divided": operator.truediv, "bahagi": operator.truediv, "per": operator.truediv,
            "setiap": operator.truediv, "seorang": operator.truediv, "sebuah": operator.truediv
        }
        
        # Extract numbers
        numbers = list(map(float, re.findall(r'\d+(?:\.\d+)?', text)))
        if not numbers:
            return "I couldn't find any numbers in the question."

        # If it's already a math expression, try directly
        math_expr = re.sub(r'[^0-9\+\-\*/\(\)\.\s]', '', text)
        if re.search(r'[\+\-\*/]', math_expr):
            try:
                return f"Answer: {eval(math_expr)}"
            except:
                pass  # Fall back to keyword parsing

        # Detect operations in order they appear
        ops_sequence = []
        for word in text.split():
            if word in keywords:
                ops_sequence.append(keywords[word])

        # If no explicit operation but pattern matches division context
        if not ops_sequence and ("setiap" in text or "seorang" in text):
            ops_sequence.append(operator.truediv)

        if not ops_sequence:
            return "I couldn't detect the math operation."

        # Apply operations step-by-step
        result = numbers[0]
        for op, num in zip(ops_sequence, numbers[1:]):
            result = op(result, num)

        # Output clean integer if no decimal part
        if isinstance(result, float) and result.is_integer():
            result = int(result)

        return f"Answer: {result}"

    except Exception as e:
        return f"Could not understand the question. ({e})"


# ----------- Routes -----------
@app.route('/', methods=['GET', 'POST'])
def index():
    answer = ""
    question_text = ""

    if request.method == 'POST':
        # If user uploaded an image
        if 'image' in request.files and request.files['image'].filename != '':
            image_file = request.files['image']
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
            image_file.save(image_path)

            # Read image using OpenCV
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Optional: improve OCR accuracy
            gray = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

            # Extract text using pytesseract
            question_text = pytesseract.image_to_string(gray)

        # If user typed a question
        elif 'text' in request.form and request.form['text'].strip() != "":
            question_text = request.form['text']

        # Process question
        answer = process_math_question(question_text)

    return render_template('index.html', answer=answer, question=question_text)


# ----------- Main -----------
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
