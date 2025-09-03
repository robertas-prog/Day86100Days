from flask import Flask, redirect, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Pagrindinis app, antra eilutė padeda rasti instance failą
app = Flask(__name__, instance_relative_config=True)
# makedirs kuria direktoriją, app.instance_path randa projekto folderį instance,
# exists_ok = true nurodo, kad jau esant, galima praleisti
os.makedirs(app.instance_path, exist_ok=True)
# Standartinis kodas. SQLite failas instance kataloge: <projektas>/instance/blog.db
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Posto modelis
class Post(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  author = db.Column(db.String(80), nullable=False)
  content = db.Column(db.Text, nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/")
def index():
  posts = Post.query.order_by(Post.id.desc()).all()
  return render_template("index.html", posts=posts)


@app.route("/new", methods=["GET", "POST"])
def new_post():
  if request.method == "POST":
    author = request.form.get("author", "").strip()
    content = request.form.get("content", "").strip()

    if not author or not content:
      # Neįvedus vieno iš laukų metama klaida "error", kuri Jinja sukuriama HTML faile,
      # Author arba Content turinys lieka vartotojui, vesti iš naujo nereikia.
      return render_template("new.html",
                             error="Užpildykite abu laukus.",
                             author=author,
                             content=content)
    # Pirmas author kairėje → lauko pavadinimas modelyje (Post.author).
    # Antras author dešinėje → kintamasis iš formos (request.form.get("author")).
    post = Post(author=author, content=content)
    db.session.add(post)
    db.session.commit()
    return redirect(url_for("index"))
  return render_template("index")

@app.route("/delete/<int:id>", methods=["POST"])
def delete_post(id):
  post = Post.query.get_or_404(id)
  db.session.delete(post)
  db.session.commit()
  return redirect(url_for("index"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    post = Post.query.get_or_404(id)

    if request.method == "POST":
        author = request.form.get("author", "").strip()
        content = request.form.get("content", "").strip()

        if not author or not content:
            # NIEKO NESUTEIKIAME į post.* kol klaida
            # Galite tiesiai perduoti formos reikšmes į šabloną:
            return render_template("edit.html", post=post,
                                   form_author=author,
                                   form_content=content,
                                   error="Užpildykite abu laukus."), 400

        # Tik čia, kai validuota, perrašome modelį
        post.author = author
        post.content = content
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("edit.html", post=post)




if __name__ == "__main__":
  with app.app_context():
    db.create_all()  # sukuria lenteles, jei dar nėra
  port = int(os.getenv("PORT", 81))  # Replit nustato PORT aplinkos kintamąjį
  app.run(host="0.0.0.0", port=port, debug=True)
