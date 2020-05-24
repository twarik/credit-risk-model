import os
import numpy as np
import pandas as pd
from flask import request, render_template, flash, redirect, url_for, request
from werkzeug.utils import secure_filename

from application import app, db, bcrypt
from application.db_models import Borrower, User
from application.ml_models import image_model, transform_data, credit_model
from application.forms import RegistrationForm, LoginForm#, RequestResetForm, RequestPasswordForm
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/')
def index():
    ''' Render home/ landing page '''
    return render_template("template.html")

@app.route('/image_classification', methods=['POST', 'GET'])
def dl():
    '''Render page serving the image classification model to allow user to upload image'''

    if request.method == "GET":
        return render_template("image.html", title ='Image classification')

    if request.method == 'POST':
        # Access the input (image) stream and keep it in the Filestorage
        file = request.files['file']
        #convert the file to bytes
        image = file.read()
        # predict the class of the image
        result = image_model(image)
        #Select the top three predictions according to their probabilities
        top1 = '1. %s: %.4f'%(result[0][0], result[0][1])
        top2 = '2. %s: %.4f'%(result[1][0], result[1][1])
        top3 = '3. %s: %.4f'%(result[2][0], result[2][1])

        ## In addition to image classification, Let's store the predicted filecd
        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath, 'static/uploads', secure_filename(file.filename))
        #save image to directory specified ('static/uploads')
        file.save(file_path)
        image_file = url_for('static', filename='uploads/'+ secure_filename(file.filename))

        return render_template('image.html', first=top1, second=top2, third=top3, image_file=image_file)

@app.route('/credit_risking', methods=['POST', 'GET'])
def credit_score():
    '''Render page serving the Credit score prediction model'''
    if request.method == "GET":
        return render_template("credit.html", title ='Credit Risk Prediction')

    if request.method == 'POST':
        '''
        pre-process the submitted values, then predict the Credit Risk
        '''
        # read in data from the input form
        full_name = str(request.form['full_name'])
        age = int(request.form['age'])
        gender = str(request.form['gender'])
        job = int(request.form['job'])
        housing = str(request.form['housing'])
        saving = str(request.form['saving'])
        checking = str(request.form['checking'])
        credit = int(request.form['credit'])
        duration = int(request.form['duration'])
        purpose = str(request.form['purpose'])

        #Data preparation
        input_data = [{'Age':age, 'Sex':gender, 'Job':job, 'Housing':housing, 'Saving accounts':saving,
        'Checking account':checking, 'Credit amount':credit, 'Duration':duration, 'Purpose':purpose}]
        data = pd.DataFrame(input_data)
        # Labels
        labels = {0: 'bad', 1: 'good'}

        #Data transformation
        credit_data = transform_data(data)

        #order the features in the dataset
        final_df = credit_data[['Age', 'Sex', 'Job', 'Housing', 'Saving accounts', 'Checking account', 'Credit amount', 'Duration', 'Purpose']]

        #predict Credit risk
        pred = credit_model.predict(final_df.values)[0]
        final = labels[pred]

        # save the form inputs to the database
        # create a new instance of a client(debtor)
        client = Borrower(full_name=full_name, age=age, sex=gender, job=job, housing=housing, saving=saving,
                            checking=checking, credit=credit, duration=duration, purpose=purpose, risk=final)
        # Add client to the changes (session) that we want to make in our database
        db.session.add(client)
        # save into the database
        db.session.commit()
        flash(f'Your data has been saved in our database','success')


        return render_template('credit.html', prediction_text='Hello {} this is a {} Loan'.format(full_name, final),
        title ='Credit Risk Prediction')


@app.route('/admin')
@login_required
def admin():
    #Query the database
    debtors = Borrower.query.all()
    return render_template('clients.html', title ="Clients' details", debtors=debtors)

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    form = RegistrationForm()
    if form.validate_on_submit():
        #Hash the password entered and save the hash to the database instead of the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! you are now able to login','success')
        return redirect(url_for('login'))
    return render_template('register.html', title ="Register", form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        #Check if the email is valid (in your database) and submitted password is similar to the password hash in the database
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'You have been logged in as {user.username}','success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin'))
        else:
            flash(f'Login Unsuccessful. Please check username and password','danger')
    return render_template('login.html', title ="Login", form=form)

@app.route('/logout', methods=['GET','POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))
