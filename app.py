# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json

app = Flask(__name__)
app.config.from_pyfile('config.py')

mongo = PyMongo(app)

@app.route('/')
def index():
    if 'coach_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        coach = mongo.db.coaches.find_one({'email': email})
        
        if coach and check_password_hash(coach['password'], password):
            session['coach_id'] = str(coach['_id'])
            session['coach_name'] = coach['name']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        sport = request.form.get('sport')
        language = request.form.get('language', 'en')
        
        # Check if coach already exists
        if mongo.db.coaches.find_one({'email': email}):
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        
        coach_data = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'sport': sport,
            'language': language,
            'created_at': datetime.utcnow()
        }
        
        result = mongo.db.coaches.insert_one(coach_data)
        session['coach_id'] = str(result.inserted_id)
        session['coach_name'] = name
        
        flash('Registration successful!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'coach_id' not in session:
        return redirect(url_for('login'))
    
    coach_id = session['coach_id']
    athletes = list(mongo.db.athletes.find({'coach_id': coach_id}))
    
    # Get recent activities
    activities = list(mongo.db.activities.find({'coach_id': coach_id}).sort('timestamp', -1).limit(5))
    
    return render_template('dashboard.html', 
                         athletes=athletes, 
                         activities=activities,
                         coach_name=session.get('coach_name'))

@app.route('/athlete_management')
def athlete_management():
    if 'coach_id' not in session:
        return redirect(url_for('login'))
    
    coach_id = session['coach_id']
    athletes = list(mongo.db.athletes.find({'coach_id': coach_id}))
    
    return render_template('athlete_management.html', athletes=athletes)

@app.route('/add_athlete', methods=['POST'])
def add_athlete():
    if 'coach_id' not in session:
        return redirect(url_for('login'))
    
    name = request.form.get('name')
    age = request.form.get('age')
    sport = request.form.get('sport')
    gender = request.form.get('gender')
    location = request.form.get('location')
    contact = request.form.get('contact')
    disabilities = request.form.get('disabilities', '')
    language_preference = request.form.get('language_preference', 'en')
    
    athlete_data = {
        'coach_id': session['coach_id'],
        'name': name,
        'age': int(age),
        'sport': sport,
        'gender': gender,
        'location': location,
        'contact': contact,
        'disabilities': disabilities,
        'language_preference': language_preference,
        'joined_date': datetime.utcnow(),
        'status': 'active'
    }
    
    mongo.db.athletes.insert_one(athlete_data)
    
    # Log activity
    activity_data = {
        'coach_id': session['coach_id'],
        'action': f'Added athlete: {name}',
        'timestamp': datetime.utcnow()
    }
    mongo.db.activities.insert_one(activity_data)
    
    flash('Athlete added successfully!', 'success')
    return redirect(url_for('athlete_management'))

@app.route('/performance_tracking/<athlete_id>')
def performance_tracking(athlete_id):
    if 'coach_id' not in session:
        return redirect(url_for('login'))
    
    athlete = mongo.db.athletes.find_one({'_id': ObjectId(athlete_id)})
    performance_data = list(mongo.db.performance.find({'athlete_id': athlete_id}).sort('date', -1))
    
    return render_template('performance.html', athlete=athlete, performance_data=performance_data)

@app.route('/add_performance', methods=['POST'])
def add_performance():
    if 'coach_id' not in session:
        return redirect(url_for('login'))
    
    athlete_id = request.form.get('athlete_id')
    metric_name = request.form.get('metric_name')
    value = request.form.get('value')
    date = request.form.get('date')
    notes = request.form.get('notes', '')
    
    performance_data = {
        'athlete_id': athlete_id,
        'metric_name': metric_name,
        'value': float(value),
        'date': datetime.strptime(date, '%Y-%m-%d'),
        'notes': notes,
        'recorded_at': datetime.utcnow()
    }
    
    mongo.db.performance.insert_one(performance_data)
    
    # Log activity
    athlete = mongo.db.athletes.find_one({'_id': ObjectId(athlete_id)})
    activity_data = {
        'coach_id': session['coach_id'],
        'action': f'Recorded performance for {athlete["name"]}: {metric_name} = {value}',
        'timestamp': datetime.utcnow()
    }
    mongo.db.activities.insert_one(activity_data)
    
    flash('Performance data added successfully!', 'success')
    return redirect(url_for('performance_tracking', athlete_id=athlete_id))

@app.route('/injury_prevention')
def injury_prevention():
    if 'coach_id' not in session:
        return redirect(url_for('login'))
    
    coach_id = session['coach_id']
    athletes = list(mongo.db.athletes.find({'coach_id': coach_id}))
    injuries = list(mongo.db.injuries.find({'coach_id': coach_id}).sort('date_reported', -1))
    
    return render_template('injury_prevention.html', athletes=athletes, injuries=injuries)

@app.route('/report_injury', methods=['POST'])
def report_injury():
    if 'coach_id' not in session:
        return redirect(url_for('login'))
    
    athlete_id = request.form.get('athlete_id')
    injury_type = request.form.get('injury_type')
    body_part = request.form.get('body_part')
    severity = request.form.get('severity')
    description = request.form.get('description')
    recovery_plan = request.form.get('recovery_plan')
    
    injury_data = {
        'coach_id': session['coach_id'],
        'athlete_id': athlete_id,
        'injury_type': injury_type,
        'body_part': body_part,
        'severity': severity,
        'description': description,
        'recovery_plan': recovery_plan,
        'date_reported': datetime.utcnow(),
        'status': 'active'
    }
    
    mongo.db.injuries.insert_one(injury_data)
    
    # Update athlete status if needed
    if severity in ['severe', 'critical']:
        mongo.db.athletes.update_one(
            {'_id': ObjectId(athlete_id)},
            {'$set': {'status': 'injured'}}
        )
    
    # Log activity
    athlete = mongo.db.athletes.find_one({'_id': ObjectId(athlete_id)})
    activity_data = {
        'coach_id': session['coach_id'],
        'action': f'Reported injury for {athlete["name"]}: {injury_type}',
        'timestamp': datetime.utcnow()
    }
    mongo.db.activities.insert_one(activity_data)
    
    flash('Injury reported successfully!', 'success')
    return redirect(url_for('injury_prevention'))

@app.route('/video_analysis')
def video_analysis():
    if 'coach_id' not in session:
        return redirect(url_for('login'))
    
    coach_id = session['coach_id']
    athletes = list(mongo.db.athletes.find({'coach_id': coach_id}))
    videos = list(mongo.db.videos.find({'coach_id': coach_id}).sort('upload_date', -1))
    
    return render_template('video_analysis.html', athletes=athletes, videos=videos)

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'coach_id' not in session:
        return redirect(url_for('login'))
    
    if 'video_file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('video_analysis'))
    
    file = request.files['video_file']
    athlete_id = request.form.get('athlete_id')
    analysis_type = request.form.get('analysis_type')
    notes = request.form.get('notes', '')
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('video_analysis'))
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        video_data = {
            'coach_id': session['coach_id'],
            'athlete_id': athlete_id,
            'filename': filename,
            'file_path': file_path,
            'analysis_type': analysis_type,
            'notes': notes,
            'upload_date': datetime.utcnow(),
            'status': 'pending_analysis'
        }
        
        mongo.db.videos.insert_one(video_data)
        
        # Log activity
        athlete = mongo.db.athletes.find_one({'_id': ObjectId(athlete_id)})
        activity_data = {
            'coach_id': session['coach_id'],
            'action': f'Uploaded video for {athlete["name"]}: {analysis_type} analysis',
            'timestamp': datetime.utcnow()
        }
        mongo.db.activities.insert_one(activity_data)
        
        flash('Video uploaded successfully!', 'success')
    
    return redirect(url_for('video_analysis'))

