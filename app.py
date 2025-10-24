# Kütüphane İçe Aktarımları
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv

# Veritabanı model ve nesneleri
# NOT: models.py içinde db, Parent olmalı.
from models import db, Parent 

# --- create_app FONKSİYONU ---
def create_app(test_config=None, **kwargs):
    # Ortam değişkenlerini (.env dosyasından) yükle
    load_dotenv()

    # Flask uygulamasını başlat
    app = Flask(__name__)
    
    # --- KONFİGÜRASYON ---
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

    # Blueprint'i Import Et ve Kaydet (API rotalarını yükleyen kısım DÜZELTİLDİ)
    # Dosya listesine göre 'routes.py' kullanılıyor olmalı.
    try:
        # routes.py dosyasından 'api_bp' objesini içe aktar
        from routes import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
        print("API Blueprint (routes.py) başarıyla yüklendi.")
    except ImportError as e:
        print(f"KRİTİK HATA: Rota (Blueprint) yüklenemedi. routes.py dosyasında 'api_bp' objesi yok veya başka bir ithalat hatası var. Hata: {e}")
    
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
                # utils.py dosyasında hash_password fonksiyonu olmalı
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
            except ImportError:
                 print("UYARI: utils.py dosyasında hash_password fonksiyonu bulunamadı. Kullanıcı şifresiz kaydedildi.")
                 # utils.py bulunamazsa şifresiz kaydet
                 parent = Parent(
                    name="Gamze Test Kullanıcısı",
                    email="gamze@example.com",
                 )
                 db.session.add(parent)
                 db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Veritabanı başlangıç hatası: {e}")
        else:
            print("Veritabanı zaten başlatılmış (Parent mevcut).")
            
    return app

# WSGI SUNUCUSU GİRİŞ NOKTASI
# 'uwsgi --module app:app' komutunun aradığı 'app' objesi oluşturulur.
app = create_app()

if __name__ == '__main__':
    # Yerel geliştirme için (python app.py çalıştırıldığında)
    app.run(debug=True, host='0.0.0.0')
