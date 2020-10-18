import firebase_admin
import pyrebase
import json
from firebase_admin import credentials
from flask import Flask, Request, render_template, redirect, url_for, request, make_response
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

''''
def generate_person_cookie(uid, email, template_function):
    r = Flask.make_response(render_template(url_for(template_function)))
    r.set_cookie("uid", value=uid, max_age=60*60*24*15)
    r.set_cookie("email", value=email, max_age=60*60*24*15)
    r.set_cookie("is_logged_in", True, max_age=60*60*24*15)
    return r
def get_person_cookie():
    person = {"is_logged_in": False, "name": "", "email": "", "uid": "", "verified_email": False, "address1": "",
              "address2": "", "city": "", "state": "", "zip": "", "account_type": "", "isSponsored": False}
    person["is_logged_in"] = request.cookies.get("is_logged_in")
    uid = request.cookies.get("uid")
    email = request.cookies.get("email")
    person["email"] = email
    person["uid"] = uid
    other_attr = db.child("users").child(uid).get()
    for i in attributes:
        person[i] = other_attr[i]
    return person
'''
#Login
@app.route("/")
def login():
    return render_template("login.html")

#Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/donor", methods = ["POST", "GET"])
def donor():
    if person["is_logged_in"]:
        if request.method == "POST":
            result = request.form
            title = result["title"]
            desc = result["desc"]
            cost = result["cost"]
            weight = result["weight_lbs"]
            volume = result["volume_in"]
            quantity = result["quantity"]
            create_donor_object(person["uid"], cost, desc, quantity, title, weight, volume)
            return redirect("/welcome")
        else:
            if "donor" in person["account_type"]:
                return render_template("list_order_donor.html", person=person)
            else:
                return render_template("welcome.html", person=person)
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
#Welcome page
@app.route("/welcome")
def welcome():
    #logged = request.cookies.get("is_logged_in") if "is_logged_in" in request.cookies else False
    if person["is_logged_in"]:
        return render_template("welcome.html", person = person)
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
            data = {"name": name, "email": email, "address1":address_1, "address2":address_2, "city":city, "state":state, "zip":zip, "account_type":account_type, "verified_email":str(False), "isSponsored":str(is_sponsored)}
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
