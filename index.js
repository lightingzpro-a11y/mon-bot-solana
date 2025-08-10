const TelegramBot = require('node-telegram-bot-api');
const { Connection, Keypair, PublicKey, Transaction, SystemProgram } = require('@solana/web3.js');
const axios = require('axios');
const base58 = require('base58');

// === CONFIG ===
const TELEGRAM_TOKEN = '8232782908:AAFlQ4_B9sfdoN9rSBMbaONdASvDYX7Vktg';  // Ton token Telegram
const SOLANA_RPC = 'https://api.mainnet-beta.solana.com'; // RPC Solana mainnet
const WALLET_PRIVATE_KEY_BASE58 = '48c9B8Dv6vBydsdeCz6o1gyYHPvcUNvJxMJkAZwShtJVSsr3bmNTPwgEzBVFLNWjxuohmqMdSqeDk8ruPoRxEBB9';

// === INIT ===
const connection = new Connection(SOLANA_RPC);
const privateKeyBytes = base58.decode(WALLET_PRIVATE_KEY_BASE58);
const keypair = Keypair.fromSecretKey(Uint8Array.from(privateKeyBytes));
const bot = new TelegramBot(TELEGRAM_TOKEN, { polling: true });

bot.on('message', async (msg) => {
  const chatId = msg.chat.id;
  const tokenAddress = msg.text.trim();

  // Validation rapide (longueur d'adresse Solana)
  if (tokenAddress.length < 32) {
    bot.sendMessage(chatId, "Adresse de token invalide.");
    return;
  }

  bot.sendMessage(chatId, `Reçu adresse token : ${tokenAddress}. Achat en cours...`);

  try {
    // Ici, tu dois appeler Jupiter API pour acheter le token.
    // Exemple fictif d'appel:
    await acheterToken(tokenAddress);

    bot.sendMessage(chatId, "Token acheté. Monitoring du prix pour vendre...");

    // Start monitoring le prix (à implémenter) pour vendre à +20% / -20%
    monitorPrix(tokenAddress, chatId);

  } catch (e) {
    bot.sendMessage(chatId, "Erreur lors de l'achat : " + e.message);
  }
});

async function acheterToken(tokenAddress) {
  // Appel simplifié à Jupiter DEX API pour acheter le token
  // Exemple: POST vers Jupiter swap endpoint
  // Tu dois construire la transaction Solana correspondante ici
  console.log("Achat token", tokenAddress);
  // TODO: Intégrer Jupiter API & construire la transaction
}

function monitorPrix(tokenAddress, chatId) {
  // TODO : Checker le prix en boucle (toutes les X secondes),
  // et vendre si +20% ou -20%
  // bot.sendMessage(chatId, "Vente déclenchée car +20% ou -20%");
}

console.log("Bot Telegram Solana démarré.");
