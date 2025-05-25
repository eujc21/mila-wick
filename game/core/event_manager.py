from collections import defaultdict

class EventManager:
    def __init__(self):
        '''Initialize the EventManager'''
        self.listeners = defaultdict(list)
        print("EventManager initialized.")

    def subscribe(self, event_type, listener_callback):
        '''Subscribe a listener callback to an event type.'''
        self.listeners[event_type].append(listener_callback)
        print(f"Listener {listener_callback.__name__} subscribed to {event_type}")

    def unsubscribe(self, event_type, listener_callback):
        '''Unsubscribe a listener callback from an event type.'''
        if listener_callback in self.listeners[event_type]:
            self.listeners[event_type].remove(listener_callback)
            print(f"Listener {listener_callback.__name__} unsubscribed from {event_type}")
        else:
            print(f"Warning: Listener {listener_callback.__name__} not found for event {event_type}")

    def emit(self, event_type, data=None):
        '''Emit an event to all subscribed listeners.'''
        # print(f"Emitting event: {event_type} with data: {data}") # Can be noisy
        for listener in self.listeners[event_type]:
            try:
                listener(data)
            except Exception as e:
                print(f"Error in listener {listener.__name__} for event {event_type}: {e}")
