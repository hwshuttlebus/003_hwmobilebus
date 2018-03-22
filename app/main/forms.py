from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, SelectField, RadioField
from wtforms.validators import Required, Length, Regexp
from wtforms import ValidationError
from ..models import mRole, mUser
import re

class EditProfileForm(FlaskForm):
    name = StringField('姓名', validators=[Length(0, 64)],\
                            render_kw={"placeholder": "真实姓名"})
    campus = RadioField('办公地点', choices=[\
        ('libingroad', u'李冰路'),
        ('huankeroad', u'环科路')],
        default = 'libingroad', validators=[Required()])

    submit = SubmitField('确定')


class EditProfileAdminForm(FlaskForm):
    mailaddr = StringField('Email', validators=[Required(), Length(1, 64)],\
                                render_kw={"placeholder": "email, 如：XX.XX@honeywell.com"})

    name = StringField('姓名', validators=[Length(0, 64)],\
                            render_kw={"placeholder": "真实姓名"})
    confirmed = BooleanField('账户是否已通过honeywell内部邮件认证')
    role = SelectField('权限', coerce=int)
    campus = RadioField('办公地点', choices=[\
        ('libingroad', u'李冰路'),
        ('huankeroad', u'环科路')],
        default = 'libingroad', validators=[Required()])

    submit = SubmitField('确定')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in mRole.query.order_by(mRole.name).all()]
        self.user = user

    def validate_mailaddr(self, field):
        value = field.data
        user_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
        re.IGNORECASE)

        user_part, domain_part = value.rsplit('@', 1)
        if field.data != self.user.mailaddr:
            if not user_regex.match(user_part) or domain_part != 'honeywell.com':
                raise ValidationError('邮箱地址无效！')

            if mUser.query.filter_by(mailaddr=field.data).first():
                raise ValidationError('该邮箱已经注册！')

class PostForm(FlaskForm):
    body = TextAreaField("", validators=[Required()],
                         render_kw={"placeholder": "请在此输入文字"})
    title = SelectField('权限')

    submit = SubmitField('提交')
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init(*args, **kwargs)
        self.title.choices = [('司机', '班车线路', '乘车环境', '安全', 'mbus软件', '其他')]