# Kütüphane İçe Aktarımları
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv

# Veritabanı model ve nesneleri
from models import db, Parent 

# --- create_app FONKSİYONU ---
# Bu, Flask uygulama örneğini oluşturan ve yapılandıran ana fonksiyondur.
# **kwargs argümanı, Render gibi dağıtım ortamlarının gönderdiği fazladan argümanları
# sorunsuz bir şekilde kabul etmesini sağlar.
def create_app(test_config=None, **kwargs):
    # Ortam değişkenlerini (.env dosyasından) yükle
    load_dotenv()

    # Flask uygulamasını başlat
    app = Flask(__name__)
    
    # --- KONFİGÜRASYON ---
    # Ortam değişkenlerini os.environ.get() ile çekiyoruz.
    # DATABASE_URL, Render veya Neon/Supabase bağlantısı için zorunludur.
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    
    if app.config['SQLALCHEMY_DATABASE_URI'] is None:
        # Eğer DATABASE_URL ayarlanmamışsa, yerel SQLite'a döner (Yerel Geliştirme için)
        print("UYARI: DATABASE_URL ayarlanmadı, yerel SQLite veritabanı kullanılıyor.")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///default_db.db'
        
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if test_config:
        app.config.update(test_config)

    # Uygulama genişletmelerini başlat
    db.init_app(app)
    # CORS ayarları
    CORS(app)

    # Blueprint'i Import Et ve Kaydet
    try:
        # api.py dosyasını kullanıyoruz (routes.py yerine)
        from api import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
    except ImportError:
        print("KRİTİK HATA: 'api.py' veya içindeki 'api_bp' bulunamadı. Lütfen kontrol edin.")
    
    # --- TEMEL ROTLAR (Sağlık Kontrolü) ---
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Çocuk Diş Fırçalama Takip API',
            'environment': 'Production Ready',
            'timestamp': datetime.utcnow().isoformat()
        })

    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

    # Veritabanı başlatma ve tabloları oluşturma
    # Bu blok sadece uygulama başlatıldığında bir kez çalışır.
    with app.app_context():
        # Tabloları oluştur
        db.create_all()

        # Varsayılan kullanıcıyı kontrol et ve ekle
        if not Parent.query.first():
            print("Veritabanı başlatılıyor... Varsayılan Kullanıcı oluşturuluyor.")
            try:
                # Varsayılan kullanıcıyı hashlenmiş bir şifre ile ekleyelim (Güvenlik)
                from utils import hash_password 
                
                # Bu kullanıcı giriş yapma hatasını test ettiğiniz kullanıcıydı.
                hashed_password = hash_password("cokgizlisifre123") 
                
                parent = Parent(
                    name="Gamze Test Kullanıcısı",
                    email="gamze@example.com",
                    password_hash=hashed_password
                )
                db.session.add(parent)
                db.session.commit()
                print("Varsayılan Veli Kullanıcı (gamze@example.com) başarıyla oluşturuldu.")
            except Exception as e:
                db.session.rollback()
                print(f"Veritabanı başlangıç hatası: {e}")
        else:
            print("Veritabanı zaten başlatılmış (Parent mevcut).")
            
    return app

# WSGI SUNUCUSU GİRİŞ NOKTASI
# Bu, uWSGI/Gunicorn sunucularının uygulamayı başlatmak için aradığı yerdir.
# Flask'ta yaygın uygulama ismi "app" veya "application"dır.
# Biz, Render'daki başlangıç komutumuz olan 'uwsgi --module app:app' ile uyumlu olması için
# 'app' değişkenini kullanıyoruz.
app = create_app()

if __name__ == '__main__':
    # Yerel geliştirme için (python app.py çalıştırıldığında)
    app.run(debug=True, host='0.0.0.0')
