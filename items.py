import db

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes

def add_item(title, ingredients, recipe, user_id, classes):
    sql = """INSERT INTO items (title, ingredients, recipe, user_id)
            VALUES (?, ?, ?, ?)"""
    db.execute(sql, [title, ingredients, recipe, user_id])

    item_id = db.last_insert_id()

    sql = "INSERT INTO item_classes (item_id, title, value) VALUES (?, ? ,?)"
    for title, value in classes:
        db.execute(sql, [item_id, title, value])

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

def update_item(item_id, title, ingredients, recipe):
    sql = """UPDATE items SET title = ?,
                              ingredients = ?,
                              recipe = ? 
                          WHERE id = ?"""
    db.execute(sql, [title, ingredients, recipe, item_id])

def remove_item(item_id):
    sql = "DELETE FROM items WHERE id = ?"
    db.execute(sql, [item_id])

def find_items(query):
    sql = """SELECT id, title
             FROM items
             WHERE title LIKE ? OR ingredients LIKE ?
             ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like])