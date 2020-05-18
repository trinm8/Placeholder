from app import db
from app.users import bp
from app.models import User, MusicPref, Review, Car
from app.users.forms import Settings, ReviewForm

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
        if 64 > len(form.liked_genre.data) > 0:
            pref = MusicPref(user=usr.id, genre=form.liked_genre.data, likes=True)
            db.session.add(pref)
            db.session.commit()

            flash(_("Liked genre added!"))

    # Add disliked genre
    if form.submit_disliked.data:
        if len(form.disliked_genre.data) > 64:
            flash(_("Genre exceeds character limit"))
        if 64 > len(form.disliked_genre.data) > 0:
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
            if not car:
                car = Car(owner_id=usr.id, color=form.color.data,
                          brand=form.brand.data, plate=form.plate.data)
                db.session.add(car)
            else:
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


@bp.route('/accounts/<int:id>/delete', methods=['GET'])
@login_required
def delete(id: int):
    # TODO: check cascade, not yet tested
    if current_user.id == id:
        logout_user()
        User.query.filter_by(id=id).delete()
        db.session.commit()
        flash(_("Your account has been deleted successfully"))
    else:
        flash(_("You can only delete your own account"))
    return redirect(url_for("main.index"))


@bp.route('/accounts/<id>/review_overview')
@login_required
def review_overview(id):
    user = User.query.get_or_404(id)
    reviews_of_me = user.get_reviews_of_me()
    reviews_by_me = user.get_reviews_by_me()
    return render_template('users/review_overview.html', title=_('Review Overview'), user=user,
                           reviews_of_me=reviews_of_me, reviews_by_me=reviews_by_me)


@bp.route('/accounts/<id>/add_review', methods=['GET', 'POST'])
@login_required
def add_review(id):
    form = ReviewForm()
    user = User.query.get_or_404(id)

    if form.validate_on_submit():
        if form.submit_review.data:
            review = Review.query.get({"reviewer_id": current_user.id, "reviewee_id": user.id})
            # check score
            if form.score.data > 5 or form.score.data < 0:
                flash(_("Review score larger than 5 or smaller then 0"))
                return render_template('users/add_review.html', title=_('Add Review'), user=user, form=form)
            elif review:
                review.score = form.score.data
                review.review_text = form.review_text.data
                db.session.commit()
                flash(_("Review edited"))
                return redirect(url_for('main.index'))
            else:
                review = Review(reviewer_id=current_user.id,
                                reviewee_id=user.id,
                                score=form.score.data,
                                review_text=form.review_text.data)
                db.session.add(review)
                db.session.commit()

                flash(_('New review added'))
                #return redirect(url_for('/users/<id>', id=current_user.id))
                return redirect(url_for('main.index'))

    return render_template('users/add_review.html', title=_('Add Review'), user=user, form=form)

