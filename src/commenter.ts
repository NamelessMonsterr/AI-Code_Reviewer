import * as core from '@actions/core';
import { Octokit } from '@octokit/rest';

interface CommentOptions {
  owner: string;
  repo: string;
  pullNumber: number;
  body: string;
  path?: string;
  position?: number;
}

export class Commenter {
  private octokit: Octokit;

  constructor(token: string) {
    this.octokit = new Octokit({
      auth: token,
    });
  }

  async postComment(options: CommentOptions): Promise<void> {
    try {
      if (options.path && options.position) {
        // Post inline comment
        await this.postInlineComment(options);
      } else {
        // Post general comment
        await this.postGeneralComment(options);
      }
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      core.error(`Failed to post comment: ${errorMessage}`);
      throw error;
    }
  }

  private async postInlineComment(options: CommentOptions): Promise<void> {
    const { data: pr } = await this.octokit.pulls.get({
      owner: options.owner,
      repo: options.repo,
      pull_number: options.pullNumber,
    });

    await this.octokit.pulls.createReviewComment({
      owner: options.owner,
      repo: options.repo,
      pull_number: options.pullNumber,
      body: options.body,
      commit_id: pr.head.sha,
      path: options.path!,
      position: options.position!,
    });

    core.info(`Posted inline comment on ${options.path}`);
  }

  private async postGeneralComment(options: CommentOptions): Promise<void> {
    await this.octokit.issues.createComment({
      owner: options.owner,
      repo: options.repo,
      issue_number: options.pullNumber,
      body: options.body,
    });

    core.info('Posted general comment');
  }

  async updateComment(
    owner: string,
    repo: string,
    commentId: number,
    body: string
  ): Promise<void> {
    await this.octokit.issues.updateComment({
      owner,
      repo,
      comment_id: commentId,
      body,
    });

    core.info(`Updated comment ${commentId}`);
  }
}
