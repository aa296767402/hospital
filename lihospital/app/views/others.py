from flask import Blueprint, render_template, redirect, url_for
from app.extensions import db


others = Blueprint('others', __name__)

@others.route('/first/')
def first():
    return render_template('others/first_zixun.html')


@others.route('/second/')
def second():
    return render_template('others/second_zixun.html')

@others.route('/third/')
def third():
    return render_template('others/third_zixun.html')