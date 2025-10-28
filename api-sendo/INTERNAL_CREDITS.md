# 💰 Sistema de Créditos Internos

Sistema para agregar créditos/bonos a usuarios sin que el monitor blockchain los sobrescriba.

## 📊 Estructura de Balances

Cada balance de usuario ahora tiene **3 campos**:

| Campo | Descripción | Actualizado por |
|-------|-------------|-----------------|
| **`onChainBalance`** | Balance real en blockchain | Monitor, Sweep, Deposits |
| **`internalCredits`** | Bonos/créditos internos | Admin (manual) |
| **`amount`** | Total disponible = onChain + internal | Sistema (calculado) |

## 🔧 Agregar Créditos Internos

### Endpoint

```http
POST /api/monitor/internal-credits
Content-Type: application/json

{
  "phoneNumber": "+523111392820",
  "currency": "PYUSD-ARB",
  "amount": 10.5,
  "note": "Bonus de bienvenida"
}
```

### Respuesta Exitosa

```json
{
  "success": true,
  "message": "Internal credits added successfully",
  "data": {
    "user": "Test User",
    "currency": "PYUSD-ARB",
    "creditsAdded": 10.5,
    "newInternalCredits": 10.5,
    "newOnChainBalance": 0,
    "newTotalBalance": 10.5
  }
}
```

### Ejemplo con curl

```bash
curl -X POST http://localhost:3000/api/monitor/internal-credits \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "+523111392820",
    "currency": "PYUSD-ARB",
    "amount": 10,
    "note": "Bonus promocional"
  }'
```

## 🎯 Casos de Uso

### 1. Bonus de Bienvenida

```bash
curl -X POST http://localhost:3000/api/monitor/internal-credits \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "+1234567890",
    "currency": "PYUSD-ARB",
    "amount": 5,
    "note": "Welcome bonus"
  }'
```

### 2. Ajuste Administrativo

```bash
curl -X POST http://localhost:3000/api/monitor/internal-credits \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "+1234567890",
    "currency": "PYUSD-ARB",
    "amount": 2.50,
    "note": "Correction for failed transaction"
  }'
```

### 3. Crédito Promocional

```bash
curl -X POST http://localhost:3000/api/monitor/internal-credits \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "+1234567890",
    "currency": "PYUSD-ARB",
    "amount": 20,
    "note": "Black Friday promo"
  }'
```

## ✅ Garantías

### ✅ El Monitor NO Sobrescribe Créditos Internos

Cuando el monitor detecta un depósito:
```javascript
onChainBalance += depositAmount  // ✅ Se incrementa
internalCredits // ⛔ NO se toca
amount = onChainBalance + internalCredits  // ✅ Se recalcula
```

Cuando sincronizas con `/api/monitor/sync` con `updateDB: true`:
```javascript
onChainBalance = blockchainAmount  // ✅ Se sincroniza
internalCredits // ⛔ NO se toca
amount = onChainBalance + internalCredits  // ✅ Se recalcula
```

### ✅ Los Withdrawals Usan el Balance Total

Cuando un usuario hace withdrawal, puede usar:
- Su balance on-chain (tokens reales en blockchain)
- Sus créditos internos (si el withdrawal service lo permite)

El balance total (`amount`) es lo que ve el usuario y puede usar.

## 📊 Ver Balances Detallados

```bash
# Ver balance de un usuario específico
curl http://localhost:3000/api/users?phoneNumber=+523111392820 | jq '.data[0].balances[]'
```

**Respuesta:**
```json
{
  "currency": "PYUSD-ARB",
  "amount": 25.5,           // Total disponible
  "onChainBalance": 15.5,   // En blockchain
  "internalCredits": 10     // Créditos internos
}
```

## 🔄 Migración de Datos Existentes

Si tienes usuarios existentes, ejecuta el script de migración:

```bash
node scripts/migrateBalances.js
```

Este script:
- ✅ Inicializa `onChainBalance` = balance actual
- ✅ Inicializa `internalCredits` = 0
- ✅ Mantiene `amount` igual

## ⚠️ Importante

1. **Los créditos internos NO están en blockchain**
   - No se pueden barrer (sweep)
   - No aparecen en exploradores como Arbiscan

2. **Los créditos internos SÍ se pueden usar para:**
   - Transfers entre usuarios dentro del sistema
   - Withdrawals (si configuras que los acepte)
   - Cualquier operación interna

3. **Para withdrawals con créditos internos:**
   - El sistema necesita tener fondos en la hot wallet
   - Los créditos internos se "convierten" a tokens reales al hacer withdrawal

## 🎓 Ejemplo Completo

```bash
# 1. Usuario nuevo sin fondos
curl http://localhost:3000/api/users?phoneNumber=+1234567890 | jq '.data[0].balances[]'
# → onChain: 0, internal: 0, total: 0

# 2. Agregar bonus de bienvenida (10 PYUSD)
curl -X POST http://localhost:3000/api/monitor/internal-credits \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber": "+1234567890", "currency": "PYUSD-ARB", "amount": 10, "note": "Welcome bonus"}'
# → onChain: 0, internal: 10, total: 10

# 3. Usuario deposita 5 PYUSD reales
# (el monitor detecta automáticamente)
# → onChain: 5, internal: 10, total: 15

# 4. Usuario hace transfer interno de 3 PYUSD a otro usuario
# → onChain: 5, internal: 7, total: 12

# 5. Sistema hace sweep automático
# → onChain: 0, internal: 7, total: 7 ✅ Créditos internos INTACTOS
```

## 📝 Notas

- Los créditos internos persisten incluso después de sweeps
- Perfectos para programas de lealtad, bonos, referidos
- Se registran en `transactions` con `metadata.source = 'internal_credits'`
- El monitor NUNCA toca los créditos internos

## 🚀 Próximos Pasos

Ahora puedes:
1. ✅ Agregar bonos de bienvenida
2. ✅ Hacer promociones sin tocar blockchain
3. ✅ Ajustar balances de usuarios de forma segura
4. ✅ Crear programas de referidos con créditos

El sistema se encarga automáticamente de mantener la separación entre fondos reales y créditos internos.

