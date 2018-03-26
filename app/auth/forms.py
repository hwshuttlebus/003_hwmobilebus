from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, ValidationError
from wtforms.validators import Required, Length, Email, EqualTo
from ..models import mUser
import re


class RegistrationForm(FlaskForm):
    mailaddr = StringField('', validators=[Required(), Length(1, 64)],\
                                render_kw={"placeholder": "email"})
    password = PasswordField('', validators=[Required(), EqualTo('password2', message='两次输入密码需一致！')],\
                                render_kw={"placeholder":"请输入密码"})
    password2 = PasswordField('', validators=[Required()],\
                                render_kw={"placeholder": "请再次确认密码"})

    campus = RadioField('', choices=[\
        ('libingroad', u'李冰路'),
        ('huankeroad', u'环科路')],
        default = 'libingroad', validators=[Required()])

    submit = SubmitField('注册')

    def validate_mailaddr(self, field):
        value = field.data + '@honeywell.com'
        user_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
        re.IGNORECASE)

        user_part, domain_part = value.rsplit('@', 1)
        if not user_regex.match(user_part):
            raise ValidationError('邮箱地址无效！')

        if mUser.query.filter_by(mailaddr=value).first():
            raise ValidationError('该邮箱已经注册！')


class LoginForm(FlaskForm):
    mailaddr = StringField('', validators=[Required(), Length(1, 64)],\
                                render_kw={"placeholder": "email"})
    password = PasswordField('', validators=[Required()],\
                                render_kw={"placeholder": "请输入密码"})
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

    def validate_mailaddr(self, field):
        value = field.data + '@honeywell.com'
        user_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
        re.IGNORECASE)

        user_part, domain_part = value.rsplit('@', 1)
        if not user_regex.match(user_part):
            raise ValidationError('邮箱地址无效！')
    

class PasswordResetRequestForm(FlaskForm):
    mailaddr = StringField('', validators=[Required(), Length(1, 64)],\
                                render_kw={"placeholder": "email"})
    submit = SubmitField('发送重置密码邮件')

    def validate_mailaddr(self, field):
        value = field.data + '@honeywell.com'
        user_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
        re.IGNORECASE)

        user_part, domain_part = value.rsplit('@', 1)
        if not user_regex.match(user_part):
            raise ValidationError('邮箱地址无效！')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('', validators=[Required(), EqualTo('password2', message='两次输入密码需一致！')],\
                                render_kw={"placeholder":"请输入旧密码"})
    password = PasswordField('', validators=[Required(), EqualTo('password2', message='两次输入密码需一致！')],\
                                render_kw={"placeholder":"请输入新密码"})
    password2 = PasswordField('', validators=[Required()],\
                                render_kw={"placeholder": "请再次确认新密码"})
    submit = SubmitField('更新密码')


class ChangePasswordFormAdmin(FlaskForm):
    password = PasswordField('', validators=[Required(), EqualTo('password2', message='两次输入密码需一致！')],\
                                render_kw={"placeholder":"请输入新密码"})
    password2 = PasswordField('', validators=[Required()],\
                                render_kw={"placeholder": "请再次确认新密码"})
    submit = SubmitField('更新密码')


class PasswordResetForm(FlaskForm):
    mailaddr = StringField('', validators=[Required(), Length(1, 64)],\
                                render_kw={"placeholder": "email"})
    password = PasswordField('', validators=[Required(), EqualTo('password2', message='两次输入密码需一致！')],\
                                render_kw={"placeholder":"请输入密码"})
    password2 = PasswordField('', validators=[Required()],\
                                render_kw={"placeholder": "请再次确认密码"})
    submit = SubmitField('确定')

    def validate_mailaddr(self, field):
        value = field.data + '@honeywell.com'
        user_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
        re.IGNORECASE)

        user_part, domain_part = value.rsplit('@', 1)
        if not user_regex.match(user_part):
            raise ValidationError('邮箱地址无效！')