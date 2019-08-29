# routes.py


from flask import request, redirect, render_template
from flask import current_app as app
from models import db, Keywords
from libs.rabbit_manager import global_rqueue

from sug_config import ALPHABETS


def add_suffixes(keyword):
    for char in ALPHABETS:
        yield '{} {}'.format(keyword, char)
        yield '{} {}'.format(char, keyword)


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
    app.logger.info('got request with q = {}'.format(search_for))
    if search_for:
        suggestions = db.session.query(Keywords).filter(
            Keywords.keyword.like('%' + search_for + '%')).all()

        app.logger.info('for {} in base {} rows'.format(
            search_for, len(suggestions)))
        if len(suggestions) < 50:
            for part in add_suffixes(search_for):
                task = {"keyword": part,
                        "country": "US",
                        "search_engine": "duckduckgo"}
                global_rqueue.publish(task)

        app.logger.debug('for {} found {}'.format(
            search_for, suggestions
        ))
    else:
        suggestions = []
    return render_template('suggestions.html',
                           keyword=search_for,
                           suggestions=suggestions,
                           results_count=len(suggestions),
                           pagination=False)

