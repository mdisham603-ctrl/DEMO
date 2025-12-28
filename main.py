from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymysql import connect

app = FastAPI(title="Billing Application API")

# ---------------- DB CONNECTION ----------------
def get_connection():
    return connect(
        host="localhost",
        user="root",
        password="ranham307306",
        database="foodbase"
    )

# ---------------- MODELS ----------------
class User(BaseModel):
    user_name: str
    password: str

class Product(BaseModel):
    ID: int
    item_name: str
    item_count: int
    gst: float
    price: float
    cash_given: float

# ---------------- USER APIs ----------------
@app.post("/signup")
def signup(user: User):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO user (user_name, password) VALUES (%s, %s)",
            (user.user_name, user.password)
        )
        conn.commit()
        conn.close()

        return {"message": "Signup successful! Please login now."}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login")
def login(user: User):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM user WHERE user_name=%s",
            (user.user_name,)
        )
        data = cur.fetchone()

        if data is None:
            raise HTTPException(status_code=401, detail="Invalid Username")

        cur.execute(
            "SELECT * FROM user WHERE user_name=%s AND password=%s",
            (user.user_name, user.password)
        )
        valid = cur.fetchone()
        conn.close()

        if valid:
            return {"message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid Password")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- PRODUCT APIs ----------------
@app.post("/product/add")
def add_item(p: Product):
    try:
        amt = p.item_count * p.price
        total = amt + (amt * p.gst / 100)
        balance = p.cash_given - total

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO product 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (p.ID, p.item_name, p.item_count, p.gst,
             p.price, total, p.cash_given, balance)
        )

        conn.commit()
        conn.close()

        return {
            "message": "Item added successfully",
            "total": total,
            "balance": balance
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/product/update/{id}")
def update_menu(id: int, item_name: str, item_count: int, price: float):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE product 
        SET item_name=%s, item_count=%s, price=%s 
        WHERE ID=%s
        """,
        (item_name, item_count, price, id)
    )

    conn.commit()
    affected = cur.rowcount
    conn.close()

    if affected == 0:
        raise HTTPException(status_code=404, detail="Invalid ID")

    return {"message": "Item updated successfully"}


@app.delete("/product/delete/{id}")
def delete_menu(id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM product WHERE ID=%s", (id,))
    conn.commit()
    affected = cur.rowcount
    conn.close()

    if affected == 0:
        raise HTTPException(status_code=404, detail="Invalid ID")

    return {"message": "Item deleted successfully"}


@app.get("/product/{id}")
def find_item(id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM product WHERE ID=%s", (id,))
    data = cur.fetchone()
    conn.close()

    if not data:
        raise HTTPException(status_code=404, detail="Item not found")

    return {
        "ID": data[0],
        "item_name": data[1],
        "item_count": data[2],
        "gst": data[3],
        "price": data[4],
        "total": data[5],
        "cash_given": data[6],
        "balance": data[7]
    }


@app.get("/products")
def print_info():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM product")
    rows = cur.fetchall()
    conn.close()

    return {"products": rows}
