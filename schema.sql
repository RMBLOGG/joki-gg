-- ============================================
-- JokiGG - Supabase SQL Schema
-- Jalankan di Supabase SQL Editor
-- ============================================

-- PROFILES (extend auth.users)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    username TEXT UNIQUE NOT NULL,
    role TEXT DEFAULT 'buyer' CHECK (role IN ('buyer', 'joki', 'admin')),
    avatar_url TEXT,
    bio TEXT,
    balance INTEGER DEFAULT 0,
    rating_avg DECIMAL(3,1) DEFAULT 5.0,
    total_orders INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- GAME CATEGORIES
CREATE TABLE IF NOT EXISTS game_categories (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    icon TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Default categories
INSERT INTO game_categories (name, icon) VALUES
    ('Mobile Legends', '⚔️'),
    ('PUBG Mobile', '🔫'),
    ('Valorant', '🎯'),
    ('Genshin Impact', '🌟'),
    ('Free Fire', '🔥'),
    ('Wuthering Waves', '🌊'),
    ('Honkai Star Rail', '🚂'),
    ('League of Legends', '🏆')
ON CONFLICT (name) DO NOTHING;

-- SERVICES (layanan joki)
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    joki_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    game_name TEXT NOT NULL,
    service_type TEXT NOT NULL,
    price INTEGER NOT NULL,
    rank_from TEXT,
    rank_to TEXT,
    thumbnail_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ORDERS
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    buyer_id UUID NOT NULL REFERENCES profiles(id),
    joki_id UUID NOT NULL REFERENCES profiles(id),
    service_id INTEGER NOT NULL REFERENCES services(id),
    price INTEGER NOT NULL,
    commission INTEGER NOT NULL,
    joki_earning INTEGER NOT NULL,
    status TEXT DEFAULT 'pending_payment' CHECK (status IN (
        'pending_payment', 'pending_verification', 'payment_rejected',
        'active', 'in_progress', 'waiting_confirmation', 'completed', 'cancelled'
    )),
    notes TEXT,
    game_account TEXT,
    game_password TEXT,
    rank_target TEXT,
    payment_proof_url TEXT,
    payment_method TEXT,
    reject_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- REVIEWS
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    order_id INTEGER UNIQUE REFERENCES orders(id),
    buyer_id UUID REFERENCES profiles(id),
    joki_id UUID REFERENCES profiles(id),
    service_id INTEGER REFERENCES services(id),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- WITHDRAWALS
CREATE TABLE IF NOT EXISTS withdrawals (
    id SERIAL PRIMARY KEY,
    joki_id UUID NOT NULL REFERENCES profiles(id),
    amount INTEGER NOT NULL,
    method TEXT NOT NULL,
    account_number TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- SET ADMIN (ganti dengan email admin kamu)
-- Jalankan setelah register akun admin pertama
-- ============================================
-- UPDATE profiles SET role = 'admin' WHERE email = 'admin@emailkamu.com';

-- RLS POLICIES (opsional tapi direkomendasikan)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE services ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE withdrawals ENABLE ROW LEVEL SECURITY;

-- Allow public read for profiles and services
CREATE POLICY "Public profiles" ON profiles FOR SELECT USING (true);
CREATE POLICY "Public services" ON services FOR SELECT USING (is_active = true);
CREATE POLICY "Public reviews" ON reviews FOR SELECT USING (true);
CREATE POLICY "Public categories" ON game_categories FOR SELECT USING (true);
