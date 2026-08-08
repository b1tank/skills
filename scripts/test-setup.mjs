#!/usr/bin/env node

import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const home = await fs.mkdtemp(path.join(os.tmpdir(), 'b1tank-skills-test-'));
const vscode = path.join(home, 'vscode-user');
const environment = {
	...process.env,
	HOME: home,
	XDG_CONFIG_HOME: path.join(home, '.config'),
	VSCODE_INSIDERS_USER_DATA_DIR: vscode,
};

async function write(relative, contents) {
	const file = path.join(home, relative);
	await fs.mkdir(path.dirname(file), { recursive: true });
	await fs.writeFile(file, contents);
}

function bootstrap() {
	return execFileSync('node', [path.join(repo, 'scripts', 'setup.mjs'), 'bootstrap'], {
		cwd: repo,
		env: environment,
		encoding: 'utf8',
	});
}

try {
	const retired = 'retired-test-server';
	for (const name of ['analyze-trace', 'investigate-incident', 'open-dashboard', 'service-health']) {
		await write(`otelux/plugins/otelux/skills/${name}/SKILL.md`, `---\nname: ${name}\ndescription: Test external skill.\n---\n\nTest.\n`);
	}
	await write('deskpal/skills/deskpal-desktop-control/SKILL.md', '---\nname: deskpal-desktop-control\ndescription: Test Deskpal skill.\n---\n\nTest.\n');
	await write('.config/b1tank-skills/state.json', `${JSON.stringify({
		mcpServers: Object.fromEntries(['vscode', 'agent-host', 'copilot', 'claude', 'codex', 'opencode'].map(target => [target, [retired]])),
		credentials: ['RETIRED_TEST_TOKEN'],
	}, null, 2)}\n`);
	await write('.codex/config.toml', `model = "keep-me"\n\n[mcp_servers.github]\nurl = "https://old.invalid"\n\n[mcp_servers.github.http_headers]\nX-Test = "old"\n\n[mcp_servers.${retired}]\nurl = "https://retired.invalid"\n\n[unrelated]\nvalue = true\n`);
	await write('.config/opencode/opencode.jsonc', `{\n  // keep this comment\n  "theme": "keep-me",\n  "mcp": { "old-server": { "type": "remote", "url": "https://old.invalid" }, "${retired}": { "type": "remote", "url": "https://retired.invalid" } }\n}\n`);
	await write('vscode-user/mcp.json', `{"servers":{"old-server":{"type":"http","url":"https://old.invalid"},"${retired}":{"type":"http","url":"https://retired.invalid"}},"inputs":[{"id":"retired_test_token","type":"promptString"}]}\n`);
	await write('vscode-user/globalStorage/agent-host-config.json', `{"mcpServers":{"${retired}":{"type":"http","url":"https://retired.invalid"}}}\n`);
	await write('.copilot/mcp-config.json', `{"mcpServers":{"${retired}":{"type":"http","url":"https://retired.invalid"}}}\n`);
	await write('.claude.json', `{"mcpServers":{"${retired}":{"type":"http","url":"https://retired.invalid"}}}\n`);
	await write('.pi/agent/settings.json', `{"theme":"keep-me","enableSkillCommands":false,"skills":["custom-skill","-skills/retired-prompt"],"packages":["keep-package","../../deskpal"]}\n`);
	await write('deskpal/package.json', '{"name":"deskpal","pi":{"extensions":["./extensions/deskpal.ts"]}}\n');
	await write('otelux/plugins/otelux/package.json', '{"name":"@otelux/pi-plugin","pi":{"extensions":["./extensions/otelux.ts"]}}\n');
	await write('.agents/skills/diff-check/SKILL.md', 'old conflicting skill\n');
	await write('.agents/skills/legacy.work-skills-backup-old/SKILL.md', 'legacy backup\n');
	await write('.pi/agent/skills/diff-check/SKILL.md', 'old Pi-specific duplicate\n');
	await write('.pi/agent/skills/pi-skills/.git/config', '[remote "origin"]\n\turl = https://github.com/badlogic/pi-skills\n');
	await write('.pi/agent/skills/pi-skills/brave-search/SKILL.md', '---\nname: brave-search\ndescription: Upstream Pi skill.\n---\n');
	await fs.mkdir(path.join(home, '.pi', 'agent', 'extensions'), { recursive: true });
	await fs.symlink(path.join(repo, 'integrations', 'pi', 'mcp-bridge.ts'), path.join(home, '.pi', 'agent', 'extensions', 'work-skills-mcp.ts'));
	await fs.mkdir(path.join(home, '.pi', 'agent', 'prompts'), { recursive: true });
	await fs.symlink(path.join(repo, '.generated', 'pi-skill-prompts', 'brave-search.md'), path.join(home, '.pi', 'agent', 'prompts', 'brave-search.md'));
	for (const [source, destination] of [
		['AGENTS.md', '.copilot/copilot-instructions.md'],
		['CLAUDE.md', '.claude/CLAUDE.md'],
		['AGENTS.md', '.codex/AGENTS.md'],
		['AGENTS.md', '.pi/agent/AGENTS.md'],
	]) {
		const target = path.join(home, destination);
		await fs.mkdir(path.dirname(target), { recursive: true });
		if (destination === '.claude/CLAUDE.md') await fs.copyFile(path.join(repo, source), target);
		else await fs.symlink(path.join(repo, source), target);
	}

	bootstrap();
	const second = bootstrap();
	assert.match(second, /unchanged\s+.*config\.toml/);
	assert.match(second, /unchanged\s+.*opencode\.jsonc/);

	const codex = await fs.readFile(path.join(home, '.codex', 'config.toml'), 'utf8');
	assert.match(codex, /model = "keep-me"/);
	assert.match(codex, /\[unrelated\]/);
	assert.equal((codex.match(/\[mcp_servers\."github"\]/g) ?? []).length, 1);
	assert.doesNotMatch(codex, /old\.invalid|http_headers/);
	assert.doesNotMatch(codex, /retired-test-server|retired\.invalid/);

	const opencode = await fs.readFile(path.join(home, '.config', 'opencode', 'opencode.jsonc'), 'utf8');
	assert.match(opencode, /keep this comment/);
	assert.match(opencode, /"theme": "keep-me"/);
	assert.match(opencode, /"old-server"/);
	assert.match(opencode, /"github"/);
	assert.doesNotMatch(opencode, /retired-test-server|retired\.invalid/);

	const vscodeMcp = JSON.parse(await fs.readFile(path.join(vscode, 'mcp.json'), 'utf8'));
	assert.ok(vscodeMcp.servers['old-server']);
	assert.ok(vscodeMcp.servers.github);
	assert.ok(!vscodeMcp.servers[retired]);
	assert.ok(!vscodeMcp.inputs.some(input => input.id === 'retired_test_token'));

	for (const relative of [
		'vscode-user/globalStorage/agent-host-config.json',
		'.copilot/mcp-config.json',
		'.claude.json',
	]) assert.doesNotMatch(await fs.readFile(path.join(home, relative), 'utf8'), /retired-test-server|retired\.invalid/);

	for (const item of [
		'.agents/skills/diff-check/SKILL.md',
		'.agents/skills/create-prompt-skill/SKILL.md',
		'.agents/skills/deskpal-desktop-control/SKILL.md',
		'.agents/skills/publish-artifact/SKILL.md',
		'.agents/skills/publish-artifact/scripts/publish_artifact.py',
		'.agents/skills/analyze-trace/SKILL.md',
		'.agents/skills/sprint-in-yolo/SKILL.md',
		'.claude/commands/sprint-in-yolo.md',
		'.codex/agents/strategy-partner.toml',
		'.pi/agent/prompts/diff-check.md',
		'.pi/agent/prompts/create-prompt-skill.md',
		'.pi/agent/prompts/sprint-in-yolo.md',
		'.config/opencode/commands/create-prompt-skill.md',
		'.config/opencode/commands/sprint-in-yolo.md',
	]) await fs.access(path.join(home, item));
	const piSettings = JSON.parse(await fs.readFile(path.join(home, '.pi', 'agent', 'settings.json'), 'utf8'));
	assert.equal(piSettings.theme, 'keep-me');
	assert.ok(!('enableSkillCommands' in piSettings));
	assert.ok(piSettings.skills.includes('custom-skill'));
	assert.ok(piSettings.skills.includes('-skills/diff-check'));
	assert.ok(piSettings.skills.includes('-skills/create-prompt-skill'));
	assert.ok(piSettings.skills.includes('-skills/sprint-in-yolo'));
	assert.deepEqual(piSettings.packages, ['keep-package', '../../deskpal', '../../otelux/plugins/otelux']);
	assert.doesNotMatch(await fs.readFile(path.join(home, '.pi', 'agent', 'prompts', 'diff-check.md'), 'utf8'), /SKILL\.md/);
	const promptNames = (await fs.readdir(path.join(repo, '.github', 'prompts')))
		.filter(name => name.endsWith('.prompt.md'))
		.map(name => name.replace(/\.prompt\.md$/, ''));
	for (const name of promptNames) {
		const command = await fs.readFile(path.join(home, '.pi', 'agent', 'prompts', `${name}.md`), 'utf8');
		assert.match(command, /## Invocation input\n\n\$ARGUMENTS/, `${name} should forward slash-command arguments`);
		try {
			await fs.access(path.join(repo, '.github', 'skills', name, 'SKILL.md'));
			continue;
		} catch {
			// Prompts without a canonical skill receive a generated skill projection.
		}
		const skill = await fs.readFile(path.join(home, '.agents', 'skills', name, 'SKILL.md'), 'utf8');
		assert.match(skill, /Treat any additional text in the user’s explicit invocation as input/, `${name} skill should consume invocation input`);
		assert.doesNotMatch(skill, /\$ARGUMENTS/, `${name} skill should not depend on command-template substitution`);
	}
	const sprintCommand = await fs.readFile(path.join(home, '.pi', 'agent', 'prompts', 'sprint-in-yolo.md'), 'utf8');
	assert.match(sprintCommand, /argument-hint: "\[task list or sprint goal\]"/);
	assert.match(sprintCommand, /Accept a numbered list, bullets, or a single-sentence sprint goal/);
	const mcporter = JSON.parse(await fs.readFile(path.join(repo, '.generated', 'mcporter.json'), 'utf8'));
	assert.ok(!mcporter.mcpServers.deskpal);
	assert.ok(!mcporter.mcpServers.otelux);
	assert.ok(!mcporter.mcpServers.workiq);
	assert.equal(mcporter.mcpServers.github.command, 'npx');
	assert.deepEqual(mcporter.mcpServers.github.args.slice(0, 2), ['-y', 'mcp-remote@0.1.38']);
	assert.ok(mcporter.mcpServers.github.args.includes('Authorization: Bearer ${GITHUB_PAT}'));
	await assert.rejects(fs.access(path.join(home, '.pi', 'agent', 'extensions', 'work-skills-mcp.ts')));
	await assert.rejects(fs.access(path.join(home, '.pi', 'agent', 'skills', 'diff-check')));
	await fs.access(path.join(home, '.pi', 'agent', 'skills', 'pi-skills', 'brave-search', 'SKILL.md'));
	await assert.rejects(fs.access(path.join(home, '.agents', 'skills', 'legacy.work-skills-backup-old')));
	for (const item of [
		'.copilot/copilot-instructions.md',
		'.claude/CLAUDE.md',
		'.codex/AGENTS.md',
		'.pi/agent/AGENTS.md',
	]) await assert.rejects(fs.access(path.join(home, item)));
	const archived = await fs.readdir(path.join(home, '.config', 'b1tank-skills', 'backups'), { recursive: true });
	assert.ok(archived.some(item => item.endsWith('legacy.work-skills-backup-old')));
	assert.ok(archived.some(item => item.endsWith('diff-check')));
	assert.ok(archived.some(item => item.endsWith('CLAUDE.md')));

	console.log('Cross-harness bootstrap test passed.');
} finally {
	await fs.rm(home, { recursive: true, force: true });
}
