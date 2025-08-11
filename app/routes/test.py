from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app

test = Blueprint('test', __name__)


@test.route('/', methods=['GET'])
def open_test():
    return render_template('main/test.html')
