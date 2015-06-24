from flask import url_for
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.form import ImageUploadField, thumbgen_filename
from markupsafe import Markup
from wtforms import SelectField, Form
from app.api import app
from app.api.users.constants import USER_ROLE_SELECT, PROVIDER_LIST_SELECT, USER_STATUS_SELECT


class ModelViewWithRelationships(ModelView):
    column_display_all_relations = True


class RecipeImageForm(Form):
    data = ImageUploadField('Image', base_path=app.config['RECIPES_UPLOAD'], thumbnail_size=(500, 500, True))


class RecipeModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.data:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='recipes/' + thumbgen_filename(model.data)))

    def get_title(view, context, model, name):
        return model.data

    can_create = True
    column_list = ('data', 'title')
    column_formatters = {
        "data": _list_thumbnail,
        "title": get_title
    }
    form = RecipeImageForm


class ChefImageForm(Form):
    data = ImageUploadField('Image', base_path=app.config['CHEFS_UPLOAD'], thumbnail_size=(500, 500, True))


class ChefModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.data:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='chefs/' + thumbgen_filename(model.data)))

    def get_title(view, context, model, name):
        return model.data

    can_create = True
    column_list = ('data', 'title')
    column_formatters = {
        "data": _list_thumbnail,
        "title": get_title
    }
    form = ChefImageForm


class SchoolImageForm(Form):
    data = ImageUploadField('Image', base_path=app.config['SCHOOLS_UPLOAD'], thumbnail_size=(500, 500, True))


class SchoolModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.data:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='schools/' + thumbgen_filename(model.data)))

    def get_title(view, context, model, name):
        return model.data

    can_create = True
    column_list = ('data', 'title')
    column_formatters = {
        "data": _list_thumbnail,
        "title": get_title
    }
    form = SchoolImageForm


class ToolImageForm(Form):
    photo = ImageUploadField('Image', base_path=app.config['TOOLS_UPLOAD'], thumbnail_size=(500, 500, True))


class ToolModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='tools/' + thumbgen_filename(model.photo)))

    can_create = True
    column_formatters = {
        "photo": _list_thumbnail,
    }
    # form = ToolImageForm
    form_extra_fields = {
        'photo': ImageUploadField('Image', base_path=app.config['TOOLS_UPLOAD'], thumbnail_size=(500, 500, True))
    }


class MyUserAdmin(ModelView):
    column_exclude_list = ('_password',)
    form_edit_rules = ('role_code',)
    column_choices = {
        'role_code': USER_ROLE_SELECT,
        'provider_id': PROVIDER_LIST_SELECT,
        'status_code': USER_STATUS_SELECT
    }
    column_display_all_relations = True
    form_overrides = dict(role_code=SelectField, provider_id=SelectField, status_code=SelectField)

    def update_model(self, form, model):
        if self.form_edit_rules:
            for field in form:
                field_name = field.name
                if field_name not in self.form_edit_rules:
                    form.__delitem__(field_name)
        return super(MyUserAdmin, self).update_model(form, model)

    form_args = dict(
        role_code=dict(
            label='Role', choices=USER_ROLE_SELECT, coerce=int
        ),
        provider_id=dict(
            label='Provider', choices=PROVIDER_LIST_SELECT, coerce=int
        ),
        status_code=dict(
            label='Status', choices=USER_STATUS_SELECT, coerce=int
        ),
    )
