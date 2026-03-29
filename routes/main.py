from flask import Blueprint, render_template, request, session
from supabase_client import supabase

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Get all active services
    services = supabase.table('services').select('*, profiles(username, avatar_url, rating_avg)').eq('is_active', True).order('created_at', desc=True).execute()
    
    # Get game categories
    categories = supabase.table('game_categories').select('*').execute()
    
    # Get top joki
    top_joki = supabase.table('profiles').select('*').eq('role', 'joki').eq('is_verified', True).order('rating_avg', desc=True).limit(6).execute()

    return render_template('main/index.html',
        services=services.data or [],
        categories=categories.data or [],
        top_joki=top_joki.data or []
    )

@main_bp.route('/browse')
def browse():
    game = request.args.get('game', '')
    service_type = request.args.get('type', '')
    
    query = supabase.table('services').select('*, profiles(username, avatar_url, rating_avg)').eq('is_active', True)
    if game:
        query = query.eq('game_name', game)
    if service_type:
        query = query.eq('service_type', service_type)
    
    services = query.order('created_at', desc=True).execute()
    categories = supabase.table('game_categories').select('*').execute()
    
    return render_template('main/browse.html',
        services=services.data or [],
        categories=categories.data or [],
        selected_game=game
    )

@main_bp.route('/service/<int:service_id>')
def service_detail(service_id):
    service = supabase.table('services').select('*, profiles(username, avatar_url, rating_avg, total_orders, bio)').eq('id', service_id).single().execute()
    reviews = supabase.table('reviews').select('*, profiles(username, avatar_url)').eq('service_id', service_id).order('created_at', desc=True).limit(10).execute()
    
    return render_template('main/service_detail.html',
        service=service.data,
        reviews=reviews.data or []
    )

@main_bp.route('/joki/<joki_id>')
def joki_profile(joki_id):
    profile = supabase.table('profiles').select('*').eq('id', joki_id).single().execute()
    services = supabase.table('services').select('*').eq('joki_id', joki_id).eq('is_active', True).execute()
    reviews = supabase.table('reviews').select('*, profiles(username)').eq('joki_id', joki_id).order('created_at', desc=True).limit(5).execute()
    
    return render_template('main/joki_profile.html',
        profile=profile.data,
        services=services.data or [],
        reviews=reviews.data or []
    )

@main_bp.route('/ads.txt')
def ads_txt():
    return 'google.com, pub-3673996314713788, DIRECT, f08c47fec0942fa0', 200, {'Content-Type': 'text/plain'}
