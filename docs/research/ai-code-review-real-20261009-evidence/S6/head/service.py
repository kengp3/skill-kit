def execute(state, key, count):
    if key in state['done']:
        return state['done'][key]
    if count < 1 or count > state['stock']:
        return 'rejected'
    state['stock'] -= count
    state['done'][key] = 'accepted'
    return 'accepted'
