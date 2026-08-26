#!/usr/bin/env node

import { execFileSync } from 'node:child_process';
import { constants } from 'node:fs';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';
import { applyEdits, modify, parse as parseJsonc } from 'jsonc-parser';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const home = os.homedir();
const generated = path.join(repo, '.generated');
const skillSource = path.join(repo, '.github', 'skills');
const promptSource = path.join(repo, '.github', 'prompts');
const agentSource = path.join(repo, '.github', 'agents');
const instructionSource = path.join(repo, '.github', 'instructions');
const externalSkillSourcesPath = path.join(repo, 'skills', 'sources.json');
const manifestPath = path.join(repo, 'mcp', 'servers.json');
const piSkillsRepository = 'https://github.com/badlogic/pi-skills';
const managedStatePath = path.join(process.env.XDG_CONFIG_HOME || path.join(home, '.config'), 'b1tank-skills', 'state.json');
const stamp = new Date().toISOString().replaceAll(':', '').replaceAll('.', '');
const backupRoot = path.join(path.dirname(managedStatePath), 'backups', stamp);
const currentPlatform = process.env.B1TANK_SKILLS_PLATFORM || process.platform;

const aliases = {
	all: ['vscode', 'agent-host', 'copilot', 'claude', 'codex', 'pi', 'opencode'],
	'vscode-claude': ['vscode', 'agent-host', 'claude'],
	'vscode-codex': ['vscode', 'agent-host', 'codex'],
};

const args = process.argv.slice(2);
const command = args[0] && !args[0].startsWith('-') ? args.shift() : 'status';
const dryRun = takeFlag('--dry-run');
const connect = takeFlag('--connect');
const requestedTargets = takeOption('--targets')?.split(',').filter(Boolean) ?? ['all'];
const targets = new Set(requestedTargets.flatMap(target => aliases[target] ?? [target]));

function takeFlag(name) {
	const index = args.indexOf(name);
	if (index === -1) return false;
	args.splice(index, 1);
	return true;
}

function takeOption(name) {
	const index = args.indexOf(name);
	if (index === -1) return undefined;
	const value = args[index + 1];
	if (!value || value.startsWith('-')) throw new Error(`${name} requires a value`);
	args.splice(index, 2);
	return value;
}

function log(action, detail) {
	console.log(`${dryRun ? '[dry-run] ' : ''}${action.padEnd(12)} ${detail}`);
}

function expand(value) {
	return value.replaceAll('{repo}', repo).replaceAll('{home}', home);
}

function supportsPlatform(item) {
	return !item.platforms?.length || item.platforms.includes(currentPlatform);
}

async function exists(file) {
	try {
		await fs.access(file, constants.F_OK);
		return true;
	} catch {
		return false;
	}
}

async function lexists(file) {
	try {
		await fs.lstat(file);
		return true;
	} catch {
		return false;
	}
}

async function readJson(file, fallback = {}) {
	if (!(await exists(file))) return structuredClone(fallback);
	return JSON.parse(await fs.readFile(file, 'utf8'));
}

async function writeJson(file, value) {
	const text = `${JSON.stringify(value, null, 2)}\n`;
	if ((await exists(file)) && (await fs.readFile(file, 'utf8')) === text) {
		log('unchanged', file);
		return;
	}
	log('write', file);
	if (dryRun) return;
	await fs.mkdir(path.dirname(file), { recursive: true });
	await fs.writeFile(file, text);
}

async function backup(file) {
	const target = path.join(backupRoot, path.relative(path.parse(file).root, file));
	log('archive', `${file} -> ${target}`);
	if (!dryRun) {
		await fs.mkdir(path.dirname(target), { recursive: true });
		await fs.rename(file, target);
	}
}

async function sameLink(source, destination) {
	try {
		if (!(await fs.lstat(destination)).isSymbolicLink()) return false;
		return path.resolve(path.dirname(destination), await fs.readlink(destination)) === source;
	} catch {
		return false;
	}
}

async function installLink(source, destination) {
	if (await sameLink(source, destination)) {
		log('linked', destination);
		return;
	}
	if (await lexists(destination)) await backup(destination);
	log('link', `${destination} -> ${source}`);
	if (dryRun) return;
	await fs.mkdir(path.dirname(destination), { recursive: true });
	try {
		await fs.symlink(source, destination, (await fs.stat(source)).isDirectory() ? 'junction' : 'file');
	} catch (error) {
		if (error?.code !== 'EPERM') throw error;
		log('copy', `${destination} (symlink unavailable)`);
		await fs.cp(source, destination, { recursive: true });
	}
}

async function removeManagedLink(source, destination) {
	if (!(await sameLink(source, destination))) return;
	log('remove', destination);
	if (!dryRun) await fs.unlink(destination);
}

