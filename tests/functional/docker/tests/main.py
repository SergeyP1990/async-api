from utils.wait_for_es import wait_for_es
from utils.wait_for_redis import wait_for_redis


if __name__ == "__main__":
    wait_for_es()
    wait_for_redis()
