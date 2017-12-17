from ParseCAN import spec, data

can = spec.car('./fsae_can_spec.yml')
race = data.race('./samples/')
log = data.log('./samples/fake.log')

boardnames = [msg.name for msg in can.boards['can_node'].subscribe['can0'].messages]
