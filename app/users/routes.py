from app import db
from app.users import bp
from app.models import User, MusicPref, Review
from app.users.forms import Settings

from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user, logout_user

from flask_babel import _


@bp.route('/users/<id>')
@login_required
def user_page(id):
    user = User.query.get_or_404(id)
    return render_template('users/user.html', title=_('Account'), user=user)


def get_suggested_genres():
    return set([g.genre for g in MusicPref.query.all()])
    # frequency = {k: 0 for k in set(all_genres)}
    # for g in all_genres:
    #     frequency[g] = frequency[g] + 1
    # # Source: https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    # frequency = {k: v for k, v in sorted(frequency.items(), key=lambda item: item[1], reverse=True)}
    # return [list(frequency)[i] for i in range(0, 10)]


@bp.route('/account/settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    form = Settings()

    if form.validate_on_submit():

        usr = User.query.filter_by(id=current_user.get_id()).first()

        # Profile settings
        if form.submit_profile.data:

            # Check lengths
            if (len(form.firstname.data) > 64
                    or len(form.lastname.data) > 64
                    or len(form.email.data) > 120):
                flash(_("User data field exceeds character limit"))

            else:
                usr.firstname = form.firstname.data
                usr.lastname = form.lastname.data
                usr.email = form.email.data

                if len(form.password.data) > 0:
                    usr.authentication().set_password(form.password.data)
                db.session.commit()

            flash(_("Profile settings updated!"))

        # Add liked genre
        if form.submit_liked.data:
            if len(form.liked_genre.data) > 64:
                flash(_("Genre exceeds character limit"))
            if len(form.liked_genre.data) > 0:
                pref = MusicPref(user=usr.id, genre=form.liked_genre.data, likes=True)
                db.session.add(pref)
                db.session.commit()

                flash(_("Liked genre added!"))

        # Add disliked genre
        if form.submit_disliked.data:
            if len(form.disliked_genre.data) > 64:
                flash(_("Genre exceeds character limit"))
            if len(form.disliked_genre.data) > 0:
                pref = MusicPref(user=usr.id, genre=form.disliked_genre.data, likes=False)
                db.session.add(pref)
                db.session.commit()

                flash(_("Disliked genre added!"))

        # Car settings
        if form.submit_car.data:
            if (len(form.color.data) > 64 or
                    len(form.brand.data) > 64 or
                    len(form.plate.data) > 32):
                flash(_("Car data field exceeds character limit"))
            else:
                car = usr.car()
                car.color = form.color.data
                car.brand = form.brand.data
                car.plate = form.plate.data
                db.session.commit()

            flash(_("Car settings updated!"))

    return render_template('users/settings.html', title='Account Settings', form=form,
                           suggested_genres=get_suggested_genres())


@bp.route('/account/settings/remove_genre/<id>', methods=['GET', 'POST'])
@login_required
def remove_genre(id):
    MusicPref.query.filter_by(id=id).delete()
    db.session.commit()

    flash(_("Genre removed!"))
    return redirect(url_for('users.account_settings'))


@bp.route('/accounts/<id>/delete', methods=['GET'])
@login_required
def delete(id):
    # TODO: check cascade, not yet tested
    if current_user.id == id:
        logout_user()
        User.query.filter_by(id=id).delete()
        db.session.commit()
        flash(_("Your account has been deleted successfully"))
    else:
        flash(_("You can only delete your own account"))
    return redirect(url_for("main.index"))


@bp.route('/accounts/<id>/review_page')
@login_required
def review_page(id):
    user = User.query.get_or_404(id)
    return render_template('users/reviews.html', title=_('Review'), user=user)
