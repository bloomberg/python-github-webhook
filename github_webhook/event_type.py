from enum import Enum


class EventType(Enum):
    """
    Event enum type
    """
    CommitComment = 'commit_comment'
    Create = 'create'
    Delete = 'delete'
    Deployment = 'deployment'
    DeploymentStatus = 'deployment_status'
    Fork = 'fork'
    Gollum = 'gollum'
    IssueComment = 'issue_comment'
    Issues = 'issues'
    Member = 'member'
    Membership = 'membership'
    PageBuild = 'page_build'
    Ping = 'ping'
    Public = 'public'
    PullRequest = 'pull_request'
    PullRequestReview = 'pull_request_review'
    PullRequestReviewComment = 'pull_request_review_comment'
    Push = 'push'
    Release = 'release'
    Repository = 'repository'
    Status = 'status'
    TeamAdd = 'team_add'
    Watch = 'watch'
