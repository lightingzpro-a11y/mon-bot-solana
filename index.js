const { Telegraf } = require('telegraf');
const { Connection, PublicKey, Keypair, Transaction, SystemProgram } = require('@solana/web3.js');
const base58 = require('base58-js');

const TELEGRAM_BOT_TOKEN = '8232782908:AAFlQ4_B9sfdoN9rSBMbaONdASvDYX7Vktg';
const SOLANA_RPC_URL = 'https://api.mainnet-beta.solana.com';  // RPC officiel public
const WALLET_PRIVATE_KEY_BASE58 = '48c9B8Dv6vBydsdeCz6o1gyYHPvcUNvJxMJkAZwShtJVSsr3bmNTPwgEzBVFLNWjxuohmqMdSqeDk8ruPoRxEBB9';

const bot = new Telegraf(TELEGRAM_BOT_TOKEN);

const connection = new Connection(SOLANA_RPC_URL, 'confirmed');
const secretKey = base58.decode(WALLET_PRIVATE_KEY_BASE58);
const wallet = Keypair.fromSecretKey(secretKey);

bot.start((ctx) => ctx.reply('Bot Solana prêt. Envoie le nom du token.'));

bot.on('text', async (ctx) => {
  const tokenAddress = ctx.message.text;
  ctx.reply(`Reçu : ${tokenAddress}\nJe vais essayer d'acheter ce token...`);
  
  // Ici tu dois implémenter la logique pour acheter via Jupiter DEX
  // Attention: acheter un token sur Solana nécessite des calls à Jupiter API + transactions signées
  // Ça dépasse ce petit exemple

  ctx.reply(`Achat automatique du token ${tokenAddress} (non implémenté dans cet exemple).`);
});

bot.launch().then(() => console.log('Bot Telegram démarré.'));

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));

