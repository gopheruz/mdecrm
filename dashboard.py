# -*- coding: utf-8 -*-
from flask import Flask, request, render_template_string, send_file, session, redirect, url_for
import paramiko
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure session key

HTML_PAGE = '''
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Просмотр записей Asterisk</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #1a73e8;
            --primary-dark: #1557b0;
            --danger: #d93025;
            --success: #188038;
            --warning: #f4b400;
            --gray: #f1f3f4;
            --dark-gray: #dadce0;
            --text: #202124;
            --text-secondary: #5f6368;
            --white: #ffffff;
            --shadow: 0 2px 8px rgba(0,0,0,0.15);
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: 'Roboto', sans-serif;
            line-height: 1.6;
            color: var(--text);
            background-color: var(--gray);
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }

        .container {
            max-width: 1280px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            background-color: var(--white);
            box-shadow: var(--shadow);
            padding: 15px 0;
            position: sticky;
            top: 0;
            z-index: 1000;
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
        }

        h1 {
            color: var(--primary);
            margin: 0;
            font-weight: 500;
            font-size: 24px;
        }

        .user-info {
            background-color: var(--gray);
            border-radius: 20px;
            padding: 8px 16px;
            font-size: 14px;
            display: flex;
            align-items: center;
            transition: background-color 0.3s;
        }

        .user-info:hover {
            background-color: var(--dark-gray);
        }

        .user-info .status {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }

        .status.connected {
            background-color: var(--success);
        }

        .status.disconnected {
            background-color: var(--danger);
        }

        .logout-btn {
            color: var(--danger);
            text-decoration: none;
            margin-left: 15px;
            font-weight: 500;
            transition: color 0.3s;
        }

        .logout-btn:hover {
            color: var(--primary);
        }

        .card {
            background: var(--white);
            border-radius: 12px;
            box-shadow: var(--shadow);
            padding: 30px;
            margin-bottom: 30px;
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
        }

        .card-title {
            font-size: 20px;
            margin: 0 0 20px;
            color: var(--primary);
            font-weight: 500;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: var(--text-secondary);
        }

        input[type="text"], 
        input[type="password"],
        input[type="number"],
        input[type="date"],
        input[type="email"],
        input[type="tel"] {
            width: 100%;
            padding: 12px 16px;
            border: 1px solid var(--dark-gray);
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s ease;
            background: var(--white);
        }

        input:focus {
            border-color: var(--primary);
            outline: none;
            box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.2);
        }

        .input-hint {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 6px;
        }

        .btn {
            background-color: var(--primary);
            color: var(--white);
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .btn:hover {
            background-color: var(--primary-dark);
            transform: translateY(-2px);
        }

        .btn-block {
            width: 100%;
        }

        .connection-details {
            background-color: var(--gray);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .connection-details p {
            margin: 8px 0;
            font-size: 14px;
        }

        .connection-details strong {
            color: var(--text-secondary);
        }

        .file-list {
            margin-top: 20px;
        }

        .file-item {
            background: var(--white);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: var(--shadow);
            border-left: 4px solid var(--primary);
            transition: transform 0.3s ease;
        }

        .file-item:hover {
            transform: translateX(5px);
        }

        .file-name {
            font-weight: 500;
            margin-bottom: 10px;
            color: var(--text);
            font-size: 16px;
        }

        .file-actions {
            margin-top: 10px;
        }

        .download-link {
            color: var(--primary);
            text-decoration: none;
            font-size: 14px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: color 0.3s;
        }

        .download-link:hover {
            color: var(--primary-dark);
            text-decoration: underline;
        }

        .error-message, .success-message {
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
            animation: fadeIn 0.5s ease;
        }

        .error-message {
            background-color: #feeae9;
            color: var(--danger);
        }

        .success-message {
            background-color: #e6f4ea;
            color: var(--success);
        }

        audio {
            width: 100%;
            margin-top: 10px;
            border-radius: 8px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }

        input[type="date"]::-webkit-calendar-picker-indicator {
            cursor: pointer;
            opacity: 0.7;
        }

        .input-with-icon {
            position: relative;
        }

        .input-with-icon i {
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-secondary);
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); }
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 600px) {
            .container {
                padding: 15px;
            }
            .grid {
                grid-template-columns: 1fr Napa County, CA

            .header-content {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }

            h1 {
                font-size: 20px;
            }

            .btn {
                padding: 10px 20px;
            }

            .card {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container header-content">
            <h1>Просмотр записей Asterisk</h1>
            <div class="user-info">
                <span class="status {% if session.get('logged_in') %}connected{% else %}disconnected{% endif %}"></span>
                IP: {{ request.remote_addr }}
                {% if session.get('logged_in') %}
                    | <a href="{{ url_for('logout') }}" class="logout-btn">Выйти</a>
                {% endif %}
            </div>
        </div>
    </header>
    
    <div class="container">
        {% if error %}
        <div class="error-message">
            <i class="fas fa-exclamation-circle"></i> {{ error }}
        </div>
        {% endif %}
        
        {% if success %}
        <div class="success-message">
            <i class="fas fa-check-circle"></i> {{ success }}
        </div>
        {% endif %}
        
        {% if not session.get('logged_in') %}
        <div class="card">
            <h2 class="card-title">Подключение к серверу</h2>
            <form method="post" action="{{ url_for('login') }}">
                <div class="grid">
                    <div class="form-group">
                        <label for="host">IP-адрес сервера</label>
                        <input type="text" id="host" name="host" required 
                               placeholder="192.168.1.1" 
                               pattern="^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$|^([a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]?\.)+[a-zA-Z]{2,}$"
                               title="Введите корректный IP-адрес или домен">
                        <div class="input-hint">Пример: 192.168.1.1 или domain.com</div>
                    </div>
                    
                    <div class="form-group">
                        <label for="port">Порт SSH</label>
                        <input type="number" id="port" name="port" required 
                               value="22" min="1" max="65535" 
                               placeholder="22">
                        <div class="input-hint">Обычно 22 для SSH</div>
                    </div>
                    
                    <div class="form-group">
                        <label for="username">Имя пользователя</label>
                        <input type="text" id="username" name="username" required 
                               placeholder="root">
                        <div class="input-hint">Имя пользователя SSH</div>
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Пароль</label>
                        <div class="input-with-icon">
                            <input type="password" id="password" name="password" required 
                                   placeholder="Введите пароль">
                            <i class="fas fa-lock"></i>
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="date">Дата записей</label>
                    <input type="date" id="date" name="date" 
                           value="{{ default_date_iso }}"
                           max="{{ max_date_iso }}"
                           required>
                    <div class="input-hint">Выберите дату для поиска записей</div>
                </div>
                
                <button type="submit" class="btn btn-block">
                    <i class="fas fa-plug"></i> Подключиться
                </button>
            </form>
        </div>
        {% else %}
        <div class="connection-details">
            <p><strong>Сервер:</strong> {{ session['host'] }}:{{ session['port'] }}</p>
            <p><strong>Пользователь:</strong> {{ session['username'] }}</p>
            <p><strong>Текущая дата:</strong> {{ session['last_date'] }}</p>
        </div>
        
        <div class="card">
            <h2 class="card-title">Поиск записей</h2>
            <form method="post" action="{{ url_for('index') }}">
                <div class="form-group">
                    <label for="search_date">Дата записей</label>
                    <input type="date" id="search_date" name="date" 
                           value="{{ date_path_iso }}"
                           max="{{ max_date_iso }}"
                           required>
                    <div class="input-hint">Выберите дату для поиска записей</div>
                </div>
                <button type="submit" class="btn">
                    <i class="fas fa-search"></i> Поиск записей
                </button>
            </form>
        </div>
        
        {% if files %}
        <div class="card">
            <h2 class="card-title">Найдено записей: {{ files|length }} ({{ date_path }})</h2>
            
            <div class="file-list">
                {% for file in files %}
                <div class="file-item">
                    <div class="file-name">
                        <i class="fas fa-file-audio"></i> {{ file }}
                    </div>
                    <audio controls preload="none">
                        <source src="{{ url_for('stream', file=file, date=date_path) }}" type="audio/wav">
                        Ваш браузер не поддерживает аудио элементы.
                    </audio>
                    <div class="file-actions">
                        <a href="{{ url_for('download', file=file, date=date_path) }}" class="download-link">
                            <i class="fas fa-download"></i> Скачать запись
                        </a>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        {% endif %}
    </div>
    
    <!-- Font Awesome for icons -->
    <script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
    <!-- Client-side form validation -->
    <script>
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function(event) {
                const inputs = form.querySelectorAll('input[required]');
                let valid = true;
                inputs.forEach(input => {
                    if (!input.value) {
                        valid = false;
                        input.style.borderColor = 'var(--danger)';
                    } else {
                        input.style.borderColor = '';
                    }
                });
                if (!valid) {
                    event.preventDefault();
                    alert('Пожалуйста, заполните все обязательные поля.');
                }
            });
        });
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle the main page for searching and displaying recordings."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    files = []
    date_path = session.get('last_date', '')
    error = None
    success = None
    
    if request.method == 'POST':
        date_path = request.form.get('date', '')
        
        if not date_path:
            error = "Пожалуйста, укажите дату для поиска записей"
        else:
            try:
                # Convert from YYYY-MM-DD to YYYY/MM/DD format
                date_path = date_path.replace('-', '/')
                
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(
                    hostname=session['host'],
                    port=session['port'],
                    username=session['username'],
                    password=session['password'],
                    timeout=10
                )
                
                remote_path = f"/var/spool/asterisk/monitor/{date_path}"
                sftp = ssh.open_sftp()
                try:
                    files = sorted(sftp.listdir(remote_path), reverse=True)
                    session['last_date'] = date_path
                    success = f"Найдено {len(files)} записей за {date_path}"
                except Exception as e:
                    error = f"Записи за указанную дату ({date_path}) не найдены"
                finally:
                    sftp.close()
                    ssh.close()
            except Exception as e:
                error = f"Ошибка при подключении: {str(e)}"

    # Prepare dates for HTML5 date inputs
    today = datetime.now()
    default_date_iso = today.strftime("%Y-%m-%d")
    max_date_iso = today.strftime("%Y-%m-%d")
    date_path_iso = date_path.replace('/', '-') if date_path else default_date_iso
    
    return render_template_string(
        HTML_PAGE, 
        files=files, 
        date_path=date_path,
        date_path_iso=date_path_iso,
        default_date_iso=default_date_iso,
        max_date_iso=max_date_iso,
        error=error,
        success=success
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login and SSH connection setup."""
    if request.method == 'POST':
        host = request.form.get('host')
        port = int(request.form.get('port', 22))
        username = request.form.get('username')
        password = request.form.get('password')
        date_iso = request.form.get('date')
        
        # Convert from YYYY-MM-DD to YYYY/MM/DD format
        date_path = date_iso.replace('-', '/') if date_iso else datetime.now().strftime("%Y/%m/%d")
        
        # Test SSH connection
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=10
            )
            ssh.close()
            
            # Store connection details in session
            session['logged_in'] = True
            session['host'] = host
            session['port'] = port
            session['username'] = username
            session['password'] = password
            session['last_date'] = date_path
            
            return redirect(url_for('index'))
        except Exception as e:
            today = datetime.now()
            return render_template_string(
                HTML_PAGE, 
                error=f"Ошибка подключения: {str(e)}",
                default_date_iso=today.strftime("%Y-%m-%d"),
                max_date_iso=today.strftime("%Y-%m-%d")
            )
    
    today = datetime.now()
    return render_template_string(
        HTML_PAGE, 
        default_date_iso=today.strftime("%Y-%m-%d"),
        max_date_iso=today.strftime("%Y-%m-%d")
    )

@app.route('/logout')
def logout():
    """Clear session and log out the user."""
    session.clear()
    return redirect(url_for('login'))

@app.route('/stream')
def stream():
    """Stream an audio file from the remote server."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    file = request.args.get('file')
    date = request.args.get('date')
    
    if not (file and date):
        return "Ошибка: Не указаны необходимые параметры", 400

    remote_file = f"/var/spool/asterisk/monitor/{date}/{file}"
    local_path = f"/tmp/{file}"

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=session['host'],
            port=session['port'],
            username=session['username'],
            password=session['password'],
            timeout=10
        )
        sftp = ssh.open_sftp()
        sftp.get(remote_file, local_path)
        sftp.close()
        ssh.close()
        
        response = send_file(local_path, mimetype='audio/wav', as_attachment=False)
        
        # Clean up temporary file
        try:
            os.remove(local_path)
        except OSError:
            pass
            
        return response
    except Exception as e:
        return f"Ошибка: {str(e)}", 500

@app.route('/download')
def download():
    """Download an audio file from the remote server."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    file = request.args.get('file')
    date = request.args.get('date')
    
    if not (file and date):
        return "Ошибка: Не указаны необходимые параметры", 400

    remote_file = f"/var/spool/asterisk/monitor/{date}/{file}"
    local_path = f"/tmp/{file}"

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=session['host'],
            port=session['port'],
            username=session['username'],
            password=session['password'],
            timeout=10
        )
        sftp = ssh.open_sftp()
        sftp.get(remote_file, local_path)
        sftp.close()
        ssh.close()
        
        response = send_file(local_path, mimetype='audio/wav', as_attachment=True, download_name=file)
        
        # Clean up temporary file
        try:
            os.remove(local_path)
        except OSError:
            pass
            
        return response
    except Exception as e:
        return f"Ошибка: {str(e)}", 500

if __name__ == '__main__':
    # Ensure temporary directory exists
    os.makedirs('/tmp', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)