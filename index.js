const { Keypair, Connection, clusterApiUrl } = require('@solana/web3.js');
const bs58 = require('bs58');
const TelegramBot = require('node-telegram-bot-api');

// === CONFIGURATION ===

// Ton token Telegram (vérifie bien que c'est celui de ton bot, pas de doublon)
const TELEGRAM_TOKEN = '8232782908:AAFlQ4_B9sfdoN9rSBMbaONdASvDYX7Vktg';

// Ta clé privée Solana en base58 (celle que tu m’as donnée)
const SECRET_KEY_BASE58 = '48c9B8Dv6vBydsdeCz6o1gyYHPvcUNvJxMJkAZwShtJVSsr3bmNTPwgEzBVFLNWjxuohmqMdSqeDk8ruPoRxEBB9';

// Connexion RPC Solana mainnet
const connection = new Connection(clusterApiUrl('mainnet-beta'), 'confirmed');

// === INITIALISATION ===

const secretKeyUint8 = bs58.decode(SECRET_KEY_BASE58);
const keypair = Keypair.fromSecretKey(secretKeyUint8);

console.log('Bot démarré avec le wallet :', keypair.publicKey.toBase58());

// === INITIALISATION TELEGRAM BOT ===

// Important : Assure-toi qu’aucun autre processus ne tourne avec ce même token, sinon conflit 409
const bot = new TelegramBot(TELEGRAM_TOKEN, { polling: true });

bot.on('message', async (msg) => {
  const chatId = msg.chat.id;
  const tokenReceived = msg.text?.trim();

  console.log(`Message reçu de ${chatId} : ${tokenReceived}`);

  if (!tokenReceived) {
    bot.sendMessage(chatId, "Merci d'envoyer une adresse de token valide.");
    return;
  }

  // Envoi de message simple en retour
  bot.sendMessage(chatId, `Token reçu : ${tokenReceived}\nDébut du processus d'achat sur Jupiter DEX...`);

  // Ici, tu ajouteras ton code pour acheter via Jupiter DEX

  // Simulé pour l’instant
  bot.sendMessage(chatId, `Achat simulé du token ${tokenReceived} avec ton wallet ${keypair.publicKey.toBase58()}`);
});

// Gestion simple des erreurs
bot.on("polling_error", (err) => {
  console.error('Erreur Telegram polling:', err.code, err.message);
});
