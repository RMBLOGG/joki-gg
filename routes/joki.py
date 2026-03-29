from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from supabase_client import supabase
from cloudinary_helper import upload_image
from functools import wraps

joki_bp = Blueprint('joki', __name__, url_prefix='/joki')

def joki_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('role') not in ('joki', 'admin'):
            flash('Akses hanya untuk joki.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated

@joki_bp.route('/dashboard')
@joki_required
def dashboard():
    joki_id = session['user_id']
    profile = supabase.table('profiles').select('*').eq('id', joki_id).single().execute()
    services = supabase.table('services').select('*').eq('joki_id', joki_id).execute()
    active_orders = supabase.table('orders').select('*, profiles!orders_buyer_id_fkey(username), services(title)').eq('joki_id', joki_id).in_('status', ['in_progress', 'waiting_confirmation']).execute()
    pending_orders = supabase.table('orders').select('*, profiles!orders_buyer_id_fkey(username), services(title)').eq('joki_id', joki_id).eq('status', 'active').execute()
    
    # Stats
    total_earnings = supabase.table('orders').select('joki_earning').eq('joki_id', joki_id).eq('status', 'completed').execute()
    earnings_sum = sum(o['joki_earning'] for o in (total_earnings.data or []))

    return render_template('joki/dashboard.html',
        profile=profile.data,
        services=services.data or [],
        active_orders=active_orders.data or [],
        pending_orders=pending_orders.data or [],
        total_earnings=earnings_sum
    )

@joki_bp.route('/services/add', methods=['GET', 'POST'])
@joki_required
def add_service():
    categories = supabase.table('game_categories').select('*').execute()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        game_name = request.form['game_name']
        service_type = request.form['service_type']
        price = int(request.form['price'])
        rank_from = request.form.get('rank_from', '')
        rank_to = request.form.get('rank_to', '')
        
        thumbnail = request.files.get('thumbnail')
        thumbnail_url = None
        if thumbnail:
            thumbnail_url = upload_image(thumbnail, folder="service_thumbnails")

        supabase.table('services').insert({
            'joki_id': session['user_id'],
            'title': title,
            'description': description,
            'game_name': game_name,
            'service_type': service_type,
            'price': price,
            'rank_from': rank_from,
            'rank_to': rank_to,
            'thumbnail_url': thumbnail_url,
            'is_active': True
        }).execute()

        flash('Layanan berhasil ditambahkan!', 'success')
        return redirect(url_for('joki.dashboard'))

    return render_template('joki/add_service.html', categories=categories.data or [])

@joki_bp.route('/services/<int:service_id>/edit', methods=['GET', 'POST'])
@joki_required
def edit_service(service_id):
    service = supabase.table('services').select('*').eq('id', service_id).eq('joki_id', session['user_id']).single().execute()
    if not service.data:
        flash('Layanan tidak ditemukan.', 'error')
        return redirect(url_for('joki.dashboard'))

    if request.method == 'POST':
        updates = {
            'title': request.form['title'],
            'description': request.form['description'],
            'price': int(request.form['price']),
            'rank_from': request.form.get('rank_from', ''),
            'rank_to': request.form.get('rank_to', ''),
            'is_active': 'is_active' in request.form
        }
        thumbnail = request.files.get('thumbnail')
        if thumbnail and thumbnail.filename:
            updates['thumbnail_url'] = upload_image(thumbnail, folder="service_thumbnails")

        supabase.table('services').update(updates).eq('id', service_id).execute()
        flash('Layanan berhasil diupdate!', 'success')
        return redirect(url_for('joki.dashboard'))

    return render_template('joki/edit_service.html', service=service.data)

@joki_bp.route('/withdraw', methods=['GET', 'POST'])
@joki_required
def withdraw():
    profile = supabase.table('profiles').select('balance').eq('id', session['user_id']).single().execute()
    
    if request.method == 'POST':
        amount = int(request.form['amount'])
        method = request.form['method']
        account_number = request.form['account_number']
        balance = profile.data.get('balance', 0) or 0

        if amount > balance:
            flash('Saldo tidak cukup.', 'error')
        elif amount < 50000:
            flash('Minimum withdraw Rp 50.000.', 'error')
        else:
            supabase.table('withdrawals').insert({
                'joki_id': session['user_id'],
                'amount': amount,
                'method': method,
                'account_number': account_number,
                'status': 'pending'
            }).execute()
            flash('Permintaan withdraw berhasil dikirim!', 'success')
            return redirect(url_for('joki.dashboard'))

    return render_template('joki/withdraw.html', profile=profile.data)

@joki_bp.route('/order/<int:order_id>/accept', methods=['POST'])
@joki_required
def accept_order(order_id):
    supabase.table('orders').update({'status': 'in_progress'}).eq('id', order_id).eq('joki_id', session['user_id']).execute()
    flash('Order diterima! Segera kerjakan.', 'success')
    return redirect(url_for('order.order_detail', order_id=order_id))
