from flask import Flask, render_template, request, session, redirect, url_for
import matplotlib

matplotlib.use("Agg")
import os
from roboadvisor_class.roboadvisor_class import RoboAdvisorClass
from questions import QUESTIONS

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False


@app.route("/")
def index():
    """Landing page"""
    session.clear()
    return render_template("index.html")


@app.route("/start_assessment", methods=["GET", "POST"])
def start_assessment():
    """Initialize the assessment"""
    session["answers"] = {}
    session["current_question"] = 1

    if request.method == "POST":
        investment_amount = request.form.get("investment_amount", "0")
        investment_amount = float(investment_amount.replace(",", ""))
        session["investment_amount"] = investment_amount

    return redirect(url_for("question", question_id=1))


@app.route("/question/<int:question_id>")
def question(question_id):
    """Display a specific question"""
    if question_id < 1 or question_id > len(QUESTIONS):
        return redirect(url_for("index"))

    question = QUESTIONS[question_id - 1]
    progress = (question_id - 1) / len(QUESTIONS) * 100

    return render_template(
        "question.html",
        question=question,
        question_id=question_id,
        total_questions=len(QUESTIONS),
        progress=progress,
    )


@app.route("/submit_answer", methods=["POST"])
def submit_answer():
    """Process answer and move to next question"""
    question_id = int(request.form["question_id"])
    answer_score = float(request.form["answer"])

    # Store answer
    if "answers" not in session:
        session["answers"] = {}
    session["answers"][str(question_id)] = answer_score
    session.modified = True

    # Move to next question or results
    if question_id < len(QUESTIONS):
        return redirect(url_for("question", question_id=question_id + 1))
    else:
        return redirect(url_for("results"))


@app.route("/results")
def results():
    """Calculate risk score and show portfolio recommendations"""

    session["max_possible_score"] = len(QUESTIONS) * 5
    session["sum_possible_score"] = list(session["answers"].values())

    market_state = request.args.get(
        "market_state", session.get("market_state", "normal")
    )
    session["market_state"] = market_state

    # Calculate risk aversion score (lower score = higher risk aversion)
    risk_aversion = sum(session["sum_possible_score"]) / session["max_possible_score"]

    # Get portfolio recommendation
    try:
        print(f"investment_amount: {session['investment_amount']}")
        advisor = RoboAdvisorClass(
            risk_aversion=risk_aversion,
            investment_amount=session["investment_amount"],
            market_state=market_state,
        )
        portfolio_data, _, charts = advisor.optimize_portfolio()

        return render_template(
            "results.html",
            risk_aversion=risk_aversion,
            portfolio=portfolio_data,
            charts=charts,
            market_state=market_state,
            sum_score=int(sum(session["sum_possible_score"]))
        )
    except Exception as e:
        import traceback

        print(f"Error during portfolio optimization: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return render_template("error.html", error=str(e))


@app.route("/additional_results")
def additional_results():

    risk_aversion = sum(session["sum_possible_score"]) / session["max_possible_score"]

    advisor = RoboAdvisorClass(
        risk_aversion=risk_aversion,
        investment_amount=session["investment_amount"],
        market_state=session["market_state"],
    )
    _, ef_plot, _ = advisor.optimize_portfolio()

    return render_template(
        "additional_results.html",
        ef_plot=ef_plot,
    )


if __name__ == "__main__":
    app.run(debug=True)