from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from supabase_client import supabase
from cloudinary_helper import upload_image
from functools import wraps

order_bp = Blueprint('order', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@order_bp.route('/order/<int:service_id>', methods=['GET', 'POST'])
@login_required
def create_order(service_id):
    service = supabase.table('services').select('*, profiles(username, avatar_url)').eq('id', service_id).single().execute()
    
    if not service.data:
        flash('Layanan tidak ditemukan.', 'error')
        return redirect(url_for('main.browse'))

    if request.method == 'POST':
        notes = request.form.get('notes', '')
        game_account = request.form.get('game_account', '')
        game_password = request.form.get('game_password', '')
        rank_target = request.form.get('rank_target', '')
        
        svc = service.data
        price = svc['price']
        commission = round(price * 0.15)
        joki_earning = price - commission

        # Create order
        order = supabase.table('orders').insert({
            'buyer_id': session['user_id'],
            'joki_id': svc['joki_id'],
            'service_id': service_id,
            'price': price,
            'commission': commission,
            'joki_earning': joki_earning,
            'notes': notes,
            'game_account': game_account,
            'game_password': game_password,
            'rank_target': rank_target,
            'status': 'pending_payment'
        }).execute()

        if order.data:
            order_id = order.data[0]['id']
            flash('Order berhasil dibuat! Silakan lakukan pembayaran.', 'success')
            return redirect(url_for('order.payment', order_id=order_id))

    return render_template('order/create.html', service=service.data)

@order_bp.route('/order/<int:order_id>/payment', methods=['GET', 'POST'])
@login_required
def payment(order_id):
    order = supabase.table('orders').select('*, services(title, game_name), profiles!orders_joki_id_fkey(username)').eq('id', order_id).eq('buyer_id', session['user_id']).single().execute()
    
    if not order.data:
        flash('Order tidak ditemukan.', 'error')
        return redirect(url_for('order.my_orders'))

    if request.method == 'POST':
        payment_proof = request.files.get('payment_proof')
        payment_method = request.form.get('payment_method')

        if payment_proof:
            proof_url = upload_image(payment_proof, folder="payment_proofs")
            supabase.table('orders').update({
                'status': 'pending_verification',
                'payment_proof_url': proof_url,
                'payment_method': payment_method
            }).eq('id', order_id).execute()
            flash('Bukti pembayaran berhasil dikirim! Menunggu verifikasi admin.', 'success')
            return redirect(url_for('order.order_detail', order_id=order_id))

    return render_template('order/payment.html', order=order.data)

@order_bp.route('/orders')
@login_required
def my_orders():
    role = session.get('role', 'buyer')
    if role == 'joki':
        orders = supabase.table('orders').select('*, services(title, game_name), profiles!orders_buyer_id_fkey(username)').eq('joki_id', session['user_id']).order('created_at', desc=True).execute()
    else:
        orders = supabase.table('orders').select('*, services(title, game_name), profiles!orders_joki_id_fkey(username)').eq('buyer_id', session['user_id']).order('created_at', desc=True).execute()
    
    return render_template('order/my_orders.html', orders=orders.data or [], role=role)

@order_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = supabase.table('orders').select('*, services(title, game_name, price), profiles!orders_joki_id_fkey(username, avatar_url), profiles!orders_buyer_id_fkey(username)').eq('id', order_id).single().execute()
    return render_template('order/detail.html', order=order.data)

@order_bp.route('/order/<int:order_id>/complete', methods=['POST'])
@login_required
def complete_order(order_id):
    # Joki marks order as done
    supabase.table('orders').update({'status': 'waiting_confirmation'}).eq('id', order_id).eq('joki_id', session['user_id']).execute()
    flash('Order ditandai selesai. Menunggu konfirmasi buyer.', 'success')
    return redirect(url_for('order.order_detail', order_id=order_id))

@order_bp.route('/order/<int:order_id>/confirm', methods=['POST'])
@login_required
def confirm_order(order_id):
    order = supabase.table('orders').select('*').eq('id', order_id).eq('buyer_id', session['user_id']).single().execute()
    if order.data:
        # Release payment to joki
        joki_id = order.data['joki_id']
        joki_earning = order.data['joki_earning']
        
        supabase.table('orders').update({'status': 'completed'}).eq('id', order_id).execute()
        
        # Add balance to joki
        joki_profile = supabase.table('profiles').select('balance').eq('id', joki_id).single().execute()
        new_balance = (joki_profile.data.get('balance', 0) or 0) + joki_earning
        supabase.table('profiles').update({'balance': new_balance}).eq('id', joki_id).execute()

        flash('Order selesai! Saldo joki telah ditransfer.', 'success')
    return redirect(url_for('order.order_detail', order_id=order_id))

@order_bp.route('/order/<int:order_id>/review', methods=['POST'])
@login_required
def submit_review(order_id):
    order = supabase.table('orders').select('*').eq('id', order_id).eq('buyer_id', session['user_id']).single().execute()
    if order.data and order.data['status'] == 'completed':
        rating = int(request.form.get('rating', 5))
        comment = request.form.get('comment', '')
        
        supabase.table('reviews').insert({
            'order_id': order_id,
            'buyer_id': session['user_id'],
            'joki_id': order.data['joki_id'],
            'service_id': order.data['service_id'],
            'rating': rating,
            'comment': comment
        }).execute()

        # Update avg rating joki
        reviews = supabase.table('reviews').select('rating').eq('joki_id', order.data['joki_id']).execute()
        if reviews.data:
            avg = sum(r['rating'] for r in reviews.data) / len(reviews.data)
            supabase.table('profiles').update({'rating_avg': round(avg, 1)}).eq('id', order.data['joki_id']).execute()

        flash('Review berhasil dikirim!', 'success')
    return redirect(url_for('order.order_detail', order_id=order_id))
