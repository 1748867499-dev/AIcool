"""
管家匹配 Agent
基于多维度特征计算最优管家匹配度
"""

import numpy as np
from typing import List, Dict, Tuple


class AgentMatcher:
    """管家匹配 Agent"""
    
    def __init__(self):
        # 匹配权重配置
        self.weights = {
            "成交率": 0.25,
            "满意度": 0.20,
            "响应速度": 0.15,
            "专业领域": 0.20,
            "workload": 0.10,
            "风格匹配": 0.10
        }
    
    def match(self, customer: Dict, agents: List[Dict]) -> List[Tuple[Dict, float, str]]:
        """
        匹配客户与管家
        
        Args:
            customer: 客户特征（含意向等级）
            agents: 管家列表
            
        Returns:
            [(管家, 匹配分数, 匹配理由), ...] 按分数降序排列
        """
        results = []
        
        for agent in agents:
            score, reason = self._calculate_match(customer, agent)
            results.append((agent, score, reason))
        
        # 按匹配分数降序排列
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def _calculate_match(self, customer: Dict, agent: Dict) -> Tuple[float, str]:
        """计算单个管家与客户的匹配度"""
        
        # 1. 成交率匹配
        close_rate_score = agent.get("close_rate", 0.5)
        
        # 2. 满意度匹配
        satisfaction_score = agent.get("satisfaction", 4.0) / 5.0
        
        # 3. 响应速度匹配
        response_speed = agent.get("avg_response_time", 300)
        response_score = max(0, 1 - response_speed / 600)
        
        # 4. 专业领域匹配
        specialty_match = self._check_specialty_match(customer, agent)
        
        # 5. Workload 匹配（避免过载）
        current_load = agent.get("current_customers", 0)
        max_load = agent.get("max_customers", 20)
        workload_score = max(0, 1 - current_load / max_load)
        
        # 6. 风格匹配
        style_match = self._check_style_match(customer, agent)
        
        # 综合评分
        total_score = (
            close_rate_score * self.weights["成交率"] +
            satisfaction_score * self.weights["满意度"] +
            response_score * self.weights["响应速度"] +
            specialty_match * self.weights["专业领域"] +
            workload_score * self.weights["workload"] +
            style_match * self.weights["风格匹配"]
        )
        
        # 生成匹配理由
        reason = self._generate_reason(
            customer, agent, close_rate_score, specialty_match, workload_score
        )
        
        return total_score, reason
    
    def _check_specialty_match(self, customer: Dict, agent: Dict) -> float:
        """检查专业领域匹配度"""
        customer_district = customer.get("preferred_district", "")
        customer_budget = customer.get("budget_range", "")
        customer_layout = customer.get("preferred_layout", "")
        
        agent_specialties = agent.get("specialties", [])
        
        match_count = 0
        total_count = 3  # 区域、预算、户型
        
        if any(customer_district in s for s in agent_specialties):
            match_count += 1
        if any(customer_budget in s for s in agent_specialties):
            match_count += 1
        if any(customer_layout in s for s in agent_specialties):
            match_count += 1
        
        return match_count / total_count
    
    def _check_style_match(self, customer: Dict, agent: Dict) -> float:
        """检查销售风格匹配度"""
        customer_type = customer.get("customer_type", "balanced")  # aggressive/balanced/cautious
        agent_style = agent.get("sales_style", "balanced")
        
        # 风格匹配矩阵
        match_matrix = {
            ("aggressive", "aggressive"): 1.0,
            ("aggressive", "balanced"): 0.7,
            ("aggressive", "cautious"): 0.3,
            ("balanced", "aggressive"): 0.7,
            ("balanced", "balanced"): 1.0,
            ("balanced", "cautious"): 0.7,
            ("cautious", "aggressive"): 0.3,
            ("cautious", "balanced"): 0.7,
            ("cautious", "cautious"): 1.0
        }
        
        return match_matrix.get((customer_type, agent_style), 0.5)
    
    def _generate_reason(self, customer: Dict, agent: Dict, 
                        close_rate: float, specialty: float, workload: float) -> str:
        """生成匹配理由"""
        reasons = []
        
        if close_rate > 0.7:
            reasons.append(f"成交率高（{close_rate:.0%}）")
        
        if specialty > 0.6:
            reasons.append("专业领域匹配")
        
        if workload > 0.7:
            reasons.append("当前 workload 适中")
        
        if agent.get("satisfaction", 0) > 4.5:
            reasons.append("客户满意度优秀")
        
        return "，".join(reasons) if reasons else "综合匹配度良好"


# 示例使用
if __name__ == "__main__":
    matcher = AgentMatcher()
    
    # 模拟客户
    customer = {
        "name": "张三",
        "intent_level": "high",
        "preferred_district": "朝阳区",
        "budget_range": "5000-8000",
        "preferred_layout": "两居室",
        "customer_type": "balanced"
    }
    
    # 模拟管家列表
    agents = [
        {
            "name": "管家A",
            "close_rate": 0.45,
            "satisfaction": 4.8,
            "avg_response_time": 120,
            "specialties": ["朝阳区", "5000-8000", "两居室"],
            "current_customers": 12,
            "max_customers": 20,
            "sales_style": "balanced"
        },
        {
            "name": "管家B",
            "close_rate": 0.38,
            "satisfaction": 4.2,
            "avg_response_time": 300,
            "specialties": ["海淀区", "3000-5000", "一居室"],
            "current_customers": 8,
            "max_customers": 20,
            "sales_style": "cautious"
        },
        {
            "name": "管家C",
            "close_rate": 0.52,
            "satisfaction": 4.6,
            "avg_response_time": 180,
            "specialties": ["朝阳区", "8000-12000", "三居室"],
            "current_customers": 15,
            "max_customers": 20,
            "sales_style": "aggressive"
        }
    ]
    
    # 执行匹配
    results = matcher.match(customer, agents)
    
    print("=" * 60)
    print("管家匹配结果")
    print("=" * 60)
    print(f"\n客户: {customer['name']} (意向等级: {customer['intent_level']})")
    print(f"需求: {customer['preferred_district']} {customer['preferred_layout']} {customer['budget_range']}\n")
    
    for i, (agent, score, reason) in enumerate(results, 1):
        print(f"排名 {i}: {agent['name']}")
        print(f"  匹配分数: {score:.2f}")
        print(f"  匹配理由: {reason}")
        print(f"  成交率: {agent['close_rate']:.0%} | 满意度: {agent['satisfaction']}/5.0")
        print(f"  当前客户数: {agent['current_customers']}/{agent['max_customers']}")
        print()
    
    print("=" * 60)
    print(f"推荐分配: {results[0][0]['name']} (匹配分数: {results[0][1]:.2f})")
    print("=" * 60)
