import csv
import pyshorteners
import sqlalchemy
from flask import url_for, flash, send_from_directory
from werkzeug.utils import secure_filename, redirect
from Notification import email_manager
from forms import RegisterForm, GoogleForm, ForgotForm
from config import *
from itsdangerous import URLSafeTimedSerializer
from product_qrcode import generate_qrcode
from user_download.inventory_download import Inventory
from user_download.profile_download import Profile
# APP Configuration
def create_app():
    """App confiquration setup """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = APP_SECRET_KEY
    app.config["RECAPTCHA_PUBLIC_KEY"] = RECAPTCHA_PUBLIC_KEY
    app.config["RECAPTCHA_PRIVATE_KEY"] = RECAPTCHA_PRIVATE_KEY
    Bootstrap(app)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    ##Connect to Database

    app.config['SQLALCHEMY_DATABASE_URI'] =DATABASE_URL
    # app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

    db.app = app
    db.init_app(app)
    init_db(app)
    ADMIN_USER = User.query.filter_by(id=1).first()
    return (ADMIN_USER, app)

ADMIN_USER, app = create_app()

# with app.app_context():
#
#     flow = Flow.from_client_secrets_file(
#         client_secrets_file=client_secrets_file_path,
#         scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
#                 "openid"],
#         redirect_uri=redirect(url_for('callback'))
#     )




# Mail-System
Mail = email_manager.EmailManager()
# Serializer for forget api key
serializer = URLSafeTimedSerializer(APP_SECRET_KEY)

# Url - shortner for the link which inside it the token of the serializer because it's too long

shortner = pyshorteners.Shortener()


