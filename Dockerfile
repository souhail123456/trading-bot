FROM node:20-slim

RUN apt-get update && apt-get install -y \
    bash curl python3 git jq ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g @anthropic-ai/claude-code

WORKDIR /app
COPY . .
RUN chmod +x scripts/*.sh scripts/run-routine.sh

CMD ["bash"]
