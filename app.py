from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv

# Veritabanı nesnesini models.py'den import ediyoruz.
# Bu, tüm modellerin tek ve doğru SQLAlchemy nesnesine bağlı olmasını sağlar.
# Not: models.py içinde 'db = SQLAlchemy()' olarak tanımlanmış olmalıdır.
from models import db 

def create_app(test_config=None):
    # Ortam değişkenlerini (.env dosyasından) yükle
    load_dotenv()

    # Flask uygulamasını başlat
    app = Flask(__name__)
    
    # --- KONFİGÜRASYON ---
    # os.environ.get() ile .env dosyasından çekiliyor. Anahtarlar .env ile EŞLEŞMELİ.
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///default_db.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if test_config:
        app.config.update(test_config)

    # Uygulama genişletmelerini başlat
    db.init_app(app)
    # CORS ayarları (Tüm kaynaklardan gelen isteklere izin verir)
    CORS(app)

    # Blueprint'i Import Et ve Kaydet
    # Eğer API rotaları dosyanızın adı 'routes.py' ise bu doğru.
    # Eğer 'api.py' ise, 'from api import api_bp' olarak değiştirin.
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
            'version': '1.0.0',
            'endpoints': {
                'children': '/api/children',
                'brushing_records': '/api/children/<child_id>/brushing-records',
                'progress': '/api/children/<child_id>/progress',
                'reminders': '/api/children/<child_id>/reminder-settings',
                'health': '/health'
            }
        })

    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

    return app

if __name__ == '__main__':
    # Uygulama fabrikasını kullanarak uygulamayı oluştur
    app = create_app()
    
    # Veritabanı tablolarını oluşturma ve başlangıç verilerini ekleme
    with app.app_context():
        # db.create_all() öncesinde modelleri tanımlamak için bir modelin import edilmesi gerekir
        # Bu, db'nin hangi tabloları oluşturacağını bilmesini sağlar.
        from models import Parent 

        # Veritabanında tabloları oluştur
        db.create_all()

        # Eğer hiç Parent yoksa, örnek bir ebeveyn oluştur
        if not Parent.query.first():
             # NOT: database.py dosyanızı kullanmak daha iyidir, ancak 
             # hızlı başlangıç için temel bir Parent oluşturuyoruz.
             # Daha fazla başlangıç verisi için database.py'yi çalıştırın.
             print("Veritabanı başlatılıyor...")
             try:
                 parent = Parent(
                     name="Veli Kullanıcı",
                     email="veli@example.com"
                 )
                 # Parola hash'leme ve JWT desteği için Parent modelinin güncellenmesi GEREKİR.
                 # Şimdilik parola olmadan ekliyoruz.
                 db.session.add(parent)
                 db.session.commit()
                 print("Varsayılan Veli Kullanıcı oluşturuldu.")
             except Exception as e:
                 db.session.rollback()
                 print(f"Hata oluştu: {e}")
        else:
            print("Veritabanı zaten başlatılmış (Parent mevcut).")
            
    # Uygulamayı çalıştır
    app.run(debug=True, host='0.0.0.0', port=5000)
