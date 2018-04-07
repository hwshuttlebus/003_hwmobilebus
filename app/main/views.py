from flask import render_template, send_file, make_response, request, url_for, redirect, flash
from flask_login import current_user, login_required
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from ..decorators import admin_required, permission_required
from ..models import mUser, mRole, mPost, Event
from .. import db

#from flask import 


@main.route('/', methods=['GET', 'POST'])
def index():
    if False == current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return render_template('index.html')
    #return make_response(open('app/templates/home.html').read())


@main.route('/user/<mailaddr>')
def user(mailaddr):
    user = mUser.query.filter_by(mailaddr=mailaddr).first_or_404()
    return render_template('user.html', user=user)

@main.route('/userdel/<int:id>')
@login_required
@admin_required
def del_user(id):
    user = mUser.query.filter_by(id=id).first_or_404()
    try:
        db.session.delete(user)
        db.session.commit()
        flash('用户删除成功!')
    except:
        db.session.rollback()
    return redirect(url_for('main.index'))

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.campus = form.campus.data
        db.session.add(current_user)
        flash('您的资料已经更新！')
        return redirect(url_for('.user', mailaddr=current_user.mailaddr))
    form.name.data = current_user.name
    form.campus.data = current_user.campus
    return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = mUser.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.mailaddr = form.mailaddr.data
        user.confirmed = form.confirmed.data
        user.role = mRole.query.get(form.role.data)
        user.name = form.name.data
        user.campus = form.campus.data
        db.session.add(user)
        flash('资料已经更新！')
        return redirect(url_for('.user', mailaddr=user.mailaddr))
    form.mailaddr.data = user.mailaddr
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.campus.data = user.campus
    return render_template('edit_profile.html', form=form, user=user)

@main.route('/infoModal.html')
def infoModal():
    return render_template('server_partial/infoModal.html')

@main.route('/ngtemplates/showmaproute.html')
def showmap():
    return render_template('/ngtemplates/showmaproute.html')
