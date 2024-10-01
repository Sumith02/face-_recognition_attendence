from flask import Flask, render_template, request, redirect, url_for
import os
from PIL import Image
import cv2

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

def read_threshold_value(file_path='value.ini'):
    with open(file_path) as f:
        return int(f.read().strip())

def convert_to_black_and_white(input_image_path, threshold_value, output_image_path):
    image = cv2.imread(input_image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, black_and_white_image = cv2.threshold(gray_image, threshold_value, 255, cv2.THRESH_BINARY)
    bw_image_pil = Image.fromarray(black_and_white_image)
    bw_image = bw_image_pil.convert('1')
    bw_image.save(output_image_path)
    return output_image_path

def compress_image(input_image_path, quality, output_image_path):
    image = Image.open(input_image_path)
    image.save(output_image_path, "JPEG", quality=quality)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return redirect(url_for('process_file', filename=file.filename))
    return redirect(request.url)

@app.route('/process/<filename>', methods=['GET', 'POST'])
def process_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if request.method == 'POST':
        process_choice = request.form['process']
        processed_image_name = 'processed_' + filename
        processed_image_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_image_name)

        if process_choice == '1':
            quality = int(request.form['quality'])
            compress_image(file_path, quality, processed_image_path)
        elif process_choice == '2':
            threshold_value = read_threshold_value()
            convert_to_black_and_white(file_path, threshold_value, processed_image_path)
        elif process_choice == '3':
            threshold_value = read_threshold_value()
            temp_path = 'temp_' + filename
            temp_image_path = os.path.join(app.config['PROCESSED_FOLDER'], temp_path)
            convert_to_black_and_white(file_path, threshold_value, temp_image_path)
            quality = int(request.form['quality'])
            compress_image(temp_image_path, quality, processed_image_path)
            os.remove(temp_image_path)

        original_size = os.path.getsize(file_path)
        processed_size = os.path.getsize(processed_image_path)
        
        return render_template('process.html', filename=filename, processed_image_name=processed_image_name, original_size=original_size, processed_size=processed_size)
    return render_template('process.html', filename=filename)

if __name__ == '__main__':
    app.run(debug=True)
