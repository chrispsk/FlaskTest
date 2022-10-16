from ast import For
from tkinter.tix import INTEGER
import uuid
import yaml

from flask import Flask, flash, request, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
app.secret_key = 'junior_dev_test'
ORDER_DB = 'orders.yml'

class Form(FlaskForm):
    breed = StringField('breeeeeeeeeee', validators=[Length(min=3, max=10)])

with open('products.yml') as _f:
    PRODUCTS = yaml.safe_load(_f)
     


def record_order(product_id, product_name, product_price, buyer, amount_paid, change, denom):
    """Adds the order details to the ORDER_DB file"""
    order_id = str(uuid.uuid4()).split('-', 1)[0]
    orders = {
        order_id: {
            'product_id': product_id,
            'product_name': product_name,
            'product_price': product_price,
            'buyer': buyer,
            'amount_paid': amount_paid,
            'change': change,
            'denom': denom
        }
    }
    with open(ORDER_DB, 'a') as f:
        f.write(yaml.dump(orders, default_flow_style=False))


@app.route('/data', methods=['POST', 'GET'])
def data():
    form = Form()
    if request.method == 'POST':
        if form.validate_on_submit():
            breed = form.breed.data
            form.breed.data = ''
            print(breed)
            return render_template('test.html', form=form, breed=breed)
    return render_template('test.html', form=form)

@app.route('/', methods=['POST', 'GET'])
def index():
    context = {}
    
    if request.method == 'POST':
        # TODO: Validate and process the data entered in the form
        id_prod = request.form.get('product', type=int)

        product_name = PRODUCTS[id_prod]["name"]
        product_price = float(PRODUCTS[id_prod]["price"])
        buyer = request.form.get('buyer')
        amount_paid = request.form.get('paid', type=float)    
        change = amount_paid - product_price
        # Denom
        notes = (500, 200, 100, 50, 20, 10, 5, 2, 1)
        amount = change * 100 # total pence
        denom = ""
        for i in notes:
            num = amount//i
            print(num)
            print("Note Value : ", i,'\tnumber of notes ',num)
            if num != 0:
                denom += str(int(num)) + " x £" + str(i/100) + ", "
            amount = amount%i
        # IF ALL OK SAVE
        record_order(id_prod, product_name, product_price, buyer, amount_paid, change, denom)


        flash('Order Placed Successfully', 'success')
        return render_template('confirmation.jinja', order_id = id_prod, amount_paid = amount_paid, item_price = product_price, change_due = change, denom = denom)
    return render_template('index.jinja', products=PRODUCTS, title='Order Form', **context)

@app.route('/list/', methods=['GET'])
def list_prod():
    with open('orders.yml') as _f:
        prods = yaml.safe_load(_f)
    print(prods) 
    return render_template('list.jinja', title='Listing products', prods = prods)


@app.route('/confirmation/<order_id>/') # 6ad25f97
def confirmation(order_id): 
    with open(ORDER_DB) as f:
        orders = yaml.safe_load(f) or {}
    
    order = orders.get(order_id) # {'amount_paid': 456.0, 'buyer': 'Boss', 'change': 454.38, 'product_id': 0, 'product_name': 'Apples', 'product_price': 1.62}
    
    if order is None:
        # TODO: What should we do here?
        flash('There is no such product', 'warning')
        return redirect(url_for('list_prod'))
    else:
        context = {
        'order_id': order_id,
        'amount_paid': order.get('amount_paid'),
        'item_price': order.get('product_price'),
        'change_due': order.get('change'),
        'denom': order.get('denom')
    }

    # TODO: Get the context for the confirmation page. Add the display of the denominations here.
    return render_template('confirmation.jinja', title='Order Confirmationnn', **context)


if __name__ == '__main__':
    app.run(debug=True)
