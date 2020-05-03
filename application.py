import os, requests
##Goodreads key: vRUBwL9EnCVMhnlDodgaGQ
##set FLASK_APP=application.py
##set FLASK_DEBUG=1
##set DATABASE_URL=postgres://tgbijznlsguunm:3e2cadcae814c852e2bb030a69778861b40e2464fffd93c2d2e0e13fa391f890@ec2-35-171-31-33.compute-1.amazonaws.com:5432/d34qc5t3k2slfi


from flask import Flask, session, render_template, request,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

##########################

def get_gr_info(book_isbn):
    res=requests.get("https://www.goodreads.com/book/review_counts.json",
                     params={"key":"vRUBwL9EnCVMhnlDodgaGQ","isbns":book_isbn})
    if res.status_code==200:
        data=res.json()
        gr_info=[data["books"][0]["average_rating"],data["books"][0]["work_ratings_count"]]
    else:
        gr_info=[]
    return gr_info

@app.route("/", methods=["GET","POST"])
def index():
    if request.method=="GET":
        if "user_id" in session:
            curr_user=db.execute("SELECT * FROM user_table WHERE id=:user_id",
                        {"user_id":session["user_id"]}).fetchone()
##            print ("in index while logged in")
##            print (type("user_id"))
##            print (session)
            return render_template("hello.html", name=curr_user.username)
        else:
            return render_template("index.html",message="")
    else:
##        print ("in index while logged out")
##        print (session)
        name=request.form.get("name")
        passw=request.form.get("passw")
        if name=="":
            return render_template("error.html", message="Please fill in Name")
        elif passw=="":
            return render_template("error.html", message="Please fill in Password")

        db.execute("INSERT INTO user_table (username, password) VALUES (:username, :password)",
                    {"username":name,"password":passw})

        info=db.execute("SELECT * FROM user_table").fetchall()
        db.commit()

        return render_template("index.html",message="User registered")


notes=[]
@app.route("/hello", methods=["POST"])
def hello():
    name=request.form.get("name")
    passw=request.form.get("passw")
    info=db.execute("SELECT * FROM user_table WHERE username=:name",
                    {"name":name}).fetchone()
    
    if info==None or info.password!=passw:
        return render_template("error.html", message="Username and/or Password do not match!")
    else:
        session["user_id"]=info.id
        curr_user=db.execute("SELECT * FROM user_table WHERE id=:user_id",
                        {"user_id":info.id}).fetchone()
##        print ("in hello while logged in")
##        print (session["user_id"])
##        print (session)
        return render_template("hello.html", name=curr_user.username)

@app.route("/register", methods=["GET","POST"])
def register():
    name=request.form.get("name")
    passw=request.form.get("passw")
    return render_template("register.html", name=name,passw=passw)

@app.route("/logout") ##, methods=["POST"])
def logout():
    session.pop("user_id",None)
##    print ("in logout while logged out")
##    print (session)
    return render_template("index.html",message="You have been logged out")

@app.route("/search", methods=["GET","POST"])
def search():
    search_text=request.form.get("search_text")
    order_by=request.form.get("order_by")
    if request.method=="GET":
        return render_template("search.html")
    else:
        books=db.execute("SELECT * FROM books WHERE (LOWER(title) LIKE LOWER(:search_t) OR (LOWER(author) LIKE LOWER(:search_t) OR (isbn LIKE :search_t)) )",
                        {"search_t":f"%{search_text}%"}).fetchall()
        
        return render_template("search.html",books=books)

@app.route("/book/<book_isbn>", methods=["GET","POST"])
def book(book_isbn):
    book=db.execute("SELECT * FROM books WHERE isbn=:isbn",
                    {"isbn":book_isbn}).fetchone()
    
    
    if request.method=="POST":
        reviewer_name=db.execute("SELECT username FROM user_table WHERE id=:id",
                                 {"id":session["user_id"]}).fetchone().username
        review=request.form.get("review")
        rating=request.form.get("rating")
        print(reviewer_name,review,rating,book.isbn)
        db.execute("INSERT INTO reviews (book_isbn,reviewer_name,review,rating) VALUES(:book_isbn,:reviewer_name,:review,:rating)",
                  {"book_isbn":book_isbn,"reviewer_name":reviewer_name,"review":review,"rating":rating})
        db.commit()
        
    if(db.execute("SELECT id FROM user_table JOIN reviews ON reviews.reviewer_name=user_table.username WHERE id=:id AND book_isbn=:isbn",
                  {"id":session["user_id"],"isbn":book_isbn}).fetchall()):
        reviewed=True

    else:
        reviewed=False
    reviews=db.execute("SELECT * FROM books JOIN reviews ON reviews.book_isbn=books.isbn WHERE isbn=:isbn",
                        {"isbn":book_isbn}).fetchall()

    gr_info=get_gr_info(book_isbn)
    return render_template("book.html", book=book,reviews=reviews,reviewed=reviewed,gr_info=gr_info)
        
@app.route("/api/<book_isbn>")
def book_api(book_isbn):
    book=db.execute("SELECT * FROM books WHERE isbn=:isbn",
                    {"isbn":book_isbn}).fetchone()
    if book==None:
        
        return jsonify({"error":"Invalid ISBN"}),404
    
    results = dict(book.items())
    gr_info=get_gr_info(book_isbn)
    if gr_info!=[]:
        results["review_count"]=gr_info[0]
        results["average_score"]=gr_info[1]
        
    return jsonify(results)
    
