import os
from functools import partial
from redis import Redis,from_url
import flask



if os.environ.get('REDISCLOUD_URL'):
    redis = from_url(os.environ['REDISCLOUD_URL'])
else:
    redis = Redis()

add_to_counter =\
        lambda key:\
            [
                (
                    lambda key: redis.get(key) and\
                                redis.incr(key) or\
                                redis.set(key,1)
                )                    
                (key) for x in range(1)
            ] and redis.get(key)


get_counter = lambda key: partial(add_to_counter,key)

cache_count = lambda: redis.set(flask.request.environ['REMOTE_ADDR'],1,px=1500)

check_cache = lambda: redis.get(flask.request.environ['REMOTE_ADDR'])

set_session = lambda: setattr(flask.session,'COUNTED',True)

check_session = lambda: hasattr(flask.session,'COUNTED')

def main():
    counter = get_counter('test3')
    print counter()

if __name__ == "__main__":
    main()

