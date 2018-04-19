from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required, login_user, logout_user
from . import auth
from .. import db
from ..models import mUser
from ..decorators import admin_required
from ..email import send_email, send_email_cloud
from .forms import LoginForm, RegistrationForm, PasswordResetRequestForm, \
        PasswordResetForm, ChangePasswordForm, ChangePasswordFormAdmin

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
            and request.endpoint \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        mailform = form.mailaddr.data+'@honeywell.com'
        user = mUser.query.filter_by(mailaddr=mailform).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('无效的用户名或者密码')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已登出！')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        newmailaddr = form.mailaddr.data+'@honeywell.com'
        user = mUser(mailaddr=newmailaddr,
                     password=form.password.data,
                     campus=form.campus.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email_cloud(newmailaddr, '请确认您的帐号', 'auth/email/confirm',\
                     user=user, token=token)
        flash('验证邮件已经发送至'+newmailaddr+'请点击邮件内连接完成认证')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('您已经确认了您的账号，欢迎继续在电脑端or手机端使用Mobilebus!')
    else:
        flash('确认链接无效或者超时！')
    return redirect(url_for('main.index'))

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email_cloud(current_user.mailaddr, '请确认您的帐号', 'auth/email/confirm',\
                     token=token)
    flash('帐号确认邮件已经发送至:' + current_user.mailaddr)
    return redirect(url_for('main.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('密码已更新！')
        else:
            flash('旧密码无效！')
    return render_template("auth/change_password.html", form=form)


@auth.route('/change-password/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def change_password_admin(id):
    user = mUser.query.get_or_404(id)
    form = ChangePasswordFormAdmin()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.add(user)
        flash('帐号密码已更新！')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        newmailaddr = form.mailaddr.data+'@honeywell.com'
        user = mUser.query.filter_by(mailaddr=newmailaddr).first()
        if user:
            token = user.generate_reset_token()
            send_email_cloud(newmailaddr, '请重置您的密码',\
                            'auth/email/reset_password',\
                            token=token,\
                            next=request.args.get('next'))
        flash('重置密码邮件已经发送到'+newmailaddr+'，请于两小时内进行确认！')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        newmailaddr = form.mailaddr.data+'@honeywell.com'
        user = mUser.query.filter_by(mailaddr=newmailaddr).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('您的密码已被重置！')
            return redirect(url_for('auth.login'))
        else:
            flash('该重置密码链接无效或者超时！')
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)