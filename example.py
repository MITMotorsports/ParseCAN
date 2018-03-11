from ParseCAN import spec, data

can = spec.car('./samples/fsae_can_spec.yml')
race = data.race('./samples/')
log = data.log('./samples/fake.log')

brd = can.boards.name['vcu']
print(brd.subscribe)
pub_msgnm = [msg.name for msg in brd.publish.name['can0'].messages]
print(pub_msgnm)

# Test implicit segment enum/values
print([(seg.value, seg.name) for seg in can.buses.name['can0']
       .messages.name['VcuToDash'].segments.name['limp_state'].values])
