from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from open_deep_research.graph import builder
from langgraph.checkpoint.memory import MemorySaver
import os
# from langgraph.prebuilt import Section
from dotenv import load_dotenv 
import uuid
import asyncio
import json
from langgraph.types import Command

# Load variables from .env
load_dotenv("D:\\Intern\\Terrabase\\open_deep_research\\.env")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
LANGSMITH_API_KEY=os.environ.get("LANGSMITH_API_KEY")
GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
PERPLEXITY_API_KEY=os.environ.get("PERPLEXITY_API_KEY")
LINKUP_API_KEY=os.environ.get("LINKUP_API_KEY")

router = APIRouter()

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

REPORT_STRUCTURE = """
Use this structure to create a report on the user-provided topic:
1. Introduction
2. Main Body Sections
3. Conclusion
"""
thread = {"configurable": {"thread_id": str(uuid.uuid4()),
                        "search_api": "tavily",
                        "planner_provider": "anthropic",
                        "planner_model": "claude-3-7-sonnet-latest",
                        "writer_provider": "anthropic",
                        "writer_model": "claude-3-5-sonnet-latest",
                        "max_search_depth": 2,
                        "report_structure": REPORT_STRUCTURE,
                        }}

@router.post("/stream_report")
async def stream_report(request: Request):
    body = await request.json()
    topic = body.get("topic", "default topic")
    useLocalFile = body.get("useLocalFile")
    async def event_stream():
        async for event in graph.astream({"topic": topic, "useLocalFile": useLocalFile}, thread, stream_mode="updates"):
            if "__interrupt__" in event:
                content = event['__interrupt__'][0].value
                print(content)
                yield json.dumps({"type": "interrupt", "content": content}) + "\n"
            await asyncio.sleep(0.01)

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@router.post("/human_feedback")
async def getHumanFeedback(request: Request):
    """
    Handles human feedback interaction. Depending on the 'resume' flag,
    either resumes a paused graph or continues live interaction.

    Expected request body:
        {
            "resume": true | String containing Feedback
        }

    Returns:
        StreamingResponse: SSE stream with either intermediate updates or final report.
    """
    body = await request.json()
    resume = body.get("resume")
    if resume == True:
        async def event_stream():
            async for event in graph.astream(Command(resume=resume), thread, stream_mode="updates"):
                print(event)
                print("\n")
                await asyncio.sleep(0.01)

            
            final_state = graph.get_state(thread)
            report = final_state.values.get('final_report')

            yield json.dumps({"type": "completed", "content": report}) + "\n"    
         
        return StreamingResponse(event_stream(), media_type="text/event-stream")
    else:
        async def event_stream():
            async for event in graph.astream(Command(resume=resume), thread, stream_mode="updates"):
                if "__interrupt__" in event:
                    content = event['__interrupt__'][0].value
                    print(content)
                    yield json.dumps({"type": "interrupt", "content": content}) + "\n"
                else:
                    print(event)
                await asyncio.sleep(0.01)
        return StreamingResponse(event_stream(), media_type="text/event-stream")