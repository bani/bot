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


const d = {
  // users
  u_bani: '227549003296800768',
  // channels
  c_tmp: '745439018002415626', // tmp @ bani
  c_dm: '757394819764060261', // direct message
  // servers
  s_bani: '684502050255667230', // bani
  s_cad: '683848441452822548', // ctrl+alt+del
}

client.on('message', msg => {
  if(msg.author.id === d.u_bani) {
    switch(msg.channel.id) {
      case d.c_tmp:
        switch(msg.content) {
          case 'ping':
            msg.reply('pong!');
          break;
          case 'post':
            post(msg.channel);
          break;
        }
      break;
      case d.c_dm:
        switch(msg.content) {
          case 'members':
            const guild = client.guilds.get(d.s_bani) // 
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
