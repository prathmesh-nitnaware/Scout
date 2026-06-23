import json

def normalize_text(value: str) -> str:
    return str(value or "").strip().lower()

AI_DOMAIN_TIERS = {
    1.0: [
        "ai engineer",
        "ml engineer",
        "machine learning engineer",
        "applied scientist",
        "nlp engineer",
        "llm engineer",
    ],
    0.8: [
        "data scientist",
        "computer vision engineer",
        "research engineer",
    ],
    0.5: [
        "software engineer",
        "backend engineer",
        "full stack engineer",
        "full-stack engineer",
        "fullstack engineer",
    ],
    0.1: [
        "customer support",
        "hr",
        "recruiter",
        "sales",
        "operations",
        "business analyst",
        "qa",
    ],
}

MEANINGFUL_AI_SKILL_PATTERNS = [
    "pytorch",
    "tensorflow",
    "transformers",
    "lora",
    "qlora",
    "faiss",
    "langchain",
    "rag",
    "llm",
    "fine-tuning",
    "huggingface",
    "hugging face",
    "vector db",
    "vector search",
]

GENERIC_SKILLS = {"python", "git", "linux", "sql"}


def experience_fit(candidate: dict, jd_profile: dict) -> float:
    exp_min = jd_profile.get("min_years", 5)
    exp_max = jd_profile.get("max_years", 9)
    yoe = float(candidate.get("years_exp", 0.0))
    
    base_score = 1.0
    
    if exp_min <= yoe <= exp_max:
        return 1.0
    elif yoe < exp_min:
        diff = exp_min - yoe
        base_score = max(0.05, 1.0 - (diff * 0.40))
        # Hard penalty for missing minimum experience
        base_score *= 0.50  
    else:  # yoe > exp_max
        diff = yoe - exp_max
        base_score = max(0.05, 1.0 - (diff * 0.15))
        # Penalty for being significantly overqualified
        if diff > 3:
            base_score *= 0.50
        else:
            base_score *= 0.80
            
    return round(base_score, 4)


def skills_fit(candidate: dict, jd_profile: dict) -> float:
    req_skills = set(s.lower() for s in jd_profile.get("required_skills", []))
    pref_skills = set(s.lower() for s in jd_profile.get("preferred_skills", []))
    
    cand_skills_raw = candidate.get("skills_list") or candidate.get("skills") or []
    if isinstance(cand_skills_raw, str):
        import json
        try:
            cand_skills_raw = json.loads(cand_skills_raw)
        except:
            cand_skills_raw = []
    cand_skill_names = set()
    
    if isinstance(cand_skills_raw, list):
        for s in cand_skills_raw:
            if isinstance(s, dict):
                name = s.get("name") or s.get("skill_name") or ""
                if name:
                    cand_skill_names.add(name.lower())
            elif isinstance(s, str):
                cand_skill_names.add(s.lower())
                
    score = 0.0
    max_possible = len(req_skills) * 1.0 + len(pref_skills) * 0.5
    if max_possible == 0: return 0.5
    
    relevant_matches = 0
    
    for rs in req_skills:
        if any(rs in cs or cs in rs for cs in cand_skill_names):
            score += 1.0
            relevant_matches += 1
            
    for ps in pref_skills:
        if any(ps in cs or cs in ps for cs in cand_skill_names):
            score += 0.5
            relevant_matches += 1
            
    base_score = min(1.0, score / max_possible)
    
    if relevant_matches >= 5:
        base_score = min(1.0, base_score * 1.1)
        
    return base_score


def title_career_fit(candidate: dict, jd_profile: dict) -> float:
    title = str(candidate.get("current_title", "")).lower()
    history = str(candidate.get("career_text", "")).lower()
    
    hard_reject = [
        "mechanical", "civil", "graphic designer", "architect",
        "hr", "sales", "marketing", "recruiter", "accountant"
    ]
    if any(word in title for word in hard_reject):
        return 0.0
    
    target_role = str(jd_profile.get("role_title", "")).lower()
    
    high_roles = [
        "ai", "ml", "machine learning", "nlp", "computer vision",
        "applied scientist", "data scientist", "ai engineer",
        "ml engineer", "machine learning engineer", "ai research engineer"
    ]
    
    mid_roles = [
        ("software engineer", 0.70),
        ("backend engineer", 0.65),
        ("data engineer", 0.55),
        ("data analyst", 0.50),
        ("frontend engineer", 0.40),
    ]
    
    low_roles = [
        "marketing", "operations", "hr", "human resources", "sales",
        "recruiter", "accountant", "project manager", "program manager",
        "content writer", "business analyst", "qa engineer",
        "test engineer", "frontend engineer"
    ]   
    
    base_role_score = 0.5
    
    target_tokens = set(target_role.split())
    title_tokens = set(title.split())
    overlap = len(target_tokens & title_tokens)
    
    if overlap >= 1:
        base_role_score = 1.0
    else:
        for role in high_roles:
            if role in title:
                base_role_score = 1.0
                break
        
        if base_role_score < 1.0:
            for role, score in mid_roles:
                if role in title:
                    base_role_score = score
                    break
            
    for role in low_roles:
        if role in title:
            return 0.1  # Severe penalty
            
    SENIORITY_ORDER = [
        ("principal", 1.00),
        ("staff", 0.98),
        ("lead", 0.95),
        ("senior", 0.92),
        ("junior", 0.40),
        ("intern", 0.30),
        ("engineer", 0.50)
    ]
    
    seniority_weight = 0.50  # Default dropped to match generic engineer
    for keyword, weight in SENIORITY_ORDER:
        if keyword in title:
            seniority_weight = weight
            break
            
    title_score = base_role_score * seniority_weight
    
    if target_role and target_role in history:
        title_score = min(1.0, title_score + 0.15)
    elif any(role in history for role in high_roles):
        title_score = min(1.0, title_score + 0.10)
        
    return title_score


