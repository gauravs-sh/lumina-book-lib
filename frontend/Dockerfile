FROM node:18-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* /app/
RUN rm -f package-lock.json && npm install --include=dev --no-audit --no-fund

COPY . /app
RUN rm -rf /app/src/pages
ENV PATH=/app/node_modules/.bin:$PATH
ENV NEXT_DISABLE_ESLINT=1
ENV NEXT_TELEMETRY_DISABLED=1
RUN npx next build --no-lint

FROM node:18-alpine

WORKDIR /app
ENV NODE_ENV=production

COPY --from=build /app/.next /app/.next
COPY --from=build /app/public /app/public
COPY --from=build /app/package.json /app/package.json
COPY --from=build /app/node_modules /app/node_modules

EXPOSE 3000
CMD ["npm", "start"]
