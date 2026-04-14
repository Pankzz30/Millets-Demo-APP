from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session, jsonify
import math
import os
import io
import qrcode
import base64
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

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
