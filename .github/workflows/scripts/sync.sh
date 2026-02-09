#!/bin/bash
set -e

mkdir -p rules logs

declare -A rules=(
  ["pro.mini"]="https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.mini.txt"
  ["tif.medium"]="https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/tif.medium.txt"
  ["spam-tlds"]="https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/spam-tlds.txt"
)

echo "🔄 Starting sync..."
any_updated=false

for rule in "${!rules[@]}"; do
  url="${rules[$rule]}"
  output="rules/${rule}.txt"
  tmp="rules/${rule}.tmp.txt"
  
  if curl -sfL --retry 3 --max-time 30 -o "$tmp" "$url" && [[ -s "$tmp" ]]; then
    if [[ -f "$output" ]] && cmp -s "$output" "$tmp"; then
      rm "$tmp"
      echo "✅ $rule: No change"
    else
      mv "$tmp" "$output"
      any_updated=true
      echo "✨ $rule: Updated"
    fi
  else
    rm -f "$tmp" 2>/dev/null
    echo "⚠️ $rule: Download failed (skipped)"
  fi
done

CURRENT_TIME=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
NEXT_SYNC=$(date -u -d '+1 hour' +"%Y-%m-%d %H:%M:%S UTC")

count() { [[ -f "$1" ]] && grep -cv '^\s*(!|$)' "$1" || echo 0; }
PRO=$(count "rules/pro.mini.txt")
TIF=$(count "rules/tif.medium.txt")
SPAM=$(count "rules/spam-tlds.txt")

# 安全更新 README（无 YAML 敏感字符风险）
if [[ -f README.md ]]; then
  sed -i "s/| pro\.mini\.txt |.*/| pro.mini.txt | $CURRENT_TIME | $PRO |/" README.md
  sed -i "s/| tif\.medium\.txt |.*/| tif.medium.txt | $CURRENT_TIME | $TIF |/" README.md
  sed -i "s/| spam-tlds\.txt |.*/| spam-tlds.txt | $CURRENT_TIME | $SPAM |/" README.md
  sed -i "s/最后同步时间:.*/最后同步时间: $CURRENT_TIME/" README.md
  sed -i "s/下次同步:.*/下次同步: $NEXT_SYNC/" README.md
else
  cat > README.md << EOF
# 🛡️ AdGuard规则同步仓库
自动同步 HaGeZi 优化版规则（每小时更新）

## 📦 规则列表
| 规则 | 最后更新 | 条目数 | RAW链接 |
|------|----------|--------|---------|
| pro.mini.txt | $CURRENT_TIME | $PRO | [复制](https://raw.githubusercontent.com/$GITHUB_REPOSITORY/main/rules/pro.mini.txt) |
| tif.medium.txt | $CURRENT_TIME | $TIF | [复制](https://raw.githubusercontent.com/$GITHUB_REPOSITORY/main/rules/tif.medium.txt) |
| spam-tlds.txt | $CURRENT_TIME | $SPAM | [复制](https://raw.githubusercontent.com/$GITHUB_REPOSITORY/main/rules/spam-tlds.txt) |

## 🔄 同步状态
**最后同步**: $CURRENT_TIME  
**下次同步**: $NEXT_SYNC  
**状态**: ✅ 正常运行

---
*数据源: [HaGeZi DNS Blocklists](https://github.com/hagezi/dns-blocklists)*
EOF
fi

cat > sync-status.txt << EOF
最后同步: $CURRENT_TIME
下次同步: $NEXT_SYNC
规则统计:
- pro.mini.txt: $PRO 条
- tif.medium.txt: $TIF 条
- spam-tlds.txt: $SPAM 条
EOF

echo "[$(date -u +'%Y-%m-%d %H:%M:%S UTC')] Sync completed" >> "logs/sync-$(date -u +'%Y-%m-%d').log"
echo "✅ Sync finished successfully"
