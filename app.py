from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv

# Veritabanı nesnesini models.py'den import ediyoruz.
# Bu, tüm modellerin tek ve doğru SQLAlchemy nesnesine bağlı olmasını sağlar.
from models import db 

# Veritabanı başlangıcı için Parent modelini içe aktarın (create_all için gerekli)
from models import Parent 

# Bu komut, uygulamanın çalışacağı ana fonksiyondur. Gunicorn bunu çağırır.
def create_app(test_config=None):
    # Ortam değişkenlerini (.env dosyasından) yükle
    load_dotenv()

    # Flask uygulamasını başlat
    app = Flask(__name__)
        
    # --- KONFİGÜRASYON ---
    # os.environ.get() ile .env dosyasından çekiliyor (Render'daki Environment Variables kullanılır).
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_URL', os.environ.get('DATABASE_URL'))
    if app.config['SQLALCHEMY_DATABASE_URI'] is None:
        # Eğer DATABASE_URL Render'da ayarlanmamışsa, yerel SQLite'a döner (Geliştirme için)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///default_db.db'
        
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if test_config:
        app.config.update(test_config)

    # Uygulama genişletmelerini başlat
    db.init_app(app)
    # CORS ayarları (Tüm kaynaklardan gelen isteklere izin verir)
    CORS(app)

    # Blueprint'i Import Et ve Kaydet
    try:
        from routes import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
    except ImportError:
        print("UYARI: 'routes.py' bulunamadı. Lütfen API rotalarının doğru dosyada (routes.py veya api.py) olduğundan emin olun.")
        
    # --- TEMEL ROTLAR ---
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

    # Veritabanı tablolarını oluşturma ve başlangıç verilerini ekleme (SADECE Gunicorn başlatıldığında çalışır)
    with app.app_context():
        # Veritabanında tabloları oluştur (Render'da ilk çalıştırmada tabloları oluşturur)
        db.create_all()

        # Eğer hiç Parent yoksa, örnek bir ebeveyn oluştur
        if not Parent.query.first():
            print("Veritabanı başlatılıyor...")
            try:
                parent = Parent(
                    name="Veli Kullanıcı",
                    email="veli@example.com"
                )
                db.session.add(parent)
                db.session.commit()
                print("Varsayılan Veli Kullanıcı oluşturuldu.")
            except Exception as e:
                db.session.rollback()
                print(f"Hata oluştu: {e}")
        else:
            print("Veritabanı zaten başlatılmış (Parent mevcut).")
                    
    return app

# KALDİRİLDİ: if __name__ == '__main__': bloku. Bu, Flask geliştirme sunucusunun çalışmasını engeller.
