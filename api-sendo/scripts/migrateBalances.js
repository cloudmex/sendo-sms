#!/usr/bin/env node
/**
 * Migration Script: Balance Separation
 * 
 * Migrates existing balances to the new structure with:
 * - onChainBalance: Amount in blockchain
 * - internalCredits: Internal credits/bonuses
 * - amount: Total (kept for compatibility)
 */

const mongoose = require('mongoose');
require('dotenv').config();

const User = require('../models/userModel');

async function migrateBalances() {
  try {
    console.log('🔄 Starting balance migration...\n');
    
    await mongoose.connect(process.env.MONGODB_URI);
    console.log('✅ Connected to MongoDB\n');

    const users = await User.find({});
    console.log(`Found ${users.length} users to migrate\n`);

    let migratedCount = 0;

    for (const user of users) {
      let needsSave = false;

      for (const balance of user.balances) {
        // Si no tiene onChainBalance definido, migrar
        if (balance.onChainBalance === undefined || balance.onChainBalance === null) {
          // Asumir que el balance actual es todo on-chain (sin créditos internos)
          balance.onChainBalance = balance.amount || 0;
          balance.internalCredits = 0;
          needsSave = true;
          
          console.log(`User ${user.name} (${user.phoneNumber}):`);
          console.log(`  ${balance.currency}: amount=${balance.amount} → onChain=${balance.onChainBalance}, internal=0`);
        }
      }

      if (needsSave) {
        await user.save();
        migratedCount++;
      }
    }

    console.log(`\n✅ Migration complete!`);
    console.log(`   Users migrated: ${migratedCount}/${users.length}`);
    console.log(`   Users already up-to-date: ${users.length - migratedCount}`);

    await mongoose.disconnect();
  } catch (error) {
    console.error('\n❌ Migration error:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

migrateBalances();