@app.errorhandler(404)
def page_not_found(e):
    """note that we set the 404 status explicitly that the page that the user is looking for is not found"""
    return render_template('error404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """note that we set the 500 status explicitly for internal error with a link for complain center"""
    link = url_for("complain_center", _external=True)
    return jsonify(response={
        'error_message': f"An UnExpected error has occurred please follow this link to raise a complain : {link}",
        "link": link},
        status="error")


@app.route("/complain_center")
@app.route("/complain")
def complain_center():
    """When an un expected error that is not handled the user complains"""
    return render_template('thanksPage.html', condition="redirecting", mail=MAIL_ME_ERROR_LINK)


@app.errorhandler(401)
def unauthorized(e):
    """note that we set the 401 status explicitly for google authentication"""
    return render_template('error404.html', condition='unauthorized'), 401


def google_login_is_required(function):
    """using google login required"""

    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


def get_user(api_key: str, admin: str):
    """Check if the user has an api key"""
    if api_key == None and admin == None:
        raise ValidationError("💡Api Key is needed for access")
    if not is_admin(admin) and api_key == None:
        raise ValidationError("💡You are not the Admin")
    elif is_admin(admin):
        return ADMIN_USER
    if api_key==None or api_key=="":
        raise ValidationError("💡Api Key is needed for access")

    if " " == api_key[0] and "+" != api_key[0]:
        api_key = "+" + api_key.strip()
    phone = api_key.split("_")[0]

    user = User.query.filter_by(phone=phone).first()
    if user == None:
        raise ValidationError("💡 Invalid Api Key please apply for an API Key")
    if check_password_hash(user.api_key, api_key.lower()):
        return user
    raise ValidationError("💡 Invalid Api Key please apply for an API Key")


def sign_up(email, name, form):
    """Signs up the user either by google sign up or manually"""
    session.clear()
    phone = str(form.phone.data).strip()
    country = str(form.country.data).title()
    status = str(form.status.data).title()
    gender = form.gender.data
    service = form.service.data
    company_url = form.company_url.data
    birth_date = form.birth_date.data

    # this + is added to all Phones for security reasons
    if "+" != phone[0]:
        phone = "+" + phone
    # Because a company doesn't have a gender nor a birth date
    if status == "Company":
        gender = None
        birth_date = None

        # Only for Contributors
        if COMPANY_END.lower() not in name.lower():
            flash("ask permission from osa.helpme@gmail.com")
        if COMPANY_END.lower() in name.lower():
            name = name.lower().replace(COMPANY_END.lower(), "")
            name = name.title()

        # Because a User doesn't have a service nor a company url
    elif status == "User":
        service = None
        company_url = None

    name_api = name.replace(" ", "_")
    user_api_key = f"{phone}_{WAREHOUSE_USER_API_KEY}_{name_api}${password_generator()}".lower()
    hash_and_salted_api_key = generate_password_hash(
        user_api_key, method='pbkdf2:sha256', salt_length=8)

    new_user = User(
        email=str(email).lower(),
        gender=str(gender).title(),
        name=str(name).title(),
        number_of_products=0,
        company_url=company_url,
        api_key=hash_and_salted_api_key,
        phone=phone,
        service=service,
        status=status,
        country=str(country).title(),
        birth_date=birth_date,
        since_date=get_date()  # means when did the user sign up
    )
    db.session.add(new_user)
    try:
        db.session.commit()
    except exc.IntegrityError as error_message:
        db.session.rollback()
        error_message = str(error_message)
        if "users.phone" in error_message:  # Phone was used before  ==> Unique
            flash("The Phone Number is used before")
        if "users.email" in error_message:  # Email was used before  ==> Unique
            flash("The Email-Address is used before")
        return redirect(url_for('get_api_key'))
    except:
        abort(500)
    message = f"Your API Key : {user_api_key}<br> <mark>please save it to be able to access the API <br>&<br>check your image attachment for<br> a Qr-code to check your inventory  </mark>"
    # generates a url that directs the user to his or her inventory to view their products
    inventory_link = url_for('get_my_products', api_key=user_api_key, _external=True)
    # generates a QR-Code that directs the user  to his or her inventory to view their products
    generate_qrcode(url=inventory_link)
    # An Email is sent with their api_key and qrcode
    Mail.send_email(subject="Warehouse API Key", html_file_path='./Notification/Email-Verification-Gmail-template.html',
                    first_name=name, last_name="", contacts=[MY_SUPPORT_EMAIL, email], message=message,
                    image_folder_path="./Notification/qr-code-store/images")
    return render_template('thanksPage.html', condition="", name=name)


@app.route('/registeration', methods=['GET', 'POST'])
@app.route('/api-key', methods=['GET', 'POST'])
@app.route('/sign-up', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def get_api_key():
    """User register for an api key manually"""
    form = RegisterForm()
    if request.method == "POST" and form.validate_on_submit():
        name = str(form.name.data).title()
        email = str(form.email.data).lower()
        return sign_up(email, name, form)

    return render_template('register.html', form=form)


@app.route("/google_register")
def google_register():
    """when google button is clicked"""
    try:
        authorization_url, state = flow.authorization_url()
        session["state"] = state
        return redirect(authorization_url)
    except:
        abort(500)


@app.route("/callback")
def callback():
    """when user finish signing up with google account"""
    try:
        flow.fetch_token(authorization_response=request.url)
        if not session["state"] == request.args["state"]:
            abort(500)  # State does not match!

        credentials = flow.credentials
        request_session = requests.session()
        cached_session = cachecontrol.CacheControl(request_session)
        token_request = google.auth.transport.requests.Request(session=cached_session)

        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=GOOGLE_CLIENT_ID
        )

        session["google_id"] = id_info.get("sub")

        # google account's name and email  is what obtained from the google sign-up way
        session["name"] = id_info.get("name")
        session["email"] = id_info.get("email")

        return redirect('/phone_register')
    except:
        abort(500)


@app.route("/phone_register", methods=['GET', 'POST'])
@google_login_is_required
def phone_register():
    """The rest of the essential information about the user after he or she used google sign-up """
    try:
        form = GoogleForm()
        if form.validate_on_submit() and request.method == "POST":
            return sign_up(str(session["email"]).lower(), str(session["name"]).title(), form)
        return render_template('register.html', form=form, condition="no_google")
    except:
        abort(500)


@app.route('/add/product', methods=["POST"])
def add_product():
    """User adds a Product if he has an api key or Admin and he must include all necessary parameters"""
    try:
        api_key = request.args.get("api_key")
        admin = request.args.get("admin")
        current_user = get_user(api_key, admin)
        product_id = (password_generator() + password_generator()).lower()
        product_id_copy = product_id
        release_date = request.args.get("release_date")
        secure = request.args.get("secure")
        if release_date == None:
            release_date = get_date()
        if secure == None or secure == False or secure.lower() == "false":
            secure = False
        else:
            secure = True
            product_id = generate_password_hash(product_id, method='pbkdf2:sha256', salt_length=8)

        new_product = Products(
            user_id=current_user.id,
            product_name=str(missing_param(request.args.get("product_name"), "product_name")).title(),
            brand=str(missing_param(request.args.get("brand"), "brand")).title(),
            category=str(missing_param(request.args.get("category"), "category")).title(),
            sub_category=request.args.get("sub_category"),  # Some companies doesn't have sub-categories option
            price=check_price(float(missing_param(request.args.get("price"), "price"))),
            img_url=is_url_image(missing_param(request.args.get("img_url"), "img_url")),
            available=check_available(missing_param(request.args.get("available"), 'available')),
            delivery=check_available(missing_param(request.args.get("delivery"), 'delivery')),
            product_description=is_abusive(missing_param(request.args.get("description"), "description")),
            currency=str(missing_param(request.args.get("currency"), "currency")).upper(),
            product_url=is_url(url=missing_param(request.args.get("product_url"), "product_url")),
            source_name=str(missing_param(request.args.get("source_name"), "source_name")).title(),
            rating=str(missing_param(request.args.get("rating"), "rating")),
            release_date=release_date,
            secure=secure,
            product_id=product_id)
        db.session.add(new_product)
        db.session.commit()
        current_user.number_of_products += 1
        db.session.commit()
    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except exc.IntegrityError as error_message:
        db.session.rollback()
        error_message = str(error_message)
        if "products.product_id" in error_message:
            return jsonify(response={"fail_message": "please retry again"}, status="fail")
        if "products.product_url" in error_message:
            return jsonify(response={"fail_message": "this product_url is already used before"}, status="fail")
        return jsonify(response={"fail_message": error_message}, status="fail")
    except:
        abort(500)
    else:
        if secure == True:
            # Generates a link for the product to be able to view it from the unhashed product_id_copy
            product_link = url_for("search_product_by_id", api_key=api_key, product_id=product_id_copy)
            # Generates a QR-code for the product to be able to view it
            generate_qrcode(url=product_link)

            message = f"Product Name:<br> {new_product.product_name}<br><br>Your Product id :<br> {product_id}<br> <mark>please save it so you can edit it later if you like <br>&<br>check your image attachment for<br> a Qr-code to check your inventory  </mark>"
            # send to the user an email with his product_id and qrcode
            Mail.send_email(subject="Warehouse API Key",
                            html_file_path='./Notification/Email-Verification-Gmail-template.html',
                            first_name=current_user.name, last_name="", contacts=[MY_SUPPORT_EMAIL, current_user.email],
                            message=message, image_folder_path="./Notification/qr-code-store/images"
                            )

        return jsonify(response={
            "success_message": f"Successfully added a {new_product.product_name} , Please Check Your email for the product_id so you can edit your product later if you like"},
            status='success')


@app.route("/all/users", methods=['GET'])
def get_all_users():
    """It Shows all the users to the Admin"""
    admin = request.args.get("admin")
    try:
        admin_user = get_user(api_key=None, admin=admin)
        users = db.session.query(User).all()
        all_users = []
        count = 0
        for user in users:
            all_users.append(user.to_dict())
            count += 1
        if count == 0:
            return jsonify(response={"fail_message": f"No Users Found"}, status="fail")
        return jsonify(response={"success_message": f"successfully found {count} users",
                                 "data": {"number_of_users": count, "users": all_users}}, status="success")

    except ValidationError as error_message:
        return jsonify(response={
            "error_message": "Page Not Found"}, status="Error")
    except:
        abort(500)


@app.route("/my/profile", methods=["GET"])
@app.route("/check/api/key", methods=["GET"])
def check_profile():
    """It checks if the api_key exists or no"""
    api_key = request.args.get("api_key")
    try:
        user = get_user(api_key=api_key, admin=None)
        return jsonify(response={"success_message": f"successfully found {user.name}",
                                 "data": user.to_dict()}, status="success")

    except ValidationError as error_message:
        return jsonify(response={
            "fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route("/all/companies", methods=['GET'])
def get_all_companies():
    """It Shows all the companies to the Users"""
    admin = request.args.get("admin")
    api_key = request.args.get("api_key")
    try:
        current_user = get_user(api_key=api_key, admin=admin)
        users = db.session.query(User).all()
        all_users = []
        count = 0
        for user in users:
            if user.status == "Company":
                all_users.append(user.to_dict())
                count += 1
        if count == 0:
            return jsonify(response={"fail_message": f"no companies are found"}, status="fail")
        return jsonify(response={"success_message": f"successfully found {count} companies",
                                 "data": {"number_of_users": count, "users": all_users}}, status="success")

    except ValidationError as error_message:
        return jsonify(response={
            "error_message": "Page Not Found"}, status="Error")
    except:
        abort(500)


@app.route("/all/products", methods=['GET'])
def get_all_product():
    """Show all the products in the Warehouse if he is a user with an api key or admin"""
    api_key = request.args.get("api_key")
    admin = request.args.get("admin")

    try:
        user = get_user(api_key=api_key, admin=admin)
        products = db.session.query(Products).all()
        all_products = []
        counter = 1
        for product in products:
            all_products.append(product.to_dict_with_owner(product.user, counter=counter))
            counter += 1

        if len(all_products) == 0:
            return jsonify(response={"fail_message": "no products are found",
                                     "data": {"products": all_products, "number_of_products": 0}}, status="fail")
        return jsonify(
            response={"success_message": f"all the products in the warehouse api",
                      "data": {"products": all_products, "number_of_products": counter - 1}},
            status="success")

    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route("/my/inventory", methods=['GET'])
def get_my_products():
    """Show the Owner products in the Warehouse if he is a user with an api key or admin"""
    api_key = request.args.get("api_key")
    admin = request.args.get("admin")

    try:
        user = get_user(api_key=api_key, admin=admin)
        products = user.products
        all_products = []

        # here i do a list inside a dictionary product_count:{product:product's info }
        counter = 1
        for product in products:
            all_products.append(product.to_dict(counter=counter))
            counter += 1

        if len(all_products) == 0:
            return jsonify(response={"fail_message": f"You don't have any Product",
                                     "data": {"products": all_products, 'number_of_products': 0}}, status="fail")
        return jsonify(response={"success_message": f"products in inventory and the owner info ",
                                 "data": {"products": all_products}, "owner": user.to_dict()}, status="success")

    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route("/search/category", methods=['GET'])
def search_product_by_category():
    """Show products by category filter in the Warehouse"""
    api_key = request.args.get("api_key")
    admin = request.args.get("admin")
    try:
        user = get_user(api_key=api_key, admin=admin)
        category = str(missing_param(request.args.get("category"), 'category')).title()
        products = db.session.query(Products).all()
        counter = 1
        all_products = []
        for product in products:
            if (category).lower() == (product.category).lower():
                all_products.append(product.to_dict_with_owner(product.user, counter=counter))
                counter += 1

        if len(all_products) == 0:
            return jsonify(response={"fail_message": f"invalid category",
                                     "data": {"products": all_products, 'number_of_products': 0}},
                           status="fail")

        return jsonify(response={"success_message": f"Products found by category",
                                 "data": {"products": all_products, 'number_of_products': counter - 1}},
                       status="success")
    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route("/search/product_name", methods=['GET'])
def search_product_by_name():
    """Show product by its name filter in the Warehouse"""
    api_key = request.args.get("api_key")
    admin = request.args.get("admin")
    try:
        user = get_user(api_key=api_key, admin=admin)
        product_name = str(missing_param(request.args.get("product_name"), 'product_name')).title()
        products = db.session.query(Products).all()
        counter = 1
        all_products = []
        # it returns a one product because a product_id is related to one product
        for product in products:
            if (product_name).lower() == (product.product_name).lower():
                all_products.append(product.to_dict_with_owner(product.user, counter=counter))
                counter += 1

        if len(all_products) == 0:
            return jsonify(response={"fail_message": f"Invalid product_name",
                                     "data": {"products": all_products, 'number_of_products': 0}}, status="fail")
        return jsonify(response={"success_message": f"Products Found",
                                 "data": {"products": all_products, 'number_of_products': counter - 1}},
                       status="success")
    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route("/search/similar/product_name", methods=['GET'])
def search_product_by_similar_name():
    """Show product by its name similar filter in the Warehouse"""
    api_key = request.args.get("api_key")
    admin = request.args.get("admin")
    try:
        user = get_user(api_key=api_key, admin=admin)
        product_name = str(missing_param(request.args.get("product_name"), 'product_name')).title()
        products = db.session.query(Products).all()
        counter = 1
        all_products = []
        # it returns a one product because a product_id is related to one product
        for product in products:
            if ((product_name).strip()).lower() in ((product.product_name).strip()).lower():
                all_products.append(product.to_dict_with_owner(product.user, counter=counter))
                counter += 1

        if len(all_products) == 0:
            return jsonify(response={"fail_message": f"Invalid product_name",
                                     "data": {"products": all_products, 'number_of_products': 0}}, status="fail")
        return jsonify(response={"success_message": f"Products Found",
                                 "data": {"products": all_products, 'number_of_products': counter - 1}},
                       status="success")
    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route("/search/product_brand", methods=['GET'])
def search_product_by_brand():
    """Show product by its name filter in the Warehouse"""
    api_key = request.args.get("api_key")
    admin = request.args.get("admin")
    try:
        user = get_user(api_key=api_key, admin=admin)
        product_brand = str(missing_param(request.args.get("product_brand"), 'product_brand')).lower()
        products = db.session.query(Products).all()
        counter = 1
        all_products = []
        # it returns a one product because a product_id is related to one product
        for product in products:
            if product_brand == (product.brand).lower():
                all_products.append(product.to_dict_with_owner(product.user, counter=counter))
                counter += 1

        if len(all_products) == 0:
            return jsonify(response={"fail_message": f"Invalid product_name",
                                     "data": {"products": all_products, 'number_of_products': 0}}, status="fail")
        return jsonify(response={"success_message": f"Products Found",
                                 "data": {"products": all_products, 'number_of_products': counter - 1}},
                       status="success")
    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route("/search/product/company", methods=['GET'])
def search_product_by_company():
    """Show product of a company"""
    api_key = request.args.get("api_key")
    admin = request.args.get("admin")
    try:

        user = get_user(api_key=api_key, admin=admin)
        company_name = str(missing_param(request.args.get("company_name"), 'company_name')).title()
        company = User.query.filter_by(name=company_name).first()
        products = company.products
        counter = 1
        all_products = []
        # it returns a one product because a product_id is related to one product
        for product in products:
            all_products.append(product.to_dict_with_owner(product.user, counter=counter))
            counter += 1

        if len(all_products) == 0:
            return jsonify(response={"fail_message": f"Invalid product_name",
                                     "data": {"products": all_products, 'number_of_products': 0}}, status="fail")
        return jsonify(response={"success_message": f"Products Found",
                                 "data": {"products": all_products, 'number_of_products': counter - 1}},
                       status="success")
    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route("/search/product_id", methods=['GET'])
def search_product_by_id():
    """Show product by its product_id filter in the Warehouse"""
    api_key = request.args.get("api_key")
    admin = request.args.get("admin")
    try:
        user = get_user(api_key=api_key, admin=admin)
        product_id = str(missing_param(request.args.get("product_id"), 'product_id')).title()
        products = db.session.query(Products).all()

        counter = 1
        all_products = []
        # it returns a one product because a product_id is related to one product
        for product in products:
            # if the product is originally secured by the user he can find his or her product_id send it by email with qrcode

            if check_available(product.secure) and check_password_hash((product.product_id).lower(),
                                                                       (product_id).lower()):
                all_products.append(product.to_dict_with_owner(product.user, counter=counter))
                counter += 1
            elif not check_available(product.secure) and (product.product_id).lower() == (product_id).lower():
                all_products.append(product.to_dict_with_owner(product.user, counter=counter))
                counter += 1

        if len(all_products) == 0:
            return jsonify(response={"fail_message": f"Invalid product_id",
                                     "data": {"products": all_products, 'number_of_products': 0}}, status="fail")
        return jsonify(response={"success_message": f"Products Found",
                                 "data": {"products": all_products, "number_of_products": counter - 1}},
                       status="success")

    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route("/search/price", methods=['GET'])
def search_product_by_price_filter():
    """Show product by its price filter in the Warehouse"""
    api_key = request.args.get("api_key")
    admin = request.args.get("admin")
    try:
        user = get_user(api_key=api_key, admin=admin)
        minimum = 0
        maximum = 1000000
        minimum = check_price(missing_param(request.args.get("min"), 'min'))
        maximum = check_price(missing_param(request.args.get("max"), 'max'))
        products = db.session.query(Products).all()
        counter = 1
        all_products = []
        for product in products:
            if minimum <= product.price and maximum >= product.price:
                all_products.append(product.to_dict_with_owner(product.user, counter=counter))
                counter += 1

        if len(all_products) == 0:
            return jsonify(response={"fail_message": f"no products are found",
                                     "data": {"products": all_products, 'number_of_products': 0}}, status="fail")

        return jsonify(response={"success_message": f"Products Found",
                                 "data": {"products": all_products, 'number_of_products': counter - 1}},
                       status="success")
    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route("/search/descending/name", methods=['GET'])
def search_product_by_name_descending_filter():
    """Show product by its name alphabetical descending in the Warehouse from the Z to A """
    api_key = request.args.get("api_key")
    admin = request.args.get("admin")
    try:
        user = get_user(api_key=api_key, admin=admin)

        query_obj = db.session.query(Products)
        desc_expression = sqlalchemy.sql.expression.desc(Products.product_name)
        products_decrease = query_obj.order_by(desc_expression)
        counter = 1
        all_products = []

        for product in products_decrease:
            all_products.append(product.to_dict_with_owner(product.user, counter=counter))
            counter += 1

        if len(all_products) == 0:
            return jsonify(response={"fail_message": f"no products are found",
                                     "data": {"products": all_products, 'number_of_products': 0}}, status="fail")

        return jsonify(response={"success_message": f"products are found from Z-A",
                                 "data": {"products": all_products, 'number_of_products': counter - 1}},
                       status="success")
    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)

@app.route("/search/ascending/name", methods=['GET'])
def search_product_by_name_ascending_filter():
    """Show product by its name alphabetical descending in the Warehouse from the A to Z """
    api_key = request.args.get("api_key")
    admin = request.args.get("admin")
    try:
        user = get_user(api_key=api_key, admin=admin)

        query_obj = db.session.query(Products)
        desc_expression = sqlalchemy.sql.expression.asc(Products.product_name)
        products_decrease = query_obj.order_by(desc_expression)
        counter = 1
        all_products = []

        for product in products_decrease:
            all_products.append(product.to_dict_with_owner(product.user, counter=counter))
            counter += 1

        if len(all_products) == 0:
            return jsonify(response={"fail_message": f"no products are found",
                                     "data": {"products": all_products, 'number_of_products': 0}}, status="fail")

        return jsonify(response={"success_message": f"products are found from A-Z",
                                 "data": {"products": all_products, 'number_of_products': counter - 1}},
                       status="success")
    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)



@app.route("/search/decrease/price", methods=['GET'])
def search_product_by_price_decreasing_filter():
    """Show product by its price decreasing in the Warehouse from the Expensive to the Cheap """
    api_key = request.args.get("api_key")
    admin = request.args.get("admin")
    try:
        user = get_user(api_key=api_key, admin=admin)

        query_obj = db.session.query(Products)
        desc_expression = sqlalchemy.sql.expression.desc(Products.price)
        products_decrease = query_obj.order_by(desc_expression)
        counter = 1
        all_products = []

        for product in products_decrease:
            all_products.append(product.to_dict_with_owner(product.user, counter=counter))
            counter += 1

        if len(all_products) == 0:
            return jsonify(response={"fail_message": f"no products are found",
                                     "data": {"products": all_products, 'number_of_products': 0}}, status="fail")

        return jsonify(response={"success_message": f"Products Found",
                                 "data": {"products": all_products, 'number_of_products': counter - 1}},
                       status="success")
    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)





