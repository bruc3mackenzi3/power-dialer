
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

    def get_number_of_leads(self):
        ''' Return number of leads currently stored for agent_id.
        Raises KeyError if agent_id is missing
        '''
        return len(AgentCollection._agents[self.agent_id])
