
import enum
import logging
from pprint import pprint
import random

from db import AgentCollection


logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

class AgentState(enum.Enum):
    OFFLINE = 1
    IDLE = 2
    ENGAGED = 3

class LeadState(enum.Enum):
    AVAILABLE = 1
    QUEUED = 2
    STARTED = 3
    FAILED = 4
    ENDED = 5
    ABANDONED = 6

DIAL_RATIO = 2

lead_phone_numbers_pool = {
    '865-384-6115': LeadState.AVAILABLE,
    '682-911-0414': LeadState.AVAILABLE,
    '618-763-9619': LeadState.AVAILABLE
}


class PowerDialer:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._alter_agent_state(AgentState.OFFLINE)


    def on_agent_login(self):
        self._alter_agent_state(AgentState.IDLE)
        self.agent_collection = AgentCollection(self.agent_id)

        number_of_leads = self.agent_collection.get_number_of_leads()  # should always return zero
        while (number_of_leads) < DIAL_RATIO:
            lead = get_lead_phone_number_to_dial()
            if lead:
                number_of_leads += 1
                self.agent_collection.add_lead(lead)
                dial(self.agent_id, lead)
            else:
                break  # out of numbers

        return self.agent_collection.get_number_of_leads()


    def on_agent_logout(self):
        self._alter_agent_state(AgentState.OFFLINE)
        self.agent_collection.remove_agent()


    def on_call_started(self, lead_phone_number: str):
        self._alter_agent_state(AgentState.ENGAGED)

        # Modify state of current calls
        for lead in self.agent_collection.get_leads():
            if lead == lead_phone_number:
                lead_phone_numbers_pool[lead] = LeadState.ENDED
            else:
                if lead_phone_numbers_pool[lead] == LeadState.STARTED:
                    lead_phone_numbers_pool[lead] = LeadState.ABANDONED
                self.agent_collection.remove_lead(lead)
                # if call failed to nothing

        return self.agent_collection.get_number_of_leads()


    def on_call_failed(self, lead_phone_number: str):
        # Remove number
        self.agent_collection.remove_lead(lead_phone_number)

        # Attempt to fill back up
        number_of_leads = self.agent_collection.get_number_of_leads()
        while (number_of_leads < DIAL_RATIO):
            lead = get_lead_phone_number_to_dial()
            if lead:
                self.agent_collection.add_lead(lead)
                dial(self.agent_id, lead)
                number_of_leads += 1
            else:
                break  # the pool is out of numbers

        return self.agent_collection.get_number_of_leads()


    def on_call_ended(self, lead_phone_number: str):
        ''' Remove number from local state and dial next number
        '''
        self._alter_agent_state(AgentState.IDLE)
        self.agent_collection.remove_lead(lead_phone_number)

        # TODO: adapt loop from on_call_failed
        lead = get_lead_phone_number_to_dial()
        if lead:
            self.agent_collection.add_lead(lead)
            dial(self.agent_id, lead)

        return self.agent_collection.get_number_of_leads()


    def _alter_agent_state(self, state):
        logging.info(str(state))
        self.agent_state = state


# services you can call
def dial(agent_id: str, lead_phone_number: str):
    ''' Given a lead_phone_number (assumed to be QUEUED) dial the number.
    Once complete set the state in the DB which can be checked by the calling
    code.
    '''
    dial_result = random.choice([LeadState.STARTED, LeadState.FAILED])
    lead_phone_numbers_pool[lead_phone_number] = dial_result


def get_lead_phone_number_to_dial() -> str:
    ''' Return the phone number of an available lead.  Returns None is no leads
    are currently available.
    '''
    for lead, state in lead_phone_numbers_pool.items():
        if state == LeadState.AVAILABLE:
            lead_phone_numbers_pool[lead] = LeadState.QUEUED
            return lead
    logging.warning('No more available leads')
    return None


def main():
    dialer = PowerDialer('agent1')
    number_of_leads = dialer.on_agent_login()

    # main event loop
    while number_of_leads > 0:
        # Print out current state
        print()
        pprint(dialer.agent_collection.get_leads())
        pprint(lead_phone_numbers_pool)

        # Get latest Lead and Agent states
        lead = dialer.agent_collection.get_next_lead()
        number_state = lead_phone_numbers_pool[lead]

        # State machine
        if dialer.agent_state == AgentState.IDLE and number_state == LeadState.STARTED:
            number_of_leads = dialer.on_call_started(lead)
        elif dialer.agent_state == AgentState.IDLE and number_state == LeadState.FAILED:
            number_of_leads = dialer.on_call_failed(lead)
        elif dialer.agent_state == AgentState.ENGAGED:
            number_of_leads = dialer.on_call_ended(lead)

    dialer.on_agent_logout()

    print()
    pprint(lead_phone_numbers_pool)


if __name__ == '__main__':
    main()
