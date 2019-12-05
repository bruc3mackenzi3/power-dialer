# Power Dialer

## Run Instructions
Python 3 is required; this app is not Python 2 compatible.  Only standard library modules are used so no installations beyond Python 3 are required.

To run the program:
```
python power_dialer.py
```
or:
```
python3 power_dialer.py
```

Program execution can be observed on stdout.

### Configuration

The Power Dialer app behaviour can be altered with the configuration file `config.py`.  The following can be altered:

`DIAL_RATIO` controls the number of concurrent numbers dialed for each agent online.  To maintain minimal call abandon rate it's recommended to be set at 2.

`SUCCESS_RATIO` represents the percentage of calls that will succeed in the lead answering the phone, as a decimal.  For example, with a success ratio of 0.25 one call will suceed for every 3 failures.

`NUMBER_OF_AGENTS` is the number of concurrent agents online.  Try running with 1 and 2 as a starting point.  Also try running more agents than there are leads in the pool * DIAL RATIO.

Finally adjust the log level set in the logging config call.  Levels utilized in this app are `WARNING`, `INFO`, and `DEBUG`.

# Original Instructions

## The Problem
The goal of the exercise is to build a power dialer.
The users are agents for which the system dials from a pool of leads.
Given that a subset of the outbound dials fails (e.g voicemail, no answer etc.),
we set the DIAL_RATIO=2; i.e for each agent, dial 2 leads at any point in time.
This increases the Agent Utilization (% of time the agent is on a call)
while maintaining a small Abandon Rate (% calls abandoned because no agent was
available to take it).

## The Solution
Your task is to implement the PowerDialer class. Assume that it's used on distributed
system (e.g AWS Lambda) with concurrent executions.
Furthermore, assume that the executions are stateless
and all state is stored on a remote data store (e.g RDS, Dynamodb etc.)
We suggest stubbing any database you choose to use for this exercise.
Complete this exercise as you'd write production quality code (including tests where you think is appropriate).

## Instructions
Use Python 3 preferably.
Please post your solution on to a Git Hub into a private repo and share it with us.
Please include basic documentation and unit tests.
Ensure that tests can be executed and test main power dialing algorithm concurrent dials.
