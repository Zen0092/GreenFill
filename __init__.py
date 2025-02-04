from flask import Flask, render_template, request, redirect, url_for, jsonify
from Forms import createProductsForm, updateProductsForm
import shelve
import Product  # Assuming Product class is defined in this module
from werkzeug.utils import secure_filename
import os
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = 'secret key'


login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    with shelve.open(User.user_db_file) as db:
        users_dict = db.get('Users', {})
        user_data = users_dict.get(int(user_id))
        if user_data:
            return user_data  # User already has the correct ID from the database
    return None


@app.route('/')
def home():
    return render_template('home.html', user=current_user)


@app.route('/createUser', methods=['GET','POST'])
def create_user():
    create_user_form = CreateUserForm(request.form)
    if request.method == 'POST' and create_user_form.validate():
        users_dict = {}
        db = shelve.open('user.db', 'c')

        try:
            users_dict = db['Users']
        except:
            print('Error in retrieving Users from user.db')

        user = User(create_user_form.username.data, create_user_form.email.data, create_user_form.password.data)
        users_dict[user.get_user_id()] = user
        db['Users'] = users_dict
        print(users_dict)

        # Test codes
        users_dict = db['Users']
        user = users_dict[user.get_user_id()]
        print(user.get_username(), 'was stored in user.db successfully with the user__id==', user.get_user_id())

        db.close()

        return redirect(url_for('login'))
    return render_template('createUser.html', form=create_user_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LogInForm(request.form)

    if request.method == 'POST' and login_form.validate():
        email = login_form.email.data
        password = login_form.password.data

        with shelve.open(User.user_db_file) as db:
            users_dict = db.get('Users', {})

            user = None
            for user_id, user_data in users_dict.items():
                if user_data.get_email() == email:
                    if user_data.verify_password(password):
                        user = user_data

                        user.set_id(int(user_id))
                        login_user(user)
                        flash("successfully logged in!")
                        return redirect(url_for('home'))
                    else:
                        flash("Invalid email or password.")
                        break

    return render_template('login.html', form=login_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('home'))


@app.route('/retrieveUsers/<int:id>/')
@login_required
def retrieve_users(id):
    if current_user.get_user_id() != id and current_user.get_user_id() != 1:
        flash("You are not authorized to view this page.")
        return redirect(url_for('home'))

    users_dict = {}
    db = shelve.open('user.db', 'r')
    users_dict = db['Users']
    db.close()

    users_list = []
    if id == 1:
        for key in users_dict:
            user = users_dict.get(key)
            users_list.append(user)

    else:
        user = users_dict.get(id)
        if user:
            users_list.append(user)

    return render_template('retrieveUsers.html', count=len(users_list), users_list=users_list)


@app.route('/updateUser/<int:id>/', methods=['GET','POST'])
@login_required
def update_user(id):
    update_user_form = CreateUserForm(request.form)
    update_password_form = UpdatePasswordForm(request.form)
    # if request.method == 'POST' and update_user_form.validate():
    #     print("POST request received. Form validated.")  # Debug print
    if request.method == 'POST':
        if not update_user_form.validate():
            print("Form validation failed.")  # Debugging
            print(update_user_form.errors)  # Show errors to help debug
        else:
            print("POST request received. Form validated.")  # Debug print
        users_dict = {}
        db = shelve.open('user.db', 'w')
        users_dict = db['Users']

        user = users_dict.get(id)
        if user:
            user.set_username(update_user_form.username.data)
            user.set_email(update_user_form.email.data)
            # user.set_password(update_user_form.password.data)

            db['Users'] = users_dict
            db.close()

            print("User details updated. Redirecting...")  # Debug print
            # if current_user.get_user_id() == 1:  # Admin
            #     return redirect(url_for('retrieve_users', id=1))
            # #     # return redirect('/')
            # else:
            return redirect(url_for('retrieve_users', id=current_user.get_user_id()))
                # return redirect('/')
        else:
            print("User not found.")  # Debug if user is missing
            flash("User not found.")
            return redirect(url_for('home'))

    if update_password_form.validate():
        db = shelve.open('user.db', 'w')
        users_dict = db['Users']
        user = users_dict.get(id)

        if user:
            if not check_password_hash(user['password'], update_password_form.current_password.data):
                    flash("Current password is incorrect.")
            else:
                user['password'] = generate_password_hash(update_password_form.new_password.data)
                db['Users'] = users_dict
                db.close()

            flash("Password updated successfully.")
            return redirect(url_for('retrieve_users', id=current_user.get_user_id()))
        db.close()

    else:
        print("GET request to update user form.")  # Debug print
        users_dict = {}
        db = shelve.open('user.db', 'r')
        users_dict = db['Users']
        db.close()

        user = users_dict.get(id)
        if user:
            update_user_form.username.data = user.get_username()
            update_user_form.email.data = user.get_email()
            # update_user_form.password.data = user.get_password()

        return render_template('updateUser.html', form=update_user_form, password_form=update_password_form)


# @app.route('/updatePassword/<int:id>/', methods=['GET','POST'])
# @login_required
# def update_password(id):
#     update_password_form = UpdatePasswordForm(request.form)
#     if update_password_form.validate():
#         db = shelve.open('user.db', 'w')
#         users_dict = db['Users']
#         user = users_dict.get(id)
#
#         if user:
#             if not check_password_hash(user['password'], update_password_form.current_password.data):
#                 flash("Current password is incorrect.")
#             else:
#                 user['password'] = generate_password_hash(update_password_form.new_password.data)
#                 db['Users'] = users_dict
#                 db.close()
#
#             flash("Password updated successfully.")
#             return redirect(url_for('retrieve_users', id=current_user.get_user_id()))
#         db.close()
#     else:
#         return render_template('updateUser.html', password_form=update_password_form)

@app.route('/deleteUser/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    users_dict = {}
    db = shelve.open('user.db', 'w')
    users_dict = db['Users']

    users_dict.pop(id)

    db['Users'] = users_dict
    db.close()
    return redirect(url_for('retrieve_users',id=current_user.get_user_id()))

# Constants for quantity limits
MIN_QUANTITY = 1
MAX_QUANTITY = 100

# Define the upload folder relative to your project directory
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')

# Ensure the folder exists, if not, create it
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configure the upload folder and allowed extensions
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/')
def home():
    user_role = request.args.get('role', 'customer')  # Default to 'customer'
    return render_template('customer_dashboard.html', user_role=user_role)

@app.route('/staff_dashboard')
def staff_dashboard():
    user_role = 'staff'  # Set the user role for staff
    return render_template('staff_dashboard.html', user_role=user_role)

@app.route('/customer_dashboard')
def customer_dashboard():
    user_role = 'customer'  # Set the user role for customer
    return render_template('customer_dashboard.html', user_role=user_role)

@app.route('/retrieveProduct', methods=['GET'])
def retrieve_products():
    products_dict = {}
    db = shelve.open('product.db', 'r')
    products_dict = db.get('product', {})  # Safely retrieve 'product' or default to empty dict
    db.close()
    user_role = request.args.get('role', 'customer')  # Ensure user role is passed
    return render_template('retrieveProduct.html', products_list=products_dict.values(), count=len(products_dict), user_role=user_role)

@app.route('/createProduct', methods=['GET', 'POST'])
def create_product():
    create_product_form = createProductsForm(request.form)
    user_role = request.args.get('role', 'customer')  # Ensure user role is passed
    if request.method == 'POST' and create_product_form.validate():
        # Handle image file upload
        product_image_url = None
        if 'product_image' in request.files:
            file = request.files['product_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)  # Save the image file to the server
                product_image_url = file_path  # Store the path or URL to the image

        # Now create the product with the image URL if available
        db = shelve.open('product.db', 'c')  # Open in create mode
        products_dict = db.get('product', {})  # Safely retrieve 'product' or default to empty dict

        # Create product instance
        product = Product.Product(
            create_product_form.Product_name.data,
            create_product_form.Description.data,
            float(create_product_form.Price.data),
            product_image_url  # Pass the image URL to the Product class
        )

        # Add product to the dictionary
        products_dict[product.get_product_id()] = product
        db['product'] = products_dict  # Save the updated products dict
        db.close()  # Don't forget to close the db!

        print(f"Product added: {product.get_product_name()}")
        print("All products in DB: ", products_dict)  # Print to see the data

        return redirect(url_for('retrieve_products', role=user_role))  # Pass the role when redirecting

    return render_template('createProduct.html', form=create_product_form, user_role=user_role)

@app.route('/productPage', methods=['GET'])
def product_page():
    db = shelve.open('product.db', 'r')  # Open the shelve database in read mode
    products_dict = db.get('product', {})  # Retrieve stored products
    db.close()

    products_list = list(products_dict.values())  # Convert dict values to a list
    # Debugging: Print out the list of products
    print("Products List: ", products_list)

    return render_template('productPage.html', products_list=products_list)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Set the allowed file extensions for upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Route to upload a file
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')

        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            return redirect(url_for('upload_file'))  # Redirect to a success page or the same page

    return render_template('retrieveProduct')


@app.route('/updateProduct/<int:id>/', methods=['GET', 'POST'])
def update_product(id):
    update_product_form = updateProductsForm(request.form)
    user_role = request.args.get('role', 'customer')  # Ensure user role is passed

    # Retrieve the product to be updated
    db = shelve.open('product.db', 'r')
    products_dict = db['product']
    product = products_dict.get(id)
    db.close()

    if request.method == 'POST' and update_product_form.validate():
        # Update product details
        product.set_product_name(update_product_form.Product_name.data)
        product.set_price(update_product_form.Price.data)
        product.set_description(update_product_form.Description.data)

        # Handle image upload if a file is selected
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product.set_image(filename)  # Assuming you have a method to set the image in the Product class

        # Save updated product in database
        db = shelve.open('product.db', 'w')
        products_dict[id] = product
        db['product'] = products_dict
        db.close()

        return redirect(url_for('retrieve_products', role=user_role))  # Redirect after update

    # If the form is not submitted yet, populate it with existing product data
    update_product_form.Product_name.data = product.get_product_name()
    update_product_form.Price.data = product.get_price()
    update_product_form.Description.data = product.get_description()

    return render_template('updateProducts.html', form=update_product_form, user_role=user_role)

@app.route('/deleteProduct/<int:id>', methods=['POST'])
def delete_product(id):
    db = shelve.open('product.db', 'w')  # Open in write mode
    products_dict = db.get('product', {})  # Safely retrieve 'product'

    if id in products_dict:
        products_dict.pop(id)  # Remove product by ID
        db['product'] = products_dict  # Save updated products dict
    else:
        db.close()
        return "Product not found", 404  # Return an error if product ID is not found

    db.close()
    return redirect(
        url_for('retrieve_products', role=request.args.get('role', 'customer')))  # Pass the role when redirecting

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Invalid request format"}), 400

        quantity = data.get("quantity", 0)

        if quantity < MIN_QUANTITY:
            return jsonify({"status": "error", "message": f"Please select at least {MIN_QUANTITY} item."}), 400
        elif quantity > MAX_QUANTITY:
            return jsonify(
                {"status": "error", "message": f"Quantity cannot exceed {MAX_QUANTITY}. Please retype."}), 400

        return jsonify({"status": "success", "message": "Item added to cart successfully!"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run()