@app.route("/search/increase/price", methods=['GET'])
def search_product_by_price_increasing_filter():
    """Show product by its price increasing in the Warehouse from the cheap to the expensive """
    api_key = request.args.get("api_key")
    admin = request.args.get("admin")
    try:
        user = get_user(api_key=api_key, admin=admin)
        query_obj = db.session.query(Products)
        desc_expression = sqlalchemy.sql.expression.asc(Products.price)
        products_decrease = query_obj.order_by(desc_expression)
        counter = 1
        all_products = []

        for product in products_decrease:
            all_products.append(product.to_dict_with_owner(product.user, counter=counter))
            counter += 1

        if len(all_products) == 0:
            return jsonify(response={"fail_message": f"no products are found",
                                     "data": {"products": all_products, 'number_of_products': 0}}, status="fail")

        return jsonify(response={"success_message": f"products are found",
                                 "data": {"products": all_products, 'number_of_products': counter - 1}},
                       status="success")
    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route("/search/price&category", methods=['GET'])
def search_product_by_price_and_category_filter():
    """Show product by its price & category filter in the Warehouse"""
    api_key = request.args.get("api_key")
    admin = request.args.get("admin")
    try:
        user = get_user(api_key=api_key, admin=admin)
        minimum = 0
        maximum = 1000000
        minimum = check_price(missing_param(request.args.get("min"), 'min'))
        maximum = check_price(missing_param(request.args.get("max"), 'max'))
        category = str(missing_param(request.args.get("category"), 'category'))
        products = db.session.query(Products).all()
        counter = 1
        all_products = []
        for product in products:
            if minimum <= product.price and maximum >= product.price and (product.category).lower() == (
                    category).lower():
                all_products.append(product.to_dict_with_owner(product.user, counter=counter))
                counter += 1

        if len(all_products) == 0:
            return jsonify(response={"fail_message": f"no products are  found",
                                     "data": {"products": all_products, 'number_of_products': 0}}, status="fail")

        return jsonify(response={"success_message": f"products are found",
                                 "data": {"products": all_products, 'number_of_products': counter - 1}},
                       status="success")
    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="success")
    except:
        abort(500)


