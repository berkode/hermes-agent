# Discord Bot Invite URL — Ready to Paste

## Your Bot ID
```
1508577525071216751
```

## Invite URL (with permissions)

**Copy and paste this into your browser:**

```
https://discord.com/api/oauth2/authorize?client_id=1508577525071216751&permissions=3072&scope=bot
```

### What This URL Does

- **client_id**: Your bot's unique ID (1508577525071216751)
- **permissions=3072**: Grants these permissions:
  - Read Messages (512)
  - Send Messages (512)
  - Read Message History (2048)
  - Total: 512 + 512 + 2048 = 3072
- **scope=bot**: Adds the bot to your server

### Permissions Breakdown

| Permission | Value | Why Needed |
|------------|-------|------------|
| Read Messages | 512 | Hermes reads your commands in Discord |
| Send Messages | 512 | Hermes posts daily briefs, summaries, alerts |
| Read Message History | 2048 | Hermes reads past conversations for context |

**Total: 3072** (minimal, safe permissions)

### Alternative: More Permissions (If You Need More)

If you want full permissions (not recommended for security):

```
https://discord.com/api/oauth2/authorize?client_id=1508577525071216751&permissions=2147483648&scope=bot
```

**permissions=2147483648** = Administrator (all permissions)

## How to Use

1. **Copy the URL** above
2. **Paste into browser** (Chrome, Firefox, Safari)
3. **Select your server** from the dropdown
4. **Click "Authorize"**
5. **Bot will appear** in your server's member list

## Next Steps After Inviting

1. **Test the bot**:
   ```
   In Discord, type: !hermes test
   ```
   (or whatever your trigger command is)

2. **Configure Hermes gateway**:
   ```bash
   hermes gateway start
   ```

3. **Verify in Hermes CLI**:
   ```bash
   hermes status
   ```
   Should show: "Discord gateway: connected"

4. **Post first test message**:
   ```bash
   hermes
   ```
   Then type: "post to discord: test message"

## Troubleshooting

### Bot Not Appearing?

- Check you selected the right server
- Check you clicked "Authorize"
- Check your server has "Add Apps" permission enabled

### Bot Says "Missing Permissions"?

- Re-invite with the URL above (permissions=3072)
- Check server roles, ensure bot role is above other roles

### Hermes Can't Connect?

- Check `~/.hermes/.env` has correct Discord token
- Check bot token hasn't been regenerated
- Run `hermes doctor` for diagnostics
