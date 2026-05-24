from redis import Redis
from rq import Worker, Queue
from app.config import settings

redis_conn = Redis.from_url(settings.REDIS_URL)

if __name__ == "__main__":
    q = Queue("reviews", connection=redis_conn)
    worker = Worker([q], connection=redis_conn)
    worker.work()
