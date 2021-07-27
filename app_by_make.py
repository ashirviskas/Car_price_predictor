from flask import Flask, request, render_template
from ml_models_by_make import AutopliusPredictorByMake, create_params, filter_ads


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def enter_details():
    if request.method == 'POST':
        try:
            make = request.form['mk']
            model = request.form['mdl']
            body_type = request.form['typ']
            year = int(request.form['yr'])
            mileage = int(request.form['mile'])
            trans = request.form['trn']
            engine = float(request.form['eng'])
            fuel = request.form['fl']
            other = [model, body_type, trans, fuel]
            params = create_params(make, year, mileage, engine, other)
            ml_model, score = AutopliusPredictorByMake(make).train_model()
            valuation = ml_model.predict([params])[0]
            ads = filter_ads(make, model, year)
            if ads.empty:
                return render_template('valuation_no_results.html',
                                           result=f'{round(int(valuation), 0):,}', score=f'{round(score,4)*100}')
            return render_template('valuation.html', result=f'{round(int(valuation), 0):,}',
                                       posts=ads, score=f'{round(score*100,2)}')
        except:
            return render_template('main_page.html', result='Neteisingai įvesti arba praleisti duomenys')
    elif request.method =='GET':
        return render_template('main_page.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
