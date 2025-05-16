from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# Configuration de la base de données 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de la base de données
db = SQLAlchemy(app)

#=====================================================

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), nullable=False, default='more_books.png')
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Book('{self.title}', '{self.author}', '{self.price}')"

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Article('{self.title}', '{self.date_posted}')"

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Contact('{self.name}', '{self.email}', '{self.subject}')"


#===================================================

# Route pour la page d'accueil
@app.route('/')
def index():
    # Récupérer les articles les plus récents pour la section blog
    articles = Article.query.order_by(Article.date_posted.desc()).limit(2).all()
    return render_template('index.html', title='Accueil', articles=articles)

@app.route('/livres')
def livres():
    books = Book.query.all()
    return render_template('livres.html', title='Livres', books=books)

#route pour les blogs
@app.route('/blog')
def blog():
    articles = Article.query.order_by(Article.date_posted.desc()).all()
    return render_template('blog.html', title='Blog', articles=articles)

#route pour la recuperation des articles
@app.route('/articles')
def articles():
    # Récupération de tous les articles depuis la base de données
    articles = Article.query.order_by(Article.date_posted.desc()).all()
    return render_template('articles.html', title='Articles', articles=articles)



#route pour les articles specifique
@app.route('/article/<int:article_id>')
def article(article_id):
    # Récupération de l'article spécifique depuis la base de données
    article = Article.query.get_or_404(article_id)
    return render_template('article.html', title=article.title, article=article)



# Route pour créer un nouvel article (GET pour afficher le formulaire, POST pour le traiter)
@app.route('/article/new', methods=['GET', 'POST'])
def new_article():
    if request.method == 'POST':
        # Récupération des données du formulaire
        title = request.form['title']
        content = request.form['content']
        
        # Création d'un nouvel article
        article = Article(title=title, content=content)
        
        # Ajout à la base de données
        db.session.add(article)
        db.session.commit()
        
        flash('Article créé avec succès!', 'success')
        return redirect(url_for('articles'))
    return render_template('new_article.html', title='Nouvel Article')



# Route pour éditer un article existant
@app.route('/article/edit/<int:article_id>', methods=['GET', 'POST'])
def edit_article(article_id):
    # Récupérer l'article à éditer
    article = Article.query.get_or_404(article_id)
    
    if request.method == 'POST':
        # Mise à jour des données de l'article
        article.title = request.form['title']
        article.content = request.form['content']
        
        # Enregistrement des modifications
        db.session.commit()
        
        flash('Article mis à jour avec succès!', 'success')
        return redirect(url_for('article', article_id=article.id))
    return render_template('edit_article.html', title='Éditer Article', article=article)





# Route pour supprimer un article
@app.route('/article/delete/<int:article_id>', methods=['POST'])
def delete_article(article_id):
    # Récupérer l'article à supprimer
    article = Article.query.get_or_404(article_id)
    
    # Supprimer l'article
    db.session.delete(article)
    db.session.commit()
    
    flash('Article supprimé avec succès!', 'success')
    return redirect(url_for('articles'))

# Route pour la page À propos
@app.route('/about')
def about():
    return render_template('about.html', title='À propos')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Ici, vous pourriez envoyer un email ou enregistrer le message dans une base de données
        # Par exemple:
        send_email(name, email, subject, message)
        new_contact = Contact(name=name, email=email, subject=subject, message=message)
        db.session.add(new_contact)
        db.session.commit()
        
        flash('Message envoyé avec succès! Nous vous répondrons dans les plus brefs délais.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html', title='Contact')


# administrateur section 




#



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)