from library import *
from settings import *


# --- MODELS ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='admin')  # master_admin, admin

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class HeadProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    logo_filename = db.Column(db.String(200))
    donation_points = db.relationship('DonationPoint', backref='head_project', lazy=True, cascade="all, delete-orphan")


class DonationPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    head_project_id = db.Column(db.Integer, db.ForeignKey('head_project.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    udise = db.Column(db.String(50))          # UDISE code
    district = db.Column(db.String(100))
    tahsil = db.Column(db.String(100))
    latitude = db.Column(db.String(50))       # School pin GPS
    longitude = db.Column(db.String(50))
    entries = db.relationship('ReceiverEntry', backref='donation_point', lazy=True, cascade="all, delete-orphan")


class ReceiverEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donation_point_id = db.Column(db.Integer, db.ForeignKey('donation_point.id'), nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.now)
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))

    district = db.Column(db.String(100))
    tahsil = db.Column(db.String(100))

    # Product info
    product_name = db.Column(db.String(100))   # e.g. "Nutri Dabba • Kit A"
    meal_count = db.Column(db.Integer)
    receiver_name = db.Column(db.String(100))

    status = db.Column(db.String(50))          # Delivered / Received
    batch_no = db.Column(db.String(50))
    box_count = db.Column(db.Integer)

    is_closed = db.Column(db.String(10))
    closed_location = db.Column(db.String(200))
    delivery_notes = db.Column(db.Text)

    photo_filename = db.Column(db.String(200))
    photo_receiver = db.Column(db.String(200))
    photo_batch = db.Column(db.String(200))
    signature_filename = db.Column(db.String(200))

    # Verification
    verification_status = db.Column(db.String(50), default='Pending')  # Pending / Verified / Flagged / Rejected
    gps_flag = db.Column(db.String(200))       # e.g. "GPS mismatch (1.8 km away)"
    rejection_reason = db.Column(db.Text)
    auditor_notes = db.Column(db.Text)         # Notes from admin audit


# Create tables and seed default admin
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        u = User(username='admin', email='admin@milletsnow.com', role='master_admin')
        u.set_password('admin123')
        db.session.add(u)
        db.session.commit()
