from library import *
from settings import *
from models import *


# --- AUTH DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two GPS coords."""
    try:
        R = 6371
        dlat = math.radians(float(lat2) - float(lat1))
        dlon = math.radians(float(lon2) - float(lon1))
        a = math.sin(dlat/2)**2 + math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) * math.sin(dlon/2)**2
        return R * 2 * math.asin(math.sqrt(a))
    except Exception:
        return None


# --- AUTH ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
def landing():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')


# --- DASHBOARD ---
@app.route('/dashboard')
@login_required
def dashboard():
    projects = HeadProject.query.all()
    all_points = DonationPoint.query.all()
    all_entries = ReceiverEntry.query.all()

    schools_covered = len(all_points)
    meals_delivered = sum(e.meal_count or 0 for e in all_entries if e.verification_status == 'Verified')
    pending_verifications = ReceiverEntry.query.filter_by(verification_status='Pending').count()
    students_reached = int(meals_delivered * 0.55)  # estimate

    # Overdue: schools with no entry in last 30 days
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=30)
    overdue = 0
    for pt in all_points:
        if not pt.entries or max(e.timestamp for e in pt.entries) < cutoff:
            overdue += 1

    recent_entries = ReceiverEntry.query.order_by(ReceiverEntry.timestamp.desc()).limit(10).all()

    return render_template('dashboard.html',
        projects=projects,
        schools_covered=schools_covered,
        meals_delivered=meals_delivered,
        pending_verifications=pending_verifications,
        students_reached=students_reached,
        overdue_schools=overdue,
        recent_entries=recent_entries
    )


# --- PROJECTS ---
@app.route('/projects')
@login_required
def projects_page():
    projects = HeadProject.query.all()
    return render_template('projects.html', projects=projects)


@app.route('/head-project/create', methods=['POST'])
@login_required
def create_head_project():
    name = request.form.get('name')
    desc = request.form.get('description')
    logo = None
    if 'logo' in request.files:
        f = request.files['logo']
        if f.filename:
            logo = secure_filename(f"{datetime.now().timestamp()}_{f.filename}")
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], logo))
    if name:
        db.session.add(HeadProject(name=name, description=desc, logo_filename=logo))
        db.session.commit()
    return redirect(url_for('projects_page'))


@app.route('/head-project/<int:hp_id>/update', methods=['POST'])
@login_required
def update_head_project(hp_id):
    project = HeadProject.query.get_or_404(hp_id)
    project.name = request.form.get('name')
    project.description = request.form.get('description')
    db.session.commit()
    return redirect(url_for('view_project', hp_id=hp_id))


@app.route('/head-project/<int:hp_id>')
@login_required
def view_project(hp_id):
    project = HeadProject.query.get_or_404(hp_id)
    return render_template('project_detail.html', project=project)


# --- SCHOOLS ---
@app.route('/schools')
@login_required
def schools_page():
    q = request.args.get('q', '')
    district_filter = request.args.get('district', '')
    status_filter = request.args.get('status', '')
    product_filter = request.args.get('product', '')

    query = DonationPoint.query
    if q:
        query = query.filter(
            DonationPoint.name.ilike(f'%{q}%') |
            DonationPoint.udise.ilike(f'%{q}%') |
            DonationPoint.location.ilike(f'%{q}%')
        )
    if district_filter:
        query = query.filter(DonationPoint.district.ilike(f'%{district_filter}%'))

    points = query.all()

    # Build enriched list with latest entry status
    enriched = []
    for pt in points:
        latest = None
        if pt.entries:
            latest = max(pt.entries, key=lambda e: e.timestamp)
        if status_filter and latest and latest.verification_status != status_filter:
            continue
        if product_filter and latest and product_filter.lower() not in (latest.product_name or '').lower():
            continue
        enriched.append({'point': pt, 'latest': latest})

    districts = [d[0] for d in db.session.query(DonationPoint.district).distinct() if d[0]]
    products = [p[0] for p in db.session.query(ReceiverEntry.product_name).distinct() if p[0]]

    return render_template('schools.html',
        enriched=enriched, q=q,
        district_filter=district_filter,
        status_filter=status_filter,
        product_filter=product_filter,
        districts=districts, products=products
    )


@app.route('/schools/add', methods=['GET', 'POST'])
@login_required
def add_school():
    projects = HeadProject.query.all()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'link':
            dp_id = request.form.get('dp_id')
            hp_id = request.form.get('hp_id')
            point = DonationPoint.query.get(dp_id)
            if point and hp_id:
                point.head_project_id = hp_id
                db.session.commit()
                flash('School linked to project.', 'success')
        else:
            name = request.form.get('name')
            location = request.form.get('location')
            udise = request.form.get('udise')
            district = request.form.get('district')
            tahsil = request.form.get('tahsil')
            lat = request.form.get('latitude')
            lng = request.form.get('longitude')
            hp_id = request.form.get('hp_id')
            if name:
                pt = DonationPoint(
                    name=name, location=location, udise=udise,
                    district=district, tahsil=tahsil,
                    latitude=lat, longitude=lng,
                    head_project_id=hp_id
                )
                db.session.add(pt)
                db.session.commit()
                flash('School added successfully.', 'success')
        return redirect(url_for('schools_page'))
    return render_template('add_school.html', projects=projects)


