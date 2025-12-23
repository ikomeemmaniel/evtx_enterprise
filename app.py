import os
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_file, abort
)
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user
)
from werkzeug.utils import secure_filename

from config import Config
from models import db, User, Upload, EventRecord
from forms import LoginForm, RegistrationForm, UploadForm, SearchForm
from utils.evtx_parser import parse_evtx_file, validate_evtx_file
from utils.csv_writer import write_events_to_csv
from utils.excel_writer import write_events_to_excel

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "login"
    login_manager.login_message = "Please log in to continue."

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Directories
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["CONVERT_FOLDER"], exist_ok=True)

    def allowed_file(filename):
        return (
            "." in filename and
            filename.rsplit(".", 1)[1].lower() in app.config.get("ALLOWED_EXTENSIONS", ["evtx"])
        )

    # --- ROUTES ---

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                return redirect(url_for("dashboard"))
            flash("Invalid username or password", "danger")
        return render_template("login.html", form=form)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        return render_template("register.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Logged out successfully.", "info")
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        page = request.args.get("page", 1, type=int)
        # Using a default order if role is not strictly defined as admin
        is_admin = getattr(current_user, 'role', 'user') == 'admin'
        
        if is_admin:
            pagination = Upload.query.order_by(Upload.uploaded_at.desc()).paginate(page=page, per_page=10, error_out=False)
        else:
            pagination = Upload.query.filter_by(user_id=current_user.id).order_by(Upload.uploaded_at.desc()).paginate(page=page, per_page=10, error_out=False)
        return render_template("dashboard.html", uploads=pagination)

    @app.route("/upload", methods=["GET", "POST"])
    @login_required
    def upload():
        form = UploadForm()
        if form.validate_on_submit():
            file = form.file.data
            if not file or not allowed_file(file.filename):
                flash("Only .evtx files are allowed", "danger")
                return render_template("upload.html", form=form)

            filename = secure_filename(file.filename)
            ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{ts}_{filename}"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            try:
                if not validate_evtx_file(file_path):
                    os.remove(file_path)
                    flash("Invalid EVTX file", "danger")
                    return render_template("upload.html", form=form)

                # 1. Parse using your forensic parser
                events_data = parse_evtx_file(file_path)
                
                upload_rec = Upload(
                    filename=filename,
                    stored_path=file_path,
                    user_id=current_user.id,
                    event_count=len(events_data)
                )
                db.session.add(upload_rec)
                db.session.flush()

                # 2. Map data to the 1-10 Forensic Order in the DB
                for e in events_data:
                    db.session.add(EventRecord(
                        upload_id=upload_rec.id,
                        user_sid=e.user_sid,      # Your "Username" column
                        ip_address=e.ip_address,
                        event_id=str(e.event_id),
                        timestamp=e.timestamp,
                        security_id=e.security_id,
                        action=e.action,
                        keywords=e.keywords,
                        failure_reason=e.failure_reason,
                        process_name=e.process_name
                    ))

                # 3. Generate Forensic Reports (CSV & Excel)
                csv_filename = f"{upload_rec.id}_forensic.csv"
                xlsx_filename = f"{upload_rec.id}_forensic.xlsx"
                csv_path = os.path.join(app.config["CONVERT_FOLDER"], csv_filename)
                xlsx_path = os.path.join(app.config["CONVERT_FOLDER"], xlsx_filename)

                write_events_to_csv(events_data, csv_path)
                write_events_to_excel(events_data, xlsx_path)

                upload_rec.converted_csv_path = csv_filename
                upload_rec.converted_xlsx_path = xlsx_filename

                db.session.commit()
                flash(f"{len(events_data)} forensic events analyzed successfully.", "success")
                return redirect(url_for("dashboard"))

            except Exception as e:
                db.session.rollback()
                if os.path.exists(file_path):
                    os.remove(file_path)
                flash(f"Upload failed: {e}", "danger")

        return render_template("upload.html", form=form)

    @app.route("/events/<int:upload_id>")
    @login_required
    def events(upload_id):
        upload_rec = Upload.query.get_or_404(upload_id)
        is_admin = getattr(current_user, 'role', 'user') == 'admin'
        if not is_admin and upload_rec.user_id != current_user.id:
            abort(403)
        
        search_form = SearchForm()
        page = request.args.get("page", 1, type=int)
        query = EventRecord.query.filter_by(upload_id=upload_id)
        
        # Sorted by timestamp for forensic accuracy
        events_paginated = query.order_by(EventRecord.timestamp.desc()).paginate(page=page, per_page=50, error_out=False)

        return render_template(
            "events.html",
            upload=upload_rec,
            events=events_paginated,
            search_form=search_form
        )

    @app.route("/download/<int:upload_id>/<file_type>")
    @login_required
    def download(upload_id, file_type):
        upload_rec = Upload.query.get_or_404(upload_id)
        is_admin = getattr(current_user, 'role', 'user') == 'admin'
        if not is_admin and upload_rec.user_id != current_user.id:
            abort(403)
        
        if file_type == "csv" and upload_rec.converted_csv_path:
            return send_file(os.path.join(app.config["CONVERT_FOLDER"], upload_rec.converted_csv_path), as_attachment=True)
        if file_type == "excel" and upload_rec.converted_xlsx_path:
            return send_file(os.path.join(app.config["CONVERT_FOLDER"], upload_rec.converted_xlsx_path), as_attachment=True)
        
        flash("File not available", "danger")
        return redirect(url_for("events", upload_id=upload_id))

    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", email="admin@example.com", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
