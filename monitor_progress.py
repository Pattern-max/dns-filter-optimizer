#!/usr/bin/env python3
import time, os, sys, math
from datetime import timedelta

def main():
    print("\033[1;36m🚀 AdGuard 规则生成 · 实时监控面板\033[0m")
    print("\033[2m（按 Ctrl+C 退出监控，不影响主任务）\033[0m\n")
    
    history = []
    start_time = time.time()
    
    while True:
        try:
            if not os.path.exists('.progress'):
                print("\033[2m⏳ 等待任务启动... (请确保主脚本已添加进度写入)\033[0m", end='\r')
                time.sleep(1)
                continue
            
            with open('.progress') as f:
                parts = f.read().strip().split(',')
                current, total, ts = int(parts[0]), int(parts[1]), int(parts[2])
            
            now = time.time()
            history.append((now, current))
            history = [(t, c) for t, c in history if now - t <= 15]
            
            speed = 0
            if len(history) > 1:
                t0, c0 = history[0]
                t1, c1 = history[-1]
                if t1 > t0 and c1 > c0:
                    speed = (c1 - c0) / (t1 - t0)
            
            remaining = total - current
            eta_sec = remaining / speed if speed > 0.1 else 0
            eta_str = str(timedelta(seconds=int(eta_sec))) if speed > 0.1 else "calculating..."
            
            percent = current / total * 100
            bar_len = 40
            filled = int(bar_len * percent / 100)
            bar = '█' * filled + '░' * (bar_len - filled)
            
            sys.stdout.write("\033[2J\033[H")
            print(f"\033[1;32m📊 任务进度\033[0m")
            print(f"进度: [\033[1;34m{bar}\033[0m] \033[1m{percent:.1f}%\033[0m")
            print(f"数量: \033[1m{current:,}\033[0m / \033[1m{total:,}\033[0m 域名")
            print(f"速度: \033[1;33m{speed:.1f}\033[0m 域名/秒  |  剩余: \033[1;36m{eta_str}\033[0m")
            print(f"已用: {str(timedelta(seconds=int(now - start_time)))}  |  预计完成: {time.strftime('%H:%M:%S', time.localtime(now + eta_sec))}")
            print(f"\n💡 \033[2m提示: 当前规则源 = pro.mini.txt + tif.medium.txt (346,059 域名)\033[0m")
            print(f"✅ \033[2m质量保障: 仅合并/去重/验活，无任何规则逻辑修改\033[0m")
            
            if current >= total:
                print("\n\033[1;32m🎉 任务完成！规则已生成: final_rules.txt\033[0m")
                os.remove('.progress')
                break
            
            time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\033[1;33m⏸️  监控已暂停（主任务仍在后台运行）\033[0m")
            break
        except Exception as e:
            print(f"\033[2m⚠️  监控异常: {str(e)[:50]} (继续重试...)\033[0m", end='\r')

if __name__ == "__main__":
    main()