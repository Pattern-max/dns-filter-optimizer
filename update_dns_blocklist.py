import re
import requests
import dns.resolver
import time
import os
from typing import List, Set

# ========== 配置区域 (按需修改) ==========
# 上游规则源 (您提供的URL)
UPSTREAM_RULES = [
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.txt",
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/tif.txt"
]

# 国内DNS (3组) - 中国主流公共DNS
DOMESTIC_DNS = [
    "114.114.114.114",  # 114 DNS
    "180.76.76.76",     # 阿里DNS
    "223.5.5.5"          # 腾讯DNS
]

# 国外DNS (3组) - 全球主流公共DNS
FOREIGN_DNS = [
    "8.8.8.8",           # Google DNS
    "1.1.1.1",           # Cloudflare DNS
    "9.9.9.9"            # Quad9 DNS
]

# 输出文件路径 (GitHub仓库内)
OUTPUT_FILE = "final_rules.txt"

# ========== 核心逻辑 ==========
def download_rules(urls: List[str]) -> Set[str]:
    """下载规则并提取有效域名 (保留唯一域名)"""
    domains = set()
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'
            for line in response.text.splitlines():
                # 跳过注释行和空行
                if line.startswith('!') or not line.strip():
                    continue
                # 从AdBlock规则提取域名 (e.g., ||example.com^ -> example.com)
                if match := re.match(r'\|\|([^/^]+)\^', line):
                    domains.add(match.group(1))
        except Exception as e:
            print(f"⚠️ 从 {url} 下载失败: {str(e)}")
    return domains

def is_domain_resolvable(domain: str, dns_servers: List[str]) -> bool:
    """检查域名是否可解析 (使用指定DNS服务器)"""
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

    # 去重后过滤无效域名
    valid_domains = []
    total = len(all_domains)
    
    for i, domain in enumerate(all_domains, 1):
        # 先用国内DNS验证 (优先检查国内解析)
        if is_domain_resolvable(domain, DOMESTIC_DNS):
            valid_domains.append(domain)
        # 国内失败则用国外DNS
        elif is_domain_resolvable(domain, FOREIGN_DNS):
            valid_domains.append(domain)
        # 无效域名跳过 (不加入规则)
        
        # 每10个域名暂停0.1秒 (避免DNS请求过载)
        if i % 10 == 0:
            time.sleep(0.1)
        print(f"🔍 检查域名 [{i}/{total}]: {domain} {'✅' if domain in valid_domains else '❌'}", end='\r')
    
    print(f"\n✅ 有效域名: {len(valid_domains)} / {total} (过滤 {total - len(valid_domains)} 个无效域名)")

    # 生成AdBlock格式规则
    new_rules = [f'||{domain}^' for domain in valid_domains]
    
    # 保存到文件
    with open(OUTPUT_FILE, 'w') as f:
        f.write("\n".join(new_rules))
    
    print(f"📝 规则已生成: {OUTPUT_FILE} (共 {len(new_rules)} 条)")
    print("✅ 任务完成！")

if __name__ == "__main__":
    main()