@app.route("/update/user/name", methods=["PATCH"])
def update_user_name():
    """change user's name """
    try:

        new_name = missing_param(param=request.args.get("new_name"), param_name="new_name")
        admin = request.args.get("admin")
        api_key = request.args.get("api_key")
        user = get_user(api_key=api_key, admin=admin)
        if user.status == "User":
            for letter in new_name:
                if letter.isdigit():
                    raise ValidationError('Please write your Real Name without Digits!')
                elif not letter.isascii():
                    raise ValidationError('Please write your Real Name only letters!')
        if user.status == "Company":
            if not is_company(company_name=str(new_name)):
                raise ValidationError('Please Enter Your company name in the correct format and ending')

        user.name = new_name
        db.session.commit()
        return jsonify(response={"success_message": f"user name is changed to {new_name}", }, status="success")

    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="success")
    except:
        abort(500)


@app.route("/update/price", methods=["PATCH"])
def update_price():
    """it changes the price of a product it needs the id which is actually the product_id or product_name if the user owns the product or the admin have control and the name of the product to change the price  """
    try:

        new_price = missing_param(param=request.args.get("new_price"), param_name="new_price")  # http://127.0.0.1:5000/update_price?new_price=9
        new_price = check_price(new_price)
        product_id = request.args.get("product_id")
        product_name = request.args.get("product_name")
        admin = request.args.get("admin")
        api_key = request.args.get("api_key")
        user = get_user(api_key=api_key, admin=admin)
        if product_id == None and product_name == None:
            raise ValidationError("Product Id is required or if you the owner product_name is required")
        if product_name != None:
            product_name = str(product_name).title()
        products = Products.query.all()
        product_update = None
        for product in products:
            if (product_name != None and user == ADMIN_USER and (product_name).lower() == (product.product_name).lower()):
                product_update = product
                break

                # if the product is originally secured by the user he can find his or her product_id send it by email with qrcode
            if product_id != None and ((check_available(product.secure) == True and check_password_hash(product.product_id,product_id)) or (check_available(product.secure) == False and (product.product_id).lower() == (product_id).lower())) or ((product_name).lower() == (product.product_name).lower() and product in user.products):
                product_update = product
                break
        if product_update == None:
            raise ValidationError("Invalid product_id or Invalid product_name ")
        product_update.price = new_price
        db.session.commit()
        return jsonify(response={"success_message": f"Successfully updated the price of {product_update.product_name}"},
                       status="success")
    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route("/delete/product", methods=["DELETE"])
