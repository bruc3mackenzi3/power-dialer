import logging

from state import LeadState


class AgentCollection:
    ''' Mock database collection for a logged in agent and their current leads.
    '''

    _agents = {}

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        AgentCollection._agents[self.agent_id] = []

    def remove_agent(self):
        if self.agent_id in AgentCollection._agents:
            del AgentCollection._agents[self.agent_id]

    def add_lead(self, lead_phone_number: str):
        ''' Raises KeyError if agent_id is missing
        '''
        AgentCollection._agents[self.agent_id].append(lead_phone_number)

    def get_next_lead(self) -> str:
        ''' Returns the next lead phone number to engage
        '''
        if AgentCollection._agents[self.agent_id]:
            return AgentCollection._agents[self.agent_id][0]
        else:
            return None

    def get_leads(self) -> list:
        # Lists are mutable so return a copy
        return AgentCollection._agents[self.agent_id].copy()

    def remove_lead(self, lead_phone_number: str):
        AgentCollection._agents[self.agent_id].remove(lead_phone_number)

    def get_number_of_leads(self) -> int:
        ''' Return number of leads currently stored for agent_id.
        Raises KeyError if agent_id is missing
        '''
        return len(AgentCollection._agents[self.agent_id])


class LeadCollection:
    ''' Mock database collection storing the pool of leads.  Note this is a
    global resource so all interaction is static; there is no interface for
    instances.
    '''

    _leads = {
        '222-384-6115': LeadState.AVAILABLE,
        '333-911-0414': LeadState.AVAILABLE,
        '444-763-9619': LeadState.AVAILABLE,
        '555-430-7663': LeadState.AVAILABLE,
        '666-919-5533': LeadState.AVAILABLE,
        '777-609-4348': LeadState.AVAILABLE
    }

    @staticmethod
    def get_lead_phone_number_to_dial() -> str:
        ''' Finds and returns the first available lead, marking it as QUEUED so
        no other agent can take it.  Returns None is no leads are currently
        available.
        '''
        for lead, state in LeadCollection._leads.items():
            if state == LeadState.AVAILABLE:
                LeadCollection._leads[lead] = LeadState.QUEUED
                return lead
        logging.warning('No more available leads')
        return None

    @staticmethod
    def get_state(lead: str) -> LeadState:
        ''' Given a lead phone number return its state, None if no found
        '''
        if lead in LeadCollection._leads:
            return LeadCollection._leads[lead]
        else:
            return None

    @staticmethod
    def update_state(lead: str, state: LeadState):
        ''' Update lead with state.  No effect if lead not found.
        '''
        if lead in LeadCollection._leads:
            LeadCollection._leads[lead] = state
