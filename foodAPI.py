from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pymysql

app = FastAPI()

# ✅ CORS MUST BE HERE (TOP)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],   # 👈 THIS ALLOWS OPTIONS
    allow_headers=["*"],
)

# ======================
# DATABASE
# ======================
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="ranham307306",
        database="foodbase",
        cursorclass=pymysql.cursors.DictCursor
    )

# ======================
# MODELS
# ======================
class User(BaseModel):
    user_name: str
    password: str

class Product(BaseModel):
    id: int
    item_name: str
    item_count: int
    gst: float
    price: float
    cash_given: float

# ======================
# AUTH APIs
# ======================
@app.post("/signup")
def signup(user: User):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO user (user_name, password) VALUES (%s,%s)",
            (user.user_name, user.password)
        )
        conn.commit()
        conn.close()
        return {"message": "Signup successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login(user: User):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM user WHERE user_name=%s AND password=%s",
        (user.user_name, user.password)
    )
    result = cur.fetchone()
    conn.close()

    if result:
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# ======================
# PRODUCT APIs
# ======================
@app.post("/product")
def add_product(p: Product):
    amt = p.item_count * p.price
    total = amt + (amt * p.gst / 100)
    balance = p.cash_given - total

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO product
        (ID, item_name, item_count, gst, price, total, cash_given, balance)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (p.id, p.item_name, p.item_count, p.gst, p.price, total, p.cash_given, balance)
    )
    conn.commit()
    conn.close()
    return {"message": "Product added"}

@app.get("/product")
def get_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM product")
    data = cur.fetchall()
    conn.close()
    return data

@app.delete("/product/{id}")
def delete_product(id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM product WHERE ID=%s", (id,))
    conn.commit()
    conn.close()
    return {"message": "Product deleted"}
