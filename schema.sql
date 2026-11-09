-- ===========================================================
--  IT234 Cake Shop · โครงสร้างฐานข้อมูล (SQLite)
--  app.py จะรันไฟล์นี้ให้อัตโนมัติ ถ้ายังไม่มีไฟล์ cakeshop.db
--  หรือเปิดใน DB Browser for SQLite > Execute SQL แล้วรันเองก็ได้
-- ===========================================================

PRAGMA foreign_keys = ON;

-- หมวดหมู่เค้ก (1 หมวด มีได้หลายเค้ก)
CREATE TABLE IF NOT EXISTS categories (
  id   INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

-- เค้ก (แต่ละชิ้นอยู่ใน 1 หมวด หรือยังไม่มีหมวดก็ได้)
CREATE TABLE IF NOT EXISTS cakes (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT    NOT NULL,
  price       REAL    NOT NULL CHECK (price >= 0),
  image       TEXT,
  stock       INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
  category_id INTEGER REFERENCES categories(id)
);

-- ---------------- ข้อมูลตัวอย่าง ----------------
INSERT INTO categories (name) VALUES
  ('Chocolate'), ('Fruit'), ('Cheese cake'), ('Premium'), ('Birthday');

INSERT INTO cakes (name, price, image, stock, category_id) VALUES
  ('Chocolate Lava Cake',         120, 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c', 2,  1),
  ('Dark Chocolate Mousse',       150, 'https://images.unsplash.com/photo-1578985545062-69928b1d9587', 20, 1),
  ('Strawberry Shortcake',        135, 'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e', 10, 2),
  ('Blueberry Cheesecake',        160, 'https://images.unsplash.com/photo-1542826438-bd32f43d626f',   5,  3),
  ('New York Cheesecake',         140, 'https://images.unsplash.com/photo-1551024601-bec78aea704b',   3,  3),
  ('Burnt Cheesecake',            155, 'https://images.unsplash.com/photo-1588195538326-c5b1e9f80a1b', 0,  3),
  ('Gold Chocolate Cake',         290, 'https://images.unsplash.com/photo-1599785209796-786432b228bc', 1,  4),
  ('Royal Strawberry Crown Cake', 280, 'https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62', 4,  4);
