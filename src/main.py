import os
import json
from decouple import config
from github import Github, InputFileContent
from unidiff import PatchSet
import openai

# Get tokens and configs
GITHUB_TOKEN = config("GITHUB_TOKEN")
OPENAI_API_KEY = config("OPENAI_API_KEY")
OPENAI_API_ENDPOINT = config(
    "OPENAI_API_ENDPOINT"
)  # Endpoint of your Azure OpenAI service
OPENAI_API_MODEL = config("OPENAI_API_MODEL", default="gpt-4-v0613")

# Instantiate Github client
g = Github(GITHUB_TOKEN)

# Configure the OpenAI API key and endpoint
openai.api_key = OPENAI_API_KEY
openai.api_base = OPENAI_API_ENDPOINT  # Set the API endpoint to Azure OpenAI endpoint


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
    try:
        response = openai.Completion.create(
            model=OPENAI_API_MODEL,  # Use custom model ID
            prompt=prompt,
            temperature=0.5,
            max_tokens=100,
        )
        return (
            response.choices[0].text.strip().split("\n")
        )  # Adjusted for expected response structure
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
