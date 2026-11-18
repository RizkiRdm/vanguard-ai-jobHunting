# Single image for both the API and the worker; run them with different commands.
FROM oven/bun:1.4.4 AS bun
FROM node:22-bookworm-slim

COPY --from=bun /usr/local/bin/bun /usr/local/bin/bun
WORKDIR /app
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Chromium and its system libraries are needed by the worker at runtime.
COPY package.json bun.lock ./
COPY apps/server/package.json apps/server/
COPY apps/web/package.json apps/web/
COPY packages/contracts/package.json packages/contracts/
RUN bun ci \
  && node_modules/.bin/playwright install --with-deps chromium \
  && rm -rf /var/lib/apt/lists/*

COPY . .
RUN bun run build

ENV NODE_ENV=production
EXPOSE 8000

CMD ["node_modules/.bin/tsx", "apps/server/src/api.ts"]
