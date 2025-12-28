#!/usr/bin/env python3
"""
Sentinel MCP Server

Provides agents as tools callable by Claude via Model Context Protocol.
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

from src.agents.orchestrator import OrchestratorAgent
from src.agents.sub_agent import SubAgent
from src.storage.postgres_client import PostgresClient
from src.storage.notion_client import NotionClient

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize app
app = FastAPI(
    title="Sentinel MCP Server",
    description="Multi-agent orchestration via Model Context Protocol",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize clients
db = PostgresClient()
notion = NotionClient()
orchestrator = None  # Lazy loaded


# ==================== Models ====================

class DiagnoseRequest(BaseModel):
    agent_id: str
    domain: str
    project: Optional[str] = None


class ExecuteRequest(BaseModel):
    agent_id: str
    action: Dict[str, Any]


class GetStateRequest(BaseModel):
    agent_id: str


# ==================== Endpoints ====================

@app.on_event("startup")
async def startup():
    """Initialize orchestrator and database"""
    global orchestrator
    db.connect()
    orchestrator = OrchestratorAgent()
    logger.info("Sentinel MCP Server started")


@app.on_event("shutdown")
async def shutdown():
    """Close database connection"""
    db.close()
    logger.info("Sentinel MCP Server stopped")


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.post("/diagnose")
async def diagnose(request: DiagnoseRequest):
    """
    Run diagnosis for a sub-agent.
    
    Returns the bottleneck identified by the agent.
    """
    try:
        logger.info(f"Diagnosing agent: {request.agent_id}")
        
        # Get or create agent
        agent = await _get_or_create_agent(
            request.agent_id,
            request.domain,
            request.project
        )
        
        # Run diagnosis
        bottleneck = await agent.diagnose()
        
        # Store result
        db.save_bottleneck(request.agent_id, bottleneck)
        
        logger.info(f"Diagnosis complete: {bottleneck}")
        
        return {
            "agent_id": request.agent_id,
            "bottleneck": bottleneck,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Diagnosis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute")
async def execute(request: ExecuteRequest):
    """
    Execute action for a sub-agent.
    
    Respects autonomy constraints and guardrails.
    """
    try:
        logger.info(f"Executing action for {request.agent_id}")
        
        agent = await _get_or_create_agent(request.agent_id)
        
        # Check autonomy
        if not agent.can_execute(request.action):
            logger.warning(f"Action blocked by guardrails: {request.action}")
            return {
                "agent_id": request.agent_id,
                "status": "pending_approval",
                "action": request.action
            }
        
        # Execute
        result = await agent.execute(request.action)
        
        # Log outcome
        db.log_action(request.agent_id, request.action, result)
        
        logger.info(f"Execution complete: {result}")
        
        return {
            "agent_id": request.agent_id,
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/orchestrate")
async def orchestrate():
    """
    Run orchestration cycle.
    
    Synthesizes all sub-agent reports and generates priorities.
    """
    try:
        logger.info("Starting orchestration cycle")
        
        # Collect all agent reports
        reports = db.get_all_agent_reports()
        
        # Synthesize via orchestrator
        plan = await orchestrator.synthesize(reports)
        
        # Update Notion dashboard
        # await notion.update_dashboard(plan)
        
        # Store in database
        db.save_orchestration_result(plan)
        
        logger.info(f"Orchestration complete: {plan}")
        
        return {
            "status": "success",
            "plan": plan,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Orchestration failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/state")
async def get_state(request: GetStateRequest):
    """Get current state of an agent"""
    try:
        state = db.get_agent_state(request.agent_id)
        
        return {
            "agent_id": request.agent_id,
            "state": state,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get state: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents")
async def list_agents():
    """List all registered agents"""
    try:
        agents = db.get_all_agents()
        return {"agents": agents}
    
    except Exception as e:
        logger.error(f"Failed to list agents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports")
async def get_reports():
    """Get latest agent reports including bottlenecks"""
    try:
        reports = db.get_all_agent_reports()
        return {"reports": reports}
    
    except Exception as e:
        logger.error(f"Failed to get reports: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Helpers ====================

async def _get_or_create_agent(
    agent_id: str,
    domain: Optional[str] = None,
    project: Optional[str] = None
) -> SubAgent:
    """Get agent from registry or create new instance"""
    from src.agents.github_agent import GitHubTriageAgent

    if domain == "github-triage":
        return GitHubTriageAgent(agent_id, domain)
        
    if domain == "ai-systems-research":
        from src.agents.research_agent import ResearchAnalystAgent
        return ResearchAnalystAgent(agent_id, domain)
        
    # In a real implementation, would load agent class dynamically
    # For now, returns a basic SubAgent
    agent = SubAgent(agent_id, domain or "default")
    return agent


# ==================== Main ====================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("SERVER_HOST", "127.0.0.1"),
        port=int(os.getenv("SERVER_PORT", "8000")),
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
