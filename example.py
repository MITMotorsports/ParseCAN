from ParseCAN import spec, data

can = spec.car('./fsae_can_spec.yml')
race = data.race('./samples/')
log = data.log('./samples/fake.log')

print(can.boards.name['can_node'].subscribe)
boardnames = [msg.name for msg in can.boards.name['can_node'].subscribe['can0'].messages]
