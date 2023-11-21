from datetime import timedelta
from flask import Flask, redirect, url_for, render_template, request, session, json
from werkzeug import Response

import Clusters
import Plot_generator
import lavoro_api_calls
import data_manipulation
import database

app = Flask(__name__)
app.secret_key = 'energy_key'
app.permanent_session_lifetime = timedelta(minutes=10)


@app.route('/', methods=["POST", "GET"])
def home() -> Response | str:
    """
    Creates an API endpoint for the root of the website (index).
    There are two possible methods for this function:

    -POST: Used when the user calls the lavoro.csd.auth API.
    -GET: Returns a rendering of the index.html template file.

    :return: (Response | str)The rendered HTML file or a Response for redirection to the results.html page.
    """
    # When lavoro API is called.
    if request.method == "POST":
        session["ID"] = request.form['energyID']
        return redirect(url_for('results'))

    elif request.method == "GET":
        message = "None"
        # If a message is stored into the session, prints it out.
        if "message" in session:
            message = session["message"]
            session.pop("message", None)
        return render_template("index.html", message=message)


@app.route("/form_page1", methods=["POST", "GET"])
def form_page1() -> Response | str:
    """
    Creates an API endpoint for the first form (Form1).
    If the user does not use the lavoro API option, they need to fill out the first form with their household and
    occupants information.
    There are two possible methods for this function:

    -POST: Used when the user submits the filled form.
    -GET: Returns a rendering of the Form1.html template file when the user gets redirected to it.

    :return: (Response | str)The rendered HTML file or a Response for redirection to the Form2.html page.
    """
    if request.method == "POST":
        # When the form gets submitted
        form_data = request.form
        serialized_form_data = json.dumps(form_data)
        session["form1_data"] = serialized_form_data

        return redirect(url_for('form_page2'))

    elif request.method == "GET":

        if request.referrer == f"http://{request.host}{url_for('home')}" or \
                request.referrer == f"http://{request.host}{url_for('results')}":
            session.clear()

        serialized_form_data = session.get('form1_data')

        if serialized_form_data is not None:
            form_data = json.loads(serialized_form_data)
            return render_template("Form1.html", form_data=form_data)
        else:
            return render_template("Form1.html", form_data="")


@app.route("/form_page2", methods=["POST", "GET"])
def form_page2() -> Response | str:
    """
    Creates an API endpoint for the second form (Form2).
    This is the last form that a user has to fill before the results are presented and contains Energy Related Information.
    There are two possible methods for this function:

    -POST: Used when the user submits the filled form.
    -GET: Returns a rendering of the Form2.html template file when the user gets redirected to it.

    :return: (Response | str)The rendered HTML file or a Response for redirection to the results.html page.
    """
    if request.method == "POST":
        # When the form gets submitted
        form_data = request.form
        serialized_form_data = json.dumps(form_data)
        session["form2_data"] = serialized_form_data

        return redirect(url_for('results'))

    elif request.method == "GET":

        serialized_form_data = session.get('form2_data')

        if serialized_form_data is not None:
            form_data = json.loads(serialized_form_data)
            return render_template("Form2.html", form_data=form_data)
        else:
            return render_template("Form2.html", form_data="")


def home_redirection_error(message) -> Response:
    """
    Whenever an exception occurs or there is missing information, redirects to the homepage (index.html) and saves
    the message to the session storage, which will be displayed on the screen.

    :param message: (str) The notification message.
    :return: (Response) A Response for redirection to the home.html page.
    """
    session["message"] = message
    return redirect(url_for('home'))


@app.route("/results", methods=["GET"])
def results() -> Response | str:
    """
    Creates an API endpoint for the results page (results).
    Presents the results after the execution of the algorithms from the backend and displays the final plots and
    messages to the user based on their consumption.
    It supports the GET method that either redirects to the home page and displays a message on the screen if there is
    missing information, or returns a rendering of the results.html template file when the user gets redirected to it.

    :return: (Response | str)The rendered HTML file or a Response for redirection to the home.html page.
    """
    if request.method == "GET":

        # When lavoro API is called.
        if "ID" in session:
            db = database.get_database()

            api_reply, consumption = lavoro_api_calls.get_element(session["ID"])
            if api_reply is None and consumption is None:
                return home_redirection_error("Wrong ID, please enter a valid one.")

            try:
                record = data_manipulation.transform_data_API(api_reply, consumption)

                prediction, data_frame = Clusters.apply_algorithm(db, record)

                plots = Plot_generator.PlotGenerator(data_frame, prediction, consumption, record)
            except (BaseException,):
                return home_redirection_error("An error occurred during the calculations, please try again later.")
            else:
                return render_template("results.html", pred=prediction, actual=consumption, plots=plots)

        # If both of the forms are stored into the session storage, then it redirects to results page.
        if not ("form1_data" in session):
            if not ("form2_data" in session):
                return home_redirection_error("Please, fill the required fields again")
            else:
                session.pop("form2_data", None)
                return home_redirection_error("Please, fill the required fields again")

        elif "form2_data" in session:

            db = database.get_database()

            record = database.save_data(db, json.loads(session["form1_data"]), json.loads(session["form2_data"]))
            prediction, data_frame = Clusters.apply_algorithm(db, record)
            actual_value = record["Kwh/day/m2"]

            plots = Plot_generator.PlotGenerator(data_frame, prediction, actual_value, record)

            return render_template("results.html", pred=prediction, actual=actual_value, plots=plots)
        else:
            session.pop("form1_data", None)
            return home_redirection_error("Please, fill the required fields again")


if __name__ == "__main__":
    app.run(debug=True)