async function removeManagedProjection(source, destination) {
	if (await sameLink(source, destination)) return removeManagedLink(source, destination);
	if (!(await lexists(destination))) return;
	try {
		const [sourceContents, destinationContents] = await Promise.all([fs.readFile(source), fs.readFile(destination)]);
		if (sourceContents.equals(destinationContents)) await backup(destination);
	} catch {
		// Leave unrelated or non-file destinations untouched.
	}
}

function projectionRoots() {
	return [
		path.join(home, '.agents', 'skills'),
		path.join(home, '.claude', 'skills'),
		path.join(home, '.codex', 'skills'),
		path.join(home, '.pi', 'agent', 'skills'),
		path.join(home, '.claude', 'commands'),
		path.join(home, '.claude', 'agents'),
		path.join(home, '.copilot', 'agents'),
		path.join(vscodeUserDirectory(), 'prompts'),
		path.join(home, '.pi', 'agent', 'prompts'),
		path.join(opencodeDirectory(), 'commands'),
		path.join(opencodeDirectory(), 'agents'),
	];
}

async function cleanProjectionRoots() {
	for (const root of projectionRoots()) {
		if (!(await exists(root))) continue;
		for (const entry of await fs.readdir(root, { withFileTypes: true })) {
			const item = path.join(root, entry.name);
			if (entry.name.includes('.work-skills-backup-')) {
				await backup(item);
				continue;
			}
			if (entry.isSymbolicLink() && !(await exists(item))) await backup(item);
		}
	}
}

async function entries(directory, suffix) {
	if (!(await exists(directory))) return [];
	return (await fs.readdir(directory, { withFileTypes: true }))
		.filter(entry => suffix ? entry.isFile() && entry.name.endsWith(suffix) : entry.isDirectory())
		.map(entry => entry.name)
		.sort();
}

async function skillEntries(directory) {
	const valid = [];
	for (const name of await entries(directory)) {
		if (await exists(path.join(directory, name, 'SKILL.md'))) valid.push(name);
	}
	return valid;
}

