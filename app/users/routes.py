from app import db
from app.users import bp
from app.models import User, MusicPref
from app.users.forms import Settings

from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user


@bp.route('/users/<username>')
@login_required
def user_page(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('users/user.html', title='Account', user=user)


def get_suggested_genres():
    all_genres = [g.genre for g in MusicPref.query.all()]
    frequency = {k: 0 for k in set(all_genres)}
    for g in all_genres:
        frequency[g] = frequency[g] + 1
    # Source: https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    frequency = {k: v for k, v in sorted(frequency.items(), key=lambda item: item[1], reverse=True)}
    return [list(frequency)[i] for i in range(0, 10)]


@bp.route('/account/settings', methods=['GET', 'POST'])
@login_required
def account_settings():

    form = Settings()

    if form.validate_on_submit():

        usr = User.query.filter_by(id=current_user.get_id()).first()

        # Profile settings
        if form.submit_profile.data:
            usr.firstname = form.firstname.data
            usr.lastname = form.lastname.data
            usr.email = form.email.data
            if len(form.password.data) > 0:
                usr.set_password(form.password.data)
            db.session.commit()

            flash("Profile settings updated!")

        # Add liked genre
        if form.submit_liked.data:
            if len(form.liked_genre.data) > 0:
                pref = MusicPref(user=usr.id, genre=form.liked_genre.data, likes=True)
                db.session.add(pref)
                db.session.commit()

                flash("Liked genre added!")

        # Add disliked genre
        if form.submit_disliked.data:
            if len(form.disliked_genre.data) > 0:
                pref = MusicPref(user=usr.id, genre=form.disliked_genre.data, likes=False)
                db.session.add(pref)
                db.session.commit()

                flash("Disliked genre added!")

        # Car settings
        if form.submit_car.data:
            usr.car_color = form.color.data
            usr.car_brand = form.brand.data
            usr.car_plate = form.plate.data
            db.session.commit()

            flash("Car settings updated!")

    return render_template('users/settings.html', title='Account Settings', form=form,
                           suggested_genres=get_suggested_genres())


@bp.route('/account/settings/remove_genre/<id>', methods=['GET', 'POST'])
@login_required
def remove_genre(id):
    MusicPref.query.filter_by(id=id).delete()
    db.session.commit()

    flash("Genre removed!")
    return redirect(url_for('users.account_settings'))
