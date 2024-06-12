import _thread
import usys


class EventStore(object):
    def __init__(self):
        self.map = dict()
        self.log = None

    def append(self, event, cb):
        self.map[event] = cb

    def fire_async(self, event, msg):
        if event in self.map:
            _thread.start_new_thread(self.map[event], (event, msg))
            if self.log:
                self.log.info("ASYNC executed (event) -> {} (params) -> {} (result) -> {}".format(event, msg, None))

    def fire_sync(self, event, msg):
        res = None
        try:
            if event in self.map:
                res = self.map[event](event, msg)
        except Exception as e:
            usys.print_exception(e)
        if self.log:
            self.log.info("SYNC executed (event) -> {} (params) -> {} (result) -> {}".format(event, msg, res))
        return res

    def print_map(self):
        print(self.map)


event_store = EventStore()


def print_ev_map():
    event_store.print_map()

def subscribe(event, cb):
    """
    subscribe event and cb
    """
    return event_store.append(event, cb)


def publish(event, msg=None):
    """
    publish event and msg
    """
    return publish_sync(event, msg)


def publish_async(event, msg=None):
    """
    异步发送
    """
    return event_store.fire_async(event, msg)


def publish_sync(event, msg=None):
    """
    同步发送
    """
    return event_store.fire_sync(event, msg)


def set_log(log_adapter):
    event_store.log = log_adapter
