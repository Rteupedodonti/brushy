from flask import Blueprint, request, jsonify
from models import db, Parent, Child, BrushingRecord, Reward
from datetime import datetime, timedelta
from sqlalchemy import func

api_bp = Blueprint('api', __name__)

# --- EBEVEYN (PARENT) ROTALARı ---
@api_bp.route('/parents', methods=['GET'])
def get_parents():
    """Tüm ebeveynleri listele"""
    parents = Parent.query.all()
    return jsonify([parent.to_dict() for parent in parents])

@api_bp.route('/parents', methods=['POST'])
def create_parent():
    """Yeni ebeveyn oluştur"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'İsim ve email gerekli'}), 400
    
    # Email kontrolü
    if Parent.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Bu email zaten kullanılıyor'}), 400
    
    parent = Parent(
        name=data['name'],
        email=data['email']
    )
    
    try:
        db.session.add(parent)
        db.session.commit()
        return jsonify(parent.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/parents/<int:parent_id>', methods=['GET'])
def get_parent(parent_id):
    """Belirli bir ebeveynin bilgilerini getir"""
    parent = Parent.query.get_or_404(parent_id)
    return jsonify(parent.to_dict())

# --- ÇOCUK (CHILD) ROTALARı ---
@api_bp.route('/parents/<int:parent_id>/children', methods=['GET'])
def get_children(parent_id):
    """Belirli bir ebeveynin çocuklarını listele"""
    parent = Parent.query.get_or_404(parent_id)
    return jsonify([child.to_dict() for child in parent.children])

@api_bp.route('/parents/<int:parent_id>/children', methods=['POST'])
def create_child(parent_id):
    """Yeni çocuk oluştur"""
    parent = Parent.query.get_or_404(parent_id)
    data = request.get_json()
    
    if not data or 'name' not in data or 'age' not in data:
        return jsonify({'error': 'İsim ve yaş gerekli'}), 400
    
    child = Child(
        name=data['name'],
        age=data['age'],
        parent_id=parent_id
    )
    
    try:
        db.session.add(child)
        db.session.commit()
        return jsonify(child.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/children/<int:child_id>', methods=['GET'])
def get_child(child_id):
    """Belirli bir çocuğun bilgilerini getir"""
    child = Child.query.get_or_404(child_id)
    return jsonify(child.to_dict())

@api_bp.route('/children/<int:child_id>', methods=['PUT'])
def update_child(child_id):
    """Çocuk bilgilerini güncelle"""
    child = Child.query.get_or_404(child_id)
    data = request.get_json()
    
    if 'name' in data:
        child.name = data['name']
    if 'age' in data:
        child.age = data['age']
    
    try:
        db.session.commit()
        return jsonify(child.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# --- FIRÇALAMA KAYITLARI (BRUSHING RECORDS) ROTALARı ---
@api_bp.route('/children/<int:child_id>/brushings', methods=['GET'])
def get_brushing_records(child_id):
    """Çocuğun fırçalama kayıtlarını listele"""
    child = Child.query.get_or_404(child_id)
    
    # Tarih filtreleme (isteğe bağlı)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = BrushingRecord.query.filter_by(child_id=child_id)
    
    if start_date:
        query = query.filter(BrushingRecord.brushed_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(BrushingRecord.brushed_at <= datetime.fromisoformat(end_date))
    
    records = query.order_by(BrushingRecord.brushed_at.desc()).all()
    return jsonify([record.to_dict() for record in records])

@api_bp.route('/children/<int:child_id>/brushings', methods=['POST'])
def create_brushing_record(child_id):
    """Yeni fırçalama kaydı oluştur"""
    child = Child.query.get_or_404(child_id)
    data = request.get_json()
    
    record = BrushingRecord(
        child_id=child_id,
        duration=data.get('duration', 120),
        quality_score=data.get('quality_score', 5),
        notes=data.get('notes', '')
    )
    
    # Eğer belirli bir tarih verilmişse
    if 'brushed_at' in data:
        record.brushed_at = datetime.fromisoformat(data['brushed_at'])
    
    try:
        db.session.add(record)
        db.session.commit()
        return jsonify(record.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/brushings/<int:record_id>', methods=['PUT'])
def update_brushing_record(record_id):
    """Fırçalama kaydını güncelle"""
    record = BrushingRecord.query.get_or_404(record_id)
    data = request.get_json()
    
    if 'duration' in data:
        record.duration = data['duration']
    if 'quality_score' in data:
        record.quality_score = data['quality_score']
    if 'notes' in data:
        record.notes = data['notes']
    
    try:
        db.session.commit()
        return jsonify(record.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/brushings/<int:record_id>', methods=['DELETE'])
def delete_brushing_record(record_id):
    """Fırçalama kaydını sil"""
    record = BrushingRecord.query.get_or_404(record_id)
    
    try:
        db.session.delete(record)
        db.session.commit()
        return jsonify({'message': 'Kayıt silindi'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# --- İSTATİSTİKLER ---
@api_bp.route('/children/<int:child_id>/stats', methods=['GET'])
def get_child_stats(child_id):
    """Çocuğun fırçalama istatistiklerini getir"""
    child = Child.query.get_or_404(child_id)
    
    # Son 30 günün kayıtları
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_records = BrushingRecord.query.filter(
        BrushingRecord.child_id == child_id,
        BrushingRecord.brushed_at >= thirty_days_ago
    ).all()
    
    # Son 7 günün kayıtları
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    week_records = [r for r in recent_records if r.brushed_at >= seven_days_ago]
    
    # İstatistikler
    stats = {
        'total_brushings': len(child.brushing_records),
        'last_30_days': len(recent_records),
        'last_7_days': len(week_records),
        'average_duration': sum(r.duration for r in recent_records) / len(recent_records) if recent_records else 0,
        'average_quality': sum(r.quality_score for r in recent_records) / len(recent_records) if recent_records else 0,
        'streak_days': calculate_streak(child_id),
        'last_brushing': recent_records[0].to_dict() if recent_records else None
    }
    
    return jsonify(stats)

def calculate_streak(child_id):
    """Çocuğun günlük fırçalama serisini hesapla"""
    today = datetime.utcnow().date()
    streak = 0
    current_date = today
    
    while True:
        # Bu günün fırçalama kaydı var mı?
        daily_record = BrushingRecord.query.filter(
            BrushingRecord.child_id == child_id,
            func.date(BrushingRecord.brushed_at) == current_date
        ).first()
        
        if daily_record:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak

# --- ÖDÜLLER (REWARDS) ---
@api_bp.route('/children/<int:child_id>/rewards', methods=['GET'])
def get_rewards(child_id):
    """Çocuğun ödüllerini listele"""
    child = Child.query.get_or_404(child_id)
    rewards = Reward.query.filter_by(child_id=child_id).all()
    return jsonify([reward.to_dict() for reward in rewards])

@api_bp.route('/children/<int:child_id>/rewards', methods=['POST'])
def create_reward(child_id):
    """Yeni ödül oluştur"""
    child = Child.query.get_or_404(child_id)
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Ödül başlığı gerekli'}), 400
    
    reward = Reward(
        child_id=child_id,
        title=data['title'],
        description=data.get('description', ''),
        points_required=data.get('points_required', 10)
    )
    
    try:
        db.session.add(reward)
        db.session.commit()
        return jsonify(reward.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/rewards/<int:reward_id>/claim', methods=['POST'])
def claim_reward(reward_id):
    """Ödülü kazandı olarak işaretle"""
    reward = Reward.query.get_or_404(reward_id)
    
    if reward.is_earned:
        return jsonify({'error': 'Bu ödül zaten kazanılmış'}), 400
    
    # Çocuğun puan kontrolü (basit hesaplama: her fırçalama = 1 puan)
    child_points = len(reward.child.brushing_records)
    
    if child_points < reward.points_required:
        return jsonify({
            'error': 'Yetersiz puan',
            'required': reward.points_required,
            'current': child_points
        }), 400
    
    reward.is_earned = True
    reward.earned_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify(reward.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
