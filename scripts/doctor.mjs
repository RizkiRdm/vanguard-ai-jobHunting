#!/usr/bin/env node
// Checks the local toolchain and configuration. Prints names, never values.
import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');

// Keep in sync with apps/server/src/config/env.ts and apps/web/src/env.ts.
const REQUIRED_ENV = [
  'DATABASE_URL',
  'SUPABASE_URL',
  'SUPABASE_PUBLISHABLE_KEY',
  'SUPABASE_SECRET_KEY',
  'SUPABASE_JWKS_URL',
  'GEMINI_API_KEY',
  'API_BASE_URL',
];

export function parseEnvFile(text) {
  const out = {};
  for (const raw of text.split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const eq = line.indexOf('=');
    if (eq < 1) continue;
    const key = line
      .slice(0, eq)
      .replace(/^export\s+/, '')
      .trim();
    let value = line.slice(eq + 1).trim();
    if (/^(['"]).*\1$/.test(value)) value = value.slice(1, -1);
    out[key] = value;
  }
  return out;
}

export function envStatus(required, env) {
  return required.map((name) => {
    const value = env[name] ?? '';
    if (value === '') return { name, status: 'missing' };
    if (/^(replace|changeme|your[-_])/i.test(value)) return { name, status: 'placeholder' };
    return { name, status: 'present' };
  });
}

export function minNodeVersion(enginesNode) {
  const match = /(\d+)/.exec(enginesNode ?? '');
  return match ? Number(match[1]) : 0;
}

export function isAtLeast(current, minimum) {
  const major = Number.parseInt(String(current).split('.')[0], 10);
  return Number.isFinite(major) && major >= minimum;
}

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'));
}

function missingDependencies() {
  try {
    const tree = JSON.parse(
      execFileSync('npm', ['ls', '--depth=0', '--json'], {
        cwd: root,
        encoding: 'utf8',
        stdio: ['ignore', 'pipe', 'ignore'],
      }),
    );
    return tree.problems ?? [];
  } catch (error) {
    try {
      return JSON.parse(String(error.stdout ?? '{}')).problems ?? [];
    } catch {
      return [{ code: 'npm-ls-failed' }];
    }
  }
}

function playwrightBrowsers() {
  const dirs = [
    process.env.PLAYWRIGHT_BROWSERS_PATH,
    join(homedir(), '.cache', 'ms-playwright'),
    join(homedir(), 'Library', 'Caches', 'ms-playwright'),
  ].filter(Boolean);
  for (const dir of dirs) {
    if (!existsSync(dir)) continue;
    return readdirSync(dir).filter((entry) => entry.startsWith('chromium'));
  }
  return [];
}

function main() {
  const labels = { ok: 'ok  ', warn: 'warn', fail: 'fail' };
  const lines = [];
  let errors = 0;
  let warnings = 0;

  function report(level, message) {
    if (level === 'fail') errors += 1;
    if (level === 'warn') warnings += 1;
    lines.push(`${labels[level]}  ${message}`);
  }

  const pkg = readJson(join(root, 'package.json'));

  const minNode = minNodeVersion(pkg.engines?.node);
  if (isAtLeast(process.versions.node, minNode)) {
    report('ok', `node ${process.versions.node} (package.json requires ${pkg.engines?.node})`);
  } else {
    report('fail', `node ${process.versions.node} is below the required ${pkg.engines?.node}`);
  }

  if (existsSync(join(root, 'package-lock.json'))) {
    report('ok', 'package-lock.json present');
  } else {
    report('fail', 'package-lock.json missing - run npm install');
  }

  if (existsSync(join(root, 'node_modules'))) {
    report('ok', 'node_modules present');
  } else {
    report('fail', 'node_modules missing - run npm install');
  }

  const problems = missingDependencies();
  for (const problem of problems) {
    if (problem.code === 'npm-ls-failed') {
      report('warn', 'npm ls failed - run npm install');
    } else if (problem.extraneous) {
      report('warn', `${problem.name ?? problem.path} installed but not in package.json`);
    } else {
      report(
        'fail',
        `${problem.name ?? problem.path} ${problem.code ?? 'invalid'} - run npm install`,
      );
    }
  }

  const envPath = join(root, '.env');
  const fileEnv = existsSync(envPath) ? parseEnvFile(readFileSync(envPath, 'utf8')) : {};
  const merged = { ...fileEnv, ...process.env };
  if (!existsSync(envPath)) report('warn', '.env not found (copy .env.example and fill it in)');

  for (const { name, status } of envStatus(REQUIRED_ENV, merged)) {
    if (status === 'present') report('ok', `${name} present`);
    else if (status === 'placeholder') report('fail', `${name} still has an example value`);
    else report('fail', `${name} missing`);
  }

  if (existsSync(join(root, '.env.example'))) {
    const example = parseEnvFile(readFileSync(join(root, '.env.example'), 'utf8'));
    const undocumented = Object.keys(fileEnv).filter((key) => !(key in example));
    if (undocumented.length > 0) {
      report('warn', `.env keys not in .env.example: ${undocumented.join(', ')}`);
    }
  }

  if (!merged.TEST_DATABASE_URL) {
    report('warn', 'TEST_DATABASE_URL unset - the 4 database integration tests will skip');
  }

  if (existsSync(join(root, 'node_modules', 'playwright'))) {
    const browsers = playwrightBrowsers();
    if (browsers.length > 0) report('ok', `playwright browsers: ${browsers.join(', ')}`);
    else
      report(
        'warn',
        'playwright installed but no chromium found - run npx playwright install chromium',
      );
  } else {
    report('fail', 'playwright not installed - run npm install');
  }

  const migrationsDir = join(root, 'supabase', 'migrations');
  if (existsSync(migrationsDir)) {
    const count = readdirSync(migrationsDir).filter((name) => name.endsWith('.sql')).length;
    report('ok', `${count} migrations in supabase/migrations (apply with npm run db:migrate)`);
  }

  console.log(lines.join('\n'));
  console.log(`\n${errors} error(s), ${warnings} warning(s)`);
  process.exit(errors > 0 ? 1 : 0);
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
