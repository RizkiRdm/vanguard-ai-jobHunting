# Single image for both the API and the worker; run them with different commands.
FROM node:22-bookworm-slim

WORKDIR /app
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Chromium and its system libraries are needed by the worker at runtime.
COPY package.json package-lock.json ./
COPY apps/server/package.json apps/server/
COPY apps/web/package.json apps/web/
COPY packages/contracts/package.json packages/contracts/
RUN npm ci --ignore-scripts=false \
  && npx playwright install --with-deps chromium \
  && rm -rf /var/lib/apt/lists/*

COPY . .
RUN npm run build

ENV NODE_ENV=production
EXPOSE 8000

CMD ["npx", "tsx", "apps/server/src/api.ts"]