function splitFrontmatter(text) {
	const normalized = text.replaceAll('\r\n', '\n').replaceAll('\r', '\n');
	if (!normalized.startsWith('---\n')) return { data: {}, body: normalized.trim() };
	const end = normalized.indexOf('\n---\n', 4);
	if (end === -1) return { data: {}, body: normalized.trim() };
	const data = {};
	for (const line of normalized.slice(4, end).split('\n')) {
		const match = /^([a-zA-Z0-9_-]+):\s*(.*)$/.exec(line);
		if (match) data[match[1]] = match[2].replace(/^['"]|['"]$/g, '');
	}
	return { data, body: normalized.slice(end + 5).trim() };
}

async function generateFiles() {
	log('generate', generated);
	if (!dryRun) {
		await fs.rm(generated, { recursive: true, force: true });
		await fs.mkdir(generated, { recursive: true });
	}

	for (const filename of await entries(promptSource, '.prompt.md')) {
		const parsed = splitFrontmatter(await fs.readFile(path.join(promptSource, filename), 'utf8'));
		const fallback = filename.replace(/\.prompt\.md$/, '');
		const name = portableId(parsed.data.name || fallback, fallback);
		const description = parsed.data.description || `Run the ${name} workflow when explicitly requested.`;
		const argumentHint = parsed.data['argument-hint'];
		const commandInput = `## Invocation input\n\n$ARGUMENTS\n\nTreat the text above as input to this workflow. If it is empty, follow the workflow's stated fallback behavior.\n\n`;
		const skillInput = '## Invocation input\n\nTreat any additional text in the user’s explicit invocation as input to this workflow. If none was supplied, follow the workflow’s stated fallback behavior.\n\n';
		await writeGenerated(path.join('commands', `${name}.md`), `---\ndescription: ${yamlScalar(description)}\n${argumentHint ? `argument-hint: ${yamlScalar(argumentHint)}\n` : ''}---\n\n${commandInput}${parsed.body}\n`);
		await writeGenerated(path.join('prompt-skills', name, 'SKILL.md'), `---\nname: ${name}\ndescription: ${yamlScalar(`${description} Use only when the user explicitly invokes or requests this workflow.`)}\n---\n\n${skillInput}${parsed.body}\n`);
	}

	for (const filename of await entries(agentSource, '.agent.md')) {
		const parsed = splitFrontmatter(await fs.readFile(path.join(agentSource, filename), 'utf8'));
		const fallback = filename.replace(/\.agent\.md$/, '');
		const name = portableId(parsed.data.name || fallback, fallback);
		const description = parsed.data.description || `${name} specialist agent.`;
		await writeGenerated(path.join('claude-agents', `${name}.md`), `---\nname: ${name}\ndescription: ${yamlScalar(description)}\n---\n\n${parsed.body}\n`);
		await writeGenerated(path.join('opencode-agents', `${name}.md`), `---\ndescription: ${yamlScalar(description)}\nmode: subagent\n---\n\n${parsed.body}\n`);
		await writeGenerated(path.join('codex-agents', `${name}.toml`), `name = ${JSON.stringify(name)}\ndescription = ${JSON.stringify(description)}\ndeveloper_instructions = ${JSON.stringify(parsed.body)}\n`);
	}

	const manifest = await loadManifest();
	const mcporter = {
		mcpServers: Object.fromEntries(selectedServers(manifest, 'pi').map(([name, server]) => [name, renderMcporterServer(server)])),
		imports: [],
	};
	await writeGenerated('mcporter.json', `${JSON.stringify(mcporter, null, 2)}\n`);
}

function yamlScalar(value) {
	return JSON.stringify(value);
}

function portableId(value, fallback) {
	const id = value.toLowerCase().trim()
		.replace(/[^a-z0-9]+/g, '-')
		.replace(/^-+|-+$/g, '');
	return id || fallback;
}

async function writeGenerated(relative, content) {
	const file = path.join(generated, relative);
	log('generate', file);
	if (dryRun) return;
	await fs.mkdir(path.dirname(file), { recursive: true });
	await fs.writeFile(file, content);
}

async function installSkills() {
	const shared = path.join(home, '.agents', 'skills');
	const sources = await skillSources();
	const sourceNames = new Set(sources.map(([name]) => name));
	for (const [name, source] of sources) await installLink(source, path.join(shared, name));
	for (const name of await skillEntries(path.join(generated, 'prompt-skills'))) {
		if (sourceNames.has(name)) continue;
		await installLink(path.join(generated, 'prompt-skills', name), path.join(shared, name));
	}

	if (targets.has('claude')) {
		const claude = path.join(home, '.claude', 'skills');
		for (const [name, source] of sources) await installLink(source, path.join(claude, name));
		for (const container of ['obstudio', 'pi-skills']) {
			const item = path.join(claude, container);
			if (await lexists(item)) await backup(item);
		}
	}

	if (targets.has('codex')) await consolidateCodexDuplicates();
	if (targets.has('pi')) await consolidatePiDuplicates();
}

async function installPiUpstreamSkills() {
	const destination = path.join(home, '.pi', 'agent', 'skills', 'pi-skills');
	const validCheckout = await exists(path.join(destination, '.git'))
		&& await exists(path.join(destination, 'brave-search', 'SKILL.md'));
	if (!validCheckout) {
		if (await lexists(destination)) await backup(destination);
		log('clone', `${piSkillsRepository} -> ${destination}`);
		if (dryRun) return;
		await fs.mkdir(path.dirname(destination), { recursive: true });
		execFileSync('git', ['clone', '--depth', '1', piSkillsRepository, destination], { stdio: 'inherit' });
	} else {
		log('upstream', destination);
	}

	for (const name of ['brave-search', 'browser-tools', 'youtube-transcript']) {
		const directory = path.join(destination, name);
		if (!(await exists(path.join(directory, 'package.json'))) || await exists(path.join(directory, 'node_modules'))) continue;
		log('npm install', directory);
		if (!dryRun) execFileSync('npm', ['install', '--no-audit', '--no-fund'], { cwd: directory, stdio: 'inherit' });
	}
}

async function installPiProductPackages() {
	const file = path.join(home, '.pi', 'agent', 'settings.json');
	const config = await readJson(file);
	let packages = Array.isArray(config.packages) ? [...config.packages] : [];
	const packageRoot = path.dirname(file);
	const packageMatches = (item, directory) => {
		const source = typeof item === 'string' ? item : item?.source;
		return typeof source === 'string' && !source.includes(':') && path.resolve(packageRoot, source) === directory;
	};
	for (const { entry, directory, platforms } of [
		{ entry: '../../deskpal', directory: path.join(home, 'deskpal'), platforms: ['linux'] },
		{ entry: '../../otelux/plugins/otelux', directory: path.join(home, 'otelux', 'plugins', 'otelux') },
	]) {
		if (!supportsPlatform({ platforms })) {
			packages = packages.filter(item => !packageMatches(item, directory));
			continue;
		}
		if (!(await exists(path.join(directory, 'package.json')))) {
			console.warn(`WARN Pi package source does not exist: ${directory}`);
			continue;
		}
		const installed = packages.some(item => packageMatches(item, directory));
		if (!installed) packages.push(entry);
	}
	config.packages = packages;
	await writeJson(file, config);
}

async function skillSources() {
	const sources = new Map((await skillEntries(skillSource)).map(name => [name, path.join(skillSource, name)]));
	const external = await readJson(externalSkillSourcesPath, { skills: [] });
	for (const skill of external.skills || []) {
		if (!supportsPlatform(skill)) continue;
		if (sources.has(skill.name)) throw new Error(`Duplicate skill source: ${skill.name}`);
		const source = expand(skill.source);
		if (!(await exists(path.join(source, 'SKILL.md')))) {
			console.warn(`WARN skill ${skill.name}: source does not exist: ${source}`);
			continue;
		}
		sources.set(skill.name, source);
	}
	return [...sources.entries()];
}

async function consolidateCodexDuplicates() {
	const codexSkills = path.join(home, '.codex', 'skills');
	const names = new Set((await skillSources()).map(([name]) => name));
	for (const name of await skillEntries(path.join(generated, 'prompt-skills'))) names.add(name);
	for (const name of names) {
		const item = path.join(codexSkills, name);
		if (await lexists(item)) await backup(item);
	}
	for (const container of ['obstudio', 'pi-skills']) {
		const item = path.join(codexSkills, container);
		if (await lexists(item)) await backup(item);
	}
}

async function consolidatePiDuplicates() {
	const piSkills = path.join(home, '.pi', 'agent', 'skills');
	const names = new Set((await skillSources()).map(([name]) => name));
	for (const name of await skillEntries(path.join(generated, 'prompt-skills'))) names.add(name);
	for (const name of names) {
		const item = path.join(piSkills, name);
		if (await lexists(item)) await backup(item);
	}
	for (const container of ['obstudio']) {
		const item = path.join(piSkills, container);
		if (await lexists(item)) await backup(item);
	}
}

async function installPromptsAndAgents() {
	if (targets.has('vscode')) {
		const prompts = path.join(vscodeUserDirectory(), 'prompts');
		for (const filename of await entries(promptSource, '.prompt.md')) await installLink(path.join(promptSource, filename), path.join(prompts, filename));
		for (const filename of await entries(agentSource, '.agent.md')) await installLink(path.join(agentSource, filename), path.join(prompts, filename));
		for (const filename of await entries(instructionSource, '.instructions.md')) await installLink(path.join(instructionSource, filename), path.join(prompts, filename));
	}
	if (targets.has('copilot')) {
		for (const filename of await entries(agentSource, '.agent.md')) await installLink(path.join(agentSource, filename), path.join(home, '.copilot', 'agents', filename));
		// Copilot CLI intentionally supports Claude's single-file command format.
		for (const filename of await entries(path.join(generated, 'commands'), '.md')) await installLink(path.join(generated, 'commands', filename), path.join(home, '.claude', 'commands', filename));
		await removeManagedProjection(path.join(repo, 'AGENTS.md'), path.join(home, '.copilot', 'copilot-instructions.md'));
	}
	if (targets.has('claude')) {
		for (const filename of await entries(path.join(generated, 'commands'), '.md')) await installLink(path.join(generated, 'commands', filename), path.join(home, '.claude', 'commands', filename));
		for (const filename of await entries(path.join(generated, 'claude-agents'), '.md')) await installLink(path.join(generated, 'claude-agents', filename), path.join(home, '.claude', 'agents', filename));
		await removeManagedProjection(path.join(repo, 'CLAUDE.md'), path.join(home, '.claude', 'CLAUDE.md'));
	}
	if (targets.has('codex')) {
		for (const filename of await entries(path.join(generated, 'codex-agents'), '.toml')) await installLink(path.join(generated, 'codex-agents', filename), path.join(home, '.codex', 'agents', filename));
		await removeManagedProjection(path.join(repo, 'AGENTS.md'), path.join(home, '.codex', 'AGENTS.md'));
	}
	if (targets.has('pi')) {
		for (const filename of await entries(path.join(generated, 'commands'), '.md')) await installLink(path.join(generated, 'commands', filename), path.join(home, '.pi', 'agent', 'prompts', filename));
		await removeManagedProjection(path.join(repo, 'AGENTS.md'), path.join(home, '.pi', 'agent', 'AGENTS.md'));
		await removeManagedLink(path.join(repo, 'integrations', 'pi', 'mcp-bridge.ts'), path.join(home, '.pi', 'agent', 'extensions', 'work-skills-mcp.ts'));
	}
	if (targets.has('opencode')) {
		for (const filename of await entries(path.join(generated, 'commands'), '.md')) await installLink(path.join(generated, 'commands', filename), path.join(opencodeDirectory(), 'commands', filename));
		for (const filename of await entries(path.join(generated, 'opencode-agents'), '.md')) await installLink(path.join(generated, 'opencode-agents', filename), path.join(opencodeDirectory(), 'agents', filename));
	}
}

async function retirePiDirectSkillAliases() {
	const prompts = path.join(home, '.pi', 'agent', 'prompts');
	if (!(await exists(prompts))) return;
	let found = false;
	for (const entry of await fs.readdir(prompts, { withFileTypes: true })) {
		if (!entry.isSymbolicLink()) continue;
		const item = path.join(prompts, entry.name);
		const target = path.resolve(prompts, await fs.readlink(item));
		if (target.startsWith(`${path.join(generated, 'pi-skill-prompts')}${path.sep}`)) found = true;
	}
	if (!found) return;
	const file = path.join(home, '.pi', 'agent', 'settings.json');
	const config = await readJson(file);
	if (config.enableSkillCommands === false) delete config.enableSkillCommands;
	await writeJson(file, config);
}

async function installPiPromptSkillOverrides() {
	const file = path.join(home, '.pi', 'agent', 'settings.json');
	const config = await readJson(file);
	const state = await readJson(managedStatePath, { mcpServers: {}, credentials: [] });
	const previous = new Set(state.piPromptSkillExclusions || []);
	const current = [];
	for (const filename of await entries(promptSource, '.prompt.md')) {
		const parsed = splitFrontmatter(await fs.readFile(path.join(promptSource, filename), 'utf8'));
		const fallback = filename.replace(/\.prompt\.md$/, '');
		current.push(`-skills/${portableId(parsed.data.name || fallback, fallback)}`);
	}
	config.skills = [...new Set([...(config.skills || []).filter(item => !previous.has(item)), ...current])];
	state.piPromptSkillExclusions = current;
	await writeJson(file, config);
	await writeJson(managedStatePath, state);
}

function vscodeUserDirectory() {
	if (process.env.VSCODE_INSIDERS_USER_DATA_DIR) return process.env.VSCODE_INSIDERS_USER_DATA_DIR;
	if (process.platform === 'darwin') return path.join(home, 'Library', 'Application Support', 'Code - Insiders', 'User');
	if (process.platform === 'win32') return path.join(process.env.APPDATA || path.join(home, 'AppData', 'Roaming'), 'Code - Insiders', 'User');
	return path.join(home, '.config', 'Code - Insiders', 'User');
}

function opencodeDirectory() {
	return path.join(process.env.XDG_CONFIG_HOME || path.join(home, '.config'), 'opencode');
}

async function loadManifest() {
	return readJson(manifestPath);
}

function selectedServers(manifest, target) {
	return Object.entries(manifest.servers).filter(([, server]) => supportsPlatform(server) && !(server.excludeTargets || []).includes(target));
}

function mergeManagedServers(existing, current, previouslyManaged) {
	const merged = { ...(existing || {}) };
	for (const name of previouslyManaged) delete merged[name];
	return { ...merged, ...current };
}

function managedServerNames(state, manifest, target) {
	return new Set([...(state.mcpServers?.[target] || []), ...(manifest.retiredServers || [])]);
}

function stdioEnvironment(server, syntax) {
	return Object.fromEntries((server.envPass || []).map(name => [name, syntax(name)]));
}

function bearerHeader(server, syntax) {
	return server.bearerEnv ? { Authorization: `Bearer ${syntax(server.bearerEnv)}` } : {};
}

function renderVSCodeServer(server) {
	if (server.transport === 'stdio') {
		return { type: 'stdio', command: expand(server.command), ...(server.args ? { args: server.args.map(expand) } : {}), ...(server.cwd ? { cwd: expand(server.cwd) } : {}), ...(server.envPass?.length ? { env: stdioEnvironment(server, name => `\${env:${name}}`) } : {}) };
	}
	return { type: 'http', url: server.url, ...(server.bearerEnv ? { headers: { Authorization: `Bearer \${input:${server.bearerEnv.toLowerCase()}}` } } : {}) };
}

function renderAgentHostServer(server) {
	if (server.transport === 'stdio') {
		return { type: 'stdio', command: expand(server.command), ...(server.args ? { args: server.args.map(expand) } : {}), ...(server.cwd ? { cwd: expand(server.cwd) } : {}), ...(server.envPass?.length ? { env: Object.fromEntries(server.envPass.filter(name => process.env[name]).map(name => [name, process.env[name]])) } : {}) };
	}
	return { type: 'http', url: server.url, ...(server.bearerEnv && process.env[server.bearerEnv] ? { headers: { Authorization: `Bearer ${process.env[server.bearerEnv]}` } } : {}) };
}

function renderCopilotServer(server) {
	if (server.transport === 'stdio') {
		return { tools: ['*'], type: 'local', command: expand(server.command), ...(server.args ? { args: server.args.map(expand) } : {}), ...(server.cwd ? { cwd: expand(server.cwd) } : {}), ...(server.envPass?.length ? { env: stdioEnvironment(server, name => `\${env:${name}}`) } : {}) };
	}
	return { tools: ['*'], type: 'http', url: server.url, ...(server.bearerEnv ? { headers: bearerHeader(server, name => `\${env:${name}}`) } : {}) };
}

function renderClaudeServer(server) {
	if (server.transport === 'stdio') {
		return { type: 'stdio', command: expand(server.command), ...(server.args ? { args: server.args.map(expand) } : {}), ...(server.cwd ? { cwd: expand(server.cwd) } : {}), ...(server.envPass?.length ? { env: stdioEnvironment(server, name => `\${${name}}`) } : {}) };
	}
	return { type: 'http', url: server.url, ...(server.bearerEnv ? { headers: bearerHeader(server, name => `\${${name}}`) } : {}) };
}

function renderOpenCodeServer(server) {
	if (server.transport === 'stdio') {
		return { type: 'local', command: [expand(server.command), ...(server.args || []).map(expand)], ...(server.cwd ? { cwd: expand(server.cwd) } : {}), ...(server.envPass?.length ? { environment: stdioEnvironment(server, name => `{env:${name}}`) } : {}) };
	}
	return { type: 'remote', url: server.url, ...(server.bearerEnv ? { headers: bearerHeader(server, name => `{env:${name}}`) } : {}) };
}

function renderMcporterServer(server) {
	server = server.mcporter ?? server;
	if (server.transport === 'stdio') {
		return {
			command: expand(server.command),
			...(server.args ? { args: server.args.map(expand) } : {}),
			...(server.cwd ? { cwd: expand(server.cwd) } : {}),
		};
	}
	return {
		baseUrl: server.url,
		...(server.bearerEnv ? { headers: bearerHeader(server, name => `$env:${name}`) } : {}),
	};
}

async function installMcp() {
	const manifest = await loadManifest();
	const state = await readJson(managedStatePath, { mcpServers: {}, credentials: [] });
	state.mcpServers ||= {};
	state.credentials ||= [];
	if (targets.has('vscode')) {
		const file = path.join(vscodeUserDirectory(), 'mcp.json');
		const config = await readJson(file, { servers: {}, inputs: [] });
		const selected = selectedServers(manifest, 'vscode');
		config.servers = mergeManagedServers(config.servers, Object.fromEntries(selected.map(([name, server]) => [name, renderVSCodeServer(server)])), managedServerNames(state, manifest, 'vscode'));
		const existingInputs = new Map((config.inputs || []).map(input => [input.id, input]));
		const currentCredentialIds = new Set(Object.keys(manifest.credentials || {}).map(name => name.toLowerCase()));
		for (const id of [...(state.credentials || []), ...(manifest.retiredCredentials || [])].map(name => name.toLowerCase())) {
			if (!currentCredentialIds.has(id)) existingInputs.delete(id);
		}
		for (const [name, description] of Object.entries(manifest.credentials || {})) existingInputs.set(name.toLowerCase(), { id: name.toLowerCase(), type: 'promptString', description, password: true });
		config.inputs = [...existingInputs.values()];
		await writeJson(file, config);
		state.mcpServers.vscode = selected.map(([name]) => name);
		state.credentials = Object.keys(manifest.credentials || {});
	}
	if (targets.has('agent-host')) {
		const file = path.join(vscodeUserDirectory(), 'globalStorage', 'agent-host-config.json');
		const config = await readJson(file);
		const selected = selectedServers(manifest, 'agent-host');
		config.mcpServers = mergeManagedServers(config.mcpServers, Object.fromEntries(selected.map(([name, server]) => [name, renderAgentHostServer(server)])), managedServerNames(state, manifest, 'agent-host'));
		await writeJson(file, config);
		state.mcpServers['agent-host'] = selected.map(([name]) => name);
	}
	if (targets.has('copilot')) {
		const file = path.join(process.env.COPILOT_HOME || path.join(home, '.copilot'), 'mcp-config.json');
		const config = await readJson(file, { mcpServers: {} });
		const selected = selectedServers(manifest, 'copilot');
		config.mcpServers = mergeManagedServers(config.mcpServers, Object.fromEntries(selected.map(([name, server]) => [name, renderCopilotServer(server)])), managedServerNames(state, manifest, 'copilot'));
		await writeJson(file, config);
		state.mcpServers.copilot = selected.map(([name]) => name);
	}
	if (targets.has('claude')) {
		const file = process.env.CLAUDE_CONFIG_DIR ? path.join(process.env.CLAUDE_CONFIG_DIR, '.claude.json') : path.join(home, '.claude.json');
		const config = await readJson(file);
		const selected = selectedServers(manifest, 'claude');
		config.mcpServers = mergeManagedServers(config.mcpServers, Object.fromEntries(selected.map(([name, server]) => [name, renderClaudeServer(server)])), managedServerNames(state, manifest, 'claude'));
		await writeJson(file, config);
		state.mcpServers.claude = selected.map(([name]) => name);
	}
	if (targets.has('codex')) {
		await installCodexMcp(manifest, managedServerNames(state, manifest, 'codex'));
		state.mcpServers.codex = selectedServers(manifest, 'codex').map(([name]) => name);
	}
	if (targets.has('opencode')) {
		await installOpenCodeMcp(manifest, managedServerNames(state, manifest, 'opencode'));
		state.mcpServers.opencode = selectedServers(manifest, 'opencode').map(([name]) => name);
	}
	await writeJson(managedStatePath, state);
}

async function installCodexMcp(manifest, previouslyManaged) {
	const file = path.join(process.env.CODEX_HOME || path.join(home, '.codex'), 'config.toml');
	let text = (await exists(file)) ? await fs.readFile(file, 'utf8') : '';
	for (const name of previouslyManaged) text = removeTomlTable(text, `mcp_servers.${name}`);
	for (const [name, server] of selectedServers(manifest, 'codex')) text = replaceTomlTable(text, `mcp_servers.${name}`, codexToml(name, server));
	if ((await exists(file)) && (await fs.readFile(file, 'utf8')) === text) return log('unchanged', file);
	log('write', file);
	if (dryRun) return;
	await fs.mkdir(path.dirname(file), { recursive: true });
	await fs.writeFile(file, text.endsWith('\n') ? text : `${text}\n`);
}

function codexToml(name, server) {
	const lines = [`[mcp_servers.${JSON.stringify(name)}]`];
	if (server.transport === 'stdio') {
		lines.push(`command = ${JSON.stringify(expand(server.command))}`);
		if (server.args?.length) lines.push(`args = ${JSON.stringify(server.args.map(expand))}`);
		if (server.cwd) lines.push(`cwd = ${JSON.stringify(expand(server.cwd))}`);
		if (server.envPass?.length) lines.push(`env_vars = ${JSON.stringify(server.envPass)}`);
	} else {
		lines.push(`url = ${JSON.stringify(server.url)}`);
		if (server.bearerEnv) lines.push(`bearer_token_env_var = ${JSON.stringify(server.bearerEnv)}`);
	}
	return `${lines.join('\n')}\n`;
}

function replaceTomlTable(text, table, replacement) {
	const stripped = removeTomlTable(text, table);
	return `${stripped}${stripped ? '\n\n' : ''}${replacement}`;
}

function removeTomlTable(text, table) {
	const output = [];
	let skipping = false;
	for (const line of text.split('\n')) {
		const header = /^\s*\[([^\]]+)\]\s*$/.exec(line);
		if (header) {
			const normalized = header[1].replaceAll('"', '').replaceAll("'", '');
			skipping = normalized === table || normalized.startsWith(`${table}.`);
		}
		if (!skipping) output.push(line);
	}
	return output.join('\n').trimEnd();
}

async function installOpenCodeMcp(manifest, previouslyManaged) {
	const file = path.join(opencodeDirectory(), 'opencode.jsonc');
	const original = (await exists(file)) ? await fs.readFile(file, 'utf8') : '{}\n';
	const parsed = parseJsonc(original) || {};
	const mcp = mergeManagedServers(parsed.mcp, Object.fromEntries(selectedServers(manifest, 'opencode').map(([name, server]) => [name, renderOpenCodeServer(server)])), previouslyManaged);
	const updated = applyEdits(original, modify(original, ['mcp'], mcp, { formattingOptions: { insertSpaces: true, tabSize: 2 } }));
	if (updated === original) return log('unchanged', file);
	log('write', file);
	if (dryRun) return;
	await fs.mkdir(path.dirname(file), { recursive: true });
	await fs.writeFile(file, updated);
}

async function importCustomizations() {
	const vscodePrompts = path.join(vscodeUserDirectory(), 'prompts');
	for (const filename of await entries(vscodePrompts, '.md')) {
		const destination = filename.endsWith('.agent.md') ? path.join(agentSource, filename)
			: filename.endsWith('.prompt.md') ? path.join(promptSource, filename)
				: filename.endsWith('.instructions.md') ? path.join(instructionSource, filename) : undefined;
		if (destination && !(await exists(destination))) await copyImported(path.join(vscodePrompts, filename), destination);
	}
	for (const root of [path.join(home, '.agents', 'skills'), path.join(home, '.copilot', 'skills'), path.join(home, '.claude', 'skills'), path.join(home, '.codex', 'skills')]) {
		for (const name of await entries(root)) {
			const source = path.join(root, name);
			if ((await exists(path.join(source, 'SKILL.md'))) && !(await exists(path.join(skillSource, name)))) await copyImported(source, path.join(skillSource, name));
		}
	}
	const vscodeMcp = await readJson(path.join(vscodeUserDirectory(), 'mcp.json'), { servers: {} });
	const manifest = await loadManifest();
	for (const name of Object.keys(vscodeMcp.servers || {}).filter(name => !manifest.servers[name])) log('review MCP', `${name} exists in VS Code but not ${manifestPath}`);
}

async function copyImported(source, destination) {
	log('import', `${source} -> ${destination}`);
	if (dryRun) return;
	await fs.mkdir(path.dirname(destination), { recursive: true });
	await fs.cp(await fs.realpath(source), destination, { recursive: true, filter: item => !item.includes(`${path.sep}node_modules${path.sep}`) });
}

async function status() {
	const external = await readJson(externalSkillSourcesPath, { skills: [] });
	console.log(`Repository: ${repo}`);
	console.log(`Targets:    ${[...targets].join(', ')}`);
	console.log(`Skills:     ${(await skillEntries(skillSource)).length} canonical roots + ${(external.skills || []).length} external roots`);
	console.log(`Prompts:    ${(await entries(promptSource, '.prompt.md')).length}`);
	console.log(`Agents:     ${(await entries(agentSource, '.agent.md')).length}`);
	for (const [name, executable] of Object.entries({ vscode: 'code-insiders', copilot: 'copilot', claude: 'claude', codex: 'codex', pi: 'pi', opencode: path.join(home, '.opencode', 'bin', 'opencode') })) {
		console.log(`${name.padEnd(12)} ${commandExists(executable) ? 'installed' : 'missing'}`);
	}
}

function commandExists(executable) {
	try {
		execFileSync(process.platform === 'win32' ? 'where' : 'sh', process.platform === 'win32' ? [executable] : ['-c', `command -v ${shellQuote(executable)}`], { stdio: 'ignore', timeout: 3000 });
		return true;
	} catch {
		return false;
	}
}

function shellQuote(value) {
	return `'${value.replaceAll("'", "'\\''")}'`;
}

async function validate() {
	let failures = 0;
	for (const name of await skillEntries(skillSource)) failures += await validateSkill(path.join(skillSource, name));
	const external = await readJson(externalSkillSourcesPath, { skills: [] });
	for (const skill of external.skills || []) {
		if (!supportsPlatform(skill)) continue;
		const source = expand(skill.source);
		if (!(await exists(path.join(source, 'SKILL.md')))) {
			console.warn(`WARN skill ${skill.name}: source does not exist: ${source}`);
			continue;
		}
		failures += await validateSkill(source, skill.name);
	}
	for (const name of await skillEntries(path.join(generated, 'prompt-skills'))) failures += await validateSkill(path.join(generated, 'prompt-skills', name));
	const manifest = await loadManifest();
	for (const [name, server] of Object.entries(manifest.servers)) {
		if (!supportsPlatform(server)) continue;
		if (server.transport === 'stdio' && expand(server.command).includes('/') && !(await exists(expand(server.command)))) console.warn(`WARN MCP ${name}: command does not exist: ${expand(server.command)}`);
		for (const variable of [server.bearerEnv, ...(server.envPass || [])].filter(Boolean)) if (!process.env[variable]) console.warn(`WARN MCP ${name}: ${variable} is not set`);
	}
	if (connect) failures += validateClients();
	if (failures) throw new Error(`${failures} validation check(s) failed`);
	console.log('Validation passed. Warnings may still require credentials or optional local programs.');
}

async function validateSkill(directory, expectedName) {
	const file = path.join(directory, 'SKILL.md');
	if (!(await exists(file))) return 0;
	const parsed = splitFrontmatter(await fs.readFile(file, 'utf8'));
	const name = parsed.data.name;
	const description = parsed.data.description;
	if (!name || !description) {
		console.error(`FAIL ${file}: name and description are required`);
		return 1;
	}
	if (expectedName && name !== expectedName) {
		console.error(`FAIL ${file}: expected skill name ${expectedName}, found ${name}`);
		return 1;
	}
	if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name) || name.length > 64) {
		console.error(`FAIL ${file}: invalid skill name ${name}`);
		return 1;
	}
	return 0;
}

