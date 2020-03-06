require('dotenv').config();
const Discord = require('discord.js');
const client = new Discord.Client();
const fs = require('fs');

client.on('ready', () => {
  console.log(`Logged in as ${client.user.tag}!`);
});

function meetup(channel){
  let content = JSON.parse(fs.readFileSync('meetup.json'));
  channel.send({embed: content});
}

client.on('message', msg => {
  if(msg.author.id === '227549003296800768') {
    switch(msg.channel.id) {
      case '684806033066950808': // bottest @ weureka
        switch(msg.content) {
          case 'ping':
            msg.reply('pong!');
          break;
          case 'meetup?':
            meetup(msg.channel);
          break;
        }
      break;
      case '683871601837735944': // events @ ctrl+alt_del
        switch(msg.content) {
          case 'meetup?':
            meetup(msg.channel);
          break;
        }
      break;
    }
  }
});

client.on('guildMemberAdd', member => {
  console.log(`${member.displayName} has joined!`);
  // member.guild.channels.get('684061018313457739').send();
});

client.login(process.env.DISCORD_TOKEN);