def education_fit(candidate: dict, jd_profile: dict = None) -> float:
    degree = str(candidate.get("highest_degree", "")).lower()
    field = str(candidate.get("education_field", "")).lower()
    edu = f"{degree} {field}"
    
    top_tier = ["computer science", "machine learning", "data science", "artificial intelligence", "ai", "mathematics", "physics"]
    mid_tier = ["engineering", "information technology", "electronics"]
    
    has_advanced = any(d in degree for d in ["phd", "m.s", "m.tech", "m.sc", "master", "masters"])
    is_top = any(kw in edu for kw in top_tier)
    is_mid = any(kw in edu for kw in mid_tier)
    
    if is_top:
        return 1.0 if has_advanced else 0.9
    elif is_mid:
        return 0.7 if has_advanced else 0.6
    
    return 0.5


def location_logistics_fit(candidate: dict, jd_profile: dict = None) -> float:
    if not jd_profile:
        return 0.8

    jd_loc = str(jd_profile.get("location", "")).lower()
    jd_raw = str(jd_profile.get("raw_jd", "")).lower()
    cand_loc = str(candidate.get("location", "")).lower()
    
    if "remote" in jd_raw or "remote" in jd_loc or "remote" in cand_loc:
        return 1.0
        
    if cand_loc and cand_loc in jd_loc:
        return 1.0
        
    return 0.8


def calculate_structured_score(candidate: dict, jd_profile: dict) -> dict:
    scores = {
        "experience": experience_fit(candidate, jd_profile),
        "skills": skills_fit(candidate, jd_profile),
        "career": title_career_fit(candidate, jd_profile),
        "education": education_fit(candidate, jd_profile),
        "location": location_logistics_fit(candidate, jd_profile),
    }
    
    weights = {
        "experience": 0.20,
        "skills": 0.30,
        "career": 0.40,
        "education": 0.05,
        "location": 0.05
    }
    
    final_score = sum(scores[k] * weights[k] for k in scores) * 100

    breakdown = {k: round(v, 2) for k, v in scores.items()}

    return {
        "final_score": round(final_score, 2),
        "breakdown": breakdown
    }


def domain_relevance_score(candidate: dict) -> float:
    title = normalize_text(candidate.get("current_title", ""))
    for score, patterns in AI_DOMAIN_TIERS.items():
        for pattern in patterns:
            if pattern in title:
                return score
    return 0.1


def is_ai_focused_jd(jd_profile: dict) -> bool:
    role_title = normalize_text(jd_profile.get("role_title", ""))
    if any(keyword in role_title for keyword in [
        "ai engineer", "machine learning", "ml engineer", "ml", "nlp", "llm", "applied scientist", "data scientist", "computer vision"
    ]):
        return True

    skills = [normalize_text(s) for s in jd_profile.get("required_skills", []) + jd_profile.get("preferred_skills", [])]
    for skill in skills:
        if any(pattern in skill for pattern in MEANINGFUL_AI_SKILL_PATTERNS):
            return True
    return False


def count_meaningful_ai_skill_matches(candidate: dict) -> int:
    skills = candidate.get("skills_list") or candidate.get("skills") or []
    if isinstance(skills, str):
        try:
            skills = json.loads(skills)
        except Exception:
            skills = []

    skill_names = set()
    for s in skills:
        if isinstance(s, dict):
            name = s.get("name") or s.get("skill_name") or ""
        else:
            name = str(s)
        name = normalize_text(name)
        if name:
            skill_names.add(name)

    matched = set()
    for name in skill_names:
        for pattern in MEANINGFUL_AI_SKILL_PATTERNS:
            if pattern in name:
                matched.add(pattern)
    return len(matched)