@app.route('/schools/search-json')
@login_required
def schools_search_json():
    q = request.args.get('q', '')
    points = DonationPoint.query.filter(
        DonationPoint.name.ilike(f'%{q}%') |
        DonationPoint.udise.ilike(f'%{q}%')
    ).limit(10).all()
    return jsonify([{'id': p.id, 'name': p.name, 'location': p.location} for p in points])


@app.route('/school/<int:dp_id>')
@login_required
def school_profile(dp_id):
    point = DonationPoint.query.get_or_404(dp_id)
    entries = ReceiverEntry.query.filter_by(donation_point_id=dp_id).order_by(ReceiverEntry.timestamp.desc()).all()
    from datetime import timedelta
    last_delivery = max((e.timestamp for e in entries), default=None)
    overdue = False
    if last_delivery and (datetime.now() - last_delivery).days > 30:
        overdue = True
    elif not last_delivery:
        overdue = True
    return render_template('school_profile.html', point=point, entries=entries, last_delivery=last_delivery, overdue=overdue, now=datetime.now())


@app.route('/head-project/<int:hp_id>/add-point', methods=['POST'])
@login_required
def add_donation_point(hp_id):
    name = request.form.get('name')
    location = request.form.get('location')
    if name:
        db.session.add(DonationPoint(head_project_id=hp_id, name=name, location=location))
        db.session.commit()
    return redirect(url_for('view_project', hp_id=hp_id))


@app.route('/donation-point/<int:dp_id>/delete')
@login_required
def delete_donation_point(dp_id):
    point = DonationPoint.query.get_or_404(dp_id)
    hp_id = point.head_project_id
    db.session.delete(point)
    db.session.commit()
    return redirect(url_for('view_project', hp_id=hp_id))


@app.route('/entry/<int:entry_id>/delete')
@login_required
def delete_entry(entry_id):
    entry = ReceiverEntry.query.get_or_404(entry_id)
    hp_id = entry.donation_point.head_project_id
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('view_project', hp_id=hp_id))


# --- VERIFICATION ---
@app.route('/verification')
@login_required
def verification_desk():
    pending = ReceiverEntry.query.filter_by(verification_status='Pending').order_by(ReceiverEntry.timestamp.desc()).all()
    selected_id = request.args.get('entry_id', type=int)
    selected = ReceiverEntry.query.get(selected_id) if selected_id else (pending[0] if pending else None)
    return render_template('verification.html', pending=pending, selected=selected)


@app.route('/entry/<int:entry_id>/verify', methods=['POST'])
@login_required
def verify_entry(entry_id):
    entry = ReceiverEntry.query.get_or_404(entry_id)
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    if action == 'approve':
        entry.verification_status = 'Verified'
    elif action == 'reject':
        entry.verification_status = 'Rejected'
        entry.rejection_reason = reason
    db.session.commit()
    return redirect(url_for('verification_desk'))


# --- QR GENERATION ---
@app.route('/donation-point/<int:dp_id>/qr')
@login_required
def generate_qr(dp_id):
    point = DonationPoint.query.get_or_404(dp_id)
    target_url = url_for('capture_form', dp_id=dp_id, _external=True)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(target_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = io.BytesIO()
    img.save(buffer, 'PNG')
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png', download_name=f'qr_{dp_id}.png')


# --- PUBLIC CAPTURE FORM (no login required) ---
@app.route('/collect/<int:dp_id>', methods=['GET', 'POST'])
def capture_form(dp_id):
    point = DonationPoint.query.get_or_404(dp_id)

    if request.method == 'POST':
        def save_file(field):
            if field in request.files:
                f = request.files[field]
                if f and f.filename:
                    fname = secure_filename(f"{datetime.now().timestamp()}_{f.filename}")
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                    return fname
            return None

        photo = save_file('photo')
        photo_receiver = save_file('photo_receiver')
        photo_batch = save_file('photo_batch')
        signature = save_file('signature')

        entry_lat = request.form.get('latitude')
        entry_lng = request.form.get('longitude')

        # GPS mismatch check
        gps_flag = None
        if point.latitude and point.longitude and entry_lat and entry_lng:
            dist = haversine_km(point.latitude, point.longitude, entry_lat, entry_lng)
            if dist is not None and dist > 0.5:
                gps_flag = f"GPS mismatch ({dist:.1f} km away from school pin)"

        new_entry = ReceiverEntry(
            donation_point_id=dp_id,
            district=request.form.get('district') or point.district,
            tahsil=request.form.get('tahsil') or point.tahsil,
            product_name=request.form.get('product_name'),
            meal_count=request.form.get('meal_count') or 0,
            receiver_name=request.form.get('receiver_name'),
            status=request.form.get('status', 'Delivered'),
            batch_no=request.form.get('batch_no'),
            box_count=request.form.get('box_count') or 0,
            is_closed=request.form.get('is_closed', 'No'),
            closed_location=request.form.get('closed_location'),
            delivery_notes=request.form.get('delivery_notes'),
            latitude=entry_lat,
            longitude=entry_lng,
            photo_filename=photo,
            photo_receiver=photo_receiver,
            photo_batch=photo_batch,
            signature_filename=signature,
            verification_status='Flagged' if gps_flag else 'Pending',
            gps_flag=gps_flag
        )
        db.session.add(new_entry)
        db.session.commit()
        return render_template('success.html', point=point)

    return render_template('capture_form.html', point=point)
