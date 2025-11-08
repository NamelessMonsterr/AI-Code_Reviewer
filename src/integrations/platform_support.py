import requests
from typing import Dict, List

class PlatformSupport:
    """Support for GitLab, Bitbucket, Azure DevOps"""
    
    def __init__(self, platform: str, token: str):
        self.platform = platform
        self.token = token
        self.api_base = self._get_api_base()
    
    def _get_api_base(self) -> str:
        """Get API base URL for platform"""
        if self.platform == 'gitlab':
            return 'https://gitlab.com/api/v4'
        elif self.platform == 'bitbucket':
            return 'https://api.bitbucket.org/2.0'
        elif self.platform == 'azure':
            return 'https://dev.azure.com'
        return ''
    
    # GitLab Integration
    def gitlab_post_mr_comment(self, project_id: str, mr_id: int, comment: str):
        """Post comment on GitLab Merge Request"""
        url = f'{self.api_base}/projects/{project_id}/merge_requests/{mr_id}/notes'
        headers = {'PRIVATE-TOKEN': self.token}
        data = {'body': comment}
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    
    def gitlab_get_mr_changes(self, project_id: str, mr_id: int) -> List[Dict]:
        """Get changed files in GitLab MR"""
        url = f'{self.api_base}/projects/{project_id}/merge_requests/{mr_id}/changes'
        headers = {'PRIVATE-TOKEN': self.token}
        response = requests.get(url, headers=headers)
        return response.json().get('changes', [])
    
    # Bitbucket Integration
    def bitbucket_post_pr_comment(self, workspace: str, repo: str, pr_id: int, comment: str):
        """Post comment on Bitbucket Pull Request"""
        url = f'{self.api_base}/repositories/{workspace}/{repo}/pullrequests/{pr_id}/comments'
        headers = {'Authorization': f'Bearer {self.token}'}
        data = {'content': {'raw': comment}}
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    
    # Azure DevOps Integration
    def azure_post_pr_comment(self, org: str, project: str, repo: str, pr_id: int, comment: str):
        """Post comment on Azure DevOps Pull Request"""
        url = f'{self.api_base}/{org}/{project}/_apis/git/repositories/{repo}/pullRequests/{pr_id}/threads'
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        data = {
            'comments': [{'content': comment, 'commentType': 1}],
            'status': 1
        }
        response = requests.post(url, headers=headers, json=data, params={'api-version': '6.0'})
        return response.json()
