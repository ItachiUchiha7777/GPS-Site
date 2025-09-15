from flask import Flask, render_template
from data import products  # Import products from data.py

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')

@app.route('/shop')
def shop():
    return render_template('shop.html', products=products)

@app.route("/privacy")
def privacy():
    return render_template('privacy.html')
@app.route("/terms")
def terms():
    return render_template('terms.html')

@app.route('/product/<int:id>')
def product_detail(id):
    # Find the product by id
    product = next((p for p in products if p['id'] == id), None)
    if product:
        return render_template('product_detail.html', product=product)
    else:
        return "Product not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
