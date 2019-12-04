
import enum
import logging
from pprint import pprint
import random


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
        self.current_leads = None

    def on_agent_login(self):
        self._alter_agent_state(AgentState.IDLE)
        self.current_leads = []

        while (len(self.current_leads) < DIAL_RATIO):
            if self._get_lead_phone_number_to_dial():
                dial(self.agent_id, self.current_leads[-1])
            else:
                break  # out of numbers

    def on_agent_logout(self):
        self._alter_agent_state(AgentState.OFFLINE)
        self.current_leads = []

    def on_call_started(self, lead_phone_number: str):
        self._alter_agent_state(AgentState.ENGAGED)

        # Modify state of current calls
        for lead in self.current_leads:
            if lead == lead_phone_number:
                lead_phone_numbers_pool[lead] = LeadState.ENDED
            else:
                if lead_phone_numbers_pool[lead] == LeadState.STARTED:
                    lead_phone_numbers_pool[lead] = LeadState.ABANDONED
            # if call failed to nothing

        # Drop other calls
        self.current_leads = [lead_phone_number]

    def on_call_failed(self, lead_phone_number: str):
        # Remove number
        self.current_leads.remove(lead_phone_number)

        # Attempt to fill back up
        while (len(self.current_leads) < DIAL_RATIO):
            if self._get_lead_phone_number_to_dial():
                dial(self.agent_id, self.current_leads[-1])
            else:
                break  # out of numbers

    def on_call_ended(self, lead_phone_number: str):
        ''' Remove number from local state and dial next number
        '''
        self._alter_agent_state(AgentState.IDLE)
        self.current_leads.remove(lead_phone_number)

        number = self._get_lead_phone_number_to_dial()
        if number:
            dial(self.agent_id, number)

    # Private helper functions
    def _get_lead_phone_number_to_dial(self):
        number = get_lead_phone_number_to_dial()
        if number:
            self.current_leads.append(number)
        return number

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
    dialer.on_agent_login()

    # main event loop
    while (len(dialer.current_leads) > 0):
        # Print out current state
        print()
        pprint(dialer.current_leads)
        pprint(lead_phone_numbers_pool)

        # Get latest Lead and Agent states
        number = dialer.current_leads[0]
        number_state = lead_phone_numbers_pool[number]

        # State machine
        if dialer.agent_state == AgentState.IDLE and number_state == LeadState.STARTED:
            dialer.on_call_started(number)
        elif dialer.agent_state == AgentState.IDLE and number_state == LeadState.FAILED:
            dialer.on_call_failed(number)
        elif dialer.agent_state == AgentState.ENGAGED:
            dialer.on_call_ended(number)

    dialer.on_agent_logout()

    print()
    pprint(lead_phone_numbers_pool)


if __name__ == '__main__':
    main()
