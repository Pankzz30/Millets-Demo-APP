from app import app, db
from models import HeadProject, DonationPoint, ReceiverEntry, User
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash

with app.app_context():
    # Clear existing data
    ReceiverEntry.query.delete()
    DonationPoint.query.delete()
    HeadProject.query.delete()
    User.query.delete()
    db.session.commit()

    # Create admin user
    admin = User(username='admin', email='admin@example.com', password_hash=generate_password_hash('admin123'))
    db.session.add(admin)
    db.session.commit()

    # Create projects
    projects = [
        HeadProject(name="Nutri Pathshala • Phase II", description="Primary rural education nutrition program covering 50+ schools in the Pune district."),
        HeadProject(name="Mid-Day Meal Initiative", description="Government-backed nutrition program for school children."),
        HeadProject(name="Community Nutrition Drive", description="Local community supported meal distribution."),
    ]
    for p in projects:
        db.session.add(p)
    db.session.commit()

    # Sample schools data
    schools_data = [
        {"name": "ZP School Aundh", "district": "Pune", "tahsil": "Haveli", "lat": 18.5606, "lng": 73.7987, "udise": "27250100101"},
        {"name": "ZP School Baner", "district": "Pune", "tahsil": "Haveli", "lat": 18.5545, "lng": 73.7868, "udise": "27250100202"},
        {"name": "ZP School Hinjawadi", "district": "Pune", "tahsil": "Mulshi", "lat": 18.5913, "lng": 73.7388, "udise": "27250100303"},
        {"name": "ZP School Wakad", "district": "Pune", "tahsil": "Mulshi", "lat": 18.5994, "lng": 73.7626, "udise": "27250100404"},
        {"name": "ZP School Pimpri", "district": "Pune", "tahsil": "Haveli", "lat": 18.6298, "lng": 73.7997, "udise": "27250100505"},
        {"name": "ZP School Chakan", "district": "Pune", "tahsil": "Khed", "lat": 18.7606, "lng": 73.8635, "udise": "27250100606"},
        {"name": "ZP School Talegaon", "district": "Pune", "tahsil": "Maval", "lat": 18.7378, "lng": 73.6756, "udise": "27250100707"},
        {"name": "ZP School Lonavala", "district": "Pune", "tahsil": "Maval", "lat": 18.7528, "lng": 73.4056, "udise": "27250100808"},
        {"name": "ZP School Khed", "district": "Pune", "tahsil": "Khed", "lat": 18.7156, "lng": 73.7897, "udise": "27250100909"},
        {"name": "ZP School Junnar", "district": "Pune", "tahsil": "Junnar", "lat": 19.2081, "lng": 73.8756, "udise": "27250101010"},
    ]

    points = []
    for school in schools_data:
        point = DonationPoint(
            head_project_id=random.choice([p.id for p in projects]),
            name=school["name"],
            location=f"{school['district']}, {school['tahsil']}",
            udise=school["udise"],
            district=school["district"],
            tahsil=school["tahsil"],
            latitude=str(school["lat"]),
            longitude=str(school["lng"])
        )
        db.session.add(point)
        points.append(point)
    db.session.commit()

    # Generate sample entries
    products = ["Ragi Porridge", "Jowar Khichdi", "Bajra Flatbread", "Foxtail Millet Upma", "Standard Meal Kit"]
    statuses = ["Verified", "Pending", "Flagged", "Rejected"]

    for i in range(200):
        point = random.choice(points)
        days_ago = random.randint(0, 30)
        timestamp = datetime.now() - timedelta(days=days_ago, hours=random.randint(8, 16))
        
        entry = ReceiverEntry(
            donation_point_id=point.id,
            timestamp=timestamp,
            latitude=str(float(point.latitude) + random.uniform(-0.01, 0.01)),
            longitude=str(float(point.longitude) + random.uniform(-0.01, 0.01)),
            district=point.district,
            tahsil=point.tahsil,
            product_name=random.choice(products),
            meal_count=random.randint(50, 200),
            verification_status=random.choices(statuses, weights=[70, 20, 7, 3])[0]
        )
        db.session.add(entry)
    
    db.session.commit()
    print("Demo data seeded successfully!")