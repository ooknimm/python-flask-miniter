import jwt 
from flask.json     import JSONEncoder
from functools      import wraps
from flask          import Response, current_app, g, request, jsonify, send_file
import json
from werkzeug.utils import secure_filename



class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(set,obj):
            return list(obj)
        return JSONEncoder.default(self,obj)

###################
## decorator
###################

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token    = request.headers.get('Authorization')
        if access_token is not None:
            try:
                payload = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], 'HS256')
            except jwt.InvaildTokenError:
                payload = None

            if payload is None:
                return Response(status=401)

            user_id     = payload['user_id']
            g.user_id   = user_id
        else:
            return Response(status=401)
        return f(*args, **kwargs)
    return decorated_function

##########################

def create_endpoints(app, services):
    
    app.json_encoder = CustomJSONEncoder

    user_service    = services.user_service
    tweet_service  = services.tweet_service

    @app.route('/ping', methods=['get'])
    def ping():
        return 'pong'

    @app.route('/sign-up', methods=['post'])
    def sign_up():
        new_user        = request.json
        new_user        = user_service.create_new_user(new_user)

        return jsonify(new_user)

    @app.route('/login', methods=['post'])
    def login():
        credential              = request.json
        authorized, user_id     = user_service.login(credential)

        if authorized:
            token   = user_service.generate_access_token(user_id)

            return jsonify({
                'user_id'   : user_id,
                'access_token'  : token
            })
        else:
            '', 401

    @app.route('/tweet', methods=['post'])
    @login_required
    def tweet():
        payload         = request.json
        tweet           = payload['tweet']
        user_id         = g.user_id

        result = tweet_service.tweet(user_id, tweet)
        if result is None:
            return '300자 초과', 400

        return '', 200

    @app.route('/follow', methods=['post'])
    @login_required
    def follow():
        payload         = request.json
        follow_id       = payload['follow']
        user_id         = g.user_id

        user_service.follow(user_id, follow_id)

        return '',200

    @app.route('/unfollow', methods=['post'])
    @login_required
    def unfollow():
        payload         = request.json
        unfollow_id     = payload['unfollow']
        user_id         = g.user_id

        user_service.unfollow(user_id, unfollow_id)
        
        return '',200

    @app.route('/timeline/<int:user_id>', methods=['get'])
    def timeilne(user_id):
        timeline        = tweet_service.timeline(user_id)

        return jsonify({
            'user_id'       : user_id,
            'timeline'      : timeline
        })
    @app.route('/timeline', methods=['get'])
    @login_required
    def user_timeline():
        timeline        = tweet_service.timeline(g.user_id)

        return {
            'user_id'       : g.user_id,
            'timeline'      : timeline
        }

    @app.route('/profile-picture', methods=['post'])
    @login_required
    def upload_profile_picture():
        
        user_id = g.user_id

        if 'profile_pic' not in request.files:
            return 'file is missing', 404

        profile_pic = request.files['profile_pic']

        if profile_pic.filename == '':
            return 'file is missing', 404

        filename = secure_filename(profile_pic.filename)
        user_service.save_profile_picture(profile_pic, filename, user_id)

        return '', 200

    
    @app.route('/profile-picture/<int:user_id>', methods=['get'])
    def get_profile_picture(user_id):
        profile_picture = user_service.get_profile_picture(user_id)

        if profile_picture:
            return jsonify({'img_url': profile_picture}) 
        else:
            return '',404
