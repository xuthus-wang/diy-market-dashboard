"""
DIY市场爆款预测引擎 — 5维打分模型
维度: 销量增速(30%) + 价格竞争力(20%) + 社交热度(20%) + 品类趋势(15%) + 创新度(15%)
"""
import json
import math
from datetime import datetime

class PredictionEngine:
    def __init__(self, data_path="weekly_data/devices.json"):
        with open(data_path, 'r') as f:
            self.devices = json.load(f)
        self.categories = self._build_categories()

    def _build_categories(self):
        cats = {}
        for d in self.devices:
            cat = d['category']
            if cat not in cats:
                cats[cat] = []
            cats[cat].append(d)
        return cats

    def _score_sales_growth(self, device):
        """销量增速评分 (0-20) — 综合增长率+绝对规模"""
        growth = device.get('weekly_growth_pct', 0)
        volume = device.get('monthly_sales', 0)
        # 增长率得分：每1%增长=0.5分，最高10分（20%以上满分）
        growth_score = min(growth * 0.5, 10)
        # 绝对值得分：对数缩放，1万=2分，10万=4分，100万=6分，1000万=8分
        if volume > 0:
            volume_score = min(math.log10(volume) * 1.5, 10)
        else:
            volume_score = 0
        return round(growth_score + volume_score, 1)

    def _score_price_competitiveness(self, device):
        """价格竞争力评分 (0-20) — 同类中性价比越高分越高"""
        cat = device['category']
        peers = self.categories.get(cat, [])
        prices = [d['price_usd'] for d in peers if d.get('price_usd')]
        if not prices or len(prices) < 2:
            return 10
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        if max_price == min_price:
            return 10
        # 价格在同类中的位置，偏低价得高分（但不过于极端）
        price_ratio = (device['price_usd'] - min_price) / (max_price - min_price)
        # 最优区间：同类价格的20%-50%位置
        if price_ratio <= 0.1:
            score = 18  # 极低价有竞争力
        elif price_ratio <= 0.3:
            score = 20  # 甜蜜点
        elif price_ratio <= 0.5:
            score = 16
        elif price_ratio <= 0.7:
            score = 10
        else:
            score = 5
        return score

    def _score_social_heat(self, device):
        """社交热度评分 (0-20)"""
        social = device.get('social_metrics', {})
        tiktok_videos = social.get('tiktok_videos', 0)
        engagement = social.get('engagement_rate', 0)
        search_growth = social.get('search_growth_pct', 0)

        video_score = min(tiktok_videos / 500, 8)  # 500视频=8分
        engagement_score = min(engagement * 2, 6)  # 3%互动率=6分
        search_score = min(search_growth / 10, 6)  # 30%搜索增长=6分
        return round(video_score + engagement_score + search_score, 1)

    def _score_category_trend(self, device):
        """品类趋势评分 (0-20)"""
        cat = device['category']
        trends = {
            '3D打印机': {'cagr': 15, 'stage': 'growth', 'base': 16},
            '智能切割机': {'cagr': 5, 'stage': 'mature', 'base': 10},
            '激光雕刻机': {'cagr': 10, 'stage': 'growth', 'base': 14},
            '热压机': {'cagr': 10, 'stage': 'growth', 'base': 13},
            '电动工具': {'cagr': 6, 'stage': 'mature', 'base': 9},
            'UV打印机': {'cagr': 40, 'stage': 'emerging', 'base': 20},
            '升华打印机': {'cagr': 12, 'stage': 'growth', 'base': 14},
            '刺绣机': {'cagr': 4, 'stage': 'mature', 'base': 10},
        }
        t = trends.get(cat, {'cagr': 5, 'stage': 'mature', 'base': 8})
        score = t['base']
        # 新品在增长品类中加分
        if device.get('is_new', False) and t['stage'] == 'growth':
            score += 3
        return min(score, 20)

    def _score_innovation(self, device):
        """创新度评分 (0-20)"""
        features = device.get('key_features', [])
        score = len(features) * 2  # 每个创新特性2分
        # 独特功能加分
        unique_keywords = ['四合', 'all-in-one', 'AI', '多色', '自动', '智能', '封闭', '14K', '光纤']
        for kw in unique_keywords:
            if kw.lower() in device.get('description', '').lower():
                score += 2
        return min(score, 20)

    def predict_all(self):
        """对所有设备进行爆款预测评分"""
        results = []
        for device in self.devices:
            sales_growth = self._score_sales_growth(device)
            price_comp = self._score_price_competitiveness(device)
            social_heat = self._score_social_heat(device)
            category_trend = self._score_category_trend(device)
            innovation = self._score_innovation(device)

            # 每维度满分20 → 加权后满分20，总分满分100
            total = (sales_growth * 0.30 + price_comp * 0.20 +
                     social_heat * 0.20 + category_trend * 0.15 +
                     innovation * 0.15) * 5  # 缩放到0-100

            # 生成爆发理由
            reasons = []
            if sales_growth >= 15:
                reasons.append(f"销量增速强劲({sales_growth}/20)")
            if price_comp >= 15:
                reasons.append(f"价格极具竞争力({price_comp}/20)")
            if social_heat >= 15:
                reasons.append(f"社交媒体热度高({social_heat}/20)")
            if category_trend >= 15:
                reasons.append(f"品类处于高速增长期({category_trend}/20)")
            if innovation >= 15:
                reasons.append(f"产品创新度突出({innovation}/20)")

            risk = "低"
            if total < 50:
                risk = "高"
            elif total < 65:
                risk = "中"

            results.append({
                'device_id': device['id'],
                'brand': device['brand'],
                'model': device['model'],
                'category': device['category'],
                'total_score': round(total, 1),
                'dimensions': {
                    'sales_growth': sales_growth,
                    'price_competitiveness': price_comp,
                    'social_heat': social_heat,
                    'category_trend': category_trend,
                    'innovation': innovation,
                },
                'reasons': reasons,
                'risk_level': risk,
                'prediction': '🔥 极高爆款潜力' if total >= 80 else
                             '⭐ 高爆款潜力' if total >= 65 else
                             '👍 有爆款潜力' if total >= 50 else
                             '👀 值得关注' if total >= 35 else '— 暂无明显信号'
            })

        results.sort(key=lambda x: x['total_score'], reverse=True)
        return results

    def get_top_predictions(self, n=10):
        all_preds = self.predict_all()
        return all_preds[:n]

    def save_predictions(self, path="weekly_data/predictions.json"):
        predictions = {
            'generated_at': datetime.now().isoformat(),
            'top_10': self.get_top_predictions(10),
            'all': self.predict_all()
        }
        with open(path, 'w') as f:
            json.dump(predictions, f, ensure_ascii=False, indent=2)
        return predictions

if __name__ == '__main__':
    engine = PredictionEngine()
    results = engine.get_top_predictions(10)
    print("=" * 60)
    print("🔥 DIY市场爆款预测 Top 10")
    print("=" * 60)
    for i, r in enumerate(results, 1):
        print(f"\n#{i} {r['brand']} {r['model']} [{r['category']}]")
        print(f"   总分: {r['total_score']}/100 | {r['prediction']}")
        print(f"   维度: 销量增速{r['dimensions']['sales_growth']} | "
              f"价格{r['dimensions']['price_competitiveness']} | "
              f"社交{r['dimensions']['social_heat']} | "
              f"品类{r['dimensions']['category_trend']} | "
              f"创新{r['dimensions']['innovation']}")
        print(f"   理由: {'; '.join(r['reasons'])}")
        print(f"   风险: {r['risk_level']}")
    engine.save_predictions()
    print("\n✅ 预测结果已保存到 weekly_data/predictions.json")
