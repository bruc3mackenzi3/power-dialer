import unittest
import sys

sys.path.append('.')

from db import AgentCollection, LeadCollection
from state import LeadState

class AgentCollectionTest(unittest.TestCase):
    def setUp(self):
        self.agent_coll = AgentCollection('test_agent')
        self.test_number = '647-000-0000'

    def test_add_lead(self):
        self.agent_coll.add_lead(self.test_number)
        self.assertEqual(self.agent_coll._agents, {'test_agent': [self.test_number]})

    def test_get_next_lead(self):
        self.agent_coll.add_lead(self.test_number)
        lead = self.agent_coll.get_next_lead()
        self.assertEqual(lead, self.test_number)

    def test_get_leads(self):
        self.agent_coll.add_lead(self.test_number)
        leads = self.agent_coll.get_leads()
        self.assertEqual(leads, [self.test_number])

    def test_remove_lead(self):
        self.agent_coll.add_lead(self.test_number)
        self.agent_coll.remove_lead(self.test_number)
        leads = self.agent_coll.get_leads()
        self.assertEqual(leads, [])

    def test_get_number_of_leads(self):
        self.agent_coll.add_lead(self.test_number)
        num = self.agent_coll.get_number_of_leads()
        self.assertEqual(num, 1)

    def test_remove_agent(self):
        self.agent_coll.remove_agent()
        self.assertEqual(self.agent_coll._agents, {})


class LeadCollectionTest(unittest.TestCase):
    def setUp(self):
        self.number = '222-384-6115'

    def test_get_lead_phone_number_to_dial(self):
        self.assertEqual(LeadCollection.get_lead_phone_number_to_dial(), self.number)

    def test_get_state(self):
        # 2 is the value of LeadState.QUEUED
        self.assertEqual(LeadCollection.get_state(self.number), LeadState.QUEUED)

    def test_update_state(self):
        LeadCollection.update_state(self.number, LeadState.ABANDONED)
        self.assertEqual(LeadCollection.get_state(self.number), LeadState.ABANDONED)


if __name__ == '__main__':
    unittest.main( )
