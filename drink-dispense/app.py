from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, StringField, IntegerField
from wtforms.validators import InputRequired, NumberRange, Length, Regexp
from wtforms_validators import AlphaNumeric
import serial
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ThisDoesntMatter'
Bootstrap(app)
port = serial.Serial('/dev/ttyACM0', 9600)
class DrinkSelectForm(FlaskForm):
    drink = RadioField('', choices = [('Screwdriver~!Screwdriver{5:10,1:2,}','Screwdriver'),('Vodka Coke~!Vodka Coke{6:10,3:2,}','Vodka Coke'),('CUSTOM','Custom Drink')], default = 'Screwdriver~!Screwdriver{5:10,1:2,}')
    # submit = SubmitField("Dispense!")
    
class CustomSelectForm(FlaskForm):
    name = StringField(u'Drink Name', validators=[InputRequired(), AlphaNumeric(), Length(min=1, max=127)])
    drink1 = IntegerField(u'Water 1 (oz.)', default = 0, validators=[NumberRange(min=0, max=12)])
    drink2 = IntegerField(u'Ginger Ale (oz.)', default = 0, validators=[NumberRange(min=0, max=12)])
    drink3 = IntegerField(u'Water 2 (oz.)', default = 0, validators=[NumberRange(min=0, max=12)])
    drink4 = IntegerField(u'Water 3 (oz.)', default = 0, validators=[NumberRange(min=0, max=12)])
    drink5 = IntegerField(u'Sprite (oz.)', default = 0, validators=[NumberRange(min=0, max=12)])
    drink6 = IntegerField(u'Coke (oz.)', default = 0, validators=[NumberRange(min=0, max=12)])
    

@app.route("/", methods=['GET','POST'])
def index():
    form = DrinkSelectForm()
    if form.validate_on_submit():
        if form.drink.data == "CUSTOM":
            return redirect(url_for('custom'))
        contents = form.drink.data.split("~")
        drink_name = contents[0]
        drink_recipe = contents[1]
        return redirect(url_for('dispense', drink_name=drink_name, drink_recipe=drink_recipe))
    return render_template("index.html", form=form)

@app.route("/dispense")
def dispense():
    #dispense based on recipe
    drink_name = request.args.get('drink_name')
    drink_recipe = request.args.get('drink_recipe')
    print(drink_recipe)
    port.write(drink_recipe.encode())
    return render_template("dispense.html", drink_name=drink_name)

@app.route("/custom", methods=['GET','POST'])
def custom():
    form = CustomSelectForm()
    if form.validate_on_submit():
        print(form.name.data)
        oz1 = int(form.drink1.data)
        oz2 = int(form.drink2.data)
        oz3 = int(form.drink3.data)
        oz4 = int(form.drink4.data)
        oz5 = int(form.drink5.data)
        oz6 = int(form.drink6.data)
        oztotal = oz1+oz2+oz3+oz4+oz5+oz6
        ozYeah = [oz1, oz2, oz3, oz4, oz5, oz6]
        if oztotal > 12:
            return render_template("custom.html", form=form, error="Total Oz must be less than 12oz")
        elif oztotal < 1:
            return render_template("custom.html", form=form, error="Total Oz must be greater than 0oz")
        else:
            recipe = "!" + str(form.name.data) + "{"
            for index, ozNum in enumerate(ozYeah):
                if ozNum > 0:
                    recipe += str(index+1)
                    recipe += ":"
                    recipe += str(ozNum)
                    recipe += ","
            recipe += "}"
            return redirect(url_for('dispense', drink_name=form.name.data, drink_recipe=recipe))
    return render_template("custom.html", form=form, error='')


@app.route("/cancel")
def cancel():
    #cancel drink method MBED SERIAL
    drink_name = request.args.get('drink_name')
    return redirect(url_for('index'))
    

    

if __name__== "__main__":
    app.run(host='0.0.0.0')