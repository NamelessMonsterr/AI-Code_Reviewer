import * as core from '@actions/core'
import * as github from '@actions/github'
import {Octokit} from '@octokit/action'

const token = core.getInput('token')
  ? core.getInput('token')
  : process.env.GITHUB_TOKEN
const octokit = new Octokit({auth: `token ${token}`})
const context = github.context
const repo = context.repo

export const COMMENT_GREETING = `:robot: OpenAI`

export const COMMENT_TAG =
  '<!-- This is an auto-generated comment by OpenAI -->'

export const COMMENT_REPLY_TAG =
  '<!-- This is an auto-generated reply by OpenAI -->'

export const SUMMARIZE_TAG =
  '<!-- This is an auto-generated comment: summarize by openai -->'

export const DESCRIPTION_TAG =
  '<!-- This is an auto-generated comment: release notes by openai -->'
export const DESCRIPTION_TAG_END =
  '<!-- end of auto-generated comment: release notes by openai -->'

export class Commenter {
  /**
   * @param mode Can be "create", "replace", "append" and "prepend". Default is "replace".
   */
  async comment(message: string, tag: string, mode: string): Promise<void> {
    let target: number
    if (context.payload.pull_request) {
      target = context.payload.pull_request.number
    } else if (context.payload.issue) {
      target = context.payload.issue.number
    } else {
      core.warning(
        `Skipped: context.payload.pull_request and context.payload.issue are both null`
      )
      return
    }

    if (!tag) {
      tag = COMMENT_TAG
    }

    const body = `${COMMENT_GREETING}

${message}

${tag}`

    if (mode === 'create') {
      await this.create(body, target)
    } else if (mode === 'replace') {
      await this.replace(body, tag, target)
    } else if (mode === 'append') {
      await this.append(body, tag, target)
    } else if (mode === 'prepend') {
      await this.prepend(body, tag, target)
    } else {
      core.warning(`Unknown mode: ${mode}, use "replace" instead`)
      await this.replace(body, tag, target)
    }
  }

  get_description(description: string): string {
    const start = description.indexOf(DESCRIPTION_TAG)
    const end = description.indexOf(DESCRIPTION_TAG_END)
    if (start >= 0 && end >= 0) {
      return (
        description.slice(0, start) +
        description.slice(end + DESCRIPTION_TAG_END.length)
      )
    }
    return description
  }

