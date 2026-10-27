#!/usr/bin/env tsx

/* eslint-disable security/detect-non-literal-fs-filename */

import { strict as assert } from 'node:assert';
import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { createTestResults, printTestSummary, testFunction, TestResult } from '../helpers/test-utils.js';

const results = createTestResults();
const repoRoot = process.cwd();

function read(path: string): string {
  return readFileSync(join(repoRoot, path), 'utf8');
}

function parseSkillFrontmatter(content: string): Record<string, string> {
  assert.ok(content.startsWith('---\n'), 'skill must start with frontmatter');
  const end = content.indexOf('\n---\n', 4);
  assert.ok(end > 0, 'skill frontmatter must be closed');
  const frontmatter = content.slice(4, end).trim();
  const entries: Record<string, string> = {};

  for (const line of frontmatter.split('\n')) {
    const match = line.match(/^([a-z_]+):\s*(.*)$/);
    assert.ok(match, `invalid frontmatter line: ${line}`);
    entries[match[1]] = match[2].replace(/^"|"$/g, '');
  }

  return entries;
}

export async function runTests(): Promise<TestResult> {
  console.log('Testing Deep Research repo assets\n');

  await testFunction('all repo skills have valid frontmatter', () => {
    const skillsDir = join(repoRoot, '.agents/skills');
    const skillNames = readdirSync(skillsDir).sort();
    assert.deepEqual(skillNames, [
      'delegated-research',
      'research',
      'research-add-fields',
      'research-add-items',
      'research-deep',
      'research-report',
    ]);

    for (const skillName of skillNames) {
      const skillPath = `.agents/skills/${skillName}/SKILL.md`;
      assert.ok(existsSync(join(repoRoot, skillPath)), `missing ${skillPath}`);
      const frontmatter = parseSkillFrontmatter(read(skillPath));
      assert.equal(frontmatter.name, skillName);
      assert.ok(frontmatter.description.includes('Use when'), `${skillName} description needs trigger guidance`);
      assert.ok(frontmatter.description.length <= 1024, `${skillName} description is too long`);
    }
  }, results);

  await testFunction('Codex TOML assets parse and reference the SearXNG MCP tools', () => {
    execFileSync('python', [
      '-c',
      [
        'import pathlib, tomllib',
        'for path in [".codex/config.toml", ".codex/agents/searxng-researcher.toml"]:',
        '    tomllib.loads(pathlib.Path(path).read_text())',
      ].join('\n'),
    ], { cwd: repoRoot });

    const config = read('.codex/config.toml');
    for (const toolName of ['searxng_web_search', 'searxng_search_suggestions', 'searxng_instance_info', 'web_url_read']) {
      assert.ok(config.includes(toolName), `missing ${toolName} from Codex config`);
    }

    const agent = read('.codex/agents/searxng-researcher.toml');
    assert.ok(agent.includes('web_search = "disabled"'));
    assert.ok(agent.includes('searxng_web_search'));
    assert.ok(agent.includes('.codex/agents/web-search-modules/'));
  }, results);

  await testFunction('research validator accepts fixture JSON', () => {
    const output = execFileSync('python', [
      'scripts/research/validate_json.py',
      '-f',
      '__tests__/fixtures/research/fields.yaml',
      '-j',
      '__tests__/fixtures/research/result.json',
      '-q',
    ], { cwd: repoRoot, encoding: 'utf8' });

    assert.ok(output.includes('Validation passed: 1/1'), output);
  }, results);

  await testFunction('research validator rejects vacuous and invalid coverage', () => {
    execFileSync('python', ['__tests__/research/test_validate_json.py'], { cwd: repoRoot });
  }, results);

  printTestSummary(results, 'Deep Research repo assets');
  return results;
}

runTests().catch((error) => {
  console.error('Fatal error running research asset tests:', error);
  process.exit(1);
});
