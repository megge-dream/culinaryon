from flask import request, jsonify, Blueprint
from flask.ext import excel
from app.api import Recipe, InstructionItem, Ingredient, db, Chef, Set, Category, CuisineType, Tool, Wine
from app.api.users.constants import RECIPE_TYPE
import pyexcel.ext.xls

mod = Blueprint('export_import', __name__, url_prefix='/export_import')


@mod.route("/", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        def time_sec_to_min(time):
            time = str(time).split(':')
            try:
                new_time = int(time[0]) * 3600 + int(time[1]) * 60 + int(time[2])
            except Exception:
                new_time = 0
            time = new_time
            return time

        def get_type(type):
            for key, value in RECIPE_TYPE.iteritems():
                if value == type:
                    return key

        def recipe_init_func(row):
            chef = Chef.query.filter_by(email=row['chef']).first()
            set = Set.query.filter_by(title_lang_ru=row['set']).first()
            categories = Category.query.filter(Category.title_lang_ru. in_(row['categories'].split(','))).all()
            cuisine_types = CuisineType.query.filter(CuisineType.title_lang_ru. in_(row['cuisine_types'].split(','))).all()
            tools = Tool.query.filter(Tool.title_lang_ru. in_(row['tools'].split(','))).all()
            wines = Wine.query.filter(Wine.title_lang_ru. in_(row['wines'].split(','))).all()
            recipe = Recipe(title_lang_ru=row['title_lang_ru'],
                            title_lang_en=row['title_lang_en'],
                            description_lang_ru=row['description_lang_ru'],
                            description_lang_en=row['description_lang_en'],
                            spicy=row['spicy'],
                            complexity=row['complexity'],
                            time=time_sec_to_min(row['time']),
                            amount_of_persons=row['amount_of_persons'],
                            video_lang_ru=row['video_lang_ru'],
                            video_lang_en=row['video_lang_en'],
                            type=get_type(row['type']),
                            chef_id=chef.id,
                            set_id=set.id,
                            categories=categories,
                            cuisine_types=cuisine_types,
                            tools=tools,
                            wines=wines
                            )
            return recipe

        def ingredient_init_func(row):
            recipe = Recipe.query.filter_by(title_lang_ru=row['recipe']).first()
            ingredient = Ingredient(title_lang_ru=row['title_lang_ru'],
                                    title_lang_en=row['title_lang_en'],
                                    amount=row['amount'],
                                    unit_lang_ru=row['unit_lang_ru'],
                                    unit_lang_en=row['unit_lang_en'],
                                    recipe_id=recipe.id
                                    )
            return ingredient

        def instruction_init_func(row):
            recipe = Recipe.query.filter_by(title_lang_ru=row['recipe']).first()
            instruction = InstructionItem(step_number=row['step_number'],
                                          time=time_sec_to_min(row['time']),
                                          video_lang_ru=row['video_lang_ru'],
                                          video_lang_en=row['video_lang_en'],
                                          description_lang_ru=row['description_lang_ru'],
                                          description_lang_en=row['description_lang_en'],
                                          recipe_id=recipe.id
                                    )
            return instruction

        request.save_book_to_database(field_name='file', session=db.session,
                                      tables=[Recipe, Ingredient, InstructionItem],
                                      initializers=[recipe_init_func,
                                                    ingredient_init_func,
                                                    instruction_init_func])

    return '''
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload (csv, tsv, csvz, tsvz only)</h1>
    <form action="" method=post enctype=multipart/form-data><p>
    <input type=file name=file><input type=submit value=Upload>
    </form>
    '''