"""
Lovable Referral Bot - Web Server
Interface PWA para controle do bot
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import threading
import time
import os
from bot_selenium import LovableBot, parse_accounts

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'lovable_bot_2024_secret')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global status
bot_status = {
    'running': False,
    'current_account': '',
    'processed': 0,
    'success': 0,
    'failed': 0,
    'total': 0,
    'logs': []
}

def log_callback(message, status='info'):
    """Callback for bot logs"""
    timestamp = time.strftime('%H:%M:%S')
    log_entry = {'time': timestamp, 'message': message, 'status': status}
    bot_status['logs'].append(log_entry)
    
    # Keep only last 100 logs
    if len(bot_status['logs']) > 100:
        bot_status['logs'] = bot_status['logs'][-100:]
    
    socketio.emit('log', log_entry)
    socketio.emit('status_update', {
        'processed': bot_status['processed'],
        'success': bot_status['success'],
        'failed': bot_status['failed'],
        'total': bot_status['total'],
        'current': bot_status['current_account'],
        'running': bot_status['running']
    })

def run_bot_thread(accounts, referral_link, headless=True):
    """Run bot in background thread"""
    bot_status['running'] = True
    bot_status['processed'] = 0
    bot_status['success'] = 0
    bot_status['failed'] = 0
    bot_status['total'] = len(accounts)
    bot_status['logs'] = []
    
    log_callback(f"🚀 Iniciando bot com {len(accounts)} contas", 'info')
    log_callback(f"🔗 Link de referral: {referral_link}", 'info')
    
    for i, account in enumerate(accounts):
        if not bot_status['running']:
            log_callback("⏹️ Bot parado pelo usuário", 'warning')
            break
        
        bot_status['current_account'] = account['email']
        log_callback(f"📌 Conta {i+1}/{len(accounts)}: {account['email']}", 'info')
        
        # Create new bot instance for each account (clean browser)
        bot = LovableBot(headless=headless, log_callback=log_callback)
        
        try:
            success = bot.process_account(
                account['email'],
                account['password'],
                referral_link
            )
            
            bot_status['processed'] += 1
            if success:
                bot_status['success'] += 1
                log_callback(f"✅ Conta {account['email']} - SUCESSO!", 'success')
            else:
                bot_status['failed'] += 1
                log_callback(f"❌ Conta {account['email']} - FALHOU", 'error')
                
        except Exception as e:
            bot_status['processed'] += 1
            bot_status['failed'] += 1
            log_callback(f"❌ Erro com {account['email']}: {str(e)}", 'error')
        
        # Delay between accounts
        if i < len(accounts) - 1 and bot_status['running']:
            delay = 5
            log_callback(f"⏳ Aguardando {delay}s antes da próxima conta...", 'info')
            time.sleep(delay)
    
    bot_status['running'] = False
    bot_status['current_account'] = ''
    log_callback(f"🏁 Bot finalizado! ✅ Sucesso: {bot_status['success']} | ❌ Falhas: {bot_status['failed']}", 'complete')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

@app.route('/api/start', methods=['POST'])
def start_bot():
    if bot_status['running']:
        return jsonify({'error': 'Bot já está rodando'}), 400
    
    data = request.json
    accounts_text = data.get('accounts', '')
    referral_link = data.get('referral_link', '')
    headless = data.get('headless', True)
    
    if not accounts_text:
        return jsonify({'error': 'Nenhuma conta fornecida'}), 400
    
    if not referral_link:
        return jsonify({'error': 'Link de referral não fornecido'}), 400
    
    accounts = parse_accounts(accounts_text)
    
    if not accounts:
        return jsonify({'error': 'Nenhuma conta válida encontrada. Use formato: email:senha'}), 400
    
    # Start bot in background thread
    thread = threading.Thread(target=run_bot_thread, args=(accounts, referral_link, headless))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'accounts_found': len(accounts)})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    bot_status['running'] = False
    return jsonify({'success': True})

@app.route('/api/status')
def get_status():
    return jsonify(bot_status)

@socketio.on('connect')
def handle_connect():
    emit('status_update', {
        'processed': bot_status['processed'],
        'success': bot_status['success'],
        'failed': bot_status['failed'],
        'total': bot_status['total'],
        'current': bot_status['current_account'],
        'running': bot_status['running']
    })
    # Send recent logs
    for log in bot_status['logs'][-20:]:
        emit('log', log)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
