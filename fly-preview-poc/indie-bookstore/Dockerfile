# Pebble preview Machine — runs `next dev` for a single generated site.
# Per-project apps (one app per slug); Fly Machine inside auto-stops on idle.
#
# 2026-05-23 POC: site files baked into the image. Stage-2 design will
# swap this for a Tigris volume mount so a single base image serves any
# slug with files synced live from the engine.

FROM node:20-alpine AS base
WORKDIR /app

# Tini = small init that reaps zombie child processes (next dev spawns workers)
RUN apk add --no-cache tini

# Copy lock files first so `npm ci` layer caches when deps don't change
COPY package.json package-lock.json* ./

# `npm ci` (not install) — uses lock file exactly, doesn't write to it
RUN npm ci --no-audit --no-fund --loglevel=error

# Copy the rest of the site
COPY . .

# Fly's auto-start sends traffic to the internal port. next dev binds
# 0.0.0.0 so it accepts connections from the Fly proxy (not just localhost).
ENV NODE_ENV=development
ENV PORT=8080
EXPOSE 8080

# Tini handles SIGTERM (Fly's graceful-stop) so next dev shuts down cleanly
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["npm", "run", "dev", "--", "-p", "8080", "-H", "0.0.0.0"]
