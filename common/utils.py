import threading


class ServerUtils:
    @staticmethod
    def async_run(func):
        def decorator(*args, **kwargs):
            th = threading.Thread(target=func, args=args, kwargs=kwargs)
            th.start()
            return th

        return decorator


class UniqueId:
    _UID = 1001001

    @staticmethod
    def generate() -> int:
        # return uuid.uuid1().int

        id_ = UniqueId._UID
        UniqueId._UID += 1
        return id_
