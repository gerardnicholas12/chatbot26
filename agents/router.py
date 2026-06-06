from agents.llm_agent import llm_agent
import sys

def classify_mode(query, history=None):
    """Classify the query into one of the modes"""
    lowered = query.lower()
    
    memory_terms = ["it", "that", "this", "previous", "earlier", "follow up", "who created"]
    web_terms = ["latest", "current", "today", "recent", "news", "stock", "market", "trend", "2026"]
    rag_terms = ["document", "uploaded", "policy", "handbook", "proposal", "company", "leave", "onboarding", "enterprise"]
    
    uses_memory = history and len(history) > 1 and any(term in lowered for term in memory_terms)
    
    if any(term in lowered for term in rag_terms):
        return "rag"
    elif any(term in lowered for term in web_terms):
        return "web"
    elif uses_memory:
        return "memory"
    else:
        return "general"


def route_query(user_query, context="", history=None):
    """Route the query and generate response"""
    try:
        mode = classify_mode(user_query, history)
        
        # Build context based on mode
        final_context = context
        if mode == "rag" and context:
            final_context = f"[RAG Context]\n{context}"
        elif mode == "web" and context:
            final_context = f"[Web Search Results]\n{context}"
        elif mode == "memory" and context:
            final_context = f"[Conversation History]\n{context}"
        
        # Generate response using LLM agent
        response = llm_agent.generate(user_query, final_context, history)
        return response, mode
    except Exception as e:
        error_msg = f"Router Error: {str(e)}"
        print(error_msg, file=sys.stderr)
        raise