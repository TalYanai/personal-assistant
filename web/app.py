from flask import Flask, render_template, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import sports, finance, fitness
from agents.calendar_agent import run as calendar_run
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/brief")
def get_brief():
    today = datetime.now().strftime("%A, %B %d %Y")
    
    sports_data = sports.run()
    finance_data = finance.run()
    fitness_data = fitness.run()
    calendar_data = calendar_run()
    
    return jsonify({
        "date": today,
        "sports": sports_data,
        "finance": finance_data,
        "fitness": fitness_data,
        "calendar": calendar_data
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)