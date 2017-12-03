from ParseCAN import spec, data

can = spec.can('./fsae_can_spec.yml')
race = data.race('./samples/')
log = data.log('./samples/fake.log')

# for inp in race.interpret(can):
#     print(inp)
#
# print('Here is the interpretation of the entire race.')
#
# log.csv('./samples/log.csv')
# print('Generated csv in samples/log!')

for msg in log:
    if msg.can_id == 0x522:
        print(msg.time, hex(msg.can_id), hex(msg.data), can.interpret(msg))

print('Here is the interpretation of fake.log.')
