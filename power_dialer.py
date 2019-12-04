
import logging
from pprint import pprint
import random

from state import AgentState, LeadState
from db import AgentCollection, LeadCollection


logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

DIAL_RATIO = 3


class PowerDialer:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._alter_agent_state(AgentState.OFFLINE)


    def on_agent_login(self):
        self._alter_agent_state(AgentState.IDLE)
        self.agent_collection = AgentCollection(self.agent_id)

        number_of_leads = self.agent_collection.get_number_of_leads()  # should always return zero
        while (number_of_leads) < DIAL_RATIO:
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
        while (number_of_leads < DIAL_RATIO):
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
        while (number_of_leads < DIAL_RATIO):
            lead = LeadCollection.get_lead_phone_number_to_dial()
            if lead:
                self.agent_collection.add_lead(lead)
                dial(self.agent_id, lead)
                number_of_leads += 1
            else:
                break  # the pool is out of numbers


    def _alter_agent_state(self, state: AgentState):
        logging.info(str(state))
        self.agent_state = state


# services you can call
def dial(agent_id: str, lead_phone_number: str):
    ''' Given a lead_phone_number (assumed to be QUEUED) dial the number.
    Once complete set the state in the DB which can be checked by the calling
    code.
    '''
    dial_result = random.choice([LeadState.STARTED, LeadState.FAILED])
    LeadCollection.update_state(lead_phone_number, dial_result)


def main():
    dialer = PowerDialer('agent1')
    dialer.on_agent_login()

    # main event loop
    while dialer.agent_collection.get_number_of_leads() > 0:
        # Print out current state
        print()
        pprint(dialer.agent_collection.get_leads())
        pprint(LeadCollection._leads)

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

    dialer.on_agent_logout()

    print()
    pprint(LeadCollection._leads)


if __name__ == '__main__':
    main()
