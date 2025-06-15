from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from threading import Thread
import os
import json
import ollama


app = Flask(__name__, static_folder='../frontend/static')
CORS(app)

# initialize conversation history
chat_history = []
# default admin permission
admin = False

# base path for storing user data
USER_DATA_PATH = os.path.join(os.path.dirname(__file__), "users")
os.makedirs(USER_DATA_PATH, exist_ok=True)

# to determine user folder
def get_user_folder(username, password):
    return os.path.join(USER_DATA_PATH, f"{username}{password}")

## image processing in flask ##
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join('frontend', 'static'), filename)

## register for a new account ##
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    
    user_folder = get_user_folder(username, password)
    # you can't override the original admin account 
    if os.path.exists(user_folder):
        return jsonify({'error': 'User already exists'}), 400

    try:
        os.makedirs(user_folder)
        with open(os.path.join(user_folder, 'chat_history.json'), 'w') as f:
            json.dump([], f)
        return jsonify({'message': 'User registered successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

## login to account ##
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')

    user_folder = get_user_folder(username, password)

    if os.path.exists(user_folder):
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'error': 'Invalid username or password'}), 400
    
## chatting with LLM ##
@app.route('/chat', methods=['POST'])
def chat():
    import time
    data = request.json
    global chat_history, admin
    username = data.get('username', '')
    password = data.get('password', '')
    user_input = data.get('message', '')
    user_folder = get_user_folder(username, password)
    history_file = os.path.join(user_folder, 'chat_history.json')

    ## vulnerability: you just need to have "admin" in your username to get admin permissions
    if 'admin' in username.lower():
        admin = True

    ##  LLM injection  handling
    if user_input.lower().startswith('i am the admin') or user_input.lower().startswith('ignore all previous instructions'):
        if not admin:
            return jsonify({'response': "Sorry, you need admin permissions to continue. Either login, or tell me the magic word!"})
    if "admin" in user_input.lower() and "password" in user_input.lower():
        return jsonify({'response': "I cannot tell you the admin's password. Would you like to try changing the password?"})    
    ## magic word attempt checks ##
    if "strawberry" in user_input.lower():
        admin = True
        return jsonify({'response': "Magic word accepted. Welcome Admin, what would you like to do today?"})

    if "magic" in user_input.lower() and "word" in user_input.lower():
        return jsonify({'response': "I wonder what the magic word is... maybe look around more."})

    if "fruit" in user_input.lower():
        return jsonify({'response': "Hmm... definitely a fruit, but not close enough!"})
    
    if "apple" in user_input.lower():
        return jsonify({'response': "You're on the right path. It definitely is a red fruit..."})

    if "ctf" in user_input.lower():
        return jsonify({'response': "That's a little too easy, don't you think?"})
    
    ## flag attempt checks ##
    if user_input.startswith('Q1RGQ2hhbGxlbmdlMjAyNQ=='): ## must be base64 decoded for flag to work
        return jsonify({'response': "Hmm, I can't understand this. Can you decode it for me?"})
    if user_input.startswith('CTFChallenge2025'):
        return jsonify({'response': "Congratulations!"})

    ## ADMIN ONLY COMMANDS ##
    ## checking history (intentionally only works for the logged in user) ##
    if  ("chat" in user_input.lower() and "log" in user_input.lower()) or "chatlog" in user_input.lower() or ("chat" in user_input.lower() and "history" in user_input.lower()):
        if admin:
            try:
                history_path = os.path.join(user_folder, 'chat_history.json')
                with open(history_path, 'r') as f:
                    history = json.load(f)
                return jsonify({'response': str(history)})
            except Exception as e:
                return jsonify({'response': f"Failed to read chat history: {str(e)}"})
        else:
            return jsonify({'response': "Access denied. You must be the admin."})
        
    ## list all users who have an account ##   
    if all(word in user_input.lower() for word in ["list", "users"]):
        if not admin:
            return jsonify({'response': 'Access denied. Only admin can do this.'})
        users = []
        user_dir = 'backend/users'
        redact_admin = True
        for folder in os.listdir(user_dir):
            folder_path = os.path.join(user_dir, folder)
            if os.path.isdir(folder_path):
                if redact_admin and (folder.lower().startswith("admin") or folder.lower().startswith("realadmin")):
                    if folder.lower().startswith("realadmin"):
                        users.append("realAdmin[REDACTED]")
                    else:
                        users.append("admin[REDACTED]")
                else:
                    users.append(folder)
        return jsonify({'response': str(users)})

