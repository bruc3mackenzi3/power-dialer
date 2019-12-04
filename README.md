# Power Dialer

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
