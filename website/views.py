from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Patient
from . import db
from tensorflow.keras.models import model_from_json
import cv2
import numpy as np
import os
import urllib.request

img_size = 300
label_dict = {0: 'Covid19', 1: 'Normal', 2: 'Pneumonia'}

views = Blueprint('views', __name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

basedir = os.path.abspath(os.path.dirname(__file__))

model_url = 'https://github.com/Nilavan/RespAI/releases/download/model/model_weights.h5'
model_filename = model_url.split('/')[-1]

if not os.path.exists(model_filename):
    print("Downloading model...")
    urllib.request.urlretrieve(model_url, model_filename)
    print("Model downloaded!")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        name = request.form.get('name')
        email = request.form.get('email')
        if file.filename == '':
            flash('No image selected', category='error')
            return redirect(request.url)
        elif (name == '' or email == ''):
            flash("Enter name and email id", category="error")
            return redirect(request.url)
        elif file and allowed_file(file.filename) and name != '' and email != '':
            json_file = open('model.json', 'r')
            loaded_model_json = json_file.read()
            json_file.close()
            model = model_from_json(loaded_model_json)
            model.load_weights(model_filename)
            filename = secure_filename(file.filename)
            file_stored = os.path.join(
                basedir, current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_stored)
            test_image = cv2.imread(file_stored)
            test_image = cv2.resize(test_image, (300, 300))
            test_image = test_image.astype('float32') / 255.0
            prediction = model.predict(
                np.expand_dims(test_image, axis=0))[0]
            result = np.argmax(prediction)
            label = label_dict[result]
            accuracy = float(np.max(prediction)*100.0)
            new_patient = Patient(name=name, email=email, result=label,
                                  probability=accuracy, user_id=current_user.id)
            db.session.add(new_patient)
            db.session.commit()
            flash('Patient added to database! Please verify the results',
                  category='success')
            return render_template('home.html', patient=name, email=email, filename=filename, result=label, accuracy=accuracy, user=current_user)
        else:
            flash('Allowed image types are -> png, jpg, jpeg', category='error')
            return redirect(request.url)

    return render_template('home.html', user=current_user)


@views.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)
