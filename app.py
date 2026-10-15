from flask import Flask, render_template, request, redirect, url_for, json, session
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Secret key acak yang lebih kuat untuk keamanan sesi di cloud
app.secret_key = 'k839!x_dny_v3r3_s3cr3t_museum_2026_key'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS_IMG = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS_AUDIO = {'mp3', 'wav', 'ogg'}

def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set

def load_data():
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'admin_password' not in data:
                data['admin_password'] = 'dnycrew123'
            if 'souvenir' not in data:
                data['souvenir'] = [
                    {"name": "Stiker Basreng Rancakole", "desc": "Stiker edisi spesial pedas mantap.", "photo": "", "is_key_item": False},
                    {"name": "Koin Emas Quest", "desc": "Koin legendaris untuk membuka pintu rahasia museum.", "photo": "", "is_key_item": True}
                ]
            if 'vault_secrets' not in data:
                data['vault_secrets'] = [
                    {"title": "Arsip Rahasia Proyek 3D Opat Baraya", "desc": "Draf skenario awal dan catatan sutradara sebelum animasi diproduksi.", "date": "Agustus 2026", "photo": ""}
                ]
            return data
            
    return {
        "admin_password": "dnycrew123",
        "crew": [], "birthday": [], "farewell": [], "guestbook": [], "events": [], 
        "featured_crew": None, "cinema": [],
        "souvenir": [
            {"name": "Stiker Basreng Rancakole", "desc": "Stiker edisi spesial pedas mantap.", "photo": "", "is_key_item": False},
            {"name": "Koin Emas Quest", "desc": "Koin legendaris untuk membuka pintu rahasia museum.", "photo": "", "is_key_item": True}
        ],
        "vault_secrets": [
            {"title": "Arsip Rahasia Proyek 3D Opat Baraya", "desc": "Draf skenario awal dan catatan sutradara sebelum animasi diproduksi.", "date": "Agustus 2026", "photo": ""}
        ]
    }

def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    data = load_data()
    has_key = session.get('has_vault_key', False) or session.get('is_admin', False)
    return render_template('index.html', data=data, has_key=has_key)

@app.route('/crew')
def crew():
    data = load_data()
    return render_template('crew.html', crew=data.get('crew', []), featured_crew=data.get('featured_crew'), is_admin=session.get('is_admin', False))

@app.route('/birthday')
def birthday():
    data = load_data()
    return render_template('birthday.html', birthday=data.get('birthday', []))

@app.route('/farewell')
def farewell():
    data = load_data()
    return render_template('farewell.html', farewell=data.get('farewell', []))

@app.route('/guestbook', methods=['GET', 'POST'])
def guestbook():
    data = load_data()
    if request.method == 'POST':
        visitor_name = request.form.get('visitor_name', 'Anonim')
        message = request.form.get('message', '')
        if message:
            now = datetime.now()
            months_id = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
            date_str = f"{now.day} {months_id[now.month - 1]} {now.year} - {now.strftime('%H:%M')}"
            if 'guestbook' not in data: data['guestbook'] = []
            data['guestbook'].insert(0, {"name": visitor_name, "message": message, "date": date_str})
            save_data(data)
        return redirect(url_for('guestbook'))
    return render_template('guestbook.html', guestbook=data.get('guestbook', []))

@app.route('/cinema')
def cinema():
    data = load_data()
    return render_template('cinema.html', cinema=data.get('cinema', []), is_admin=session.get('is_admin', False))

@app.route('/events')
def events():
    data = load_data()
    return render_template('events.html', events=data.get('events', []), is_admin=session.get('is_admin', False))

@app.route('/souvenir')
def souvenir():
    data = load_data()
    inventory = session.get('inventory', [])
    has_key = session.get('has_vault_key', False) or session.get('is_admin', False)
    return render_template('souvenir.html', souvenirs=data.get('souvenir', []), inventory=inventory, has_key=has_key, is_admin=session.get('is_admin', False))

