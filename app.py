from flask import Flask,redirect
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import flash
from bson.json_util import loads, dumps
from flask import make_response
import database as db
import authentication
import logging
import ordermanagement as om

app = Flask(__name__)

app.secret_key = b's@g@d@c0ff33!'


logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)


@app.route('/')
def index():
    return render_template('index.html', page="Index")

@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page="Products", product_list=product_list)

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))

    return render_template('productdetails.html', code=code, product=product)

@app.route('/branches')
def branches():
    branch_list = db.get_branches()
    return render_template('branches.html', page="Branches", branch_list=branch_list)

@app.route('/branch_details/<int:code>')
def branch_details(code):
    branch = db.get_branch(code)
    return render_template('branchdetails.html', branch=branch)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/auth', methods = ['GET', 'POST'])
def auth():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

    if not username or not password:
        error_message = "Incomplete login data. Please provide both username and password."
        return render_template('login.html', error_message=error_message)

    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if(is_successful):
        session["user"] = user
        return redirect('/')
    else:
        error_message = "Invalid username or password. Please try again."
        return render_template('login.html', error_message=error_message)

    
@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')

@app.route('/addtocart')
def addtocart():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    item=dict()
  

    item["qty"] = 1
    item["name"] = product["name"]
    item["subtotal"] = product["price"]*item["qty"]

    if(session.get("cart") is None):
        session["cart"]={}

    cart = session["cart"]
    cart[code]=item
    session["cart"]=cart
    return redirect('/cart')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/updatecart', methods=['POST'])
def update_cart():
    if request.method == 'POST':
        cart = session.get("cart", {})
        for code, item in cart.items():
            new_quantity = int(request.form.get(f'quantity_{code}', 1))
            if new_quantity > 0:
                cart[code]["qty"] = new_quantity
                cart[code]["subtotal"] = new_quantity * db.get_product(int(code))["price"]
            else:
                del cart[code]
        session["cart"] = cart
    return redirect('/cart')

@app.route('/removefromcart/<int:code>')
def remove_from_cart(code):
    if session.get("cart") is not None:
        cart = session["cart"]
        if str(code) in cart:
            del cart[str(code)]
            session["cart"] = cart
    return redirect('/cart')

@app.route('/checkout')
def checkout():
    
    om.create_order_from_cart()
    session.pop("cart",None)
    return redirect('/ordercomplete')

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')

@app.route('/past_orders')
def past_orders():
    username = session.get("user")["username"]
    past_orders = db.get_past_orders(username)
    if past_orders is None:
        past_orders = []
    return render_template('pastorders.html', page="Past Orders", past_orders=past_orders)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user' not in session:
      
        return redirect(url_for('login'))

    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

       
        username = session['user']['username']

     
        is_valid_login, user = authentication.login(username, old_password)

        if not is_valid_login:
            flash('Incorrect old password. Please try again.', 'error')
        elif new_password != confirm_password:
            flash('New password and confirmation do not match. Please try again.', 'error')
        else:
          
            db.update_password(username, new_password)
            flash('Password updated successfully!', 'success')
            return redirect(url_for('index'))

    return render_template('change_password.html', page="Change Password")

@app.route('/api/products',methods=['GET'])
def api_get_products():
    resp = make_response( dumps(db.get_products()) )
    resp.mimetype = 'application/json'
    return resp

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/api/products/<int:code>',methods=['GET'])
def api_get_product(code):
    resp = make_response(dumps(db.get_product(code)))
    resp.mimetype = 'application/json'
    return resp
