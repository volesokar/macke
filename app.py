from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import json

app = Flask(__name__)
CORS(app)

# Genel HTTP isteği için ortak başlıklar
HEADERS = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "tr-TR,tr;q=0.9",
    "origin": "https://1xlite-900665.top/",
    "referer": "https://1xlite-900665.top/",
    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

@app.route('/getm3u8', methods=['GET'])
def get_m3u8():
    """Hedef siteden .m3u8 dosyasını alır."""
    source = request.args.get("source")
    videoid = request.args.get("videoid")
    
    if not source:
        return jsonify({"error": "Source parametresi eksik!"}), 400

    # URL düzenleme işlemleri
    source = source.replace('%2F', '/').replace('%3F', '?')
    
    try:
        # Hedef URL'yi indir
        response = requests.get(source, headers=HEADERS)
        if response.status_code == 200:
            tsal = response.text
            # Video ID bazlı URL dönüşümleri
            tsal = tsal.replace(
                f"{videoid}_",
                f"https://sea-lion-app-mx8cy.ondigitalocean.app/getstream?param=getts&source=https://edge10.xmediaget.com/hls-live/{videoid}/1/{videoid}_"
            )
            return tsal
        else:
            return jsonify({"error": f"Hedef URL isteğinde hata: {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": f"İşlem sırasında hata oluştu: {str(e)}"}), 500

@app.route('/getstream', methods=['GET'])
def get_stream():
    """Hedef dosya akışını döndürür."""
    param = request.args.get("param")
    source = request.args.get("source")
    
    if param == "getts" and source:
        source = source.replace('%2F', '/').replace('%3F', '?')
        try:
            # Akış isteği
            response = requests.get(source, headers=HEADERS, stream=True)
            return response.content, response.status_code, {'Content-Type': 'application/octet-stream'}
        except Exception as e:
            return jsonify({"error": f"Akış sırasında hata oluştu: {str(e)}"}), 500
    else:
        return jsonify({"error": "Geçersiz parametreler!"}), 400

@app.route('/getvideo', methods=['POST'])
def get_video():
    """Hedef siteden video bilgisi alır ve uygun URL'yi döner."""
    videoid = request.json.get("videoid")
    
    if not videoid:
        return jsonify({"error": "Video ID eksik!"}), 400
    
    payload = {
        "AppId": "3",
        "AppVer": "1025",
        "VpcVer": "1.0.12",
        "Language": "tr",
        "Token": "",
        "VideoId": videoid
    }

    try:
        # Hedef siteye POST isteği
        response = requests.post("https://1xlite-900665.top/cinema", json=payload, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("FullscreenAllowed"):
                url = data.get("URL", "").replace("\\/", "/")
                return jsonify({"url": url})
            else:
                return jsonify({"error": "Erişim engellendi!"}), 403
        else:
            return jsonify({"error": f"API isteği başarısız: {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": f"İşlem sırasında hata oluştu: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
