"""
Integrations Module
~~~~~~~~~~~~~~~~~~~

Third-party integrations (GitHub, GitLab, Slack, etc.).
"""

try:
    from src.integrations.github_integration import GitHubIntegration
    from src.integrations.gitlab_integration import GitLabIntegration
    from src.integrations.slack_integration import SlackIntegration
    from src.integrations.ide_integration import IDEIntegration
except ImportError:
    GitHubIntegration = None
    GitLabIntegration = None
    SlackIntegration = None
    IDEIntegration = None

__all__ = [
    "GitHubIntegration",
    "GitLabIntegration",
    "SlackIntegration",
    "IDEIntegration",
]
