import firebase_admin
import pyrebase
import json
from firebase_admin import credentials
from flask import Flask, Request, render_template, redirect, url_for, request
import os
base = os.getcwd()
app = Flask(__name__)

#Connecting to firebase
cred = credentials.Certificate(os.path.normpath(os.path.join(base,"fbAdminConfig.json"))) #this file is not in our repo for security reasons
admin_fire= firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open(os.path.normpath(base+'/fbconfig.json'))))

auth = pb.auth()
db = pb.database()

person = {"is_logged_in": False, "name": "", "email": "", "uid": "", "verified_email":False, "address1":"", "address2":"", "city":"", "state":"", "zip":"", "account_type":"", "isSponsored":False}
attributes = ["name", "verified_email", "address1", "address2", "city", "state", "zip", "account_type", "isSponsored"]

#Login
@app.route("/")
def login():
    return render_template("login.html")

#Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")

#Welcome page
@app.route("/welcome")
def welcome():
    if person["is_logged_in"] == True:
        return render_template("welcome.html", email = person["email"], name = person["name"], account_type = person["account_type"], isSponsored = person["isSponsored"], address1=person["address1"], address2=person["address2"], city = person["city"], state=person["state"],zip=person["zip"])
    else:
        return redirect(url_for('login'))
#Settings
@app.route("/savesettings", methods = ["POST", "GET"])
def savesettings():
    global person 
    if request.method == "POST":
        result = request.form
        static = False
        try:
            response = result['static']
            static = True
        except:
            static = False
    data = {"static" : str(static)}
    db.child("users").child(person["uid"]).update(data)
    return redirect(url_for('settings'))

@app.route("/settings")
def settings():
    global person 
    if person["is_logged_in"] == True:
        return render_template("settings.html", name=person["name"], role=person["account_type"])
    else:
        return redirect(url_for('login'))
#If someone clicks on login, they are redirected to /result
@app.route("/result", methods = ["POST", "GET"])
def result():
    if request.method == "POST":        #Only if data has been posted
        result = request.form           #Get the data
        email = result["email"]
        password = result["pass"]
        #address_1 = result["address1"]
        #address_2 = result["address2"]
        #city = result["city"]
        #state = result["state"]
        #zip = result["zip"]
        #account_type = result["account_type"]
        #is_sponsored = "is_sponsor" in result.getlist("isSponsored")[0]
        try:
            #Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            #Insert the user data in the global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            #Get the name of the user
            data = db.child("users").get()
            for i in attributes:
                person[i] = data.val()[person["uid"]][i]
            #Redirect to welcome page
            return redirect(url_for('welcome'))
        except:
            #If there is any error, redirect back to login
            return redirect(url_for('login'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('login'))

#If someone clicks on register, they are redirected to /register
@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":        #Only listen to POST
        result = request.form           #Get the data submitted
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        address_1 = result["address1"]
        address_2 = result["address2"]
        city = result["city"]
        state = result["state"]
        zip = result["zip"]
        account_type = result["account_type"]
        is_sponsored = "is_sponsor" in result.getlist("isSponsored")
        try:
            #Try creating the user account using the provided data
            auth.create_user_with_email_and_password(email, password)
            #Login the user
            user = auth.sign_in_with_email_and_password(email, password)
            #Add data to global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["name"] = name
            #Append data to the firebase realtime database
            data = {"name": name, "email": email, "address1":address_1, "address2":address_2, "city":city, "state":state, "zip":zip, "account_type":account_type, "verified_email":str(False), "isSponsored":str(is_sponsored), "static": str(False)}
            db.child("users").child(person["uid"]).set(data)
            auth.send_email_verification(person["uid"])
            #Go to welcome page
            return redirect(url_for('welcome'))
        except:
            #If there is any error, redirect to register
            return redirect(url_for('register'))

    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('register'))

if __name__ == "__main__":
    app.run()
