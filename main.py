import firebase_admin
import pyrebase
import json
from firebase_admin import credentials
from flask import Flask, Request, render_template, redirect, url_for, request, session
import os
base = os.getcwd()
app = Flask(__name__)
app.secret_key = "asdfasfdasfdsafasddfsadfasdfsadfdas"  
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
#Connecting to firebase
cred = credentials.Certificate(os.path.normpath(os.path.join(base,"fbAdminConfig.json"))) #this file is not in our repo for security reasons
admin_fire= firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open(os.path.normpath(base+'/fbconfig.json'))))

auth = pb.auth()
db = pb.database()
person = {"is_logged_in": False, "name": "", "email": "", "uid": "", "verified_email":False, "address1":"", "address2":"", "city":"", "state":"", "zip":"", "account_type":"", "isSponsored":False, "static":False}
attributes = ["name", "verified_email", "address1", "address2", "city", "state", "zip", "account_type", "isSponsored", "static"]

#Login
@app.route("/")
def login():
    try:
        if session["is_logged_in"] == True:
            return redirect("welcome")
    except:
        for x in person.keys():
            session[x] = person[x]
        session["is_logged_in"] = False
    return render_template("login.html")

@app.route("/donor", methods = ["POST", "GET"])
def donor():
    try:
        if session["is_logged_in"] == True:
            pass
    except:
        for x in person.keys():
            session[x] = person[x]
        session["is_logged_in"] = False
        return redirect("/")
    if session["is_logged_in"]:
        if request.method == "POST":
            result = request.form
            title = result["title"]
            desc = result["desc"]
            cost = result["cost"]
            weight = result["weight_lbs"]
            volume = result["volume_in"]
            quantity = result["quantity"]
            create_donor_object(session["uid"], cost, desc, quantity, title, weight, volume)
            return redirect("/welcome")
        else:
            if "donor" in session["account_type"]:
                return render_template("list_order_donor.html", person=session)
            else:
                return render_template("welcome.html", person=session)
    else:
        return redirect(url_for('login'))
def create_donor_object(uid, cost, desc, quantity, title, weight_lbs, volume_in):
    #orders = db.child("orders")

    import random
    mx = random.randint(0, 1000)
    object_id = title + "-" + str(mx)
    while (object_id in db.child("orders").get().key()):
        mx = random.randint(0, 1000)
        object_id = title + "-" + str(mx)
    data = {"cost": cost, "desc":desc, "listed":True, "quantity":quantity, "title":title, "volume_in":volume_in, "weight_lbs":weight_lbs, "participants":{"u_donor":uid}}
    db.child("orders").child(object_id).set(data)
#Sign up/ Register
@app.route("/signup")
def signup():
    try:
        if session["is_logged_in"] == True:
            return redirect("welcome")
    except:
        for x in person.keys():
            session[x] = person[x]
        session["is_logged_in"] = False
    return render_template("signup.html")

#Welcome page
@app.route("/welcome")
def welcome():
    if session["is_logged_in"] == True:
        return render_template("welcome.html", email = session["email"], name = session["name"], account_type = session["account_type"], isSponsored = session["isSponsored"], address1=session["address1"], address2=session["address2"], city = session["city"], state=session["state"],zip=session["zip"])
    else:
        return redirect(url_for('login'))
#Settings
@app.route("/savesettings", methods = ["POST", "GET"])
def savesettings():
    if request.method == "POST":
        result = request.form
        static = False
        try:
            response = result['static']
            static = True
        except Exception as e:
            print(e)
            static = False
    data = {"static" : static}
    db.child("users").child(session["uid"]).update(data)
    session['static'] = static
    return redirect(url_for('settings'))

@app.route("/settings")
def settings():
    if session["is_logged_in"]:
        return render_template("settings.html", name=session["name"], role=session["account_type"], static=session['static'])
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
            #Insert the user data in the global session
            session["is_logged_in"] = True
            session["email"] = user["email"]
            session["uid"] = user["localId"]
            #Get the name of the user
            data = db.child("users").get()
            for i in attributes:
                session[i] = data.val()[session["uid"]][i]
            #Redirect to welcome page
            return redirect(url_for('welcome'))
        except Exception as e:
            print(e)
            #If there is any error, redirect back to login
            return redirect(url_for('login'))
    else:
        if session["is_logged_in"] == True:
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
            #Add data to global session
            session["is_logged_in"] = True
            session["email"] = user["email"]
            session["uid"] = user["localId"]
            session["name"] = name
            #Append data to the firebase realtime database
            data = {"name": name, "email": email, "address1":address_1, "address2":address_2, "city":city, "state":state, "zip":zip, "account_type":account_type, "verified_email":str(False), "isSponsored":str(is_sponsored), "static": False}
            db.child("users").child(session["uid"]).set(data)
            auth.send_email_verification(session["uid"])
            for i in attributes:
                session[i] = data[i]
            #Go to welcome page
            return redirect(url_for('welcome'))
        except Exception as e:
            print(e)
            #If there is any error, redirect to register
            return redirect(url_for('register'))

    else:
        try:
            if session["is_logged_in"] == True:
                return redirect(url_for('welcome'))
            else:
                return redirect(url_for('signup'))
        except Exception as e:
            print(e)
            return redirect(url_for('signup'))

@app.route("/signout")
def signout():
    for x in person.keys():
        session[x] = person[x]
    session["is_logged_in"] = False
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
