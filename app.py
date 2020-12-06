from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'j551'

db = SQLAlchemy(app)

class City(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50),)


@app.route('/')
def indexGet():
	getWeatherData()
	return render_template('weather.html', weather_data=getWeatherData())


@app.route('/', methods=['POST'])
def index():
	saveData()
	return redirect(url_for('indexGet'))


@app.route('/delete/<name>')
def delete_city(name):
	delete(name)
	return redirect(url_for('indexGet'))


def saveData():
	err_msg = ''
	new_city = request.form.get('city')

	if new_city:
		existing_city = City.query.filter_by(name=new_city).first()

		if not existing_city:
			new_city_data = dataCheck(new_city)
		
			if new_city_data['cod'] ==200:
				new_city_obj = City(name=new_city)

				db.session.add(new_city_obj)
				db.session.commit()
			else:
				err_msg = 'City does not exist!'
		else:
			err_msg = 'City already on your list!'

	if err_msg:
		flash(err_msg, 'error')
	else:
		flash('City added Successfully!')

	return redirect(url_for('indexGet'))


def getWeatherData():
	cities = City.query.all()
	
	weather_data= []

	for city in cities:

		r = dataCheck(city.name)

		weather = {
			'city' : city.name,
			'temperature' : r['main']['temp'],
			'description' : r['weather'][0]['description'],
			'icon' : r['weather'][0]['icon'],
		}
		weather_data.append(weather)

	return weather_data


def dataCheck(city):
		url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=metric&appid=b2222a49317028fabcbcf0cbffb8c21d'
		r = requests.get(url).json()
		return r


def delete(name):
	city = City.query.filter_by(name=name).first()
	db.session.delete(city)
	db.session.commit()

	return flash(f'succesfully deleted { city.name }', 'success')
	