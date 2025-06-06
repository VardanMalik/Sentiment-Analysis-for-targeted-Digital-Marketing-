from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc
from datetime import datetime
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os
from flask import session
from flask import request

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://vardan:vardan123@localhost/gym_feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
analyzer = SentimentIntensityAnalyzer()

# Feedback Model
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    sentiment = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    avg_rating = db.session.query(func.avg(Feedback.rating)).scalar()
    all_positive_feedback = Feedback.query.filter_by(sentiment='Positive').order_by(desc(Feedback.created_at)).all()
    return render_template(
        'index.html',
        avg_rating=round(avg_rating or 0, 1),
        all_positive_feedback=all_positive_feedback
    )

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        rating = int(request.form['rating'])

        score = analyzer.polarity_scores(message)['compound']
        if score >= 0.05:
            sentiment = 'Positive'
        elif score <= -0.05:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'

        entry = Feedback(name=name, email=email, message=message, rating=rating, sentiment=sentiment)
        db.session.add(entry)
        db.session.commit()

        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('feedback'))

    feedback_list = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template('feedback.html', feedback_list=feedback_list)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()

    sentiment_counts = {
        'Positive': Feedback.query.filter_by(sentiment='Positive').count(),
        'Neutral': Feedback.query.filter_by(sentiment='Neutral').count(),
        'Negative': Feedback.query.filter_by(sentiment='Negative').count(),
    }

    # Star rating counts (1-5 stars)
    star_counts = {}
    for i in range(1, 6):
        star_counts[i] = Feedback.query.filter_by(rating=i).count()

    ratings = db.session.query(Feedback.rating, func.count(Feedback.rating)).group_by(Feedback.rating).all()

    # Total number of feedbacks
    total_feedback = Feedback.query.count()

    # Latest feedback date
    latest_feedback_date = db.session.query(func.max(Feedback.created_at)).scalar()

    return render_template(
        'admin.html',
        feedbacks=feedbacks,
        sentiments=sentiment_counts,
        ratings=ratings,
        star_counts=star_counts,
        total_feedback=total_feedback,
        latest_feedback_date=latest_feedback_date
    )
    

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.route('/delete-feedback/<int:feedback_id>', methods=['POST'])
def delete_feedback(feedback_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    fb = Feedback.query.get_or_404(feedback_id)
    db.session.delete(fb)
    db.session.commit()
    flash('Feedback deleted successfully.', 'success')
    return redirect(url_for('admin'))

@app.before_request
def auto_logout_on_user_routes():
    if session.get('admin_logged_in'):
        path = request.path
        allowed_routes = [
            '/admin',
            '/admin-login',
            '/admin-logout',
            '/delete-feedback',
        ]

        # also allow favicon and static assets
        if path.startswith('/static') or path.startswith('/favicon.ico'):
            return

        # Allow if path matches or starts with allowed route
        if not any(path.startswith(route) for route in allowed_routes):
            if request.method == 'GET':  # only auto-logout on GET routes
                session.pop('admin_logged_in', None)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


