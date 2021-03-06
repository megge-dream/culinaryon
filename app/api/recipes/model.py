from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

from app.api import db
from app.api.categories.model import Category
from app.api.cuisine_types.model import CuisineType
from app.api.favorites.model import Favorite
from app.api.ingredients.model import Ingredient
from app.api.likes.model import Like
from app.api.photos.model import RecipePhoto
from app.api.tools.model import Tool
from app.api.users.constants import PUBLISHED
from app.api.wines.model import Wine


recipes_categories = db.Table('recipes_categories',
                              db.Column('recipe_id', db.Integer(), db.ForeignKey('recipes.id')),
                              db.Column('category_id', db.Integer(), db.ForeignKey('categories.id')))
recipes_cuisine_types = db.Table('recipes_cuisine_types',
                                 db.Column('recipe_id', db.Integer(), db.ForeignKey('recipes.id')),
                                 db.Column('cuisine_types_id', db.Integer(), db.ForeignKey('cuisineTypes.id')))
recipes_tools = db.Table('recipes_tools',
                         db.Column('recipe_id', db.Integer(), db.ForeignKey('recipes.id')),
                         db.Column('tool_id', db.Integer(), db.ForeignKey('tools.id')))
recipes_wines = db.Table('recipes_wines',
                         db.Column('recipe_id', db.Integer(), db.ForeignKey('recipes.id')),
                         db.Column('wine_id', db.Integer(), db.ForeignKey('wines.id')))


class InstructionItem(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "instructionItems"

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))
    step_number = db.Column(db.Integer)
    time = db.Column(db.Integer)
    video_lang_ru = db.Column(db.Text, nullable=True)
    video_lang_en = db.Column(db.Text, nullable=True)
    photo = db.Column(db.Text, nullable=True)
    description_lang_ru = db.Column(db.Text, nullable=True)
    description_lang_en = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())

    def __unicode__(self):
        return unicode(self.id) or u''


class Recipe(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title_lang_ru = db.Column(db.String(length=255), nullable=False)
    title_lang_en = db.Column(db.String(length=255), nullable=True)
    description_lang_ru = db.Column(db.Text, nullable=True)
    description_lang_en = db.Column(db.Text, nullable=True)
    spicy = db.Column(db.Boolean, nullable=True)
    complexity = db.Column(db.Integer, nullable=True)
    time = db.Column(db.String, nullable=True)
    amount_of_persons = db.Column(db.Integer, nullable=True)
    chef_id = db.Column(db.Integer, db.ForeignKey('chefs.id'))
    set_id = db.Column(db.Integer, db.ForeignKey('sets.id'), nullable=True)
    video_lang_ru = db.Column(db.Text, nullable=True)
    video_lang_en = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    type = db.Column(db.SmallInteger, default=PUBLISHED)

    # links
    likes = db.relationship(Like, backref='recipes', cascade="all, delete-orphan", lazy='select')
    favorites = db.relationship(Favorite, backref='recipes', cascade="all, delete-orphan", lazy='select')
    categories = db.relationship(Category, secondary=recipes_categories,
                                 backref=db.backref('recipes', lazy='select'))
    cuisine_types = db.relationship(CuisineType, secondary=recipes_cuisine_types,
                                    backref=db.backref('recipes', lazy='select'))
    photos = db.relationship(RecipePhoto, backref='recipes', cascade="all, delete-orphan", lazy='select')
    instructions = db.relationship(InstructionItem, backref='recipes', cascade="all, delete-orphan", lazy='select')
    tools = db.relationship(Tool, secondary=recipes_tools,
                            backref=db.backref('recipes', lazy='select'))
    wines = db.relationship(Wine, secondary=recipes_wines,
                            backref=db.backref('recipes', lazy='select'))
    ingredients = db.relationship(Ingredient, backref='recipes', cascade="all, delete-orphan", lazy='select')

    def __unicode__(self):
        return unicode(self.title_lang_ru) or u''

    @hybrid_property
    def num_likes(self):
        return len(self.likes)

    @num_likes.expression
    def _num_likes_expression(cls):
        return (db.select([db.func.count(Like.id).label("num_likes")])
                .where(Like.recipe_id == cls.id)
                .label("total_likes")
                )
