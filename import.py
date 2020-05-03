import os, csv

##from flask import Flask, session, render_template, request
##from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

##app = Flask(__name__)

### Check for environment variable
##if not os.getenv("DATABASE_URL"):
##    raise RuntimeError("DATABASE_URL is not set")

### Configure session to use filesystem
##app.config["SESSION_PERMANENT"] = False
##app.config["SESSION_TYPE"] = "filesystem"
##Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

f=open("books.csv")
reader=csv.reader(f)
##print(reader[0])
next(reader)
for isbn,title,author,year in reader:
##    print(isbn)
##    print(title)
    db.execute("INSERT INTO books (isbn,title,author,year) VALUES (:isbn,:title,:author,:year)",
               {"isbn":isbn,"title":title,"author":author,"year":int(year)})
##    print (f"{isbn},{title},{author},{year}")
db.commit()

############################
##
##@app.route("/", methods=["GET","POST"])
##def index():
##    if request.method=="GET":
##        if "user_id" in session:
##            curr_user=db.execute("SELECT * FROM user_table WHERE id=:user_id",
##                        {"user_id":session["user_id"]}).fetchone()
##            print ("in index while logged in")
##            print (type("user_id"))
##            print (session)
##            return render_template("hello.html", name=curr_user.username)
##        else:
##            return render_template("index.html",message="")
##    else:
##        print ("in index while logged out")
##        print (session)
##        name=request.form.get("name")
##        passw=request.form.get("passw")
##        if name=="":
##            return render_template("error.html", message="Please fill in Name")
##        elif passw=="":
##            return render_template("error.html", message="Please fill in Password")
##
##        db.execute("INSERT INTO user_table (username, password) VALUES (:username, :password)",
##                    {"username":name,"password":passw})
##
##        info=db.execute("SELECT * FROM user_table").fetchall()
##        db.commit()
##
##        return render_template("index.html",message="User registered")
##
##
##notes=[]
##@app.route("/hello", methods=["POST"])
##def hello():
##    name=request.form.get("name")
##    passw=request.form.get("passw")
##    info=db.execute("SELECT * FROM user_table WHERE username=:name",
##                    {"name":name}).fetchone()
##    
##    if info==None or info.password!=passw:
##        return render_template("error.html", message="Username and/or Password do not match!")
##    else:
##        session["user_id"]=info.id
##        curr_user=db.execute("SELECT * FROM user_table WHERE id=:user_id",
##                        {"user_id":info.id}).fetchone()
##        print ("in hello while logged in")
##        print (session["user_id"])
##        print (session)
##        return render_template("hello.html", name=curr_user.username)
##
##@app.route("/register", methods=["GET","POST"])
##def register():
##    name=request.form.get("name")
##    passw=request.form.get("passw")
##    return render_template("register.html", name=name,passw=passw)
##
##@app.route("/logout") ##, methods=["POST"])
##def logout():
##    session.pop("user_id",None)
##    print ("in logout while logged out")
##    print (session)
##    return render_template("index.html",message="You have been logged out")

