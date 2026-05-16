"""
智能线索分配系统 - 完整演示
展示多 Agent 协作流程
"""

from intent_scorer import IntentScorer
from agent_matcher import AgentMatcher


def main():
    """演示完整的线索分配流程"""
    
    print("=" * 70)
    print("智能线索分配系统 - 演示")
    print("=" * 70)
    
    # 初始化 Agent
    intent_scorer = IntentScorer()
    agent_matcher = AgentMatcher()
    
    # 模拟客户数据
    customers = [
        {
            "name": "客户A",
            "browse_duration": 1800,
            "browse_count": 8,
            "consult_count": 5,
            "consult_topics": ["价格", "付款方式", "入住时间", "物业费"],
            "showing_count": 2,
            "showing_punctuality": 1.0,
            "price_sensitivity": 0.3,
            "response_speed": 120,
            "budget_match": 0.85,
            "move_in_days": 10,
            "preferred_district": "朝阳区",
            "budget_range": "5000-8000",
            "preferred_layout": "两居室",
            "customer_type": "balanced"
        },
        {
            "name": "客户B",
            "browse_duration": 300,
            "browse_count": 2,
            "consult_count": 1,
            "consult_topics": ["价格"],
            "showing_count": 0,
            "showing_punctuality": 0,
            "price_sensitivity": 0.8,
            "response_speed": 600,
            "budget_match": 0.5,
            "move_in_days": 60,
            "preferred_district": "海淀区",
            "budget_range": "3000-5000",
            "preferred_layout": "一居室",
            "customer_type": "cautious"
        },
        {
            "name": "客户C",
            "browse_duration": 1200,
            "browse_count": 5,
            "consult_count": 3,
            "consult_topics": ["位置", "交通", "周边配套"],
            "showing_count": 1,
            "showing_punctuality": 0.8,
            "price_sensitivity": 0.5,
            "response_speed": 200,
            "budget_match": 0.75,
            "move_in_days": 20,
            "preferred_district": "朝阳区",
            "budget_range": "8000-12000",
            "preferred_layout": "三居室",
            "customer_type": "aggressive"
        }
    ]
    
    # 模拟管家数据
    agents = [
        {
            "name": "管家A（资深）",
            "close_rate": 0.45,
            "satisfaction": 4.8,
            "avg_response_time": 120,
            "specialties": ["朝阳区", "5000-8000", "两居室"],
            "current_customers": 12,
            "max_customers": 20,
            "sales_style": "balanced"
        },
        {
            "name": "管家B（新手）",
            "close_rate": 0.28,
            "satisfaction": 4.0,
            "avg_response_time": 400,
            "specialties": ["海淀区", "3000-5000", "一居室"],
            "current_customers": 5,
            "max_customers": 15,
            "sales_style": "cautious"
        },
        {
            "name": "管家C（高销）",
            "close_rate": 0.52,
            "satisfaction": 4.6,
            "avg_response_time": 180,
            "specialties": ["朝阳区", "8000-12000", "三居室"],
            "current_customers": 15,
            "max_customers": 20,
            "sales_style": "aggressive"
        }
    ]
    
    # 处理每个客户
    for customer in customers:
        print(f"\n{'='*70}")
        print(f"处理客户: {customer['name']}")
        print(f"{'='*70}")
        
        # Step 1: 意向评估
        print("\n[Step 1] 意向评估 Agent 分析中...")
        intent_result = intent_scorer.evaluate(customer)
        print(f"意向等级: {intent_result['level'].upper()}")
        print(f"置信度: {intent_result['confidence']:.0%}")
        print(f"综合评分: {intent_result['score']:.2f}")
        print(f"\n推理过程:\n{intent_result['reasoning']}")
        
        # Step 2: 管家匹配
        print(f"\n[Step 2] 管家匹配 Agent 计算中...")
        match_results = agent_matcher.match(customer, agents)
        
        print("\n匹配结果:")
        for i, (agent, score, reason) in enumerate(match_results, 1):
            print(f"  排名 {i}: {agent['name']} - 匹配分数: {score:.2f}")
            print(f"    理由: {reason}")
        
        # Step 3: 分配决策
        print(f"\n[Step 3] 分配执行 Agent 决策...")
        best_agent = match_results[0][0]
        
        if intent_result['level'] == 'high':
            print(f"✅ 高意向客户 → 分配给资深管家: {best_agent['name']}")
            print(f"   原因: 高意向客户需要最强销售能力跟进")
        elif intent_result['level'] == 'medium':
            print(f"✅ 中意向客户 → 分配给匹配管家: {best_agent['name']}")
            print(f"   原因: 中意向客户需要专业引导")
        else:
            print(f"✅ 低意向客户 → 分配给新手管家: {match_results[-1][0]['name']}")
            print(f"   原因: 低意向客户适合新手练手")
        
        print(f"\n{'='*70}")
    
    # 总结
    print("\n" + "=" * 70)
    print("演示总结")
    print("=" * 70)
    print("""
多 Agent 协作流程:
1. 数据采集 Agent → 提取客户行为数据
2. 意向评估 Agent → 长链推理判断意向等级
3. 管家匹配 Agent → 多维度计算匹配度
4. 分配执行 Agent → 根据意向等级分配管家
5. 效果追踪 Agent → 监控转化效果并反馈调优

预期效果:
- 高意向客户转化率提升 15pp
- 管家人均月签约量提升 23%
- 线索跟进及时率提升 24pp

Token 消耗:
- 试点阶段: 200 万 Token/日
- 全面推广: 500-800 万 Token/日
    """)
    print("=" * 70)


if __name__ == "__main__":
    main()
