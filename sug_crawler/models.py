
# models.py

from init_app import db


class Keyword(db.Model):
    '''
    # insert sample data with ignore
    stmt = Keyword.__table__.insert().prefix_with('OR IGNORE').values([
        {'keyword': 'apple'}, {'keyword': 'apple pie'}
    ])
    db.session.execute(stmt)
    db.session.commit()
    '''
    id = db.Column('sug_id', db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, keyword):
        self.keyword = keyword