function validateClients() {
	let failures = 0;
	const checks = [
		['codex', ['mcp', 'list']],
		['claude', ['mcp', 'list']],
		['copilot', ['mcp', 'list']],
		[path.join(home, '.opencode', 'bin', 'opencode'), ['mcp', 'list']],
	];
	for (const [executable, clientArgs] of checks) {
		if (!commandExists(executable)) continue;
		try {
			execFileSync(executable, clientArgs, { stdio: 'inherit', timeout: 120000, env: { ...process.env, COPILOT_AUTO_UPDATE: 'false' } });
		} catch {
			console.error(`FAIL ${executable} ${clientArgs.join(' ')}`);
			failures++;
		}
	}
	return failures;
}

async function credentials() {
	const manifest = await loadManifest();
	for (const [name, description] of Object.entries(manifest.credentials || {})) console.log(`${name}\n  ${description}\n`);
}

async function bootstrap() {
	if (targets.has('pi')) await retirePiDirectSkillAliases();
	await generateFiles();
	await cleanProjectionRoots();
	await installSkills();
	if (targets.has('pi')) await installPiUpstreamSkills();
	await installPromptsAndAgents();
	if (targets.has('pi')) {
		await installPiProductPackages();
		await installPiPromptSkillOverrides();
	}
	await installMcp();
	console.log('\nBootstrap complete. Restart VS Code and start new CLI sessions, then run ./setup.sh validate.');
}

if (args.length) throw new Error(`Unknown arguments: ${args.join(' ')}`);

switch (command) {
	case 'bootstrap':
	case 'install': await bootstrap(); break;
	case 'generate': await generateFiles(); break;
	case 'import': await importCustomizations(); break;
	case 'status': await status(); break;
	case 'validate': await validate(); break;
	case 'credentials': await credentials(); break;
	default: throw new Error(`Unknown command: ${command}`);
}
