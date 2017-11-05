from ParseCAN import spec, data

spec = spec.can('./fsae_can_spec.yml')
race = data.race('./samples/')
log = data.log('./samples/fake.log')

for inp in race.interpret(spec):
    print(inp)

print('Here is the interpretation of the entire race.')

log.csv('./samples/log.csv')
print('Generated csv in samples/log!')

for msg in log:
    print(msg.time, hex(msg.can_id), msg.interpret(spec))

print('Here is the interpretation of fake.log.')
