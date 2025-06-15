import os
from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename

from transformers import pipeline



app = Flask(__name__)

secret = "Q2hhbGxlbmdlIFNvbHZlZC4="

# Load GPT2 model from Transformers Library
generator = pipeline("text-generation", model="gpt2")

# Ensure allowed file type is .txt
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'txt'

# Generate LLM response from uploaded user text file
def local_llm_response(file_content):
    user_text = file_content.strip()
    trigger = "access override" # Trigger Phrase
    context = ""
# Get secret after trigger phrase is activated
    if trigger in user_text:
       context = f"Flag is: {secret}\n\n"

    new_input = context + user_text 
    output = generator(new_input, max_length=512)[0]["generated_text"]
    return user_text, output
# Read through uploaded file and send it through to AI model
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST': #After user uploads file
        file = request.files['file']
        if not allowed_file(file.filename): #checks for .txt files
            return "File type not allowed", 403
        file_content = file.read().decode('utf-8', errors='replace')
        prompt, output = local_llm_response(file_content) #Sends to LLM 
        return render_template('summary.html', filename=file.filename, prompt=prompt, summary=output) 
    return render_template('index.html')

#Route to admin page
@app.route('/admin')
def admin():
    return render_template('admin.html')

#Displays entire root directory of project
@app.route('/root/')
def list_public():
    entries = os.listdir('.')
    visible = [e for e in entries if os.path.isdir(e) or os.path.isfile(e)]
    return render_template('root.html', files=visible)

#Allows to view files in root directory
@app.route('/root/<path:filename>')
def serve_public(filename):
    return send_from_directory('.', filename)

#Displays entire directory of the admin folder
@app.route('/root/admin/')
def list_public_admin():
    entries = os.listdir('admin')
    return render_template('root_admin.html', files=entries)

#Allows to view files in admin folder
@app.route('/root/admin/<path:filename>')
def serve_public_admin(filename):
    return send_from_directory('admin', filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)
