import re
import os

filepath = "backend/api/routes/recruiter_dashboard_routes.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Make all route handlers async
content = re.sub(r'(@router\.[a-z]+\("[^"]+"(?:, [^)]+)?\)\n)def ', r'\1async def ', content)

# Await the DB functions returned directly:
store_functions = [
    "get_evaluation_dashboard",
    "list_candidates",
    "get_interview_report",
    "get_skill_analytics",
    "compare_candidates",
    "get_db_metrics_aggregates",
    "get_historical_trends",
    "get_experiments",
    "log_experiment",
    "compare_experiments",
    "list_job_posts",
    "create_job_post",
    "get_job_post",
    "update_job_post",
    "delete_job_post",
    "invite_candidate",
    "generate_interview_link",
    "update_candidate_status",
]

for func in store_functions:
    # return func( -> return await func(
    content = re.sub(rf'return {func}\(', rf'return await {func}(', content)
    # var = func( -> var = await func(
    content = re.sub(rf'(\w+)\s*=\s*{func}\(', rf'\1 = await {func}(', content)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated recruiter_dashboard_routes.py")
