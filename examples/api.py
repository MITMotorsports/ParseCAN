b = {busnm: {msgnm: {valnm: val.unit if val.unit else None for valnm, val in msg.segments.name.items()} for msgnm, msg in bus.messages.name.items()} for busnm, bus in car.buses.name.items()}
