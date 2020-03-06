'use strict';

require('dotenv').config();
const fs = require('fs');
const Discord = require('discord.js');

const hook = new Discord.WebhookClient(process.env.WEBHOOK_ID, process.env.WEBHOOK_TOKEN);

let content = JSON.parse(fs.readFileSync('meetup.json'));
hook.send({
  "embeds": [content]
});
