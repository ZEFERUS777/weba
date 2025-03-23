from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shop.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "supersecretkey"  # Замените на случайный ключ в продакшене

db = SQLAlchemy(app)

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class ShopMag(db.Model):
    __tablename__ = "shop"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Загрузчик пользователя
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Маршруты
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
@login_required
def about():
    return render_template("about.html")

@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        try:
            item = ShopMag(
                title=request.form["title"],
                price=request.form["price"]
            )
            db.session.add(item)
            db.session.commit()
            return redirect(url_for("index"))
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()
    return render_template("create.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            email = request.form.get("email")
            username = request.form.get("username")
            password = request.form.get("password")

            # Проверка уникальности
            if User.query.filter((User.email == email) | (User.username == username)).first():
                return render_template("register.html", error="Пользователь уже существует")

            new_user = User(email=email, username=username)
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("index"))

        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            return render_template("register.html", error="Ошибка регистрации")
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("/"))
        
        return render_template("login.html", error="Неверные учетные данные")
    
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# Инициализация БД
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
    