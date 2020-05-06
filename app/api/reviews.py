from flask import jsonify, request, url_for, g
from app.models import User, UserAuthentication, Review
from app.api.errors import bad_request
from app.auth.routes import register_user_func
from app.api import bp
from app.api.tokens import login_required
from app import db


@bp.route('/user/<int:reviewer_id>/reviews/<int:reviewee_id>', methods=['GET'])
@login_required
def get_review(reviewer_id, reviewee_id):
    return jsonify(Review.query.get_or_404({"reviewer_id": reviewer_id, "reviewee_id": reviewee_id}).to_dict())



@bp.route('/user/reviews', methods=['POST'])
@login_required
def create_review():
    data = request.get_json() or {}
    if data.get("reviewee_id") is None or data.get("score") is None:
        return bad_request("Must include reviewee_id and score")
    review = Review()
    review.from_dict(data)
    review.reviewer_id = g.current_user.id
    db.session.add(review)
    db.session.commit()
    response = jsonify(review.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_review', reviewer_id=g.current_user.id, reviewee_id=review.reviewee_id)
    return response


@bp.route('/user/reviews/<int:reviewee_id>', methods=['DELETE'])
@login_required
def delete_review(reviewee_id):
    Review.query.filter_by(reviewer_id=g.current_user.id, reviewee_id=reviewee_id).delete()
    db.session.commit()

    response = jsonify({})
    response.status_code = 200
    return response


@bp.route('/user/reviews/<int:reviewee_id>', methods=['PUT'])
@login_required
def update_review(reviewee_id):
    data = request.get_json() or {}
    review = Review.query.get_or_404({"reviewer_id": g.current_user.id, "reviewee_id": reviewee_id})

    review.from_dict(data)
    db.session.commit()

    review = Review.query.get({"reviewer_id": g.current_user.id, "reviewee_id": reviewee_id})
    response = jsonify(review.to_dict())
    response.status_code = 200
    response.headers['Location'] = url_for('api.get_review', reviewer_id=g.current_user.id, reviewee_id=review.reviewee_id)
    return response