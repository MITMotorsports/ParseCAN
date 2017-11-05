# ParseCAN
A Python package for integrating CAN specifications and parsing logged CAN messages.

## Structure
This package is intuitively split into two top-level sub-packages: `ParseCAN.spec` and `ParseCAN.data`.

### spec
`raise NotWrittenError`

### data
`ParseCAN.data` provides classes whose instances specify CAN messages, logs, and races.

#### Messages
There are two message variants:
- `ParseCAN.spec.message`
- `ParseCAN.spec.messageTimed`

#### Logs
Log instances point to a log file full of CAN messages.
Found under `ParseCAN.data.log`.

#### Races
Races are collections of logs collected in sequence, but split across multiple files.
Found under `ParseCAN.data.race`.
