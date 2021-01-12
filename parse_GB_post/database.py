from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models


class Database:
    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=engine)
        self.session_m = sessionmaker(bind=engine)

    def get_or_create(self, session, model, **data):
        db_model = session.query(model).filter(model.url == data["url"]).first()
        if not db_model:
            db_model = model(**data)
        return db_model

    def create_post(self, data):
        session = self.session_m()
        tags = map(
            lambda tag_data: self.get_or_create(session, models.Tag, **tag_data),
            data["tags"],
        )
        writer = self.get_or_create(session, models.Writer, **data["writer"])
        post = self.get_or_create(session, models.Post, **data["post_data"], writer=writer)
        post.tags.extend(tags)
        session.add(post)

        try:
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()