@app.route('/analyze_video/<video_id>')
def analyze_video(video_id):
    if 'coach_id' not in session:
        return redirect(url_for('login'))
    
    video = mongo.db.videos.find_one({'_id': ObjectId(video_id)})
    athlete = mongo.db.athletes.find_one({'_id': ObjectId(video['athlete_id'])})
    
    # In a real application, this would involve actual video analysis
    # For this example, we'll generate some mock analysis data
    
    analysis_data = {
        'video_id': video_id,
        'athlete_id': video['athlete_id'],
        'analysis_date': datetime.utcnow(),
        'technique_score': 85,
        'form_issues': ['Slight forward lean during takeoff', 'Arm position could be improved'],
        'recommendations': ['Focus on maintaining upright posture', 'Practice arm swing drills'],
        'strengths': ['Good explosive power', 'Excellent follow-through'],
        'status': 'analyzed'
    }
    
    # Update video status
    mongo.db.videos.update_one(
        {'_id': ObjectId(video_id)},
        {'$set': {'status': 'analyzed', 'analysis_data': analysis_data}}
    )
    
    # Log activity
    activity_data = {
        'coach_id': session['coach_id'],
        'action': f'Analyzed video for {athlete["name"]}',
        'timestamp': datetime.utcnow()
    }
    mongo.db.activities.insert_one(activity_data)
    
    flash('Video analysis completed!', 'success')
    return redirect(url_for('video_analysis'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'coach_id' not in session:
        return redirect(url_for('login'))
    
    coach_id = session['coach_id']
    coach = mongo.db.coaches.find_one({'_id': ObjectId(coach_id)})
    
    if request.method == 'POST':
        name = request.form.get('name')
        sport = request.form.get('sport')
        language = request.form.get('language')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        update_data = {
            'name': name,
            'sport': sport,
            'language': language
        }
        
        if current_password and new_password:
            if check_password_hash(coach['password'], current_password):
                update_data['password'] = generate_password_hash(new_password)
            else:
                flash('Current password is incorrect', 'error')
                return redirect(url_for('settings'))
        
        mongo.db.coaches.update_one(
            {'_id': ObjectId(coach_id)},
            {'$set': update_data}
        )
        
        session['coach_name'] = name
        
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings'))
    
    return render_template('settings.html', coach=coach)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)