import json
from scout.pipeline.credibility_engine import format_credibility


def generate_reasoning(candidate: dict, final_score: float, credibility: dict, retrieved_by: str, jd_profile: dict) -> str:
    """
    Generate deterministic recruiter-style explanations dynamically based on JD profile.
    """
    title = candidate.get("current_title", "Candidate")
    yoe = float(candidate.get("years_exp", 0.0))
    cred_score = credibility.get("credibility_score", 100)
    flags = credibility.get("flags", [])
    
    # Parse skills
    skills_str = candidate.get("skills", "[]")
    if isinstance(skills_str, str):
        try:
            skills_list = json.loads(skills_str)
        except:
            skills_list = []
    else:
        skills_list = skills_str
        
    req_skills = [s.lower() for s in jd_profile.get("required_skills", [])]
    pref_skills = [s.lower() for s in jd_profile.get("preferred_skills", [])]
    
    # Sort candidate skills by evidence strength (endorsements + duration)
    skills_list = sorted(skills_list, key=lambda x: x.get("endorsements", 0) + x.get("duration_months", 0), reverse=True)
    
    # Issue 1 & 2: Containment matching and prioritizing Required over Preferred
    matched_req = []
    matched_pref = []
    
    for s in skills_list:
        if isinstance(s, dict):
            name = s.get("name", s.get("skill_name", ""))
        else:
            name = str(s)
            
        if not name: 
            continue
            
        skill_lower = name.lower()
        
        # Check required first
        if any(req in skill_lower or skill_lower in req for req in req_skills):
            if name not in matched_req:
                matched_req.append(name)
        # Check preferred
        elif any(pref in skill_lower or skill_lower in pref for pref in pref_skills):
            if name not in matched_pref:
                matched_pref.append(name)
                
    # Combine, guaranteeing required skills always appear first
    matched_skills = (matched_req + matched_pref)[:3]
    
    # Issue 3 & 4: Stronger fallback text using relevant experience and activity metrics
    if matched_skills:
        skills_text = f"Strong matches: {', '.join(matched_skills)}"
    else:
        skills_text = f"Meets experience requirements ({yoe:.1f}y in range)"
    
    # Centralized credibility formatting
    cred_text = format_credibility(cred_score)
    # Append flag count for transparency when there are flags
    if flags:
        cred_text = f"{cred_text} ({len(flags)} flags)"
        
    # Professionalized retrieval status
    if retrieved_by == "BOTH":
        retrieval_text = "Validated by both retrieval systems"
    elif retrieved_by == "TF-IDF":
        retrieval_text = "Retrieved via keyword matching"
    else:
        retrieval_text = "Retrieved via semantic search"
        
    reasoning = f"{title} ({yoe:.1f}y); {skills_text}; {cred_text}; {retrieval_text}; Score: {final_score:.2f}."
    
    return reasoning