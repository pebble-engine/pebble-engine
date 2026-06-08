# Pebble preview-machine image — one shared image, cloned into a Fly Machine
# per active preview. Foundation deps are baked in so `next dev` boots with NO
# npm install; the engine only ever syncs source files into /site at runtime.
#
# Build + push once (see README.md):
#   fly deploy --image-label pebble-preview --dockerfile fleet/preview-machine/Dockerfile
FROM node:20-slim

WORKDIR /site

# Bake node_modules from the canonical foundation dep set. Layer-cached: only
# rebuilds when package.json changes.
COPY package.json /site/package.json
RUN npm install --no-audit --no-fund --loglevel=error

# A minimal placeholder so `next dev` can start before the first /sync. The
# engine overwrites these with the real site on the first sync.
RUN mkdir -p /site/app \
 && printf 'export default function Page(){return null}\n' > /site/app/page.tsx \
 && printf 'export default function RootLayout({children}:{children:React.ReactNode}){return (<html lang="en"><body>{children}</body></html>)}\n' > /site/app/layout.tsx \
 && printf '/** @type {import("next").NextConfig} */\nconst nextConfig = { typescript: { ignoreBuildErrors: true }, eslint: { ignoreDuringBuilds: true }, images: { unoptimized: true } };\nexport default nextConfig;\n' > /site/next.config.mjs \
 && printf '{"compilerOptions":{"target":"ES2017","lib":["dom","dom.iterable","esnext"],"allowJs":true,"skipLibCheck":true,"strict":false,"noEmit":true,"esModuleInterop":true,"module":"esnext","moduleResolution":"bundler","resolveJsonModule":true,"isolatedModules":true,"jsx":"preserve","incremental":true,"paths":{"@/*":["./*"]}},"include":["next-env.d.ts","**/*.ts","**/*.tsx",".next/types/**/*.ts"],"exclude":["node_modules"]}\n' > /site/tsconfig.json

# The receiver runs on the public port and proxies to next dev internally.
COPY receiver.mjs /receiver.mjs

ENV PORT=8080
EXPOSE 8080
CMD ["node", "/receiver.mjs"]
