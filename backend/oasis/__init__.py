import asyncio
import sqlite3
import json
import random
from enum import Enum
from datetime import datetime

class ActionType(Enum):
    CREATE_POST = "create_post"
    LIKE_POST = "like_post"
    REPOST = "repost"
    FOLLOW = "follow"
    QUOTE_POST = "quote_post"
    DO_NOTHING = "do_nothing"
    DISLIKE_POST = "dislike_post"
    CREATE_COMMENT = "create_comment"
    LIKE_COMMENT = "like_comment"
    DISLIKE_COMMENT = "dislike_comment"
    SEARCH_POSTS = "search_posts"
    SEARCH_USER = "search_user"
    TREND = "trend"
    REFRESH = "refresh"
    MUTE = "mute"
    INTERVIEW = "interview"

class LLMAction:
    pass

class ManualAction:
    def __init__(self, action_type, action_args):
        self.action_type = action_type
        self.action_args = action_args

class DefaultPlatformType(Enum):
    TWITTER = "twitter"
    REDDIT = "reddit"

class MockAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.agent_name = f"MockAgent_{agent_id}"
        self.name = f"MockAgent_{agent_id}"

class MockAgentGraph:
    def __init__(self, agents):
        self.agents = agents

    def get_agent(self, agent_id):
        return MockAgent(agent_id)

    def get_agents(self):
        return [(a.agent_id, a) for a in self.agents]

async def generate_twitter_agent_graph(*args, **kwargs):
    return MockAgentGraph([MockAgent(i) for i in range(1, 20)])

async def generate_reddit_agent_graph(*args, **kwargs):
    return MockAgentGraph([MockAgent(i) for i in range(1, 20)])

class MockEnv:
    def __init__(self, agent_graph, platform, database_path):
        self.agent_graph = agent_graph
        self.platform = platform
        self.database_path = database_path
        self.round_num = 0
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.database_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS trace
                     (user_id INTEGER, action TEXT, info TEXT, created_at TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS post
                     (post_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, content TEXT, created_at TEXT)''')
        conn.commit()
        conn.close()

    async def reset(self):
        self.round_num = 0

    async def step(self, actions):
        conn = sqlite3.connect(self.database_path)
        c = conn.cursor()
        now = datetime.now().isoformat()
        
        for agent, action in actions.items():
            user_id = agent.agent_id
            
            # Use ManualAction or simulate LLMAction
            if isinstance(action, ManualAction):
                act_type = getattr(action, 'action_type', ActionType.DO_NOTHING)
                args = getattr(action, 'action_args', {})
            else:
                act_type = random.choice([ActionType.CREATE_POST, ActionType.LIKE_POST, ActionType.REPOST, ActionType.DO_NOTHING])
                args = {"content": f"Mocking an autonomous {act_type.value} from agent {user_id}"}
                if act_type == ActionType.CREATE_POST:
                    args["post_id"] = random.randint(100, 999)
                elif act_type == ActionType.LIKE_POST:
                    args["post_id"] = random.randint(10, 50)
            
            info_json = json.dumps(args)
            c.execute("INSERT INTO trace (user_id, action, info, created_at) VALUES (?, ?, ?, ?)",
                      (user_id, act_type.value, info_json, now))
                      
            if act_type == ActionType.CREATE_POST:
                c.execute("INSERT INTO post (user_id, content, created_at) VALUES (?, ?, ?)",
                          (user_id, args.get("content", ""), now))
                          
        conn.commit()
        conn.close()
        self.round_num += 1
        await asyncio.sleep(0.5)

    async def close(self):
        pass

def make(*args, **kwargs):
    return MockEnv(kwargs.get("agent_graph"), kwargs.get("platform"), kwargs.get("database_path"))
