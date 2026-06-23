import json

# Provide a base map of common aliases so candidates aren't penalized for terminology
SKILL_ALIASES = {
    "pytorch": ["torch"],
    "transformers": ["bert", "gpt", "llama", "llm", "foundation model"],
    "rag": ["retrieval augmented generation", "retrieval-augmented", "vector search"],
    "llm": ["large language model", "gpt", "claude", "llama"],
    "machine learning": ["ml", "deep learning", "dl"],
    "artificial intelligence": ["ai"],
    "nlp": ["natural language processing", "text classification"],
    "computer vision": ["cv", "image classification", "object detection"],
    "kubernetes": ["k8s"],
    "aws": ["amazon web services"],
    "gcp": ["google cloud"],
    "react": ["reactjs", "react.js"],
    "node.js": ["nodejs", "node"]
}

def compute_credibility(candidate: dict, jd_profile: dict) -> dict:
    score = 100
    flags = []
    penalties = []
    
    def apply_penalty(reason: str, amount: int):
        nonlocal score
        score -= amount
        flags.append(reason)
        penalties.append(amount)

    yoe = float(candidate.get("years_exp", 0.0))
    title = str(candidate.get("current_title", "")).lower()
    summary = str(candidate.get("summary", "")).lower()
    career_text = str(candidate.get("career_text", "")).lower()
    narrative = summary + " " + career_text
    
    # Parse skills
    skills_str = candidate.get("skills", "[]")
    if isinstance(skills_str, str):
        try:
            skills_list = json.loads(skills_str)
        except:
            skills_list = []
    else:
        skills_list = skills_str
        
    skills_count = candidate.get("skills_count", len(skills_list))
    
    # --- CRITICAL FIX 1: JD-Responsive Target Skills ---
    # Merge required and preferred skills to form the target list
    req_skills = [s.lower() for s in jd_profile.get("required_skills", [])]
    pref_skills = [s.lower() for s in jd_profile.get("preferred_skills", [])]
    target_skills = list(set(req_skills + pref_skills))

    claimed_target_skills = []
    for s in skills_list:
        if isinstance(s, dict):
            s_name = s.get("name", s.get("skill_name", "")).lower()
        else:
            s_name = str(s).lower()
            
        for kw in target_skills:
            if kw in s_name:
                claimed_target_skills.append(kw)
    
    claimed_target_skills = list(set(claimed_target_skills))
    
    # --- CRITICAL FIX 2: Softened Narrative Check via Aliases ---
    unsupported_skills = []
    for kw in claimed_target_skills:
        search_terms = [kw]
        if kw in SKILL_ALIASES:
            search_terms.extend(SKILL_ALIASES[kw])
            
        # Check if ANY of the aliases or the root keyword exist in the narrative
        if not any(term in narrative for term in search_terms):
            unsupported_skills.append(kw)
            
    # --- CRITICAL FIX 3: Capped Penalty for Contradictions ---
    if len(unsupported_skills) > 0:
        # Cap at 25 points maximum, 5 points per unsupported skill
        penalty = min(25, len(unsupported_skills) * 5)
        apply_penalty(f"Skills-Narrative Contradiction: Claims {', '.join(unsupported_skills)} but missing from narrative.", penalty)

    # 2. Skill Inflation
    if yoe < 3.0 and skills_count > 20:
        apply_penalty(f"Skill Inflation: Claims {skills_count} skills with only {yoe:.1f} years of experience.", 15)
        
    # 3. Keyword Stuffing
    if skills_count > 30:
        apply_penalty(f"Keyword Stuffing: Exceeds reasonable skill count ({skills_count} > 30).", 20)
        
    # --- MEDIUM FIX 5: Nuanced Title Inflation ---
    extreme_titles = ["principal", "director", "head", "vp", "chief"]
    senior_titles = ["senior", "lead", "manager"]
    
    if any(st in title for st in extreme_titles) and yoe < 5.0:
        apply_penalty(f"Extreme Title Inflation: Claims '{title}' with only {yoe:.1f} years of experience.", 30)
    elif any(st in title for st in senior_titles) and yoe < 3.0:
        apply_penalty(f"Inflated Title: Claims '{title}' with only {yoe:.1f} years of experience.", 15)
        
    # --- MEDIUM FIX 4: Softened Career Instability Threshold ---
    num_jobs = int(candidate.get("num_jobs", 1))
    if yoe > 0 and (num_jobs / yoe) > 2.0 and yoe > 2.0:
        apply_penalty(f"Career Instability: {num_jobs} jobs in {yoe:.1f} years.", 15)
        
    # --- MEDIUM FIX 6: Generic JD-Responsive Evidence Checks ---
    for s in skills_list:
        if not isinstance(s, dict):
            continue
            
        s_name = s.get("name", s.get("skill_name", "")).lower()
        
        # Only penalize weak evidence if the skill is actually demanded by the JD
        if any(req in s_name for req in target_skills):
            # Fallback to generous defaults if parsing missed the metrics
            duration = s.get("duration_months", 12)
            endorsements = s.get("endorsements", 5)
            
            if duration < 3 and endorsements < 2:
                apply_penalty(f"Weak Evidence for '{s.get('name')}': Less than 3 months duration and < 2 endorsements.", 10)

    score = max(0, score)
    return {
        "credibility_score": score,
        "flags": flags,
        "penalties": penalties
    }


def format_credibility(score: float) -> str:
    """
    Centralized credibility formatter.
    Replaces multiple legacy formats across the codebase.
    """
    try:
        s = float(score)
    except Exception:
        return "Low"

    if s >= 90:
        return "High"
    elif s >= 75:
        return "Medium"
    else:
        return "Low"