"""
MiroFish TN2026 Simulation Runner - Groq-powered
Bypasses camel/oasis - uses direct LLM for agent actions
"""
import sys
import os
import json
import time
import asyncio
import argparse
import random
from datetime import datetime, timedelta

_scripts_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_scripts_dir, '..'))
sys.path.insert(0, _backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(_backend_dir, '.env'))

import sqlite3
from openai import OpenAI

# ── Config ────────────────────────────────────────────────────
API_KEY = os.environ.get('LLM_API_KEY', '')
BASE_URL = os.environ.get('LLM_BASE_URL', 'https://api.groq.com/openai/v1')
MODEL = os.environ.get('LLM_MODEL_NAME', 'llama-3.3-70b-versatile')

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

TN_AGENTS = [
    {"name": "M.K. Stalin", "party": "DMK", "role": "Chief Minister", "type": "PoliticalLeader"},
    {"name": "Edappadi Palaniswami", "party": "AIADMK", "role": "Opposition Leader", "type": "PoliticalLeader"},
    {"name": "C. Joseph Vijay", "party": "TVK", "role": "TVK President", "type": "PoliticalLeader"},
    {"name": "K. Annamalai", "party": "BJP", "role": "BJP TN President", "type": "PoliticalLeader"},
    {"name": "Seeman", "party": "NTK", "role": "NTK Leader", "type": "PoliticalLeader"},
    {"name": "Udhayanidhi Stalin", "party": "DMK", "role": "Deputy CM", "type": "PoliticalLeader"},
    {"name": "Aadhav Arjuna", "party": "TVK", "role": "TVK General Secretary", "type": "Candidate"},
    {"name": "KA Sengkottaiyan", "party": "TVK", "role": "TVK Candidate Thirupparankundram", "type": "Candidate"},
    {"name": "Chennai Youth Voter", "party": "TVK-leaning", "role": "First-time voter", "type": "Voter"},
    {"name": "Rural Thevar Voter", "party": "AIADMK-leaning", "role": "Rural voter South TN", "type": "Voter"},
    {"name": "Vanniyar Community Leader", "party": "PMK-AIADMK", "role": "Caste leader North TN", "type": "CasteOrCommunity"},
    {"name": "Dalit Voter Chennai", "party": "DMK-VCK", "role": "Dalit community voter", "type": "Voter"},
    {"name": "Sun TV Journalist", "party": "DMK-aligned", "role": "Political journalist", "type": "MediaOutlet"},
    {"name": "Jaya TV Reporter", "party": "AIADMK-aligned", "role": "Political reporter", "type": "MediaOutlet"},
    {"name": "Women Welfare Beneficiary", "party": "DMK", "role": "Welfare scheme recipient", "type": "Voter"},
]

ACTION_TYPES = ["CREATE_POST", "REPOST", "LIKE_POST", "FOLLOW", "DO_NOTHING", "QUOTE_POST"]

def generate_action(agent, round_num, sim_requirement):
    """Generate a realistic agent action using LLM"""
    try:
        prompt = f"""You are simulating {agent['name']} ({agent['role']}, {agent['party']}) during the Tamil Nadu 2026 election campaign.

Context: {sim_requirement[:500]}

Round {round_num} of the campaign simulation. Generate ONE realistic social media action this person would take RIGHT NOW.

Respond ONLY with valid JSON:
{{
  "action_type": "{random.choice(['CREATE_POST', 'REPOST', 'LIKE_POST', 'QUOTE_POST'])}",
  "content": "The actual post/tweet content in character (max 280 chars)",
  "sentiment": "positive/negative/neutral",
  "target_party": "DMK/AIADMK/TVK/BJP/NTK",
  "platform": "twitter"
}}"""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.8
        )
        
        text = response.choices[0].message.content.strip()
        # Extract JSON
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"Action generation error: {e}")
    
    # Fallback
    return {
        "action_type": random.choice(ACTION_TYPES),
        "content": f"{agent['name']} campaigns for TN2026 election. #TamilNaduElections2026",
        "sentiment": "neutral",
        "target_party": agent['party'].split('-')[0],
        "platform": "twitter"
    }

