import os
import json
import random
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from dotenv import load_dotenv
from data import products
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback-secret-key')

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'yourname@yourdomain.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])


mail = Mail(app)


# Email utility functions
def send_email_to_admin(subject, body, sender_email, sender_name):
    """Send form data to your email"""
    try:
        msg = Message(
            subject=f"Website Contact: {subject}",
            recipients=[app.config['MAIL_USERNAME']],  # Your email
            body=f"""
            New contact form submission:
            
            From: {sender_name}
            Email: {sender_email}
            
            Message:
            {body}
            """
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email to admin: {e}")
        return False

def send_confirmation_to_user(subject, body, recipient_email, recipient_name):
    """Send confirmation email to the user"""
    try:
        msg = Message(
            subject="Thank you for contacting GetYourGps",
            recipients=[recipient_email],
            body=f"""
            Dear {recipient_name},
            
            Thank you for contacting GetYourGps. We have received your message and will get back to you shortly.
            
            Your message:
            {body}
            
            Best regards,
            The GetYourGps Team
            """
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        return False

# Your existing routes
@app.route('/')
def index():
    return render_template('index.html', products=products[:9])

@app.route('/update')
def update():
    return render_template('map_update.html', products=products[:9])

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Create the full message body
        full_name = f"{first_name} {last_name}"
        full_message = f"""
        Name: {full_name}
        Email: {email}
        Phone: {phone}
        Subject: {subject}
        
        Message:
        {message}
        """
        
        # Send emails
        admin_sent = send_email_to_admin(subject, full_message, email, full_name)
        user_sent = send_confirmation_to_user(subject, message, email, full_name)
        
        if admin_sent and user_sent:
            flash('Your message has been sent successfully! We will get back to you soon.', 'success')
        else:
            flash('There was an error sending your message. Please try again later.', 'error')
        
        return redirect(url_for('contact'))
    
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

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        address = request.form.get('address')
        address2 = request.form.get('address2')
        city = request.form.get('city')
        zip_code = request.form.get('zipCode')
        state = request.form.get('state')
        country = request.form.get('country')
        phone = request.form.get('phone')
        payment_method = request.form.get('paymentMethod')
        order_notes = request.form.get('orderNotes')
        
        # Get cart items from hidden input
        cart_data = request.form.get('cartData', '[]')
        try:
            cart = json.loads(cart_data)
        except:
            cart = []
        
        # Create the full message body
        full_name = f"{first_name} {last_name}"
        full_message = f"""
        New Order Received:
        
        Customer: {full_name}
        Email: {email}
        Phone: {phone}
        Payment Method: {payment_method}
        
        Shipping Address:
        {address}
        {address2 if address2 else ''}
        {city}, {state} {zip_code}
        {country}
        
        Order Notes:
        {order_notes if order_notes else 'None'}
        
        Cart Items:
        """
        
        # Add cart items to message
        total = 0
        for item in cart:
            item_total = float(item['price']) * int(item['quantity'])
            total += item_total
            full_message += f"\n- {item['quantity']} x {item['name']}: ${item_total:.2f}"
        
        full_message += f"\n\nTotal: ${total:.2f}"
        
        # Send emails
        admin_sent = send_email_to_admin("New Order", full_message, email, full_name)
        user_sent = send_confirmation_to_user("Order Confirmation", 
                                             f"Thank you for your order. We will process it shortly.\n\nOrder Details:\n{full_message}", 
                                             email, full_name)
        
        if admin_sent and user_sent:
            flash('Your order has been placed successfully! You will receive a confirmation email shortly.', 'success')
            # Clear cart from localStorage using JavaScript
            return render_template('checkout_success.html')
        else:
            flash('There was an error processing your order. Please try again later.', 'error')
        
        return redirect(url_for('checkout'))
    
    return render_template('checkout.html')
@app.route('/map-update-submit', methods=['POST'])
def map_update_submit():
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    gps_model = request.form.get('gpsModel')
    phone = request.form.get('phone')
    
    # Create the full message body
    full_message = f"""
    Map Update Request:
    
    Name: {name}
    Email: {email}
    GPS Model: {gps_model}
    Phone: {phone}
    """
    
    # Send emails
    admin_sent = send_email_to_admin("Map Update Request", full_message, email, name)
    user_sent = send_confirmation_to_user("Map Update Request Received", 
                                         f"Thank you for your map update request. We will process it shortly.\n\nRequest Details:\n{full_message}", 
                                         email, name)
    
    if admin_sent and user_sent:
        # Return JSON response for AJAX handling
        return {'status': 'error', 'message': '500 Internal Server Error! Server encountered an error while downloading the files. Updates failed! Please contact support to update required files.'}
    else:
        return {'status': 'error', 'message': 'There was an error processing your request. Please try again later.'}

@app.route('/product/<int:id>')
def product_detail(id):
    # Find the product by id
    product = next((p for p in products if p['id'] == id), None)
    if product:
        # Pick 4 related products (excluding current one)
        related = [p for p in products if p['id'] != id]
        related_products = random.sample(related, min(4, len(related)))

        return render_template('product_detail.html', product=product, related_products=related_products)
    else:
        return "Product not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)