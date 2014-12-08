from datetime import datetime

from app.api import db
from app.api.categories.model import Category
from app.api.cuisine_types.model import CuisineType
from app.api.favorites.model import Favorite
from app.api.ingredients.model import Ingredient
from app.api.likes.model import Like
from app.api.photos.model import RecipePhoto
from app.api.tools.model import Tool
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
    video = db.Column(db.Text, nullable=True)
    photo = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())


class Recipe(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(length=255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    spicy = db.Column(db.Boolean, nullable=True)
    complexity = db.Column(db.Integer, nullable=True)
    time = db.Column(db.String, nullable=True)
    amount_of_persons = db.Column(db.Integer, nullable=True)
    chef_id = db.Column(db.Integer, db.ForeignKey('chefs.id'))
    video = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())

    # links
    likes = db.relationship(Like, backref='recipes', lazy='dynamic')
    favorites = db.relationship(Favorite, backref='recipes', lazy='dynamic')
    categories = db.relationship(Category, secondary=recipes_categories,
                                 backref=db.backref('recipes', lazy='dynamic'))
    cuisine_types = db.relationship(CuisineType, secondary=recipes_cuisine_types,
                                    backref=db.backref('recipes', lazy='dynamic'))
    photos = db.relationship(RecipePhoto, backref='recipes', lazy='dynamic')
    instructions = db.relationship(InstructionItem, backref='recipes', lazy='dynamic')
    tools = db.relationship(Tool, secondary=recipes_tools,
                            backref=db.backref('recipes', lazy='dynamic'))
    wines = db.relationship(Wine, secondary=recipes_wines,
                            backref=db.backref('recipes', lazy='dynamic'))
    ingredients = db.relationship(Ingredient, backref='recipes', lazy='dynamic')

    def __unicode__(self):
        return self.title