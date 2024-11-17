import threading

from component import Component

if __name__ == '__main__':
    component = Component()
    component_thread = threading.Thread(target=component.start)
    component_thread.start()