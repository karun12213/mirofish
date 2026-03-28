import sys
from unittest.mock import MagicMock
import json
import logging

logger = logging.getLogger("mock_apis")

class ZepMockObject:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
            
    def __getattr__(self, name):
        return None

# Mock OpenAI
class MockOpenAIChoices:
    def __init__(self, content):
        self.message = MagicMock()
        self.message.content = content
        self.finish_reason = "stop"

class MockOpenAIResponse:
    def __init__(self, content):
        self.choices = [MockOpenAIChoices(content)]

class MockOpenAI:
    def __init__(self, *args, **kwargs):
        self.chat = MagicMock()
        def create_mock(*args, **kwargs):
            logger.info("Mock OpenAI called")
            messages = kwargs.get("messages", [])
            prompt = ""
            for m in messages:
                prompt += str(m.get("content", ""))
            
            is_json_request = "json" in prompt.lower() or "schema" in prompt.lower() or "entities" in prompt.lower() or kwargs.get("response_format")
            
            if is_json_request:
                mock_json = {
                    "entities": [{"name": "Alice (Mock)", "description": "A mock person", "type": "Person"}],
                    "relations": [],
                    "agent_configs": [
                        {
                            "agent_id": 0,
                            "activity_level": 0.5,
                            "posts_per_hour": 1,
                            "comments_per_hour": 2,
                            "active_hours": [9, 10, 11, 12, 13, 14, 15, 16],
                            "response_delay_min": 1,
                            "response_delay_max": 10,
                            "sentiment_bias": 0.0,
                            "stance": "neutral",
                            "influence_weight": 1.0
                        }
                    ],
                    "time_config": {
                        "total_simulation_hours": 24,
                        "minutes_per_round": 60,
                        "agents_per_hour_min": 1,
                        "agents_per_hour_max": 5,
                        "peak_hours": [20, 21],
                        "off_peak_hours": [3, 4],
                        "morning_hours": [8],
                        "work_hours": [10]
                    },
                    "hot_topics": ["Mocked Topic"],
                    "narrative_direction": "Mock direction",
                    "initial_posts": [
                        {"content": "Hello World from Mock", "poster_type": "Person"}
                    ],
                    "reasoning": "Mock reasoning",
                    "report_content": "# Mock Report\nThis is a mocked report.",
                    "analysis": "Mock analysis"
                }
                return MockOpenAIResponse(json.dumps(mock_json))
            else:
                last_msg = messages[-1].get("content", "") if messages else ""
                reply = f"Mocked Agent Reply: I am functioning perfectly in Mock API mode! You asked: '{last_msg}'."
                return MockOpenAIResponse(reply)
        self.chat.completions.create = create_mock

import openai
openai.OpenAI = MockOpenAI

# Mock Zep
class MockNode:
    def get(self, *args, **kwargs):
        return ZepMockObject(
            uuid_=kwargs.get("uuid_", "id"),
            name="MockNode_" + str(kwargs.get("uuid_", "id")),
            labels=["Person"],
            summary="Mock summary",
            attributes={"entity_type": "Person"}
        )
    
    def get_entity_edges(self, *args, **kwargs):
        return []

    def get_by_graph_id(self, *args, **kwargs):
        node = ZepMockObject(
            uuid_="node-1",
            name="MockNode1",
            labels=["Person"],
            summary="Mock node summary",
            attributes={"entity_type": "Person"}
        )
        return [node] if not kwargs.get("uuid_cursor") else []

class MockEdge:
    def get_by_graph_id(self, *args, **kwargs):
        edge = ZepMockObject(
            uuid_="edge-1",
            source_node_uuid="node-1",
            target_node_uuid="node-1",
            name="connected_to",
            fact="Mock fact",
            episodes=["mock_ep_1"]
        )
        return [edge] if not kwargs.get("uuid_cursor") else []

class MockEpisode:
    def get(self, *args, **kwargs):
        return ZepMockObject(
            content="Mock episode content", 
            processed=True, 
            uuid=kwargs.get("uuid_", "ep_1")
        )

class MockGraph:
    def __init__(self):
        self.node = MockNode()
        self.edge = MockEdge()
        self.episode = MockEpisode()
        
    def add(self, *args, **kwargs):
        pass
        
    def add_batch(self, *args, **kwargs):
        return [ZepMockObject(uuid="mock_ep_1")]
        
    def search(self, *args, **kwargs):
        node = ZepMockObject(
            uuid="mock-uuid", 
            name="MockNode", 
            label="Person", 
            attributes={"description": "Mocked node"}
        )
        return ZepMockObject(edges=[], nodes=[node])
        
    def create(self, *args, **kwargs):
        pass
        
    def set_ontology(self, *args, **kwargs):
        pass
        
    def delete(self, *args, **kwargs):
        pass

class MockZep:
    def __init__(self, *args, **kwargs):
        self.graph = MockGraph()

import zep_cloud.client
zep_cloud.client.Zep = MockZep

logger.info("Mock APIs successfully injected for OpenAI and Zep.")
