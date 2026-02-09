import re
import requests
import dns.resolver
import time
import os
from typing import List, Set

# ========== 配置区域 (已按要求更新) ==========
UPSTREAM_RULES = [
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.mini.txt",  # ✅ 正确规则源
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/tif.medium.txt"  # ✅ 正确规则源
]

DOMESTIC_DNS = [
    "114.114.114.114",  # 114 DNS
    "180.76.76.76",     # 阿里 DNS
    "223.5.5.5"          # 腾讯 DNS
]

FOREIGN_DNS = [
    "8.8.8.8",           # Google DNS
    "1.1.1.1",           # Cloudflare DNS
    "9.9.9.9"            # Quad9 DNS
]

OUTPUT_FILE = "final_rules.txt"

# ========== 核心逻辑 (已优化进度写入) ==========
def download_rules(urls: List[str]) -> Set[str]:
    domains = set()
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'
            for line in response.text.splitlines():
                if line.startswith('!') or not line.strip():
                    continue
                if match := re.match(r'\|\|([^/^]+)\^', line):
                    domains.add(match.group(1))
        except Exception as e:
            print(f"⚠️ 从 {url} 下载失败: {str(e)}")
    return domains

def is_domain_resolvable(domain: str, dns_servers: List[str]) -> bool:
    for dns in dns_servers:
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns]
            resolver.resolve(domain, 'A', raise_on_no_answer=False)
            return True
        except:
            continue
    return False

def main():
    print("🚀 正在下载上游规则...")
    all_domains = download_rules(UPSTREAM_RULES)
    print(f"✅ 已获取 {len(all_domains)} 个域名")
    
    valid_domains = []
    total = len(all_domains)
    for i, domain in enumerate(all_domains, 1):
        # DNS验证逻辑
        if is_domain_resolvable(domain, DOMESTIC_DNS):
            valid_domains.append(domain)
        elif is_domain_resolvable(domain, FOREIGN_DNS):
            valid_domains.append(domain)
        
        # >>>>> 关键优化：实时写入进度 <<<<<
        try:
            with open('.progress', 'w') as f:
                f.write(f"{i},{total},{int(time.time())}\n")
        except:
            pass  # 忽略写入错误，不影响主流程
        # <<<<< 进度写入结束 >>>>>
        
        if i % 10 == 0:
            time.sleep(0.1)
        print(f"🔍 检查域名 [{i}/{total}]: {domain} {'✅' if domain in valid_domains else '❌'}", end='\r')
    
    print(f"\n✅ 有效域名: {len(valid_domains)} / {total} (过滤 {total - len(valid_domains)} 个无效域名)")
    
    new_rules = [f'||{domain}^' for domain in valid_domains]
    with open(OUTPUT_FILE, 'w') as f:
        f.write("\n".join(new_rules))
    
    print(f"📝 规则已生成: {OUTPUT_FILE} (共 {len(new_rules)} 条)")
    print("✅ 任务完成！")

if __name__ == "__main__":
    main()
