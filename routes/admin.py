from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from supabase_client import supabase
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Akses ditolak.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_orders = supabase.table('orders').select('id', count='exact').execute()
    pending_payments = supabase.table('orders').select('id', count='exact').eq('status', 'pending_verification').execute()
    pending_withdrawals = supabase.table('withdrawals').select('id', count='exact').eq('status', 'pending').execute()
    total_users = supabase.table('profiles').select('id', count='exact').execute()
    recent_orders = supabase.table('orders').select('*').order('created_at', desc=True).limit(10).execute()
    completed = supabase.table('orders').select('commission').eq('status', 'completed').execute()
    revenue = sum(o['commission'] for o in (completed.data or []))

    return render_template('admin/dashboard.html',
        total_orders=total_orders.count or 0,
        pending_payments=pending_payments.count or 0,
        pending_withdrawals=pending_withdrawals.count or 0,
        total_users=total_users.count or 0,
        recent_orders=recent_orders.data or [],
        revenue=revenue
    )

@admin_bp.route('/payments')
@admin_required
def payments():
    orders = supabase.table('orders').select('*').eq('status', 'pending_verification').order('created_at', desc=True).execute()
    return render_template('admin/payments.html', orders=orders.data or [])

@admin_bp.route('/payment/<int:order_id>/approve', methods=['POST'])
@admin_required
def approve_payment(order_id):
    supabase.table('orders').update({'status': 'active'}).eq('id', order_id).execute()
    flash('Pembayaran diverifikasi! Order aktif.', 'success')
    return redirect(url_for('admin.payments'))

@admin_bp.route('/payment/<int:order_id>/reject', methods=['POST'])
@admin_required
def reject_payment(order_id):
    reason = request.form.get('reason', 'Bukti pembayaran tidak valid')
    supabase.table('orders').update({'status': 'payment_rejected', 'reject_reason': reason}).eq('id', order_id).execute()
    flash('Pembayaran ditolak.', 'success')
    return redirect(url_for('admin.payments'))

@admin_bp.route('/withdrawals')
@admin_required
def withdrawals():
    wds = supabase.table('withdrawals').select('*').eq('status', 'pending').order('created_at', desc=True).execute()
    return render_template('admin/withdrawals.html', withdrawals=wds.data or [])

@admin_bp.route('/withdrawal/<int:wd_id>/approve', methods=['POST'])
@admin_required
def approve_withdrawal(wd_id):
    wd = supabase.table('withdrawals').select('*').eq('id', wd_id).single().execute()
    if wd.data:
        joki_id = wd.data['joki_id']
        amount = wd.data['amount']
        profile = supabase.table('profiles').select('balance').eq('id', joki_id).single().execute()
        new_balance = max(0, (profile.data.get('balance', 0) or 0) - amount)
        supabase.table('profiles').update({'balance': new_balance}).eq('id', joki_id).execute()
        supabase.table('withdrawals').update({'status': 'approved'}).eq('id', wd_id).execute()
        flash('Withdraw disetujui!', 'success')
    return redirect(url_for('admin.withdrawals'))

@admin_bp.route('/withdrawal/<int:wd_id>/reject', methods=['POST'])
@admin_required
def reject_withdrawal(wd_id):
    supabase.table('withdrawals').update({'status': 'rejected'}).eq('id', wd_id).execute()
    flash('Withdraw ditolak.', 'success')
    return redirect(url_for('admin.withdrawals'))

@admin_bp.route('/joki')
@admin_required
def manage_joki():
    joki_list = supabase.table('profiles').select('*').eq('role', 'joki').order('created_at', desc=True).execute()
    return render_template('admin/joki.html', joki_list=joki_list.data or [])

@admin_bp.route('/joki/<joki_id>/verify', methods=['POST'])
@admin_required
def verify_joki(joki_id):
    supabase.table('profiles').update({'is_verified': True}).eq('id', joki_id).execute()
    flash('Joki berhasil diverifikasi!', 'success')
    return redirect(url_for('admin.manage_joki'))

@admin_bp.route('/orders')
@admin_required
def all_orders():
    status = request.args.get('status', '')
    query = supabase.table('orders').select('*')
    if status:
        query = query.eq('status', status)
    orders = query.order('created_at', desc=True).execute()
    return render_template('admin/orders.html', orders=orders.data or [], selected_status=status)
