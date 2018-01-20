from ParseCAN import spec, data

can = spec.car('./samples/fsae_can_spec.yml')
race = data.race('./samples/')
log = data.log('./samples/fake.log')

brd = can.boards.name['vcu']
print(brd.subscribe)
pub_msgnm = [msg.name for msg in brd.publish.name['can0'].messages]
print(pub_msgnm)
