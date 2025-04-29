import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder to save uploaded images
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16 MB
db = SQLAlchemy(app)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)  # Store image filename

# Create the database
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        title = request.form.get('title')
        ingredients = request.form.get('ingredients')
        instructions = request.form.get('instructions')
        image = request.files.get('image')

        print(f"Title: {title}, Ingredients: {ingredients}, Instructions: {instructions}, Image: {image}")

        # Save the image if it exists
        image_filename = None
        if image:
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            
        try:
            db.session.commit()  # Attempt to commit the new recipe
            print("Recipe saved successfully!")
        except Exception as e:
            db.session.rollback()  # Rollback the session on error
            print(f"Error saving recipe: {e}")  # Print the error message
        
        new_recipe = Recipe(title=title, ingredients=ingredients, instructions=instructions, image_filename=image_filename)
        db.session.add(new_recipe)
        db.session.commit()
        
        return redirect(url_for('view_recipes'))

    return render_template('add_recipe.html')

@app.route('/view_recipes')
def view_recipes():
    recipes = Recipe.query.all()  # Fetch all recipes from the database
    print(f"Number of recipes fetched: {len(recipes)}")  # Debugging line
    return render_template('view_recipe.html', recipes=recipes)

@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)  # Fetch the recipe by ID or return a 404 error
    return render_template('recipe_detail.html', recipe=recipe)

if __name__ == '__main__':
    app.run(debug=True)