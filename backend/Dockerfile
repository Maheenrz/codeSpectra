FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# Replace with your actual startup command
CMD ["npm", "start"]