def run_simulation(config_path, simulation_dir, no_wait=False, twitter_only=False, reddit_only=False):
    """Main simulation loop"""
    
    # Load config
    with open(config_path) as f:
        config = json.load(f)
    
    sim_id = config.get('simulation_id', 'unknown')
    total_rounds = config.get('time_config', {}).get('total_rounds', 24)
    sim_requirement = config.get('simulation_requirement', 'TN2026 election simulation')
    
    print(f"Starting TN2026 simulation: {sim_id}")
    print(f"Total rounds: {total_rounds}")
    print(f"Agents: {len(TN_AGENTS)}")
    
    # Setup action log files
    twitter_dir = os.path.join(simulation_dir, 'twitter')
    reddit_dir = os.path.join(simulation_dir, 'reddit')
    os.makedirs(twitter_dir, exist_ok=True)
    os.makedirs(reddit_dir, exist_ok=True)
    
    twitter_log = os.path.join(twitter_dir, 'actions.jsonl')
    reddit_log = os.path.join(reddit_dir, 'actions.jsonl')
    
    # State file
    state_file = os.path.join(simulation_dir, 'run_state.json')
    
    state = {
        "simulation_id": sim_id,
        "status": "running",
        "current_round": 0,
        "total_rounds": total_rounds,
        "twitter_actions": 0,
        "reddit_actions": 0,
        "started_at": datetime.now().isoformat()
    }
    
    with open(state_file, 'w') as f:
        json.dump(state, f)
    
    # Run rounds
    for round_num in range(1, total_rounds + 1):
        print(f"\n=== Round {round_num}/{total_rounds} ===")
        
        round_actions = []
        
        # Each agent acts each round
        active_agents = random.sample(TN_AGENTS, min(8, len(TN_AGENTS)))
        
        for agent in active_agents:
            action = generate_action(agent, round_num, sim_requirement)
            
            timestamp = datetime.now().isoformat()
            
            log_entry = {
                "round": round_num,
                "timestamp": timestamp,
                "agent_id": TN_AGENTS.index(agent),
                "agent_name": agent['name'],
                "agent_party": agent['party'],
                "agent_type": agent['type'],
                "action_type": action.get('action_type', 'DO_NOTHING'),
                "action_args": {"content": action.get('content', '')},
                "sentiment": action.get('sentiment', 'neutral'),
                "result": None,
                "success": True
            }
            
            round_actions.append(log_entry)
            print(f"  [{agent['name']}] {action.get('action_type')}: {action.get('content', '')[:80]}...")
            
            # Write to twitter log
            with open(twitter_log, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            # Mirror some to reddit
            if random.random() > 0.5:
                reddit_entry = dict(log_entry)
                reddit_entry['platform'] = 'reddit'
                with open(reddit_log, 'a') as f:
                    f.write(json.dumps(reddit_entry) + '\n')
        
        # Update state
        state['current_round'] = round_num
        state['twitter_actions'] = state.get('twitter_actions', 0) + len(round_actions)
        state['reddit_actions'] = state.get('reddit_actions', 0) + len([a for a in round_actions if random.random() > 0.5])
        state['progress_percent'] = (round_num / total_rounds) * 100
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        # Small delay between rounds
        time.sleep(0.5)
    
    # Complete
    state['status'] = 'completed'
    state['completed_at'] = datetime.now().isoformat()
    state['progress_percent'] = 100.0
    
    with open(state_file, 'w') as f:
        json.dump(state, f)
    
    print(f"\n✅ Simulation complete! {state['twitter_actions']} actions generated.")
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--no-wait', action='store_true')
    parser.add_argument('--twitter-only', action='store_true')
    parser.add_argument('--reddit-only', action='store_true')
    args = parser.parse_args()
    
    config_path = args.config
    simulation_dir = os.path.dirname(config_path)
    
    sys.exit(run_simulation(
        config_path=config_path,
        simulation_dir=simulation_dir,
        no_wait=args.no_wait,
        twitter_only=args.twitter_only,
        reddit_only=args.reddit_only
    ))