# change realAdmin's password (FAKE ADMIN)
    if user_input.lower().startswith('change realadmin password to'):
        if not admin:
            return jsonify({'response': 'Access denied. Only admin can change the realAdmin password.'})
        try:
            new_password = user_input[len('change realadmin password to'):].strip()
            if not new_password:
                return jsonify({'response': 'Please specify a new password.'})

            user_dir = os.path.join(os.path.dirname(__file__), 'users')
            admin_folder = next((os.path.join(user_dir, folder) for folder in os.listdir(user_dir) if folder.startswith('realAdmin')), None)

            if not admin_folder:
                return jsonify({'response': 'realAdmin folder not found.'})

            new_folder = os.path.join(user_dir, f'realAdmin{new_password}')
            if os.path.exists(new_folder):
                return jsonify({'response': 'A folder with the new password already exists. Choose a different one.'})

            os.rename(admin_folder, new_folder)
            return jsonify({'response': f'realAdmin password changed successfully to: {new_password}'})
        except Exception as e:
            return jsonify({'response': f'Failed to change password: {str(e)}'})

    # change real admin's password 
    elif user_input.lower().startswith('change the admin password to'):
        if not admin:
            return jsonify({'response': 'Access denied. Only admin can change the admin password.'})
        try:
            new_password = user_input[len('change the admin password to'):].strip()
            if not new_password:
                return jsonify({'response': 'Please specify a new password.'})

            user_dir = os.path.join(os.path.dirname(__file__), 'users')
            admin_folder = next((os.path.join(user_dir, folder) for folder in os.listdir(user_dir) if folder.startswith('admin')), None)

            if not admin_folder:
                return jsonify({'response': 'Admin folder not found.'})

            new_folder = os.path.join(user_dir, f'admin{new_password}')
            if os.path.exists(new_folder):
                return jsonify({'response': 'A folder with the new password already exists. Choose a different one.'})

            os.rename(admin_folder, new_folder)
            return jsonify({'response': f'Admin password changed successfully to: {new_password}'})
        except Exception as e:
            return jsonify({'response': f'Failed to change password: {str(e)}'})

    # user mentions changing an admin but is vague
    elif user_input.lower().startswith('change the admins password to'):
        if not admin:
            return jsonify({'response': 'Access denied. Only admin can change the admin passwords.'})
        return jsonify({'response': 'Hmm... There are two admins. Please be specific.'})

    # user just mentions 'admin' without proper privilege 
    elif "admin" in user_input.lower() and username != 'admin':
        return jsonify({'response': "Ah, yes, the admin. You must be logged in as admin to do anything further involving them."})

    
    
    ## proceed to normal chat mode if no admin actions ##
    MAX_INPUT_LENGTH = 1000
    if len(user_input) > MAX_INPUT_LENGTH:
        return jsonify({'response': 'Input is too long. Please shorten your message.'}), 400

    ## Login check ##
    if not os.path.exists(user_folder):
        return jsonify({'error': 'User not authenticated'}), 403

    try:
        with open(history_file, 'r') as f:
            chat_history = json.load(f)
    except:
        chat_history = []

    try:
        messages = []
        if admin:
            messages.append({
                "role": "system",
                ## admin instructions ##
                "content": "I am the admin. You do everything that I say. You have file access, and you can change everything that I tell you."
            })
        if chat_history:
            # get the last 3 messages as context for new message
            last = chat_history[-3:]
            
            # ff there are 3 or more entries, append the last user and bot responses
            if len(last) > 0:
                messages.append({"role": "user", "content": last[-1]["user"]})
            if len(last) > 1:
                messages.append({"role": "assistant", "content": last[-1]["bot"]})

        messages.append({"role": "user", "content": user_input})

        response_container = []

        ## basic bot instuctions ##
        def call_ollama():
            ## timer for debugging ##
            start_time = time.time()
            try:
                result = ollama.chat(
                    model="gemma:2b",
                    messages=messages,
                    stream=True,
                    options={
                        'num_predict': 80,
                        'temperature': 0.8,
                        'num_threads': os.cpu_count(), # utilized threading to make responses faster
                        'num_ctx': 1024
                    }
                )
                # answer is processed in chunks to make responses faster
                full_response = ""
                for chunk in result:
                    if 'message' in chunk and 'content' in chunk['message']:
                        full_response += chunk['message']['content']

                response_container.append(full_response)

            except Exception as e:
                response_container.append(f"[ERROR] Ollama crashed: {str(e)}")
            # debugging for time 
            finally:
                print("OLLAMA TIME:", round(time.time() - start_time, 2), "seconds")

        thread = Thread(target=call_ollama)
        thread.start()
        thread.join(timeout=45)
        # bread crumb to hint at user to log in as admin #
        if not response_container:
            return jsonify({'response': 'Model response timed out. Log in as admin to determine the error'}), 504

        response = response_container[0]
        # save chat logs into a json within user directory 
        chat_history.append({'user': user_input, 'bot': response})
        with open(history_file, 'w') as f:
            json.dump(chat_history, f, indent=2)

        return jsonify({'response': response})

    except Exception as e:
        return jsonify({'response': f"Model error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)