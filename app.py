import os
import sqlite3

from flask import Flask, abort, redirect, render_template, request

app = Flask(__name__)

# ที่อยู่เต็มของไฟล์ฐานข้อมูล: อยู่โฟลเดอร์เดียวกับ app.py เสมอ
# (ถ้าเขียนแค่ "cakeshop.db" แล้วเปิดเว็บจากโฟลเดอร์อื่น จะได้ฐานข้อมูลเปล่าไฟล์ใหม่)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "cakeshop.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # SQLite ไม่ตรวจ FOREIGN KEY จนกว่าจะเปิดบรรทัดนี้ ต้องเปิดทุกครั้งที่เชื่อมต่อ
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# สร้างฐานข้อมูลจาก schema.sql ครั้งแรก (ถ้ายังไม่มีไฟล์ cakeshop.db)
def init_db():
    if os.path.exists(DB_PATH):
        return
    conn = get_db()
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


init_db()


# อ่านค่าจากฟอร์ม และตรวจก่อนบันทึก (อย่าเชื่อข้อมูลจากหน้าเว็บ 100%)
def read_cake_form():
    form = {
        "name": request.form.get("name", "").strip(),
        "price": request.form.get("price", "").strip(),
        "image": request.form.get("image", "").strip(),
        "stock": request.form.get("stock", "0").strip() or "0",
        "category_id": request.form.get("category_id", "").strip(),
    }
    if not form["name"]:
        return form, "กรุณากรอกชื่อเค้ก"
    try:
        form["price"] = float(form["price"])
    except ValueError:
        return form, "ราคาต้องเป็นตัวเลข"
    if form["price"] < 0:
        return form, "ราคาต้องไม่ติดลบ"
    try:
        form["stock"] = int(form["stock"])
    except ValueError:
        return form, "จำนวนคงเหลือต้องเป็นจำนวนเต็ม"
    if form["stock"] < 0:
        return form, "จำนวนคงเหลือต้องไม่ติดลบ"
    form["category_id"] = int(form["category_id"]) if form["category_id"].isdigit() else None
    form["image"] = form["image"] or None
    return form, None


# หน้าเมนู (Read: SELECT + JOIN)
@app.route("/")
def cakemenu():
    conn = get_db()
    cakes = conn.execute("""
        SELECT cakes.*, categories.name AS category_name
        FROM cakes
        LEFT JOIN categories ON cakes.category_id = categories.id
        ORDER BY cakes.id
    """).fetchall()
    conn.close()
    return render_template("cakemenu.html", cakes=cakes)


# เพิ่มเมนู (Create: INSERT)
@app.route("/append", methods=["GET", "POST"])
def append():
    conn = get_db()
    categories = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
    error, form = None, {}

    if request.method == "POST":
        form, error = read_cake_form()
        if not error:
            try:
                conn.execute(
                    "INSERT INTO cakes (name, price, image, stock, category_id) VALUES (?, ?, ?, ?, ?)",
                    (form["name"], form["price"], form["image"], form["stock"], form["category_id"]),
                )
                conn.commit()
                conn.close()
                return redirect("/")
            except sqlite3.IntegrityError as e:   # เช่น หมวดที่เลือกไม่มีอยู่จริง (FOREIGN KEY)
                error = "บันทึกไม่ได้: " + str(e)

    conn.close()
    return render_template("append.html", categories=categories, form=form, error=error)


# แก้ไขเมนู (Update: UPDATE ... WHERE id = ?)
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    categories = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
    cake = conn.execute("SELECT * FROM cakes WHERE id = ?", (id,)).fetchone()
    if cake is None:
        conn.close()
        abort(404)
    error = None

    if request.method == "POST":
        form, error = read_cake_form()
        if not error:
            try:
                conn.execute(
                    "UPDATE cakes SET name = ?, price = ?, image = ?, stock = ?, category_id = ? WHERE id = ?",
                    (form["name"], form["price"], form["image"], form["stock"], form["category_id"], id),
                )
                conn.commit()
                conn.close()
                return redirect("/")
            except sqlite3.IntegrityError as e:
                error = "บันทึกไม่ได้: " + str(e)
        cake = dict(form, id=id)   # แสดงค่าที่เพิ่งกรอกกลับไปในฟอร์ม

    conn.close()
    return render_template("edit.html", cake=cake, categories=categories, error=error)


# ลบเมนู (Delete: DELETE ... WHERE id = ?)
# ใช้ POST เท่านั้น: กันการลบโดยไม่ตั้งใจจากการเปิดลิงก์
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM cakes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
