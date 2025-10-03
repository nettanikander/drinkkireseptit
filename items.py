import db
import sqlite3

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes.setdefault(title, []).append(value)

    return classes

def add_item(title, ingredients, recipe, user_id, classes):
    sql = """INSERT INTO items (title, ingredients, recipe, user_id)
            VALUES (?, ?, ?, ?)"""
    db.execute(sql, [title, ingredients, recipe, user_id])

    item_id = db.last_insert_id()

    sql = "INSERT INTO item_classes (item_id, title, value) VALUES (?, ? ,?)"
    for title, value in classes:
        db.execute(sql, [item_id, title, value])

def get_images(item_id):
    sql = "SELECT id FROM images WHERE item_id = ?"
    return db.query(sql, [item_id])

def add_image(item_id, image):
    sql = "INSERT INTO images (item_id, image) VALUES (?, ?)"
    db.execute(sql, [item_id, image])

def get_image(image_id):
    sql = "SELECT image FROM images WHERE id = ?"
    result = db.query(sql, [image_id])
    return result[0][0] if result else None

def remove_image(item_id, image_id):
    sql = "DELETE FROM images WHERE id = ? AND item_id = ?"
    db.execute(sql, [image_id, item_id])

def add_comment(item_id, user_id, comment):
    sql = """INSERT INTO comments (item_id, user_id, comment)
            VALUES (?, ?, ?)"""
    db.execute(sql, [item_id, user_id, comment])

def get_comments(item_id):
    sql = """SELECT comments.id, comments.comment, users.id user_id, users.username
             FROM comments, users
             WHERE comments.item_id = ? AND comments.user_id = users.id
             ORDER BY comments.id DESC"""
    return db.query(sql, [item_id])

def get_comment_by_id(comment_id):
    sql = "SELECT id, comment, user_id, item_id FROM comments WHERE id = ?"
    result = db.query(sql, [comment_id])
    return result[0] if result else None

def add_rating(item_id, user_id, score):
    sql = """INSERT INTO ratings(item_id, user_id, score)
             VALUES (?, ?, ?)"""

    try:
        db.execute(sql, [item_id, user_id, score])
    except sqlite3.IntegrityError:
        return False
    return True

def get_avg_rating(item_id):
    sql = "SELECT AVG(score) FROM ratings WHERE item_id = ?"
    result = db.query(sql, [item_id])
    return round(result[0][0], 1) if result and result[0][0] else None

def get_user_rating(item_id, user_id):
    sql = "SELECT id, score FROM ratings WHERE item_id = ? AND user_id = ?"
    result = db.query(sql, [item_id, user_id])
    return result[0] if result else None

def get_classes(item_id):
    sql = "SELECT title, value FROM item_classes WHERE item_id = ?"
    return db.query(sql, [item_id])

def get_items():
    sql = "SELECT id, title FROM items ORDER BY id DESC"
    return db.query(sql)

def get_item(item_id):
    sql = """SELECT items.id,
                    items.title,
                    items.ingredients,
                    items.recipe,
                    users.id user_id,
                    users.username
            FROM items, users
            WHERE items.user_id = users.id AND
                  items.id = ?"""
    result =  db.query(sql, [item_id])
    return result[0] if result else None

def update_item(item_id, title, ingredients, recipe, classes):
    sql = """UPDATE items SET title = ?,
                              ingredients = ?,
                              recipe = ? 
                          WHERE id = ?"""
    db.execute(sql, [title, ingredients, recipe, item_id])

    sql = "DELETE FROM item_classes WHERE item_id = ?"
    db.execute(sql, [item_id])

    sql = "INSERT INTO item_classes (item_id, title, value) VALUES (?, ? ,?)"
    for title, value in classes:
        db.execute(sql, [item_id, title, value])

def remove_rating_by_id(rating_id):
    sql = "DELETE FROM ratings WHERE id = ?"
    db.execute(sql, [rating_id])

def remove_comment(comment_id):
    sql = "DELETE FROM comments WHERE id = ?"
    db.execute(sql, [comment_id])

def remove_item(item_id):
    sql = "DELETE FROM ratings WHERE item_id = ?"
    db.execute(sql, [item_id])

    sql = "DELETE FROM comments WHERE item_id = ?"
    db.execute(sql, [item_id])

    sql = "DELETE FROM item_classes WHERE item_id = ?"
    db.execute(sql, [item_id])

    sql = "DELETE FROM items WHERE id = ?"
    db.execute(sql, [item_id])

def find_items(query):
    sql = """SELECT id, title
             FROM items
             WHERE title LIKE ? OR ingredients LIKE ?
             ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like])