  async update_description(pull_number: number, message: string): Promise<void> {
    try {
      const pr = await octokit.pulls.get({
        owner: repo.owner,
        repo: repo.repo,
        pull_number
      })
      let body = ''
      if (pr.data.body) {
        body = pr.data.body
      }
      const description = this.get_description(body)

      const tag_index = description.indexOf(DESCRIPTION_TAG)
      const tag_end_index = description.indexOf(DESCRIPTION_TAG_END)
      const comment = `${DESCRIPTION_TAG}\n${message}\n${DESCRIPTION_TAG_END}`
      if (tag_index === -1 || tag_end_index === -1) {
        const new_description = `${description}\n${comment}`
        await octokit.pulls.update({
          owner: repo.owner,
          repo: repo.repo,
          pull_number,
          body: new_description
        })
      } else {
        let new_description = description.substring(0, tag_index)
        new_description += comment
        new_description += description.substring(
          tag_end_index + DESCRIPTION_TAG_END.length
        )
        await octokit.pulls.update({
          owner: repo.owner,
          repo: repo.repo,
          pull_number,
          body: new_description
        })
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      core.warning(
        `Failed to get PR: ${errorMessage}, skipping adding release notes to description.`
      )
    }
  }

  async review_comment(
    pull_number: number,
    commit_id: string,
    path: string,
    line: number,
    message: string,
    tag: string = COMMENT_TAG
  ): Promise<void> {
    message = `${COMMENT_GREETING}

${message}

${tag}`
    try {
      let found = false
      const comments = await this.get_comments_at_line(pull_number, path, line)
      for (const comment of comments) {
        if (comment.body.includes(tag)) {
          await octokit.pulls.updateReviewComment({
            owner: repo.owner,
            repo: repo.repo,
            comment_id: comment.id,
            body: message
          })
          found = true
          break
        }
      }

      if (!found) {
        await octokit.pulls.createReviewComment({
          owner: repo.owner,
          repo: repo.repo,
          pull_number,
          body: message,
          commit_id,
          path,
          line
        })
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      core.warning(`Failed to post review comment: ${errorMessage}`)
    }
  }

  async review_comment_reply(
    pull_number: number,
    top_level_comment: any,
    message: string
  ): Promise<void> {
    const reply = `${COMMENT_GREETING}

${message}

${COMMENT_REPLY_TAG}
`
    try {
      await octokit.pulls.createReplyForReviewComment({
        owner: repo.owner,
        repo: repo.repo,
        pull_number,
        body: reply,
        comment_id: top_level_comment.id
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      core.warning(`Failed to reply to the top-level comment ${errorMessage}`)
      try {
        await octokit.pulls.createReplyForReviewComment({
          owner: repo.owner,
          repo: repo.repo,
          pull_number,
          body: `Could not post the reply to the top-level comment due to the following error: ${errorMessage}`,
          comment_id: top_level_comment.id
        })
      } catch (secondError) {
        const secondErrorMessage = secondError instanceof Error ? secondError.message : String(secondError)
        core.warning(`Failed to reply to the top-level comment ${secondErrorMessage}`)
      }
    }
    try {
      if (top_level_comment.body.includes(COMMENT_TAG)) {
        const newBody = top_level_comment.body.replace(
          COMMENT_TAG,
          COMMENT_REPLY_TAG
        )
        await octokit.pulls.updateReviewComment({
          owner: repo.owner,
          repo: repo.repo,
          comment_id: top_level_comment.id,
          body: newBody
        })
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      core.warning(`Failed to update the top-level comment ${errorMessage}`)
    }
  }

  async get_comments_at_line(pull_number: number, path: string, line: number): Promise<any[]> {
    const comments = await this.list_review_comments(pull_number)
    return comments.filter(
      (comment: any) =>
        comment.path === path && comment.line === line && comment.body !== ''
    )
  }

  async get_conversation_chains_at_line(
    pull_number: number,
    path: string,
    line: number,
    tag: string = ''
  ): Promise<string> {
    const existing_comments = await this.get_comments_at_line(
      pull_number,
      path,
      line
    )
    const top_level_comments = []
    for (const comment of existing_comments) {
      if (!comment.in_reply_to_id) {
        top_level_comments.push(comment)
      }
    }

    let all_chains = ''
    let chain_num = 0
    for (const top_level_comment of top_level_comments) {
      const chain = await this.compose_conversation_chain(
        existing_comments,
        top_level_comment
      )
      if (chain && chain.includes(tag)) {
        chain_num += 1
        all_chains += `Conversation Chain ${chain_num}:
${chain}
---
`
      }
    }
    return all_chains
  }

  async compose_conversation_chain(
    reviewComments: any[],
    topLevelComment: any
  ): Promise<string> {
    const conversationChain = reviewComments
      .filter((cmt: any) => cmt.in_reply_to_id === topLevelComment.id)
      .map((cmt: any) => `${cmt.user.login}: ${cmt.body}`)

    conversationChain.unshift(
      `${topLevelComment.user.login}: ${topLevelComment.body}`
    )

    return conversationChain.join('\n---\n')
  }

  async get_conversation_chain(pull_number: number, comment: any): Promise<{chain: string, topLevelComment: any}> {
    try {
      const review_comments = await this.list_review_comments(pull_number)
      const top_level_comment = await this.get_top_level_comment(
        review_comments,
        comment
      )
      const chain = await this.compose_conversation_chain(
        review_comments,
        top_level_comment
      )
      return {chain, topLevelComment: top_level_comment}
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      core.warning(`Failed to get conversation chain: ${errorMessage}`)
      return {
        chain: '',
        topLevelComment: null
      }
    }
  }

  async get_top_level_comment(reviewComments: any[], comment: any): Promise<any> {
    let top_level_comment = comment

    while (top_level_comment.in_reply_to_id) {
      const parent_comment = reviewComments.find(
        (cmt: any) => cmt.id === top_level_comment.in_reply_to_id
      )

      if (parent_comment) {
        top_level_comment = parent_comment
      } else {
        break
      }
    }

    return top_level_comment
  }

  async list_review_comments(target: number): Promise<any[]> {
    const all_comments: any[] = []
    let page = 1
    try {
      for (;;) {
        const {data: comments} = await octokit.pulls.listReviewComments({
          owner: repo.owner,
          repo: repo.repo,
          pull_number: target,
          page,
          per_page: 100
        })
        all_comments.push(...comments)
        page++
        if (!comments || comments.length < 100) {
          break
        }
      }

      return all_comments
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      core.warning(`Failed to list review comments: ${errorMessage}`)
      return all_comments
    }
  }

  async create(body: string, target: number): Promise<void> {
    try {
      await octokit.issues.createComment({
        owner: repo.owner,
        repo: repo.repo,
        issue_number: target,
        body
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      core.warning(`Failed to create comment: ${errorMessage}`)
    }
  }

  async replace(body: string, tag: string, target: number): Promise<void> {
    try {
      const cmt = await this.find_comment_with_tag(tag, target)
      if (cmt) {
        await octokit.issues.updateComment({
          owner: repo.owner,
          repo: repo.repo,
          comment_id: cmt.id,
          body
        })
      } else {
        await this.create(body, target)
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      core.warning(`Failed to replace comment: ${errorMessage}`)
    }
  }

  async append(body: string, tag: string, target: number): Promise<void> {
    try {
      const cmt = await this.find_comment_with_tag(tag, target)
      if (cmt) {
        await octokit.issues.updateComment({
          owner: repo.owner,
          repo: repo.repo,
          comment_id: cmt.id,
          body: `${cmt.body} ${body}`
        })
      } else {
        await this.create(body, target)
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      core.warning(`Failed to append comment: ${errorMessage}`)
    }
  }

  async prepend(body: string, tag: string, target: number): Promise<void> {
    try {
      const cmt = await this.find_comment_with_tag(tag, target)
      if (cmt) {
        await octokit.issues.updateComment({
          owner: repo.owner,
          repo: repo.repo,
          comment_id: cmt.id,
          body: `${body} ${cmt.body}`
        })
      } else {
        await this.create(body, target)
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      core.warning(`Failed to prepend comment: ${errorMessage}`)
    }
  }

  async find_comment_with_tag(tag: string, target: number): Promise<any | null> {
    try {
      const comments = await this.list_comments(target)
      for (const cmt of comments) {
        if (cmt.body && cmt.body.includes(tag)) {
          return cmt
        }
      }

      return null
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      core.warning(`Failed to find comment with tag: ${errorMessage}`)
      return null
    }
  }

  async list_comments(target: number): Promise<any[]> {
    const all_comments: any[] = []
    let page = 1
    try {
      for (;;) {
        const {data: comments} = await octokit.issues.listComments({
          owner: repo.owner,
          repo: repo.repo,
          issue_number: target,
          page,
          per_page: 100
        })
        all_comments.push(...comments)
        page++
        if (!comments || comments.length < 100) {
          break
        }
      }

      return all_comments
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      core.warning(`Failed to list comments: ${errorMessage}`)
      return all_comments
    }
  }
}