def delete_product():
    """it deletes a product it needs the id which is actually the product_id or the or the product name if the user is the owner of that product and the admin have access too"""
    try:
        product_id = request.args.get("id")
        product_name = request.args.get("product_name")
        admin = str(request.args.get("admin"))
        api_key = str(request.args.get("api_key"))
        user = get_user(api_key=api_key, admin=admin)
        if product_id == None and product_name == None:
            raise ValidationError("Product name or it's unique id is required")
        if product_name != None:
            product_name = str(product_name).title()
        products = Products.query.all()
        product_delete = None
        for product in products:
            if (admin != None and product_name != None and user == ADMIN_USER and (product_name).lower() == (
                    product.product_name).lower()):
                product_delete = product
                break
                # if the product is originally secured by the user he can find his or her product_id send it by email with qrcode

            if product_id != None and (
                    (check_available(product.secure) == True and check_password_hash((product.product_id).lower(),
                                                                                     (product_id).lower())) or (
                            check_available(product.secure) == False and (product.product_id).lower() == (
                            product_id).lower())) or (
                    (product_name).lower() == (product.product_name).lower() and product in user.products):
                product_delete = product
                break
        if product_delete == None:
            raise ValidationError("product is not found 'please recheck product_name or product_id params'")
        db.session.delete(product_delete)
        db.session.commit()

        # decreasing the number of the User's products
        user.number_of_products -= 1
        db.session.commit()
        return jsonify(
            response={"success_message": f"Successfully Deleted the Product called {product_delete.product_name}"},
            status="success")
    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route("/delete/user", methods=["DELETE"])
