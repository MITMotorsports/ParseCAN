from ParseCAN import spec, data

spec = spec.can('./fsae_can_spec.yml')
log = data.log('./samples/fake.log')


log.csv('./samples/log.csv')
print('Generated csv in samples/log!')

for msg in log:
    print(msg.time, hex(msg.can_id), msg.interpret(spec))

print('Here is the interpretation of this fake log.')
