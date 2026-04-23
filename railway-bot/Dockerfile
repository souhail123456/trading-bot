FROM node:20-slim

# Install git, curl, python3 (needed for agent tool execution)
RUN apt-get update && apt-get install -y git curl python3 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package.json ./
RUN npm install --production
COPY agent.js scheduler.js ./

CMD ["node", "scheduler.js"]
