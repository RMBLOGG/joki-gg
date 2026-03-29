from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from supabase_client import supabase

auth_bp = Blueprint('auth', __name__)

ADMIN_EMAIL = "ramdanbmxflat008@gmail.com"
ADMIN_PASSWORD = "RMBLOGG"

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Hardcode admin
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['user_id'] = 'admin-hardcode'
            session['email'] = email
            session['role'] = 'admin'
            session['username'] = 'Admin'
            session['balance'] = 0
            flash('Login berhasil!', 'success')
            return redirect(url_for('admin.dashboard'))

        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            user = res.user
            session['user_id'] = user.id
            session['email'] = user.email

            profile = supabase.table('profiles').select('*').eq('id', user.id).single().execute()
            if profile.data:
                session['role'] = profile.data.get('role', 'buyer')
                session['username'] = profile.data.get('username', email)
                session['balance'] = profile.data.get('balance', 0)

            flash('Login berhasil!', 'success')
            if session.get('role') == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.index'))
        except Exception as e:
            flash('Email atau password salah.', 'error')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        role = request.form.get('role', 'joki')

        try:
            res = supabase.auth.sign_up({"email": email, "password": password})
            user = res.user
            if user:
                supabase.table('profiles').insert({
                    'id': user.id,
                    'email': email,
                    'username': username,
                    'role': role,
                    'balance': 0,
                    'is_verified': False
                }).execute()
                flash('Registrasi berhasil! Silakan login.', 'success')
                return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Registrasi gagal: {str(e)}', 'error')
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    supabase.auth.sign_out()
    session.clear()
    return redirect(url_for('main.index'))
