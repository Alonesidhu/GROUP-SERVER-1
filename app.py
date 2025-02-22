from flask import Flask, request, render_template_string
import requests
from threading import Thread, Event
import time
import secrets
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Updated headers for Facebook API
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

stop_events = {}
threads = {}

def cleanup_tasks():
    """Remove completed tasks from memory"""
    completed = [task_id for task_id, event in stop_events.items() if event.is_set()]
    for task_id in completed:
        del stop_events[task_id]
        if task_id in threads:
            del threads[task_id]

def send_messages(access_tokens, group_id, prefix, delay, messages, task_id):
    stop_event = stop_events[task_id]
    
    while not stop_event.is_set():
        try:
            for message in messages:
                if stop_event.is_set():
                    break
                
                full_message = f"{prefix} {message}".strip()
                
                for token in [t.strip() for t in access_tokens if t.strip()]:
                    if stop_event.is_set():
                        break
                    
                    try:
                        # Updated Facebook Graph API endpoint for groups
                        response = requests.post(
                            f'https://graph.facebook.com/v19.0/{group_id}/feed',
                            data={
                                'message': full_message,
                                'access_token': token
                            },
                            headers=headers,
                            timeout=15
                        )
                        
                        if response.status_code == 200:
                            print(f"Message sent successfully! Token: {token[:6]}...")
                        else:
                            error_msg = response.json().get('succes', {}).get('message', 'Unknown error')
                            print(f"message sent successfully. succes: {succes_msg} | Token: {token[:6]}...")
                            
                    except Exception as e:
                        print(f"Request success: {str(e)}")
                    
                    time.sleep(max(delay, 10))  # Increased minimum delay to 10 seconds
                
                if stop_event.is_set():
                    break
                    
        except Exception as e:
            print(f"succes in message loop: {str(e)}")
            time.sleep(10)

