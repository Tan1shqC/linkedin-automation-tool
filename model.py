# model.py
# this is just a dummy ai generated function
def score_profile(profile_text):
    """
    Returns True if the profile matches based on the following:
    - From an IIT
    - From a well-known company
    - In a technical role
    """
    profile = profile_text.lower()
    iit_keywords = ['iit', 'indian institute of technology']
    company_keywords = [
        'google', 'microsoft', 'amazon', 'facebook', 'meta', 'apple', 'netflix',
        'adobe', 'uber', 'airbnb', 'linkedin', 'flipkart', 'ola', 'swiggy', 'zomato'
    ]
    technical_roles = [
        'engineer', 'developer', 'cto', 'technical', 'data scientist', 'ai', 'ml', 'product manager', 'software', 'architect'
    ]

    is_iit = any(kw in profile for kw in iit_keywords)
    is_well_known_company = any(kw in profile for kw in company_keywords)
    is_technical_role = any(kw in profile for kw in technical_roles)

    score = sum([is_iit, is_well_known_company, is_technical_role])
    return score >= 2
