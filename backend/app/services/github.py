import httpx
import logging

logger = logging.getLogger(__name__)
GITHUB_API = "https://api.github.com"

class GitHubClient:
    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_pr(self, repo: str, pr_number: int) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}",
                headers=self.headers
            )
            r.raise_for_status()
            data = r.json()
            # attach files list
            files = await self._get_pr_files(repo, pr_number)
            data["files"] = files
            return data

    async def _get_pr_files(self, repo: str, pr_number: int) -> list:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}/files",
                headers=self.headers
            )
            r.raise_for_status()
            return r.json()

    async def get_pr_diff(self, repo: str, pr_number: int) -> str:
        headers = {**self.headers, "Accept": "application/vnd.github.v3.diff"}
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}",
                headers=headers
            )
            r.raise_for_status()
            return r.text

    async def post_review_comment(self, repo: str, pr_number: int, body: str):
        # Use issue comments — no commit_id needed, always works
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{GITHUB_API}/repos/{repo}/issues/{pr_number}/comments",
                headers=self.headers,
                json={"body": body}
            )
            r.raise_for_status()
            logger.info(f"Posted summary comment to PR #{pr_number}")

    async def post_line_comment(
        self, repo: str, pr_number: int,
        path: str, line: int, body: str
    ):
        pr = await self.get_pr(repo, pr_number)
        commit_id = pr["head"]["sha"]

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}/comments",
                headers=self.headers,
                json={
                    "body": body,
                    "commit_id": commit_id,
                    "path": path,
                    "line": line,
                    "side": "RIGHT",
                }
            )
            if r.status_code not in (200, 201):
                logger.warning(f"Line comment failed {r.status_code}: {r.text}")
            else:
                r.raise_for_status()
