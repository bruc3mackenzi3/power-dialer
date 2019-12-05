
import logging
from pprint import pformat
import random

import config
from state import AgentState, LeadState
from db import AgentCollection, LeadCollection


class PowerDialer:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._alter_agent_state(AgentState.OFFLINE)

    def on_agent_login(self):
        self._alter_agent_state(AgentState.IDLE)
        self.agent_collection = AgentCollection(self.agent_id)

        number_of_leads = self.agent_collection.get_number_of_leads()  # should always return zero
        while (number_of_leads) < config.DIAL_RATIO:
            lead = LeadCollection.get_lead_phone_number_to_dial()
            if lead:
                number_of_leads += 1
                self.agent_collection.add_lead(lead)
                dial(self.agent_id, lead)
            else:
                break  # out of numbers

    def on_agent_logout(self):
        self._alter_agent_state(AgentState.OFFLINE)
        self.agent_collection.remove_agent()

    def on_call_started(self, lead_phone_number: str):
        self._alter_agent_state(AgentState.ENGAGED)

        # Modify state of current calls
        for lead in self.agent_collection.get_leads():
            if lead == lead_phone_number:
                LeadCollection.update_state(lead, LeadState.ENDED)
            else:
                if LeadCollection.get_state(lead) == LeadState.STARTED:
                    LeadCollection.update_state(lead, LeadState.ABANDONED)
                self.agent_collection.remove_lead(lead)
                # if call failed to nothing

    def on_call_failed(self, lead_phone_number: str):
        # Remove number
        self.agent_collection.remove_lead(lead_phone_number)

        # TODO: remove duplicate code below by moving to helper function
        # Attempt to fill back up
        number_of_leads = self.agent_collection.get_number_of_leads()
        while (number_of_leads < config.DIAL_RATIO):
            lead = LeadCollection.get_lead_phone_number_to_dial()
            if lead:
                self.agent_collection.add_lead(lead)
                dial(self.agent_id, lead)
                number_of_leads += 1
            else:
                break  # the pool is out of numbers

    def on_call_ended(self, lead_phone_number: str):
        ''' Remove number from local state and dial next number
        '''
        self._alter_agent_state(AgentState.IDLE)
        self.agent_collection.remove_lead(lead_phone_number)

        # Attempt to fill back up
        number_of_leads = self.agent_collection.get_number_of_leads()
        while (number_of_leads < config.DIAL_RATIO):
            lead = LeadCollection.get_lead_phone_number_to_dial()
            if lead:
                self.agent_collection.add_lead(lead)
                dial(self.agent_id, lead)
                number_of_leads += 1
            else:
                break  # the pool is out of numbers

    def _alter_agent_state(self, state: AgentState):
        logging.info('{} {}'.format(self.agent_id, str(state)))
        self.agent_state = state


# Implementation of dial service
def dial(agent_id: str, lead_phone_number: str):
    ''' Given a lead_phone_number (assumed to be QUEUED) dial the number.
    Once complete set the state in the DB which can be checked by the calling
    code.

    The result of the call is mocked with random numbers.  Adjust SUCCESS_RATIO
    to configure this.
    '''
    if config.SUCCESS_RATIO > random.random():
        dial_result = LeadState.STARTED
    else:
        dial_result = LeadState.FAILED
    LeadCollection.update_state(lead_phone_number, dial_result)


def main():
    dialers = []
    for i in range(config.NUMBER_OF_AGENTS):
        dialer = PowerDialer('agent' + str(i+1))
        dialer.on_agent_login()
        dialers.append(dialer)

    # Main event loop
    # Takes round robin approach, allowing each agent one turn / state change
    #  before going on to next.
    while len(dialers) > 0:
        for dialer in dialers:
            logging.debug('================')
            if dialer.agent_collection.get_number_of_leads() > 0:
                # Print out current state
                logging.debug('{}\n{}\n{}'.format(
                        dialer.agent_id,
                        pformat(dialer.agent_collection.get_leads()),
                        pformat(LeadCollection._leads)
                ))

                # Get latest Lead and Agent states
                lead = dialer.agent_collection.get_next_lead()
                lead_state = LeadCollection.get_state(lead)

                # State machine
                if dialer.agent_state == AgentState.IDLE and lead_state == LeadState.STARTED:
                    dialer.on_call_started(lead)
                elif dialer.agent_state == AgentState.IDLE and lead_state == LeadState.FAILED:
                    dialer.on_call_failed(lead)
                elif dialer.agent_state == AgentState.ENGAGED:
                    dialer.on_call_ended(lead)
            else:
                dialer.on_agent_logout()
                dialers.remove(dialer)

    logging.info('LEADS POOL FINAL STATE\n{}'.format(pformat(LeadCollection._leads)))


if __name__ == '__main__':
    main()
