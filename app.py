import sqlite3, hashlib, base64, os, traceback
from flask import Flask, request, jsonify, make_response, render_template, redirect, url_for

app = Flask(__name__)
DB = os.path.join(os.path.dirname(__file__), "technova.db")

def db():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def md5(s): return hashlib.md5(s.encode()).hexdigest()

def init_db():
    if os.path.exists(DB): return
    c = db()
    c.executescript("""
    CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, email TEXT, rut TEXT);
    CREATE TABLE products(id INTEGER PRIMARY KEY, name TEXT, price INTEGER, stock INTEGER);
    CREATE TABLE coupons(code TEXT, pct INTEGER);
    CREATE TABLE orders(id INTEGER PRIMARY KEY, user_id INTEGER, total REAL, status TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE order_items(order_id INTEGER, product_id INTEGER, qty INTEGER, price INTEGER);
    CREATE TABLE reviews(id INTEGER PRIMARY KEY, product_id INTEGER, author TEXT, text TEXT);
    """)
    for u in [("admin","admin123","admin","admin@technova.cl","11.111.111-1"),
              ("ana","ana123","cliente","ana@mail.cl","12.345.678-5"),
              ("luis","luis123","cliente","luis@mail.cl","9.876.543-2")]:
        c.execute("INSERT INTO users(username,password,role,email,rut) VALUES(?,?,?,?,?)",(u[0],md5(u[1]),u[2],u[3],u[4]))
    for p in [("Placa madre B650",129990,10),("CPU Ryzen 5 7600",189990,8),("RAM DDR5 16GB",64990,25),
              ("SSD NVMe 1TB",79990,30),("Tarjeta de video RTX 4060",349990,5),("Fuente 650W 80+",59990,12)]:
        c.execute("INSERT INTO products(name,price,stock) VALUES(?,?,?)",p)
    c.execute("INSERT INTO coupons VALUES('BIENVENIDA10',10)")
    c.commit(); c.close()

def current_user():
    sid = request.cookies.get("sid")
    if not sid: return None
    try:
        uid, role = base64.b64decode(sid).decode().split(":")
        row = db().execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        return dict(row) if row else None
    except Exception:
        return None

# --- RUTAS DE PÁGINAS (FRONTEND) ---
@app.route("/")
def index():
    # Redirige la raíz al catálogo
    return redirect(url_for("catalogo"))

@app.route("/catalogo")
def catalogo():
    q = request.args.get("q", "")
    # VULNERABILIDAD: Inyección SQL en la búsqueda
    rows = db().execute(f"SELECT * FROM products WHERE name LIKE '%{q}%'").fetchall()
    return render_template("catalogo.html", products=rows, user=current_user(), q=q)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u, p = request.form.get("username",""), request.form.get("password","")
        # VULNERABILIDAD: Inyección SQL en el Login
        row = db().execute(f"SELECT id,username,role FROM users WHERE username='{u}' AND password='{md5(p)}'").fetchone()
        if not row: 
            return render_template("login.html", error="Credenciales inválidas")
        
        r = make_response(redirect(url_for("index")))
        # VULNERABILIDAD: Cookie de sesión predecible e insegura (Base64)
        r.set_cookie("sid", base64.b64encode(f"{row['id']}:{row['role']}".encode()).decode())
        return r
    return render_template("login.html", user=current_user())

@app.route("/logout")
def logout():
    r = make_response(redirect(url_for("index")))
    r.delete_cookie("sid")
    return r

@app.route("/carrito")
def carrito():
    return render_template("carrito.html", user=current_user())

# --- RUTAS API (BACKEND PARA LÓGICA DE NEGOCIO) ---

@app.route("/api/checkout", methods=["POST"])
def checkout():
    u = current_user()
    if not u: return jsonify(error="Debe iniciar sesión"), 401
    d = request.get_json(); c = db(); total = 0
    
    # VULNERABILIDAD BLV: El cliente envía el precio de los productos
    for it in d.get("items", []):
        total += it["price"] * it["qty"]
    for code in d.get("coupons", []):
        cp = c.execute("SELECT pct FROM coupons WHERE code=?", (code,)).fetchone()
        if cp: total -= total * cp["pct"] / 100
        
    cur = c.execute("INSERT INTO orders(user_id,total,status) VALUES(?,?,'pagado')", (u["id"], total))
    oid = cur.lastrowid
    for it in d.get("items", []):
        c.execute("INSERT INTO order_items VALUES(?,?,?,?)", (oid, it["id"], it["qty"], it["price"]))
        c.execute("UPDATE products SET stock=stock-? WHERE id=?", (it["qty"], it["id"]))
    c.commit()
    return jsonify(order_id=oid, total=total)

# ====== NUEVAS RUTAS: perfil, pedidos y administración (BASELINE, vulnerables) ======

# Datos del perfil de la cuenta activa
@app.route("/api/me")
def api_me():
    u = current_user()
    if not u: return jsonify(error="Debe iniciar sesión"), 401
    return jsonify(id=u["id"], username=u["username"], role=u["role"], email=u["email"], rut=u["rut"])

# Historial de pedidos del usuario autenticado
@app.route("/api/orders")
def api_orders():
    u = current_user()
    if not u: return jsonify(error="Debe iniciar sesión"), 401
    rows = db().execute("SELECT id,total,status,created FROM orders WHERE user_id=? ORDER BY id DESC", (u["id"],)).fetchall()
    return jsonify([dict(r) for r in rows])

# Detalle de un pedido
@app.route("/api/orders/<int:oid>")
def api_order_detail(oid):
    u = current_user()
    if not u: return jsonify(error="Debe iniciar sesión"), 401
    # VULNERABILIDAD IDOR: no verifica que el pedido sea del usuario
    o = db().execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone()
    if not o: return jsonify(error="No existe"), 404
    items = db().execute("SELECT * FROM order_items WHERE order_id=?", (oid,)).fetchall()
    d = dict(o); d["items"] = [dict(i) for i in items]
    return jsonify(d)

# Listado de usuarios (SOLO ADMIN) - [MITIGADO C-01]
@app.route("/api/admin/users")
def api_admin_users():
    u = current_user()
    if not u: return jsonify(error="Debe iniciar sesión"), 401
    
    # PARCHE C-01: Validación estricta de rol en el backend
    if u.get("role") != "admin":
        return jsonify(error="Acceso denegado. Se requieren privilegios de administrador."), 403
        
    # PARCHE EXTRA (Fuga de datos): Ya no consultamos la columna 'password'
    rows = db().execute("SELECT id, username, role, email, rut FROM users").fetchall()
    return jsonify([dict(r) for r in rows])

# Modificar precio o stock de un producto (SOLO ADMIN) - [MITIGADO C-01]
@app.route("/api/admin/products/<int:pid>", methods=["POST"])
def api_admin_edit_product(pid):
    u = current_user()
    if not u: return jsonify(error="Debe iniciar sesión"), 401
    
    # PARCHE C-01: Validación estricta de rol en el backend
    if u.get("role") != "admin":
        return jsonify(error="Acceso denegado. Se requieren privilegios de administrador."), 403
        
    d = request.get_json()
    c = db()
    prod = c.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    if not prod: return jsonify(error="No existe"), 404
    price = d.get("price", prod["price"])
    stock = d.get("stock", prod["stock"])
    c.execute("UPDATE products SET price=?, stock=? WHERE id=?", (price, stock, pid))
    c.commit()
    return jsonify(id=pid, price=price, stock=stock)

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)