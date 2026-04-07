import io
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import qrcode
import os
import math
from datetime import datetime
import socket
