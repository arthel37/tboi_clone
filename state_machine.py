class StateMachine:
    def __init__(self):
        self.state = 'menu'

    def get_state(self):
        return self.state
    
    def set_state(self, new_state):
        self.state = new_state