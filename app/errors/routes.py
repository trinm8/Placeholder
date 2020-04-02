from app.errors import bp
from flask import render_template


@bp.app_errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('errors/404.html', title='Page not found'), 404


@bp.app_errorhandler(405)
def method_not_allowed(e):
    return render_template('errors/405.html', title='Method not allowed'), 405


@bp.app_errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html', title='Internal error'), 500
