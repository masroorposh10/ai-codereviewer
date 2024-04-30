import os
import json
from decouple import config
from github import Github, InputFileContent
from unidiff import PatchSet
import openai

# Get tokens and configs
GITHUB_TOKEN = config("GITHUB_TOKEN")
OPENAI_API_KEY = config("OPENAI_API_KEY")
OPENAI_API_MODEL = config("OPENAI_API_MODEL", default="gpt-4")

# Instantiate Github & OpenAI client
g = Github(GITHUB_TOKEN)
openai.api_key = OPENAI_API_KEY


def get_pr_details():
    # Get the event
    with open(os.environ["GITHUB_EVENT_PATH"], "r") as f:
        event = json.load(f)

    # Grab the PR from the event
    pr = g.get_repo(event["repository"]["full_name"]).get_pull(event["number"])

    return pr


def analyze_code(diff, pr_details):
    comments = []

    # Loop over modified files
    for file in diff:
        # Ignore deleted files
        if "/dev/null" in file.path:
            continue

        for hunk in file:
            prompt = create_prompt(file, hunk, pr_details)
            ai_response = get_ai_response(prompt)

            if ai_response:
                new_comments = create_comment(file, hunk, ai_response)
                if new_comments:
                    comments += new_comments

    return comments


def create_prompt(file, hunk, pr_details):
    return f"""
	Your task is to review pull requests. Instructions:

	- Pull request title: {pr_details.title}
	- Pull request description: {pr_details.body}
	
	Review the following code diff in the file "{file.path}":
	
	```diff
	{hunk}
	```
	"""


def get_ai_response(prompt):
    # Define the query config for the model
    query_config = {
        "model": OPENAI_API_MODEL,
        "temperature": 0.2,
        "max_tokens": 700,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
    }

    try:
        response = openai.Completion.create(
            engine="text-davinci-003", prompt=prompt, temperature=0.5, max_tokens=100
        )
        return response["choices"][0]["message"]["content"].strip().split("\n")
    except Exception as error:
        print(f"Error: {error}")
        return None


def create_comment(file, hunk, ai_responses):
    return [
        {"body": body, "path": file.path, "line": hunk.target_start}
        for body in ai_responses
    ]


def create_review_comment(pr, comments):
    pr.create_review(
        event="COMMENT",
        body="\n".join(
            [
                f"{comment['body']} ({comment['path']} Line:{comment['line']})"
                for comment in comments
            ]
        ),
    )


def main():
    pr = get_pr_details()
    diff = PatchSet(pr.get_files().getcontents())

    comments = analyze_code(diff, pr)
    if comments:
        create_review_comment(pr, comments)


if __name__ == "__main__":
    main()
