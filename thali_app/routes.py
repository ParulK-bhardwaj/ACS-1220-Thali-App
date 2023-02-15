from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from thali_app.models import City, Dish, User
from thali_app.forms import CityForm, DishForm, LoginForm, SignUpForm
# Import app and db from events_app package so that we can run app
from thali_app.extensions import app, db, bcrypt

# Blueprints
main = Blueprint("main", __name__)
# We'll use this blueprint to define the routes for login & signup.
auth = Blueprint("auth", __name__)

##########################################
#           Routes                       #
##########################################

@main.route('/')
def homepage():
    all_cities = City.query.all()
    print(all_cities)
    return render_template('home.html', all_cities=all_cities)

@main.route('/new_city', methods=['GET', 'POST'])
@login_required
def new_City():
    # Created a CityForm
    form = CityForm()

    if form.validate_on_submit():
        new_city = City(
            name=form.name.data,
            state=form.state.data,
            region=form.region.data,
            country=form.country.data,
            created_by=current_user
        )
        db.session.add(new_city)
        db.session.commit()

        flash("New City was successfully created.")
        return redirect(url_for("main.city_detail", city_id=new_city.id))

    return render_template('new_city.html', form=form)

@main.route('/new_dish', methods=['GET', 'POST'])
@login_required
def new_dish():
    # Created a DishForm
    form = DishForm()

    if form.validate_on_submit():
        new_dish = Dish(
            name=form.name.data,
            short_desc=form.short_desc.data,
            category=form.category.data,
            photo_url=form.photo_url.data,
            city=form.city.data,
            created_by=current_user
        )
        
        db.session.add(new_dish)
        db.session.commit()

        flash("New dish was successfully created.")
        return redirect(url_for("main.dish_detail", dish_id=new_dish.id))

    return render_template('new_dish.html', form=form)

@main.route('/city/<city_id>', methods=['GET', 'POST'])
@login_required
def city_detail(store_id):
    city = City.query.get(store_id)

    # Created a CityForm and pass in `obj=store`
    form = City(obj=city)

    if form.validate_on_submit():
        form.populate_obj(store)

        db.session.add(store)
        db.session.commit()
        flash("Store was updated successfully")
        return redirect(url_for("main.store_detail", store_id=store.id))
        
    store = City.query.get(store_id)
    return render_template('store_detail.html',store=store, form=form)

@main.route('/dish/<dish_id>', methods=['GET', 'POST'])
@login_required
def dish_detail(dish_id):
    dish = Dish.query.get(dish_id)
    # Created a DishForm and pass in `obj=dish`
    form = DishForm(obj=dish)
    if form.validate_on_submit():
        form.populate_obj(dish)

        db.session.add(dish)
        db.session.commit()
        flash("dish was updated successfully")
        return redirect(url_for("main.dish_detail",dish_id=dish.id))

    dish = Dish.query.get(dish_id)
    return render_template('dish_detail.html', dish=dish, form=form)

# ... adds dish to current_user's favorites list
@main.route('/add_to_favorites_list/<dish_id>', methods=['POST'])
def add_to_favorites_list(dish_id):
    dish = Dish.query.get(dish_id)
    current_user.favorites_list_user.append(dish)
    db.session.add(current_user)
    db.session.commit()
    flash("dish has been successfully added to the favorites list.")
    return redirect(url_for("main.favorites_list"))

# Stretch Challenge: removes dish from current_user's favorites list
@main.route('/remove_from_favorites_list/<dish_id>', methods=['POST'])
def remove_from_favorites_list(dish_id):
    dish = Dish.query.get(dish_id)
    current_user.favorites_list_user.remove(dish)
    db.session.add(current_user)
    db.session.commit()
    flash("dish has been successfully removed from the favorites list.")
    return redirect(url_for("main.favorites_list"))

# ... get logged in user's favorites list dishs ...
# ... display favorites list dishs in a template ...
@main.route('/favorites_list')
@login_required
def favorites_list():
    favorites_list = current_user.favorites_list_user
    return render_template('favorites_list.html', favorites_list=favorites_list)


# AUTH ROUTES
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    print('in signup')
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Account Created.')
        print('created')
        return redirect(url_for('auth.login'))
    print(form.errors)
    return render_template('signup.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user, remember=True)
        next_page = request.args.get('next')
        return redirect(next_page if next_page else url_for('main.homepage'))
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.homepage'))



