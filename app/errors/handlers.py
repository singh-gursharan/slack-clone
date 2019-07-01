from flask import render_template
from app.errors import bp
from app import db

@bp.errorhandler(404)
def errorhandler(error):
    return render_template('404.html'), 404

@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('505.html'), 500
