FROM node:20

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
COPY . .

RUN npm install
RUN npm install --save-dev vite

EXPOSE 3000

CMD ["npm", "run", "dev"]