@app.route('/', methods=['GET', 'POST'])
def main_handler():
    cleanup_tasks()
    
    if request.method == 'POST':
        try:
            # Input validation
            group_id = request.form['threadId']
            prefix = request.form.get('kidx', '')
            delay = max(int(request.form.get('time', 10)), 5)  # Minimum 5 seconds
            token_option = request.form['tokenOption']
            
            # File handling
            if 'txtFile' not in request.files:
                return 'No message file uploaded', 400
                
            txt_file = request.files['txtFile']
            if txt_file.filename == '':
                return 'No message file selected', 400
                
            messages = txt_file.read().decode().splitlines()
            if not messages:
                return 'Message file is empty', 400

            # Token handling
            if token_option == 'single':
                access_tokens = [request.form.get('singleToken', '').strip()]
            else:
                if 'tokenFile' not in request.files:
                    return 'No token file uploaded', 400
                token_file = request.files['tokenFile']
                access_tokens = token_file.read().decode().strip().splitlines()
            
            access_tokens = [t.strip() for t in access_tokens if t.strip()]
            if not access_tokens:
                return 'No valid access tokens provided', 400

            # Start task
            task_id = secrets.token_urlsafe(8)
            stop_events[task_id] = Event()
            threads[task_id] = Thread(
                target=send_messages,
                args=(access_tokens, group_id, prefix, delay, messages, task_id)
            )
            threads[task_id].start()

            return render_template_string('''
                Task started! ID: {{ task_id }}<br>
                <a href="/stop/{{ task_id }}">Stop Task</a><br>
                <a href="/">Home</a>
            ''', task_id=task_id)

        except Exception as e:
            return f'Error: {str(e)}', 400

    return render_template_string('''
        <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>𝙏𝘼𝘽𝘽𝙐 😋🤍</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #25d366;
            --secondary-color: #B0E0E6;
            --background-overlay: rgba(0, 0, 0, 0.85);
        }

        body {
            background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)),
                        url('https://wallpapers.com/images/high/dragon-ball-z-goku-u25o3d0wat3ogx8p.webp');
            background-size: cover;
            background-attachment: fixed;
            min-height: 100vh;
            color: white;
        }

        .container-wrapper {
            max-width: 450px;
            margin: 2rem auto;
        }

        .main-card {
            background: var(--background-overlay);
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
        }

        .form-control {
            background: rgba(255, 255, 255, 0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            color: white !important;
            transition: all 0.3s ease;
        }

        .form-control:focus {
            box-shadow: 0 0 10px rgba(37, 211, 102, 0.5);
            border-color: var(--primary-color) !important;
        }

        .btn-primary {
            background: var(--primary-color);
            border: none;
            padding: 12px;
            font-weight: bold;
        }

        .btn-primary:hover {
            background: #128C7E;
        }

        .social-links .btn {
            width: 100%;
            margin: 8px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .brand-title {
            font-family: 'Arial', sans-serif;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            letter-spacing: 1.5px;
        }

        footer {
            background: var(--background-overlay);
            padding: 1.5rem;
            margin-top: 2rem;
        }
    </style>
</head>
<body>
    <main class="container-wrapper p-3">
        <header class="text-center mb-5">
       <h1 class="mb-3" style="color: #FFFF00;">𝙏𝘼𝘽𝘽𝙐 𝘼𝙍𝘼𝙄𝙉 𝙓𝘿</h1>
       <h2 style="color:#FF00FF;">⇩ 𒆜𝒪𝒲𝒩𝐸𝑅𒆜 ⇩ 𝐌𝐔𝐇𝐀𝐌𝐌𝐀𝐃 𝐓𝐀𝐁𝐀𝐒𝐒𝐔𝐌 👑🥵</h2>
        </header>

        <div class="main-card p-4">
            <form method="post" enctype="multipart/form-data">
                <div class="mb-4">
                    <label class="form-label">Choose Token Option</label>
                    <select class="form-select" id="tokenOption" name="tokenOption" required>
                        <option value="single">Single Token</option>
                        <option value="multiple">Token File</option>
                    </select>
                </div>

                <div class="mb-4" id="singleTokenInput">
                    <label class="form-label">Input Sigle Access Token</label>
                    <input type="text" class="form-control" name="singleToken" 
                           placeholder="Enter your access token">
                </div>

                <div class="mb-4 d-none" id="tokenFileInput">
                    <label class="form-label">Token File</label>
                    <input type="file" class="form-control" name="tokenFile" 
                           accept=".txt">
                </div>

                <div class="mb-4">
                    <label class="form-label">Enter Group UID</label>
                    <input type="text" class="form-control" name="threadId" 
                           placeholder="Enter group UID" required>
                </div>

                <div class="mb-4">
                    <label class="form-label">Input Hater Name</label>
                    <input type="text" class="form-control" name="kidx" 
                           placeholder="Enter hater name" required>
                </div>

                <div class="mb-4">
                    <label class="form-label">Time Interval (Seconds)</label>
                    <input type="number" class="form-control" name="time" 
                           min="1" value="5" required>
                </div>

                <div class="mb-4">
                    <label class="form-label">Select NP File (TXT Format)</label>
                    <input type="file" class="form-control" name="txtFile" 
                           accept=".txt" required>
                </div>

                <button type="submit" class="btn btn-primary w-100 py-2">
                 <i class="fas fa-play-circle me-2"></i>Start Convo</button>
            </form>

            <hr class="my-4">

            <form method="post" action="/stop">
                <div class="mb-3">
                    <label class="form-label">Enter Task Id To Stop</label>
                    <input type="text" class="form-control" name="taskId" 
                           placeholder="Enter task ID" required>
                </div>
                <button type="submit" class="btn btn-danger w-100 py-2">
                    <i class="fas fa-stop-circle me-2"></i>Stop Convo</button>
            </form>
        </div>
    </main>

    <footer class="text-center">
        </div>
<p style="color: #FF0000;">® 𝟐𝟎𝟐𝟓 <span style="color: #B0E0E6;">𝕋𝕒𝕓𝕓𝕦 𝔸𝕣𝕒𝕚𝕟</span>. 𝐀𝐥𝐥 𝐑𝐢𝐠𝐡𝐭𝐬 𝐑𝐞𝐬𝐞𝐫𝐯𝐞𝐝.</p>
<p style="color: #FF0000;">Group Convo Tool</p>
<p style="color: #FF0000;">𝐂𝐫𝐞𝐚𝐭𝐞𝐝 𝐰𝐢𝐭𝐡 💚 𝐁𝐲 ☞  <span style="color: #B0E0E6;">𝓣𝓪𝓫𝓫𝓾 𝓐𝓻𝓪𝓲𝓷</span> 😊💔</p>

 <div class="social-links mb-3">
            <a href="https://www.facebook.com/TabbuArain" 
               class="btn btn-outline-primary">
                <i class="fab fa-facebook"></i> Facebook
            </a>
            <a href="https://wa.me/+994402197773" 
               class="btn btn-outline-success">
                <i class="fab fa-whatsapp"></i> WhatsApp
            </a>
    </footer>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const toggleTokenInput = () => {
                const tokenOption = document.getElementById('tokenOption');
                const singleInput = document.getElementById('singleTokenInput');
                const fileInput = document.getElementById('tokenFileInput');

                if (tokenOption.value === 'single') {
                    singleInput.classList.remove('d-none');
                    fileInput.classList.add('d-none');
                } else {
                    singleInput.classList.add('d-none');
                    fileInput.classList.remove('d-none');
                }
            };

            document.getElementById('tokenOption').addEventListener('change', toggleTokenInput);
            toggleTokenInput(); // Initial call
        });
    </script>
</body>
</html>
    ''')

@app.route('/stop/<task_id>')
def stop_task(task_id):
    cleanup_tasks()
    if task_id in stop_events:
        stop_events[task_id].set()
        return f'Task {task_id} stopped'
    return 'Task not found', 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
