import secrets
import sqlite3
from flask import Flask
from flask import abort, make_response, redirect, render_template, flash, request, session
import config
import db
import items
import users
import markupsafe

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route("/")
def index():
    all_items = []
    for row in items.get_items():
        item = dict(row)
        item["avg_score"] = items.get_avg_rating(item["id"])
        all_items.append(item)

    return render_template("index.html", items=all_items)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    items = users.get_items(user_id)
    return render_template("show_user.html", user=user, items=items)

@app.route("/find_item")
def find_item():
    query = request.args.get("query")
    if query:
        results = items.find_items(query)
    else:
        query = ""
        results = []
    return render_template("find_item.html", query=query, results=results)

@app.route("/item/<int:item_id>")
def show_item(item_id):
    item = items.get_item(item_id)
    if not item:
        abort(404)
    classes = items.get_classes(item_id)
    comments = items.get_comments(item_id)
    average_ra = items.get_avg_rating(item_id)
    images = items.get_images(item_id)
    user_rating = None
    if "user_id" in session:
        user_rating = items.get_user_rating(item_id, session["user_id"])

    return render_template("show_item.html", item=item, classes=classes, comments=comments, average_ra=average_ra, 
    user_rating=user_rating, images=images)

@app.route("/image/<int:image_id>")
def show_image(image_id):
    image = items.get_image(image_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response

@app.route("/new_item")
def new_item():
    require_login()
    classes = items.get_all_classes()
    return render_template("new_item.html", classes=classes)

@app.route("/create_item", methods=["POST"])
def create_item():
    require_login()
    check_csrf()

    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    ingredients = request.form["ingredients"]
    if not ingredients or len(ingredients) > 1200:
        abort(403)
    recipe = request.form["recipe"]
    if not recipe or len(recipe) > 1000:
        abort(403)
    user_id = session["user_id"]

    all_classes = items.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))

    items.add_item(title, ingredients, recipe, user_id, classes)

    item_id = db.last_insert_id()
    return redirect("/item/" + str(item_id))

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/rate_item/<int:item_id>", methods=["POST"])
def rate_item(item_id):
    require_login()
    check_csrf()

    score = int(request.form["score"])
    if score < 1 or score > 5:
        abort(403)

    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item:
        abort(403)
    user_id = session["user_id"]

    if not items.add_rating(item_id, user_id, score):
        flash("Olet jo arvostellut tämän reseptin. Poista ensin edellinen arvostelusi")

    return redirect("/item/" + str(item_id))

@app.route("/create_comment", methods=["POST"])
def create_comment():
    require_login()
    check_csrf()

    comment = request.form["comment"]
    if not comment or len(comment) > 500:
        abort(403)

    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item:
        abort(403)
    user_id = session["user_id"]

    items.add_comment(item_id, user_id, comment)

    return redirect("/item/" + str(item_id))

@app.route("/edit_item/<int:item_id>")
def edit_item(item_id):
    require_login()
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)
    all_classes = items.get_all_classes()
    classes = {}
    for my_class in all_classes:
        classes[my_class] = ""
    for entry in items.get_classes(item_id):
        classes[entry["title"]] = entry["value"]

    return render_template("edit_item.html", item=item, classes=classes, all_classes=all_classes)

@app.route("/update_item", methods=["POST"])
def update_item():
    require_login()
    check_csrf()

    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    ingredients = request.form["ingredients"]
    if not ingredients or len(ingredients) > 1000:
        abort(403)
    recipe = request.form["recipe"]
    if not recipe or len(recipe) > 1000:
        abort(403)

    all_classes = items.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
       if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))

    items.update_item(item_id, title, ingredients, recipe, classes)

    return redirect("/item/" + str(item_id))

@app.route("/images/<int:item_id>")
def edit_images(item_id):
    require_login()
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)

    images = items.get_images(item_id)

    return render_template("images.html", item=item, images=images)

@app.route("/add_image", methods=["POST"])
def add_image():
    require_login()
    check_csrf()

    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)

    file = request.files["image"]
    if not file.filename.endswith(".jpg"):
        flash("Väärä tiedostomuoto", "error")
        return redirect("/add_image/" + str(item_id))

    image = file.read()
    if len(image) > 100 * 1024:
        flash("Liian suuri kuva", "error")
        return redirect("/add_image/" + str(item_id))


    items.add_image(item_id, image)
    return redirect("/item/" + str(item_id))

@app.route("/remove_images", methods=["POST"])
def remove_images():
    require_login()
    check_csrf()

    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)

    for image_id in request.form.getlist("image_id"):
        items.remove_image(item_id, image_id)

    return redirect("/user/" + str(item_id))

@app.route("/remove_rating/<int:item_id>", methods=["POST"])
def remove_rating(item_id):
    require_login()
    check_csrf()

    item = items.get_item(item_id)
    if not item:
        abort(404)

    user_id = session["user_id"]
    rating = items.get_user_rating(item_id, user_id)
    if not rating:
        abort(404)

    items.remove_rating_by_id(rating["id"])

    flash("Arvostelu poistettu", "succes")
    return redirect("/item/" + str(item_id))

@app.route("/remove_comment/<int:comment_id>", methods=["POST"])
def remove_comment(comment_id):
    require_login()
    check_csrf()

    user_id = session["user_id"]

    rem_comment = items.get_comment_by_id(comment_id)
    if not rem_comment:
        abort(404)

    if rem_comment["user_id"] != user_id:
        abort(403)

    items.remove_comment(comment_id)

    flash("Kommentti poistettu", "success")
    return redirect("/item/" + str(rem_comment["item_id"]))

@app.route("/remove_item/<int:item_id>", methods=["GET", "POST"])
def remove_item(item_id):
    require_login()

    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_item.html", item=item)

    if request.method == "POST":
        check_csrf()
        if "remove" in request.form:
            items.remove_item(item_id)
            return redirect("/")
        else:
            return redirect("/item/" + str(item_id))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    check_csrf()

    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if not username or not password1 or not password2:
        abort(403)
    if len(username) > 15 or len(password1) > 15 or len(password2) > 15:
        abort(403)

    if password1 != password2:
        flash("Salasanat eivät ole samat", "error")
        return render_template("register.html", username=username)

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("Tunnus on jo varattu", "error")
        return redirect("/register")

    flash("Tunnuksen luonti onnistui", "success")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            abort(403)
        if len(username) > 15 or len(password) > 15:
            abort(403)

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        else:
            flash("Väärä tunnus tai salasana", "error")
            return redirect("/login")

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")