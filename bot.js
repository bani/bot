require('dotenv').config();
const Discord = require('discord.js');
const client = new Discord.Client();
const fs = require('fs');

client.on('ready', () => {
  console.log(`Logged in as ${client.user.tag}!`);
});

function post(channel){
  let content = JSON.parse(fs.readFileSync('meetup.json'));
  channel.send({embed: content});
}

client.on('message', msg => {
  if(msg.author.id === '227549003296800768') {

    switch(msg.channel.id) {
      case '745439018002415626': // tmp @ bani
        switch(msg.content) {
          case 'ping':
            msg.reply('pong!');
          break;
          case 'post':
            post(msg.channel);
          break;
        }
      break;
      case '757394819764060261': // DM
        switch(msg.content) {
          case 'members':
            const guild = client.guilds.get('683848441452822548') // 684502050255667230
            guild.fetchMembers().then(r => {
              r.members.array().forEach(r => {
                let userData = `${r.user.username},${r.joinedAt.toISOString()},${r.user.createdAt.toISOString()}`;
                console.log(`${userData}`);
              });
            });
          break;
        }
      break;
    }
  }
});

client.login(process.env.DISCORD_TOKEN);
