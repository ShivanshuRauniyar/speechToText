from flask import Flask, render_template, request
import razorpay
import os

app = Flask(__name__)

# Replace these with your Razorpay test credentials
RAZORPAY_KEY_ID = "rzp_test_RabCipwRqE6OvD"
RAZORPAY_KEY_SECRET = "CRq63kgfFXVlnnG7dnxjhMzF"

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@app.route('/')
def index():
    return render_template('index.html', razorpay_key=RAZORPAY_KEY_ID)

@app.route('/create_order', methods=['POST'])
def create_order():
    amount = int(request.form['amount']) * 100  # Convert to paise
    currency = 'INR'
    payment_order = razorpay_client.order.create(dict(amount=amount, currency=currency, payment_capture='1'))
    order_id = payment_order['id']
    return render_template('index.html', razorpay_key=RAZORPAY_KEY_ID, order_id=order_id, amount=amount)

@app.route('/success', methods=['POST'])
def success():
    payment_id = request.form['razorpay_payment_id']
    order_id = request.form['razorpay_order_id']
    signature = request.form['razorpay_signature']

    # You can verify signature if needed
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })
        message = "Payment successful!"
    except razorpay.errors.SignatureVerificationError:
        message = "Payment verification failed!"

    return render_template('success.html', message=message)

if __name__ == "__main__":
    app.run(debug=True)
