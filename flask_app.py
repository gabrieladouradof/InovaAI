from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash #importacao pra fazer criptografia da senha
from openai import OpenAI

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'your_secret_key'

# Singleton para a instância do banco de dados
class DatabaseSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseSingleton, cls).__new__(cls, *args, **kwargs)
            cls._instance.db = SQLAlchemy(app)
        return cls._instance

db_singleton = DatabaseSingleton()
db = db_singleton.db

client = OpenAI(api_key='')

# Padrão Factory para criação de usuários e solicitações de conteúdo
class UserFactory:
    @staticmethod
    def create_user(username, email, password):
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        return User(username=username, email=email, password=hashed_password)

class ContentRequestFactory:
    @staticmethod
    def create_content_request(user_id, theme, main_message, points, additional_info):
        return ContentRequest(user_id=user_id, theme=theme, main_message=main_message, points=points, additional_info=additional_info)

# Observer pattern classes
#Permite que os observadores sejam notificados de mudanças nos objetos ContentRequest.
from abc import ABC, abstractmethod

class Observer(ABC):  # Adicionado
    @abstractmethod
    def update(self, content_request):
        pass

class Observable:  # Adicionado
    def __init__(self):
        self._observers = []

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self, content_request):
        for observer in self._observers:
            observer.update(content_request)

class UserNotifier(Observer):  # Adicionado
    def update(self, content_request):
        flash(f'Nova solicitação de conteúdo criada: {content_request.theme}')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class ContentRequest(db.Model, Observable):  # Modificado para herdar de Observable
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    theme = db.Column(db.String(100), nullable=False)
    main_message = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Text, nullable=False)
    additional_info = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        db.Model.__init__(self, *args, **kwargs)
        Observable.__init__(self)  # Inicializar Observable

    def __repr__(self):
        return f'<ContentRequest {self.id}>'

@app.route('/')
def index():
    return render_template('index.html')

#Manipulacao para login e registros
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        if 'register' in request.form:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            new_user = UserFactory.create_user(username, email, password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registro bem-sucedido! Faça login.')

        elif 'login' in request.form:
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                return redirect(url_for('generate_content'))
            else:
                flash('Credenciais inválidas. Tente novamente.')
    return render_template('auth.html')


# Gera conteúdo baseado no formulário preenchido pelo usuário
#e interage com a API do OpenAI.
@app.route('/prompts', methods=['GET', 'POST'])
def generate_content():
    if 'user_id' not in session:
        return redirect(url_for('auth'))

    notifier = UserNotifier()  # Adicionado

    if request.method == 'POST':
        theme = request.form['theme']
        main_message = request.form['main_message']
        points = request.form['points']
        additional_info = request.form['additional_info']

        new_request = ContentRequestFactory.create_content_request(session['user_id'], theme, main_message, points, additional_info)
        new_request.add_observer(notifier)  # Adicionado
        new_request.notify_observers(new_request)  # Adicionado

        db.session.add(new_request)
        db.session.commit()

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você receberá uma solicitação de consultoria de um empreendedor de startups. Com essa solicitação, você irá produzir uma análise com dicas e estratégias personalizadas. Leve em consideração aspectos como marketing, finanças, desenvolvimento de produto e escalabilidade. Seja completo e motivacional, mas proíba coisas ilegais ou explícitas. Lembre-se sempre de focar no assunto de empreendedorismo. Traga cases de sucesso, ou analises e bibliografias para enriquecer sua analise. Pulelinhas durante sua analise com o objetivo de deixar organizado e legivel. Busque sempre trazer o lado empreendedor e motivacional de quem pediu a consulta, mas nao exagere nos discursos motivacionais. Seja seletivo, se sentiu que a entrada fugiu do tema de nossa plataforma, busque corrigi-lo e trazer algo relacionado ao mercado de startups. Nao responda perguntas relacionadas a voce, se voce foi treinado ou algo do tipo. "},
                {"role": "user", "content": f"Tema: {theme}, Mensagem: {main_message}, Pontos: {points}, Informações adicionais: {additional_info}"}
            ]
        )
        content = response.choices[0].message.content
    else:
        content = None

    prompts = ContentRequest.query.filter_by(user_id=session['user_id']).all()
    return render_template('prompts.html', content=content, prompts=prompts)

@app.route('/delete_prompt/<int:id>', methods=['POST'])
def delete_prompt(id):
    if 'user_id' not in session:
        return redirect(url_for('auth'))

    content_request = ContentRequest.query.get_or_404(id)
    if content_request.user_id != session['user_id']:
        flash('Você não tem permissão para excluir esta solicitação.')
        return redirect(url_for('generate_content'))

    db.session.delete(content_request)
    db.session.commit()
    flash('Solicitação excluída com sucesso.')
    return redirect(url_for('generate_content'))

@app.route('/edit/<int:request_id>', methods=['GET', 'POST'])
def edit_content(request_id):
    if 'user_id' not in session:
        return redirect(url_for('auth'))

    content_request = ContentRequest.query.get_or_404(request_id)
    if content_request.user_id != session['user_id']:
        flash('Você não tem permissão para editar esta solicitação.')
        return redirect(url_for('generate_content'))

    if request.method == 'POST':
        content_request.theme = request.form['theme']
        content_request.main_message = request.form['main_message']
        content_request.points = request.form['points']
        content_request.additional_info = request.form['additional_info']
        db.session.commit()
        flash('Solicitação atualizada com sucesso.')
        return redirect(url_for('generate_content'))

    prompts = ContentRequest.query.filter_by(user_id=session['user_id']).all()
    return render_template('prompts.html', prompts=prompts, prompt_to_edit=content_request)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
