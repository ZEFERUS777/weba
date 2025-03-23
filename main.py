from flask import Flask, render_template, request, redirect
from sqlalchemy import create_engine, MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shop.db" # Replace with your database URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "supersecretkey" # Change this to something more secure
db = SQLAlchemy(app)


"""Создание объекта LoginManager для авторизации пользователя"""
LogManager = LoginManager()
LogManager.init_app(app)
LogManager.login_view = "login"


class ShopMag(db.Model):
    __tablename__ = "shop"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    # Uncomment if you need a text field
    # text = db.Column(db.Text, nullable=False)
    


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)


@app.route("/")
def index():
    items = ShopMag.query.order_by(ShopMag.price).all()
    return render_template("index.html", data=items)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == 'POST':
        title = request.form["title"]
        price = request.form["price"]
        
        item = ShopMag(title=title, price=price)
        
        try:
            db.session.add(item)
            db.session.commit
            return redirect("/")
        except Exception as e:
            print(f"Error: {e}")
    else:
        return render_template("create.html")



if __name__ == "__main__":
    app.run(debug=True)