def delete_user():
    """It deletes  users only  Admin has access and by phone"""
    try:
        admin = request.args.get("admin")
        admin_user = get_user(api_key=None, admin=admin)
        phone = str(request.args.get("phone"))
        email = str(request.args.get("email")).lower()
        return delete_user_by_email_or_phone(phone=phone, email=email, admin=admin)

    except ValidationError as error_message:
        return jsonify(response={
            "Fail": f"{error_message}"})
    except:
        abort(500)


def delete_user_by_email_or_phone(phone: str, email: str, admin: str):
    """It gets the user by their Email or Phone number for deleting the user and his or her products"""
    try:
        admin_user = get_user(api_key=None, admin=admin)
        if email == None and phone == None:
            raise ValidationError("Phone number or Email is needed")

        if phone != None and ("+" != phone[0] and " " == phone[0]):
            phone = "+" + phone.strip()
        user_delete = None
        if phone != None:
            user_delete = User.query.filter_by(phone=phone).first()
        elif email != None:
            user_delete = User.query.filter_by(email=email.lower()).first()
        if user_delete == None or ADMIN_USER == user_delete:
            raise ValidationError("User is not Found")

        user_delete_info = user_delete.to_dict()
        user_delete_products = user_delete.products
        for product in user_delete_products:
            db.session.delete(product)

        db.session.commit()
        db.session.delete(user_delete)
        db.session.commit()
        return jsonify(response={"success_message": f"{user_delete_info}"}, status="Success")
    except ValidationError as error_message:
        return jsonify(response={
            "Fail": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route('/report/user', methods=['POST'])
def report_user():
    """The reporter reports me a user descriping his or her problem with a user"""
    try:
        api_key = request.args.get('api_key')
        reporter_user = get_user(api_key=api_key, admin=None)
        phone = str(missing_param(request.args.get("phone"), "phone"))
        email = str(missing_param(request.args.get("email"), "email")).lower()

        problem_description = str(missing_param(request.args.get("problem_description"), "problem_description"))
        if (phone == None and email == None):
            raise ValidationError("I need the other user's email or phone number")
        if len(problem_description) <= 10:
            raise ValidationError("Problem Description is too short ,please explain more ")
        reported_user = None
        if phone != None:
            if "+" != phone[0] and " " == phone[0]:
                phone = "+" + phone.strip()
            reported_user = User.query.filter_by(phone=phone).first()

        elif email != None:
            reported_user = User.query.filter_by(email=email).first()
        if reported_user == None:
            raise ValidationError("User is not found")
        message = f"{reporter_user.name} <br>has reported <br> {reported_user.name}<br>by<br>{problem_description} "
        Mail.send_email(subject="Report User",
                        html_file_path='./Notification/Email-Verification-Gmail-template.html',
                        first_name=reported_user.name, last_name="", contacts=[MY_SUPPORT_EMAIL, reported_user.email],
                        message=message)
        message = f"Thank you for your Co-operation , we will check the report as soon as possible"
        Mail.send_email(subject="Report User",
                        html_file_path='./Notification/Email-Verification-Gmail-template.html',
                        first_name=reporter_user.name, last_name="", contacts=[MY_SUPPORT_EMAIL, reporter_user.email],
                        message=message)
        return jsonify(response={
            "success_message": f"Successfully Reported {reported_user.name}",
            "problem_description": problem_description}, status="success")

    except ValidationError as error_message:
        return jsonify(response={
            "fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route('/report/product', methods=['POST'])
def report_product():
    """The reporter reports me a user describing his or her problem with a user"""
    try:
        api_key = request.args.get('api_key')
        reporter_user = get_user(api_key=api_key, admin=None)
        product_name = str(missing_param(request.args.get('product_name'), 'product_name'))

        problem_description = str(
            is_abusive(text=missing_param(request.args.get("problem_description"), "problem_description")))

        if len(problem_description) <= 10:
            raise ValidationError("Problem Description is too short ,please explain more ")

        reported_product = Products.query.filter_by(product_name=product_name).first()

        if reported_product == None:
            raise ValidationError("Product is not found")

        message = f"{reporter_user.name} <br>has reported <br> {reported_product.user.name}<br>by<br>{problem_description} "
        Mail.send_email(subject=f"Report {reported_product.product_name}",
                        html_file_path='./Notification/Email-Verification-Gmail-template.html',
                        first_name=reported_product.user.name, last_name="",
                        contacts=[MY_SUPPORT_EMAIL, reported_product.user.email], message=message)
        message = f"Thank you for your Co-operation , we will check the report as soon as possible"
        Mail.send_email(subject=f"Report {reported_product.product_name}",
                        html_file_path='./Notification/Email-Verification-Gmail-template.html',
                        first_name=reporter_user.name, last_name="", contacts=[MY_SUPPORT_EMAIL, reporter_user.email],
                        message=message)
        return jsonify(response={
            "success_message": f"Successfully Reported {product_name}",
            "problem_description": problem_description}, status="success")

    except ValidationError as error_message:
        return jsonify(response={
            "fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route("/email/users")
def send_emails_to_all_users():
    """Send Emails to all Users """
    try:
        admin = request.args.get('admin')
        admin_user = get_user(api_key=None, admin=admin)
        users = db.session.query(User).all()
        message = missing_param(param=request.args.get('message'), param_name='message')
        users_count = 0
        for user in users:
            users_count += 1
            Mail.send_email(subject="Warehouse API News",
                            html_file_path='./Notification/Email-Verification-Gmail-template.html',
                            first_name=user.name, last_name="", contacts=user.email, message=message)

        return jsonify(response={
            "success_message": f"Email is Sent to {users_count} Users"}, status="success")
    except ValidationError as error_message:
        return jsonify(response={
            "fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route('/forgot/api_key', methods=['GET', "POST"])
def forgot_api_key():
    """it sends a link to the user by email so he can see his new api_key """
    try:
        form = ForgotForm()
        if form.validate_on_submit() and request.method == "POST":
            email = str(form.email.data).lower()
            phone = str(form.phone.data)
            user = User.query.filter_by(email=email).first()
            if user == None or phone != user.phone:
                flash("Invalid Data")
                return render_template('register.html', condition='no_google', forgot=True, form=form)

            token = serializer.dumps(email, salt='change-api-key')
            link = url_for('found_api_key', token=token, id=user.id, _external=True)
            shorted_link = shortner.tinyurl.short(link)  #  shortened the link because it was lengthy
            message = f"Please open this link to get a new API Key:\n {shorted_link} "
            Mail.send_email(subject="Warehouse API Key",
                            html_file_path='./Notification/Email-Verification-Gmail-template.html',
                            first_name=user.name, last_name="", contacts=[MY_SUPPORT_EMAIL, email], message=message)
            return render_template('thanksPage.html', condition="check_your_email", name=user.name)

        return render_template('register.html', form=form, condition='no_google', forgot=True)
    except:
        abort(500)


@app.route('/found/api_key/<token>/<int:id>', methods=["GET", "POST"])
def found_api_key(token, id):
    """found api_key token page with a token that expires in an hour"""

    try:
        email = serializer.loads(token, salt='change-api-key', max_age=3600)
        user = User.query.filter_by(id=id).first()
        new_api_key = update_api_key(user=user)
        if request.method == "POST":
            return redirect(url_for('get_api_key'))
        return render_template('thanksPage.html', name=user.name, message=f"Your new Api key: {new_api_key}",
                               condition="found_api_key")
    except:
        # means token expired
        # flash("Token Expired")
        abort(404)


def update_api_key(user) -> str:
    """Updates the api Key and commits it"""
    name = str(user.name).title()
    name_api = name.replace(" ", "_")
    new_api_key = f"{user.phone}_{WAREHOUSE_USER_API_KEY}_{name_api}${password_generator()}".lower()
    hash_and_salted_api_key = generate_password_hash(
        new_api_key, method='pbkdf2:sha256', salt_length=8)
    user.api_key = hash_and_salted_api_key
    db.session.commit()
    return new_api_key


@app.route("/download/profile")
def download_profile():
    """The user downloads his or her  User  Profile"""
    api_key = request.args.get("api_key")
    admin = request.args.get("admin")

    try:
        user = get_user(api_key=api_key, admin=admin)
        user = [user.to_dict_save()]
        if len(user) == 0 or user == [None]:
            return jsonify(response={"fail_message": f"You don't have any Product"}, status="fail")
        profile = Profile(my_profile=user)
        # it prepares the csv file containing all_products structured by panda and save it in the static folder
        profile.prepare_data()
        return send_from_directory(app.static_folder,
                                   'files/user_profile.csv', as_attachment=True)

    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")


@app.route("/download/inventory")
def download_inventory():
    """The user downloads his or her inventory of products he or she own"""
    api_key = request.args.get("api_key")
    admin = request.args.get("admin")

    try:
        user = get_user(api_key=api_key, admin=admin)
        products = user.products
        all_products = [product.to_dict_save() for product in products]
        if len(all_products) == 0 or all_products == [None]:
            return jsonify(response={"fail_message": f"You don't have any Product"}, status="fail")
        inventory = Inventory(my_products=all_products)
        # it prepares the csv file containing all_products structured by panda and save it in the static folder
        inventory.prepare_data()
        return send_from_directory(app.static_folder,
                                   'files/user_inventory.csv', as_attachment=True)

    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


def read_page_data(name):
    """Reads the Inventory in the excel or csv file of the user or company if it was well formatted"""
    TITLES = ["Product Name", "Product Currency", "Product Price", "Product Brand", "Product Description",
              "Product Page Link", "Product Image Link", "Category", "Sub-Category", "Rating", "Source", "Available",
              "Delivery", "Release Date"]
    with open(f'./uploads/{name}', newline='') as file:
        reader = csv.reader(file)
        all_products_info = []
        i = 0
        for row in reader:
            if i == 0:
                if row != TITLES:
                    raise ValidationError(f"The File have to be formated in this way {TITLES}")
                i += 1
                continue
            all_products_info.append(row)
    return all_products_info


@app.route('/uploads/<name>/<api_key>')
def download_file(name, api_key):
    """It Downloads the uploaded file to do some operations"""
    send_from_directory(app.config["UPLOAD_FOLDER"], name)
    try:
        all_inventory_products = read_page_data(name=name)

        if os.path.exists(
                f'./uploads/{name}'):  # it deletes the file because it became useless now  so it wont get over crowded
            os.remove(f'./uploads/{name}')

        counter = 0
        error_message = ""
        fall_backs = []
        add_product_link = url_for("add_product", _external=True)
        for product in all_inventory_products:
            counter += 1
            product_name = product[0]
            product_currency = product[1]
            product_price = product[2]
            product_brand = product[3]
            product_description = product[4]
            product_page_url = product[5]
            product_image_url = product[6]
            product_category = product[7]
            product_sub_category = product[8]
            product_rating = product[9]
            product_source_name = product[10]
            product_available = product[11]
            product_delivery = product[12]
            product_release_date = product[13]

            product_counter = f"product_{counter}"

            products_params = {}  # first product is product_1
            products_params[product_counter] = {'api_key': api_key}
            products_params[product_counter]["product_name"] = product_name
            products_params[product_counter]["brand"] = product_brand
            products_params[product_counter]["category"] = product_category
            products_params[product_counter]["sub_category"] = product_sub_category
            products_params[product_counter]["price"] = product_price
            products_params[product_counter]["img_url"] = product_image_url
            products_params[product_counter]["available"] = product_available
            products_params[product_counter]["delivery"] = product_delivery
            products_params[product_counter]["description"] = product_description
            products_params[product_counter]["currency"] = product_currency
            products_params[product_counter]["product_url"] = product_page_url
            products_params[product_counter]["source_name"] = product_source_name
            products_params[product_counter]["rating"] = product_rating
            products_params[product_counter]["release_date"] = product_release_date

            response = requests.post(url=add_product_link, params=products_params[product_counter])
            content = (response.json())
            status = content.get('status')
            fail_response = content.get('response').get('fail_message')
            if fail_response != None and (
                    "Invalid Api Key please apply for an API Key" in fail_response or "Api Key is needed for access" in fail_response):
                return jsonify(response={'fail_message': "💡 Api Key is needed for access"}, status="fail")

            if status != None and status == 'error':
                error_message += response.json()['response']['error_message']
                break

            if status != None and status == 'fail':
                fall_backs.append(f"❌ {product_name} is not added due to {response.json()['response']['fail_message']}")
                counter -= 1
                continue

        if len(error_message) != 0:
            return jsonify(response={"error_message": f"{error_message}"}, status="error")
        elif counter - 1 == 0 or len(all_inventory_products) == 0:
            return jsonify(response={"fail_message": f"No Products are in the file "}, status="fail")
        elif counter - 1 > 0 and len(fall_backs) != 0:
            return jsonify(
                response={"success_message": f"Your Products are added to your inventory with some fall backs ",
                          "fall_backs": fall_backs}, status="success")
        elif counter - 1 > 0 and len(all_inventory_products) > 0 and counter == len(all_inventory_products):
            return jsonify(
                response={"success_message": f"Your Products are added to your inventory Successfully", },
                status="success")
        else:
            return abort(500)
    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)


@app.route('/upload/inventory', methods=['GET', 'POST'])
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """The User uploads his or her excel file to upload it to their inventory """
    try:
        admin = str(request.args.get("admin"))
        api_key = str(request.args.get("api_key"))
        user = get_user(api_key=api_key, admin=admin)
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if not allowed_file(file.filename):
                flash("Incorrect file extension")
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('download_file', name=filename, api_key=api_key))
        return render_template('thanksPage.html', condition="upload_file", name="")
    except ValidationError as error_message:
        return jsonify(response={"fail_message": f"{error_message}"}, status="fail")
    except:
        abort(500)

@app.route('/documentation')
@app.route('/docs')
def documentation():
    """The WareHouse API Documentation"""
    return redirect("https://documenter.getpostman.com/view/17286684/UUy65PqF")

@app.route('/Privacy&Policy')
def Privacy_Policy():
    """renders the Privacy and Policy Page"""
    return render_template('Privacy-Policy.html', policy='policy')


@app.route("/")
@app.route("/home")
@app.route('/features')
@app.route("/about")
def about():
    """The about page"""
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=False)