@app.route('/claim_souvenir/<int:index>', methods=['POST'])
def claim_souvenir(index):
    data = load_data()
    souvenirs = data.get('souvenir', [])
    if 0 <= index < len(souvenirs):
        item = souvenirs[index]
        if 'inventory' not in session: session['inventory'] = []
        if item not in session['inventory']:
            session['inventory'].append(item)
            session.modified = True
    return redirect(url_for('souvenir'))

@app.route('/exchange_key', methods=['POST'])
def exchange_key():
    session['has_vault_key'] = True
    session.modified = True
    return redirect(url_for('souvenir'))

@app.route('/admin_vault', methods=['GET', 'POST'])
def admin_vault():
    data = load_data()
    error = None
    if request.method == 'POST':
        code = request.form.get('code', '')
        actual_password = data.get('admin_password', 'dnycrew123')
        if code == actual_password:
            session['is_admin'] = True
            session['has_vault_key'] = True
            session.modified = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Kode Sandi Pengelola Salah!"
    return render_template('admin_vault.html', error=error)

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('is_admin', False):
        return redirect(url_for('admin_vault'))
    data = load_data()
    success_msg = request.args.get('success', '')
    return render_template('admin_dashboard.html', data=data, success_msg=success_msg)

@app.route('/admin/change_password', methods=['POST'])
def change_password():
    if not session.get('is_admin', False): return redirect(url_for('admin_vault'))
    data = load_data()
    new_password = request.form.get('new_password', '')
    if new_password:
        data['admin_password'] = new_password
        save_data(data)
        return redirect(url_for('admin_dashboard', success='Sandi admin berhasil diperbarui!'))
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_crew', methods=['POST'])
def admin_add_crew():
    if not session.get('is_admin', False): return redirect(url_for('admin_vault'))
    data = load_data()
    name = request.form.get('name', '')
    role = request.form.get('role', '')
    bday_date = request.form.get('bday_date', '')
    
    photo_filename = ''
    if 'photo' in request.files:
        file = request.files['photo']
        if file and file.filename != '' and allowed_file(file.filename, ALLOWED_EXTENSIONS_IMG):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo_filename = filename

    new_member = {"name": name, "role": role, "photo": photo_filename, "bday_date": bday_date}
    if 'crew' not in data: data['crew'] = []
    data['crew'].append(new_member)

    if bday_date:
        if 'birthday' not in data: data['birthday'] = []
        existing_bday = next((b for b in data['birthday'] if b['name'] == name), None)
        if not existing_bday:
            data['birthday'].append({"name": name, "date": bday_date, "photo": photo_filename})
        else:
            existing_bday['date'] = bday_date
            if photo_filename: existing_bday['photo'] = photo_filename

    save_data(data)
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_crew/<int:index>', methods=['POST'])
def admin_delete_crew(index):
    if not session.get('is_admin', False): return redirect(url_for('admin_vault'))
    data = load_data()
    crew_list = data.get('crew', [])
    if 0 <= index < len(crew_list):
        removed = crew_list.pop(index)
        if data.get('featured_crew') and data['featured_crew'].get('name') == removed.get('name'):
            data['featured_crew'] = None
        save_data(data)
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/set_featured_crew/<int:index>', methods=['POST'])
def admin_set_featured_crew(index):
    if not session.get('is_admin', False): return redirect(url_for('admin_vault'))
    data = load_data()
    crew_list = data.get('crew', [])
    if 0 <= index < len(crew_list):
        data['featured_crew'] = crew_list[index]
        save_data(data)
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/transfer_to_farewell/<int:index>', methods=['POST'])
def admin_transfer_to_farewell(index):
    if not session.get('is_admin', False): return redirect(url_for('admin_vault'))
    data = load_data()
    crew_list = data.get('crew', [])
    if 0 <= index < len(crew_list):
        member = crew_list.pop(index)
        if data.get('featured_crew') and data['featured_crew'].get('name') == member.get('name'):
            data['featured_crew'] = None

        audio_filename = ''
        if 'farewell_audio' in request.files:
            file_audio = request.files['farewell_audio']
            if file_audio and file_audio.filename != '' and allowed_file(file_audio.filename, ALLOWED_EXTENSIONS_AUDIO):
                filename_audio = secure_filename(file_audio.filename)
                file_audio.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_audio))
                audio_filename = filename_audio

        now = datetime.now()
        months_id = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        date_str = f"{now.day} {months_id[now.month - 1]} {now.year}"
        
        farewell_item = {
            "title": f"Perpisahan - {member['name']}",
            "message": f"Peran: {member.get('role', '-')}",
            "photo": member.get('photo', ''),
            "audio": audio_filename,
            "end_date": date_str
        }
        if 'farewell' not in data: data['farewell'] = []
        data['farewell'].append(farewell_item)
        save_data(data)
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_cinema/<int:index>', methods=['POST'])
def admin_delete_cinema(index):
    if not session.get('is_admin', False): return redirect(url_for('admin_vault'))
    data = load_data()
    cinema_list = data.get('cinema', [])
    if 0 <= index < len(cinema_list):
        cinema_list.pop(index)
        save_data(data)
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_cinema', methods=['POST'])
def admin_add_cinema():
    if not session.get('is_admin', False): return redirect(url_for('admin_vault'))
    data = load_data()
    title = request.form.get('title', '')
    desc = request.form.get('desc', '')
    video_url = request.form.get('video_url', '')
    category = request.form.get('category', 'Animasi 3D')

    if title and video_url:
        if 'watch?v=' in video_url: video_url = video_url.replace('watch?v=', 'embed/')
        elif 'youtu.be/' in video_url: video_url = video_url.replace('youtu.be/', 'www.youtube.com/embed/')

        if 'cinema' not in data: data['cinema'] = []
        data['cinema'].insert(0, {"title": title, "desc": desc, "video_url": video_url, "category": category})
        save_data(data)
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_souvenir', methods=['POST'])
def admin_add_souvenir():
    if not session.get('is_admin', False): return redirect(url_for('admin_vault'))
    data = load_data()
    name = request.form.get('name', '')
    desc = request.form.get('desc', '')
    is_key_item = True if request.form.get('is_key_item') == 'on' else False
    
    photo_filename = ''
    if 'photo' in request.files:
        file = request.files['photo']
        if file and file.filename != '' and allowed_file(file.filename, ALLOWED_EXTENSIONS_IMG):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo_filename = filename

    if name:
        if 'souvenir' not in data: data['souvenir'] = []
        data['souvenir'].append({"name": name, "desc": desc, "photo": photo_filename, "is_key_item": is_key_item})
        save_data(data)
    return redirect(url_for('admin_dashboard'))

@app.route('/vault', methods=['GET', 'POST'])
def vault():
    has_key = session.get('has_vault_key', False)
    is_admin = session.get('is_admin', False)
    
    if not has_key and not is_admin:
        return redirect(url_for('admin_vault'))
        
    data = load_data()
    if request.method == 'POST':
        title = request.form.get('title', '')
        desc = request.form.get('desc', '')
        
        photo_filename = ''
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename, ALLOWED_EXTENSIONS_IMG):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                photo_filename = filename

        if title:
            if 'vault_secrets' not in data: data['vault_secrets'] = []
            now = datetime.now()
            months_id = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
            date_str = f"{now.day} {months_id[now.month - 1]} {now.year}"
            
            data['vault_secrets'].insert(0, {"title": title, "desc": desc, "date": date_str, "photo": photo_filename})
            save_data(data)
        return redirect(url_for('vault'))
        
    return render_template('vault.html', secrets=data.get('vault_secrets', []))

if __name__ == '__main__':
    # Mode debug dimatikan untuk keamanan saat online
    app.run(debug=False, host='0.0.0.0', port=5000)
