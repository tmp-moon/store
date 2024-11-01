import json
import os
import uuid
from typing import Any

import yaml
from fastapi import Request
from langchain import hub
from langchain.agents import AgentExecutor, create_json_chat_agent
from langchain_core.prompts.loading import load_prompt_from_config
from langchain_openai import ChatOpenAI

from .beamlit import functions
from .bl_generate_functions import parse_beamlit_yaml
from .prompt import prompt

try:
    BEAMLIT_CHAIN = json.loads(os.getenv("BEAMLIT_CHAIN", None))
except:
    BEAMLIT_CHAIN = None

# Create the agent
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_json_chat_agent(model, functions, prompt)
agent_executor = AgentExecutor(agent=agent, functions=functions)

async def chain_function(all_responses, config):
    from .beamlit import BeamlitChain

    chain_functions = [BeamlitChain()]
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent_two = create_json_chat_agent(llm, chain_functions, prompt)
    agent_two_executor = AgentExecutor(agent=agent_two, functions=chain_functions)
    for chunk in agent_two_executor.stream({"input": json.dumps(all_responses)}, config):
        if "output" in chunk:
            response = chunk["output"]
    return response

async def main(request: Request):
    sub = request.headers.get("X-Beamlit-Sub", str(uuid.uuid4()))
    config = {"configurable": {"thread_id": sub}}
    response = ""
    body = await request.json()
    if body.get("inputs"):
        body["input"] = body["inputs"]

    all_responses = [body]
    for chunk in agent_executor.stream(body, config):
        if "output" in chunk:
            response = chunk["output"]

    all_responses.append({"input": response})
    beamlit_config = parse_beamlit_yaml()
    chain = beamlit_config['chain']
    if chain and chain.get('enabled'):
        response = await chain_function(all_responses, config)
    return response
