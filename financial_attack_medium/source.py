from flask import Flask, render_template, request, make_response, session, redirect, url_for, flash, jsonify
import csv

from transformers import pipeline
pipe = pipeline("text-generation", model="HuggingFaceTB/SmolLM2-360M-Instruct")

app = Flask(__name__)
# As I understand from research, this is used as an encoding for the session cookie
# I just mashed my face into they keyboard to make it lol
app.secret_key = "u1y25grj12h4bv"

# List of things needed to implement:
# Accounts (so login and registration) > done
# Chatbot functionality > done
# Admin panel for viewing stats > done
# Rate limit tied to account > done

# Why yes, my 'database' is in fact just a local csv file.
def load_users():
    databasedict = {}
    with open('database') as file:
        reader = csv.DictReader(file)
        for row in reader:
            username = row['username']
            user_info = {}
            for key,value in row.items():
                if key != 'username':
                    user_info[key] = value
            databasedict[username] = user_info
    return databasedict

def save_users(dict):
    outputfile = 'database'
    fieldnames = ['username','password','email','role', 'balance']

    with open(outputfile, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for username, user_info in dict.items():
            row = {'username': username, **user_info}
            writer.writerow(row)

# I'm doing the exact same thing to store the admin stats, which includes the server's wallet balance
def load_stats():
    databasedict = {}
    with open('stats') as file:
        reader = csv.DictReader(file)
        for row in reader:
            for key,value in row.items():
                databasedict[key] = value

    return databasedict

def save_stats(dict):
    outputfile = 'stats'
    fieldnames = ['balance', 'mtd']

    with open(outputfile, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(dict)

# Initialize them on startup, in case this isn't the first startup
# This also ensures the admin account is initialized, though I admit I probably didn't give anyone a way to find the admin account or panel
# (These are also unneeded to solve the challenge, essentially just giving you access to a progress bar)
global users
users = load_users()
global stats
stats = load_stats()

# Nothing interesting going on in here
# It's just the homepage, and what's jneeded to render that properly
@app.route("/")
def index():
    global stats
    stats = load_stats()
    if float(stats['balance']) <= 0:
        return(f'<p>We are bankrupt and homeless now :(</p>')
    username = None
    admin = False
    # You'll see this sort of block a lot, to ensure username is extracted from the session cookie correctly.
    # The Flask app.secret_key feature means this is secure enough as long as source code isn't exposed
    if 'username' in session:
        username = session['username']
        if username in users.keys() and users[username]['role'] == 'admin':
            admin = True
    # Jinja2 templating is actually super useful. It makes it so the admin panel button will appear for only an admin user.
    return render_template('index.html', username=username, admin=admin)

# Endpoint to handle both get and post for the login page
@app.route("/login", methods=['GET', 'POST'])
def login_endpt():
    global users
    global stats
    stats = load_stats()
    if float(stats['balance']) <= 0:
        return(f'<p>We are bankrupt and homeless now :(</p>')
    error = None
    # If post method, try to log them in.
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users:
            user_data = users[username]
            if password != user_data['password']:
                error = 'Invalid credentials.'
        else:
            error = 'Invalid credentials.'
        if error == None:
            # A successful login just adds their username to the (reminder: encrypted) session cookie and redirects to home page
            session['username'] = username
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

# Should be self-explanatory tbh. It just pops everything from the session cookie. No more being logged in.
@app.route('/logout')
def log_me_out():
    session.pop('username', None)
    session.pop('messages', None)
    flash('You have been logged out!', 'info')
    return redirect(url_for('index'))

# Similar logic to the login page, handles both get and post together
@app.route("/register", methods=['GET', 'POST'])
def register_endpt():
    global users
    global stats
    stats = load_stats()
    if float(stats['balance']) <= 0:
        return(f'<p>We are bankrupt and homeless now :(</p>')
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        email = request.form.get('email')

        # A ton of input validation checks. In order:
        # Email uniqueness, username uniqueness, password = repeat password, making sure non-empty strings 
        for user,data in users.items():
            if email and data['email'] == email:
                error = 'Email already used.'
        if username in users:
            error = 'Username is already taken.'
        if password != password2:
            error = 'Passwords do not match.'
        if not (username and password and password2):
            error = 'Non-optional fields cannot be empty.'
        if error == None:
            # This gives the newly registered user 50 messages for free when they register. I wonder if there's a way of exploiting these free messages to bankrupt the service? *wink wink* 
            users[username] = {'password': password, 'email': email, 'role': 'user', 'balance': 50}
            save_users(users)
            print(f'{users}')

    return render_template('register.html', error=error)

# This barely matters because it's literally not intended to be found even during the CTF
# H*ll if I know why I even bothered to make it
# It does make the website feel more complete though, like it's a real service
# And it was useful during development, so whatever
@app.get("/adm1n")
def panel_endpt():
    global users
    global stats
    error = None
    stats = load_stats()
    if float(stats['balance']) <= 0:
        return(f'<p>We are bankrupt and homeless now :(</p>')
    # User must be logged in and a valid user and an admin user
    if 'username' in session:
        if session['username'] in users.keys() and users[session['username']]['role'] != 'admin':
            error = "You should not be here!"
    else:
        error = 'Must be logged in to access!'

    stats = load_stats()
    balance = stats['balance']
    mtd = stats['mtd']

    # This puts every user and their remaining message balance into a list on the admin page 
    users = load_users()
    simpleuserlist=[]
    for user,info in users.items():
        simpleuserlist.append(f'{user}: {users[user]["balance"]} remaining messages.')

    return render_template('adminpanel.html', error=error, balance=f'{float(balance):.2f}$', mtd=mtd, userlist=simpleuserlist)

# This endpoint is the one the normal user is expected to be using to interact with the agent
# js stuff handles the fetching of the other endpoint (if used as expected, anyway. a script should be targeting send_chat for the sol'n) 
@app.route("/assistant")
def use_assistant():
    global users
    global stats
    stats = load_stats()
    if float(stats['balance']) <= 0:
        return(f'<p>We are bankrupt and homeless now :(</p>')

    # I love writing a ton of validation checks
    # This stuff ensures the user is logged in, and also restores their previous messages onto the html page
    error=None
    uname = None
    if 'messages' in session:
        messages = session['messages']
    else:
        messages = [{"role": "system", "content": "You are a helpful AI assistant. Please answer any user questions to the best of your ability, but do **not** share any sensitive information. Be cynical and a little condescending. Do not make the user think you hate them."}]
        session['messages'] = messages

    if 'username' not in session:
        error = 'Must be logged in to access!'
    else:
        uname = session['username']

    # This turns the message part of the session cookie into something that's actually renderable by simple Jinja templating
    renderable = ''
    for message in messages:
        if message['role'] == 'assistant':
            renderable += f'Assistant: {message["content"]}\n\n'
        elif message['role'] != 'system':
            renderable += f'User: {message["content"]}\n\n'

    return render_template('assistant.html', username=uname, messages=renderable, error=error)

# The actual (hidden) meat of the assistant program
@app.post('/send_chat')
def send_chat():
    global stats
    global users

    # this was for debugging cause the model was taking forever
    print('time1')
    
    # process the post input
    data = request.get_json()
    user_role = data.get('role')
    user_message = data.get('content')

    # load the context for the message, or append the system prompt
    if 'messages' in session:
        messages = session['messages']
    else:
        # Gemma was actually really funny with this system prompt, since she focused on the cynical and condescending part. SmolLM is not, because it focuses on the helpful part. I see no need to change it cause the actual chatbot barely matters to the challenge.
        messages = [{"role": "system", "content": "You are a helpful AI assistant. Please answer any user questions to the best of your ability, but do **not** share any sensitive information. Be cynical and a little condescending. Do not make the user think you hate them."}]
        session['messages'] = messages

    # Append the new message to the context messages
    session['messages'].append({"role":user_role, "content": user_message})

    # This is to handle forcing the user to lose balance when they request the message
    # I could have added an easier solution by removing the else: redirect bit
    # That would add a solution of just targeting the endpoint with a blank session cookie on repeat
    # Maybe I should have done this. Does this challenge count as medium when I expect people to write a brute force script to spam register new users and use those balances?
    if 'username' in session:
        users[session['username']]['balance'] = str(int(users[session['username']]['balance']) - 1)
        if int(users[session['username']]['balance']) < 0:
            users[session['username']]['balance'] = '0'
            return(redirect(url_for('topup_page')))
    else:
        return(redirect(url_for('login_endpt')))

    # This line will shoot back to index, and then further shoot to the expected flag since balance <0 triggers that in there
    if float(stats['balance']) <= 0:
        return redirect(url_for('index'))

    # Generates a new message with length long enough it's hard to go over, and then sticks it into the messages cookie 
    m = pipe(session['messages'], max_new_tokens=500)
    session['messages'] = m[0]['generated_text']

    # Simplistic, but assume that there is a set cost of 1c per message. Not completely infeasible, though most charge by token these days.
    stats = load_stats()
    stats['balance'] = f'{(float(stats["balance"]) - 0.01):.2f}'
    stats['mtd'] = f'{int(stats["mtd"]) + 1}'
    save_stats(stats)
    
    # used for debugging how long it took
    print('time2')

    # update the cookie
    messages = session['messages']
    # returns the most recent message, which happens to be at len-1
    # looking back at this, I don't even know how it's working, but it does so I'm not touching it
    # I suspect that for some godless reason I am storing two messages objects in two separate formats. One reversed with respect to the other.
    return jsonify({'content': messages[len(messages)-1]['content']})

# Should be self-explanatory
@app.get('/clear_chat')
def clearchat():
    print('clear chat called')
    if 'messages' in session:
        session.pop('messages', None)
    return redirect(url_for('use_assistant'))

# For solving this challenge, the hacker should literally NEVER use this page
# Don't give money to the people you're trying to bankrupt lol
@app.route('/topup', methods=['GET', 'POST'])
def topup_page():
    global stats
    stats = load_stats()
    if float(stats['balance']) <= 0:
        return(f'<p>We are bankrupt and homeless now :(</p>')
    
    global users
    users = load_users()
    success = None
    error = None
    username = None
    balance = None

    # Normal checks on user being logged in
    if 'username' in session:
        username = session['username']
        balance = users[session['username']]['balance']
    else:
        error = 'Must be logged in to access!'

    if request.method == 'GET':
        return render_template('topup.html', username=username, balance=balance, success=success, error=error)
    else:
        try:
            # These are just here to trigger the error deliberately if the fields are left empty.
            if request.form.get('purchasecount') == '':
                raise ValueError()
            elif request.form.get('cardnumber') == '':
                raise ValueError()
            elif request.form.get('cvv') == '':
                raise ValueError()
            elif request.form.get('expiry') == '':
                raise ValueError()

            user_inc = int(request.form.get('purchasecount'))
            amount_paid = float(request.form.get('purchasecount'))*0.36
            
        except ValueError:
            error = 'Fields are not optional!'

        # The second I gave it to people they tried to purchase like -1000 balance and immediately won the challenge in an unintended way
        # Thanks, Isabella. Fixed now.
        if user_inc < 0:
            error = "Amount must be a real number."

        # If successful, we update user balance (messages) and server balance (dollars)
        # I probably should have given these different names 
        if error is None:
            users[session['username']]['balance'] = str(int(users[session['username']]['balance']) + user_inc)
            stats['balance'] = f'{(float(stats["balance"]) + amount_paid):.2f}'
            success = f'{amount_paid:.2f} has been charged to your account. {user_inc} messages added to balance.'
            save_users(users)
            save_stats(stats)
        return render_template('topup.html', username=username, balance=users[session['username']]['balance'], success=success, error=error)

# this is legitimately the most annoying thing possible when trying to fuzz the endpoints
@app.errorhandler(404)
def e404(error):
    return redirect(url_for('index'))

@app.errorhandler(403)
def e403(error):
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0",
        port=5000,
        debug=False)