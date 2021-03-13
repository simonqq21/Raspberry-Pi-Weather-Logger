script_path=`dirname $(realpath $0)`
echo $script_path
cd $script_path
source venv/bin/activate
export FLASK_ENV=development
export FLASK_APP=app.py
flask run --host=0.0.0.0
