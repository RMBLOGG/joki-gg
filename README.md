# JokiGG - Marketplace Joki Game

Platform joki game terpercaya untuk Mobile Legends, PUBG, Valorant, Genshin Impact, dan 20+ game lainnya.

## Stack
- **Backend**: Flask (Python)
- **Database**: Supabase (PostgreSQL)
- **Storage**: Cloudinary (upload gambar)
- **Deploy**: Vercel

## Setup

### 1. Supabase
- Buka Supabase SQL Editor
- Jalankan semua isi `schema.sql`
- Setelah daftar akun admin, jalankan:
  ```sql
  UPDATE profiles SET role = 'admin' WHERE email = 'email_admin_kamu@gmail.com';
  ```

### 2. Environment Variables (Vercel)
Set di Vercel Dashboard → Settings → Environment Variables:
```
SECRET_KEY=random_string_panjang
SUPABASE_SERVICE_KEY=your_service_role_key
```

### 3. Deploy ke Vercel
```bash
npm i -g vercel
vercel --prod
```

## Alur Order
1. Buyer cari layanan → buat order
2. Buyer upload bukti transfer
3. Admin verifikasi pembayaran → order aktif
4. Joki terima order → kerjakan
5. Joki tandai selesai
6. Buyer konfirmasi → saldo joki bertambah
7. Joki withdraw → admin approve & transfer manual

## Monetisasi
Platform mengambil komisi **15%** dari setiap transaksi.
Contoh: Order Rp 100.000 → Platform dapat Rp 15.000, Joki dapat Rp 85.000

## Struktur Folder
```
jokigg/
├── app.py              # Entry point
├── config.py           # Konfigurasi
├── supabase_client.py  # Supabase helper
├── cloudinary_helper.py # Cloudinary helper
├── requirements.txt
├── vercel.json
├── schema.sql          # Jalankan di Supabase
└── routes/
    ├── auth.py         # Login, register, logout
    ├── main.py         # Homepage, browse, detail
    ├── order.py        # Buat order, bayar, review
    ├── joki.py         # Dashboard joki, layanan, withdraw
    └── admin.py        # Dashboard admin
└── templates/
    ├── base.html
    ├── auth/
    ├── main/
    ├── order/
    ├── joki/
    └── admin/
```
