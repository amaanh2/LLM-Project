from flask import Flask, render_template, request
from transformers import pipeline

app = Flask(__name__)

generator = pipeline('text-generation', model="gpt2")

conversation_history = []

@app.route('/')
def index():
    return render_template('index.html', prompt='', result='', history=conversation_history)

@app.route('/generate', methods=['POST'])
def generate():
    user_input = request.form.get('prompt', '')
    response = generator(user_input, max_length=100, num_return_sequences=1)
    generated_text = response[0]['generated_text']

    conversation_history.append((user_input, generated_text))

    return render_template('index.html', prompt=user_input, result=generated_text, history=conversation_history)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")