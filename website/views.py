from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Patient
from . import db
import json
#from keras.models import load_model
import cv2
import numpy as np
import base64
from PIL import Image
import io
import re
import os

img_size = 100

#model = load_model('model-018.h5')
label_dict = {0: 'Pneumonia', 1: 'Covid19', 2: 'Normal'}

views = Blueprint('views', __name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

basedir = os.path.abspath(os.path.dirname(__file__))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess(img):
    img = np.array(img)
    print(img.shape)
    if(img.ndim == 3):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    gray = gray/255
    resized = cv2.resize(gray, (img_size, img_size))
    reshaped = resized.reshape(1, img_size, img_size)

    return reshaped


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        #message = request.get_json(force=True)
        #encoded = message['image']
        #decoded = base64.b64decode(encoded)
        #dataBytesIO = io.BytesIO(decoded)
        # dataBytesIO.seek(0)
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No image selected for uploading', category='error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_stored = os.path.join(
                basedir, current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_stored)
            image = Image.open(file_stored)
            test_image = preprocess(image)
            prediction = [[50, 94, 0]]  # model.predict(test_image)
            result = np.argmax(prediction, axis=1)[0]
            accuracy = float(np.max(prediction, axis=1)[0])
            label = label_dict[result]

            name = request.form.get('name')
            phone = request.form.get('phone')
            result = label
            probability = accuracy
            new_patient = Patient(name=name, phone=phone, result=result,
                                  probability=probability, user_id=current_user.id)
            db.session.add(new_patient)
            db.session.commit()
            flash('Patient added!', category='success')
            return render_template('home.html', patient=name, phone=phone, filename=filename, result=result, accuracy=accuracy, user=current_user)
        else:
            flash('Allowed image types are -> png, jpg, jpeg, gif', category='error')
            return redirect(request.url)

    return render_template('home.html', user=current_user)


@views.route('/display/<filename>')
def display_image(filename):
        #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)
