# routes.py


from flask import request, redirect, render_template
from flask import current_app as app
from models import db, Keyword
from libs.rabbit_wrapper import global_rqueue


@app.route('/', methods=["POST", "GET"])
def suggestions():
    if request.method == "POST":
        # search_for = search_for or 'apple'
        search_for = request.form['keyword']
        if search_for:
            return redirect('/?q={}'.format(search_for))
        else:
            return redirect('/')

    search_for = request.args.get('q')

    if search_for:
        suggestions = db.session.query(Keyword).filter(
            Keyword.keyword.like('%' + search_for + '%')).all()

        if len(suggestions) < 50:
            task = {"keyword": search_for,
                    "country": "US",
                    "search_engine": "google"}

            global_rqueue.publish(task)

        app.logger.debug('for {} found {}'.format(
            search_for, suggestions
        ))
    else:
        suggestions = []
    return render_template('suggestions.html',
                           keyword=search_for,
                           suggestions=suggestions,
                           pagination=False)

