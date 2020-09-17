from sqlalchemy     import text

class TweetDao:
    def __init__(self, database):
        self.db     = database

    def insert_tweet(self, user_id, tweet):
        return self.db.execute(text("""
            insert into tweets (
                user_id,
                tweet
            ) values (
                :id,
                :tweet
            )
        """), {
            'id'    : user_id,
            'tweet' : tweet
        }).rowcount

    def get_timeline(self, user_id):
        rows = self.db.execute(text("""
            select 
                t.user_id,
                t.tweet
            from tweets t
            left join users_follow_list ufl
                on ufl.user_id = :user_id
            where t.user_id = :user_id
                or t.user_id = ufl.follow_user_id
        """),{'user_id' : user_id}).fetchall()

        return [{
            'user_id'       : row['user_id'],
            'tweet'         : row['tweet']
        } for row in rows]




