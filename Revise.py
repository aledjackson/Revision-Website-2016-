from flask import Flask, redirect, url_for, render_template, session, g, request
import sqlite3
import jinja2
import threading
import os
import flask_sijax

app = Flask(__name__)
app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'

path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
app.config['SIJAX_STATIC_PATH'] = path
#app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js' this is needed if the browser doesn't have json2
flask_sijax.Sijax(app)

conn = sqlite3.connect('revision.db')
c = conn.cursor()
c.close()
conn.close()

@app.route('/login' , methods=['POST', 'GET'])
def login():
    if request.method == 'POST':

        if request.form['submit'] == "login":
            print("understands login")
            inputLoginName = request.form['username']
            inputPassword = request.form['password']
            conn = sqlite3.connect('revision.db')
            c = conn.cursor()
            c.execute("SELECT * FROM userlogin WHERE username='{}' AND password='{}';".format(inputLoginName , inputPassword))
            user = c.fetchall()
            if len(user) != 0:
                user = user[0]
                session['id'] = user[0]
                session['username'] = user[1]
                session['password'] = user[2]
                return redirect(url_for('home'))
            conn.commit()
            c.close()
            conn.close()

    return render_template('login page.html')

@app.route('/home' , methods=['POST','GET'])
def home():
    flashCards= ""
    conn = sqlite3.connect('revision.db')
    c = conn.cursor()
    c.execute("SELECT subject FROM subjects WHERE username='{}';".format(session['username']))
    flashCards = c.fetchall()
    if len(flashCards) == 0:
        flashCards = ""
    conn.commit()
    c.close()
    conn.close()
    if request.method == "POST":
        if request.form['data'] == "subject":
            session['currentSubject'] = request.form['subject']
            #need to have some data checking server side to make sure they are sending only the data I allow
            return redirect(url_for('subject'))
    #the form will send over the value "subject" and also the name of the subject they clicked on
    #add the subject they clicked onto a session variable and redirect them to another page
    #then using the session variable retrieve a table which has all the details about the subject
    return render_template('home page.html' , flashCards=flashCards)

@app.route('/subject', methods=['POST','GET'])
def subject():
    userdata = ""
    #use session to find which subject they are opening
    conn = sqlite3.connect('revision.db')
    c = conn.cursor()
    c.execute("SELECT dataname FROM flashcardlist WHERE username='{}' AND subject='{}';".format(session['username'], session['currentSubject']))
    userdata = c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    if request.method == "POST":
        if request.form['data'] == "flashcard":
            session['flashcards'] = request.form['topic']
            print(session['flashcards'])
            return redirect(url_for('flashCardPage'))
        if request.form['data'] == "newTopic":
            conn = sqlite3.connect('revision.db')
            c = conn.cursor()
            # I need a data check in here to make sure I'm not re-entering the same subject twice!!!
            c.execute("INSERT INTO flashcardlist (username , subject, type, dataname) VALUES ('{}' , '{}' , 'flashcards', '{}');".format(session['username'], session['currentSubject'], request.form['newTopicName']))
            conn.commit()
            c.close()
            conn.close()
            session['flashcards'] = request.form['newTopicName']
            return redirect(url_for('flashCardPage'))

     #use flashcardlist sql table to display all flash cards
    return render_template('subject page.html', userdata=userdata)

@app.route('/flashcards', methods=['POST','GET'])
def flashCardPage():
    print(session['flashcards'])
    flashcardslist = []
    conn = sqlite3.connect('revision.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS flashcards{}(subject TEXT, topic TEXT, cardnumber TEXT, information TEXT);".format(session['username']))
    c.execute("SELECT cardnumber, information FROM flashcards{} WHERE subject='{}' AND topic='{}';".format(session['username'], session['currentSubject'], session['flashcards']))
    flashcardslist = c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    if request.method == 'POST':
        if request.form['data'] == "SaveEdit":
            flashcardexists = ""
            conn = sqlite3.connect('revision.db')
            c = conn.cursor()
            c.execute("UPDATE flashcards{} SET information='{}' WHERE subject='{}' AND cardnumber={} AND topic='{}';".format(session['username'], request.form['flashcardtextsave'], session['currentSubject'], request.form['flashcardnumbersave'], session['flashcards']))
            c.execute("SELECT * FROM flashcards{} WHERE cardnumber={} AND subject='{}' AND topic='{}';".format(session['username'], request.form['flashcardnumbersave'], session['currentSubject'], session['flashcards']))
            flashcardexists = c.fetchall()
            print(flashcardexists)
            conn.commit()
            c.close()
            conn.close()
            if len(flashcardexists) == 0:
                print("this works")
                conn = sqlite3.connect('revision.db')
                c = conn.cursor()
                c.execute("INSERT INTO flashcards{} (subject, topic, cardnumber, information) VALUES ('{}' , '{}', '{}', '{}'); ".format(session['username'], session['currentSubject'], session['flashcards'], request.form['flashcardnumbersave'], request.form['flashcardtextsave'] ))
                conn.commit()
                c.close()
                conn.close()
            return redirect(url_for('flashCardPage'))
    return render_template('flashcards page.html', flashcardslist=flashcardslist , topic=session['flashcards'])

app.debug = True
app.run()


#need to create a function on whether they have the correct session data to be on
#that page then redirect them to the home page if they don't
